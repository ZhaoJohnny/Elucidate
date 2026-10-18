import katex from "katex";
import "katex/dist/katex.min.css";

/** Renders text containing \( ... \) and \[ ... \] segments with KaTeX. */
export default function RichText({ text }: { text: string }) {
  const parts = text.split(/(\\\(.+?\\\)|\\\[.+?\\\])/gs);
  return (
    <>
      {parts.map((part, i) => {
        const inline = part.startsWith("\\(") && part.endsWith("\\)");
        const block = part.startsWith("\\[") && part.endsWith("\\]");
        if (!inline && !block) return <span key={i}>{part}</span>;
        return (
          <span
            key={i}
            dangerouslySetInnerHTML={{
              __html: katex.renderToString(part.slice(2, -2), {
                throwOnError: false,
                displayMode: block,
              }),
            }}
          />
        );
      })}
    </>
  );
}