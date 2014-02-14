#!/usr/bin/env python
#encoding=utf-8
import os
import web
import json
import time
import pg
import utils
import decimal
import datetime
import traceback
from auth import *

from render import rendeHtml

mobile_app = web.auto_application()


class ExtendedEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            # If it's a date, convert to a string
            # Replace this with whatever your preferred date format is
            return o.strftime("%Y-%m-%d %H:%M")
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return int(o)
        # Defer to the superclass method
        return json.JSONEncoder(self, o)


class MobileIndex(mobile_app.page):
    path = "/index"

    @mobileLoginRequired
    def GET(self):
        isAjax = bool(web.input().get("ajax"))
        u_id = getUserId()

        sql = """
   select p.*,rd.f_car_type,to_char(rd.f_parking_stamp,'HH24:MI:SS'),
rd.f_car_no,s.f_name as f_street_name
from t_parking p left join t_parking_record rd on rd.f_key = p.f_key
left join t_street s on p.f_street_id = s.f_id
left join t_parking_image tpi on tpi.f_key = rd.f_key
left join t_user_parking tup on tup.f_parking_id = p.f_id
where 
tup.f_user_id = %s
order by p.f_id
                """ % u_id
        data = pg.query(sql)
        if isAjax:
            return json.dumps(data)
        else:
            return rendeHtml("mobile/index", parkings=data)


class MobileMain(mobile_app.page):
    path = "/main"

    @mobileLoginRequired
    def GET(self):
        u_id = getUserId()

#        shift_data = pg.db.query(
#            ("select s.* from t_shift s, t_user u "
#             "where s.f_id = u.f_shift_id and u.f_id = $u_id"),
#            locals())
#        shift_data = list(shift_data)[0]
        
#        now = datetime.datetime.now().time()
#        start_time = datetime.time(
#            *[int(x) for x in shift_data.f_start.split(":")])
#        end_time = datetime.time(
#            *[int(x) for x in shift_data.f_end.split(":")])

#        print now, start_time, end_time

#        if now < start_time or now > end_time:
#            parkings = []
#        else:
        parkings = self.getParkingData(u_id)

        return rendeHtml("mobile/main", parkings=parkings)

    def getParkingData(self, uid):
        
        sql = """
           select
             pr.f_id,
             pr.f_act_cost::numeric,
             pr.f_parking_code,
             pr.f_key,
             pr.f_car_no,
             (
                select
                  count(*)
                from
                  t_parking_record tpr
                where
                  tpr.f_cost::numeric > 0.00 and
                  tpr.f_cost_type = '逃逸' and
                  tpr.f_car_no = pr.f_car_no
             ) as f_escape_count,
             to_char(pr.f_parking_stamp, 'HH24:MI:SS') as f_parking_stamp
           from
             t_parking p
           left join
             t_parking_record pr on p.f_key = pr.f_key
           where
             p.f_id in (select f_parking_id from t_user_parking where f_user_id = %s) and 
             p.f_state = 1
        """ % (uid)

        return pg.query(sql)


class MobileLogin(mobile_app.page):
    path = "/login"

    def GET(self):
        account = getUserAccount()
        return rendeHtml("mobile/login", account=account)

    def POST(self):
        u = web.input().get("un", "").strip()
        p = web.input().get("pw", "").strip()

        ret = {
            "error": 0
        }

        if u and p:
            user = list(pg.db.select("t_user", where="f_account='%s'" % u, limit=1))
            if user and user[0]["f_password"] == p:
                loginUser(user[0]["f_id"], u)
                ret["u_id"] = user[0]["f_id"]
                sql = """
                    select
                    f_icon as icon
                    ,f_name as title
                    ,-1 as count
                    ,f_key as key
                    ,f_uri as url
                    from t_unit tu
                    where
                    tu.f_key like 'Mobile.%%'
                    and tu.f_type = 'Func'
                    and tu.f_id in (select f_unit_id from t_role_unit tru where tru.f_role_id in (select f_role_id from t_user_role where f_user_id = %s))
                    order by f_index desc
                """ % ret["u_id"]
                units = pg.query(sql)

                url = "/mobile/main"
                sql_user = """select * from t_user where f_id = %s""" % ret["u_id"]
                user = pg.query(sql_user)
                if user:
                    user = user[0]
                    if user.f_type == "收费人员":
                        url = "/mobile/main?u_id=" + str(ret["u_id"])
                    else:
                        url = "/mobile/queryparkingrecord_checkfilter"
                ret["units"] = units
                ret["url"] = url
            else:
                ret["error"] = 1
                ret["errorMsg"] = "用户名或密码错误!"
        else:
            ret["error"] = 1
            ret["errorMsg"] = "没有输入用户名和密码!"

        return json.dumps(ret)


