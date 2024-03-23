import json
import os
import datetime
import calendar
import boto3
import botocore

from src.ScheduledFunction import app
from moto import mock_aws
from tests.unit.variables import DAILY_NO_SCORE, DAILY_SCORE_ONEDAY_HEALTY, DAILY_SCORE_ONEDAY_UNHEALTY, WEEKLY_SCORE
import pytest
import requests_mock
import re

today = datetime.date.today()


@pytest.fixture(scope='function')
def os_env_setup():
    os.environ['SLEEP_API_URL'] = 'https://api.ouraring.com/v2/usercollection/daily_sleep'
    os.environ['ACTIVE_API_URL'] = 'https://api.ouraring.com/v2/usercollection/daily_activity'
    os.environ['READINESS_API_URL'] = 'https://api.ouraring.com/v2/usercollection/daily_readiness'
    os.environ['SUBJECT'] = "Ouraスコアレポート"
    os.environ['HEALTH_BORDER'] = '69'
    os.environ['ACTIVE_HEALTH_BORDER'] = '49'
    os.environ['TOPIC_ARN'] = 'dummy'


@pytest.fixture(scope='function')
def request_mock_daily_score(today_url):
    with requests_mock.Mocker() as m:
        m.get(today_url['SLEEP_API_URL'],
              text=DAILY_SCORE_ONEDAY_HEALTY['SLEEP'], status_code=200)
        m.get(today_url['ACTIVE_API_URL'],
              text=DAILY_SCORE_ONEDAY_HEALTY['ACTIVE'], status_code=200)
        m.get(today_url['READINESS_API_URL'],
              text=DAILY_SCORE_ONEDAY_HEALTY['READINESS'], status_code=200)
        yield


@pytest.fixture(scope='function')
def request_mock_daily_score_unhealty(today_url):
    with requests_mock.Mocker() as m:
        m.get(today_url['SLEEP_API_URL'],
              text=DAILY_SCORE_ONEDAY_UNHEALTY['SLEEP'], status_code=200)
        m.get(today_url['ACTIVE_API_URL'],
              text=DAILY_SCORE_ONEDAY_UNHEALTY['ACTIVE'], status_code=200)
        m.get(today_url['READINESS_API_URL'],
              text=DAILY_SCORE_ONEDAY_UNHEALTY['READINESS'], status_code=200)
        yield


@pytest.fixture(scope='function')
def request_mock_weekly_score(weekly_url):
    with requests_mock.Mocker() as m:
        m.get(weekly_url['SLEEP_API_URL'],
              text=WEEKLY_SCORE['SLEEP'], status_code=200)
        m.get(weekly_url['ACTIVE_API_URL'],
              text=WEEKLY_SCORE['ACTIVE'], status_code=200)
        m.get(weekly_url['READINESS_API_URL'],
              text=WEEKLY_SCORE['READINESS'], status_code=200)
        yield


@pytest.fixture(scope='function')
def request_mock_daily_no_score(today_url):
    with requests_mock.Mocker() as m:
        m.get(today_url['SLEEP_API_URL'],
              text=DAILY_NO_SCORE['SLEEP'], status_code=200)
        m.get(today_url['ACTIVE_API_URL'],
              text=DAILY_NO_SCORE['ACTIVE'], status_code=200)
        m.get(today_url['READINESS_API_URL'],
              text=DAILY_NO_SCORE['READINESS'], status_code=200)
        yield


@pytest.fixture(scope='function')
def request_mock_daily_no_score_sleep(today_url):
    with requests_mock.Mocker() as m:
        m.get(today_url['SLEEP_API_URL'],
              text=DAILY_NO_SCORE['SLEEP'], status_code=200)
        m.get(today_url['ACTIVE_API_URL'],
              text=DAILY_SCORE_ONEDAY_HEALTY['ACTIVE'], status_code=200)
        m.get(today_url['READINESS_API_URL'],
              text=DAILY_SCORE_ONEDAY_HEALTY['READINESS'], status_code=200)
        yield


@mock_aws
def test_schedule_success_1(request_mock_daily_score, os_env_setup):
    """正常系のテスト
    当日のスコア取得テスト
    """
    os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                     datetime.timedelta(days=1)).weekday()]

    client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
    client_ssm.put_parameter(
        Name='OURA_TOKEN',
        Value='dummy',
        Type='SecureString',
    )
    client_sns = boto3.client('sns', region_name='ap-northeast-1')
    res = client_sns.create_topic(Name='test-oura-score-get-app')
    os.environ['TOPIC_ARN'] = res["TopicArn"]

    ret = app.lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "MessageId" in ret["body"]
    assert type(data["MessageId"]) == str
    assert "SendMessage" in ret["body"]
    assert type(data["SendMessage"]) == str
    assert len(re.findall(
        r'(^(sleep).*70)|(^(active).*50)|(^(readiness).*70)|(本日の体調は良好です)', data['SendMessage'], re.MULTILINE)) == 4


