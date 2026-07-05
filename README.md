# GeM Tender Discovery & Extraction Pipeline

A production-oriented, cost-optimized procurement intelligence pipeline for discovering, processing, extracting, and classifying Government e-Marketplace (GeM) tenders using deterministic filtering and pluggable LLM providers.

> **Core Principle:** *Spend tokens last, not first.*

The pipeline progressively filters tenders using deterministic logic before invoking an LLM, minimizing API cost while maintaining high-quality structured extraction.

---

# Project Status

**Current Phase:** MVP V1 (≈90% Complete)

### ✅ Completed

* GeM Tender Discovery
* PostgreSQL Data Model
* Bid Persistence
* Keyword Prefilter
* Document Download
* PDF Text Extraction
* Content Cleaning
* Content Hash Gate
* LLM Extraction Pipeline
* Multi-provider LLM Support
* Automatic LLM Fallback
* Bid Classification
* Company Profile Matching
* Pipeline Metrics & Cost Accounting
* Airflow-ready Pipeline Entrypoint

### 🚧 In Progress

* Google Gemini Flash Integration
* Slack Digest
* Human Review Workflow
* Airflow Production Scheduling
* Prompt Tuning
* Keyword Optimization

---

# Architecture

```
                        GeM Tender Discovery Pipeline

                     ┌──────────────────────────────┐
                     │      GeM Listing API         │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │      1. Bid Discovery        │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   2. Keyword Prefilter       │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   3. Document Download       │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │    4. Text Extraction        │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │    5. Content Hash Gate      │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │    6. LLM Extraction         │
                     │                              │
                     │  • Ollama                   │
                     │  • OpenAI                   │
                     │  • Gemini Flash (Planned)   │
                     │  • Fake Provider            │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │    7. Bid Classification     │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Review Queue / Slack Digest  │
                     │      (Planned)               │
                     └──────────────────────────────┘
```

---

# Features

* End-to-end GeM tender discovery pipeline
* Cost-first LLM architecture
* PostgreSQL persistence
* Repository-Service architecture
* Versioned LLM extractions
* Versioned company profiles
* Deterministic keyword filtering
* Content hash-based deduplication
* PDF download and text extraction
* Automatic LLM fallback
* Multi-provider LLM abstraction
* Token accounting
* Cost accounting
* Airflow-ready orchestration
* Structured pipeline metrics

---

# Quick Start

## Prerequisites

* Python 3.11+
* PostgreSQL 15+
* Git

Optional

* Ollama
* OpenAI API Key
* Google Gemini API Key

---

## Installation

```bash
git clone <repository-url>

cd gem_pipeline

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Configuration

Copy the template

```bash
copy .env.example .env
```

or

```bash
cp .env.example .env
```

Supported providers

```
fake
openai
ollama
gemini
```

---

## Database

Create database

```bash
createdb gem_pipeline
```

Initialize schema

```bash
python -m app.db.init_db
```

---

# Running the Pipeline

Run complete pipeline

```bash
python -m app.cli.test_gem_pipeline
```

Run with custom limit

```bash
python -m app.cli.test_gem_pipeline 50
```

---

# Pipeline Stages

## Stage 1 — Bid Discovery

* Fetches latest GeM listings
* Parses listing metadata
* Stores bids in PostgreSQL
* Records pipeline events

---

## Stage 2 — Keyword Prefilter

Uses deterministic include/exclude keyword scoring.

```
Score = Include Matches − (2 × Exclude Matches)
```

Only bids with positive scores proceed.

---

## Stage 3 — Document Download

* Builds GeM document URLs
* Downloads PDFs
* Computes SHA256 content hash
* Stores metadata

---

## Stage 4 — Text Extraction

Uses

* pdfplumber
* pdfminer
* pypdf

Features

* PDF validation
* Signature validation
* Empty file detection
* Text cleaning
* SHA256 text hash

---

## Stage 5 — Content Hash Gate

Skips LLM calls when document text has not changed.

Benefits

* Avoids duplicate processing
* Reduces LLM cost
* Detects corrigenda

---

## Stage 6 — LLM Extraction

Supported providers

| Provider     | Status     |
| ------------ | ---------- |
| Fake         | ✅          |
| Ollama       | ✅          |
| OpenAI       | ✅          |
| Gemini Flash | 🚧 Planned |

Features

* Structured JSON extraction
* Automatic fallback
* Token accounting
* Cost accounting
* Prompt versioning

---

## Stage 7 — Bid Classification

Scores extracted tenders against

* preferred keywords
* excluded keywords
* company profile

Stores

* confidence
* relevance
* decision reason

---

# Database Schema

```
bids
│
├── bid_documents
│
├── bid_extractions
│      │
│      └── bid_classifications
│
├── bid_events
│
└── bid_reviews

