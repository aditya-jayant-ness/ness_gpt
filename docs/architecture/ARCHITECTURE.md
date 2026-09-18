# Architecture

## Overview

The system is a local-first monorepo with separate frontend and backend services.

1. Frontend (React)
- Collects target website URL and user question.
- Calls backend chat API.
- Renders assistant answers and source snippets.
- Shows analytics summary and allows PDF report download.

2. Backend (FastAPI)
- Exposes REST APIs for chat, integrations, and analytics.
- Runs LangGraph orchestration for URL-grounded responses.
- Uses Bedrock Nova Pro through langchain-aws.
- Provides internal MCP tool dispatch for SMTP and Google Calendar.

3. Crawler Service
- Fetches latest HTML for requested URL.
- Extracts title and text chunks for grounding context.

4. Integrations
- SMTP email via standard SMTP transport.
- Google Calendar event creation via Google Calendar API.

5. Analytics
- Tracks session-level message and tool usage metrics.
- Generates downloadable PDF summaries.

## Core Runtime Flow

1) User submits URL + question.
2) Chat graph node crawls website content.
3) Context chunks are passed to Nova Pro.
4) Generated answer and sources are returned.
5) Analytics events are tracked.
6) Optional integration actions happen through MCP tool calls.

## Deployment

- Local prototype with two processes:
  - backend on port 8000
  - frontend on port 5173
