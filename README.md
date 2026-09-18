# Ness GPT

Website-grounded chatbot prototype with LangGraph orchestration, Amazon Nova Pro on AWS Bedrock, real-time website crawling per query, SMTP email and Google Calendar integrations via an internal MCP tool server, and chat analytics with PDF reporting.

## Monorepo Layout

- frontend: React + Vite UI
- backend: FastAPI + LangGraph orchestration and integrations
- docs: architecture and API notes

## Quick Start

1) Create .env at project root from .env.example.
2) Backend setup:
   - cd backend
   - pip install -r requirements.txt
   - uvicorn app.main:app --reload --port 8000
3) Frontend setup:
   - cd frontend
   - npm install
   - npm run dev
4) Open http://localhost:5173

## Current Implementation Scope

- Chat endpoint that crawls the target URL and answers with Bedrock Nova Pro.
- Internal MCP tool registry with:
  - send_email (SMTP)
  - create_calendar_event (Google Calendar)
- Analytics endpoint and downloadable PDF report per session.

## Next Build Iterations

- Add richer LangGraph routing for automatic tool invocation based on intent.
- Expand crawler with multi-page traversal and JS-render fallback.
- Add persistent DB models and auth/session management.
- Improve UI parity against provided Figma references.
