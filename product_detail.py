#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_detail.py
@time: 2022/4/21 14:17
"""
import hashlib
import re

from bs4 import BeautifulSoup
from urllib.parse import quote
from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, format_img_url, serverUrl


# 解析详细内容
def parse_detail(product_info, html):
    soup = BeautifulSoup(html, 'lxml')
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
                pro_desc = soup.find('div', {'class': 'show_property'}).find('p').get_text().replace('\n', '').replace(
                    '\t', '').replace('\r', '').replace('产品简介：', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'show_property'})) + '\n' + str(
                    soup.find('div', {'class': 'content_body'}))
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

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
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
                pro_desc = soup.find('div', {'class': 'p_content'}).get_text().replace('\n', '').replace('\t',
                                                                                                         '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'p_content'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'p_content'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.lk.world":
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
                pro_desc = soup.find('div', {'id': 'banner'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = []
                for item in soup.find('div', {'id': 'swap_1'}).find_all('div', {'class': 'item_name'}):
                    try:
                        pro_yyly.append(item.get_text().strip())
                    except:
                        pass
                if pro_yyly:
                    pro_yyly = ' | '.join(pro_yyly)
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'product_detail'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'large_photo'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        img_url = img_url.strip()
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            try:
                pro_file_front = []
                pro_file_back = []

                # 收集产品文件
                try:
                    for item in soup.find_all('div', {'class': 'item_pdf'}):
                        try:
                            file_url = item.find('a').get('href')
                            if not isinstance(file_url, str) or file_url == '#': continue

                            new_file_url = format_img_url(product_info, file_url.strip())
                            if not new_file_url: continue

                            if new_file_url not in pro_file_front:
                                pro_file_front.append(new_file_url)

                            hash_key = hashlib.md5(new_file_url.encode("utf8")).hexdigest()
                            back_file_url = serverUrl + hash_key + '.' + new_file_url.split('.')[-1]
                            pro_file_back.append(back_file_url)
                        except:
                            pass
                except:
                    pass

                # 下载
                if pro_file_front:
                    command_thread(product_info['company_name'], list(set(pro_file_front)), Async=True)
            except:
                pro_file_front = None
                pro_file_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_file_front': pro_file_front,
                'pro_file_back': pro_file_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
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

                # 产品图
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

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "faygoplast.cn":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'fusion-text'}).find('p').get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for p in soup.find('div', {'class': 'tab-pane fade fusion-clearfix in active'}).find_all('p'):
                    pro_jscs_html.append(str(p))
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'fusion-builder-row fusion-row'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集产品视频
                try:
                    videos = re.findall('plv_(.*?)_', html, re.S)
                    if videos:
                        for img in videos:
                            try:
                                img_url = f'https://dpv.videocc.net/{img[:10]}/b/{img}_3.mp4'
                                if not isinstance(img_url, str): continue

                                new_img_url = format_img_url(product_info, img_url.strip())
                                if not new_img_url: continue
                                if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                    if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                            '.pdf') or img_url.endswith('.wbep'):
                                        pro_images_front.append(new_img_url)
                                    else:
                                        pro_video_front.append(new_img_url)
                                    if img_url not in replace_list:
                                        replace_list.append(img_url)
                            except:
                                pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
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

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.xinbeijx.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = []
                for num, h2 in enumerate(soup.find('div', {'id': 'contentvalue100'}).find_all('h2')):
                    if '特点' in h2.get_text() or '优势' in h2.get_text():
                        try:
                            info = h2.find_next('ul')
                        except:
                            info = h2.find_next('span')
                    else:
                        continue

                    try:
                        pro_desc.append(info.get_text().replace('\n', '').replace('\t', '').replace('\r', '').replace(
                            '在线咨询联系我们  微信公众号  移动版官网', '').strip())
                    except:
                        pass
                if pro_desc:
                    pro_desc = '\n'.join(pro_desc)
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'id': 'contentvalue100'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('ul', {'id': 'img_list'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
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
                pro_desc = soup.find('div', {'class': 'cont_body'}).find_all('div', {'class': 'text_box'})[
                    0].get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = soup.find('div', {'class': 'cont_body'}).find_all('div', {'class': 'text_box'})[
                    -1].get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(
                    soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_title'})[0]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[
                                        0]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div',
                                                                                         {'class': 'text_title'})[
                                        1]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[
                                        1]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div',
                                                                                         {'class': 'text_title'})[
                                        2]) + '\n' + \
                                str(soup.find('div', {'class': 'porduct_show'}).find_all('div', {'class': 'text_box'})[
                                        2])
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

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
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
                pro_desc = soup.find('div', {'class': 'jyms'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').replace('简要描述：', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'pro_xxjs'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                try:
                    for img in soup.find('div', {'class': 'jqzoom'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")
                replace_text = """<script>window.onload=function(){  changeTableHeight();  }  window.onresize=function(){ changeTableHeight();  }  function changeTableHeight(){ $('.proshowParameter table th').each(function (i,o){    var $this=$(o),     height=$this.next().height();    $(this).css('height',height);var obj = $(o);var val = obj.text();if(val == '' || val == null || val == undefined){$(this).addClass('none');}else{$(this).removeClass('none');}});$('.proshowParameter table td').each(function (i,o){var obj = $(o);var val = obj.text();if(val == '' || val == null || val == undefined){$(this).addClass('none');}else{$(this).removeClass('none');}});}</script>"""
                pro_jscs_html = pro_jscs_html.replace(replace_text, "")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
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
                pro_desc = soup.find('div', {'class': 'p14-prodcontent-1 blk'}).find_next('div').get_text().replace(
                    '\n', '').replace('\t', '').replace(
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

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.tieljx.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'neiyer'}).find_all('tr')[1].find_all('p')[-1].get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'neiyer'}).find_all('tr')[1])
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'neiyer'}).find_all('tr')[1].find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.jwell.cn":
        try:
            for info in soup.find_all('div', {'class': 'pbox'}):
                if info.find('h2').get_text() != product_info["pro_name"]: continue

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
                    pro_desc = info.find_all('div', {'class': 'con'})[0].get_text().replace('\n', '').replace('\t',
                                                                                                              '').replace(
                        '\r', '').strip()
                except:
                    pro_desc = None

                try:
                    pro_yyly = None
                except:
                    pro_yyly = None

                try:
                    pro_jscs_html = str(info)
                except:
                    pro_jscs_html = None

                try:
                    replace_list = []
                    pro_images_front = []
                    pro_images_back = []

                    for img in info.find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url)
                            if new_img_url and new_img_url not in pro_images_front:
                                replace_list.append(img_url)
                                pro_images_front.append(new_img_url)
                        except:
                            pass

                    # 替换非产品图片
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for img_url in not_pro_pic_list:
                            new_img_url = format_img_url(product_info, img_url)
                            if new_img_url and new_img_url not in pro_images_front:
                                replace_list.append(img_url)
                                pro_images_front.append(new_img_url)

                    if pro_images_front:
                        command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                    # 替换产品图片
                    if pro_jscs_html and replace_list:
                        for img_url in replace_list:
                            if 'zuiyouliao' in img_url: continue
                            encode_img_url = format_img_url(product_info, img_url)
                            if not encode_img_url: continue

                            hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                            pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                except:
                    pro_images_front = None
                    pro_images_back = None
                finally:
                    pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

                _data = {
                    'pro_link': product_info['pro_link'],
                    'pro_name': product_info['pro_name'],
                    'series': series,
                    'pro_desc': pro_desc,
                    'pro_yyly': pro_yyly,
                    'pro_jscs_html': pro_jscs_html,
                    'pro_images_front': pro_images_front,
                    'pro_images_back': pro_images_back,
                    'status': 1
                }
                return _data
        except Exception as error:
            log_err(error)
    # useon 数据问题
    if product_info['domain'] == "www.useon.cn":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'data-elementor-type': 'wp-page'}).find_all('div', {
                    'class': 'elementor-widget-container'})[1].get_text().strip()

            except:
                pro_desc = None

            try:
                pro_yyly = []
                for num, info in enumerate(soup.find('div', {'data-elementor-type': 'wp-page'}).find_all('div', {
                    'class': 'elementor-widget-container'})):
                    try:
                        if '应用' in info.find('h2').get_text():
                            _div_info = soup.find('div', {'data-elementor-type': 'wp-page'}).find_all('div', {
                                'class': 'elementor-widget-container'})[num + 1]
                            for li in _div_info.find_all('li'):
                                pro_yyly.append(li.get_text().strip())
                            break
                    except:
                        pass
                if pro_yyly:
                    pro_yyly = ' | '.join(pro_yyly)
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for info in soup.find('div', {'data-elementor-type': 'wp-page'}).find_all('div', {
                    'class': 'elementor-widget-container'})[6:-5]:
                    pro_jscs_html.append(str(info))
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
                else:
                    pro_jscs_html = ''
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'data-elementor-type': 'wp-page'}).find_all('div', {
                        'class': 'elementor-widget-container'})[2].find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    # huabaosuliaojixie 数据问题
    if product_info['domain'] == "www.huabaosuliaojixie.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find_all('p', {'class': 'MsoNormal'})[0].get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for p in soup.find('article', {'id': 'pshow'}).find_all('p', {'class': 'MsoNormal'})[1:]:
                    pro_jscs_html.append(str(p))
                try:
                    pro_jscs_html.append(str(soup.find('div', {'align': 'center'})))
                except:
                    pass
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'w3cFocus'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.kymach.com":
        try:
            try:
                if '系列' in product_info['cate_1_name']:
                    series = product_info['cate_1_name'].split('系列')[0] + '系列'
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = []
                for p in soup.find('div', {'id': 'desc1'}).find_all('p'):
                    _text = p.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()
                    if _text:
                        pro_desc.append(_text)
            except:
                pro_desc = None

            try:
                pro_yyly = soup.find('div', {'id': 'desc3'}).get_text().replace('\n', '').replace('\t', '').replace(
                    '\r', '').replace('等', '').replace('。', '').strip()
                if pro_yyly:
                    pro_yyly = ' | '.join(pro_yyly.split('、'))
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'desc'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'detail'}).find_all('img'):
                    try:
                        img_url = img.get('src')
                        if not isinstance(img_url, str): continue

                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                # 替换非产品图片
                not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.topstarltd.com":
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
                pro_desc = soup.find('div', {'class': 'product_basic_introduce'}).get_text().replace('\n', '').replace(
                    '\t', '').replace('\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = [li.get_text() for li in soup.find('div', {'class': 'product_basic_para'}).find_all('li') if
                            '用途' in li.get_text()]
                if pro_yyly:
                    pro_yyly = pro_yyly[0]
                    if '：' in pro_yyly:
                        pro_yyly = pro_yyly.split('：')[1]
                    if '等' in pro_yyly:
                        pro_yyly = pro_yyly.split('等')[0]
                    if '、' in pro_yyly:
                        pro_yyly = ' | '.join(pro_yyly.split('、'))
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'id': 'product1'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'product_basic'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass

                    for a in soup.find('div', {'id': 'product2'}).find_all('a'):
                        try:
                            img_url = a.get('href')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.donghua-ml.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('ul', {'class': 'ul_prodinfo'}).get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'id': 'detailvalue0'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('ul', {'id': 'img_list'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.logge.com.cn":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
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
                pro_jscs_html = str(soup.find('div', {'id': 'id-desc'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'r-product-k'}).find_all('img'):
                        try:
                            img_url = img.get('data-src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith('.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('data-src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'data-src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'data-src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.yonghuazhusuji.com":
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
                pro_desc = soup.find('div', {'class': 'productintro'}).get_text().replace('\n', '').replace('\t',
                                                                                                            '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for num, title in enumerate(soup.find('div', {'class': 'tab-nav container'}).find_all('a')):
                    pro_jscs_html.append(str(title))

                    info = soup.find('div', {'class': 'tab-con container'}).find_all('div', {'class': 'con'})[num]
                    if info:
                        pro_jscs_html.append(str(info))
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'productimgs container'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.tongdamachine.com":
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
                pro_desc = soup.find('div', {'class': 'fk-editor simpleText fk-editor-break-word'}).get_text().replace(
                    '\n', '').replace('\t', '').replace('\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = '\n'.join([
                    str(soup.find('div', {'_modulestyle': '1'}).find_next('div', {'_modulestyle': '79'})),
                    str(soup.find('div', {'_modulestyle': '1'}))
                ])
            except:
                pro_jscs_html = ''

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'pdLayoutL'}).find_all('img'):
                    try:
                        img_url = img.get('data-original')
                        if not isinstance(img_url, str): continue

                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)
                    except:
                        pass

                # 替换非产品图片
                not_pro_pic_list = re.findall('data-original=\"(.*?)\"', pro_jscs_html, re.S)
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))

                # 替换产品图片
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                            "'").replace(
                    'data-original', "src")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    # www.victorpm.com 数据问题
    if product_info['domain'] == "www.victorpm.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'elementor-section-wrap'}).find_next('section')
            except:
                pro_desc = None

            try:
                pro_yyly = []
                for div in soup.find('div', {'class': 'post-content'}).find_all('div', {'class': 'elementor-container elementor-column-gap-default'})[2].find_all('figcaption'):
                    pro_yyly.append(div.get_text())
                if pro_yyly:
                    pro_yyly = ' | '.join(pro_yyly)
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for p in soup.find('div', {'class': 'post-content'}).find_all('div', {'class': 'elementor-container elementor-column-gap-default'})[1:3]:
                    pro_jscs_html.append(str(p))
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'post-content'}).find_all('div', {'class': 'elementor-container elementor-column-gap-default'})[0].find_all('div', {'class': 'elementor-widget-container'})[-1].find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.yizumi.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'caste_2-con2'}).get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'caste_2-xqy'}).find('div', {'class': 'w1200'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    imgs = re.findall('style="background: url\((.*?)\)', html, re.S)
                    for img in imgs:
                        try:
                            img_url = img
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集产品视频
                try:
                    for img in soup.find('div', {'class': 'vidbox'}).find_all('video'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.beierpm.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'pageCon proDpage'}).get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'pinner content-page'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'id': 'procon3'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.dekuma.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'col-md-4'}).find('ul').get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = soup.find('div', {'class': 'rqq_content'}).find('div', {'class': 'vc_tta-container'})\
                    .find('div', {'class': 'vc_tta-panel-body'}).get_text()
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'rqq_content'}).find('div', {'class': 'vc_tta-container'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'col-md-8'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载文件
                try:
                    for img in soup.find('div', {'class': 'download'}).find_all('a'):
                        try:
                            img_url = img.get('href')
                            print(img_url)
                            if not str(img_url).endswith('.pdf') and not str(img_url).endswith('.PDF'):
                                img_url += quote(img.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip())
                            if not isinstance(img_url, str): continue
                            if str(img_url).endswith('.PDF'):
                                img_url = img_url.split('.PDF')[0] + '.pdf'
                            print(img_url)
                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)), Async=True)

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.tongjia.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'cbox-19-0 p_item'}).find('p').get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find_all('div', {'class': 'p_infoItem'})[-1])
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'id': 'magnifierWrapper'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载文件
                try:
                    for img in soup.find('div', {'class': 'ckeditor-html5-video'}).find_all('video'):
                        try:
                            img_url = img.get('src')
                            print(img_url)
                            if not str(img_url).endswith('.pdf') and not str(img_url).endswith('.PDF'):
                                img_url += quote(img.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip())
                            if not isinstance(img_url, str): continue
                            if str(img_url).endswith('.PDF'):
                                img_url = img_url.split('.PDF')[0] + '.pdf'
                            print(img_url)
                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.yankanggroup.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
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
                pro_jscs_html = str(soup.find('div', {'style': 'margin-bottom:50px;'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'style': 'margin-bottom:50px;'}).find_all('h3')[0].find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.qinchuan.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('li', {'class': 'pro_des'}).find('p').get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('ul', {'id': 'sms'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('li', {'class': 'pro_img'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.shini.com.cn":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'prod_top'}).get_text().strip().split('\n')[-1].strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'prod_feature'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'prod_map'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    for img in soup.find('ul', {'class': 'list-unstyled download_list'}).find_all('a'):
                        try:
                            img_url = img.get('href')
                            if str(img_url).startswith('.'):
                                img_url = '/cn/' + img_url[1:]
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            print(new_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.kraussmaffei.ltd":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'txt'}).find_all('p')[0].get_text().strip().split('\n')[-1].strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = []
                for p in soup.find('div', {'class': 'txt'}).find_all('p')[2:]:
                    pro_jscs_html.append(str(p))
                if pro_jscs_html:
                    pro_jscs_html = '\n'.join(pro_jscs_html)
                else:
                    pro_jscs_html = ''
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'img'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    for img in soup.find('div', {'class': 'pro_app__con mb'}).find_all('a'):
                        try:
                            img_url = img.get('href')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            print(new_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集视频
                try:
                    for img in soup.find('div', {'class': 'video_pop__body'}).find_all('video'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            print(new_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.arburg.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'id': 'field_content'}).find_all('div', {'class': 'ce-bodytext'})[0].get_text().strip().split('\n')[-1].strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'id': 'field_content'}).find_all('div', {'class': 'ce-bodytext'})[1].find('ul'))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'id': 'field_content'}).find('div', {'class': 'tx-mwxgallery-pi1'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    for img in soup.find('div', {'id': 'field_content'}).find_all('div', {'class': 'ce-bodytext'})[2].find_all('a'):
                        try:
                            img_url = img.get('href')
                            if not isinstance(img_url, str): continue
                            if not str(img_url).endswith('.pdf'):
                                if str(img_url).endswith('/'):
                                    img_url = img_url[:-1]
                                img_url += '.pdf'

                            new_img_url = format_img_url(product_info, img_url.strip())
                            print(new_img_url)
                            '/fileadmin/redaktion/mediathek/prospekte/arburg_hydraulic_allrounders_680477_zh_cn.pdf'

                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.akei.com.cn":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'product_info'}).get_text().replace('在线询价','').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'product_con'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('ul', {'class': 'showpic_flash'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    for img in soup.find('div', {'class': 'product_con'}).find_all('video'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str):
                                continue
                            if str(img_url).endswith('.mp4'):
                                new_img_url = format_img_url(product_info, img_url.strip())
                                print(new_img_url)

                                if not new_img_url: continue
                                if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                    if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                            '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                        pro_images_front.append(new_img_url)
                                    else:
                                        pro_video_front.append(new_img_url)
                                    if img_url not in replace_list:
                                        replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.china-leshan.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'listbox'}).get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = []
                for div in soup.find('div', {'class': 'listbox'}).find_all('div'):
                    if '产品用途' in div.get_text():
                        pro_yyly.append(div.get_text().split('：')[1].strip().split('等')[0].strip())
                if pro_yyly:
                    pro_yyly = ' | '.join(pro_yyly[0].split('、'))
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('ul', {'class': 'productView-section2-tab clearfix'})) + '\n' + str(soup.find('div', {'class': 'productView-section2-content-swiper'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'productView-section2-content open'}).find_next('div').find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    for img in soup.find('div', {'class': 'flexbox'}).find_all('video'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str):
                                continue
                            if str(img_url).endswith('.mp4'):
                                new_img_url = format_img_url(product_info, img_url.strip())
                                print(new_img_url)

                                if not new_img_url: continue
                                if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                    if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                            '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                        pro_images_front.append(new_img_url)
                                    else:
                                        pro_video_front.append(new_img_url)
                                    if img_url not in replace_list:
                                        replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.fcs.com.tw":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
                else:
                    series = None
            except:
                series = None

            try:
                pro_desc = soup.find('div', {'class': 'col-md-12 pl-0'}).get_text().strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'bs-example tooltip-demo'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'class': 'carousel_holder pd_plate_img_align'}).find_all('img'):
                        try:
                            img_url = img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集下载
                try:
                    try:
                        img_url = soup.find('div', {'class': 'col-md-12 product_detail button'}).find_all('a')[1].get('href')

                        if str(img_url).startswith('../'):
                            img_url = img_url.replace('../', 'https://www.fcs.com.tw/').split('&name')[0]
                        if str(img_url).endswith('.pdf'):
                            new_img_url = format_img_url(product_info, img_url.strip())
                            print(new_img_url)

                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep') or img_url.endswith('.PDF'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                    except:
                        pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.kshrjx.com":
        try:
            try:
                if '系列' in product_info['cate_2_name']:
                    series = product_info['cate_2_name']
                elif '系列' in product_info.get('cate_1_name'):
                    series = product_info['cate_1_name']
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
                pro_jscs_html = str(soup.find('div', {'class': 'product_content'}).find_next('div'))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []
                pro_video_front = []
                pro_video_back = []

                # 收集产品图
                try:
                    for img in soup.find('div', {'id': 'center'}).find_all('img'):
                        try:
                            img_url = 'http://www.kshrjx.com' + img.get('src')
                            if not isinstance(img_url, str): continue

                            new_img_url = format_img_url(product_info, img_url.strip())
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if img_url.endswith('.jpg') or img_url.endswith('.png') or img_url.endswith(
                                        '.pdf') or img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if img_url not in replace_list:
                                    replace_list.append(img_url)
                        except:
                            pass
                except:
                    pass

                # 收集非产品图
                if pro_jscs_html:
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url: continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith(
                                        '.pdf') or not_img_url.endswith('.wbep'):
                                    pro_images_front.append(new_img_url)
                                else:
                                    pro_video_front.append(new_img_url)
                                if not_img_url not in replace_list:
                                    replace_list.append(not_img_url)

                ## 下载
                if pro_images_front:
                    command_thread(product_info['company_name'], list(set(pro_images_front)))
                if pro_video_front:
                    command_thread(product_info['company_name'], list(set(pro_video_front)))

                # 替换
                if pro_jscs_html and replace_list:
                    for img_url in replace_list:
                        img_url = img_url.strip()
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith(
                                '.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith(
                            '.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = ''
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:
                                pass
            except:
                pro_images_front = None
                pro_images_back = None
                pro_video_front = None
                pro_video_back = None
            finally:
                pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_name': product_info['pro_name'],
                'series': series,
                'pro_desc': pro_desc,
                'pro_yyly': pro_yyly,
                'pro_jscs_html': pro_jscs_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'pro_video_front': pro_video_front,
                'pro_video_back': pro_video_back,
                'status': 1
            }
            return _data
        except Exception as error:
            log_err(error)