import urllib.request
from bs4 import BeautifulSoup
import gzip

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
    data = None
    requestBody = urllib.request.Request(url, data, {})
    content = urllib.request.urlopen(requestBody)
    readContent = content.read()
    # html = gzip.decompress(readContent).decode('gbk')
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
    readContent  =  chapter_soup.select_one(content_rule).encode_contents()

    try:
        content = readContent.decode('gbk')
    except:
        content = readContent.decode('utf-8')
    else:
        content = content

    return content



