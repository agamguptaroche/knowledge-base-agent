# Knowledge Base Agent

A document-powered Q&A agent. Admins upload documents, users ask questions and get answers grounded in those documents.

**Stack:** FastAPI, React, OpenAI (text-embedding-3-small + gpt-4o-mini), FAISS

## Prerequisites

- Python 3.10+
- Node.js 18+ (only needed if modifying the frontend)
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

```bash
# 1. Create virtual environment and install dependencies
python3 -m venv venv
. venv/bin/activate
pip install -r backend/requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here
```

## Run the server

```bash
cd backend && . ../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open:

| Page | URL | Purpose |
|------|-----|---------|
| User chat | `http://localhost:8000/` | Ask questions against the knowledge base |
| Admin portal | `http://localhost:8000/admin` | Upload and manage documents |

## Supported document types

PDF, TXT, Markdown (.md), DOCX

## Rebuilding the frontend

Only needed if you modify files in `frontend/src/`:

```bash
cd frontend && npm install && npm run build
```

The built files are served automatically by the backend.
