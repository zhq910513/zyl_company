#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: company_info.py
@time: 2022/4/21 14:17
"""
import hashlib
import os
from multiprocessing.pool import ThreadPool

import requests

from common.log_out import log_err, log

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

import pprint

pp = pprint.PrettyPrinter(indent=4)


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
