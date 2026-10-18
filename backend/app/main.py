from fastapi import FastAPI

app = FastAPI(title="Conceptual Learning Assistant API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
