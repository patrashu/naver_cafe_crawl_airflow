import sys
sys.path.append('/opt/airflow/dags/crawl')
import yaml
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from utils.utils import (
    get_chrome_driver_options, naver_login, search_keyword,
    extract, transform, load, table_check_sql
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
    
    table_check_sql(_config[car_name]['table_name'])
    load(transformed_data, _config[car_name]['table_name'], _config[car_name]['save_sql'])
    print(extract_data)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False, # whether or not to run the task if the previous task failed
    'start_date': datetime(2024, 6, 4), # start date
    'end_date': datetime(2024, 6, 5), # end date
    'email_on_failure': False, # email notification
    'email_on_retry': False, # email notification
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
    template_searchpath=['/opt/airflow/data'],  # 템플릿 파일을 검색할 경로 설정
)

ioniq_operator = PythonOperator(
    task_id='ioniq_operator',
    python_callable=naver_cafe_crawl,
    op_kwargs={
        "car_name": "ioniq"
    },
    dag=dag,
)

ioniq_table_check_operator = PostgresOperator(
    task_id='ioniq_table_check_operator',
    postgres_conn_id='test_postgres',
    sql='/opt/airflow/data/create_ioniq.sql',
    dag=dag
)

ioniq_save_operator = PostgresOperator(
    task_id='ioniq_save_operator',
    postgres_conn_id='test_postgres',
    sql='/opt/airflow/data/ioniq.sql',
    dag=dag
)

ioniq_operator >> ioniq_table_check_operator >> ioniq_save_operator