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

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, format_img_url, serverUrl


# 解析详细内容
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
                            if not new_img_url:continue
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
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url:continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith('.pdf') or not_img_url.endswith('.wbep'):
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
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith('.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith('.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = False
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:pass
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
                pro_jscs_html = str(soup.find('div', {'class': 'product-info'})) + '\n' + str(
                    soup.find('div', {'class': 'details'}))
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
                    pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t',"").replace('\r',"").replace('\"', "'")

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
    if product_info['domain'] == 'www.dxs1907.cn':
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
                pro_desc = soup.find('div', {'class': 'e_box d_ProSummary p_ProSummary'}).get_text().replace(
                    '\n', '').replace('\t', '').replace(
                    '\r', '').strip()
            except:
                pro_desc = None

            try:
                pro_yyly = None
            except:
                pro_yyly = None

            try:
                pro_jscs_html = str(soup.find('div', {'class': 'e_box p_content borderB_dividers'})) + '\n' + str(
                    soup.find('div', {'class': 'e_box d_DescriptionBoxA p_DescriptionBoxA'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                images = re.findall('"path":"(.*?)_\{i}xaf\.jpg"', str(html), re.S)
                if images:
                    for img_url in images:
                        try:
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

                    ## 下载图片
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
    #
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
                pro_jscs_html = str(soup.find('div', {'class': 'product_detail_bg'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'product_detail_bg'}).find_all('img'):
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
                pro_jscs_html = str(
                    soup.find('div', {'class': 'tab-con container'}).find_all('div', {'class': 'con'})[-1])
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'productimgs container'}).find_all('img'):
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
                            if not new_img_url:continue
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
                            if not new_img_url:continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith('.pdf') or not_img_url.endswith('.wbep'):
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
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith('.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith('.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = False
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:pass
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
                            if not isinstance(file_url, str) or file_url=='#': continue

                            new_file_url = format_img_url(product_info, file_url.strip())
                            if not new_file_url:continue

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
                pro_jscs_html = str(soup.find('div', {'class': 'richContent richContent0'}))
            except:
                pro_jscs_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                for img in soup.find('div', {'class': 'pdLayoutL'}).find_all('img'):
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
                            if not new_img_url:continue
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
                    not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
                    if not_pro_pic_list:
                        for not_img_url in not_pro_pic_list:
                            not_img_url = not_img_url.strip()
                            new_img_url = format_img_url(product_info, not_img_url)
                            if not new_img_url:continue
                            if new_img_url not in pro_images_front and new_img_url not in pro_video_front:
                                if not_img_url.endswith('.jpg') or not_img_url.endswith('.png') or not_img_url.endswith('.pdf') or not_img_url.endswith('.wbep'):
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
                        if img_url and img_url.endswith('.mp4') or img_url.endswith('.avi') or img_url.endswith('.wmv') or img_url.endswith('.mpeg') or img_url.endswith('.flv') or img_url.endswith('.m4v') or img_url.endswith('.mov'):
                            hash_mongo = MongoPipeline('video_hash').find_one({'hash_key': hash_key})
                            if hash_mongo:
                                new_img_url = hash_mongo.get('video_url_back')
                                pro_video_back.append(new_img_url)
                            else:
                                new_img_url = False
                        else:
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                        if new_img_url:
                            if f'src=\"{img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
                            elif f'src=\"{encode_img_url}\"' in pro_jscs_html:
                                pro_jscs_html = pro_jscs_html.replace(encode_img_url, new_img_url)
                            else:pass
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
