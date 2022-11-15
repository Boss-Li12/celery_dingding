import requests


def get_turing_response(userid, msg):
    KEY = 'b0f346feca1a4133b4e524df281c661d'
    apiUrl = 'http://openapi.turingapi.com/openapi/api/v2'
    data = {
	    "reqType":0,
        "perception": {
            "inputText": {
                "text": msg
            },
        },
        "userInfo": {
            "apiKey": KEY,
            "userId": userid
        }
    }
    try:
        res = requests.post(url = apiUrl, json = data)
        ans = res.json()["results"][0]["values"]["text"]
    except:
        ans = "陷入了奇怪的错误（有可能是超过了100/天的调用次数)"
    finally:
        return ans

print(get_turing_response("新加坡的天气"))
