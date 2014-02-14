#!/usr/bin/env python
#encoding=utf-8
import web
import datetime
import calendar
import psycopg2
import public
import traceback

web.config.debug = False
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = None


def connect(test_db=False):
    global db
    if public.isTest():
        db = web.database(port=5432, host='127.0.0.1', dbn='postgres', db='parking', user='parking', pw='parking')
    else:
        db = web.database(port=5432, host='10.1.1.100', dbn='postgres', db='parking', user='parking', pw='parking)()#')

    try:
        db.set_client_encoding('UTF8')
    except (AttributeError):
        db.query("set client_encoding to 'UTF-8'")

connect()


def query(sql):
    '''重载 query,返回 list,否则是一个 IterBetter'''
    return list(db.query(sql))


def add_months(dt, months):
    '''增加月,负则是减少月'''
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def getYearMonth(months=None):
    '''取当年当月
       可以取上月,返回 str
    '''
    today = datetime.date.today()
    if months is not None:
        today = add_months(today, months)
    year = str(today.year)
    month = str(today.month)
    if len(month) == 1:
        year_month = year + '0' + month
    else:
        year_month = year + month
    return year_month


def his(table_name, **kwargs):
    '''插入历史表,当月表不存在则创建'''
    year_month = getYearMonth()
    all_table_name = table_name + "_all"
    his_table_name = table_name + '_his_' + year_month
    try:
        if 'f_id' in kwargs:
            kwargs.pop('f_id')

        if kwargs["f_leave_stamp"] is None:
            db.insert(his_table_name, **kwargs)
        else:
            records = list(db.query("select * from %s where f_street_id=%s and f_parking_code='%s' and f_parking_stamp='%s'" %
                                    (his_table_name, kwargs["f_street_id"], kwargs["f_parking_code"], kwargs["f_parking_stamp"],)))
            if records:
                db.update(his_table_name, where="f_id=%s" % records[0].f_id, **kwargs)
    except psycopg2.ProgrammingError:
        msg = traceback.print_exc()
        print msg

        sql = ' CREATE TABLE %s()INHERITS (%s)' % (his_table_name, all_table_name)
        db.query(sql)
        #sms.sendDeveloperWarningSms('创建历史表 %s' % his_table_name)
        his(table_name, **kwargs)
    except Exception:
        # 输出错误信息
        msg = traceback.print_exc()
        print msg


def createParkingData():
    '''
    批量生成车位数据
    '''
    sql = "select * from t_street where f_id != 1"
    streets = db.query(sql)
    print streets

    for s in streets:
        count = 1
        while count <= s.f_total:
            data = {
                "f_code": str(count), "f_name": s.f_name + str(count) + "号车位", "f_street_id": s.f_id, "f_type": "普通车位", "f_remark": "", "f_state": 0, "f_region_id": -1, "f_is_free": 0, "f_is_private": 0, "f_has_device": 0, "f_index": s.f_total - count, "f_key": ""
            }
            db.insert("t_parking", **data)
            count += 1
    print "success!"


def createDevice():
    '''
    批量生成地磁设备数据
    '''
    sql = "select * from t_street where f_id = 3"
    streets = db.query(sql)
    print streets

    for s in streets:
        count = 1
        while count <= s.f_total:
            data = {
                "f_name": "地磁检测器%02d" % count, "f_code": '%02d' % count, "f_street_id": 3, "f_type": "地磁检测器", "f_parking_code": str(count)
            }
            db.insert("t_device", **data)
            count += 1
    print "success!"


if __name__ == '__main__':
    #while True:
        #entries = db.query('select * from vc_detail')
        #print list(entries)
    #createParkingData()
    #createDevice()
    pass
