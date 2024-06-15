# mysql驱动连接
import logging
import traceback
import pymysql

from SpiderForCollege.logs.Logging import load_my_logging_cfg


class DBUtil(object):
    load_my_logging_cfg()
    def __init__(self,connect):
        self.connect=connect

    def insert(self, sql, data):
        try:
            try:
                # logging.info('成功连接！！！')
                self.cursor = self.connect.cursor()
                # 执行 sql 语句
                self.cursor.execute(sql, data)
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                # print('提交完毕')
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')
        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')
    def delete(self, sql):
        try:
            # logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            # 执行 sql 语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.cursor.close()
            self.connect.commit()
            # print('提交完毕')
        except:
            logging.error(traceback.format_exc())
            # 如果发生错误则进行回滚
            self.connect.rollback()
            print('\n Some Error happend ! \n')

    def select(self,name):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                collegeId =self.cursor.execute('SELECT * FROM college WHERE name ="'+name+'"')
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return collegeId
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')
    def select_score_by_city(self,city):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                scoreId =self.cursor.execute('SELECT * FROM score WHERE city ="'+city+'"')
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return scoreId
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_major_by_province_page(self, province, page):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                scoreId =self.cursor.execute('SELECT id FROM major_score WHERE province ="'+province+'" and page='+str(page))
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return scoreId
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_major_urls(self):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                major_urls =self.cursor.execute('select DISTINCT major_url from major_score')
                major_urls = [i for i in self.cursor]
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return major_urls
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')
    def select_avg_score_urls(self, page, page_num):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                avg_score_urls =self.cursor.execute('select major_score_info_url from major_score_urls order by id limit '+str((page-1)*page_num)+','+str(page*page_num))
                avg_score_urls = [i for i in self.cursor]
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return avg_score_urls
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')
    def select_avg_score_url_num(self):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                num =self.cursor.execute('select count(*) from major_score_urls ')
                num = [i for i in self.cursor]
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return num
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_major(self, major_url):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                major_url_id =self.cursor.execute('select  id from major where major_url="'+major_url+'"')
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return major_url_id
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_major_score_info(self, major_score_info_url):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                major_score_info_id =self.cursor.execute('select  id from major_score_info where major_score_info_url="'+major_score_info_url+'"')
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return major_score_info_id
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_adjustment_score_line_urls(self, url, img_url):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                urlId =self.cursor.execute('SELECT id FROM adjustment_score_line_urls WHERE url ="'+url+'" and img_url="'+str(img_url)+'"')
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return urlId
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')
    def get_adjustment_score_line_urls(self):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                urls = self.cursor.execute('SELECT id, url,img_url FROM adjustment_score_line_urls order by id')
                urls = [i for i in self.cursor]
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return urls
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')

    def select_adjustment_score_lines(self, url_id):
        try:
            #logging.info('成功连接！！！')
            self.cursor = self.connect.cursor()
            try:
                # 执行 sql 语句
                line_id =self.cursor.execute('SELECT id FROM adjustment_score_line WHERE url_id ='+str(url_id))
                # 提交到数据库执行
                self.cursor.close()
                self.connect.commit()
                return line_id
            except:
                logging.error(traceback.format_exc())
                # 如果发生错误则进行回滚
                self.connect.rollback()
                print('\n Some Error happend ! \n')

        except:
            logging.error(traceback.format_exc())
            logging.error('连接失败！！！')



if __name__ == '__main__':
    db = DBUtil()
    if db.select('111')>0:
        print('存在相同的值')
    else:
        print('不存在')


