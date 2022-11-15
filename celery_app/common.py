import time
import hmac
import hashlib
import base64
import json
import requests

# “自动回复”机器人
def get_sign_1():
    # 当前时间戳
    timestamp =  int(round(time.time() * 1000))
    # 密文
    app_secret = 'kVAUQEjagaPv3OG2BirIYh7Fwlf-N7qO5Ef3bhoOm7xn9guMMrQFI9Z5MN2GGQop'
    # 编码
    app_secret_enc = app_secret.encode('utf-8')
    # 时间戳 + 密文
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    # （时间戳 + 密文） 编码
    string_to_sign_enc = string_to_sign.encode('utf-8')
    # 哈希摘要
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    # base64签名
    sign = base64.b64encode(hmac_code).decode('utf-8')
    # 返回时间戳 和签名
    return timestamp, sign

# dingRobot post message
def ding_message(mes):
    ding_header = {"Content-Type": "application/json; charset=utf-8", 'timestamp': str((get_sign_1())[0]),
                   'sign': str((get_sign_1())[1])}
    ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=cb580af07f2c2556b018d7dd786800a708daae7b6f1f41dba3904016dc67995e'
    res = requests.post(ding_url, data=json.dumps(mes), headers=ding_header)

# message type
def ding_message_text(text):
    mes = {
        "msgtype": "text",
        "text": {
            'content': text
        }
    }
    ding_message(mes)