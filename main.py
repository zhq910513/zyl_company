#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: main.py
@time: 2022/4/21 14:17
"""
import os
from os import path

import requests

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.product_detail import parse_detail
from spiders.product_list import parse_list

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
videoPageHeaders = {
    'authority': 'v.jin10.com',
    'method': 'GET',
    'path': '/details.html?id=12574',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
}
videoUploadHeaders = {
    'accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '25',
    'Content-Type': 'application/json',
    'Host': '8.129.215.170:8855',
    'Origin': 'http://8.129.215.170:8855',
    'Pragma': 'no-cache',
    'Referer': 'http://8.129.215.170:8855/swagger-ui.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
}
serverUrl = 'https://zuiyouliao-prod.oss-cn-beijing.aliyuncs.com/zx/image/'
pic_info = {'id': 0, 'pic_type': 3}

import pprint

pp = pprint.PrettyPrinter(indent=4)


# 请求产品列表
def product_list(company_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        resp = requests.get(company_info['company_url'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            parse_list(company_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)


# 请求产品详细内容
def product_detail(product_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        print(product_info['pro_link'])
        resp = requests.get(url=product_info['pro_link'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            _data = parse_detail(product_info, resp.text)
            # print(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
    except Exception as error:
        log_err(error)


"""
                '生产企业': i.get('company_name'),
                '产品类型（1-3级）': i.get('category_excel'),
                '产品名称': i.get('pro_name'),
                '产品图片': i.get('images_excel'),
                '产品介绍': i.get('pro_desc'),
                # '产品详情': i.get('pro_jscs_html'),
                '应用行业-领域': i.get('pro_yyly'),
                '部件介绍': i.get('pro_detail')
"""

if __name__ == "__main__":
    ci = {
        'company_name': '苏州铁龙机械有限公司',
        'company_url': 'https://tielong437.51pla.com/product.htm'
    }
    # product_list(ci)

    for pi in MongoPipeline("products").find({"domain": "www.jmjj.com"}).skip(1):
        product_detail(pi)
        # break
