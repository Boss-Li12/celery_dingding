import time
import requests
from bs4 import BeautifulSoup
import openpyxl
from openpyxl import Workbook
import datetime

from celery_app import app
from celery_app.common import ding_message_text


JOBTYPE = ['python', 'java', 'C', 'C++', 'golang']



class JobSpider:
    # 初始化方法
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'cookie': '__gc_id=aed007dfce3b43698c406b8c4250e0a1; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1646572665; __uuid=1646572664800.01; __tlog=1646572664835.36%7C00000000%7C00000000%7C00000000%7C00000000; __s_bid=b6a36d39f89bc3db9c210745f684a4973312; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1646572672; __session_seq=3; __uv_seq=3',
        }
        self.session.headers.update(self.headers)


    # 获取单页数据
    def get_one_page_data(self, url):
        one_page_data = []  # 用于按条记录获取到的招聘信息
        req = self.session.get(url)
        # 获取成功时，解析网页
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, 'html.parser')
            # 获取所有 40 条招聘信息
            job_items = soup.find_all('div', class_='job-card-pc-container')
            # 遍历每条招聘信息，提取出所需数据
            for item in job_items:
                # 用字典存储每条招聘信息
                result = {}
                # 提取职位信息
                result['job_name'] = item.select_one('div.ellipsis-1').text  # 职位名
                result['area'] = item.select_one('span.ellipsis-1').text  # 地区
                result['company_name'] = item.select_one('span.company-name').text  # 公司名
                result['salary'] = item.select_one('span.job-salary').text  # 薪资范围
                # 提取职位要求
                job_labels = item.select('span.labels-tag')
                result['working_exp'] = job_labels[0].text  # 经验要求
                result['edu_level'] = job_labels[1].text  # 学历要求
                # 提取公司信息
                company_labels = item.select('.company-tags-box > span')
                # 若该公司提交了公司类型等信息，则提取出公司类型，否则类型默认为“无”
                if company_labels:
                    result['company_type'] = company_labels[0].text
                else:
                    result['company_type'] = '无'
                # 将每条招聘信息存到列表中
                one_page_data.append(result)

            # 返回所有获取到的招聘信息
            return one_page_data

        # 获取失败时，打印失败信息
        else:
            print('解析失败')


    # 获取多页数据
    def get_data(self, job_key):
        data = []  # 用于按条记录 1～10 页所有招聘信息
        for i in range(10):
            url = 'https://www.liepin.com/zhaopin/?headId=50338e415cb4837971583f47ec6ca922&oldCkId=50338e415cb4837971583f47ec6ca922&fkId=32vtkhyyf8yw5crx6huiu58hrspb67jb&skId=32vtkhyyf8yw5crx6huiu58hrspb67jb&sfrom=search_job_pc&key={}&currentPage={}&scene=page'.format(job_key, i)
            data = data + self.get_one_page_data(url)
            time.sleep(1)  # 防止爬取速度过快被封 ip
        # 返回所有获取到的招聘信息
        return data


    # 处理数据
    def process_data(self, job_key):
        data = self.get_data(job_key)
        total = 0  # 累计平均年薪
        count = 0  # 统计非面议职位个数
        # ['职位名', '地区', '薪资范围', '平均薪资', '学历要求', '经验要求', '公司名', '公司类型', '出现时间', '结束时间', '在线状态']
        rows = []
        # 遍历每条数据
        for item in data:
            # 计算该职位平均年薪
            salary = self.get_salary_value(item['salary'])
            if salary != '面议':
                total += salary
                count += 1
                # 将数据添加到 rows 中
                row = list(item.values())
                row.insert(3, salary)
                row.append(datetime.datetime.now().strftime("%Y-%m-%d"))
                row.append(datetime.datetime.now().strftime("%Y-%m-%d"))
                row.append(1)
                rows.append(row)

        '''salary_avg = round(total / count, 2)  # 计算平均年薪并保留两位小数
        print('Python 相关职位平均年薪是{}元'.format(salary_avg))'''
        return rows


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


    # 计算平均年薪
    def get_salary_value(self, salary):
        if salary == '面议':
            return '面议'
        else:
            if '薪' in salary:
                salary_range, salary_times_str = salary.split('k·')  # 分割成两部分
                salary_times = int(salary_times_str.strip('薪'))  # 一年发多少薪
            else:
                salary_range = salary.strip('k')
                salary_times = 12

            if '-' in salary_range:
                salary_min_str, salary_max_str = salary_range.split('-')  # 分割薪资范围
                salary_min = int(salary_min_str)  # 最低月薪
                salary_max = int(salary_max_str)  # 最高月薪
                salary_avg = (salary_min + salary_max) / 2  # 平均月薪
            else:
                salary_avg = int(salary_range)  # 给定月薪

            return salary_avg * salary_times * 1000  # 计算平均年薪

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
        raw_data = self.process_data(job_key)
        previous_data = self.read_xls(workbook, job_key)
        new_data = self.merge(previous_data, raw_data)
        workbook.remove(workbook[job_key])
        # 选择默认的工作表
        sheet = workbook.create_sheet(job_key)
        # 给工作表重命名
        # sheet.title = job_key
        # 将数据一行一行写入
        for row in new_data:
            sheet.append(row)

        # 保存文件


    def run(self):
        workbook = openpyxl.load_workbook('celery_app/crontabTasks/liepin_jobInfo.xlsx')
        # 获取表单
        # sheet = workbook[sheet_name]
        for job_key in JOBTYPE:

            print("spidering {}".format(job_key))
            self.save_data(job_key, workbook)

        workbook.save('celery_app/crontabTasks/liepin_jobInfo.xlsx')
        ding_message_text("完成爬虫：{}".format(JOBTYPE))



# 拉起来
@app.task(name = 'task_liepin.get_started')
def get_started():
    spider = JobSpider()
    # 一天一次
    spider.run()