class CheckIn(mobile_app.page):
    path = "/checkin"

    @mobileLoginRequired
    def GET(self):
        """
        停车登记
        """
        data = web.input()
        parking_code = data.get("parking_code", "")

        key = utils.createParkingRecordKey()
        return rendeHtml("mobile/checkin", key=key, parking_code=parking_code)

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')

        data = web.input()
        """
        保存停车登记
        """
        ret = {
            "error": 1
        }

        u_id = getUserId()
        car_no = data.get("car_no")
        car_type = data.get("car_type")
        act_cost = data.get("act_cost")
        car_state = data.get("car_state")
        parking_code = data.get("parking_code")
        key = data.get("key")

        #取当前用户信息
        user = list(pg.db.query("select * from t_user where f_id = %s" % u_id))
        if user:
            user = user[0]

        sql_escape = "select count(*) as count from t_parking_record where f_cost::numeric > 0.00 and  f_car_no = '%s' and f_cost_type = '逃逸'" % car_no
        escape_data = pg.db.query(sql_escape)[0]

        #取车位编号对应的车位ID
        parking = pg.db.query("""
                   select
                     *
                   from
                     t_parking
                   where
                     f_id in (select f_parking_id from t_user_parking where f_user_id = $u_id) and
                     f_code = $parking_code""", vars=locals())

        #车位输入错误
        if not parking:
            ret["errorMsg"] = "无效的车位, 请重新输入."
            return json.dumps(ret)
        #FIXME:如果有多个相同编号的车位杂整
        #目前这种车位是输入方式的没有办法解决
        parking = parking[0]

        #已经有车的车位
        if parking.f_state == 1:
            ret["errorMsg"] = "此车位已经停有车辆, 请重新输入车位"
            return json.dumps(ret)

        now = datetime.datetime.now()

        data = {
            "f_key": key,
            "f_car_no": car_no,
            "f_car_type": car_type,
            "f_act_cost": act_cost,
            "f_creater_id": u_id,
            "f_charger_id": u_id,
            "f_car_state": car_state,
            "f_parking_code": parking_code,
            "f_street_id": parking.f_street_id,
            "f_shift_id": user.f_shift_id,
            "f_parking_stamp": now
        }

        #先增加停车记录
        pg.db.insert("t_parking_record", **data)
        #更新车位状态
        pg.db.update("t_parking", where="f_id=%s" % parking.f_id, f_state=1, f_key=key)

        ret["error"] = 0

        template_data = {
            "date": now, "key": key, "car_no": car_no, "car_type": car_type, "now": now, "phone": user.f_phone, "parking_name": "", "act_cost": act_cost
        }

        ret["print_content"] = rendeHtml("mobile/checkin_report", **template_data)
        ret["u_id"] = u_id
        ret["car_no"] = car_no
        ret["escape_count"] = escape_data.count

        return json.dumps(ret, cls=ExtendedEncoder)


class CheckInEdit(mobile_app.page):
    """
    修改停车登记
    """
    path = "/checkinedit/(\d+)"

    @mobileLoginRequired
    def GET(self, parkingrecord_id):
        parking_record = pg.db.select("t_parking_record", where="f_id=%s" % parkingrecord_id, limit=1)[0]
        parking_record["f_act_cost"] = parking_record["f_act_cost"]
        return rendeHtml("mobile/checkin_edit", parking_record=parking_record)

    @mobileLoginRequired
    def POST(self, parkingrecord_id):
        web.header('Content-Type', 'application/json;charset=UTF-8')

        data = web.input()
        """
        保存停车登记修改
        """
        ret = {
            "error": 1
        }

        parking_record = pg.db.select("t_parking_record", where="f_id=%s" % parkingrecord_id, limit=1)[0]
        parking_record.f_car_no = data.get("car_no")
        parking_record.f_car_type = data.get("car_type")
        parking_record.f_act_cost = data.get("act_cost")
        parking_record.f_car_state = data.get("car_state")
        parking_record.f_parking_code = data.get("parking_code")

        u_id = getUserId()
        user = list(pg.db.query("select * from t_user where f_id = %s" % u_id))
        if user:
            user = user[0]

        #sql_parking_state = "select f_state from t_parking where f_code = '%s' and f_street_id = %s" % (parking_record.f_parking_code, user.f_street_id,)
        #parking_state = list(pg.db.query(sql_parking_state))
        #if parking_state:
            #parking_state = parking_state[0]

            #if parking_state.f_state == 1:
                #ret["error"] = 1
                #ret["errorMsg"] = "当前车位状态显示为已停入车辆！"
                #return json.dumps(ret, cls=ExtendedEncoder)

        pg.db.update("t_parking_record", where="f_id =%s" % parkingrecord_id, **parking_record)

        ret["error"] = 0
        template_data = {
            "date": parking_record.f_parking_stamp, "key": parking_record.f_key, "car_no": parking_record.f_car_no, "car_type": parking_record.f_car_type, "now": parking_record.f_parking_stamp, "phone": user.f_phone, "act_cost": parking_record.f_act_cost
        }

        ret["print_content"] = rendeHtml("mobile/checkin_report", **template_data)
        ret["u_id"] = u_id
        return json.dumps(ret, cls=ExtendedEncoder)


