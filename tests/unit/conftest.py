import pytest
import datetime
import calendar


@pytest.fixture()
def sns_event_success():
    return {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:ap-northeast-1:705427061380:oura-score-get-notice:ec0cac32-709e-4d65-9ae2-c36d03a0b72a",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "1968c4f8-b167-52cf-a9f7-98293740cd9c",
                    "TopicArn": "arn:aws:sns:ap-northeast-1:705427061380:oura-score-get-notice",
                    "Subject": "Ouraスコアレポート",
                    "Message": "\n===============\n本日のスコア\nsleep        =    49\nactive       =    64\nreadiness    =    72\n===============\n今日はsleep, activeが不調みたい。",
                    "Timestamp": "2023-05-07T10:56:39.623Z",
                    "SignatureVersion": "1",
                    "Signature": "LKz/XtiqX0BZOswMGOYwRl6FEq1SA9x1fFH5pn1E5+q62RgZxa1cPQI9AkVOns/fJujcmsqD66+xB/sk1wHzWBvgOnlRj+VhEqg24VF34J8DbU9ef51j2uSO4/QRCfpxgTdyQNZa2D8MPcdYWAfCF+TL1HfwfEQ0VawTSiVSuiO6UFm0ptSk/+aA/kzMjDYiOJDriBVFTKm7skR5DEcnJklE2I0XttdgszU2t7oaTneN92wOkrr/K3xt4zl9gTOBQ2Y9RkQ9U1OuFYEXi9Ys4BySAV96QEdEGjAZx7LnZWXlK4mk3tbAFXTCJmvNpqxNr0Yu7eJv/urhBayVr6ZTPA==",
                    "SigningCertUrl": "https://sns.ap-northeast-1.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",
                    "UnsubscribeUrl": "https://sns.ap-northeast-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:ap-northeast-1:705427061380:oura-score-get-notice:ec0cac32-709e-4d65-9ae2-c36d03a0b72a",
                    "MessageAttributes": {

                    }
                }
            }
        ]
    }


@pytest.fixture()
def today_url():
    time_range = start_and_end_day()

    SLEEP_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_sleep", time_range)
    ACTIVE_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_activity", time_range)
    READINESS_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_readiness", time_range)

    return {
        "SLEEP_API_URL": SLEEP_API_URL,
        "ACTIVE_API_URL": ACTIVE_API_URL,
        "READINESS_API_URL": READINESS_API_URL
    }


@pytest.fixture()
def weekly_url():
    time_range = start_and_end_day(weeklyFlg=True)
    SLEEP_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_sleep", time_range)
    ACTIVE_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_activity", time_range)
    READINESS_API_URL = request_mock_url(
        "https://api.ouraring.com/v2/usercollection/daily_readiness", time_range)

    return {
        "SLEEP_API_URL": SLEEP_API_URL,
        "ACTIVE_API_URL": ACTIVE_API_URL,
        "READINESS_API_URL": READINESS_API_URL
    }


def request_mock_url(urls, params):
    path_param = '?'
    for ind, key in enumerate(params):
        tail = '' if ind == len(params) - 1 else '&'
        path_param += f"{key}={params[key]}{tail}"

    return f"{urls}{path_param}"


def start_and_end_day(weeklyFlg=False):
    today = datetime.date.today()
    end_date = today
    start_day = end_date - datetime.timedelta(days=(7 if weeklyFlg else 1))
    return {
        'start_date': start_day.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
