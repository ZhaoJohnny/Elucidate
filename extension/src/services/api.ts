import type { Analysis, Category, ExplainResponse, Variation } from "./types";

const API_BASE = "http://localhost:8000/api/v1/problems";

/** Error with a message that is safe to show the student. */
export class ApiError extends Error {
  constructor(message: string, public retryable: boolean) {
    super(message);
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "Can't reach the Elucidate backend. Is it running on localhost:8000?",
      true
    );
  }

  if (!res.ok) {
    let message = `Request failed (${res.status}).`;
    try {
      const data = await res.json();
      if (typeof data?.message === "string") message = data.message;
    } catch {
      /* body wasn't JSON; keep the generic message */
    }
    throw new ApiError(message, res.status >= 500);
  }
  return res.json() as Promise<T>;
}

export const analyze = (question: string) =>
  post<Analysis>("/analyze", { question });

export const generateVariations = (
  question: string,
  analysis: Analysis,
  categories: Category[]
) =>
  post<{ variations: Variation[] }>("/variations", {
    question,
    analysis,
    categories,
    count_per_category: 1,
  }).then((r) => r.variations);

export const explain = (question: string, variation: Variation) =>
  post<ExplainResponse>("/explain", { question, variation });