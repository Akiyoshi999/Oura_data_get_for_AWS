import json
import requests
import boto3
import botocore


def handle_message(url, message, token):
    try:
        data = {'message': f'{message}'}
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url, headers=headers, data=data)
    except Exception as e:
        print(e)
        raise e
    return response


def line_notice_handler(event, context):
    try:
        ssm = boto3.client('ssm')
        line_notify_token = ssm.get_parameter(
            Name='OURA_NOTIFY_TOKEN',
            WithDecryption=True
        )['Parameter']['Value']
        line_notify_url = ssm.get_parameter(
            Name='LineNotice-WebhookURL',
            WithDecryption=True
        )['Parameter']['Value']

        message = event['Records'][0]['Sns']['Message']

        # Line Notifyを使った、送信部分
        response = handle_message(
            url=line_notify_url, token=line_notify_token, message=message)

        if response.status_code == requests.codes.ok:
            res_text = json.loads(response.text)
            return {
                'statusCode': res_text['status'],
                'body': json.dumps({'message': res_text['message']})
            }
        else:
            raise requests.exceptions.HTTPError(response.raise_for_status)

    except botocore.exceptions.ClientError as error:
        print(error)
        raise error
    except Exception as error:
        print(error)
        raise error
