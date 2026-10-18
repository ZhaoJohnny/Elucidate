"""Thin wrapper around the Gemini API that returns validated Pydantic objects."""

import logging
from functools import lru_cache
from typing import Callable, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.config import settings

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class AIError(Exception):
    """A failure the client can display. Mapped to ErrorResponse in main.py."""

    def __init__(self, code: str, message: str, retryable: bool):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    """Create the client lazily, so the server still starts (e.g. in mock mode) without a key."""
    if not settings.api_key:
        raise AIError("ai_auth", "The server has no Gemini API key configured.", False)
    return genai.Client(
        api_key=settings.api_key,
        http_options=types.HttpOptions(timeout=int(settings.request_timeout_s * 1000)),  # ms
    )


def generate_structured(
    *,
    system: str,
    user: str,
    schema: type[T],
    validate: Callable[[T], None] | None = None,
) -> T:
    """Call the model and return an instance of `schema`.

    Gemini is asked for JSON matching `schema`. The reply is then re-validated
    with our own (strict) Pydantic model plus the optional `validate` check
    (which should raise ValueError). On failure, the error is fed back for one
    repair attempt before giving up.
    """
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=schema,
        max_output_tokens=settings.max_tokens,
        temperature=0.4,
    )
    contents = user

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=settings.model, contents=contents, config=config
            )
        except httpx.TimeoutException:
            raise AIError("ai_timeout", "The AI took too long to respond.", True)
        except httpx.ConnectError:
            raise AIError("ai_unreachable", "Couldn't reach the AI service.", True)
        except errors.APIError as e:
            log.error("Gemini API error %s: %s", e.code, e.message)
            if e.code == 429:
                raise AIError("ai_rate_limited", "Free-tier limit reached. Wait a minute and retry.", True)
            if e.code in (401, 403) or "API key" in str(e.message):
                raise AIError("ai_auth", "The server's Gemini API key is invalid.", False)
            raise AIError("ai_error", "The AI service returned an error.", (e.code or 500) >= 500)

        text = response.text  # None if blocked or truncated
        if not text:
            error_text = "The model returned an empty response."
        else:
            try:
                result = schema.model_validate_json(text)
                if validate:
                    validate(result)
                return result
            except (ValidationError, ValueError) as e:
                error_text = str(e)

        log.warning("Invalid AI output (attempt %d): %s", attempt + 1, error_text)
        if attempt == 0:
            contents = (
                f"{user}\n\nYour previous attempt was invalid.\n"
                f"Previous output:\n{text or '(empty)'}\n\n"
                f"Error: {error_text}\nReturn a corrected answer."
            )

    raise AIError("ai_invalid_output", "The AI returned an unusable answer. Please retry.", True)