class CheckOut(mobile_app.page):
    """
    车辆结帐
    """
    path = "/checkout/(\d+)"

    @mobileLoginRequired
    def GET(self, parking_id):
        sql = """
            select
            p.f_id
            ,p.f_act_cost
            ,p.f_parking_code
            ,p.f_key
            ,p.f_car_type
            ,p.f_parking_stamp as f_parking_stamp1
            ,to_char(p.f_parking_stamp, 'HH24:MI:SS') as f_parking_stamp
            ,p.f_car_no
            ,(select f_name from t_street s where s.f_id = p.f_street_id) as f_street_name
            from t_parking_record p
            where
                p.f_id = %s
            """ % parking_id

        data = pg.query(sql)[0]

        data["f_time"] = datetime.datetime.now() - data["f_parking_stamp1"]
        data["f_cost"] = str(utils.getActualCost(data["f_time"]) if utils.getActualCost(data["f_time"]) > 0 else 0.00)
        data["f_time"] = str(data["f_time"])[0:8]

        data["f_act_cost"] = str(data["f_act_cost"])[1:-3]

        return rendeHtml("mobile/checkout", parking=data)

    @mobileLoginRequired
    def POST(self, parking_id):
        web.header('Content-Type', 'application/json;charset=UTF-8')

        checkout_data = web.input()
        """
        收费
        """
        ret = {
            "error": 1
        }

        parking_record = pg.db.select("t_parking_record", where="f_id=%s" % parking_id, limit=1)[0]

        now = datetime.datetime.now()
        u_id = getUserId()
        user = list(pg.db.query("select * from t_user where f_id = %s" % u_id))
        if user:
            user = user[0]

        data = {
            "f_cost": utils.getActualCost(now - parking_record["f_parking_stamp"]),
            "f_act_cost": checkout_data.get("act-cost", "0"),
            "f_coster_id": u_id,
            "f_cost_type": checkout_data.get("cost-type"),
            "f_leave_stamp": now
        }

        pg.db.update("t_parking_record", where="f_id=%s" % parking_id, **data)
        pg.db.update("t_parking", where="f_street_id = %s and f_code='%s'" % (parking_record.f_street_id, parking_record.f_parking_code,), f_state=0)

        template_data = dict(parking_record.items())
        template_data["f_time"] = str(now - parking_record["f_parking_stamp"])[0:8]
        template_data["f_phone"] = user.f_phone[-4:]
        template_data["f_leave_stamp"] = now
        template_data["f_act_cost"] = data["f_act_cost"]
        template_data["f_cost"] = str(data["f_cost"])[0:-2] if data["f_cost"] > 0.00 else 0

        ret["error"] = 0
        ret["print_content"] = rendeHtml("mobile/checkout_report", **template_data)
        ret["u_id"] = u_id
        return json.dumps(ret, cls=ExtendedEncoder)


class SetupPrinter(mobile_app.page):
    """
    打印机设置面页
    """
    path = "/setup_printer"

    def GET(self):
        return rendeHtml("mobile/setup_printer")


class DailyReport(mobile_app.page):
    """
    日报表
    """
    path = "/reports"

    @mobileLoginRequired
    def GET(self):
        uid = getUserId()
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        template_data = {}

        user_info_sql = """
            select
                u.f_name as user_name
                ,(select f_name from t_street ts where ts.f_id = u.f_street_id) as street_name
            from
                t_user u
            where
                u.f_id = %s
        """ % uid

        user = pg.query(user_info_sql)
        if user:
            user = user[0]

        template_data["user_id"] = uid
        template_data["today"] = today
        template_data["street_name"] = user.street_name
        template_data["coster_name"] = user.user_name
        template_data["print"] = ""

        parking_count_sql = """
            select
              sum(case when f_leave_stamp is null then 1 else 0 end) as uncost_times
              ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as cost_times
              ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as parking_range
              ,sum(f_act_cost) as act_cost
              ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as free_times
              ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as free_range
            from t_parking_record tpr
            where
            f_coster_id = %s
            and
            date(f_parking_stamp) = CURRENT_DATE
            """ % uid

        parking_count_info = pg.query(parking_count_sql)
        if parking_count_info:
            parking_count_info = parking_count_info[0]

        template_data["car_count"] = parking_count_info.cost_times
        template_data["cost_count"] = parking_count_info.act_cost
        template_data["free_car_count"] = parking_count_info.free_times
        template_data["free_car_time_count"] = parking_count_info.free_range
        template_data["stay_car"] = parking_count_info.uncost_times
        template_data["print"] = rendeHtml("mobile/dailyreport_print", **template_data)
        return rendeHtml("mobile/dailyreport", **template_data)


