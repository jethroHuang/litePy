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
import time
import shutil
# 配置选项 #
img_path = 'wallpaper'  # 图片存放的位置,脚本所在文件下的wallpaper
category = 'illustration'  # 插画分类
type_ = 'hot'  # 热门插画,如需获取最新壁纸,可改为'new'
page_size = 20  # 每一页要获取的插画数量
thread_num = 3  # 最多用3条线程下载图片
wallpaper_max = 5  # 最多读取5页插画
width_min=1920 # 壁纸的最小宽度
# other #
jilu_path = os.path.join(img_path,"jilu.zz")
config_file = "config.json"

def get_img_urls():
    '''
    获取图片链接
    :return:
    '''
    queue = Queue()
    flag=True

    def filter_url(result):
        '''
        筛选出尺寸要求的插画
        :param result: 获取到的数据,dict类型
        :return:
        '''
        if not result['message'] == 'success' and result['msg'] == "success":
            return False

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
                
                # 如果宽度大于高度表示这是适合电脑壁纸,并且宽度应大于width_min保证清晰度
                if img_width > img_height and img_width >= width_min:
                    queue.put(img_src)
                if queue.qsize() >= wallpaper_max:
                    print("筛选完成")
                    return False
        return True

    # 发送请求得到包含图片url和图片信息的json
    i=0
    while flag:
        canshu = {
            "category": category,
            "type": type_,
            "page_num": i,
            "page_size": page_size
        }
        try:
            result_json = requests.get("https://api.vc.bilibili.com/link_draw/v2/Doc/list", params=canshu).json()
            # 筛选出图片
            flag = filter_url(result_json)
        except Exception as e:
            print(e)
            break
        i=i+1
    return queue


class DownImgThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        if not isinstance(queue, Queue):
            raise type_Error('请传入Queue对象')
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

def checkInternet():
    try:
        requests.get("http://baidu.com")
        return True
    except:
        return False
import shutil

def toastInternetError():
    print("网络错误", "无法连接网络,插画下载失败")

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
    print("开始获取图片链接...")
    queue = get_img_urls()  # 获取图片链接
    print("图片链接获取完成")
    print("开始下载图片...")
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
    print("壁纸下载完成,壁纸保存在脚本所在目录的wallpaper目录里")

def main():
    def int_input(strs):
        try:
            return int(input(strs))
        except:
            return int_input("输入错误,请输入纯数字:")
    global wallpaper_max,width_min
    width_min=int_input("请输入壁纸的最小宽度(比如 1920):")
    wallpaper_max=int_input("请输入你想要多少张壁纸(比如 50):")
    if not checkInternet():
        toastInternetError()  # 提示网络错误
    else:
        if os.path.exists(img_path):
           shutil.rmtree(img_path)
        os.mkdir(img_path)
        run()
        input()

def main_():
    #检查配置文件
    if os.path.exists(config_file):
        #载入配置
        pass
    else:
        #初始化配置
        pass
    
if __name__ == "__main__":
    main()
