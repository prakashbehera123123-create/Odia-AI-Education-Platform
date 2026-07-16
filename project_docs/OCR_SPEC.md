# OCR & Document Understanding Specification

## Purpose

The OCR module is responsible for converting curriculum PDF pages into structured educational documents.

This stage is **not limited to text extraction**.

It must preserve the logical structure of the textbook so downstream stages (chunking, embedding, retrieval, and answer generation) have access to rich metadata.

---

# Objective

Transform each PDF page into a structured document containing:

- Clean OCR text
- Page metadata
- Chapter metadata
- Section hierarchy
- Document structure
- Layout information

The output of this stage becomes the input for the chunking pipeline.

---

# Current Implementation

Current pipeline:

PDF
↓

PyMuPDF

↓

Page Image

↓

Tesseract OCR

↓

Raw Text

↓

Cleaning

Current limitations:

- Page number is not extracted
- Chapter name is not detected
- Chapter number is not detected
- Section headings are lost
- Subsection headings are lost
- Layout information is discarded
- OCR confidence is ignored
- Images/tables are ignored

---

# Target Architecture

PDF

↓

PyMuPDF

↓

Page Image

↓

OCR

↓

Document Understanding

↓

Metadata Extraction

↓

Structured Page JSON

↓

Chunking

---

# Responsibilities

The OCR module MUST:

## 1. Extract Text

Extract all readable text from the page.

Requirements

- Preserve paragraph order.
- Preserve line order.
- Preserve Unicode.
- Preserve Odia characters.
- Remove OCR artifacts.
- Normalize whitespace.

---

## 2. Extract Page Metadata

Each page must contain:

- page_number
- subject
- class
- board
- language
- source_pdf

Example

Page 42

Subject = History

Language = Odia

---

## 3. Detect Chapter Information

The OCR pipeline should detect:

Chapter Number

Chapter Name

Example

Chapter Number = 7

Chapter Name = ରୁଷ ବିପ୍ଳବ

If no new chapter exists on the page,
inherit the previous chapter.

---

## 4. Detect Section Headings

Detect educational headings.

Example

Causes

Effects

Summary

Exercises

These headings must become metadata.

---

## 5. Detect Subsections

Example

Russian Revolution

↓

Causes

↓

Economic Causes

↓

Political Causes

Maintain the hierarchy.

---

## 6. Detect Educational Blocks

Identify

- Questions
- Exercises
- Examples
- Notes
- Tables
- Images
- Captions

Future retrieval may use these separately.

---

## 7. OCR Cleaning

Normalize:

Unicode

Punctuation

Extra spaces

Broken lines

Hyphenated words

Incorrect OCR characters

---

# Output Schema

Every page MUST produce exactly one structured JSON object.

Example

{
    "page": 42,

    "class": 10,

    "board": "BSE Odisha",

    "subject": "History",

    "language": "odia",

    "chapter_number": 7,

    "chapter_name": "ରୁଷ ବିପ୍ଳବ",

    "section": "Causes",

    "subsection": "Political Causes",

    "text": "...",

    "images": [],

    "tables": [],

    "source": "history.pdf"
}

---

# Metadata Extraction Rules

Metadata should be extracted using:

1. Visual Layout

Large bold text

Centered headings

Font size

2. Text Patterns

Chapter keywords

Roman numerals

Numeric headings

3. Previous Page Context

If a page has no chapter title,
inherit the previous chapter metadata.

---

# Current Metadata Assumptions

Until layout-aware OCR is added, the OCR pipeline uses conservative text-pattern extraction.

- Board defaults to `BSE Odisha` when no explicit board is supplied.
- Language defaults to `odia` when `ori` is present in the configured OCR language list.
- Chapter detection requires explicit chapter keywords such as `Chapter`, `ଅଧ୍ୟାୟ`, or `ପାଠ`.
- Section and subsection detection uses numbered headings and known educational headings such as exercises, summary, and questions.
- If chapter, section, or subsection cannot be detected on a page, the previous page metadata is inherited.
- If metadata is still missing after inheritance, the page is preserved and a warning is logged.
- The OCR stage keeps backward-compatible `.txt` page files and additionally writes `structured_pages/page_###.json` plus `structured_pages.json`.

---

# OCR Quality Requirements

Minimum accuracy target

95%

Unicode preservation

100%

Paragraph order

100%

Page number accuracy

100%

Chapter detection

100%

---

# Error Handling

If OCR confidence is low:

Log warning.

Store raw OCR.

Do NOT discard the page.

If chapter cannot be detected:

Use previous page chapter.

If page number missing:

Infer from PDF ordering.

---

# Future Improvements (no need to do it right now)


LayoutParser

Document AI

Table Detection

Image Caption Extraction

Formula Recognition

Diagram Detection

Figure References

---

# Success Criteria

The OCR stage is complete only if every page contains:

✓ Clean text

✓ Page number

✓ Subject

✓ Chapter number

✓ Chapter name

✓ Section

✓ Subsection

✓ Source file

✓ Language

The output must be immediately consumable by the chunking module without additional document understanding.
