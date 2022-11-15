import json
import requests
import hmac
import base64
import time
import hashlib
import sympy

# import module
from stupidtalk import analyze
from otherTools import getWeather, getNba
from messageType import sendText, sendMarkdown
from smarttalk import get_turing_response
from CZB_spider import CZB_Spider
from singaporeSales import get_sinapore_sales
import tornado.ioloop
import tornado.web
from nba_game_score import getNbaDataOnPeroid, getToday, selectDb
import datetime



def get_sign(timestamp):
    app_secret = 'd8Ovq-OUKZRaPzzKLBCMN_E05RA8zDPbOs861zxb7y5b8jpLw67zHbWMQ4yKXo5y'
    # app_secret = 'kVAUQEjagaPv3OG2BirIYh7Fwlf-N7qO5Ef3bhoOm7xn9guMMrQFI9Z5MN2GGQop'
    app_secret_enc = app_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


## 利用tornado处理get和post信息
## 并通过write方法回传给发送者地址
class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Hello, world feima")

    def post(self):
        
        sign = self.request.headers.get('Sign')
        
        timestamp = self.request.headers.get('Timestamp')
        if sign != get_sign(timestamp):
            self.write("illegal message")


        body = json.loads(self.request.body.decode('utf-8'))
        post_mes = body.get('text').get('content').strip()
        post_userid = body.get('senderId').strip()

        message_json = json.dumps(selectMes(post_userid='', post_mes=post_mes))
    
        self.write(message_json)



# support the calculation of sympy
global x, y, z
x = sympy.Symbol('x')
y = sympy.Symbol('y')
z = sympy.Symbol('z')

def selectMes(post_userid, post_mes):

    # 判断指令选择对应回复
    if (post_mes == '天气'):
        send_mes = getWeather()
        return sendMarkdown('天气预报', send_mes)
    elif post_mes == '爬nba':
        end_date = getToday()
        start_date = end_date - datetime.timedelta(days=30)
        getNbaDataOnPeroid(str(start_date),str(end_date))
    
        return sendMarkdown('您的结果', '行啦行啦最近一个月的又爬了一次放进数据库了')
    elif post_mes[:3] == 'nba':
        date = post_mes.split()[-1]
        res = selectDb(date)
        return sendMarkdown('您的结果', res)
    elif (post_mes[:4] == 'cal '):
        try:
            ans = eval(post_mes[4:])
        except:
            ans = "你这是什么鬼"
        finally:
            return sendMarkdown('您的结果', ans)
    elif (post_mes[:11] == 'stupidtalk '):
        ans = analyze(post_mes[11:])
        return sendMarkdown('robot', ans)
    elif (post_mes[:10] == 'smarttalk '):
        ans = get_turing_response('1234', post_mes[10:])
        return sendMarkdown('turing_robot', ans)
    elif (post_mes[:5] == '自言自语 '):
        i = 0
        context = post_mes[5:]
        total = ''
        while i < 10:
            name = 'temp1' if i % 2 == 0 else 'temp2'
            now = get_turing_response(name, context)
            total += now + '\n'
            context = now
            i += 1
        return sendMarkdown('turing_robot', total)
    elif (post_mes == '新币实时'):
        time, price = get_sinapore_sales()
        return sendMarkdown(time, price + '(银行现汇买入)')
    elif post_mes == 'CZB':
        return CZB_Spider()
    else:
        return sendText(post_userid, '我懒得理你')


