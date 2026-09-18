import ChatPanel from "./features/chat/ChatPanel";
import AnalyticsPanel from "./features/analytics/AnalyticsPanel";

const sessionId = `session-${Math.random().toString(36).slice(2, 10)}`;

export default function App() {
  return (
    <main className="app-root">
      <aside className="left-pane">
        <h1>Ness GPT</h1>
        <p>Agentic website chatbot powered by LangGraph and Bedrock.</p>
        <ul>
          <li>Real-time crawl per question</li>
          <li>SMTP email and Google Calendar via MCP</li>
          <li>Analytics dashboard and PDF reports</li>
        </ul>
      </aside>

      <section className="right-pane">
        <ChatPanel sessionId={sessionId} />
        <AnalyticsPanel sessionId={sessionId} />
      </section>
    </main>
  );
}
