# Conceptual Learning Assistant

An AI-powered learning assistant that helps students understand *why* a problem works, not just how to solve it.

## Structure
- `frontend/`  Sample-question website (React + TypeScript + Vite)
- `extension/` Chrome Manifest V3 extension with side panel
- `backend/`   FastAPI service (validation, prompts, AI orchestration)
- `docs/`      Requirements, architecture, API

## Setup
```bash
cp .env.example .env

# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e . && uvicorn app.main:app --reload

# frontend / extension
cd frontend && npm install && npm run dev
cd extension && npm install && npm run dev
```

## Roadmap
1. Define scope and question format
2. Sample-question website
3. Extension shell
4. Backend + AI connection
5. Variation engine
6. Test correctness and educational quality
7. Polish and demo
