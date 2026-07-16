# Project Context

## Project Name

Odia Educational RAG Platform

## Goal

Build an enterprise-grade multilingual educational assistant for BSE Odisha curriculum.

The assistant should answer educational questions accurately using Retrieval-Augmented Generation (RAG) grounded on official textbooks.

The system should never rely on LLM memory when textbook evidence is available.

---

## Current Scope

Current implementation includes:

- PDF OCR
- Text extraction
- Chunking
- BGE-M3 embeddings
- Local Qdrant Vector DB
- OpenAI GPT-4o-mini
- Streamlit Chat UI
- Intent Router
- Educational RAG

---

## Current Problems

Current OCR extracts text only.

Missing metadata:

- page number
- chapter number
- chapter title
- section heading
- subsection heading

Current chunking uses RecursiveCharacterTextSplitter.

Current retrieval is pure dense vector search.

Hallucinations occur because retrieved chunks often lack sufficient contextual metadata.

---

## Target Architecture

OCR

↓

Metadata Extraction

↓

Hierarchical Chunking

↓

Embeddings

↓

Qdrant Payload

↓

Hybrid Retrieval

↓

Cross Encoder Reranker

↓

LLM

↓

Grounded Answer

---

## Primary Objective

Improve retrieval quality before improving generation.

Retrieval quality is currently the biggest bottleneck.

Generation should always be grounded on retrieved textbook evidence.
