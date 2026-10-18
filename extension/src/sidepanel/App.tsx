import { useState, type CSSProperties, type ReactNode } from "react";
import { analyze, explain, generateVariations } from "../services/api";
import { captureFromActiveTab, type CaptureResult } from "../services/capture";
import type {
  Analysis,
  Category,
  ExplainResponse,
  Variation,
} from "../services/types";
import RichText from "./RichText";

// Each variation type keeps one palette color everywhere it appears.
const CATEGORIES: Record<Category, { label: string; color: string }> = {
  changed_conditions: { label: "Changed conditions", color: "var(--lagoon)" },
  edge_cases: { label: "Edge cases", color: "var(--cobalt)" },
  negation_counterexample: { label: "Negation / counterexample", color: "var(--glacier)" },
  reverse_reasoning: { label: "Reverse reasoning", color: "var(--deep)" },
};
const ALL_CATEGORIES = Object.keys(CATEGORIES) as Category[];

/** Four-facet mark in the palette colors. */
function Mark() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
      <polygon points="13,2 24,13 13,13" fill="#cbddf1" />
      <polygon points="13,2 2,13 13,13" fill="#9bc1e0" />
      <polygon points="2,13 13,13 13,24" fill="#4a93a2" />
      <polygon points="24,13 13,13 13,24" fill="#3f78a8" />
    </svg>
  );
}

/** One step on the vertical rail. The dot fills in when the step is done. */
function Stage({ title, done, children }: { title: string; done: boolean; children: ReactNode }) {
  return (
    <section className={`stage${done ? " done" : ""}`}>
      <span className="dot" aria-hidden="true" />
      <h2>{title}</h2>
      {children}
    </section>
  );
}

