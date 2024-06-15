# --*--encoding:utf-8--*--
'''
http的工具类
'''
import copy
import enum
import logging
import json
import time
import traceback

import requests
import urllib.request
from urllib.parse import urlencode
from SpiderForCollege.utils import timing


session = requests.Session()

@timing(log_params=True, log_level=logging.INFO)
def http_post(url, data, headers=None, timeout=600,stop_post_times=1):
    '''
    requests 发送postq请求
    :param url:
    :param data:dict
    stop_post_times:最大调用次数，默认1，大于1时，重试n-1次
    :return:
    '''
    text = ""
    data_size_mb=0
    try:
        # raise Exception("手动抛出异常")
        data_size_mb = len(json.dumps(data).encode()) / 1024.0 / 1024.0
        print("{} data_size:{:.2f}MB".format(url,data_size_mb))#0.26MB 500
        r = session.post(url=url, data=json.dumps(data),
                         headers={'Content-Type': 'application/json','Connection': 'close'} if not headers else headers, timeout=timeout)
        if r.status_code == 200:
            text = r.text
        else:
            # text = "%d error,text:%s" % (r.status_code, r.text)
            # print("%d error,text:%s,url:%s,data:%s" % (r.status_code, r.text, url, data))
            # send_msg_to_ding(f"url:{url},data:{data},status_code:{r.status_code},error_info:{text}")
            if stop_post_times-1 >= 1:
                time.sleep(0.1)
                text = http_post(url, data, headers, timeout,stop_post_times-1)
            else:
                text = "%d error,text:%s" % (r.status_code, r.text)
                print(text)
                print(f"url:{url},data:{data},status_code:{r.status_code},error_info:{text}")
        # return text
    except Exception as err:
        if stop_post_times - 1 >= 1:
            time.sleep(0.1)
            text = http_post(url, data, headers, timeout, stop_post_times - 1)
        else:
            print(f"error_info:{str(err)},url:{url},data_size:{data_size_mb}MB,data:{data}")
            print(traceback.format_exc())
    finally:
        return text


def http_post_not_session(url, data, headers=None, timeout=60):
    '''
    requests 发送postq请求
    :param url:
    :param data:dict
    :return:
    '''
    try:
        r = requests.post(url=url, data=json.dumps(data),
                          headers={'Content-Type': 'application/json;charset=utf-8'} if not headers else headers,
                          timeout=timeout)
        text = ""
        if r.status_code == 200:
            text = r.text
        else:
            text = "%d error,text:%s" % (r.status_code, r.text)
            print("%d error,text:%s,url:%s,data:%s" % (r.status_code, r.text, url, data))
            print(f"url:{url},data:{data},status_code:{r.status_code},error_info:{text}")
        return text
    except Exception as err:
        print(f"url:{url},data:{data},error_info:{str(err)}")
        print(traceback.print_exc())


def http_get(url, timeout=600):
    '''
    requests 发送postq请求
    :param url:
    :param data:dict
    :return:
    '''
    try:
        r = session.get(url=url, headers={'Content-Type': 'application/json'}, timeout=timeout)
        text = ""
        if r.status_code == 200:
            text = r.text
        else:
            text = "%d error,text:%s" % (r.status_code, r.text)
            print("%d error,text:%s,url:%s" % (r.status_code, r.text, url))
            print(f"url:{url},status_code:{r.status_code},error_info:{text}")
        return text
    except Exception as err:
        print(traceback.print_exc())
        print(f"url:{url},error_info:{str(err)}")


def http_post_file(url, data={}, files=None,timeout=600):
    '''
    post发送请求文件
    :param url:请求的url
    :param data:
    :param files:
    :return:
    '''
    try:
        r = requests.post(url=url, data=data, files=files, timeout=timeout)
        text = ""
        if r.status_code == 200:
            text = r.text
        else:
            text = "%d error,text:%s" % (r.status_code, r.text)
            print("%d error,text:%s,url:%s,data:%s" % (r.status_code, r.text, url, data))
            print(f"url:{url},data:{data},status_code:{r.status_code},error_info:{text}")
        return text
    except Exception as err:
        print(f"url:{url},data:{data},error_info:{str(err)}")
        print(traceback.print_exc())


def http_post_formdata(url, data, headers=None):
    '''
    requests 发送postq请求
    :param url:
    :param data:dict
    :return:
    '''
    try:
        encode_data = urlencode(data)
        r = session.post(url=url, data=encode_data,
                         headers={'Content-Type': 'application/json'} if not headers else headers, timeout=600)
        text = ""
        if r.status_code == 200 or r.status_code == 201:
            text = r.text
        else:
            text = "%d error,text:%s" % (r.status_code, r.text)
            print("%d error,text:%s,url:%s,data:%s" % (r.status_code, r.text, url, data))
            print(f"url:{url},data:{data},status_code:{r.status_code},error_info:{text}")
        return text
    except Exception as err:
        print(f"url:{url},data:{data},error_info:{str(err)}")
        print(traceback.print_exc())


def posturl(url, data={}, headers={}):
    '''

    :param url:
    :param data:
    :param headers:
    :return:
    '''
    # try:
    params = json.dumps(data).encode(encoding='UTF8')
    req = urllib.request.Request(url, params, headers)
    r = urllib.request.urlopen(req)
    html = r.read()
    r.close()
    return html.decode("utf-8")


class ContentStatus(enum.IntEnum):
    """区别于 HttpStatus, 通常认为是不太好的设计"""

    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.description = description
        return obj

    OK = 0, 'OK', 'success'
    FAILED = 500, 'Internal Server Error', 'generic error'
    TIMEOUT = 504, 'Gateway Timeout'


def http_get_2(url, timeout=600,stream=True):
    '''
    requests 发送postq请求  下载资源中心文件
    :param url:
    :param data:dict
    :return:
    '''
    try:
        req = requests.get(url=url,stream=stream, timeout=timeout)
        if req.status_code != 200:
            print(f"url:{url},status_code:{req.status_code},error_info:{req.text}")
        return req
    except Exception as err:
        print(f"url:{url},error_info:{str(err)}")
        print(traceback.print_exc())

