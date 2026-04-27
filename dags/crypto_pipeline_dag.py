from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'proud',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='crypto_analytics_pipeline',
    default_args=default_args,
    description='Ingest crypto data and run dbt transformations',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 4, 25),
    catchup=False,
    tags=['crypto', 'snowflake', 'dbt'],
) as dag:

    ingest = DockerOperator(
        task_id='ingest_crypto_data',
        image='crypto-ingest:latest',
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
        env_file='/opt/airflow/.env',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='echo "dbt run triggered — connect dbt Cloud API or dbt Core here"',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='echo "dbt test triggered"',
    )

    ingest >> dbt_run >> dbt_test