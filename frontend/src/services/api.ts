export type SourceSnippet = {
  citation_id: string;
  url: string;
  title?: string;
  snippet: string;
  score: number;
  metadata?: Record<string, unknown>;
};

export type ChatResponse = {
  answer: string;
  sources: SourceSnippet[];
  tool_events: Array<Record<string, unknown>>;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function askChat(params: {
  sessionId: string;
  websiteUrl: string;
  question: string;
}): Promise<ChatResponse> {
  try {
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
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        "Network request failed. Ensure backend is running on port 8000 and CORS allows your frontend origin."
      );
    }
    throw error;
  }
}

export async function fetchAnalytics(sessionId: string) {
  const response = await fetch(`${API_BASE}/analytics/${sessionId}`);
  if (!response.ok) throw new Error("Failed to fetch analytics.");
  return response.json();
}

export function analyticsPdfUrl(sessionId: string): string {
  return `${API_BASE}/analytics/${sessionId}/report`;
}
