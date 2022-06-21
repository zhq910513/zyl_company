#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: main.py
@time: 2022/4/21 14:17
"""
import os
import time
from os import path

import requests

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.product_detail import parse_detail
from spiders.product_list import parse_list
import pprint
pp=pprint.PrettyPrinter(indent=4)
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

from bs4 import BeautifulSoup


# 请求列表
def product_list(company_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        resp = requests.get(company_info['company_url'], headers=headers, verify=False)
        resp.encoding = 'gbk'
        if resp.status_code == 200:
            parse_list(company_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)


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
            _data = parse_detail(product_info, resp.text)
            pp.pprint(_data)
            html_css = _data.get('pro_jscs_html')
            if html_css:
                html_css = html_css.replace('\"', "'")
                html_css = html_css.replace('\n', "'").replace('\t', "'").replace('\r', "'")
                _data['pro_jscs_html'] = html_css
            MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, _data)
    except Exception as error:
        log_err(error)


# 获取所有分类
def get_all_category(company_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        resp = requests.get(company_info['company_url'], headers=headers, verify=False)
        resp.encoding = 'gbk'
        if resp.status_code == 200:
            return parse_all_category(company_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)

# 解析所有分类
def parse_all_category(company_info, html):
    url_list = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for li in soup.find('div', {'class': 'sort_nor'}).find_all('tr'):
            cate_1_name = li.find('a').get_text().strip()
            _link = 'http://www.kshrjx.com/' + li.find('a').get('href')
            url_list.append({
                'company_name': company_info['company_name'],
                'company_url': _link,
                'cate_1_name': cate_1_name,
                'cate_2_name': None,
                'cate_3_name': None
            })
    except Exception as error:
        log_err(error)
    return url_list


# 获取所有分类
def get_all_category_2(company_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        resp = requests.get(company_info['company_url'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            return parse_all_category_2(company_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)

# 解析所有分类
def parse_all_category_2(company_info, html):
    url_list = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for li in soup.find('div', {'class': 'product_type'}).find_all('li'):
            _link = li.find('a').get('href')
            if not str(_link).startswith('http'):
                link = 'http://www.topstarltd.com' + _link
            else:
                link = _link
            cate_2_name = li.get_text().strip()
            url_list.append({
                'company_name': company_info['company_name'],
                'cate_1_name': company_info['cate_1_name'],
                'company_url': link,
                'cate_2_name': cate_2_name
            })
    except Exception as error:
        log_err(error)
    return url_list


if __name__ == "__main__":
    ci = {
        'company_name': '昆山恒诚荣机械设备有限公司',
        'company_url': 'http://www.kshrjx.com/product.asp'
    }
    # product_list(ci)

    # urls_1 = get_all_category(ci)
    # for url_info in urls_1:
    #     print(url_info)
    #     product_list(url_info)
    #     break
    #     urls_2 = get_all_category_2(url_info)
    #     print(urls_2)
    #     for url_info_2 in urls_2:
    #         print(url_info_2['cate_2_name'])
    #         # print(url_info_2)
    #         product_list(url_info_2)
    #         # break
    #     # break

    for pi in MongoPipeline("products").find({"company_name" : "东莞信易电热机械有限公司", "pro_jscs_html" : ""}):
        product_detail(pi)
        # break
