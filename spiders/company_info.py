#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: company_info.py
@time: 2022/4/21 14:17
"""
import os
import pprint
from multiprocessing.pool import ThreadPool
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err, log

pp = pprint.PrettyPrinter(indent=4)
import hashlib
from dbs.pipelines import MongoPipeline

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
image_base_path = 'D:/BaiduNetdiskDownload/zyl_company/download_data'


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
                            return product_list(next_page)
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


# 解析产品详细内容
def parse_detail(product_info, html):
    soup = BeautifulSoup(html, 'lxml')
    if product_info['domain'] == 'www.jmjj.com':
        try:
            try:
                pro_desc = soup.find('div', {'class': 'mb-60'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r',
                    '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = ' | '.join(
                    [item.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip() for item in
                     soup.find('section', {'class': 'applications mt-60 mb-90'}).find_all('div', {'class': 'item'})])
            except:
                pro_yyly = None

            try:
                pro_detail = []
                for det in soup.find('section', {'class': 'mt-90 mb-90'}).find_all('div', {'class': 'col-md-6'}):
                    try:
                        h3 = det.find('h3').get_text()
                        p = det.find('p').get_text()
                        pro_detail.append(f"{h3}-{p}")
                    except:
                        pass
                if pro_detail:
                    pro_detail = '\n'.join(pro_detail)
                if pro_desc:
                    pro_detail = '\n'.join([pro_desc, pro_detail])
            except:
                pro_detail = None

            try:
                pro_jscs_html = str(soup.find('main', {'class': 'main product_i'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                for img in soup.find('section', {'class': 'product_i-bg mb-200 mb-md-20'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                for img in soup.find('section', {'class': 'mt-90 mb-90'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                if pro_images_front:
                    command_thread(product_info['company_name'], pro_images_front, Async=True)

                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if not str(img_url).startswith('https:'):
                            encode_img_url = 'https:' + img_url
                        else:
                            encode_img_url = img_url
                        new_img_url = serverUrl + hashlib.md5(encode_img_url.encode("utf8")).hexdigest() + '.' + \
                                      img_url.split('.')[-1]
                        pro_images_back.append(new_img_url.split('/')[-1])
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_yyly': pro_yyly,
                'pro_desc': pro_detail,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.njkwls.com":
        try:
            pro_desc = None
            pro_detail = None
            if pro_desc:
                pro_detail = '\n'.join([pro_desc, pro_detail])
            pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'info_right'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                for img in soup.find('div', {'class': 'p_content'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                if pro_images_front:
                    command_thread(product_info['company_name'], pro_images_front, Async=True)

                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue
                        new_img_url = serverUrl + hashlib.md5(encode_img_url.encode("utf8")).hexdigest() + '.' + \
                                      img_url.split('.')[-1]
                        pro_images_back.append(new_img_url.split('/')[-1])
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_yyly': pro_yyly,
                'pro_desc': pro_detail,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.gdhuaxing.com':
        try:
            pro_desc = None

            pro_yyly = None

            try:
                pro_detail = []
                for det in soup.find_all('div', {'class': 'nbcqcsb_slideitem'}):
                    for p in det.find_all('p'):
                        try:
                            pro_detail.append(p.get_text().replace('\n', '').replace('\t', '').replace(
                                '\r',
                                '').strip())
                        except:
                            pass
                if pro_detail:
                    pro_detail = '\n'.join(pro_detail)
                if pro_desc:
                    pro_detail = '\n'.join([pro_desc, pro_detail])
            except:
                pro_detail = None

            try:
                pro_jscs_html = str(soup.find('body'))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                for img in soup.find('div', {'class': 'nbcpxqboxl_lb'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                for img in soup.find('div', {'class': 'swiper-wrapper nbcqcsb_wrapper'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                if pro_images_front:
                    command_thread(product_info['company_name'], pro_images_front, Async=True)

                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if not str(img_url).startswith('https:'):
                            encode_img_url = 'https:' + img_url
                        else:
                            encode_img_url = img_url
                        new_img_url = serverUrl + hashlib.md5(encode_img_url.encode("utf8")).hexdigest() + '.' + \
                                      img_url.split('.')[-1]
                        pro_images_back.append(new_img_url.split('/')[-1])
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_yyly': pro_yyly,
                'pro_desc': pro_detail,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.syntop-ien.com":
        try:
            try:
                pro_desc = soup.find('div', {'class': 'jyms'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r',
                    '').strip()
            except:
                pro_desc = None

            pro_yyly = None

            try:
                pro_detail = soup.find('div', {'class': 'pro_xxjs'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r',
                    '').strip()
                if pro_desc:
                    pro_detail = '\n'.join([pro_desc, pro_detail])
            except:
                pro_detail = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'prodetail_con'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'jqzoom'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                if pro_images_front:
                    command_thread(product_info['company_name'], pro_images_front, Async=True)

                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if not str(img_url).startswith('https:'):
                            encode_img_url = 'https:' + img_url
                        else:
                            encode_img_url = img_url
                        new_img_url = serverUrl + hashlib.md5(encode_img_url.encode("utf8")).hexdigest() + '.' + \
                                      img_url.split('.')[-1]
                        pro_images_back.append(new_img_url.split('/')[-1])
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_yyly': pro_yyly,
                'pro_desc': pro_detail,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'tielong437.51pla.com':
        try:
            pro_desc = None

            pro_yyly = None

            try:
                pro_detail = soup.find('meta', {'name': 'description'}).get('content').replace('\n', '').replace('\t', '').replace(
                    '\r',
                    '').strip()
                if pro_desc:
                    pro_detail = '\n'.join([pro_desc, pro_detail])
            except:
                pro_detail = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'product-info'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'swiper-wrapper'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                if pro_images_front:
                    command_thread(product_info['company_name'], pro_images_front, Async=True)

                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if not str(img_url).startswith('https:'):
                            encode_img_url = 'https:' + img_url
                        else:
                            encode_img_url = img_url
                        new_img_url = serverUrl + hashlib.md5(encode_img_url.encode("utf8")).hexdigest() + '.' + \
                                      img_url.split('.')[-1]
                        pro_images_back.append(new_img_url.split('/')[-1])
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_yyly': pro_yyly,
                'pro_desc': pro_detail,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)

# 下载/上传 图片 函数
def DownloadPicture_Video(img_path, img_url, retry=0):
    # 图片
    if img_url and img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith('.pdf') or img_url.endswith(
            '.gif'):
        try:
            res = requests.get(img_url, timeout=60)
            if res.status_code == 200:
                basename = hashlib.md5(img_url.encode("utf8")).hexdigest() + '.' + img_url.split('.')[-1]
                filename = os.path.join(img_path + '/' + basename)
                with open(filename, "wb") as f:
                    content = res.content
                    f.write(content)

                # upload picture
                uploadUrl = 'http://27.150.182.135:8855/api/common/upload?composeId={0}&type={1}&isNameReal=0'.format(
                    pic_info['id'], pic_info['pic_type'])

                files = {
                    'file': (basename, open(filename, 'rb'), 'image/jpg')
                }

                picHeaders.update({
                    'Content-Length': str(os.path.getsize(filename))
                })

                try:
                    resp = requests.post(url=uploadUrl, headers=picHeaders, files=files, timeout=60)
                    if resp.json().get('message') == '携带数据成功':
                        print(
                            f"id {pic_info['id']} *** type {pic_info['pic_type']} *** download image successfully:{img_url} *** upload status {resp.json().get('code')}")
                    else:
                        log_err(resp.json())
                except requests.exceptions.ConnectionError:
                    log('服务器上传图片网络问题，重试中...')
                    if retry < 3:
                        return DownloadPicture_Video(img_path, img_url, retry + 1)
                    else:
                        log_err(f'服务器上传图片网络问题，重试中...   {img_url}')
                except Exception as error:
                    log_err(error)
                    log_err(uploadUrl)
        except requests.exceptions.ConnectionError:
            print(f'下载图片网络问题，重试中...  {img_url}')
            if retry < 3:
                return DownloadPicture_Video(img_path, img_url, retry + 1)
        except Exception as error:
            log_err(error)
            return None
        return None
    else:
        pass


# 多线程处理数据
def command_thread(company_name, image_list, Async=True):
    thread_list = []
    # 设置进程数
    pool = ThreadPool(processes=8)

    for img_url in image_list:
        file_path = image_base_path + f'/{company_name}'
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        if Async:
            out = pool.apply_async(func=DownloadPicture_Video, args=(file_path, img_url,))  # 异步
        else:
            out = pool.apply(func=DownloadPicture_Video, args=(file_path, img_url,))  # 同步
        thread_list.append(out)
        # break
    pool.close()
    pool.join()


# 格式化图片链接
def format_img_url(product_info, img_url):
    try:
        if 'http:' not in img_url and 'https' not in img_url:
            if f'http://{product_info["domain"]}' not in img_url:
                img_url = f'http://{product_info["domain"]}' + img_url
            elif f'https://{product_info["domain"]}' not in img_url:
                img_url = f'https://{product_info["domain"]}' + img_url
            else:
                pass
        return img_url
    except:
        return None


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

    for pi in MongoPipeline("products").find({'status': None}):
        product_detail(pi)
        # break
