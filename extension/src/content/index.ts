/**
 * Content script: runs on the demo page and answers capture requests
 * from the side panel. Keep this file free of imports so it builds to a
 * plain script.
 */

interface CapturedQuestion {
  id: string;
  text: string;
}

interface CaptureResult {
  selection: string | null;
  questions: CapturedQuestion[];
}

/**
 * Extract readable text from a DOM node, converting rendered KaTeX back
 * to LaTeX. KaTeX includes a hidden MathML copy alongside the visual copy,
 * so reading textContent directly would duplicate every formula.
 */
function extractText(node: Node): string {
  const clone = node.cloneNode(true) as Element;
  clone.querySelectorAll?.(".katex").forEach((katexEl) => {
    const tex =
      katexEl.querySelector('annotation[encoding="application/x-tex"]')
        ?.textContent ?? "";
    katexEl.replaceWith(document.createTextNode(`\\(${tex}\\)`));
  });
  return (clone.textContent ?? "").replace(/\s+/g, " ").trim();
}

function getSelectionText(): string | null {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return null;
  const holder = document.createElement("div");
  holder.appendChild(sel.getRangeAt(0).cloneContents());
  return extractText(holder) || null;
}

function getPageQuestions(): CapturedQuestion[] {
  return Array.from(
    document.querySelectorAll<HTMLElement>("[data-question-id] .question-text")
  ).map((el) => ({
    id: el.closest("[data-question-id]")!.getAttribute("data-question-id")!,
    text: extractText(el),
  }));
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "CAPTURE_QUESTION") {
    const result: CaptureResult = {
      selection: getSelectionText(),
      questions: getPageQuestions(),
    };
    sendResponse(result);
  }
});