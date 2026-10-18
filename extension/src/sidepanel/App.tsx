import { useState } from "react";
import { analyze, explain, generateVariations } from "../services/api";
import { captureFromActiveTab, type CaptureResult } from "../services/capture";
import type {
  Analysis,
  Category,
  ExplainResponse,
  Variation,
} from "../services/types";

const CATEGORY_LABELS: Record<Category, string> = {
  changed_conditions: "Changed conditions",
  edge_cases: "Edge cases",
  negation_counterexample: "Negation / counterexample",
  reverse_reasoning: "Reverse reasoning",
};
const ALL_CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <>
      <h4>{title}</h4>
      <ul>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </>
  );
}

export default function App() {
  const [captured, setCaptured] = useState<CaptureResult | null>(null);
  const [question, setQuestion] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [categories, setCategories] = useState<Set<Category>>(
    new Set<Category>(["changed_conditions"]),
  );
  const [variations, setVariations] = useState<Variation[]>([]);
  const [answers, setAnswers] = useState<Record<string, ExplainResponse>>({});

  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<{
    message: string;
    retry: () => void;
  } | null>(null);

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
      else if (result.questions.length === 1)
        chooseQuestion(result.questions[0].text);
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
      setVariations(
        await generateVariations(question, analysis, [...categories]),
      );
      setAnswers({});
    });

  const reveal = (v: Variation) =>
    run("Loading answer…", async () => {
      const result = await explain(question, v);
      setAnswers((prev) => ({ ...prev, [v.id]: result }));
    });

  const busy = loading !== null;
  const needsPicker =
    captured &&
    !captured.selection &&
    captured.questions.length > 1 &&
    !question;

  return (
    <main>
      <h1>Elucidate</h1>

      {/* 1. Capture */}
      <section>
        <button onClick={capture} disabled={busy}>
          Capture question
        </button>
        <p className="hint">
          Select text on the page first, or capture the page's questions.
        </p>

        {needsPicker && (
          <ul className="picker">
            {captured.questions.map((q) => (
              <li key={q.id}>
                <button onClick={() => chooseQuestion(q.text)}>{q.text}</button>
              </li>
            ))}
          </ul>
        )}

        {question && <blockquote>{question}</blockquote>}
      </section>

      {loading && <p className="status">{loading}</p>}
      {error && (
        <p className="error">
          {error.message} <button onClick={error.retry}>Retry</button>
        </p>
      )}

      {/* 2. Analysis */}
      {question && (
        <section>
          <button onClick={runAnalysis} disabled={busy}>
            Analyze
          </button>
          {analysis && (
            <div>
              <p>
                <strong>{analysis.summary}</strong>
              </p>
              <List title="Principles" items={analysis.principles} />
              <List title="Assumptions" items={analysis.assumptions} />
              <List title="Constraints" items={analysis.constraints} />
              <h4>Reasoning</h4>
              <p>{analysis.reasoning}</p>
            </div>
          )}
        </section>
      )}

      {/* 3. Variations */}
      {analysis && (
        <section>
          <h3>Challenge your understanding</h3>
          {ALL_CATEGORIES.map((c) => (
            <label key={c} className="check">
              <input
                type="checkbox"
                checked={categories.has(c)}
                onChange={() => toggleCategory(c)}
              />
              {CATEGORY_LABELS[c]}
            </label>
          ))}
          <button
            onClick={runVariations}
            disabled={busy || categories.size === 0}
          >
            Generate variations
          </button>

          {variations.map((v) => {
            const answer = answers[v.id];
            return (
              <div key={v.id} className="variation">
                <div className="tag">{CATEGORY_LABELS[v.category]}</div>
                <p>{v.question}</p>
                <p className="hint">Goal: {v.learning_objective}</p>
                {answer ? (
                  <div className="answer">
                    <p>
                      <strong>Answer:</strong> {answer.expected_answer}
                    </p>
                    <p>{answer.explanation}</p>
                  </div>
                ) : (
                  <button onClick={() => reveal(v)} disabled={busy}>
                    Reveal answer
                  </button>
                )}
              </div>
            );
          })}
        </section>
      )}
    </main>
  );
}
