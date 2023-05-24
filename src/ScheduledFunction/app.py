import json
import requests
import datetime
import calendar
import os
import boto3
import botocore


split_line = '\n=====================\n'


def lambda_handler(event, context):
    try:
        sns = boto3.client('sns')
        ssm = boto3.client('ssm')
        OURA_TOKEN = ssm.get_parameter(
            Name='OURA_TOKEN',
            WithDecryption=True
        )['Parameter']['Value']
        urls = {
            'sleep': os.environ['SLEEP_API_URL'],
            'active': os.environ['ACTIVE_API_URL'],
            'readiness': os.environ['READINESS_API_URL']
        }

        trigger_week_day = os.environ['WEEK_SCORE_DAY']
        today = datetime.date.today()
        today_week = calendar.day_name[today.weekday()]
        week_flg = today_week == trigger_week_day

        time_range = start_and_end_day(today=today, weeklyFlg=week_flg)
        headers = {'Authorization': f'Bearer {OURA_TOKEN}'}

        sleep_score = api_get_request(urls['sleep'], time_range, headers)
        active_score = api_get_request(urls['active'], time_range, headers)
        readiness_score = api_get_request(
            urls['readiness'], time_range, headers)
        print(sleep_score.json())

        sleep_score_result = score_total(sleep_score.json()['data'])
        active_score_result = score_total(active_score.json()['data'])
        readiness_score_result = score_total(readiness_score.json()['data'])

        today_scores = {
            'sleep': sleep_score_result['today_score'],
            'active': active_score_result['today_score'],
            'readiness': readiness_score_result['today_score'],
        }
        week_scores = {
            'sleep': sleep_score_result['score_avg'],
            'active': active_score_result['score_avg'],
            'readiness': readiness_score_result['score_avg'],
        } if week_flg else {}

        message = score_create(today_scores, week_scores)
        message += blurred_create(today_scores)

        response = sns.publish(
            TopicArn=os.environ['TOPIC_ARN'],
            Message=message,
            Subject=os.environ['SUBJECT'],
        )
    except botocore.exceptions.ClientError as error:
        print(error)
        raise error
    except Exception as error:
        print(error)
        raise error

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps({'MessageId': response['MessageId'],
                            'SendMessage': message})
    }


def start_and_end_day(today, weeklyFlg=False):
    end_date = today
    start_day = end_date - datetime.timedelta(days=(7 if weeklyFlg else 1))
    return {
        'start_date': start_day.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }


def score_total(score_array: list, target_key: str = 'score') -> dict:
    """スコアの合計

    Args:
        score_array (list): データ値をリストで受け取る
        target_key (str, optional):score_arrayの中から取得したいKeyを指定する。デフォルトは'score'

    Returns:
        dict: 複数のスコア、当日のスコア、スコアの平均値を返す。
              当日のスコアがない場合は空の配列を返す。
    """
    scores = []
    for tar in score_array:
        scores.append(tar[target_key])
    score_avg = round(sum(scores) / len(scores), 1) if len(scores) > 1 else 0
    return {
        'score': scores,
        'today_score': scores[-1] if scores else [],
        'score_avg': score_avg
    }


def api_get_request(url: str, params: dict, headers: str) -> requests.models.Response:
    try:
        res = requests.get(url, params=params, headers=headers)
        return res
    except requests.exceptions.RequestException as e:
        print(e)
        raise e


def score_create(today_scores: dict, week_scores: dict):
    """
    スコアをメッセージにするモジュール
    """
    today_score = '本日のスコア'
    week_score = None
    for k, v in today_scores.items():
        if v:
            today_score += '\n{:12} = {:5}'.format(k, v)
    if week_scores:
        week_score = ('1週間の平均スコア\n' + '\n'.join
                      (['{:12} = {:5}'.format(k, v) for k, v in week_scores.items()]))
        message = split_line + today_score + split_line + week_score + split_line
    else:
        message = split_line + today_score + split_line
    return message


def blurred_create(today_score: int) -> str:
    """
    ぼやきメッセージを作成する
    スコアが悪ければ、その悪いスコアを教えるメッセージを作成する
    """
    bad_item = []
    no_score_item = []
    blurred_message = ''

    for key, value in today_score.items():
        if not value:
            no_score_item.append(key)
            continue
        elif key == 'active' and value <= int(os.environ['ACTIVE_HEALTH_BORDER']):
            bad_item.append(key)
        elif key != 'active' and value <= int(os.environ['HEALTH_BORDER']):
            bad_item.append(key)
    if bad_item == [] and not no_score_item:
        blurred_message = ('本日の体調は良好です')
    elif no_score_item:
        blurred_message += '今日は' + ', '.join(no_score_item) + 'のスコアがないみたい。'
    else:
        blurred_message += ('今日は' + ', '.join(bad_item) + 'が不調みたい。')
    return blurred_message


if __name__ == '__main__':
    lambda_handler('', '')
