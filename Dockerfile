FROM apache/airflow:2.9.3

COPY requirements.txt .
COPY config/* /opt/airflow/config/
COPY data/* /opt/airflow/data/
RUN pip install --no-cache-dir -r requirements.txt