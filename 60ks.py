#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'JethroCup'


'''
自动下载m.60ks.com网站的小说
第三方依赖:requests
'''
import re
import requests
import os

class DownXs():
    def __init__(self, url, xs_name):
        self.url = url
        self.xs_name = xs_name
        self.host="http://m.60ks.com"
    def get_title(self, html):
        '''
        get章节标题
        :param html:
        :return:
        '''
        try:
            title = re.findall(r'<div class="nr_title" id="nr_title">(.*?)</div>',html,re.S)[0]
            return title
        except Exception as e:
            print("已经到底啦~",e)
            exit(0)

    def get_html(self,url):
        html = requests.get(url)
        html.encoding='gbk'
        return html.text

    def get_content(self,html):
        '''
        获取章节正文
        :param html:
        :return:
        '''
        content = re.findall(r'<div id="nr1">(.*?)</div>',html,re.S)[0]
        content = content.replace('<br/>','\r\n')
        content  =content.replace('&nbsp;',' ')

        return content

    def save_xs(self,title,content):
        '''
        把章节内容保存仅txt
        :param title: 章节标题
        :param content: 章节正文
        :return:
        '''
        with open(self.xs_name,'a') as file:
            file.write(title+content)
            file.close()
    def ent_nextZj(self,html):
        '''
        获取下一章的链接
        :param html:
        :return:
        '''
        url = re.findall(r'<a id="pb_next" href="(.*?)">下一章',html,re.S)[0]
        self.url =self.host+url

    def down(self):
        while True:
            html = self.get_html(self.url)
            title = self.get_title(html)
            content=self.get_content(html)
            self.save_xs(title,content)
            print("已保存->",title)
            self.ent_nextZj(html)

if __name__ == '__main__':
    print("==== m.60ks.com ====")
    zj_url=input("请输入章节内容链接: ")
    file_name = input("请输入要保存的文件名: ")
    xs_down = DownXs(zj_url, file_name)
    xs_down.down()
