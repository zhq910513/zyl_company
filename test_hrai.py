import copy
import struct
import time

import requests
from multiprocess.pool import ThreadPool
from pymongo import MongoClient

requests.packages.urllib3.disable_warnings()

"""
    用户配置
"""
MONGO_HOST = '192.168.50.22'
MONGO_DB = 'resume'
MONGO_COLLECTION = 'resume.chunks'

query = {}  # 查询条件
SKIP = 0  # 跳过前面几条数据
LIMIT = 300  # 返回几条数据  默认 None 表示返回全部
PROCESSES = 30  # 并发数

client = MongoClient('mongodb://{}:27017'.format(MONGO_HOST))
coll = client[MONGO_DB][MONGO_COLLECTION]

FILTTER_KEYS = []


def select_all_bdata():
    bdata_list = []
    if LIMIT:
        _mongo = coll.find(query).skip(SKIP).limit(LIMIT)
    else:
        _mongo = coll.find(query).skip(SKIP)
    for num, info in enumerate(_mongo):
        bdata_list.append(info)
    return bdata_list


def bytes2hex(_bytes):
    """二进制转哈希"""
    num = len(_bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % _bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


def file_type(binfile):
    """通过二进制判断文件类型"""
    tl = {
        "FFD8FF": "jpeg",
        "89504E47": "png",
        "D0CF11E0": "doc",
        "504B0304": "docx",
        "255044462D312E": "pdf",
    }
    try:
        if '<!DOCTYPE html>' in binfile.decode():
            return 'html'
    except:
        pass
    ftype = None
    for hcode in tl.keys():
        numOfBytes = len(hcode) // 2
        hbytes = struct.unpack_from("B" * numOfBytes, binfile)
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    if not ftype:
        ftype = 'docx'
    return ftype


# 多线程处理数据
def command_thread(_list, Async=True):
    thread_list = []
    # 设置进程数
    pool = ThreadPool(processes=PROCESSES)

    time_list = []
    code_list = []
    filetype_list = []
    s_code = 0
    error_id = []

    s_time_all = time.time()
    for info in _list:
        if Async:
            out = pool.apply_async(func=_post2server, args=(info,))  # 异步
        else:
            out = pool.apply(func=_post2server, args=(info,))  # 同步
        thread_list.append(out)
    pool.close()
    pool.join()

    for tp in thread_list:
        p_out = tp.get()

        time_list.append(p_out.get('time'))
        code_list.append(p_out.get('code'))
        if p_out.get('code') == 200:
            if p_out.get('msg').get('code') == '9999':
                s_code += 1
        filetype_list.append(p_out.get('filetype'))
        if p_out.get('code') != 200:
            error_id.append(p_out.get('id'))

    try:
        e_time_all = time.time()
        u_time_all = e_time_all - s_time_all
        v_time = u_time_all / LIMIT
        req_rate_s = f'{((LIMIT - len(error_id)) / LIMIT) * 100} %'
        rate_s = f'{(s_code / LIMIT) * 100} %'
        new_time_list = sorted(time_list)
        new_type = copy.deepcopy(filetype_list)
        dist_new_type = list(set(new_type))
        type_count = ''
        for _type in dist_new_type:
            type_count += f'{_type} {filetype_list.count(_type)}次,   '
        print(f'本次测试抽取样例 {LIMIT}\n'
              f'并发请求 {PROCESSES}\n'
              f'总共耗时 {u_time_all}\n'
              f'平均耗时 {v_time}\n'
              f'请求成功率 {req_rate_s}\n'
              f'解析成功率 {rate_s}\n'
              f'单个最长时间 {new_time_list[-1]}\n'
              f'单个最短时间 {new_time_list[0]}\n'
              f'识别文件类统计 {type_count}\n'
              f'识别错误的文件ID {error_id}')
    except:
        pass


def _post2server(info):
    s_time = time.time()
    filetype = file_type(info.get('data'))
    # print(f'{filetype}    {info.get("_id")}')
    try:
        # esume_txt = file2txt(info.get('data')).get('txt')
        # print(esume_txt)

        files = {
            'file': info.get('data'),
        }
        resp = requests.post(url='http://192.168.50.22:5678/qf/file_parse', files=files, verify=False)
        # print(resp.json())
        resp.close()
        return {
            'time': time.time() - s_time,
            'filetype': filetype,
            'code': resp.status_code,
            'id': info.get('_id'),
            'msg': resp.json()
        }
    except Exception as error:
        # print(error)
        return {
            'time': time.time() - s_time,
            'filetype': filetype,
            'code': 1000,
            'id': info.get('_id'),
            'msg': error
        }


def run():
    data_list = select_all_bdata()
    command_thread(data_list)


if __name__ == '__main__':
    run()