class GetMessageCount(mobile_app.page):
    """
    获取地磁消息通知总数
    """
    path = "/getmessagecount"

    def GET(self):
        uid = getUserId()

        sql = """
          select count(*) as count from t_message
          where
          f_is_done = 0 and
          abs(extract(epoch from now() - f_create_time)/60) < 5
          and f_street_id = (select f_street_id from t_user where f_id = %s limit 1)
        """ % uid

        msg_count = pg.query(sql)[0]
        return json.dumps(msg_count)


class Messages(mobile_app.page):
    """
    message list
    """
    path = "/messages"

    @mobileLoginRequired
    def GET(self):
        uid = getUserId()
        sql = """
          select
           *
           ,(select f_name from t_parking tp1 where tp1.f_id = tm.f_parking_id) as f_parking_name
          from
          t_message  tm
          where
          f_is_done = 0 and
          abs(extract(epoch from now() - f_create_time)/60) < 5
          and
          f_street_id = (select f_street_id from t_user where f_id = %s limit 1)
          order by f_create_time desc
        """ % uid

        msgs = pg.query(sql)

        return rendeHtml("mobile/msglist", msgs=msgs)


class MessageDone(mobile_app.page):
    """
    Done Message
    """
    path = "/messagedone/(\d+)"

    @mobileLoginRequired
    def GET(self, id):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        msgid = int(id)
        uid = getUserId()
        sql = "select * from t_message where f_id = $msgid"
        msgs = list(pg.db.query(sql, vars={"msgid": msgid}))

        if msgs:
            msgs = msgs[0]
            msgs.f_is_done = 1
            msgs.f_done_time = datetime.datetime.now()
            msgs.f_done_user_id = uid
            pg.db.update("t_message", where="f_id=%d" % msgid, **msgs)

        return  web.seeother('/messages')


class Image(mobile_app.page):
    """
    Done Message
    """
    path = "/image/(\w+)"

    @mobileLoginRequired
    def GET(self, key):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        sql = "select * from t_parking_image where f_key = $key"
        images = list(pg.db.query(sql, vars={"key": key}))
        return rendeHtml("mobile/image", images=images)


class Documents(mobile_app.page):
    """
    message list
    """
    path = "/documents"

    @mobileLoginRequired
    def GET(self):
        sql = """
          select
           *
          from
          t_document
          """

        docs = pg.query(sql)

        return rendeHtml("mobile/doclist", docs=docs)


class Document(mobile_app.page):
    """
    message list
    """
    path = "/doc/(\d+)"

    @mobileLoginRequired
    def GET(self, id):
        sql = """
          select
           *
          from
          t_document
          where f_id=%d
          """ % int(id)

        docs = pg.query(sql)

        doc = None
        if docs:
            doc = docs[0]

        return rendeHtml("mobile/doccontent", doc=doc)


class QueryParkingRecord(mobile_app.page):
    """
    收费人员停车记录查询（只限当天）
    """
    path = "/queryparkingrecord"

    def POST(self):
        input = web.input()
        parking_code = input.get("parking_code", "")
        carfirst = input.get("carfirst", "")
        carsecond = input.get("carsecond", "")
        car_no = carfirst + carsecond + " " + input.get("car_no", "")

        u_id = getUserId()
        where = ""

        if parking_code != "":
            where += " and f_parking_code='%s'" % parking_code

        if input.get("car_no") != "":
            where += " and f_car_no like '%%%s%%'" % car_no

        sql = """
                select
                    *
                    ,(case when f_leave_stamp is null then 1 else 0 end) as f_state
                    from
                    t_parking_record tpr
                    where date(f_parking_stamp) = CURRENT_DATE and f_street_id in
                    (select
                        f_street_id
                        from t_user
                        where f_id = %s
                    )
                    %s
                """ % (u_id, where,)

        data = pg.db.query(sql, vars={"car_no": car_no})
        return rendeHtml("mobile/queryparkingrecord", parkings=data)


class RePrintCheckout(mobile_app.page):
    """
    复打结帐账单
    """
    path = "/checkout_reprint/(\d+)"

    def POST(self, sid):
        sql = """
                select
                *
                ,(select f_phone from t_user tu where tu.f_id = tpr.f_coster_id) as f_phone
                ,round((case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as f_time
                from t_parking_record tpr where f_id = %s
              """ % sid

        datas = pg.query(sql)
        parking_record = {}
        if datas:
            parking_record = datas[0]

        template_data = dict(parking_record.items())
        template_data["f_time"] = str(parking_record["f_leave_stamp"] - parking_record["f_parking_stamp"])[0:8]
        template_data["f_cost"] = str(parking_record["f_cost"])[1:-3]
        template_data["f_act_cost"] = str(parking_record["f_act_cost"])[1:-3]
        template_data["f_phone"] = template_data["f_phone"][-4:]
        return rendeHtml("mobile/checkout_report", **template_data)


class QueryParkingRecordFilter(mobile_app.page):
    """
    未驶离车辆停车记录查询
    """
    path = "/queryparkingrecord_filter"

    def GET(self):
        return rendeHtml("mobile/queryparkingrecord_filter")


