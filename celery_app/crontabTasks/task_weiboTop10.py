import requests
import json
import time

from celery_app import app
from celery_app.common import get_sign_1


def ding_mesage(news):
    # 钉钉header 加入时间戳 和 签名信息
    ding_header = {"Content-Type": "application/json; charset=utf-8", 'timestamp': str((get_sign_1())[0]),
                   'sign': str((get_sign_1())[1])}
    # 自己的oapi robot url，对应特定的token
    ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=cb580af07f2c2556b018d7dd786800a708daae7b6f1f41dba3904016dc67995e'
    mes = {
        "msgtype": "markdown",
        "markdown": {
            'title': "#### <font color=#FF0000>微博十大热门话题 </font> \n\n",
            "text": "## <font color=#FF0000>微博十大热门话题 </font> \n\n",
        }
    }
    # 加一个时间提示
    mes['markdown']['text'] += time.ctime() + " \n\n"

    url_specific = '(https://s.weibo.com/weibo?q=%23{}%23)'
    # 信息link
    for new in news:
        new = ''.join(new.split())
        mes['markdown']['text'] += '[' + new + ']' + url_specific.format(new) + " \n\n"

    res = requests.post(ding_url, data=json.dumps(mes), headers=ding_header)


# 要对下面这个函数定时出发，一小时一次吧
@app.task(name = 'task_weiboTop10.get_news')
def get_news():
    global latest_news
    spider_header = {
        'referer': 'https://weibo.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
    }
    url = 'https://weibo.com/ajax/side/hotSearch'
    res = requests.get(url=url, headers=spider_header)

    news = []
    for i in range(10):
        news.append(res.json()['data']['realtime'][i]['note'])

    ding_mesage(news)
