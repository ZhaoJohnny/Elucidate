# Architecture

Website (React + TS + Vite, KaTeX) -> Extension (MV3, side panel) -> FastAPI backend -> AI model

- The AI API key lives only in the backend.
- No database: state is in-memory / client-side for the session.
