import katex from "katex";

type Question = {
  id: string;
  subject: string;
  difficulty: "Easy" | "Medium" | "Hard";
  text: string; // inline math uses \( ... \)
};

// Static for now. Move to src/questions/ when the list grows.
const QUESTIONS: Question[] = [
  {
    id: "calc-001",
    subject: "Calculus",
    difficulty: "Medium",
    text: String.raw`Find the absolute maximum of \(f(x) = x^3 - 3x\) on the interval \([-2, 2]\).`,
  },
  {
    id: "phys-001",
    subject: "Physics",
    difficulty: "Easy",
    text: String.raw`A ball is thrown straight up at \(20\ \text{m/s}\). Ignoring air resistance and taking \(g = 9.8\ \text{m/s}^2\), what maximum height does it reach?`,
  },
  {
    id: "la-001",
    subject: "Linear Algebra",
    difficulty: "Easy",
    text: String.raw`Is the matrix \(A = \begin{pmatrix} 1 & 2 \\ 2 & 4 \end{pmatrix}\) invertible? Justify your answer.`,
  },
];

// Renders text containing \( ... \) segments as KaTeX math.
function RichText({ text }: { text: string }) {
  const parts = text.split(/(\\\(.+?\\\))/gs);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("\\(") && part.endsWith("\\)") ? (
          <span
            key={i}
            dangerouslySetInnerHTML={{
              __html: katex.renderToString(part.slice(2, -2), {
                throwOnError: false,
              }),
            }}
          />
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

export default function App() {
  return (
    <main className="container">
      <h1>Sample Questions</h1>
      <p>Select a question, or just open the extension, to analyze it.</p>

      {QUESTIONS.map((q) => (
        // data-question-id and .question-text give the extension stable hooks.
        <article
          key={q.id}
          className="question"
          data-question-id={q.id}
          data-subject={q.subject}
          data-difficulty={q.difficulty}
        >
          <div className="meta">
            {q.subject} · {q.difficulty}
          </div>
          <p className="question-text">
            <RichText text={q.text} />
          </p>
        </article>
      ))}
    </main>
  );
}