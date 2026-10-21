import os
import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Enterprise RAG Assistant", page_icon="📚", layout="wide")
st.title("📚 Enterprise RAG Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("Upload PDF, DOCX, TXT, MD", accept_multiple_files=True,
                             type=["pdf", "docx", "txt", "md"])
    if st.button("Index documents") and files:
        for f in files:
            with st.spinner(f"Indexing {f.name}..."):
                r = requests.post(f"{BACKEND}/upload", files={"file": (f.name, f.getvalue())})
            if r.ok:
                st.success(f"{f.name}: {r.json()['chunks_indexed']} chunks")
            else:
                st.error(f"{f.name}: {r.json().get('detail', r.text)}")

    st.divider()
    try:
        docs = requests.get(f"{BACKEND}/documents", timeout=5).json()["documents"]
    except Exception:
        docs = []
        st.warning("Backend not reachable.")
    for d in docs:
        c1, c2 = st.columns([4, 1])
        c1.write(f"📄 {d}")
        if c2.button("🗑", key=f"del-{d}"):
            requests.delete(f"{BACKEND}/documents/{d}")
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        for s in m.get("sources", []):
            with st.expander(f"[{s['id']}] {s['source']} (page {s['page'] or 'n/a'}, score {s['score']})"):
                st.write(s["snippet"])

if prompt := st.chat_input("Ask a question about your documents"):
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            r = requests.post(f"{BACKEND}/ask", json={"question": prompt, "history": history})
        if r.ok:
            data = r.json()
            st.markdown(data["answer"])
            for s in data["sources"]:
                with st.expander(f"[{s['id']}] {s['source']} (page {s['page'] or 'n/a'}, score {s['score']})"):
                    st.write(s["snippet"])
            st.session_state.messages.append(
                {"role": "assistant", "content": data["answer"], "sources": data["sources"]})
        else:
            st.error(r.text)
