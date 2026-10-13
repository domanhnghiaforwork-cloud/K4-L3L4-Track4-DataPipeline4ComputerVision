#!/bin/bash
# one container = scheduler + webserver (LocalExecutor) to keep RAM low
export AIRFLOW__WEBSERVER__WEB_SERVER_MASTER_TIMEOUT=600
airflow db migrate
airflow users create --username admin --password admin --firstname Lab --lastname User --role Admin --email lab@example.com || true
airflow scheduler &
exec airflow webserver
