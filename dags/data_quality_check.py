"""
Data Quality Check DAG
Monitors and validates data quality across tables
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'alitaha',
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}


def check_row_count(**context):
    """Check if table has minimum expected rows"""
    expected_min_rows = 1000
    actual_rows = 1500  # Simulate query result

    logger.info(f"Row count check: {actual_rows} rows (expected min: {expected_min_rows})")

    if actual_rows >= expected_min_rows:
        logger.info("Row count check PASSED")
        return True
    else:
        logger.error("Row count check FAILED")
        return False


def check_null_values(**context):
    """Check for unexpected null values"""
    null_count = 5  # Simulate query result
    threshold = 10

    logger.info(f"Null value check: {null_count} nulls (threshold: {threshold})")

    if null_count <= threshold:
        logger.info("Null value check PASSED")
        return True
    else:
        logger.error("Null value check FAILED")
        return False


def check_data_freshness(**context):
    """Check if data is fresh (updated recently)"""
    hours_since_update = 2  # Simulate
    max_hours = 24

    logger.info(f"Freshness check: {hours_since_update} hours since last update")

    if hours_since_update <= max_hours:
        logger.info("Freshness check PASSED")
        return True
    else:
        logger.error("Freshness check FAILED - Data is stale")
        return False


def decide_action(**context):
    """Decide whether to proceed or alert based on checks"""
    ti = context['ti']

    # Pull results from previous tasks
    checks = {
        'row_count': ti.xcom_pull(task_ids='check_row_count'),
        'nulls': ti.xcom_pull(task_ids='check_null_values'),
        'freshness': ti.xcom_pull(task_ids='check_data_freshness'),
    }

    all_passed = all(checks.values())

    if all_passed:
        logger.info("All quality checks passed")
        return 'quality_passed'
    else:
        logger.warning("Some quality checks failed")
        return 'send_alert'


with DAG(
    dag_id='data_quality_check',
    default_args=default_args,
    description='Monitor data quality metrics',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['quality', 'monitoring'],
) as dag:

    check_rows = PythonOperator(
        task_id='check_row_count',
        python_callable=check_row_count,
    )

    check_nulls = PythonOperator(
        task_id='check_null_values',
        python_callable=check_null_values,
    )

    check_fresh = PythonOperator(
        task_id='check_data_freshness',
        python_callable=check_data_freshness,
    )

    decide = BranchPythonOperator(
        task_id='decide_action',
        python_callable=decide_action,
    )

    passed = BashOperator(
        task_id='quality_passed',
        bash_command='echo "All quality checks passed!"',
    )

    alert = BashOperator(
        task_id='send_alert',
        bash_command='echo "ALERT: Data quality issues detected!"',
    )

    # Dependencies
    [check_rows, check_nulls, check_fresh] >> decide >> [passed, alert]
