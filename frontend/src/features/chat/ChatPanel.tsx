import { FormEvent, useMemo, useState } from "react";

import { askChat, SourceSnippet } from "../../services/api";

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: SourceSnippet[];
};

type Props = {
  sessionId: string;
};

export default function ChatPanel({ sessionId }: Props) {
  const [websiteUrl, setWebsiteUrl] = useState("https://example.com");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const canSend = useMemo(() => Boolean(question.trim()) && Boolean(websiteUrl.trim()) && !isLoading, [question, websiteUrl, isLoading]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSend) return;

    const userText = question.trim();
    setQuestion("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setIsLoading(true);

    try {
      const result = await askChat({
        sessionId,
        websiteUrl: websiteUrl.trim(),
        question: userText,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      const reason = err instanceof Error ? err.message : "Unknown error";
      setError(reason);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="chat-shell">
      <header className="chat-header">
        <h2>Website Agent</h2>
        <p>Ask questions grounded in live website content.</p>
      </header>

      <form className="url-form" onSubmit={onSubmit}>
        <label>
          Target URL
          <input value={websiteUrl} onChange={(e) => setWebsiteUrl(e.target.value)} placeholder="https://your-site.com" />
        </label>
      </form>

      <div className="messages">
        {messages.length === 0 ? <p className="empty-state">Start by entering a URL and asking a question.</p> : null}
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className={`message ${message.role}`}>
            <p>{message.text}</p>
            {message.sources && message.sources.length > 0 ? (
              <ul className="sources">
                {message.sources.map((source, sourceIndex) => (
                  <li key={`${source.url}-${sourceIndex}`}>
                    <a href={source.url} target="_blank" rel="noreferrer">
                      [{source.citation_id}] {source.title || source.url}
                    </a>
                    <span>{source.snippet}</span>
                    <span>Score: {source.score.toFixed(3)}</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </article>
        ))}
      </div>

      <form className="ask-form" onSubmit={onSubmit}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the website..."
          rows={3}
        />
        <button type="submit" disabled={!canSend}>
          {isLoading ? "Thinking..." : "Send"}
        </button>
      </form>

      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
