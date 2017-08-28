#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, os, re, time, sys
from requests.exceptions import RequestException

__author__ = 'JethroCup'

'''
订阅下载最新的包含关键字的帖子
第三方依赖：requests
开发环境：python3.6.2
'''

# 保存文件的根目录
root_folder = "images"

# 需要抓取的关键字帖子
key_words = ("美乳", "情趣", "丝", "美足", "脚", "裸", "喷", "淫水")

# 轮询时长间隔
sleep = 60

# host
host = "https://t66y.com/"

# 新时代的我们index
xsd = host + "thread0806.php"

# page
page = 1

# fid，自拍区的fid=16
fid = 8


# 检查标题里是否含有关键字
def is_in_words(title):
    for key in key_words:
        if key in title:
            return True


# 检测该帖子是否已下载
def is_exits_tz(title):
    path = os.path.join(root_folder, title)

    if os.path.exists(path):
        return True
    else:
        return False


# 保存所有图片
def save_img(img_urls, title):
    img_path = os.path.join(root_folder, title)

    if not is_exits_tz(title):
        os.makedirs(img_path)

    print("开始下载 : {title}".format(title=title))
    # 文件名下标
    xb = 0
    if not isinstance(img_urls, list):
        return

    for img_url in img_urls:
        print(img_url)
        try:
            r_img = requests.get(img_url)
        except RequestException as e:
            print("遇到了链接错误，跳过第{0}张图片下载，错误信息：{1}".format(xb, e))
            xb += 1
            continue

        file_name = os.path.join(img_path, "{0}.jpg".format(xb))
        with open(file_name, "wb") as f:
            f.write(r_img.content)
        xb += 1


while True:
    cs = {"fid": fid, "search": "", "page": page}

    try:
        r_html = requests.get(xsd, params=cs)
    except RequestException as e:
        print("出现链接异常,5秒后重试 {0}".format(e))
        time.sleep(5)
        continue
    r_html.encoding = "gbk"
    html = r_html.text

    # 获取含有主题列表的html
    title_html = \
        re.findall(r'<tr class="tr2"><td colspan="6" class="tac" style="border-top:0">普通主題</td></tr>(.*?)</table>',
                   html,
                   re.S)[0]

    # 获取第一个主题
    posts = re.findall(r'<tr class="tr3 t_one tac">(.*?)</tr>', title_html, re.S)[0]

    # 取出标题
    title = re.findall(r'id="">(.*?)</a>', posts)[0]

    # 判断标题是否包含关键字
    if is_in_words(title):
        # 判断是否未已下载
        if not is_exits_tz(title):
            # 取出url
            url = re.findall(r'<a href="(.*?)" target="_blank" id="">', posts)[0]
            # 下载该帖子
            r = requests.get(host + url)
            r.encoding = "GBK"
            tz_html = r.text
            # 抓出所有的图片链接
            img_urls = re.findall(r"<input src='(.*?)' type='image' onclick", tz_html, re.S)

            save_img(img_urls, title)

    # 休息一段时间后再来查询
    print("未检测到更新，一段时间后重新检测")

    time.sleep(sleep)
