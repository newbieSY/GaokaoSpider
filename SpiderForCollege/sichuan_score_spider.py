#--*--encoding:utf-8--*--

import requests
import io
import os
import re
import json
from bs4 import BeautifulSoup
from SpiderForCollege.utils import http_utils
from SpiderForCollege.db.DBUtil import DBUtil
from SpiderForCollege.utils import pool_utils#待公开
import pymysql
import logging

host = '127.0.0.1'
port = 3306
user = 'root'
password = '123456'
db = "faker"

connect = pymysql.connect(host=host,
                           port=port,
                           user=user,
                           passwd=password,
                           db=db,
                           charset='utf8')
img_extract_url = "http://127.0.0.1:9231/image_extract?"

year_pattern = re.compile("^.*?(\\d{4})年.*$")
score_line_pattern = re.compile("^.*?(专科批|专科提前批|本科二批|本科一批|本科提前批).*$")
category_pattern = re.compile("^.*?(文科|理科).*$")

def get_images(url, province):
    '''
    插入所有的调档线的url和image url
    '''
    db = DBUtil(connect)
    a = requests.get(url).content.decode("utf-8")
    html_obj = BeautifulSoup(a, "html.parser")
    title = html_obj.title.text.strip()  # '2023年普通高校在川招生专科批录取调档线-四川省教育考试院'
    try:
        year = int(year_pattern.match(title).group(1))
    except Exception as e:
        year = -1
    try:
        score_line = score_line_pattern.match(title).group(1)
    except Exception as e:
        score_line = ""
    div_obj = html_obj.find("div", class_="news")
    img_objs = div_obj.find_all("img")
    for each_img in img_objs:
        img_url = each_img["src"]
        has_url = db.select_adjustment_score_line_urls(url, img_url)
        if has_url:
            logging.info("url,:{},img_url:{} exists!".format(url, img_url))
            continue
        else:
            majorOne = (url, img_url, province, str(year), score_line)
            sql = """INSERT INTO adjustment_score_line_urls(url, img_url, province, year, score_line) VALUES (%s,%s,%s,%s,%s)"""
            db.insert(sql, majorOne)

#记录上一张图匹配到的各字段的列下标
pre_yw_index = None
pre_sx_index = None
pre_wz_index = None
pre_lz_index = None
pre_school_code_index = None
pre_school_name_index = None
pre_category_index = None
pre_college_score_index = None
pre_remark_index = None

