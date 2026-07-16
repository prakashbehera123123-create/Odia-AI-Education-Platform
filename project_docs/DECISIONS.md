# Architectural Decisions

## Embedding Model

Chosen

BAAI/bge-m3

Reason

Excellent multilingual retrieval for Odia.

---

## Vector Database

Chosen

Qdrant

Reason

Payload filtering

Local deployment

Fast similarity search

---

## Chunking

Chosen

Hierarchical

Reason

Educational textbooks have natural structure.

---

## OCR

Chosen

PyMuPDF + Tesseract

Reason

Offline

Supports Odia

---

## Retrieval

Current

Dense

Future

Hybrid

Reason

Reduce hallucinations.

Improve recall.

---

## Metadata

Stored in Qdrant Payload

Reason

Fast filtering.
