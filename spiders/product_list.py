#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_list.py
@time: 2022/4/21 14:17
"""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err, log
from dbs.pipelines import MongoPipeline

import pprint
pp = pprint.PrettyPrinter(indent=4)


# 请求产品列表
def next_product_list(company_info):
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


# 解析产品列表
def parse_list(company_info, html):
    soup = BeautifulSoup(html, 'lxml')
    domain = urlparse(company_info['company_url']).netloc

    try:
        if domain == "www.jmjj.com":
            for li in soup.find_all('li', {'class': 'nav-item'}):
                try:
                    if li.find('a', {'id': 'product-list'}):
                        for num, cate_li in enumerate(
                                li.find('div', {'id': 'product-dropdown'}).find('ul', {'id': 'pills-tab'}).find_all(
                                    'li')):
                            cate_1_name = cate_li.find('a').get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                   '').strip()
                            cate_2_info = li.find('div', {'id': 'product-dropdown'}).find('div', {
                                'id': f'product-{num}-content'})

                            for item in cate_2_info.find_all('div', {'class': 'item'}):
                                cate_2_name = item.find('a', {'class': 'product_sub'}).get('title').replace('\n',
                                                                                                            '').replace(
                                    '\t', '').replace('\r', '').strip()

                                for cate_3_info in item.find_all('li', {'class': 'mb-20'}):
                                    cate_3_name = cate_3_info.find('h4').get_text().replace('\n', '').replace('\t',
                                                                                                              '').replace(
                                        '\r', '').strip()

                                    for pro_info in cate_3_info.find_all('a'):
                                        pro_name = pro_info.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                   '').strip()
                                        pro_link = pro_info.get('href')
                                        if not str(pro_link).startswith('https:'):
                                            pro_link = 'https:' + pro_link

                                        if cate_3_name in cate_2_name:
                                            pro_data = {
                                                'company_name': company_info['company_name'],
                                                'company_url': company_info['company_url'],
                                                'domain': domain,
                                                'cate_1_name': cate_1_name,
                                                'cate_2_name': cate_2_name,
                                                'cate_3_name': None,
                                                'categories': f'{cate_1_name}-{cate_2_name}',
                                                'pro_name': pro_name,
                                                'pro_link': pro_link
                                            }
                                        else:
                                            pro_data = {
                                                'company_name': company_info['company_name'],
                                                'company_url': company_info['company_url'],
                                                'domain': domain,
                                                'cate_1_name': cate_1_name,
                                                'cate_2_name': cate_2_name,
                                                'cate_3_name': cate_3_name,
                                                'categories': f'{cate_1_name}-{cate_2_name}-{cate_3_name}',
                                                'pro_name': pro_name,
                                                'pro_link': pro_link
                                            }
                                        MongoPipeline('products').update_item({'pro_link': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.njkwls.com":
            for a in soup.find('div', {'class': 'sidebar_list'}).find_all('a', {'target': '_self'}):
                try:
                    cate_1_name = a.find('span').get_text()
                    pro_name = cate_1_name
                    pro_link = 'http://www.njkwls.com/' + a.get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
                except:
                    pass
        if domain == "www.gdhuaxing.com":
            for a in soup.find_all('a', {'class': 'nycqlbrbox_cta'}):
                try:
                    cate_1_name = a.find('div', {'class': 'nycqlbrbox_ctatxtct'}).get_text()
                    pro_name = cate_1_name
                    pro_link = a.get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
                except:
                    pass
        if domain == "www.syntop-ien.com":
            cate_1_name = soup.find('div', {'class': 'ny_pos'}).find_all('a')[2].get_text()
            cate_2_name = soup.find('div', {'class': 'ny_pos'}).find_all('a')[3].get_text()
            for pro in soup.find('div', {'class': 'pro_list2'}).find_all('li'):
                pro_name = pro.find('div', {'class': 'pro_img'}).find('img').get('alt')
                pro_link = 'http://www.syntop-ien.com' + pro.find('div', {'class': 'pro_img'}).find('a').get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.syntop-ien.com/products.html',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': cate_2_name,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}-{cate_2_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            try:
                for a in soup.find('div', {'class': 'ly_page'}).find_all('a'):
                    try:
                        if '下一页' in a.get_text():
                            next_page = {
                                'company_name': '南京新拓智能装备有限公司',
                                'company_url': 'http://www.syntop-ien.com' + a.get('href')
                            }
                            return next_product_list(next_page)
                    except:
                        pass
            except:
                pass
        if domain == "tielong437.51pla.com":
            for li in soup.find('ul', {'class': 'product-list'}).find_all('li'):
                try:
                    cate_1_name = li.find('a').get('title')
                    pro_name = cate_1_name
                    pro_link = li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
                except:
                    pass
        if domain == "www.oubeitejx.com":
            cate_1_name = soup.find('div', {'class': 'weizhi'}).find('h2').get_text()
            for pro in soup.find('div', {'class': 'pro'}).find_all('div', {'class': 'proimg'}):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = 'http://www.oubeitejx.com' + pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.oubeitejx.com/cp/',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
        if domain == "www.asiastarpm.com":
            cate_1_name = soup.find('div', {'class': 'cont_body'}).find('div', {'class': 'title'}).get_text()
            for pro in soup.find('ul', {'id': 'product'}).find_all('li'):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.asiastarpm.com/html/product/',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
        if domain == "www.gelanjx.com":
            cate_1_name = soup.find('h3', {'class': 'leftnav-z1-tit'}).get_text().strip()
            for pro in soup.find('div', {'class': 'leftnav-z1-list'}).find_all('dl'):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = 'https://www.gelanjx.com/' + pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'https://www.gelanjx.com/product.html',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
    except Exception as error:
        log_err(error)
