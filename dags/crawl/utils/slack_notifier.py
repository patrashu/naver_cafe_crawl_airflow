from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

# Slack Webhook Operator를 먼저 정의
# 1. Connection ID
SLACK_DAG_CONN_ID = "naver_cafe_slack_conn"

# 2. Webhook 함수 정의
def send_message(slack_msg):
    return SlackWebhookOperator(
        task_id="slack_webhook",
        slack_webhook_conn_id=SLACK_DAG_CONN_ID,
        message=slack_msg,
        username="Airflow-alert",
    )

# 3. slack alert 함수 정의
# 메세지에 slack id 추가해서 tag 가능
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
    alert = send_message(slack_msg)
    
    return alert.execute(context=context)


def task_succ_slack_alert(context):
    slack_msg = f"""
        :large_green_circle: Task SUCC.
        *Task*: {context.get("task_instance").task_id}  
        *Dag*: {context.get("task_instance").dag_id} 
        *Execution Time*: {context.get("execution_date")}
    """
    alert = send_message(slack_msg)

    return alert.execute(context=context)