import boto3
import configparser
from datetime import datetime, timezone

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

REGION = config['aws']['region']
SNS_TOPIC_ARN = config['aws']['sns_topic_arn']

client = boto3.client('sns', region_name=REGION)


def send_alert(result):
    issues_text = '\n'.join(f"  - {issue}" for issue in result['issues'])

    message = (
        f"⚠️ UPTIME ALERT: {result['name']}\n\n"
        f"URL: {result['url']}\n"
        f"Status: {result['status']}\n"
        f"Status Code: {result['status_code']}\n"
        f"Response Time: {result['response_time_ms']}ms\n\n"
        f"Issues Detected:\n{issues_text}\n\n"
        f"Timestamp: {result['timestamp']}"
    )

    try:
        client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Uptime Alert — {result['name']} is {result['status']}",
            Message=message
        )
        print(f"    🚨 Alert sent for {result['name']}")
    except Exception as e:
        print(f"    ❌ Failed to send alert for {result['name']}: {str(e)}")


def process_alerts(validated_results):
    alerts_fired = 0
    for result in validated_results:
        if not result['healthy']:
            send_alert(result)
            alerts_fired += 1
    return alerts_fired