class QueryParkingRecordCheckFilter(mobile_app.page):
    """
    巡查人员或公司领导停车记录查询
    """
    path = "/queryparkingrecord_checkfilter"

    def GET(self):
        return rendeHtml("mobile/queryparkingrecord_checkfilter")


class QueryParkingRecord4check(mobile_app.page):
    """
    巡查或公司领导停车记录查询列表（只限当天）
    """
    path = "/queryparkingrecord4check"

    def POST(self):
        input = web.input()
        car_no = input.get("car_no", "")
        carfirst = input.get("carfirst", "")
        carsecond = input.get("carsecond", "")

        car_no = carfirst + carsecond + " " + input.get("car_no", "")
        where = ""

        if car_no != "":
            where += " and f_car_no like '%%%s%%'" % car_no

        sql = """
                select
                    *
                    ,(select f_state from t_parking tp3 where tp3.f_code = tpr.f_parking_code and tpr.f_street_id = tp3.f_street_id) as f_state
                    ,(select f_name from t_parking tp1 where tp1.f_code = tpr.f_parking_code and tpr.f_street_id = tp1.f_street_id) as f_parking_name
                    from
                    t_parking_record tpr
                    where date(f_parking_stamp) = CURRENT_DATE %s
                """ % where

        data = pg.db.query(sql)
        return rendeHtml("mobile/queryparkingrecord4check", car_no=car_no, parkings=data)


class QueryParkingFilter(mobile_app.page):
    """
    车位状态查询条件
    """
    path = "/queryparking_filter"

    def GET(self):
        sql_region = 'select f_id as "Value", f_name as "DisplayText" from t_region'
        regions = list(pg.db.query(sql_region))

        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        return rendeHtml("mobile/queryparking_filter", regions=regions, streets=streets)


class QueryParking(mobile_app.page):
    """
    车位状态查询结果
    """
    path = "/queryparking"

    def POST(self):
        input = web.input()
        street = input.get("street", "")
        region = input.get("region", "")

        where = ""
        filters = {}
        if street != "":
            where += """ and p.f_street_id = $street"""
            filters["street"] = street

        if region != "":
            where += """ and p.f_region_id = $region"""
            filters["region"] = region

        sql = """
                select
                *
                ,(select f_key from t_parking_record tpr where tpr.f_id = p.f_parking_record_id) as f_key
                ,(select f_parking_stamp from t_parking_record tpr where tpr.f_id = p.f_parking_record_id) as f_parking_stamp
                ,(select f_car_no from t_parking_record tpr where tpr.f_id = p.f_parking_record_id) as f_car_no
                from t_parking p
                where 1=1 %s
              """ % where

        data = pg.db.query(sql, vars=filters)
        return rendeHtml("mobile/queryparking", parkings=data)


class CheckRecord(mobile_app.page):
    """
    巡查人员违规记录登记（只限当天）
    """
    path = "/checkrecord"

    def GET(self):
        input = web.input()
        car_no = input.get("car_no", "")

        sql_shift = 'select f_id as "Value", f_name as "DisplayText" from t_shift'
        shifts = list(pg.db.query(sql_shift))

        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        sql_parkings = """
                    select
                        tp.f_code as "Value"
                        ,tp.f_name as "DisplayText"
                        from
                        t_parking tp
                        order by f_index desc
                """

        parkings = list(pg.db.query(sql_parkings))

        return rendeHtml("mobile/checkrecord", shifts=shifts, parkings=parkings, streets=streets, users=users, car_no=car_no)

    def POST(self):
        input = web.input()
        data = {}

        data["f_checker_id"] = getUserId()
        data["f_check_stamp"] = datetime.datetime.now()
        data["f_street_id"] = input.get("street", "")
        data["f_parking_code"] = input.get("parking_code", "")
        data["f_result"] = input.get("result", "")
        data["f_image"] = input.get("car_img", "")
        data["f_car_no"] = input.get("car_no", "")
        data["f_duty_user_id"] = input.get("costerid", "")
        data["f_region_id"] = input.get("region", "")
        data["f_shift_id"] = input.get("shift", "")

        for k, v in data.items():
            if v == '':
                data[k] = None
        pg.db.insert('t_check_record', **data)

        return web.seeother("/queryparkingrecord_checkfilter")


class QueryCheckRecordFilter(mobile_app.page):
    """
    巡查违规记录查询搜索
    """
    path = "/querycheckrecord_filter"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        return rendeHtml("mobile/querycheckrecord_filter", streets=streets, users=users)


