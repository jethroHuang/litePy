#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'jethro'

import requests, re, json

'''
爬取重庆机电学院学生的成绩
'''
username = "12*******"  # 学号
passworld = "xsc*****"  # 登陆密码

url = "http://i.cqevi.net.cn/zfca/login"
session = requests.session()

# 获取lt参数
lt_for_html = session.get("http://i.cqevi.net.cn/zfca/login")
lt = re.findall(r'<input type="hidden" name="lt" value="(.*?)" />', lt_for_html.text, re.S)

data = {
    'useValidateCode': '0',
    'isremenberme': '0',
    'ip': '',
    'username': username,
    'password': passworld,
    'losetime': '30',
    'lt': lt,
    '_eventId': 'submit',
    'submit1': ''
}

r = session.post(url, data=data)
if "欢迎" in r.text:
    print("登陆成功")
    formdata = {
        "xh": ""
    }

    # 登陆学生信息管理
    xx = session.get("http://i.cqevi.net.cn/zfca?yhlx=student&login=122579031373493679&url=stuPage.jsp")
    # print(xx.text)

    # 获取成绩json
    cj = session.post("http://222.179.45.241:10081/xgxt/xsxx_xsxxgl.do?method=xsxxglCk&type=query",
                      data=formdata)

    jsonx = json.loads(cj.text)

    cj_list = jsonx['stuCjList']

    print("亲爱的{name}，你好，你的成绩已读取成功\n".format(name=jsonx['xqzcbdxxList'][0]['xm']))

    for i in cj_list:
        print(i["kcmc"] + "：" + i["cj"])

# 登出账号
session.get("http://i.cqevi.net.cn/zfca/logout")
input("按回车退出")
