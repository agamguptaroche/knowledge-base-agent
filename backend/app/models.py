from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
from datetime import datetime
from app.config import DATA_DIR

DOCUMENTS_DB = DATA_DIR / "documents.json"


class Document(BaseModel):
    id: str
    filename: str
    original_name: str
    upload_date: str
    chunk_count: int = 0
    status: str = "processing"  # processing, ready, error


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


def load_documents() -> list[Document]:
    if not DOCUMENTS_DB.exists():
        return []
    with open(DOCUMENTS_DB, "r") as f:
        data = json.load(f)
    return [Document(**d) for d in data]


def save_documents(docs: list[Document]):
    with open(DOCUMENTS_DB, "w") as f:
        json.dump([d.model_dump() for d in docs], f, indent=2)


def add_document(doc: Document):
    docs = load_documents()
    docs.append(doc)
    save_documents(docs)


def update_document(doc_id: str, **kwargs):
    docs = load_documents()
    for d in docs:
        if d.id == doc_id:
            for k, v in kwargs.items():
                setattr(d, k, v)
            break
    save_documents(docs)


def delete_document_record(doc_id: str):
    docs = load_documents()
    docs = [d for d in docs if d.id != doc_id]
    save_documents(docs)
