import io
from pypdf import PdfReader
from docx import Document


def extract_text(filename: str, data: bytes) -> list[tuple[str, int | None]]:
    """Return a list of (text, page_number) tuples."""
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return [(p.extract_text() or "", i + 1) for i, p in enumerate(reader.pages)]
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return [("\n".join(p.text for p in doc.paragraphs), None)]
    if name.endswith((".txt", ".md")):
        return [(data.decode("utf-8", errors="ignore"), None)]
    raise ValueError(f"Unsupported file type: {filename}")


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