def get_sichuan_score(url_id, url, img_url,pre_index_dict):
    pre_index_dict["utf"]=url
    db = DBUtil(connect)
    line_id = db.select_adjustment_score_lines(url_id)
    if line_id:
        logging.info("url_id:{},url:{},img_url:{} exists!".format(url_id, url, img_url))
    else:
        logging.info("pre_index_dict:{}".format(json.dumps(pre_index_dict, ensure_ascii=False)))
        logging.info("url_id:{},url:{},img_url:{} processing!".format(url_id, url, img_url))
        dir_path, html_file_name = os.path.split(url)
        file_suffix = img_url.split(".")[-1]
        file_bytes = requests.get(dir_path+"/"+img_url).content
        fin = io.BytesIO(file_bytes)
        fin.name = "temp.{}".format(file_suffix)
        files = {'file': fin}
        ocr_param = {}
        img_result = http_utils.http_post_file(img_extract_url, ocr_param, files, timeout=300)
        img_obj = BeautifulSoup(json.loads(img_result)["data"],"html.parser")
        yw_index = None
        sx_index = None
        wz_index = None
        lz_index = None
        school_code_index = None
        school_name_index = None
        category_index = None
        college_score_index = None
        remark_index = None
        try:
            trs = img_obj.table.find_all("tr")
            tr_tds = pool_utils.supply_table(trs, "",max_table_rows=100)
            header_texts = []
            start_tr_index = 1
            if "数学" in trs[1].text.strip() and "语文" in trs[1].text.strip():
                for td_index in range(0,len(tr_tds[1])):
                    header_texts.append(tr_tds[0][td_index][1].text.strip()+tr_tds[1][td_index][1].text.strip())
                start_tr_index=2
            elif "数学" in trs[0].text.strip() and "语文" in trs[0].text.strip():
                for each_td in trs[0].find_all("td"):
                    header_texts.append(each_td.text.strip())
            else:
                logging.info("all index is None,use pre index.")
                yw_index = pre_index_dict.get("pre_yw_index", None)
                sx_index = pre_index_dict.get("pre_sx_index", None)
                wz_index = pre_index_dict.get("pre_wz_index", None)
                lz_index = pre_index_dict.get("pre_lz_index", None)
                school_code_index = pre_index_dict.get("pre_school_code_index", None)
                school_name_index = pre_index_dict.get("pre_school_name_index", None)
                category_index = pre_index_dict.get("pre_category_index", None)
                college_score_index = pre_index_dict.get("pre_college_score_index", None)
                remark_index = pre_index_dict.get("pre_remark_index", None)
            for header_index, each_header in enumerate(header_texts):
                if "语文" in each_header:
                    yw_index = header_index
                elif "数学" in each_header:
                    sx_index = header_index
                elif "文综" in each_header:
                    wz_index = header_index
                elif "理综" in each_header:
                    lz_index = header_index
                elif "院校代码" in each_header:
                    school_code_index = header_index
                elif "院校名称" in each_header:
                    school_name_index = header_index
                elif "科类名称" in each_header or "科类" in each_header:
                    category_index = header_index
                elif "总分" in each_header or "调档线" in each_header:
                    college_score_index = header_index
                elif "备注" in each_header or "考生范围" in each_header:
                    remark_index = header_index
            if category_index is None:
                category_index = pre_index_dict.get("pre_category_index",None)
                if category_index is None or category_index=="文科" or category_index == "理科":
                    for each_ele in BeautifulSoup(requests.get(url).content.decode("utf-8"), "html.parser").find("img",
                                                         src=img_url).previous_elements:
                        if "文科" in each_ele.text:
                            category_index="文科"
                            break
                        elif "理科" in each_ele.text:
                            category_index = "理科"
                            break
            pre_index_dict["pre_yw_index"] = yw_index
            pre_index_dict["pre_sx_index"] = sx_index
            pre_index_dict["pre_wz_index"] = wz_index
            pre_index_dict["pre_lz_index"] = lz_index
            pre_index_dict["pre_school_code_index"] = school_code_index
            pre_index_dict["pre_school_name_index"] = school_name_index
            pre_index_dict["pre_category_index"] = category_index
            pre_index_dict["pre_college_score_index"] = college_score_index
            pre_index_dict["pre_remark_index"] = remark_index
            logging.info("语文:{},数学:{},文综:{},理综:{},院校代码:{},院校名称:{},科类名称:{},总分:{},备注:{}".format(
                yw_index, sx_index, wz_index, lz_index,school_code_index,school_name_index,category_index,college_score_index,remark_index))
            for row_index in range(start_tr_index, len(tr_tds)):
                try:
                    school_code = tr_tds[row_index][school_code_index][1].text.strip()
                except Exception as e:
                    school_code = ""
                try:
                    school_name = tr_tds[row_index][school_name_index][1].text.strip()
                except Exception as e:
                    school_name = ""
                try:
                    category = tr_tds[row_index][category_index][1].text.strip()
                except Exception as e:
                    category = category_index
                try:
                    score = tr_tds[row_index][college_score_index][1].text.strip()
                except Exception as e:
                    score = ""
                try:
                    chinese_score = tr_tds[row_index][yw_index][1].text.strip()
                except Exception as e:
                    chinese_score = ""
                try:
                    math_score = tr_tds[row_index][sx_index][1].text.strip()
                except Exception as e:
                    math_score = ""
                try:
                    english_score = tr_tds[row_index][sx_index][1].text.strip()
                except Exception as e:
                    english_score = ""
                try:
                    wz_score = tr_tds[row_index][wz_index][1].text.strip()
                except Exception as e:
                    wz_score = ""
                try:
                    lz_score = tr_tds[row_index][lz_index][1].text.strip()
                except Exception as e:
                    lz_score = ""
                try:
                    remark = tr_tds[row_index][remark_index][1].text.strip()
                except Exception as e:
                    remark = ""
                majorOne = (
                    school_code, school_name, category, score, chinese_score, math_score,
                    english_score, wz_score, lz_score, str(url_id), remark)
                sql = """INSERT INTO adjustment_score_line(school_code, school_name, category, score, chinese_score, math_score,
                    english_score, wz_score, lz_score, url_id, remark)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                db.insert(sql, majorOne)
        except Exception as e:
            category_index = category_pattern.match(img_obj.text.strip()).group(1)
            pre_index_dict["pre_category_index"] = category_index
            logging.info("url_id:{},url:{},img_url:{} parse error!".format(url_id, url, img_url))
if __name__=="__main__":
    urls=[
        "https://www.sceea.cn/Html/202308/Newsdetail_3334.html",
        "https://www.sceea.cn/Html/202308/Newsdetail_3326.html",
        "https://www.sceea.cn/Html/202308/Newsdetail_3328.html",
        "https://www.sceea.cn/Html/202308/Newsdetail_3306.html",
        "https://www.sceea.cn/Html/202307/Newsdetail_3281.html",
        "https://www.sceea.cn/Html/202307/Newsdetail_3267.html",
        "https://www.sceea.cn/Html/202307/Newsdetail_3268.html"
    ]
    for each_url in urls:
        get_images(each_url,"四川省")
    #解析每个图片
    db = DBUtil(connect)
    urls = db.get_adjustment_score_line_urls()
    pre_index_dict = {}
    for each_url in urls:
        if "url" in pre_index_dict and pre_index_dict["url"]!=each_url[1]:
            pre_index_dict = {}
        get_sichuan_score(*each_url,pre_index_dict)
