
import datetime
import time
import requests
from bs4 import BeautifulSoup
import json
import hmac
import hashlib
import base64

def CZB_Spider():
    header = {
        "Content-Type": "application/json",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
        'referer': 'http://www.mof.gov.cn/index.htm',

    }
    url = 'http://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/index.htm'

    # news url concat base url
    def get_url(new):
        if new.startswith("..."):
            new = new[4:]
            return 'http://www.mof.gov.cn/' + new
        if new.startswith(".."):
            new = new[3:]
            return 'http://www.mof.gov.cn/zhengwuxinxi/' + new
        if new.startswith("."):
            new = new[2:]
            return 'http://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/' + new
        else:
            return new

    res = requests.get(url, headers=header)

    soup = BeautifulSoup(res.content, 'html.parser')

    caizhengbu = []

    for block in soup.select(".xwfb_listbox"):
        for news in block.select('li'):
            if news.select_one('span').text == datetime.datetime.now().strftime("%Y-%m-%d"):
                new = news.select_one('a')
                caizhengbu.append('[{}]({})'.format(new.attrs['title'], get_url(new.attrs['href'])))

    mes = {
        "msgtype": "markdown",
        "markdown": {
            'title': "#### <font color= #FF0000>财政部新闻 </font> \n\n",
            "text": "## <font color= #FF0000>财政部新闻 </font> \n\n",
        }
    }

    # 加一个时间提示
    mes['markdown']['text'] += time.ctime() + " \n\n"
    # 信息
    for czb_news in caizhengbu:
       mes['markdown']['text'] += czb_news + " \n\n"

    return mes

'''def ding_mesage(news):

    def get_sign(app_secret='kVAUQEjagaPv3OG2BirIYh7Fwlf-N7qO5Ef3bhoOm7xn9guMMrQFI9Z5MN2GGQop'):
        timestamp = int(round(time.time() * 1000))
        app_secret_enc = app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, sign

    # 钉钉header 加入时间戳 和 签名信息
    ding_header = {"Content-Type": "application/json; charset=utf-8", 'timestamp': str((get_sign())[0]),
                   'sign': str((get_sign())[1])}
    # 自己的oapi robot url，对应特定的token
    ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=cb580af07f2c2556b018d7dd786800a708daae7b6f1f41dba3904016dc67995e'
    mes = {
        "msgtype": "markdown",
        "markdown": {
            'title': "#### <font color= #FF0000>财政部新闻 </font> \n\n",
            "text": "## <font color= #FF0000>财政部新闻 </font> \n\n",
        }
    }

    # 加一个时间提示
    mes['markdown']['text'] += time.ctime() + " \n\n"
    # 信息
    for new in news:
       mes['markdown']['text'] += new + " \n\n"
    res = requests.post(ding_url, data=json.dumps(mes), headers=ding_header)

# 每天23点跑一次
ding_mesage(CZB_Spider())'''