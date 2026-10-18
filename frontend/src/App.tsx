import type { CSSProperties } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

type Problem = {
  id: string;
  title: string;
  subject: string;
  points: number;
  lines: number; // ruled lines of work space
  text: string; // inline math uses \( ... \)
};

// Keep the key phrases ("absolute maximum", "thrown straight up", "invertible")
// if you use mock mode: the mock backend matches on them.
const PROBLEMS: Problem[] = [
  {
    id: "calc-001",
    title: "Optimization on a closed interval",
    subject: "Calculus",
    points: 10,
    lines: 7,
    text: String.raw`Find the absolute maximum of \(f(x) = x^3 - 3x\) on the interval \([-2, 2]\).`,
  },
  {
    id: "phys-001",
    title: "Vertical motion",
    subject: "Physics",
    points: 6,
    lines: 6,
    text: String.raw`A ball is thrown straight up at \(20\ \text{m/s}\). Ignoring air resistance and taking \(g = 9.8\ \text{m/s}^2\), what maximum height does it reach?`,
  },
  {
    id: "la-001",
    title: "Invertibility",
    subject: "Linear Algebra",
    points: 8,
    lines: 6,
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
  const total = PROBLEMS.reduce((sum, p) => sum + p.points, 0);

  return (
    <div className="desk">
      <main className="sheet">
        <header className="sheet-head">
          <div>
            <p className="dept">Department of Mathematical Sciences</p>
            <h1>SCI 210: Mathematical Methods for Science</h1>
            <p className="set-title">
              Problem Set 6: Optimization, Motion, and Matrices
            </p>
          </div>
          <div className="score-box">
            <span className="score-label">Score</span>
            <span className="score-row">
              <span className="score-line" />
              <span>/ {total}</span>
            </span>
          </div>
        </header>

        <div className="fields">
          <div className="field">
            <span>Name</span>
            <span className="line" />
          </div>
          <div className="field">
            <span>Student ID</span>
            <span className="line" />
          </div>
          <div className="field">
            <span>Section</span>
            <span className="line" />
          </div>
        </div>

        <p className="due">
          Due Friday, October 23, at 11:59 PM. Submit through the course portal.
        </p>

        <section className="instructions">
          <h2>Instructions</h2>
          <ul>
            <li>Show all work and justify each answer in complete sentences.</li>
            <li>Give exact answers where possible. Round numerical answers to three significant figures.</li>
            <li>A scientific calculator is allowed. Graphing calculators are not.</li>
            <li>You may discuss the problems with classmates, but write up your own solutions.</li>
          </ul>
        </section>

        <section className="problems">
          {PROBLEMS.map((p, i) => (
            // data-question-id and .question-text are the extension's hooks.
            <article
              key={p.id}
              className="problem"
              data-question-id={p.id}
              data-subject={p.subject}
            >
              <div className="problem-head">
                <h2>Problem {i + 1}</h2>
                <span className="problem-title">{p.title}</span>
                <span className="points">{p.points} points</span>
              </div>
              <p className="question-text">
                <RichText text={p.text} />
              </p>
              <div
                className="work"
                aria-hidden="true"
                style={{ "--lines": p.lines } as CSSProperties}
              />
            </article>
          ))}
        </section>

        <footer className="sheet-foot">
          <span>SCI 210, Problem Set 6</span>
          <span>Page 1 of 1</span>
        </footer>
      </main>
    </div>
  );
}