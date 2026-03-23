"""OpenAI API wrapper for embeddings and chat completions."""

from openai import OpenAI
from app.config import OPENAI_API_KEY, EMBEDDING_MODEL, CHAT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a list of text chunks. Batches automatically."""
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


def get_single_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def chat_with_context(question: str, context_chunks: list[dict]) -> str:
    """Answer a question using retrieved document chunks as context."""
    context_text = "\n\n---\n\n".join(
        f"[Source: {c['filename']}]\n{c['text']}" for c in context_chunks
    )

    system_prompt = (
        "You are a knowledgeable assistant that answers questions based on the provided documents. "
        "Use ONLY the information from the provided context to answer. "
        "If the answer cannot be found in the context, say so clearly. "
        "Cite the source document names when possible."
    )

    user_prompt = f"""Context from knowledge base documents:

{context_text}

---

Question: {question}

Answer based on the above context:"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message.content
