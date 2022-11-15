def sendText(post_userid, send_mes):
    # 发送文本形式
    message = {
        "msgtype": "text",
        "text": {
            "content": send_mes
        },
        "at": {
            "atDingtalkIds": [post_userid],
            "isAtAll": False
        }
    }
    return message


def sendMarkdown(title, send_mes):
    # 发送Markdown形式
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": str(title) + ':' + str(send_mes)
        },
        "at": {
            "atDingtalkIds": [],
            "isAtAll": False
        }
    }
    return message