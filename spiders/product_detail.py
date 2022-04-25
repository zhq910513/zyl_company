#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_detail.py
@time: 2022/4/21 14:17
"""
import hashlib
import pprint

from bs4 import BeautifulSoup

from common.log_out import log_err
from spiders.image_download import command_thread, format_img_url, serverUrl

pp = pprint.PrettyPrinter(indent=4)


# 解析产品详细内容
def parse_detail(product_info, html):
    soup = BeautifulSoup(html, 'lxml')
    if product_info['domain'] == 'www.jmjj.com':
        try:
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'mb-60'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = ' | '.join(
                    [item.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip() for item in
                     soup.find('section', {'class': 'applications mt-60 mb-90'}).find_all('div', {'class': 'item'})])
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('section', {'class': 'mt-90 mb-90'})) + '\n' + str(
                    soup.find('section', {'class': 'mt-90 pb-45 pt-90 bg-lightgray'}))
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
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
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'p_content'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
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
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = None
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'row nbcqcsbox'}))
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
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
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'jyms'}).get_text().replace('\n', '').replace('\t', '').replace('\r', '').replace('简要描述：', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'jyms'})) + '\n' + str(soup.find('div', {'class': 'pro_xxjs'}))
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
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
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('meta', {'name': 'description'}).get('content').replace('\n', '').replace('\t',
                                                                                                                 '').replace(
                    '\r',
                    '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'product-info'})) + '\n' + str(soup.find('div', {'class': 'details'}))
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.oubeitejx.com':
        try:
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'show_property'}).find('p').get_text().replace('\n', '').replace('\t', '').replace('\r','').replace('产品简介：','').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'show_property'})) + '\n' + str(soup.find('div', {'class': 'content_body'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'show_gallery'}).find_all('img'):
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.asiastarpm.com':
        try:
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'cont_body'}).find_all('div', {'class': 'text_box'})[0].get_text().replace('\n', '').replace('\t', '').replace('\r','').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = soup.find('div', {'class': 'cont_body'}).find_all('div', {'class': 'text_box'})[-1].get_text().replace('\n', '').replace('\t', '').replace('\r','').strip()
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_title'})[0]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[0]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_title'})[1]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[1]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_title'})[2]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[2])
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'list-in'}).find_all('a'):
                    try:
                        img_url = img.get('href')
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.gelanjx.com':
        try:
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name']
                elif '系列' in product_info.get('cate_2_name'):
                    series = product_info['cate_2_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'p14-prodcontent-1 blk'}).find_next('div').get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'p14-prodcontent-1 blk'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'p14-prodcontent-1 blk'}).find_all('img'):
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
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': '/'.join(pro_images_back),
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)