class QueryCheckRecord(mobile_app.page):
    """
    巡查违规记录查询结果
    """
    path = "/querycheckrecord"

    def POST(self):
        input = web.input()
        street = input.get("street", "")
        costerid = input.get("costerid", "")

        where = ""
        filters = {}
        if street != "":
            where += """ and f_street_id = $street"""
            filters["street"] = street

        if costerid != "":
            where += """ and f_duty_user_id = $costerid"""
            filters["costerid"] = costerid

        sql = """
                select
                *
                ,(select f_name from t_parking tp where tp.f_street_id = tcr.f_street_id and tp.f_code = tcr.f_parking_code) as f_parking_name
                ,(select f_name from t_user tu where tu.f_id = tcr.f_duty_user_id) as f_user_name
                from t_check_record tcr where 1=1 %s
                """ % where

        data = pg.db.query(sql, vars=filters)
        return rendeHtml("mobile/querycheckrecord", records=data)


class CheckRecordImage(mobile_app.page):
    """
    Done Message
    """
    path = "/checkrecord_image/(\d+)"

    @mobileLoginRequired
    def GET(self, id):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        sql = "select * from t_check_record where f_id = $id"
        images = list(pg.db.query(sql, vars={"id": id}))
        image = ""
        if images:
            image = images[0].f_image

        return rendeHtml("mobile/image", image=image)


class GetUnits(mobile_app.page):
    """
    获取用户权限列表
    """
    path = "/getunits"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            u_id = getUserId()
            print "u_id is %s" % u_id
            sql = """
                select
                f_icon as icon
                ,f_name as title
                ,-1 as count
                ,f_key as key
                ,f_uri as url
                from t_unit tu
                where
                tu.f_key like 'Mobile.%%'
                and tu.f_type = 'Func'
                and tu.f_id in (select f_unit_id from t_role_unit tru where tru.f_role_id in (select f_role_id from t_user_role where f_user_id = %s))
                order by f_index desc
            """ % u_id
            data = pg.query(sql)

            url = "/mobile/index"
            sql_user = """select * from t_user where f_id = %s""" % u_id
            user = pg.query(sql_user)
            if user:
                user = user[0]
                if user.f_type == "收费人员":
                    url = "/mobile/index?u_id=" + u_id
                else:
                    url = "/mobile/queryparkingrecord_checkfilter"

            result = {"success": "true", "data": data, "url": url}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class TestUrl(mobile_app.page):
    """
    测试Web.py获取中文路径
    """
    path = "/test_url/(\w+)"

    def GET(self, p):
        print p
        return p


class Test(mobile_app.page):
    """
    测试Web.py获取中文路径
    """
    path = "/test"

    def GET(self):
        return rendeHtml("mobile/test")


class CheckoutQuick(mobile_app.page):
    """
    快速结帐
    """
    path = "/checkout_quick/(\d+)"

    def POST(self, parking_id):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        ret = {
            "error": 1
        }

        try:
            parking_record = pg.db.select("t_parking_record", where="f_id=%s" % parking_id, limit=1)[0]

            now = datetime.datetime.now()
            u_id = getUserId()
            user = list(pg.db.query("select * from t_user where f_id = %s" % u_id))
            if user:
                user = user[0]

            data = {
                "f_cost": utils.getActualCost(now - parking_record["f_parking_stamp"]),
                "f_act_cost": utils.getActualCost(now - parking_record["f_parking_stamp"]),
                "f_coster_id": u_id,
                "f_cost_type": "正常缴费",
                "f_leave_stamp": now
            }

            pg.db.update("t_parking_record", where="f_id=%s" % parking["f_parking_record_id"], **data)

            template_data["f_time"] = str(now - parking_record["f_parking_stamp"])[0:8]
            template_data["f_user_name"] = user.f_name

            ret["error"] = 0
            ret["print_content"] = rendeHtml("mobile/checkout_report", **template_data)
            ret["u_id"] = u_id
            return ret
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            ret["error"] = 1
            ret["message"] = msg
            return ret


