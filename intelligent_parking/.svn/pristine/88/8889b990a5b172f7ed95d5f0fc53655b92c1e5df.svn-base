#coding=utf-8

from datetime import datetime


def createParkingRecordKey():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S") + str(now.microsecond).rjust(6, "0")


def getActualCost(timedelta, free_minutes=20, fee=3.00, rate_time=15):
    """
    计算停车费用

    Arguments:
    - `timedelta`:时长, timedelta对象
    - `free_minutes`: 免费多长时间, 单位是分钟
    - `fee`: 每小时费用
    - `rate_time`: 从第二个小时开始, 大于这个值才按一个小时计费
    """

    total_seconds = timedelta.total_seconds()

    #转换为秒
    free_minutes = free_minutes * 60
    hour = 3600

    #免费时间内不收费
    if total_seconds <= free_minutes:
        return 0

    if total_seconds <= hour:
        return fee

    cast = total_seconds // hour * fee
    mod = total_seconds % hour

    if mod != 0 and mod > rate_time * 60:
        cast += fee

    return cast


if __name__ == '__main__':
    print getActualCost(datetime.now() - datetime(2013, 11, 12, 8, 18))
