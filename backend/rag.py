from groq import Groq
from . import config, vector_store

_client = Groq(api_key=config.GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are an enterprise document assistant. Answer ONLY using the provided context. "
    "Cite sources inline like [1], [2] matching the numbered context blocks. "
    "If the answer is not in the context, say you could not find it in the uploaded documents."
)


def answer(question: str, history: list[dict] | None = None) -> dict:
    hits = vector_store.search(question)
    if not hits:
        return {"answer": "No documents have been indexed yet.", "sources": []}

    context = "\n\n".join(
        f"[{i+1}] (source: {h['source']}, page: {h['page'] or 'n/a'})\n{h['text']}"
        for i, h in enumerate(hits)
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += (history or [])[-6:]
    messages.append(
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    )

    resp = _client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
    )
    return {
        "answer": resp.choices[0].message.content,
        "sources": [
            {"id": i + 1, "source": h["source"], "page": h["page"],
             "score": round(h["score"], 3), "snippet": h["text"][:300]}
            for i, h in enumerate(hits)
        ],
    }
