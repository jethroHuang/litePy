#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
使脚本开机自启,当日期得号数是5的倍数时,自动下载哔哩哔哩相簿中的热门插画
默认间隔5天,获取宽度大于高度的图片(适合设置为电脑壁纸)
依赖:request,win10toast
'''

__author__ = 'JethroCup'

import requests, os
from queue import Queue
from threading import Thread
from win10toast import ToastNotifier
import time

# 配置选项 #
img_path = 'wallpaper'  # 图片存放的位置,脚本所在文件下的wallpaper
category = 'illustration'  # 插画分类
type = 'hot'  # 热门插画,如需获取最新壁纸,可改为'new'
page_size = 20  # 每一页要获取的插画数量
thread_num = 3  # 最多用3条线程下载图片
page_max = 5  # 最多读取3页插画
gap = 5  # 间隔5天

# other #
jilu_path = os.path.join(img_path,"jilu.zz")


def get_img_urls():
    '''
    获取图片链接
    :return:
    '''
    queue = Queue()

    def filter_url(result):
        '''
        筛选出尺寸要求的插画
        :param result: 获取到的数据,dict类型
        :return:
        '''
        if not result['message'] == 'success' and result['msg'] == "success":
            return

        # 清洗出链接,要横屏
        data_items = result['data']['items']
        for item in data_items:
            # 获取图片列表
            item_pictures = item['item']['pictures']

            for img in item_pictures:
                try:
                    img_height = img['img_height']
                    img_width = img['img_width']
                    img_src = img['img_src']
                except:
                    continue

                # 如果宽度大于高度表示这是适合电脑壁纸,并且宽度应大于1000保证清晰度
                if img_width > img_height and img_width > 1000:
                    queue.put(img_src)

    # 发送请求得到包含图片url和图片信息的json
    for i in range(page_max):
        canshu = {
            "category": category,
            "type": type,
            "page_num": i,
            "page_size": page_size
        }
        try:
            result_json = requests.get("https://api.vc.bilibili.com/link_draw/v2/Doc/list", params=canshu).json()
            # 筛选出图片
            filter_url(result_json)
        except Exception as e:
            print(e)
            break
    return queue


class DownImgThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        if not isinstance(queue, Queue):
            raise TypeError('请传入Queue对象')
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            try:
                self.save_img(self.queue.get(False))
            except Exception as e:
                print(e)
                return

    def save_img(self, url):
        try:
            img = requests.get(url)
        except:
            return
        file_path = os.path.join(img_path, os.path.split(url)[1])
        with open(file_path, 'wb') as file:
            file.write(img.content)
            file.close()


def checkBootCondition():
    '''
    检查是否满足启动条件
    :return: True or False >>True表示满足条件
    '''
    current_day = time.localtime().tm_mday

    if current_day % gap == 0 and current_day != get_jilu():
        return True
    else:
        return False


def checkInternet():
    try:
        requests.get("http://baidu.com")
        return True
    except:
        return False


def toastInternetError():
    toaster = ToastNotifier()
    toaster.show_toast("网络错误", "无法连接网络,插画下载失败")

def save_jilu():
    # 保存最后一次下载插画时的号数
    with open(jilu_path,'w') as file:
        file.write(str(time.localtime().tm_mday))
        file.close()

def get_jilu():
    # 读取最后一次下载插画时的号数
    try:
        with open(jilu_path,'r') as file:
            jilu=file.read()
            jilu=int(jilu)
            file.close
            return jilu
    except:
        return 0
def run():
    queue = get_img_urls()  # 获取图片链接
    thread_list = []
    for i in range(thread_num):
        thread = DownImgThread(queue)
        thread.start()
        thread_list.append(thread)

    while not queue.empty():
        pass

    for t in thread_list:
        t.join()


    save_jilu()
    toaster = ToastNotifier()
    toaster.show_toast("壁纸下载完成", '壁纸路径{}'.format(os.path.abspath(img_path)), duration=20)

if __name__ == "__main__":


    # 如果存放图片的文件夹存在则表示已初始化
    if os.path.exists(img_path):
        # 如果已初始化则检查是否满足运行条件
        if checkBootCondition():
            if not checkInternet():
                toastInternetError()  # 提示网络错误
                os._exit(0)  # 退出程序
            # 如果满足则清空图片,然后启动下载程序下载壁纸

            for file in os.listdir(img_path):
                os.remove(os.path.join(img_path, file))
            run()
    # 如果文件夹不存在则开始初始化,下载图片
    else:
        if not checkInternet():
            toastInternetError()  # 提示网络错误
            os._exit(0)  # 退出程序
        os.mkdir(img_path)
        run()
