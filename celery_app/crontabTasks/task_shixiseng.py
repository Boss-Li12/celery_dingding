import time
import requests
from bs4 import BeautifulSoup
import openpyxl
from openpyxl import Workbook
import datetime


from celery_app import app
from celery_app.common import ding_message_text


JOBTYPE = ['python', 'java', 'c++', 'nlp', '机器学习', '开发', '算法']


class JobSpider:

    # 初始化方法
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'cookie': 'MEIQIA_TRACK_ID=1pkT2J2ec2l7naBrMfOiwRngik7; 1pkT2J2ec2l7naBrMfOiwRngik7=undefined; utm_source_first=sem-baidu-pc-pinpai-4; gr_user_id=7a63884e-132e-4067-9038-5742f918e6b7; uuid=25d0c72a-f9ed-60b3-9e57-596359a4f00a; SXS_VISIT_XSESSION_ID_V3.0="2|1:0|10:1650617941|26:SXS_VISIT_XSESSION_ID_V3.0|48:ZjQ2MDY2ODEtNzdjYy00NzZlLTg1NDQtYjg2MzQwY2Y3NTMz|2414560ff188b1118993a7be4ec7259e3ec1c0a005c13dee226812938586d13b"; SXS_VISIT_XSESSION_ID_V3.0_EXP="2|1:0|10:1650617941|30:SXS_VISIT_XSESSION_ID_V3.0_EXP|16:MTY1MzIwOTk0MQ==|9a6e89be79f0361c96cdda971dce8ad18a5ac197180b7dee0087a9e92b316dc4"; SXS_XSESSION_ID="2|1:0|10:1650617941|15:SXS_XSESSION_ID|48:ZWExZjA3ZjctMmM0NC00NjZlLThjYzMtZDdhM2I5MzkzZDNk|e6a984347816993781b7bf0611cc28f0302e70b00e74bade2077e815d0aa5245"; SXS_XSESSION_ID_EXP="2|1:0|10:1650617941|19:SXS_XSESSION_ID_EXP|16:MTY1MDcwNDM0MQ==|5e26cbb0bf22b4a457bf8c3052867958699daad4431279a48ae19f3bfa63ee19"; Hm_lvt_03465902f492a43ee3eb3543d81eba55=1650617943; MEIQIA_VISIT_ID=2899Tg5aEMenOtWTlTmeyzvS09S; uid1=null; uid2=0bcee902-3de6-c0c0-a59e-e4620820feb8; search=; gr_session_id_96145fbb44e87b47=054f8da7-e08d-4ba9-8187-c51e2ebd5906; gr_cs1_054f8da7-e08d-4ba9-8187-c51e2ebd5906=user_id:null; gr_session_id_96145fbb44e87b47_054f8da7-e08d-4ba9-8187-c51e2ebd5906=true; utm_source=PC; utm_campaign=PC; Hm_lpvt_03465902f492a43ee3eb3543d81eba55=1650626886; RANGERS_WEB_ID=7089350039508633119; RANGERS_SAMPLE=0.30107820842041866',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
            'referer': 'https://resume.shixiseng.com/'
        }
        self.session.headers.update(self.headers)


    # 获取单页数据
    def get_one_page_data(self, url):
        one_page_data = []  # 用于按条记录获取到的招聘信息
        # req = requests.get(url, headers=self.headers)
        req = self.session.get(url)
        # 获取成功时，解析网页
        if req.status_code == 200:
            for data in req.json()['msg']['data']:
                job_mes = {}
                job_mes['city'] = data['city']
                job_mes['company_name'] = data['cname']
                job_mes['name'] = data['name']
                job_mes['degree'] = data['degree']

                if float(data['maxsal']) == 0:
                    job_mes['salary'] = '面议'
                else:
                    job_mes['salary'] = (float(data['maxsal']) + float(data['minsal'])) * 6
                job_mes['industry'] = data['industry']
                job_mes['start_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
                job_mes['end_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
                job_mes['active'] = 1
                one_page_data.append(list(job_mes.values()))

            # 返回所有获取到的招聘信息
            return one_page_data, len(one_page_data)

        # 获取失败时，打印失败信息
        else:
            print('解析失败')

    # 获取多页数据
    def get_data(self, keyword):
        data = []  # 用于按条记录 1～10 页所有招聘信息
        for page in range(1,100):
            url = 'https://www.shixiseng.com/app/interns/search/v2?build_time={}&page={}&keyword={}&city=&intern_type=xz'.format(round(time.time()), page, keyword)

            one_page_data, data_len = self.get_one_page_data(url)
            data = data + one_page_data
            if data_len < 20:
                break
            time.sleep(1)  # 防止爬取速度过快被封 ip
        # 返回所有获取到的招聘信息
        return data


    def read_xls(self, workbook, sheet_name):
        sheet = workbook[sheet_name]
        rows = sheet.rows
        data = []
        for row in rows:
            temp = []
            for cell in row:
                temp.append(cell.value)

            temp[-2] = datetime.datetime.strptime((temp[-2]), '%Y-%m-%d').strftime('%Y-%m-%d')
            temp[-3] = datetime.datetime.strptime((temp[-3]), '%Y-%m-%d').strftime('%Y-%m-%d')
            temp[-1] = -temp[-1]
            data.append(temp)

        return data


    def merge(self, old_data, new_data):
        for mes in new_data:
            for data in old_data:
                if data[0:3] == mes[0:3] and data[-1] == -1:
                    data[-2] = mes[-2]
                    data[-1] = 1
                    mes[-1] = 0
                    continue
            if mes[-1] == 1:
                old_data.append(mes)

        for data in old_data:
            if data[-1] == -1:
                data[-1] = 0

        return old_data

    # 保存数据方法
    def save_data(self, job_key, workbook):
        # 处理后的数据
        raw_data = self.get_data(job_key)
        previous_data = self.read_xls(workbook, job_key)
        new_data = self.merge(previous_data, raw_data)
        workbook.remove(workbook[job_key])
        # 选择默认的工作表
        sheet = workbook.create_sheet(job_key)
        for row in new_data:
            sheet.append(row)


    def run(self):
        workbook = openpyxl.load_workbook('celery_app/crontabTasks/shixiseng_jobInfo.xlsx')
        # 获取表单
        # sheet = workbook[sheet_name]
        for job_key in JOBTYPE:

            print("spidering {}".format(job_key))
            self.save_data(job_key, workbook)
        workbook.save('celery_app/crontabTasks/shixiseng_jobInfo.xlsx')
        ding_message_text("完成实习僧爬虫")


# 拉起来
@app.task(name = 'task_shixiseng.get_started')
def get_started():
    spider = JobSpider()
    # 一天一次
    spider.run()
