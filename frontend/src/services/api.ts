export type SourceSnippet = {
  url: string;
  title?: string;
  snippet: string;
};

export type ChatResponse = {
  answer: string;
  sources: SourceSnippet[];
  tool_events: Array<Record<string, unknown>>;
};

const API_BASE = "http://localhost:8000/api/v1";

export async function askChat(params: {
  sessionId: string;
  websiteUrl: string;
  question: string;
}): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: params.sessionId,
      website_url: params.websiteUrl,
      question: params.question,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || "Chat request failed.");
  }

  return response.json();
}

export async function fetchAnalytics(sessionId: string) {
  const response = await fetch(`${API_BASE}/analytics/${sessionId}`);
  if (!response.ok) throw new Error("Failed to fetch analytics.");
  return response.json();
}

export function analyticsPdfUrl(sessionId: string): string {
  return `${API_BASE}/analytics/${sessionId}/report`;
}
