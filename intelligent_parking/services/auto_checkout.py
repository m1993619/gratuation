#!/usr/bin/env python
#encoding=utf-8
import sys
import os
path = os.getcwd()

# 默认工程路径
if "intelligent_parking" not in path and "services" not in path:
    path += "/intelligent_parking"

sys.path.append(path)
sys.path.append("..")


# 默认服务路径
if "services" not in path:
    path += "/services"


import datetime
import pg
import time
import utils
import traceback


def auto_checkout():
    t = time.strftime('%Y%m', time.localtime(time.time()))
    h = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # self.request is the TCP socket connected to the client
    file_object = open(path + '/auto_checkout_log%s.txt' % t, 'a+')

    records = pg.db.select("t_parking_record", where='f_leave_stamp is null')

    if records:
        for r in records:
            cost = utils.getActualCost(datetime.datetime.strptime(r.f_parking_stamp.strftime("%Y-%m-%d 22:00:00"), '%Y-%m-%d %H:%M:%S') - r.f_parking_stamp)

            data = {
                "f_leave_stamp": datetime.datetime.strptime(r.f_parking_stamp.strftime("%Y-%m-%d 22:00:00"), '%Y-%m-%d %H:%M:%S'), "f_cost": cost, "f_act_cost": cost, "f_coster_id": r.f_creater_id, "f_cost_type": '逃逸'
            }

            # 自动结帐
            pg.db.update("t_parking_record", where='f_id = %s' % r.f_id, **data)

        # 自动生成日报统计
        sql = """
            insert into t_reports
                (f_coster_id,f_street_id, f_report_day,f_group_leader_id,f_confirm_day,f_cost_times,f_cost, f_act_cost, f_free_times,f_escape_times,f_is_confirm)
            select
                bbb.*
            from
                (
                select
                aaa.*
                ,(case when
                    (select count(*) from t_reports tr
                    where tr.f_coster_id = aaa.f_coster_id and tr.f_report_day = aaa.f_report_day) > 0
                    then 1
                    else 0
                    end) as f_is_confirm
                from
                    (select
                    f_coster_id
                    ,f_street_id
                    ,date(f_leave_stamp) as f_report_day
                    ,-1 as f_group_leader_id
                    ,current_date as f_confirm_day
                    ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as f_cost_times
                    ,sum(f_cost) as f_cost
                    ,sum(f_act_cost::numeric) as f_act_cost
                    ,sum(case when f_cost_type = '免费' then 1 else 0 end) as f_free_times
                    ,sum(case when f_cost_type = '逃逸' then 1 else 0 end) as f_escape_times
                    from t_parking_record tpr
                    where f_leave_stamp is not null
                    group by f_coster_id, f_street_id, date(f_leave_stamp)
                ) aaa
            ) bbb
            where bbb.f_is_confirm = 0
        """
        pg.db.query(sql)
        file_object.writelines("auto_checkout is success:%s" % h)

    file_object.close()


if __name__ == '__main__':

    # 自动结帐标识: 非管理时段，且标识为True，则进行自动结帐，否则跳过
    CHECKOUT_FLAG = False

    while True:
        now = datetime.datetime.now()
        try:
            # 非收费管理时段
            if now.hour >= 23:
                if CHECKOUT_FLAG:
                    auto_checkout()
                    CHECKOUT_FLAG = False
            else:
                CHECKOUT_FLAG = True
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()

            t = time.strftime('%Y%m%d', time.localtime(time.time()))
            h = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            file_object = open(path + '/auto_checkout_errors_log%s.txt' % t, 'a+')
            file_object.writelines("[%s]自动结帐失败，详细信息: %s, " % (h, msg,))
            file_object.close()
        finally:
            time.sleep(300)  # 休眠5分钟