company_profiles

pipeline_runs
```

---

# Database Tables

| Table               | Purpose                |
| ------------------- | ---------------------- |
| bids                | Tender metadata        |
| bid_documents       | Downloaded documents   |
| bid_events          | Audit trail            |
| bid_extractions     | Structured LLM output  |
| bid_classifications | Relevance scoring      |
| bid_reviews         | Human review           |
| company_profiles    | Company capabilities   |
| pipeline_runs       | Pipeline observability |

---

# LLM Providers

| Provider     | Purpose                     |
| ------------ | --------------------------- |
| Fake         | Integration testing         |
| Ollama       | Local inference             |
| OpenAI       | Cloud inference             |
| Gemini Flash | Planned production provider |

Provider selection

```
LLM_PROVIDER=fake

LLM_PROVIDER=openai

LLM_PROVIDER=ollama

LLM_PROVIDER=gemini
```

---

# Technology Stack

### Backend

* Python 3.11
* PostgreSQL
* SQLAlchemy 2.x

### LLM

* LangChain
* Ollama
* OpenAI
* Google Gemini Flash (planned)

### Document Processing

* pdfplumber
* pdfminer
* pypdf

### Infrastructure

* Apache Airflow
* PostgreSQL
* LocalExecutor

### Testing

* Pytest
* Ruff
* Black
* MyPy

---

# Project Structure

```
gem_pipeline/

├── airflow/
│   └── dags/

├── app/
│   ├── cli/
│   ├── config.py
│   ├── db/
│   ├── documents/
│   ├── filters/
│   ├── llm/
│   ├── pipelines/
│   ├── repositories/
│   ├── services/
│   └── sources/

├── configs/

├── data/
│   └── raw/
│       └── gem/

├── requirements/

├── scripts/

├── tests/

├── .env.example

├── requirements.txt

└── README.md
```

---

# Airflow

The DAG invokes a **single canonical pipeline entrypoint**

```
run_gem_pipeline()
```

No duplicate orchestration logic exists.

---

# CLI Commands

| Command                                             | Description       |
| --------------------------------------------------- | ----------------- |
| python -m app.cli.test_gem_pipeline                 | Complete pipeline |
| python -m app.cli.test_gem_discovery                | Discovery         |
| python -m app.cli.test_keyword_prefilter            | Keyword filtering |
| python -m app.cli.test_gem_document_download        | Document download |
| python -m app.cli.test_gem_document_text_processing | Text extraction   |
| python -m app.cli.test_content_hash_gate            | Content hash gate |
| python -m app.cli.test_llm_extraction               | LLM extraction    |
| python -m app.cli.test_post_classification          | Classification    |

---

# Example Pipeline Summary

```python
{
    "bids_scanned": 20,
    "bids_relevant": 3,
    "documents_downloaded": 3,
    "documents_processed": 2,
    "documents_failed_text_extraction": 1,
    "llm_candidates": 2,
    "llm_success": 2,
    "llm_failed": 0,
    "llm_fallback_used": 0,
    "llm_estimated_cost_inr": Decimal("0.0024"),
    "run_status": "success"
}
```

---

# Troubleshooting

### Ollama unavailable

```
RuntimeError:
Ollama server is not running
```

Start

```bash
ollama serve
```

---

### Model missing

```
ValueError:
Configured model not found
```

Pull model

```bash
ollama pull qwen3:4b
```

---

### Database

```bash
psql -U postgres -d gem_pipeline
```

---

### Seed Company Profile

```bash
python -m app.db.init_db
```

---

# Roadmap

## MVP V1

* ✅ Discovery
* ✅ Persistence
* ✅ Keyword Filtering
* ✅ Document Download
* ✅ PDF Processing
* ✅ Content Hash Gate
* ✅ LLM Extraction
* ✅ Bid Classification
* 🚧 Google Gemini Flash
* 🚧 Slack Digest
* 🚧 Human Review Workflow

---

## MVP V2

* FastAPI Review UI
* CPPP Adapter
* OCR Support
* Bid Response Drafting
* Semantic Search
* Reviewer Feedback Learning
* Multi-source Procurement Discovery

---

# Current Progress

| Area                | Status |
| ------------------- | ------ |
| Discovery Pipeline  | ✅      |
| Document Processing | ✅      |
| LLM Integration     | ✅      |
| Cost Optimization   | ✅      |
| Classification      | ✅      |
| Airflow Integration | 🚧     |
| Gemini Flash        | 🚧     |
| Human Review        | 🚧     |

**Overall MVP V1 Completion:** **~90%**

---

# License

This project is currently being developed as part of a Government Procurement Automation initiative focused on intelligent tender discovery, extraction, and bid qualification.
