import configparser
import os
import pymysql
import func
from bs4 import BeautifulSoup
import time

# step 0 获取解析配置文件的配置信息
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

cursor.execute("SELECT id,last_chapter,bs_id,`name` from book where finished=0")
data = cursor.fetchall()
for book in data:
    # step 2 根据图书id 获取对应的采集规则
    cursor.execute(
        "SELECT id,site_url,info_url,list_url,detail_url,info_rule,list_rule,detail_rule from book_spider where b_id=%d" % (
            book[0]))
    spider_rules = cursor.fetchall()
    process_status = False
    for spider_rule in spider_rules:
        if (process_status):  # 如果第一次采集ok了那么 不用第二条采集规则备用方案
            break
        # step 4 差异化采集 采集入库
        # step 4.1 采集目录 遍历目录 与last_chapter比较  确定切入点
        list_html = func.getHtmlFromRemoteUrl(spider_rule[3])
        list_soup = BeautifulSoup(list_html, "html.parser")
        start_point = False
        if (book[1] == ''):  # step 3 匹配图书最后更新章节 跟 采集源最新章节比对 如果有更新则更新
            start_point = True

        for link in list_soup.select(spider_rule[6]):
            # chapter_href = "https://www.ddxs.cc" + link.get('href')
            chapter_title = link.get_text()
            if (start_point):  # 如果开始采集内容
                if '/' in link.get('href'):
                    article_url = spider_rule[1] + link.get('href')
                else:
                    article_url = spider_rule[3] + link.get('href')
                ref_id = link.get('href').split('/').pop().split('.').pop(0)
                ref_id = int(ref_id)

                try:
                    chapter_content = func.getChapterContent(article_url, spider_rule[7])
                except:
                    chapter_content = '404:::' + chapter_title + ':::' + article_url  # 采集失败可以继续 回头可以重新采集
                    print('章节' + chapter_title + article_url + '采集失败')

                chapter_content = pymysql.escape_string(chapter_content)

                # step 5 更新图书信息
                datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                sql1 = "INSERT INTO book_chapter(b_id, bs_id, title, content,ref_id,`order`,`created_at`,`updated_at`) VALUES ('%d', '%d', '%s', '%s','%d','%d','%s','%s')" % (
                    book[0], spider_rule[0], chapter_title, chapter_content, ref_id, ref_id, datetime, datetime)
                sql2 = "UPDATE book SET last_chapter = '%s',bs_id='%d' WHERE id = '%d'" % (
                    chapter_title, spider_rule[0], book[0])

                try:
                    # 执行SQL语句
                    cursor.execute(sql1)
                    cursor.execute(sql2)
                    # 提交到数据库执行
                    db.commit()
                except pymysql.InternalError as error:
                    code, message = error.args
                    print(">>>>>>>>>>>>>", code, message)
                    # 发生错误时回滚
                    print(sql1)
                    print(sql2)
                    db.rollback()
                else:
                    print('图书：《%s》章节：《%s》 采集成功' % (book[3], chapter_title))
                    time.sleep(1)

            if (book[1] == chapter_title):  # step 3 匹配图书最后更新章节 跟 采集源最新章节比对 如果有更新则更新
                start_point = True

# 关闭数据库连接
db.close()
