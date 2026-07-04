# GeM Tender Discovery & Extraction Pipeline

An end-to-end pipeline for discovering public tenders from the Government e-Marketplace (GeM), filtering them through multiple low-cost stages, downloading bid documents, extracting text, running LLM-based structured extraction, and classifying bids for human review.

---

## Overview

The project follows a **"spend tokens last, not first"** design — progressively filtering bids through cheap stages before invoking expensive LLM calls.

```
┌──────────────────────────────────────────────────────────┐
│                   GeM Discovery Pipeline                 │
│                                                          │
│  1. Discovery     ─  Scrape GeM listing pages            │
│         ↓                                                │
│  2. Keyword Filter ─  Config-driven include/exclude      │
│         ↓                                                │
│  3. Doc Download   ─  Fetch PDFs from GeM                │
│         ↓                                                │
│  4. Text Extraction─  pdfplumber + validation guards     │
│         ↓                                                │
│  5. Content Hash   ─  Skip unchanged documents           │
│         ↓                                                │
│  6. LLM Extraction ─  Ollama / OpenAI / Fake fallback    │
│         ↓                                                │
│  7. Classification ─  Score against company profile      │
│         ↓                                                │
│  ✔ Review-ready bids                                     │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- (Optional) Ollama for local LLM or OpenAI API key

### Installation

```bash
# Clone and set up virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements/base.txt

# Copy environment template and edit
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/macOS
```

### Database Setup

```bash
# Create the PostgreSQL database
createdb gem_pipeline

# Initialize schema and seed default company profile
python -m app.db.init_db
```

### Run the Pipeline

```bash
# Run complete 7-stage pipeline (default: 20 bid limit)
python -m app.cli.test_gem_pipeline

