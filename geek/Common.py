#!/usr/bin/python3
#coding=utf-8

import json
import os
import sys
import time
import logging
from urllib.parse import urljoin

import html2text
import requests
from requests.cookies import cookiejar_from_dict

headers = {
    'Content-Type': "application/json",
    'Referer': "https://account.geekbang.org/dashboard/buy",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    'Accept': "*/*",
    'Host': "time.geekbang.org",
}
session = requests.session()
account_url = 'https://account.geekbang.org/account/ticket/login'
base_url = 'https://time.geekbang.org/serv/v1/'
book_name = ''

phone = ''
pw = ''
prefix = ''

cookies_content = '_ga=GA1.2.1986526120.1575103003; MEIQIA_TRACK_ID=1Wet7DfNqhkEjBXM18lPnLlOFrV; LF_ID=1579521737866-6818105-4231347; MEIQIA_VISIT_ID=1X15zELUvW5SmurzQ6pE6l1LoxS; GCID=4c6936c-a4d3eae-fe4d318-de3c3df; GRID=4c6936c-a4d3eae-fe4d318-de3c3df; _gid=GA1.2.729605111.1587093054; gksskpitn=43436f86-bba2-41d5-8320-80748dd2d8c5; _gat=1; GCESS=BAwBAQgBAwMEqVadXgkBAQcEU.xRRQUEAAAAAAsCBAAEBAAvDQAGBHsG7HgKBAAAAAABBGOhGwACBKlWnV4-; Hm_lvt_022f847c4e3acd44d4a2481d9187f1e6=1587363574,1587363873,1587365632,1587369643; Hm_lpvt_022f847c4e3acd44d4a2481d9187f1e6=1587369643; SERVERID=1fa1f330efedec1559b3abbcb6e30f50|1587369644|1587347923'


def login(cell_phone, password):
    global phone
    global pw
    phone = cell_phone
    pw = password
    login_headers = {
        'Content-Type': "application/json",
        'Referer': "https://account.geekbang.org",
        'Host': "account.geekbang.org",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    }

    data = {
        "country": 86,
        "cellphone": cell_phone,
        "password": password,
        "captcha": "",
        "remember": 1,
        "platform": 3,
        "appid": 1
    }

    assert cell_phone is not None and password is not None
    response = post(account_url, data, hs=login_headers)
    res = response.json()
    if res['code'] != 0:
        logging.error("login failed, error: %s" % str(response))
        sys.exit()
    session.cookies = response.cookies


def post(url, data=None, hs=headers, retry=3):
    payload = json.dumps(data) if data else "{}"
    res = session.request("POST", url, data=payload, headers=hs)
    if res.status_code != 200:
        if retry > 0:
            login(phone, pw)
            return post(url, data, hs, retry - 1)
    return res


def get_article(article_id):
    content_payload = {
        "id": article_id,
        "include_neighbors": True,
        "is_freelyread": True
    }
    comments_payload = {
        "aid": article_id,
        "prev": 0
    }
    content_response = post(urljoin(base_url, 'article'), content_payload)  # 读取文章内容
    comments_response = post(urljoin(base_url, 'comments'), comments_payload)  # 读取评论内容
    data = content_response.json(encoding='utf-8')['data']
    if 'article_content' not in data:
        raise Exception("no article content in article id = %s" % article_id)
    article_title = data['article_title']
    article_content = data['article_content']
    h = html2text.HTML2Text()
    h.ignore_links = False
    md_content = h.handle(article_content)
    md_content = md_content.replace("****", "**")
    md_content = md_content.replace("** **", "**")
    md_content = md_content.replace("**\n**", "**")
    comments = parse_comments(comments_response.json(encoding='utf-8')['data'])
    result = get_title(article_title) + md_content + comments
    write_to_file(result, prefix + article_title)
    logging.info("读取成功 %s" % article_title)
    # 开始解析下一篇文章的地址
    right = data['neighbors']['right']
    if 'id' in right:
        return right['id']


def parse_comments(data):
    if not data:
        return ""

    if len(data["list"]) == 0:
        return ""
    result = "---\n"

    for comment in data["list"]:
        user_name = comment['user_name']
        comment_content = comment['comment_content']
        result = result + '- %s<br/> %s<br/><br/>' % (user_name, comment_content)
        if 'replies' in comment:
            for reply in comment['replies']:
                result = result + '%s:%s \n' % (reply['user_name'], reply['content'])
    return result


def write_to_file(md_text, file_name):
    file_name = file_name.replace('/', '')
    f = open("/home/duke/geek/%s/%s.md" % (book_name, file_name), "w")
    f.write(md_text)
    f.close()


def create_path(path_name):
    path = "/home/duke/geek/%s/" % path_name
    if not os.path.exists(path):
        os.mkdir(path)


def get_title(title):
    return '<h1 style="text-align:center">%s</h1>' % title


def get_cookies():
    cookie = {}
    for s in cookies_content.split(':'):
        name, value = s.strip().split('=', 1)
        cookie[name] = value
    session.cookies = cookiejar_from_dict(cookie)


def main():
    global book_name
    global prefix
    book_name = '技术与商业案例解读'
    create_path(book_name)
    get_cookies()
    article_id = 49
    once = False
    i = 1
    while True:
        prefix = 'Part' + str(i).rjust(3, '0') + ' '
        article_id = get_article(article_id)
        i += 1
        time.sleep(3)  # 休眠一段时间，防止被封
        if once:
            break
        if not article_id:
            break


if __name__ == '__main__':
    main()