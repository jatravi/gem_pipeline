# GeM Tender Discovery Pipeline

An end-to-end pipeline for discovering public tenders from the Government e-Marketplace (GeM), filtering them through multiple low-cost stages, downloading bid documents, extracting document text, and preparing only qualified tenders for downstream LLM-based extraction and classification.

---

# Overview

The project is built as a staged pipeline that minimizes unnecessary processing by progressively filtering bids before expensive AI operations.

Current pipeline:

```
Discover Bids
      ↓
Persist Bid Metadata
      ↓
Keyword Prefilter
      ↓
Candidate Selection
      ↓
Document Download
      ↓
Document Persistence
      ↓
PDF Text Extraction
      ↓
Text Cleaning
      ↓
Content Hash Gate
      ↓
LLM Candidates
      ↓
(Next)
LLM Extraction
      ↓
Bid Classification
      ↓
Review Workflow
```

---

# Current Capabilities

## Discovery

* Discover GeM tenders
* Parse bid metadata
* Persist bids into PostgreSQL
* Track discovery events
* Track pipeline runs

---

## Persistence

Persists data into:

* bids
* pipeline_runs
* bid_events

---

## Keyword Prefilter

Config-driven keyword filtering.

Supports:

* include keywords
* exclude keywords
* keyword scoring
* candidate selection

Configuration files:

```
configs/
    keyword_include.txt
    keyword_exclude.txt
```

Only relevant bids continue through the pipeline.

---

## Document Processing

Uses GeM source identifiers to:

* build document URLs
* download PDFs
* persist document metadata
* update existing documents
* compute content hashes

Documents are stored in:

```
bid_documents
```

---

## PDF Processing

Uses pdfplumber to:

* extract raw text
* clean extracted text
* compute SHA-256 text hash
* persist processed document data

Stored fields include:

* raw_text
* cleaned_text
* text_hash
* page_count
* extraction_method
* processing_status

---

## Content Hash Gate

Prevents unnecessary downstream LLM work.

Compares:

* previous processed hash
* current processed hash

If unchanged:

```
Skip LLM
```

Otherwise:

```
Proceed to LLM extraction
```

---

# Current Pipeline

```
GeM Listing
      │
      ▼
Discovery
      │
      ▼
Bid Persistence
      │
      ▼
Keyword Prefilter
      │
      ▼
Relevant Candidates
      │
      ▼
Document Download
      │
      ▼
Downloaded Documents
      │
      ▼
Text Extraction
      │
      ▼
Processed Documents
      │
      ▼
Content Hash Gate
      │
      ▼
LLM Candidates
```

---

# Project Status

## Completed

### Discovery

* GeM listing parser
* Bid persistence
* Pipeline runs
* Bid events

### Filtering

* Config-driven keyword prefilter
* Candidate selection

### Documents

* Direct GeM document download
* Document persistence
* Document upsert
* PDF text extraction
* Text cleaning
* SHA-256 hashing

### Pipeline

* End-to-end discovery pipeline
* Stage-wise orchestration
* Candidate propagation between stages

---

## Next Stage

* LLM Extraction Pipeline
* bid_extractions persistence

---

## Planned

* Bid classification
* Human review workflow
* Retry policies
* Better document versioning
* Airflow production orchestration

---

# Repository Structure

```
app/
│
├── cli/
├── db/
├── documents/
├── filters/
├── pipelines/
├── repositories/
├── schemas/
├── services/
└── sources/
    └── gem/

configs/

data/
    raw/
```

---

# Core Database Tables

* bids
* pipeline_runs
* bid_events
* bid_documents
* bid_extractions
* bid_classifications
* bid_reviews

---

# Technology Stack

* Python
* PostgreSQL
* SQLAlchemy
* Requests
* pdfplumber

Future:

* OpenAI / OpenRouter
* LangChain (optional)
* Apache Airflow

---

# Running the Pipeline

Run the complete pipeline:

```bash
python -m app.cli.test_gem_pipeline
```

Pipeline stages:

1. Discover bids
2. Keyword prefilter
3. Candidate selection
4. Document download
5. Text extraction
6. Content hash gate

Example output:

```
20 bids scanned
↓
1 relevant candidate
↓
1 document downloaded
↓
1 document processed
↓
1 LLM candidate
```

---

# Individual Test CLIs

Discovery

```bash
python -m app.cli.test_gem_discovery
```

Keyword Pipeline

```bash
python -m app.cli.test_keyword_prefilter_pipeline
```

Document Download

```bash
python -m app.cli.test_gem_document_download
```

Document Processing

```bash
python -m app.cli.test_gem_document_text_processing
```

Content Hash Gate

```bash
python -m app.cli.test_content_hash_gate
```

Complete Pipeline

```bash
python -m app.cli.test_gem_pipeline
```

---

# Development Philosophy

The project follows a staged pipeline architecture.

Each stage:

* has a single responsibility
* persists intermediate artifacts
* returns outputs to the next stage
* minimizes downstream cost
* remains independently testable

The goal is to ensure only high-value candidate tenders reach the LLM extraction stage.

---

# Roadmap

## Stage 1 ✅

* Discovery
* Persistence
* Events

## Stage 2 ✅

* Keyword filtering
* Candidate selection

## Stage 3 ✅

* Document download
* PDF processing
* Content hash gate

## Stage 4 (Next)

* LLM extraction
* bid_extractions

## Stage 5

* Bid classification
* bid_classifications

## Stage 6

* Human review
* bid_reviews

---


