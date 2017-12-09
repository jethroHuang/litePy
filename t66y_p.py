#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, requests, time, sys, uuid
from requests.exceptions import RequestException
from queue import Queue
from threading import Thread

__author__ = 'JethroCup'

'''
本程序可取草榴网的新时代的我们中的帖子图片

程序的依赖：
requests

开发环境：python3.6.2
'''

# 保存文件的根目录
root_folder = "images"

# 需要抓取的关键字帖子
key_words = ("白丝","丝袜","黑丝")

# 是否在遇到已下载的帖子时退出程序
auto_exit = False

# host
host = "https://t66y.com/"

# 列表页
xsd = host + "thread0806.php"

# page
page = 1

# fid 草榴网的旗帜fid=16
fid = 8

# 图片下载线程数
thread_num = 4


class SaveImg_thread(Thread):
    def __init__(self, queue,name):
        Thread.__init__(self,name=name)
        if not isinstance(queue, Queue):
            raise TypeError("请传入Queue得实例")

        self.queue = queue

    def run(self):
        while True:
            if self.queue.empty():
                break
            try:
                item = self.queue.get(False)
                self.save(item)
            except Exception as e:
                print(e)

    def save(self, item):
        if not isinstance(item, dict):
            raise TypeError("请传图dict数据")
        self.img_url = item["img_url"]
        self.title = item["title"]

        img_path = os.path.join(root_folder, self.title)

        try:
            r_img = requests.get(self.img_url,timeout=5)
        except RequestException as e:
            print("遇到了链接错误，跳过本次图片下载，错误信息：{0}".format(e))
            return
        file_name = os.path.join(img_path, "{0}.jpg".format(str(uuid.uuid1())))
        with open(file_name, "wb") as f:
            f.write(r_img.content)
            f.close()
            r_img.close()


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

    if not isinstance(img_urls, list):
        return

    queue = Queue()
    for img_url in img_urls:
        xx = {
            "title": title,
            "img_url": img_url
        }
        queue.put(xx)

    imgDown_Threads = []

    # 开始创建线程
    for i in range(1,thread_num+1):
        thread = SaveImg_thread(queue,i)
        thread.start()
        imgDown_Threads.append(thread)

    while not queue.empty():
        pass

    # 等待所有线程结束
    for t in imgDown_Threads:
        t.join()

def main():
    global page
    print("程序开始运行")
    while True:
        cs = {"fid": fid, "search": "", "page": page}

        try:
            r_html = requests.get(xsd, params=cs)
        except RequestException as e:
            print("遇到网络错误，将在5秒后重试")
            time.sleep(5)
            continue
        r_html.encoding = "gbk"
        html = r_html.text
        r_html.close()

        # 获取含有主题列表的html
        title_html = \
            re.findall(r'<tbody style="table-layout:fixed;"><tr></tr>(.*?)</table>', html,
                       re.S)[0]

        # 获取所有主题列表
        title_list = re.findall(r'<tr class="tr3 t_one tac">(.*?)</tr>', title_html, re.S)

        # 标题以及链接list
        title_url_list = []

        # 取出所有的标题和url
        for i in title_list:
            # 取出标题
            title = re.findall(r'id="">(.*?)</a>', i)[0]

            # 取出url
            url = re.findall(r'<a href="(.*?)" target="_blank" id="">', i)[0]

            strinfo = re.compile(r'[/\\:*?"<>|]')
            title = strinfo.sub('_', title)

            # 存储标题和url
            if is_in_words(title):
                title_url_list.append((title, url))

        # 挨个进入帖子
        for tz in title_url_list:
            tz_title = tz[0]
            tz_url = tz[1]

            # 判断该帖子是否已下载
            if is_exits_tz(tz_title):
                # 如果auto_exit为True，表示在遇到已下载的帖子时应该退出程序
                if auto_exit:
                    print("遇到已下载的帖子，程序自动退出")
                    exit()
                else:
                    print("已下载{title}，跳过本次下载".format(title=tz_title))
                    continue

            try:
                r = requests.get(host + tz_url)
            except RequestException:
                print("遇到网络错误，跳过 {title} 下载，并且休息5秒".format(title=tz_title))
                time.sleep(5)
                continue
            r.encoding = "GBK"
            tz_html = r.text
            r.close()
            # 抓出所有的图片链接
            img_urls = re.findall(r"<input src='(.*?)' type='image' onclick", tz_html, re.S)

            # 保存图片
            start = time.time()
            save_img(img_urls, tz_title)
            stop=time.time()
            hs=stop-start
            print("下载耗时：{0} 秒".format(hs))
        # 进入下一页
        page = page + 1
        print("进入第{0}页".format(page))

if __name__ == "__main__":
    main()
