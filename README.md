# Enterprise RAG Assistant (Groq)

Stack: FastAPI + Streamlit + ChromaDB + Groq (LLM) + sentence-transformers (local embeddings) + Docker.

## Run with Docker
    cp .env.example .env   # add GROQ_API_KEY
    docker compose up --build
UI: http://localhost:8501  |  API docs: http://localhost:8000/docs

## Run locally
    pip install -r requirements.txt
    uvicorn backend.main:app --reload
    streamlit run frontend/app.py
