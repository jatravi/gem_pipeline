# GeM Tender Discovery Pipeline

An end-to-end pipeline for discovering public tenders from the Government e-Marketplace (GeM), persisting bid metadata, downloading bid documents, extracting PDF text, and preparing structured data for downstream qualification and decision workflows.

## Overview

This project is being built as a staged pipeline:

1. **Discover tenders** from GeM
2. **Persist bid metadata** into PostgreSQL
3. **Download bid documents** using GeM source identifiers
4. **Extract and normalize document text**
5. **Generate structured bid extractions**
6. **Classify relevance and eligibility**
7. **Support review and decision workflows**

At the current stage, the repository includes a completed **Week 2 MVP**, covering:

- GeM bid discovery
- bid persistence
- source ID persistence
- direct PDF document download
- document persistence
- PDF text extraction
- cleaned text + hash persistence

---

## What problem this solves

Tender evaluation is usually fragmented across:
- listing portals
- downloaded PDFs
- manual reading
- eligibility interpretation
- internal review notes

This pipeline is intended to turn that into a structured workflow by:
- capturing tender metadata at discovery time
- tying documents back to stable source identifiers
- processing PDF text into a machine-readable form
- building toward automated extraction and classification

---

## Current capabilities

### Discovery
- fetches tender listing data from GeM
- parses core bid metadata
- stores bids in PostgreSQL
- logs discovery runs and bid events

### Persistence
- stores bids in the `bids` table
- stores pipeline execution metadata in `pipeline_runs`
- stores bid lifecycle events in `bid_events`

### Source tracking
- persists:
  - `source_bid_id`
  - `parent_source_bid_id`

These fields enable direct lookup of source-linked bid artifacts.

### Document processing
- constructs GeM document URLs from `source_bid_id`
- downloads bid PDFs directly from GeM
- stores document metadata in `bid_documents`
- extracts text from PDFs using `pdfplumber`
- stores:
  - raw extracted text
  - cleaned text
  - text hash
  - page count
  - extraction method
  - processing status

---

## Project status

### Completed
- Week 1 MVP: discovery + persistence
- Week 2 MVP: document download + document text processing

### In progress / planned
- structured extraction into `bid_extractions`
- bid relevance and eligibility classification into `bid_classifications`
- review workflow support via `bid_reviews`

---

## Architecture

### High-level flow

```text
GeM listing source
    ↓
Discovery parser
    ↓
bids
    ↓
source_bid_id
    ↓
GeM document URL
    ↓
PDF download
    ↓
bid_documents
    ↓
PDF text extraction
    ↓
cleaned_text + text_hash
    ↓
future: bid_extractions / bid_classifications / bid_reviews
```

---

## Repository structure

```text
app/
  cli/                  # CLI entrypoints and test runners
  db/                   # database base, session, models
  documents/            # download, extraction, cleaning, hashing
  repositories/         # persistence layer
  services/             # orchestration logic
  sources/
    gem/                # GeM-specific discovery and document logic

data/
  raw/                  # downloaded source files
```

---

## Database model

Core tables used in the current implementation:

- `bids`
- `pipeline_runs`
- `bid_events`
- `bid_documents`
- `bid_extractions`
- `bid_classifications`
- `bid_reviews`

### Key tables

#### `bids`
Stores discovered tender metadata, including:
- `bid_number`
- `ra_number`
- `title`
- `ministry`
- `department`
- `organisation`
- `office`
- `start_date`
- `closing_date`
- `estimated_value`
- `emd_amount`
- `status`
- `source_url`
- `source_bid_id`
- `parent_source_bid_id`

#### `bid_documents`
Stores downloaded and processed document data, including:
- `document_url`
- `local_path`
- `file_size`
- `content_hash`
- `mime_type`
- `raw_text`
- `cleaned_text`
- `text_hash`
- `text_extracted_at`
- `text_extraction_method`
- `page_count`
- `processing_status`
- `processing_error`

---

## Technology stack

- **Python**
- **PostgreSQL**
- **SQLAlchemy**
- **Requests**
- **pdfplumber**

Planned later:
- LLM-based extraction/classification
- orchestration hardening
- retry/failure policies
- better dedup/upsert behavior

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/jatravi/gem_pipeline
cd gem_pipeline
```

### 2. Create a virtual environment

#### PowerShell
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

#### Bash
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If your `requirements.txt` is still being finalized, make sure these are installed:

- `sqlalchemy`
- `psycopg2-binary`
- `requests`
- `pdfplumber`

### 4. Set up PostgreSQL

Create a database:

```sql
CREATE DATABASE gem_pipeline;
```

Configure your local database settings according to the project’s session/config setup.

---

## Running the pipeline

### 1. Run discovery test

```bash
python -m app.cli.test_gem_discovery
```

This should:
- create a `pipeline_runs` row
- discover and persist bids
- populate `source_bid_id` for newly discovered bids
- create `bid_events`

---

### 2. Test direct GeM document download

```bash
python -m app.cli.test_gem_document_download
```

This validates direct PDF retrieval from:

```text
https://bidplus.gem.gov.in/showbidDocument/{source_bid_id}
```

---

### 3. Test document persistence

```bash
python -m app.cli.test_gem_document_persist
```

This should:
- download a bid PDF
- create a `bid_documents` row
- persist document metadata

---

### 4. Test PDF text extraction and persistence

```bash
python -m app.cli.test_gem_document_text_processing
```

This should:
- load a downloaded PDF
- extract text using `pdfplumber`
- clean the extracted text
- compute a SHA-256 text hash
- update `bid_documents` with processed text metadata

---

## Example validated output

A successful document processing flow has produced:

- `mime_type = application/pdf`
- `page_count = 8`
- `raw_text_length = 26534`
- `cleaned_text_length = 26534`
- populated `text_hash`
- `text_extraction_method = pdfplumber`
- `processing_status = processed`

---

## Useful SQL checks

### Recently discovered bids
```sql
select id, bid_number, source_bid_id, parent_source_bid_id
from bids
order by id desc
limit 20;
```

### Latest persisted documents
```sql
select
    id,
    bid_id,
    document_type,
    file_name,
    document_url,
    local_path,
    file_size,
    content_hash,
    mime_type,
    sequence_no,
    processing_status,
    downloaded_at
from bid_documents
order by id desc
limit 10;
```

### Latest text processing results
```sql
select
    id,
    page_count,
    length(raw_text) as raw_len,
    length(cleaned_text) as cleaned_len,
    text_hash,
    text_extraction_method,
    processing_status,
    processing_error
from bid_documents
order by id desc
limit 10;
```

---

## Current implementation notes

- direct GeM document retrieval currently uses `source_bid_id`
- repeated manual test runs may create multiple `bid_documents` rows for the same logical document
- text cleaning is intentionally minimal in the current MVP
- extraction persistence is working, but structured semantic extraction is the next stage

---

## Roadmap

### Next milestone
- add structured extraction into `bid_extractions`

### After that
- classify bid relevance and eligibility into `bid_classifications`
- support review decisions in `bid_reviews`
- improve rerun idempotency for documents
- harden retry/error handling
- add production-grade pipeline orchestration

---

## Development philosophy

This project is being built incrementally:
- validate one pipeline stage at a time
- persist intermediate artifacts
- keep source traceability intact
- prefer observable, testable progress over premature abstraction

---

## License

Add your project license here.
