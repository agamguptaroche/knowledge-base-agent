"""Handles document parsing, chunking, and text extraction."""

from pathlib import Path
from PyPDF2 import PdfReader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(filepath)
    elif suffix == ".txt":
        return filepath.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".md":
        return filepath.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".docx":
        return _extract_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(filepath: Path) -> str:
    reader = PdfReader(str(filepath))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def _extract_docx(filepath: Path) -> str:
    from docx import Document
    doc = Document(str(filepath))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
