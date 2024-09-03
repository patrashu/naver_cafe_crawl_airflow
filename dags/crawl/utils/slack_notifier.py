from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

# 1. Connection ID
SLACK_DAG_CONN_ID = "naver_cafe_slack_conn"

# 2. Webhook 함수 정의
def send_message(task_id, slack_msg):
    return SlackWebhookOperator(
        task_id=task_id,
        slack_webhook_conn_id=SLACK_DAG_CONN_ID,
        message=slack_msg,
        username="Airflow-alert",
    )

def task_fail_slack_alert(context):
    slack_msg = """
        :red_circle: Task Failed.
        *Task*: {task}
        *Dag*: {dag}
        *Execution Time*: {exec_date}
    """.format(
        task=context.get("task_instance").task_id,
        dag=context.get("task_instance").dag_id,
        exec_date=context.get("execution_date"),
    )
    alert = send_message("slack_fail_alert", slack_msg)
    return alert.execute(context=context)

# 성공 시 알림 함수
def task_succ_slack_alert(context):
    slack_msg = f"""
        :large_green_circle: Task Succeeded.
        *Task*: {context.get("task_instance").task_id}
        *Dag*: {context.get("task_instance").dag_id}
        *Execution Time*: {context.get("execution_date")}
    """
    alert = send_message("slack_success_alert", slack_msg)
    return alert.execute(context=context)