/** One layer of the analysis. Lighter = closer to the surface of the problem. */
function Band({ title, items, tone }: { title: string; items: string[]; tone: "surface" | "mid" | "deep" }) {
  return (
    <div className={`band ${tone}`}>
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="none">None stated.</p>
      ) : (
        <ul>
          {items.map((item, i) => (
            <li key={i}>
              <RichText text={item} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function App() {
  const [captured, setCaptured] = useState<CaptureResult | null>(null);
  const [question, setQuestion] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [categories, setCategories] = useState<Set<Category>>(
    new Set<Category>(["changed_conditions"])
  );
  const [variations, setVariations] = useState<Variation[]>([]);
  const [answers, setAnswers] = useState<Record<string, ExplainResponse>>({});

  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<{ message: string; retry: () => void } | null>(null);

  /** Run an async action with shared loading, error, and retry handling. */
  async function run(label: string, action: () => Promise<void>) {
    setLoading(label);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError({
        message: e instanceof Error ? e.message : "Something went wrong.",
        retry: () => run(label, action),
      });
    } finally {
      setLoading(null);
    }
  }

  /** Set the active question and clear everything derived from the old one. */
  function chooseQuestion(text: string) {
    setQuestion(text);
    setAnalysis(null);
    setVariations([]);
    setAnswers({});
  }

  function toggleCategory(c: Category) {
    const next = new Set(categories);
    if (next.has(c)) next.delete(c);
    else next.add(c);
    setCategories(next);
  }

  const capture = () =>
    run("Capturing question…", async () => {
      const result = await captureFromActiveTab();
      setCaptured(result);
      if (result.selection) chooseQuestion(result.selection);
      else if (result.questions.length === 1) chooseQuestion(result.questions[0].text);
      else chooseQuestion(""); // several questions: let the student pick
    });

  const runAnalysis = () =>
    run("Analyzing…", async () => {
      setAnalysis(await analyze(question));
      setVariations([]);
      setAnswers({});
    });

  const runVariations = () =>
    run("Generating variations…", async () => {
      if (!analysis) return;
      setVariations(await generateVariations(question, analysis, [...categories]));
      setAnswers({});
    });

  const reveal = (v: Variation) =>
    run("Loading answer…", async () => {
      const result = await explain(question, v);
      setAnswers((prev) => ({ ...prev, [v.id]: result }));
    });

  const busy = loading !== null;
  const needsPicker =
    captured && !captured.selection && captured.questions.length > 1 && !question;

  return (
    <>
      <header className="top">
        <div className="brand">
          <Mark />
          <div>
            <h1>Elucidate</h1>
            <p>See why it works.</p>
          </div>
        </div>
        {busy && (
          <div className="progress" aria-hidden="true">
            <span />
          </div>
        )}
      </header>

      <main>
        {loading && (
          <p className="status" role="status">
            {loading}
          </p>
        )}
        {error && (
          <div className="error" role="alert">
            <p>{error.message}</p>
            <button className="btn secondary" onClick={error.retry}>
              Retry
            </button>
          </div>
        )}

        <Stage title="Question" done={!!question}>
          <p className="hint">
            Select text on the page to capture just that part, or capture every
            question on it.
          </p>
          <button className="btn" onClick={capture} disabled={busy}>
            Capture question
          </button>

          {needsPicker && (
            <ul className="picker">
              {captured.questions.map((q) => (
                <li key={q.id}>
                  <button onClick={() => chooseQuestion(q.text)}>
                    <RichText text={q.text} />
                  </button>
                </li>
              ))}
            </ul>
          )}

          {question && (
            <blockquote className="question">
              <RichText text={question} />
            </blockquote>
          )}
        </Stage>

        {question && (
          <Stage title="Analysis" done={!!analysis}>
            <button className="btn" onClick={runAnalysis} disabled={busy}>
              Analyze
            </button>
            {analysis && (
              <>
                <p className="summary">
                  <RichText text={analysis.summary} />
                </p>
                <div className="strata">
                  <Band title="Principles" items={analysis.principles} tone="surface" />
                  <Band title="Assumptions" items={analysis.assumptions} tone="mid" />
                  <Band title="Constraints" items={analysis.constraints} tone="deep" />
                </div>
                <h3 className="reasoning-title">Reasoning</h3>
                <p className="reasoning">
                  <RichText text={analysis.reasoning} />
                </p>
              </>
            )}
          </Stage>
        )}

        {analysis && (
          <Stage title="Variations" done={variations.length > 0}>
            <fieldset className="chips">
              <legend>Choose variation types</legend>
              <div className="chip-row">
                {ALL_CATEGORIES.map((c) => (
                  <label
                    key={c}
                    className="chip"
                    style={{ "--cat": CATEGORIES[c].color } as CSSProperties}
                  >
                    <input
                      type="checkbox"
                      checked={categories.has(c)}
                      onChange={() => toggleCategory(c)}
                    />
                    <span className="chip-body">{CATEGORIES[c].label}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            <button
              className="btn"
              onClick={runVariations}
              disabled={busy || categories.size === 0}
            >
              Generate variations
            </button>

            {variations.map((v) => {
              const answer = answers[v.id];
              return (
                <article
                  key={v.id}
                  className="variation"
                  style={{ "--cat": CATEGORIES[v.category].color } as CSSProperties}
                >
                  <p className="cat">{CATEGORIES[v.category].label}</p>
                  <p className="vq">
                    <RichText text={v.question} />
                  </p>
                  {v.modified_conditions.length > 0 && (
                    <p className="meta">
                      What changed: <RichText text={v.modified_conditions.join("; ")} />
                    </p>
                  )}
                  <p className="meta">
                    Goal: <RichText text={v.learning_objective} />
                  </p>
                  {answer ? (
                    <div className="answer">
                      <p className="final">
                        <RichText text={answer.expected_answer} />
                      </p>
                      <p className="why">
                        <RichText text={answer.explanation} />
                      </p>
                    </div>
                  ) : (
                    <button
                      className="btn secondary"
                      onClick={() => reveal(v)}
                      disabled={busy}
                    >
                      Reveal answer
                    </button>
                  )}
                </article>
              );
            })}
          </Stage>
        )}
      </main>
    </>
  );
}