from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.problems import router as problems_router
from app.schemas import ErrorResponse
from app.services.ai_client import AIError

app = FastAPI(title="Elucidate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems_router)


@app.exception_handler(AIError)
async def ai_error_handler(_: Request, exc: AIError) -> JSONResponse:
    """Return AI failures in the ErrorResponse shape the extension expects."""
    body = ErrorResponse(code=exc.code, message=exc.message, retryable=exc.retryable)
    return JSONResponse(status_code=502, content=body.model_dump())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}