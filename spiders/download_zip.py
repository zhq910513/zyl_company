#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: main.py
@time: 2022/4/21 14:17
"""

import pprint

import requests

from spiders.product_detail import parse_detail

# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_detail.py
@time: 2022/4/21 14:17
"""
import hashlib
import re

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, format_img_url, serverUrl

pp = pprint.PrettyPrinter(indent=4)
requests.packages.urllib3.disable_warnings()

picHeaders = {
    'accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': '27.150.182.135:8855',
    'Origin': 'http://8.129.215.170:8855',
    'Pragma': 'no-cache',
    'Referer': 'http://8.129.215.170:8855/swagger-ui.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
}
pic_info = {'id': 0, 'pic_type': 3}

from bs4 import BeautifulSoup


# 请求详细内容
def product_detail(product_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        print(product_info['pro_link'])
        resp = requests.get(url=product_info['pro_link'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            _data = file_parse_detail(product_info, resp.text)
            pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, _data)
    except Exception as error:
        log_err(error)


# 解析详细内容
def file_parse_detail(product_info, html):
    soup = BeautifulSoup(html, 'lxml')

    if product_info['domain'] == "www.topstarltd.com":
        try:
            try:
                replace_list = []
                pro_file_front = []
                pro_file_back = []

                # 收集产品图
                try:
                    for a in soup.find('div', {'class': 'product_detail'}).find_all('a'):
                        try:
                            file_name = a.get('title')
                            img_url = a.get('href')
                            new_img_url = 'http://www.topstarltd.com/' + img_url
                            if not new_img_url: continue
                            if str(new_img_url).endswith('.zip'):
                                pro_file_front.append([file_name, new_img_url, img_url])
                        except:
                            pass
                except:
                    pass

                # 下载
                if pro_file_front:
                    pic_return = command_thread(product_info['company_name'], pro_file_front)
                    if pic_return:
                        replace_list.extend(pic_return)

                if replace_list:
                    for replace_info in replace_list:
                        pro_file_back.append(replace_info[-1])
            except:
                pro_file_front = None
                pro_file_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'pro_file_front': pro_file_front,
                'pro_file_back': pro_file_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)


if __name__ == "__main__":
    for pi in MongoPipeline("products").find({"company_name" : "广东拓斯达科技股份有限公司"}):
        product_detail(pi)
        break