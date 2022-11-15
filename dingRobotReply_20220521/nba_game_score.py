import datetime
import requests
import pymysql
from bs4 import BeautifulSoup

NBADict = {
    '勇士': 'Warriors',
    '快船': 'Clippers',
    '湖人': 'Lakers',
    '太阳': 'Suns',
    '开拓者': 'Trailblazers',
    '国王': 'Kings',
    '雷霆': 'Thunder',
    '独行侠': 'Mavericks',
    '掘金': 'Nuggets',
    '火箭': 'Rockets',
    '森林狼': 'Timberwolves',
    '马刺': 'Spurs',
    '爵士': 'Jazz',
    '灰熊': 'Grizzlies',
    '热火': 'Heat',
    '尼克斯': 'Knicks',
    '76人': '76ers',
    '魔术': 'Magic',
    '凯尔特人': 'Celtics',
    '篮网': 'Nets',
    '奇才': 'Wizards',
    '老鹰': 'Hawks',
    '黄蜂': 'Hornets',
    '公牛': 'Bulls',
    '骑士': 'Cavaliers',
    '活塞': 'Pistons',
    '步行者': 'Pacers',
    '雄鹿': 'Bucks',
    '猛龙': 'Raptors',
    '鹈鹕': 'Pelicans',
}

# 获取当天的信息
def getToday():
    return datetime.date.today()

#  获取一段时间的日期
def getDateList(start_date, end_date):
    date_list = []
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    date_list.append(start_date.strftime('%Y-%m-%d'))
    while start_date < end_date:
        start_date += datetime.timedelta(days=1)
        date_list.append(start_date.strftime('%Y-%m-%d'))
    return date_list

def getNbaGameResult(date):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }
    res = requests.get(f'https://nba.hupu.com/games/{date}', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    # 获取每个比赛的信息
    print(f'{date}:')
    # [日期，team_a, team_a_score, team_b, team_b_score]
    allData = [] # 记录所有数据
    game_infos = soup.select('div.gamecenter_content_l div.list_box')
    for game in game_infos:
        team_vs_flag = game.select('div.team_vs div.team_vs_b span.b')[0].text.strip()
        # 只有结束的才记录
        if team_vs_flag == '已结束':
            team_a = game.select('div.team_vs_a_1 a')[1].text
            team_a = NBADict[team_a]
            #print(team_a)
            team_a_score = game.select('div.team_vs_a_1 div.txt span')[0].text
            #print(team_a_score)
            team_b = game.select('div.team_vs_a_2 a')[1].text
            team_b = NBADict[team_b]
            team_b_score = game.select('div.team_vs_a_2 div.txt span')[0].text
            print(f'{team_a}:{team_b} = {team_a_score}:{team_b_score}')
            allData.append([date, team_a, team_a_score, team_b, team_b_score])
    return allData


def getNbaDataOnPeroid(date1, date2):
    allData = []
    date_list = getDateList(date1, date2)
    for date in date_list:
        nowData = getNbaGameResult(date)
        if nowData:
            allData += nowData
    # 写入db
    writeDb(allData)

    #return allData


def selectDb(date):
    # 连接db
    conn = pymysql.connect(host='47.96.75.130',
                           user='root',
                           password='abAB12',
                           database='nba',
                           charset='utf8')

    # 得到一个可以执行sql的光标
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 定义要执行的sql
    sql = "SELECT * FROM nba.game_score where game_time = '%s' " % date


    # 执行sql
    cursor.execute(sql)
    info = cursor.fetchall()
    mes = ""
    for game in info:
        mes = mes + "{} vs {} {}:{}".format(game['host_team'], game['other_team'], game['host_score'], game['other_score'])
    return mes


def writeDb(data):
    # 连接db
    conn = pymysql.connect(host='47.96.75.130',
                           user='root',
                           password='abAB12',
                           database='nba',
                           charset='utf8')

    # 得到一个可以执行sql的光标
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 定义要执行的sql
    '''
    sql = """
    SELECT * FROM nba.game_score;
    """

    # 执行sql
    cursor.execute(sql)
    info = cursor.fetchall()
    print(info)
    '''

    # 将expense_record信息insert到spm_ledger_record中
    # 定义要执行的sql

    for item in data:
        game_time = item[0]
        other_team = item[1]
        other_score = int(item[2])
        host_team = item[3]
        host_score = int(item[4])


        sql = "insert into nba.game_score(game_time, other_team, other_score, host_team, host_score) values('%s', '%s', %s, '%s', %s)" % (game_time, other_team, other_score, host_team, host_score)

        print(sql)
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            pass # 重复就算了


    # 关闭光标
    cursor.close()
    # 关闭db
    conn.close()




if __name__ == '__main__':
    '''
    print(getToday())
    print(getDateList('2022-04-01', '2022-05-08'))
    getNbaGameResult(getToday())
    print('---------')
    # 一段时间的
    for date in getDateList('2022-04-01', '2022-05-08'):
        getNbaGameResult(date)
    '''
    test_data = getNbaDataOnPeroid('2022-05-08', '2022-05-21')
    print(test_data)
