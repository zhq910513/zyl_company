#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: download.py
@time: 2022/4/21 14:17
"""
import hashlib
import os
from multiprocessing.pool import ThreadPool
from os import path

import requests

from common.log_out import log_err, log
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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
}
serverUrl = 'https://zuiyouliao-prod.oss-cn-beijing.aliyuncs.com/zx/image/'
videoServerUrl = 'http://qiniu.zuiyouliao.com/video/upload/'
pic_info = {'id': 0, 'pic_type': 3}
image_base_path = path.dirname(os.path.abspath(path.dirname(__file__)))


# 下载/上传 图片/视频 函数
def DownloadPicture_Video(img_url, retry=0):
    if not img_url:return
    try:
        res = requests.get(img_url, timeout=60)
        if res.status_code == 200:
            basename = hashlib.md5(img_url.encode("utf8")).hexdigest()
            filename = os.path.join(i_path + '/' + basename + '.mp4')
            with open(filename, "wb") as f:
                content = res.content
                f.write(content)

            # upload video
            # uploadUrl = 'http://27.150.182.135:8855/articleMaterials/attach/video'
            uploadUrl = 'https://zshqadmin.zuiyouliao.com/api/information/video/upload'

            file = open(filename, "rb")
            files = {'file': file}

            try:
                print("视频id {0} *** video upLoading ...... ***".format(img_url))
                resp = requests.post(url=uploadUrl, headers=videoUploadHeaders, files=files, verify=False, timeout=120)
                if resp.json().get('code') == '200' and resp.json().get('entity'):
                    return_url = 'https://qiniu.zuiyouliao.com' + resp.json().get('entity')['filePath']
                    print(f"视频id {img_url} *** upload video successfully *** upload {return_url}")
                    MongoPipeline("products").update_item({'_id': None}, {'_id': _id, 'pro_video_front': [img_url], 'pro_video_back': [return_url]})
                elif resp.json().get('status') == '500' and 'DuplicateKey' in resp.json().get('exception'):
                    pass
                else:
                    log_err(resp.json())
            except requests.exceptions.ConnectionError:
                log(f'服务器上传视频网络问题，重试中...{img_url}')
                if retry < 3:
                    return DownloadPicture_Video(img_url, retry + 1)
                else:
                    log_err(f'超过三次 服务器上传视频网络问题  {img_url}')
            except Exception as error:
                log_err(error)
                log_err(uploadUrl)
    except requests.exceptions.ConnectionError:
        print(f'下载视频网络问题，重试中...  {img_url}')
        if retry < 3:
            return DownloadPicture_Video(img_url, retry + 1)
    except Exception as error:
        log_err(error)
        return None
    return None


if __name__ == "__main__":
    i_path = r'D:/Projects/zyl_company/download_data/富強鑫精密工業股份有限公司/files'
    for pro in MongoPipeline("products").find({"company_name" : "富強鑫精密工業股份有限公司", "pro_video_back" : []}).skip(5).limit(1):
        print(pro['pro_link'])
        _id = pro['_id']

        url = ''

        DownloadPicture_Video(url)
