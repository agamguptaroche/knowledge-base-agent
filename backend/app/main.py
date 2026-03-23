"""FastAPI application — admin document management + user query endpoints."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import UPLOAD_DIR, TOP_K
from app.models import (
    Document, QueryRequest, QueryResponse,
    load_documents, add_document, update_document, delete_document_record,
)
from app.document_processor import extract_text, chunk_text
from app.vector_store import vector_store
from app.openai_client import get_embeddings, get_single_embedding, chat_with_context

app = FastAPI(title="Knowledge Base Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React build
FRONTEND_BUILD = Path(__file__).resolve().parent.parent.parent / "frontend" / "build"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


# ── Admin endpoints ──────────────────────────────────────────────────────────

@app.post("/api/admin/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    doc_id = str(uuid.uuid4())
    safe_name = f"{doc_id}{ext}"
    filepath = UPLOAD_DIR / safe_name

    content = await file.read()
    filepath.write_bytes(content)

    doc = Document(
        id=doc_id,
        filename=safe_name,
        original_name=file.filename,
        upload_date=datetime.utcnow().isoformat(),
        status="processing",
    )
    add_document(doc)

    # Process synchronously for simplicity
    try:
        text = extract_text(filepath)
        chunks = chunk_text(text)
        if not chunks:
            update_document(doc_id, status="error", chunk_count=0)
            raise HTTPException(400, "No text could be extracted from the document.")

        embeddings = get_embeddings(chunks)
        vector_store.add(embeddings, chunks, doc_id, file.filename)
        update_document(doc_id, status="ready", chunk_count=len(chunks))
    except HTTPException:
        raise
    except Exception as e:
        update_document(doc_id, status="error")
        raise HTTPException(500, f"Processing failed: {str(e)}")

    return {"id": doc_id, "filename": file.filename, "chunks": len(chunks), "status": "ready"}


@app.get("/api/admin/documents")
async def list_documents():
    return load_documents()


@app.delete("/api/admin/documents/{doc_id}")
async def delete_document(doc_id: str):
    docs = load_documents()
    doc = next((d for d in docs if d.id == doc_id), None)
    if not doc:
        raise HTTPException(404, "Document not found")

    # Remove file
    filepath = UPLOAD_DIR / doc.filename
    if filepath.exists():
        filepath.unlink()

    # Remove from vector store and DB
    vector_store.delete_by_doc_id(doc_id)
    delete_document_record(doc_id)
    return {"status": "deleted"}


# ── User endpoints ───────────────────────────────────────────────────────────

@app.post("/api/query", response_model=QueryResponse)
async def query_knowledge_base(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    docs = load_documents()
    ready_docs = [d for d in docs if d.status == "ready"]
    if not ready_docs:
        return QueryResponse(
            answer="No documents have been uploaded to the knowledge base yet. Please ask an admin to upload documents first.",
            sources=[],
        )

    query_embedding = get_single_embedding(req.question)
    results = vector_store.search(query_embedding, top_k=TOP_K)

    if not results:
        return QueryResponse(
            answer="I couldn't find any relevant information in the knowledge base for your question.",
            sources=[],
        )

    answer = chat_with_context(req.question, results)
    sources = list(set(r["filename"] for r in results))
    return QueryResponse(answer=answer, sources=sources)


@app.get("/api/health")
async def health():
    docs = load_documents()
    return {
        "status": "ok",
        "documents": len(docs),
        "ready": len([d for d in docs if d.status == "ready"]),
        "total_vectors": vector_store.index.ntotal,
    }


# ── Serve React frontend ────────────────────────────────────────────────

if FRONTEND_BUILD.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        file_path = FRONTEND_BUILD / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_BUILD / "index.html"))