# Custom limit
python -m app.cli.test_gem_pipeline 50
```

### Run Tests

```bash
python -m pytest tests/ -v
```

---

## Pipeline Stages

### 1. Discovery
- Scrapes GeM listing pages and persists bid metadata to PostgreSQL.
- Tracks pipeline runs and bid events.

### 2. Keyword Prefilter
- Config-driven include/exclude keyword matching.
- Scoring formula: `score = includes − (2 × excludes)`. Only bids with `score > 0` proceed.
- Configuration files: `configs/keyword_include.txt`, `configs/keyword_exclude.txt`

### 3. Document Download
- Builds document URLs from GeM source identifiers.
- Downloads PDFs to `data/raw/gem/`.
- Computes content hashes and persists to `bid_documents`.

### 4. Text Extraction
- Uses **pdfplumber** to extract raw text.
- **PDF guardrails**: validates file existence, non-zero size, and `%PDF-` magic bytes.
- Invalid PDFs are marked as failed (not crash-causing).
- Cleans text (CRLF normalization, whitespace collapse) and computes SHA-256 hash.

### 5. Content Hash Gate
- Compares current text hash with previous run's hash.
- Documents with unchanged text skip the LLM stage — saving cost.

### 6. LLM Extraction
- Providers: **Ollama** (local), **OpenAI**, **Fake** (zero-cost integration testing).
- `SafeLLMExtractor` wraps the primary extractor with automatic fallback to Fake on error.
- Ollama health check validates server reachability and model availability at startup.
- Token usage and cost (INR) are tracked per extraction and surfaced in the pipeline summary.

### 7. Bid Classification
- Scores extracted bids against the active company profile's preferred/excluded keywords.
- Results persisted to `bid_classifications` with confidence scores.

---

## LLM Provider Configuration

| Provider | `LLM_PROVIDER` | Requirements |
|----------|----------------|--------------|
| Fake | `fake` | None (zero-cost mock) |
| Ollama | `ollama` | Ollama server running, model pulled |
| OpenAI | `openai` | Valid `LLM_API_KEY` |

Set `LLM_FALLBACK_TO_FAKE_ON_ERROR=true` (default) to auto-fallback to the Fake extractor on LLM errors.

---

## Airflow Orchestration

The Airflow DAG (`airflow/dags/gem_discovery_dag.py`) calls the **single canonical entrypoint** `run_gem_pipeline()` — no duplicate orchestration logic.

```bash
# Initialize Airflow (LocalExecutor, single-node)
bash scripts/init_airflow.sh
```

Schedule: daily at 06:00 UTC.

---

## Project Structure

```
gem_pipeline/
├── airflow/dags/            # Airflow DAG (single entrypoint)
├── app/
│   ├── cli/                 # CLI test scripts
│   ├── config.py            # Pydantic settings (reads .env)
│   ├── db/                  # Models, session, init_db
│   ├── documents/           # PDF extractor, cleaner, hashing
│   ├── filters/             # Keyword prefilter, content hash gate
│   ├── llm/                 # LLM client, schemas, prompts
│   ├── pipelines/           # Stage pipelines + canonical entrypoint
│   ├── repositories/        # SQLAlchemy repository pattern
│   ├── services/            # Business logic (extraction, classification)
│   └── sources/gem/         # GeM scraper, parser, document URLs
├── configs/                 # Keyword lists
├── data/raw/gem/            # Downloaded PDFs
├── tests/                   # Automated pytest suite
├── requirements/            # pip requirements
├── scripts/                 # Setup scripts (Airflow, EC2)
├── .env.example             # Environment template
└── README.md
```

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `bids` | Discovered bid metadata |
| `pipeline_runs` | Pipeline execution tracking |
| `bid_events` | Discovery event log |
| `bid_documents` | Downloaded document metadata + text |
| `bid_extractions` | LLM extraction results + token usage |
| `bid_classifications` | Company-profile scoring |
| `bid_reviews` | Human review workflow (planned) |
| `company_profiles` | Company preferences for classification |

---

## Technology Stack

- **Python 3.11+** — core runtime
- **PostgreSQL** — single persistent store
- **SQLAlchemy 2.x** — ORM and repository pattern
- **pdfplumber** — PDF text extraction
- **LangChain** — LLM provider abstraction (Ollama, OpenAI)
- **Pydantic** — configuration and data validation
- **Apache Airflow** — orchestration (LocalExecutor, single-node)
- **pytest** — automated test suite

---

## Troubleshooting

### Ollama Not Reachable
```
RuntimeError: Ollama server is not running or unreachable at http://localhost:11434
```
**Fix**: Start Ollama (`ollama serve`) and pull the model (`ollama pull qwen3:4b`).

### Model Not Pulled
```
ValueError: Configured Ollama model 'qwen3:4b' is not pulled.
```
**Fix**: `ollama pull qwen3:4b`

### Invalid PDF Errors
The pipeline gracefully marks invalid PDFs as failed without crashing. Check logs for:
- `missing_file` — file not found at expected path
- `empty_file` — zero-byte file downloaded
- `invalid_pdf_signature` — file does not start with `%PDF-`

### Database Connection
Ensure PostgreSQL is running and `.env` credentials match:
```bash
psql -U postgres -d gem_pipeline -c "SELECT 1"
```

### No Active Company Profile
```
ValueError: No active company profile found.
```
**Fix**: Run `python -m app.db.init_db` to seed the default profile.

---

## CLI Scripts

| Command | Description |
|---------|-------------|
| `python -m app.cli.test_gem_pipeline` | Full 7-stage pipeline |
| `python -m app.cli.test_gem_discovery` | Discovery only |
| `python -m app.cli.test_keyword_prefilter` | Keyword filter only |
| `python -m app.cli.test_gem_document_download` | Document download |
| `python -m app.cli.test_gem_document_text_processing` | Text extraction |
| `python -m app.cli.test_content_hash_gate` | Content hash gate |
| `python -m app.cli.test_llm_extraction` | Full pipeline (LLM focused) |
| `python -m app.cli.test_post_classification` | Classification only |

---

## Pipeline Summary Output

Each pipeline run prints a machine-readable summary:

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

## Roadmap

- [x] Stage 1 — Discovery & Persistence
- [x] Stage 2 — Keyword Filtering
- [x] Stage 3 — Document Download & PDF Processing
- [x] Stage 4 — Content Hash Gate
- [x] Stage 5 — LLM Extraction (Ollama, OpenAI, Fake)
- [x] Stage 6 — Bid Classification
- [ ] Stage 7 — Human Review Workflow
- [ ] Retry Policies & Dead-letter Queue
- [ ] Document Versioning
