import requests
import json

from celery_app import app
from celery_app.common import get_sign_1


def ding_mesage(news):
    ding_header = {"Content-Type": "application/json; charset=utf-8", 'timestamp': str((get_sign_1())[0]),
                   'sign': str((get_sign_1())[1])}
    ding_url = 'https://oapi.dingtalk.com/robot/sendBySession?session=ce8e46dc13d957af20951c9e5e3f2e68'
    mes = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": news['title'],
            'text': "#### <font color=#FF0000>{} </font> \n\n {} \n\n来源：金色财经".format(news['title'], news['content']),
            "singleTitle": "阅读全文",
            "singleURL": news['url']
        }
    }

    res = requests.post(ding_url, data=json.dumps(mes), headers=ding_header)


# 要对下面这个函数定时出发，一小时一次吧
@app.task(name = 'task_jinseNews.get_news')
def get_news():
    with open('celery_app/crontabTasks/resource_jinse.txt', 'r') as file:
        latest_news = int(file.read())
    spider_header = {
        'referer': 'https://www.jinse.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }
    res = requests.get(url='https://api.jinse.cn/noah/v2/lives?limit=20&reading=false&source=web&flag=up&id=&category=1'.format(latest_news), headers=spider_header)
    for news in res.json()['list'][0]['lives']:

        if news['id'] == latest_news:
            break
        news_data = {}
        news_data['title'] = news['content_prefix']
        news_data['content'] = news['content'].split('】')[-1]
        news_data['url'] = 'https://www.jinse.com/lives/{}.html'.format(news['id'])
        ding_mesage(news_data)


    latest_news = res.json()['list'][0]['lives'][0]['id']
    with open('celery_app/crontabTasks/resource_jinse.txt', 'w') as file_w:
        file_w.write(str(latest_news))