class UploadImage(mobile_app.page):
    """
    上传停车登记拍照图片文件
    """
    path = "/uploadimage"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            key = input.get("key", "")
            img_data = input.get("img_data", "")

            now = datetime.datetime.now()
            data = {
                "f_key": key,
                "f_image": img_data,
                "f_create_time": now
            }

            pg.db.insert("t_parking_image", **data)

            result = {"success": "true"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '图片上传失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UploadImageFile(mobile_app.page):
    path = "/uploadimagefile"
    ext_arr = {
        'image': ['jpg', 'gif', 'png', 'tif', 'bmp'],
        'flash': ['swf', 'flv'],
        'media': ['swf', 'flv', 'mp3', 'wav', 'wma', 'wmv', 'mid', 'avi', 'mpg', 'asf', 'rm', 'rmvb'],
        'file': ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'htm', 'html', 'txt', 'zip', 'rar', 'gz', 'bz2'],
    }

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            x = web.input(imgFile={})
            jerror = lambda msg: json.dumps({'success': 'false', 'message': msg})

            if 'imgFile' not in x:
                return jerror('请选择文件!')

            filepath = x.imgFile.filename.replace('\\', '/')  # 客户端为windows时注意
            filename = filepath.split('/')[-1]  # 获取文件名
            ext = filename.split('.', 1)[1]  # 获取后缀

            if ext not in self.ext_arr["image"]:
                return jerror('请选择正确的文件类型!')

            homedir = os.getcwd()
            if "intelligent_parking" not in homedir:
                homedir += "/intelligent_parking"

            filedir = '%s/static/uploads' % homedir  # 要上传的路径
            now = datetime.datetime.now()
            t = "%d%d%d%d%d%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)  # 以时间作为文件名
            filename = t + '.' + ext

            fout = open(filedir + '/' + filename, 'wb')
            fout.write(x.imgFile.file.read())
            fout.close()

            input = web.input()
            key = input.get("key", "")
            now = datetime.datetime.now()
            data = {
                "f_key": key,
                "f_image": "/static/uploads/%s" % filename,
                "f_create_time": now
            }

            pg.db.insert("t_parking_image", **data)

            result = {"success": "true", "url": data["f_image"]}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '图片上传失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class QueryDetails(mobile_app.page):
    """
    收费人员日报明细（只限当天所有停车记录）
    """
    path = "/details"

    def GET(self):
        input = web.input()
        coster_id = input.get("coster_id", "")

        sql = """
                select
                    *
                    ,(case when f_leave_stamp is null then 1 else 0 end) as f_state
                    from
                    t_parking_record tpr
                    where date(f_parking_stamp) = CURRENT_DATE
                    and
                    ((f_creater_id = %s and f_leave_stamp is null) or f_coster_id = %s)
                """ % (coster_id, coster_id,)

        data = pg.db.query(sql)
        return rendeHtml("mobile/details", parkings=data)


