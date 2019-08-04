import urllib.request
from bs4 import BeautifulSoup
import gzip
import time
import os
import pymysql
import configparser


def getHtmlFromRemoteUrl(url):
    headers = {
        'Host': 'www.cits0871.com',
        'Proxy-Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'Hm_lvt_28dca3408b4d7b74d7cb72f2ec2b7f80=1563777965; Hm_lpvt_28dca3408b4d7b74d7cb72f2ec2b7f80=1563779615',
    }
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    data = None
    requestBody = urllib.request.Request(url, data, headers)
    content = urllib.request.urlopen(requestBody)
    readContent = content.read()
    try:
        readContent = gzip.decompress(readContent)  # 可能是压缩的gzip格式
    except:
        1 == 1

    try:
        html = readContent.decode('gbk')
    except:
        html = readContent.decode('utf-8')
    else:
        html = html

    return html


def getChapterContent(article_url, content_rule):
    article_Html = getHtmlFromRemoteUrl(article_url)
    chapter_soup = BeautifulSoup(article_Html, "html.parser")
    readContent = chapter_soup.select_one(content_rule).encode_contents()

    try:
        content = readContent.decode('gbk')
    except:
        content = readContent.decode('utf-8')
    else:
        content = content

    return content


# db日志函数
def doDBLog(code, s_code, content):
    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    flow = 'book_spider-' + datetime + str(int(time.time()))
    module = 'book'
    intro = '图书采集'

    dir = os.getcwd()
    ini_file = dir + '/.env.ini'
    config = configparser.ConfigParser()
    config.read(ini_file)
    # step 1 获取数据库所有待更新的图书 并遍历 book
    # 打开数据库连接
    db = pymysql.connect(config['database']['db_host'], config['database']['db_username'],
                         config['database']['db_password'], config['database']['db_database'])

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    sql = "INSERT INTO log(`flow`, `module`, `intro`, `code`,`s_code`,`content`,`created_at`,`updated_at`) VALUES ('%s', '%s', '%s','%d','%d','%s','%s','%s')" % (
    flow, module, intro, code, s_code, content, datetime, datetime)

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except pymysql.InternalError as error:
        code, message = error.args
        print(">>>>>>>>>>>>>", code, message)
        # 发生错误时回滚
        print(sql)
        db.rollback()

    db.close()
