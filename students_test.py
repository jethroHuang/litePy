#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
__author__ = 'JethroCup'

'''
验证学生学号是否存在
'''


def xhyz(xh,y,n):
    s = requests.get("http://i.cqevi.net.cn/zfca/retakepwdbyquestep2.do?yhm={}".format(xh))
    if "错误提示页面" in s.text:
        n.write(xh+"\n")
        n.flush()
        print("学号{}不存在".format(xh))
    else:
        y.write(xh+"\n")
        y.flush()
        print("学号{}存在".format(xh))

y = open("xh.txt","a")
n=open("xh_n.txt","a")
try:
    for i in range(5000,10000):
        yum_head='126072020'
        yum_fout="%04d"%i

        xhyz(yum_head+yum_fout,y,n)
except Exception as e:
    print(e)
finally:
    y.close()
    n.close()
