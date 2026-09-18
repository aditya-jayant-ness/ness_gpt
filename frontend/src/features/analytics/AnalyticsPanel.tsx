import { useEffect, useState } from "react";

import { analyticsPdfUrl, fetchAnalytics } from "../../services/api";

type Props = {
  sessionId: string;
};

type Summary = {
  session_id: string;
  total_messages: number;
  total_questions: number;
  avg_answer_length: number;
  crawl_count: number;
  tool_invocations: number;
};

export default function AnalyticsPanel({ sessionId }: Props) {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    fetchAnalytics(sessionId)
      .then(setSummary)
      .catch(() => setSummary(null));
  }, [sessionId]);

  return (
    <section className="analytics-shell">
      <div className="analytics-header">
        <h3>Chat Analysis</h3>
        <a href={analyticsPdfUrl(sessionId)} target="_blank" rel="noreferrer">
          Download PDF
        </a>
      </div>

      {!summary ? (
        <p>No analytics yet. Ask at least one question.</p>
      ) : (
        <div className="analytics-grid">
          <article><span>Total Messages</span><strong>{summary.total_messages}</strong></article>
          <article><span>Total Questions</span><strong>{summary.total_questions}</strong></article>
          <article><span>Avg Answer Length</span><strong>{summary.avg_answer_length.toFixed(1)}</strong></article>
          <article><span>Crawls</span><strong>{summary.crawl_count}</strong></article>
          <article><span>Tool Calls</span><strong>{summary.tool_invocations}</strong></article>
        </div>
      )}
    </section>
  );
}
