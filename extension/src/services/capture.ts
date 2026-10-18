export interface CaptureResult {
  selection: string | null;
  questions: { id: string; text: string }[];
}

/** Ask the content script on the active tab for the selection and page questions. */
export async function captureFromActiveTab(): Promise<CaptureResult> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new Error("No active tab found.");

  try {
    return await chrome.tabs.sendMessage(tab.id, { type: "CAPTURE_QUESTION" });
  } catch {
    throw new Error(
      "Can't read this page. Open the demo site (localhost:5173) and refresh it."
    );
  }
}