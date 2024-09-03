import sys
sys.path.append('/opt/airflow/dags/crawl')
import yaml
import pandas as pd
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.postgres_operator import PostgresOperator
from utils.utils import (
    get_chrome_driver_options, naver_login, search_keyword, extract, transform, load,
)
from utils.slack_notifier import (
    task_fail_slack_alert, task_succ_slack_alert
)


def naver_cafe_crawl(**kwargs):
    car_name = kwargs["car_name"]
    with open("config/naver_cafe_info.yaml", "r") as f:
        _config = yaml.safe_load(f)
    
    # convert start_time to Seoul
    start_date = kwargs['ds']
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    start_date_str = datetime.strftime(start_date, "%Y-%m-%d")

    command_executor = RemoteConnection("remote_chromedriver:4444/wd/hub")
    command_executor.set_timeout(300)
    
    driver = webdriver.Remote(
        command_executor=command_executor,
        options=get_chrome_driver_options()
    )

    naver_login(driver, _config[car_name]["login_info"])

    # 검색 키워드 입력
    keyword_dict = {
        "cafe_url": _config[car_name]['cafe_url'],
        "start_date": start_date_str,
        "end_date": start_date_str,
        "keyword": _config[car_name]['keyword'],
        "search_type":_config[car_name]['search_type'],
        "select_all": _config[car_name]['select_all'],
        "exclude_word": _config[car_name]['exclude_word'],
        "select_any": _config[car_name]['select_any'],
        "correct_word": _config[car_name]['correct_word'],
    }
    search_keyword(driver, keyword_dict)
    extract_data = extract(driver, _config[car_name]['max_page_num'])
    transformed_data = transform(extract_data, _config[car_name]['keyword'])
    load(transformed_data, _config[car_name]['save_csv'])


def load_data_and_save_to_postgres(**kwargs):
    car_name = kwargs["car_name"]
    with open("config/naver_cafe_info.yaml", "r") as f:
        _config = yaml.safe_load(f)
        
    df = pd.read_csv(_config[car_name]['save_csv'])
    data = []
    for _, row in df.iterrows():
        data.append(tuple(row))
        
    postgres_hook = PostgresHook(postgres_conn_id='airflow')
    for record in data:
        postgres_hook.run("""
            INSERT INTO ioniq (upload_date, upload_time, title, num_view, num_like, body, comments, car_name, community, comm_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, parameters=record)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False, # whether or not to run the task if the previous task failed
    'start_date': datetime(2024, 9, 3), # start date
    'end_date': datetime(2024, 9, 4), # end date
    'retries': 2, # retry the task
    'retry_delay': timedelta(minutes=1) # retry delay
}

dag = DAG(
    dag_id='naver_cafe_crawl', # dag_id
    default_args=default_args, # default_args
    description='naver_cafe_crawling every day', # description
    tags=['crawling'], # tags
    schedule_interval='0 0 * * *',  # every day at 00:00
    max_active_runs=1, # max_active_runs on parallel
    template_searchpath=['/opt/airflow/data'],
    on_failure_callback=task_fail_slack_alert,
    on_success_callback=task_succ_slack_alert,
)

# crawling operator
ioniq_operator = PythonOperator(
    task_id='ioniq_operator',
    python_callable=naver_cafe_crawl,
    op_kwargs={
        "car_name": "ioniq"
    },
    dag=dag,
)

# check table operator
ioniq_table_check_operator = PostgresOperator(
    task_id='ioniq_table_check_operator',
    postgres_conn_id='airflow',
    sql='create_ioniq.sql',
    dag=dag
)

# load and save operator
load_and_save_operator = PythonOperator(
    task_id='load_operator',
    python_callable=load_data_and_save_to_postgres,
    op_kwargs={
        "car_name": "ioniq"
    },
    dag=dag,
)

# schedule
ioniq_operator >> ioniq_table_check_operator >> load_and_save_operator