@mock_aws
def test_schedule_success_2(request_mock_daily_score_unhealty, os_env_setup):
    """正常系のテスト
    当日のスコア取得テスト(体調が悪い時のテスト)
    """
    os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                     datetime.timedelta(days=1)).weekday()]
    client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
    client_ssm.put_parameter(
        Name='OURA_TOKEN',
        Value='dummy',
        Type='SecureString',
    )
    client_sns = boto3.client('sns', region_name='ap-northeast-1')
    res = client_sns.create_topic(Name='test-oura-score-get-app')
    os.environ['TOPIC_ARN'] = res["TopicArn"]

    ret = app.lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "MessageId" in ret["body"]
    assert type(data["MessageId"]) == str
    assert "SendMessage" in ret["body"]
    assert type(data["SendMessage"]) == str
    assert len(re.findall(
        r'(^(sleep).*69)|(^(active).*49)|(^(readiness).*69)|(今日はsleep, active, readinessが不調みたい。)', data['SendMessage'], re.MULTILINE)) == 4


@mock_aws
def test_schedule_success_3(request_mock_weekly_score, os_env_setup):
    """正常系のテスト
    当日のスコア取得テスト(1週間)
    """
    os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                     datetime.timedelta()).weekday()]
    client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
    client_ssm.put_parameter(
        Name='OURA_TOKEN',
        Value='dummy',
        Type='SecureString',
    )
    client_sns = boto3.client('sns', region_name='ap-northeast-1')
    res = client_sns.create_topic(Name='test-oura-score-get-app')
    os.environ['TOPIC_ARN'] = res["TopicArn"]

    ret = app.lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "MessageId" in ret["body"]
    assert type(data["MessageId"]) == str
    assert "SendMessage" in ret["body"]
    assert type(data["SendMessage"]) == str
    assert len(re.findall(
        r'(^(sleep).*([0-9]{2})$)|(^(active).*([0-9]{2})$)|(^(readiness).*([0-9]{2})$)', data['SendMessage'], re.MULTILINE)) == 3
    assert len(re.findall(
        r'(^(sleep).*([0-9]{2}\.[0-9])$)|(^(active).*([0-9]{2}\.[0-9])$)|(^(readiness).*([0-9]{2}\.[0-9])$)|(1週間の平均スコア)', data['SendMessage'], re.MULTILINE)) == 4


@mock_aws
def test_schedule_success_4(request_mock_daily_no_score, os_env_setup):
    """正常系のテスト
    当日のスコアが全部取得できない
    """
    os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                     datetime.timedelta(days=1)).weekday()]
    client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
    client_ssm.put_parameter(
        Name='OURA_TOKEN',
        Value='dummy',
        Type='SecureString',
    )
    client_sns = boto3.client('sns', region_name='ap-northeast-1')
    res = client_sns.create_topic(Name='test-oura-score-get-app')
    os.environ['TOPIC_ARN'] = res["TopicArn"]

    ret = app.lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert len(re.findall(
        r'今日はsleep, active, readinessのスコアがないみたい。', data['SendMessage'], re.MULTILINE)) == 1
    assert len(re.findall(
        r'[0-9]', data['SendMessage'], re.MULTILINE)) == 0


@mock_aws
def test_schedule_success_5(request_mock_daily_no_score_sleep, os_env_setup):
    """正常系のテスト
    当日のスコアがsleepのみ取得できない
    """
    os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                     datetime.timedelta(days=1)).weekday()]
    client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
    client_ssm.put_parameter(
        Name='OURA_TOKEN',
        Value='dummy',
        Type='SecureString',
    )
    client_sns = boto3.client('sns', region_name='ap-northeast-1')
    res = client_sns.create_topic(Name='test-oura-score-get-app')
    os.environ['TOPIC_ARN'] = res["TopicArn"]

    ret = app.lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert len(re.findall(
        r'^(今日はsleepのスコアがないみたい。)$', data['SendMessage'], re.MULTILINE)) == 1
    assert len(re.findall(
        r'(^(active).*([0-9]{2})$)|(^(readiness).*([0-9]{2})$)', data['SendMessage'], re.MULTILINE)) == 2


@mock_aws
def test_schedule_fail_1(request_mock_daily_score_unhealty, os_env_setup):
    """異常系のテスト
    SNSのエンドポイントがない場合
    """
    with pytest.raises(botocore.exceptions.ClientError):
        os.environ['WEEK_SCORE_DAY'] = calendar.day_name[(today -
                                                          datetime.timedelta(days=1)).weekday()]
        client_ssm = boto3.client('ssm', region_name='ap-northeast-1')
        client_ssm.put_parameter(
            Name='OURA_TOKEN',
            Value='dummy',
            Type='SecureString',
        )
        app.lambda_handler("", "")
