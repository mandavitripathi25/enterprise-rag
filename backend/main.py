from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from . import vector_store, rag

app = FastAPI(title="Enterprise RAG Assistant (Groq)")


class Query(BaseModel):
    question: str
    history: list[dict] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    try:
        n = vector_store.add_document(file.filename, data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if n == 0:
        raise HTTPException(422, "No extractable text found in document.")
    return {"filename": file.filename, "chunks_indexed": n}


@app.post("/ask")
def ask(q: Query):
    if not q.question.strip():
        raise HTTPException(400, "Question is empty.")
    return rag.answer(q.question, q.history)


@app.get("/documents")
def documents():
    return {"documents": vector_store.list_documents()}


@app.delete("/documents/{filename}")
def delete(filename: str):
    vector_store.delete_document(filename)
    return {"deleted": filename}
