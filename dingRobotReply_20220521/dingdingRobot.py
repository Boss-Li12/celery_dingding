# -*- coding: GBK -*-
import requests
import json
import time
import hmac
import hashlib
import base64
import socket
from multiprocessing import Process
import re
import random
from time import sleep
import math
import sympy
import pandas
import numpy
import tornado.ioloop
import tornado.web
from dingdingMessageProcess import MainHandler


# ���߼�
if __name__ == "__main__":
    print("tornado ����������")
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(30421)
    tornado.ioloop.IOLoop.current().start()
