#!/usr/bin/env python
#encoding=utf-8
import datetime
import time
import calendar
import sys

TEST = None
CHECKOUT_FLAG = False


def timestampTodateTime(timestamp, millisecond=False):
    '''
    timestamp float
    timestamp 转为 dateTime 类型, 针对 js(精度 millisecond 毫秒) 需要除以 1000
    '''
    if millisecond:
        #timestamp = (decimal.Decimal(timestamp))/1000
        timestamp = timestamp / 1000
    return datetime.datetime.fromtimestamp(timestamp)


def getCurrentTime(fmt="%Y-%m-%d %H:%M:%S"):
    '''获取当前时间 '''
    return time.strftime(fmt, time.localtime())


def add_months(dt, months):
    '''增加月,负则是减少月'''
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def getLastMonth():
    '''取上个月 仅要月份'''
    today = datetime.date.today()
    today = add_months(today, -1)
    month = str(today.month)
    return month


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


def isTest():
    '''验证是否测试模式'''
    if TEST is not None:
        return True
    args = sys.argv
    length = len(args)
    if length == 1:
        return False
    if args[length - 1] == 'test':
        return True
    else:
        return False


def setUTF8():
    reload(sys)
    sys.setdefaultencoding('utf-8')


def isTime(time_line, format="%M"):
    '''
    是否到达时间点
    >>> isTime('03')
    True
    '''
    current_time = time.strftime('%M', time.localtime())
    return current_time == time_line


def getSleepTime():
    '''
    监控间隔时间,秒
    '''
    if isTest():
        return 5
    else:
        return 60


def lowerDict(obj):
    '''
    字典key转化为小写
    >>>lowerDict({'NAME':'djoin.NET'})
    {'name':'djoin.NET'}
    '''
    lower = {}
    for k in obj:
        lower[k.lower()] = obj[k]
    return lower


def lowerDicts(objs):
    '''
    当从数据库中取出的记录,字段全是大写时非常有用
    '''
    for obj in objs:
        yield lowerDict(obj)


def disableLog():
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('suds.client').setLevel(logging.ERROR)
    logging.disable(logging.ERROR)


def getInStr(l):
    '''用来拼凑 sql 中的 in()括号内的东西,要带 ',给 string 用的'''
    string = ''
    for i, e in enumerate(l):
        if i == 0:
            string = "'" + e + "'"
        else:
            string += ",'" + e + "'"
    return string


if __name__ == '__main__':
    print getInStr(['ibgzhu', 'bigzu', 'bigzhu'])
