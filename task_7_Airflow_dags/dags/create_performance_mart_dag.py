from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from build_performance_mart import create_performance_mart


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
    "create_analytics_student_performance",
    default_args=default_args,
    description="Создание и обновление витрины dmr.analytics_student_performance",
    schedule_interval="0 2 * * *",
    catchup=False,
    tags=["mart", "student_performance"],
) as dag:
    create_performance_mart_task = PythonOperator(
        task_id="create_student_performance_mart",
        python_callable=create_performance_mart,
    )

    create_performance_mart_task
