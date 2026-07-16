from __future__ import annotations

import uuid
import os
import streamlit as st
from configs.settings import EmbeddingSettings, RetrievalSettings
from rag.logging_config import configure_logging
from app.orchestrator import QueryOrchestrator
from app.retrieval import QdrantRetriever


configure_logging()


def get_orchestrator(threshold: float) -> QueryOrchestrator:
    settings = RetrievalSettings(similarity_threshold=threshold)
    return QueryOrchestrator(retriever=QdrantRetriever(settings=settings))


st.set_page_config(page_title="Odia Educational RAG", page_icon=":books:", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

embedding_settings = EmbeddingSettings()

with st.sidebar:
    st.title("RAG Settings")
    model_name = st.text_input("Model name", value="gpt-4o-mini")
    os.environ["OPENAI_MODEL"] = model_name
    top_k = st.slider("Top K", min_value=1, max_value=15, value=5)
    threshold = st.slider("Retrieval threshold", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    st.caption(f"Vector DB: {embedding_settings.qdrant_db_path}")
    st.caption(f"Collection: {embedding_settings.collection_name}")
    st.caption(f"Embedding: {embedding_settings.embedding_model}")
    st.caption(f"Session: {st.session_state.session_id}")
    if st.button("Reset conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_result = None
        st.rerun()

st.title("Odia Educational AI Tutor")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["message"])

query = st.chat_input("Ask a question in Odia...")
if query:
    st.session_state.messages.append({"role": "user", "message": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and generating answer..."):
            orchestrator = get_orchestrator(threshold)
            try:
                result = orchestrator.ask(
                    query=query,
                    session_id=st.session_state.session_id,
                    conversation_history=st.session_state.messages[:-1],
                    top_k=top_k,
                )
            finally:
                orchestrator.close()
            answer = result["answer"]
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "message": answer})
            st.session_state.last_result = result

if st.session_state.last_result:
    result = st.session_state.last_result
    with st.expander("Retrieval debug", expanded=False):
        retrieval_debug = result.get("retrieval_debug", {})
        st.subheader("Intent")
        st.code(result.get("intent", "unknown"))
        st.subheader("Filtering")
        st.write(
            {
                "total_retrieved": retrieval_debug.get("total_retrieved", len(result["retrieved_chunks"])),
                "filtered_count": retrieval_debug.get("filtered_count", len(result["retrieved_chunks"])),
                "deduped_count": retrieval_debug.get("deduped_count", len(result["retrieved_chunks"])),
                "similarity_threshold": retrieval_debug.get("similarity_threshold"),
                "similarity_scores": retrieval_debug.get("similarity_scores", []),
                "used_filter_fallback": retrieval_debug.get("used_filter_fallback", False),
            }
        )
        st.subheader("Retrieved chunks")
        for index, chunk in enumerate(result["retrieved_chunks"], start=1):
            payload = chunk["payload"]
            st.markdown(f"**Chunk {index} | score={chunk['score']:.4f}**")
            st.caption(
                f"class={payload.get('class')} subject={payload.get('subject')} "
                f"chapter={payload.get('chapter')} page={payload.get('page')}"
            )
            st.write(payload.get("text", ""))
        st.subheader("Generated context")
        st.text_area("Context", result["context"], height=300)
        st.subheader("Prompt preview")
        st.json(result.get("prompt_preview", []))
