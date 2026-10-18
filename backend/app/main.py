from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.problems import router as problems_router

app = FastAPI(title="Elucidate API")

# Dev-only CORS: the demo site and any Chrome extension origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}