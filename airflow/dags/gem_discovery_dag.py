from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.pipelines.gem_discovery_pipeline import run_gem_pipeline


default_args = {
    "owner": "gem_pipeline",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _run_pipeline(**context) -> None:
    """
    Thin wrapper so Airflow can pass execution context.
    Calls the canonical single entrypoint which runs all 7 stages:
      Discovery → Keyword Filter → Download → Text Extraction →
      Content Hash Gate → LLM Extraction → Bid Classification
    """
    summary = run_gem_pipeline(limit=20)
    # Push the summary dict to XCom for downstream monitoring / alerting
    context["ti"].xcom_push(key="pipeline_summary", value=summary)


with DAG(
    dag_id="gem_discovery_pipeline",
    default_args=default_args,
    description=(
        "GeM Tender Discovery & Extraction Pipeline — "
        "runs all 7 stages via single canonical entrypoint"
    ),
    schedule="0 6 * * *",
    start_date=datetime(2026, 6, 27),
    catchup=False,
    tags=["gem", "discovery", "pipeline"],
) as dag:
    run_pipeline = PythonOperator(
        task_id="run_gem_pipeline",
        python_callable=_run_pipeline,
    )