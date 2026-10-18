# Elucidate

An AI-powered learning assistant that helps students understand *why* a problem works, not just how to solve it.

Elucidate is a Chrome extension that reads an academic question from the page, breaks it down into the principles, assumptions, and constraints behind it, and then generates new practice questions that test whether the student can apply those ideas in unfamiliar situations. Students attempt each variation first and reveal the answer only when they're ready.

## Overview

Most AI study tools show a student how to get the answer. Elucidate focuses on the reasoning behind it:

1. The student opens a question on a webpage and captures it with the extension.
2. Elucidate analyzes the question and shows the concepts it depends on.
3. The student picks a type of variation to challenge their understanding.
4. They attempt the new question, then reveal the answer and explanation.

The project has three parts:

- **Extension**: the main product, a Chrome side panel.
- **Backend**: a FastAPI service that holds the API key, builds prompts, and validates AI output.
- **Demo page**: a static sample problem set used as a local test target.

## Key features

- **Question capture.** Reads the selected text on the page, or every question on it if nothing is selected. Rendered math is converted back to LaTeX so formulas aren't duplicated.
- **Conceptual analysis.** Splits a problem into principles, assumptions, constraints, and reasoning. The side panel shows these as layered bands, from the surface of the problem down to its limiting conditions.
- **Four kinds of variation.** Each tests a different way of transferring the same concepts:
  - *Changed conditions*: what if one condition changes?
  - *Edge cases*: what happens at a boundary or exceptional case?
  - *Negation / counterexample*: what if a key assumption is false?
  - *Reverse reasoning*: work backward from a result to what must be true.
- **Attempt first, reveal later.** Variations are generated without answers. The answer and explanation are fetched only when the student asks.
- **Math rendering.** Equations render with KaTeX in both the demo page and the side panel.
- **Loading, error, and retry states** on every request.
- **Mock mode.** Run the whole flow on hardcoded data with no API key, useful for UI work and offline demos.
- **Validated AI output.** Every model response is checked against strict Pydantic schemas, with one automatic repair attempt on invalid output.

## Tech stack

| Part | Technology |
|---|---|
| Extension | Chrome Manifest V3, React, TypeScript, Vite, KaTeX |
| Demo page | React, TypeScript, Vite, KaTeX |
| Backend | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| AI model | Google Gemini via the `google-genai` SDK (free tier from Google AI Studio) |

The extension never contains the AI key. It talks to the backend over HTTP, and the backend calls the model.

## Project structure

```
elucidate/
├── frontend/            # Demo page: a sample problem set (React + Vite)
│   └── src/
├── extension/           # Chrome extension (Manifest V3 + React)
│   ├── public/manifest.json
│   ├── sidepanel.html
│   └── src/
│       ├── sidepanel/   # Side panel UI
│       ├── content/     # Content script that reads questions from the page
│       ├── background/  # Opens the side panel
│       └── services/    # API client, page capture, shared types
├── backend/             # FastAPI service
│   └── app/
│       ├── api/         # Routes
│       ├── schemas/     # Pydantic request/response models
│       ├── services/    # AI client, AI service, mock data
│       └── prompts/     # Prompt templates
├── docs/                # Requirements, architecture, API notes
├── .env.example
└── README.md
```

## API

The backend is stateless. The extension sends the question and analysis back with each request, so no database is needed.

| Endpoint | Request | Response |
|---|---|---|
| `POST /api/v1/problems/analyze` | `{ question }` | `summary`, `principles[]`, `assumptions[]`, `constraints[]`, `reasoning` |
| `POST /api/v1/problems/variations` | `{ question, analysis, categories[], count_per_category }` | `variations[]` (no answers) |
| `POST /api/v1/problems/explain` | `{ question, variation }` | `expected_answer`, `explanation` |
| `GET /health` | | `{ "status": "ok" }` |

Interactive docs are available at `http://localhost:8000/docs` while the backend is running. Failures return `{ code, message, retryable }`.

## Running the project

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Chrome
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) (not needed in mock mode)

### 1. Configure the environment

From the repo root:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
GEMINI_API_KEY=your-key-here
AI_MODEL=gemini-3.8-flash
USE_MOCK=false
ALLOWED_ORIGINS=http://localhost:5173
```

Set `USE_MOCK=true` to run without an API key. The backend then returns hardcoded responses for the three sample questions. Model names change over time, so if you get a "model not found" error, check which models your key can use in AI Studio and update `AI_MODEL`.

The backend only reads `.env` at startup, so restart it after any change.

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload
```

Check that it's running at `http://localhost:8000/docs`.

### 3. Start the demo page

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### 4. Build and load the extension

In a new terminal:

```bash
cd extension
npm install
npm run build
```

Then in Chrome:

1. Go to `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and select the `extension/dist` folder.
3. Open `http://localhost:5173` and **refresh the page**. The content script is only injected into pages loaded after the extension.
4. Click the Elucidate toolbar icon to open the side panel.

### 5. Try it

1. Click **Capture question**. With no selection, you can pick one of the page's questions.
2. Click **Analyze**.
3. Choose variation types and click **Generate variations**.
4. Attempt a variation, then click **Reveal answer**.

## Developing

- **Backend** reloads automatically on code changes.
- **Demo page** hot-reloads.
- **Extension:** `npm run dev` rebuilds on save, but you still need to click the reload icon on the extension's card in `chrome://extensions`. Refresh the demo page too if you changed the content script.

## Troubleshooting

| Message or symptom | Likely cause and fix |
|---|---|
| "Can't reach the Elucidate backend" | The backend isn't running on port 8000. |
| "Can't read this page" | You're not on `localhost:5173`, or you haven't refreshed it since loading the extension. |
| "The server has no Gemini API key configured" | `GEMINI_API_KEY` is missing from the root `.env`, or the backend wasn't restarted after editing it. |
| "The AI service returned an error" | Check the backend terminal for the `Gemini API error` line. A 404 usually means `AI_MODEL` isn't available to your key. |
| "Free-tier limit reached" | You hit the Gemini free-tier rate limit. Wait a minute, or set `USE_MOCK=true`. |
| Extension looks outdated after changes | The build may have failed (check for an error from `npm run build`), or you didn't reload the extension in `chrome://extensions`. |

## Limitations

- **Correctness isn't guaranteed.** Schema validation confirms the *shape* of a response, not that the math or physics is right. The prompts ask the model to verify its own work, but errors can still occur, so check generated questions and answers.
- **Built for the demo page.** The content script only runs on `localhost:5173`. Supporting other sites is a small manifest change, but capture quality on arbitrary pages hasn't been tested.
- **Free-tier limits.** Gemini's free tier is rate-limited, and Google may use free-tier requests to improve its products, so don't send private information.
- **Text only.** No image or OCR input yet.

## Roadmap

- A script that runs every sample question through every variation category for quality review
- Cross-checking variation answers against independently generated solutions
- Support for more websites and for image input
- Saved sessions and progress tracking