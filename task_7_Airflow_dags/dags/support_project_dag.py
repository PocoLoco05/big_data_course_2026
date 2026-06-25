from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project/task_10_ProjectTask"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="support_project_pipeline",
    default_args=default_args,
    description="Generate support data, build marts and visualizations",
    schedule_interval=None,
    catchup=False,
    tags=["support", "project", "mart"],
) as dag:
    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_DIR} && python -m src.generate_data",
    )

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command="echo 'CSV files are prepared in data/raw. Use SQL COPY scripts for DB loading.'",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=f"cd {PROJECT_DIR} && python -m src.create_marts transform",
    )

    create_mart = BashOperator(
        task_id="create_mart",
        bash_command=f"cd {PROJECT_DIR} && python -m src.create_marts marts",
    )

    visualize = BashOperator(
        task_id="visualize",
        bash_command=f"cd {PROJECT_DIR} && python -m src.visualize",
    )

    generate_data >> load_raw >> transform >> create_mart >> visualize
