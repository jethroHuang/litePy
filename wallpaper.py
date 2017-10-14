#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'JethroCup'

from PIL import Image
import os, sys, random, time
import win32gui, win32con, win32api

'''
每隔一段时间随机设置一个壁纸
'''

# 图片根目录,和脚本处于同一目录
storeFolder = os.path.join(sys.path[0], "wallpaper")  # 为了兼容win10,故使用绝对路径
# 图片分类目录
sortFloder = os.path.join(storeFolder, "被临幸的壁纸")


def set_wallpaper_fromBMP(bmp_path):
    '''
    将BMP图象设置为壁纸
    :param bmp_path:bmp图象的路径
    :return:
    '''

    # 打开值定注册表路径
    k = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(k, "WallpaperStyle", 0, win32con.REG_SZ, "10")  # 2拉伸适应桌面,0桌面居中,6适应,10填充,0平铺
    win32api.RegSetValueEx(k, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 除了1是平铺,其他都是0
    # 刷新桌面
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, bmp_path, 1 + 2)


def set_wallpaper(img_path):
    '''
    将图片转换成bmp格式,然后设置为壁纸
    :param img_path: 图片的路径
    :return:
    '''
    bmp_img = Image.open(img_path)
    new_path = os.path.join(storeFolder, "当前壁纸", "wallpaper.bmp")
    bmp_img.save(new_path, "BMP")

    set_wallpaper_fromBMP(new_path)


def random_wallpaper():
    '''
    从指定分类文件夹返回一个随机图片
    :return: 随机图片的绝对地址
    '''
    imgs = [x for x in os.listdir(sortFloder) if os.path.isfile(os.path.join(sortFloder, x))]
    img = random.choice(imgs)

    return os.path.join(sortFloder, img)

if __name__ == "__main__":
    while True:
        time.sleep(10)  # 休眠60个60秒,就是一个小时
        img_path = random_wallpaper()
        set_wallpaper(img_path)