class DeleteParkingRecord(mobile_app.page):
    """
    删除停车记录
    """
    path = "/deleteparkingrecord"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            id = input.get("id", "")
            pg.db.delete("t_parking_record", where="f_id=%s" % id)
            result = {"success": "true"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '删除停车记录失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class QueryStreetCount(mobile_app.page):
    """
    路段统计列表
    """
    path = "/querystreetcount"

    def GET(self):
        sql = """
            select
              f_street_id
              ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as f_street_name
              ,sum(case when f_leave_stamp is null then 1 else 0 end) as uncost_times
              ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as cost_times
              ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as parking_range
              ,sum(f_act_cost) as act_cost
              ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as free_times
              ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as free_range
            from t_parking_record tpr
            where
            date(f_parking_stamp) = CURRENT_DATE
            group by tpr.f_street_id
            """

        data = pg.query(sql)
        return rendeHtml("mobile/querystreetcount", result=data)


class QueryCosterCount(mobile_app.page):
    """
    根据路段，统计该路段下所有收费人员当天收费统计列表
    """
    path = "/querycostercount/(\d+)"

    def GET(self, street_id):
        sql = """
            select
              f_coster_id
              ,(select f_name from t_user tu where tu.f_id = tpr.f_coster_id) as f_coster_name
              ,sum(case when f_leave_stamp is null then 1 else 0 end) as uncost_times
              ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as cost_times
              ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as parking_range
              ,sum(f_act_cost) as act_cost
              ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as free_times
              ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as free_range
            from t_parking_record tpr
            where
            date(f_parking_stamp) = CURRENT_DATE
            and f_street_id = %s
            and f_coster_id is not null
            group by tpr.f_coster_id
            """ % street_id

        data = pg.query(sql)
        return rendeHtml("mobile/querycostercount", result=data)


class DailyShift(mobile_app.page):
    """
    交班日报表
    """
    path = "/shiftreports"

    @mobileLoginRequired
    def GET(self):
        uid = getUserId()
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        template_data = {}

        user_info_sql = """
            select
                u.f_name as user_name
                ,(select f_name from t_street ts where ts.f_id = u.f_street_id) as street_name
            from
                t_user u
            where
                u.f_id = %s
        """ % uid

        user = pg.query(user_info_sql)
        if user:
            user = user[0]

        template_data["today"] = today
        template_data["street_name"] = user.street_name
        template_data["coster_name"] = user.user_name
        template_data["print"] = ""

        parking_count_sql = """
            select
              count(p.f_state) as uncost_times,
              sum(pr.f_act_cost) as act_cost
            from
              t_parking p
            left join
              t_parking_record pr on pr.f_key = p.f_key
            where
              p.f_id in (select f_parking_id from t_user_parking where f_user_id = %s) and
              p.f_state = 1
            """ % uid

        parking_count_info = pg.query(parking_count_sql)
        if parking_count_info:
            parking_count_info = parking_count_info[0]

        template_data["act_cost"] = parking_count_info.act_cost
        template_data["stay_car"] = parking_count_info.uncost_times
        template_data["print"] = rendeHtml("mobile/dailyshift_print", **template_data)
        return rendeHtml("mobile/dailyshift", **template_data)

    def POST(self):
        try:
            uid = getUserId()

            # 自动生成日报统计表
            sql = """insert into t_reports
            (f_id, f_coster_id,f_street_id, f_report_day,f_group_leader_id,f_confirm_day,f_cost_times,f_cost, f_act_cost, f_free_times,f_escape_times,f_is_confirm)
            select
              nextval('t_reports_f_id_seq'::regclass) as f_id
              ,f_coster_id
              ,f_street_id
              ,current_date as f_report_day
              ,null as f_group_leader_id
              ,null as f_confirm_day
              ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as f_cost_times
              ,sum(f_cost) as f_cost
              ,sum(f_act_cost::numeric) as f_act_cost
              ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as f_free_times
              ,sum(case when f_cost_type = '逃逸' then 1 else 0 end) as f_escape_times
              ,0 as f_is_confirm
            from t_parking_record tpr
            where
            date(f_parking_stamp) = CURRENT_DATE
            and f_coster_id = %s
            group by f_coster_id, f_street_id
            """ % uid
            pg.db.query(sql)
            public.CHECKOUT_FLAG = False

            result = {"success": "true"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '生成日报结帐单失败，详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class QueryShiftDetails(mobile_app.page):
    """
    收费人员交班未驶离车辆明细（只限当天停车记录）
    """
    path = "/shiftdetails"

    def GET(self):
        u_id = getUserId()
        sql = """
                select
                    *
                    ,(case when f_leave_stamp is null then 1 else 0 end) as f_state
                    from
                    t_parking_record tpr
                    where date(f_parking_stamp) = CURRENT_DATE
                    and
                    f_creater_id = %s and f_leave_stamp is null
                """ % u_id

        data = pg.db.query(sql)
        return rendeHtml("mobile/shiftdetails", parkings=data)


class CheckOutEscape(mobile_app.page):
    """
    逃逸记录结帐管理
    """
    path = "/checkoutescape"

    def GET(self):
        input = web.input()
        car_no = input.get("car_no", "")

        sql = """
                select
                    *
                    ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id ) as f_street_name
                     ,round(abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60)::numeric,0) || '分钟' as f_range_stamp
                    from
                    t_parking_record tpr
                    where
                    f_cost_type = '逃逸'
                    and
                    f_car_no= '%s'
                    and
                    f_cost::numeric > 0.00
                """ % car_no

        data = pg.db.query(sql)
        return rendeHtml("mobile/checkout_escape", parkings=data)

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            u_id = getUserId()
            input = web.input()
            ids = input.get("ids", "")

            user = list(pg.db.query("select * from t_user where f_id = %s" % u_id))
            if user:
                user = user[0]

            print_content = ""
            for id in ids.split(','):
                record = pg.db.select("t_parking_record", where="f_id=%s" % id)[0]
                pg.db.update("t_parking_record", where="f_id=%s" % id, f_cost_type="正常缴费", f_coster_id=u_id, f_act_cost=record.f_cost)

                template_data = dict(record.items())
                template_data["f_time"] = str(record.f_leave_stamp - record.f_parking_stamp)[0:8]
                template_data["f_phone"] = user.f_phone[-4:]
                template_data["f_cost"] = str(record.f_cost)[1:-3]
                template_data["f_act_cost"] = str(record.f_act_cost)

                print_content += rendeHtml("mobile/checkout_report", **template_data)
                print_content += "\r\n"
                print_content += "\r\n"

            result = {"success": "true", "print_content": print_content}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class QueryCosters(mobile_app.page):
    """
    收费人员列表
    """
    path = "/costers"

    def GET(self):
        u_id = getUserId()
        sql = """
                select
                    *
                    ,(select f_name from t_shift ts where ts.f_id = tu.f_shift_id) as f_shift_name
                    ,(select count(*) from t_reports tr where tr.f_coster_id = tu.f_id and f_is_confirm = 0) as f_unconfirm
                    from
                    t_user tu
                    where f_street_id = (select f_street_id from t_user tu1 where tu1.f_id = %s)
                """ % (u_id,)

        costers = pg.db.query(sql)
        return rendeHtml("mobile/costers", costers=costers)


class CosterReports(mobile_app.page):
    """
    收费人员日报列表
    """
    path = "/coster_reports"

    def GET(self):
        input = web.input()
        coster_id = input.get("coster_id", "")

        sql = """
                select
                    *
                    ,(select f_name from t_user tu where tu.f_id = tr.f_coster_id ) as f_coster_name
                    from
                    t_reports tr
                    where
                    f_coster_id = $coster_id
                    and f_is_confirm = 0
                """

        data = pg.db.query(sql, vars={"coster_id": coster_id})
        return rendeHtml("mobile/reports", reports=data)

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            u_id = getUserId()
            input = web.input()
            ids = input.get("ids", "")

            for id in ids.split(','):
                pg.db.update("t_reports", where="f_id=%s" % id, f_group_leader_id=u_id, f_is_confirm=1, f_confirm_day=str(datetime.date.today()))

            result = {"success": "true"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': "false", 'message': '确认日报结帐失败，详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


if __name__ == '__main__':
    pass