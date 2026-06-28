from __future__ import annotations
from app.pipelines.gem_filter_pipeline import run_keyword_prefilter_pipeline
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.pipelines.gem_discovery_pipeline import run_gem_discovery_pipeline
from app.pipelines.gem_document_pipeline import (
    run_document_download_pipeline,
    run_document_text_extraction_pipeline,
)


def dedup_bids_task() -> None:
    print("Dedup bids task started")
    # TODO: implement dedup orchestration
    print("Dedup bids task completed")


def keyword_prefilter_task() -> None:
    print("Keyword prefilter task started")
    run_keyword_prefilter_pipeline(limit=20)
    print("Keyword prefilter task completed")


def content_hash_gate_task() -> None:
    print("Content hash gate task started")
    # TODO: implement content-hash comparison for processed documents
    print("Content hash gate task completed")


def prepare_llm_candidates_task() -> None:
    print("Prepare LLM candidates task started")
    # TODO: mark/store bids that survive all cheap filters
    print("Prepare LLM candidates task completed")


default_args = {
    "owner": "copilot",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="gem_discovery_pipeline",
    default_args=default_args,
    description="GeM discovery, filtering, document download, and text processing pipeline",
    schedule="0 6 * * *",
    start_date=datetime(2026, 6, 27),
    catchup=False,
    tags=["gem", "discovery", "pipeline"],
) as dag:
    discover_bids = PythonOperator(
        task_id="discover_bids",
        python_callable=run_gem_discovery_pipeline,
    )

    dedup_bids = PythonOperator(
        task_id="dedup_bids",
        python_callable=dedup_bids_task,
    )

    keyword_prefilter = PythonOperator(
        task_id="keyword_prefilter",
        python_callable=keyword_prefilter_task,
    )

    download_documents = PythonOperator(
        task_id="download_documents",
        python_callable=run_document_download_pipeline,
    )

    extract_document_text = PythonOperator(
        task_id="extract_document_text",
        python_callable=run_document_text_extraction_pipeline,
    )

    content_hash_gate = PythonOperator(
        task_id="content_hash_gate",
        python_callable=content_hash_gate_task,
    )

    prepare_llm_candidates = PythonOperator(
        task_id="prepare_llm_candidates",
        python_callable=prepare_llm_candidates_task,
    )

    (
        discover_bids
        >> dedup_bids
        >> keyword_prefilter
        >> download_documents
        >> extract_document_text
        >> content_hash_gate
        >> prepare_llm_candidates
    )