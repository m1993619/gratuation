#!/usr/bin/env python
#encoding=utf-8
import render
import web
import json
import datetime
import decimal
import pg
import traceback
import time
import os
import pyExcelerator
import StringIO
from auth import *

pc_app = web.auto_application()
render.addGlobalVar(cache=True)


def mustLogin():
    try:
        return isLogin()
    except Exception:
        print 'web.seeother'
        raise web.seeother('/pc/login')


def isLogin():
    session = web.ctx.session
    if session and session.user:
        return session.user
    else:
        raise Exception('登录信息失效,请退出重登录')


def getjTablePageRow(datas, start, limit):
    #开始序号
    start = int(start)
    #每页显示几条记录
    limit = int(limit) + start

    json_data = {'Result': "OK", 'Records': datas[start:limit], 'TotalRecordCount': len(datas)}
    return json.dumps(json_data, cls=ExtendedEncoder)


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


class PCLogin(pc_app.page):
    path = "/login"

    def GET(self):
        return render.rendeHtml("pc/login")


class PCIndex(pc_app.page):
    path = "/index"

    def GET(self):
        return render.rendeHtml("pc/index")


class PCMain(pc_app.page):
    path = "/main"

    def GET(self):
        web.header('Content-Type', 'text/html; charset=UTF-8')
        user = mustLogin()
        #sql_units = "select * from t_unit where f_key like 'PC.%%' order by f_index desc"

        sql = """
            select * from t_unit
            where f_id in (
                select f_unit_id from t_role_unit where f_role_id in (
                    select f_role_id from t_user_role where f_user_id = $userid
                )
            )
            order by f_index desc
        """
        units = list(pg.db.query(sql, vars={"userid": user.f_id}))

        models = [u for u in units if (u.f_type == u"Model" and "PC" in u.f_key)]

        for m in models:
            m.funcs = [f for f in units if f.f_type == "Func" and f.f_parent_id == m.f_id]

        return render.rendeHtml("pc/main", models=models, user=user)


class PCStreet(pc_app.page):
    path = "/street"

    def GET(self):
        return render.rendeHtml("pc/street")


class PCParking(pc_app.page):
    path = "/parking"

    def GET(self):
        sql_street = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))

          

        sql_shift = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_shift"""
        shifts = list(pg.db.query(sql_shift))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/parking", streets=json.dumps(streets),     shifts=json.dumps(shifts), users=json.dumps(users))


class PCRegion(pc_app.page):
    path = "/region"

    def GET(self):
        sql_street = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))

        return render.rendeHtml("pc/region", streets=json.dumps(streets))


class PCShift(pc_app.page):
    path = "/shift"

    def GET(self):
        sql_street = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))

          

        sql_users = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_users))

        return render.rendeHtml("pc/shift", streets=json.dumps(streets),     users=json.dumps(users))


class PCUser(pc_app.page):
    path = "/user"

    def GET(self):
        sql_street = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))

        sql_shift = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_shift"""
        shifts = list(pg.db.query(sql_shift))

          
        return render.rendeHtml("pc/user", streets=json.dumps(streets), shifts=json.dumps(shifts)   )


class PCRole(pc_app.page):
    path = "/role"

    def GET(self):
        return render.rendeHtml("pc/role")


class PCUnit(pc_app.page):
    path = "/unit"

    def GET(self):
        sql_units = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_unit where f_type != 'Func'"""
        models = list(pg.db.query(sql_units))
        return render.rendeHtml("pc/unit", models=json.dumps(models))


class PCCodeData(pc_app.page):
    path = "/codedata"

    def GET(self):
        sql_datas = """select f_value as "Value", f_code as "DisplayText" from t_code_data where f_category='System.CodeData'"""
        datas = list(pg.db.query(sql_datas))
        return render.rendeHtml("pc/codedata", datas=json.dumps(datas))


class PCCodeMan(pc_app.page):
    path = "/codeman"

    def GET(self):
        return render.rendeHtml("pc/codeman")


class PCLog(pc_app.page):
    path = "/log"

    def GET(self):
        sql_users = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_users))

        return render.rendeHtml("pc/log", users=json.dumps(users))


class PCParkingRecord(pc_app.page):
    path = "/parkingrecord"

    def GET(self):
        sql_streets = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_streets))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/parkingrecord", streets=json.dumps(streets), users=json.dumps(users))


class PCEscapeRecord(pc_app.page):
    path = "/escaperecord"

    def GET(self):
        sql_shift = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_shift"""
        shifts = list(pg.db.query(sql_shift))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/escaperecord", shifts=json.dumps(shifts), users=json.dumps(users))


class PCParkingCount(pc_app.page):
    """
    收费总额统计
    """
    path = "/parkingcount"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return render.rendeHtml("pc/parkingcount", now=now, streets_json=json.dumps(streets), streets=streets, users_json=json.dumps(users), users=users)


class PCParkingTypeCount(pc_app.page):
    """
    收费类型统计
    """
    path = "/parkingtypecount"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return render.rendeHtml("pc/parkingtypecount", now=now, streets_json=json.dumps(streets), streets=streets, users_json=json.dumps(users), users=users)


class PCParkingDayCount(pc_app.page):
    """
    收费日报统计
    """
    path = "/parkingdaycount"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return render.rendeHtml("pc/parkingdaycount", now=now, streets_json=json.dumps(streets), streets=streets, users_json=json.dumps(users), users=users)


class PCParkingDetailsCount(pc_app.page):
    """
    收费流水明细
    """
    path = "/parkingdetailscount"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        sql_shift = 'select f_id as "Value",f_name as "DisplayText" from t_shift'
        shifts = list(pg.db.query(sql_shift))

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return render.rendeHtml("pc/parkingdetailscount", now=now, streets=streets, users=users, shifts=shifts)


class PCReports(pc_app.page):
    """
    日报结帐确认查询
    """
    path = "/reports"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_user = 'select f_id as "Value",f_name as "DisplayText" from t_user'
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/reports", streets=json.dumps(streets), streets_nojson=streets, users=json.dumps(users), users_nojson=users)


class PCCheckRecord(pc_app.page):
    path = "/checkrecord"

    def GET(self):
        sql_shift = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_shift"""
        shifts = list(pg.db.query(sql_shift))

        sql_region = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_region"""
        regions = list(pg.db.query(sql_region))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/checkrecord", shifts=json.dumps(shifts),     users=json.dumps(users))


class PCMessage(pc_app.page):
    path = "/message"

    def GET(self):
        sql_street = 'select f_id as "Value", f_name as "DisplayText" from t_street'
        streets = list(pg.db.query(sql_street))

        sql_device = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_device"""
        devices = list(pg.db.query(sql_device))

        sql_parking = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_parking"""
        parkings = list(pg.db.query(sql_parking))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/message", streets=json.dumps(streets), devices=json.dumps(devices), parkings=json.dumps(parkings), users=json.dumps(users))


class PCMonitorRecord(pc_app.page):
    path = "/monitorrecord"

    def GET(self):
        sql_device = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_device"""
        devices = list(pg.db.query(sql_device))

        sql_parking = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_parking"""
        parkings = list(pg.db.query(sql_parking))

        return render.rendeHtml("pc/monitorrecord", devices=json.dumps(devices), parkings=json.dumps(parkings))


class PCMonitorRecordAll(pc_app.page):
    path = "/monitorrecordall"

    def GET(self):
        sql_device = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_device"""
        devices = list(pg.db.query(sql_device))

        sql_parking = """select f_id as "Value", f_name as "DisplayText" from t_parking where f_id in (select f_parking_id from t_device) order by f_id"""
        parkings = list(pg.db.query(sql_parking))

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        return render.rendeHtml("pc/monitorrecordall", now=now, devices=json.dumps(devices), parkings=parkings, parkings_json=json.dumps(parkings))


class ExportMonitorRecordAll(pc_app.page):
    """
    地磁监控查询导出
    """
    
    path = "/exportmonitorrecordall"
    
    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        data = web.input()
        now = datetime.datetime.now()

        data["start_date"] = data.get("start_date") or str(now.date())
        data["end_date"] = data.get("end_date") or str(now.date())
        data["start_time"] = data.get("start_time") or "00:00"
        data["end_time"] = data.get("end_time") or "23:59"

        parking = data.get("parking")

        sql = """
            SELECT
                m.*, d.f_name as f_device_name, p.f_name as f_parking_name
            FROM
                t_monitor_record_all m,
                t_device d,
                t_parking p
            WHERE
                m.f_parking_stamp between $start_time and $end_time and
                d.f_id = m.f_device_id and
                p.f_id = m.f_parking_id
        """

        if parking:
            sql += " and f_parking_id = $parking"

        sql += " order by f_id desc, f_stamp desc"

        param = {
            "start_time": data["start_date"] + \
                " " + data["start_time"],
            "end_time": data["end_date"] + " " + data["end_time"],
            "parking": parking
        }

        result = pg.db.query(sql, vars=param)

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'地磁监控状态')
        title = (u"序号", u"设备数据", u"车位", u"设备",
                 u"停入时间", u"离开时间", u"停车时长(分钟)", u"车位状态")
        for idx, t in enumerate(title):
            ws.write(0, idx, t)

        for idx, r in enumerate(result):
            ws.write(idx + 1, 0, r.f_id)
            ws.write(idx + 1, 1, r.f_data.strip())
            ws.write(idx + 1, 2, r.f_parking_name)
            ws.write(idx + 1, 3, r.f_device_name)
            parking_stamp = u""
            if r.f_parking_stamp:
                parking_stamp = r.f_parking_stamp.strftime(
                    "%Y-%m-%d %H:%M")
            ws.write(idx + 1, 4, parking_stamp)
            parking_minutes = 0
            leave_stamp = u""
            if r.f_leave_stamp:
                leave_stamp = r.f_leave_stamp.strftime(
                    "%Y-%m-%d %H:%M")
                parking_minutes = r.f_leave_stamp - r.f_parking_stamp
                parking_minutes = parking_minutes.total_seconds() / 60
                parking_minutes = int(round(parking_minutes, 1))
            
            ws.write(idx + 1, 5, leave_stamp)
            ws.write(idx + 1, 6, parking_minutes)
            ws.write(idx + 1, 7, u"有车" if r.f_state else u"没车")

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()

    

class PCDevice(pc_app.page):
    path = "/device"

    def GET(self):
        sql_street = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))

        sql_device = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_device"""
        devices = list(pg.db.query(sql_device))

        sql_parking = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_parking order by "DisplayText" """
        parkings = list(pg.db.query(sql_parking))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        sql_devicetype = """select null as "Value", '[空]' as "DisplayText" union all select f_value as "Value", f_code as "DisplayText" from t_code_data where f_category='DeviceType'"""
        devicetypes = list(pg.db.query(sql_devicetype))

        return render.rendeHtml("pc/device", streets=json.dumps(streets), devices=json.dumps(devices), parkings=json.dumps(parkings), users=json.dumps(users), devicetypes=json.dumps(devicetypes))


class PCCommand(pc_app.page):
    path = "/command"

    def GET(self):
        sql_device = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value", f_name as "DisplayText" from t_device"""
        devices = list(pg.db.query(sql_device))

        sql_user = """select null as "Value", '[空]' as "DisplayText" union all select f_id as "Value",f_name as "DisplayText" from t_user"""
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/command", devices=json.dumps(devices), users=json.dumps(users))


class PCDocument(pc_app.page):
    path = "/document"

    def GET(self):
        sql_doctype = """select null as "Value", '[空]' as "DisplayText" union all select f_value as "Value", f_code as "DisplayText" from t_code_data where f_category = 'DocumentType'"""
        doctypes = list(pg.db.query(sql_doctype))

        return render.rendeHtml("pc/document", doctypes=json.dumps(doctypes))



class PCLoginAction(pc_app.page):
    path = "/loginaction"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            account = input.get('username')
            password = input.get('password')

            user = pg.db.query("SELECT * FROM t_user WHERE f_account=$account and f_password=$password", vars={'account': account, 'password': password})

            if user:
                user = user[0]

            json_data = {"code": 5, "message": "登录验证失败：账号为【" + account + "】的账户不存在或已被停用！"}
            if user is not None:
                json_data = {"code": 1}
                web.ctx.session.user = user
                content = "用户[" + user.f_name + "]于" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " 登录系统"
                pg.db.insert('t_log', f_content=content, f_loger_id=user.f_id, f_action="登录")

            return json.dumps(json_data, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'code': 6, 'message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUser4jtable(pc_app.page):
    path = "/GetUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_user where f_name ~* $filter or f_account ~* $filter or f_phone ~* $filter order by f_id"
            shifts = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteUser4jtable(pc_app.page):
    path = "/DeleteUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_user', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateUser4jtable(pc_app.page):
    path = "/UpdateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_user', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateUser4jtable(pc_app.page):
    path = "/CreateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_account = data.f_account
            users = pg.db.select('t_user', where="f_account='%s'" % f_account)
            result = {"Result": "ERROR", "Message": "该帐号已经存在！"}

            if not users:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_user', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUser4jtable(pc_app.page):
    path = "/GetUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_user where f_name ~* $filter or f_account ~* $filter or f_phone ~* $filter order by f_id"
            shifts = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteUser4jtable(pc_app.page):
    path = "/DeleteUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_user', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateUser4jtable(pc_app.page):
    path = "/UpdateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_user', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateUser4jtable(pc_app.page):
    path = "/CreateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_account = data.f_account
            users = pg.db.select('t_user', where="f_account='%s'" % f_account)
            result = {"Result": "ERROR", "Message": "该帐号已经存在！"}

            if not users:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_user', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUser4jtable(pc_app.page):
    path = "/GetUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_user where f_name ~* $filter or f_account ~* $filter or f_phone ~* $filter order by f_id"
            shifts = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteUser4jtable(pc_app.page):
    path = "/DeleteUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_user', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateUser4jtable(pc_app.page):
    path = "/UpdateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_user', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateUser4jtable(pc_app.page):
    path = "/CreateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_account = data.f_account
            users = pg.db.select('t_user', where="f_account='%s'" % f_account)
            result = {"Result": "ERROR", "Message": "该帐号已经存在！"}

            if not users:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_user', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetStreet4jtable(pc_app.page):
    path = "/GetStreet4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_street order by f_id"
            streets = list(pg.db.query(sql))

            return getjTablePageRow(streets, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteStreet4jtable(pc_app.page):
    path = "/DeleteStreet4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_street', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateStreet4jtable(pc_app.page):
    path = "/UpdateStreet4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_street', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateStreet4jtable(pc_app.page):
    path = "/CreateStreet4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_name = data.f_name
            streets = pg.db.select('t_street', where="f_name='%s'" % f_name)
            result = {"Result": "ERROR", "Message": "该名称路段已经存在！"}

            if not streets:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_street', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParking4jtable(pc_app.page):
    path = "/GetParking4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_parking where f_name ~* $filter or f_code ~* $filter order by f_id"
            parkings = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(parkings, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteParking4jtable(pc_app.page):
    path = "/DeleteParking4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_parking', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateParking4jtable(pc_app.page):
    path = "/UpdateParking4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {'f_is_free': 0, 'f_is_private': 0, 'f_has_device': 0}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_parking', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateParking4jtable(pc_app.page):
    path = "/CreateParking4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_code = data.f_code
            streets = pg.db.select('t_parking', where="f_code='%s'" % f_code)
            result = {"Result": "ERROR", "Message": "该编号车位已经存在！"}

            if not streets:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_parking', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetRegion4jtable(pc_app.page):
    path = "/GetRegion4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_region order by f_id"
            streets = list(pg.db.query(sql))

            return getjTablePageRow(streets, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteRegion4jtable(pc_app.page):
    path = "/DeleteRegion4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_region', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateRegion4jtable(pc_app.page):
    path = "/UpdateRegion4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_region', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateRegion4jtable(pc_app.page):
    path = "/CreateRegion4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_name = data.f_name
            regions = pg.db.select('t_region', where="f_name='%s'" % f_name)
            result = {"Result": "ERROR", "Message": "该名称路段已经存在！"}

            if not regions:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_region', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetShift4jtable(pc_app.page):
    path = "/GetShift4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_shift order by f_id"
            shifts = list(pg.db.query(sql))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteShift4jtable(pc_app.page):
    path = "/DeleteShift4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_shift', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateShift4jtable(pc_app.page):
    path = "/UpdateShift4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_shift', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateShift4jtable(pc_app.page):
    path = "/CreateShift4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_name = data.f_name
            shifts = pg.db.select('t_shift', where="f_name='%s'" % f_name)
            result = {"Result": "ERROR", "Message": "该名称班次已经存在！"}

            if not shifts:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_shift', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUser4jtable(pc_app.page):
    path = "/GetUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_user where f_name ~* $filter or f_account ~* $filter or f_phone ~* $filter order by f_id"
            shifts = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteUser4jtable(pc_app.page):
    path = "/DeleteUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_user', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateUser4jtable(pc_app.page):
    path = "/UpdateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_user', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateUser4jtable(pc_app.page):
    path = "/CreateUser4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_account = data.f_account
            users = pg.db.select('t_user', where="f_account='%s'" % f_account)
            result = {"Result": "ERROR", "Message": "该帐号已经存在！"}

            if not users:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_user', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParkingRecord4jtable(pc_app.page):
    path = "/GetParkingRecord4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = """
                select *
                ,
                (select f_image from t_parking_image tpi where tpi.f_key = tpr.f_key and char_length(f_image) < 200 limit 1 ) as f_image
                from t_parking_record tpr
                where
                (f_key ~* $filter
                   or
                 f_parking_code ~* $filter
                   or f_creater_id in (select f_id from t_user where f_name ~* $filter)
                   or f_coster_id in (select f_id from t_user where f_name ~* $filter))
                   and  date(f_parking_stamp) = date($datepicker)
                   order by f_id desc"""
            parkings = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(parkings, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetRole4jtable(pc_app.page):
    path = "/GetRole4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_role order by f_id"
            roles = list(pg.db.query(sql))

            return getjTablePageRow(roles, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteRole4jtable(pc_app.page):
    path = "/DeleteRole4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_role', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateRole4jtable(pc_app.page):
    path = "/UpdateRole4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_role', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateRole4jtable(pc_app.page):
    path = "/CreateRole4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_name = data.f_name
            roles = pg.db.select('t_role', where="f_name='%s'" % f_name)
            result = {"Result": "ERROR", "Message": "该名称角色已经存在！"}

            if not roles:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_role', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUnit4jtable(pc_app.page):
    path = "/GetUnit4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get('filter', '')
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_unit where f_name ~* $filter or f_key ~* $filter order by f_id"
            units = list(pg.db.query(sql, vars={'filter': filter}))

            return getjTablePageRow(units, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteUnit4jtable(pc_app.page):
    path = "/DeleteUnit4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_unit', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateUnit4jtable(pc_app.page):
    path = "/UpdateUnit4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_unit', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateUnit4jtable(pc_app.page):
    path = "/CreateUnit4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_key = data.f_key
            units = pg.db.select('t_unit', where="f_key='%s'" % f_key)
            result = {"Result": "ERROR", "Message": "该Key已经存在！"}

            if not units:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_unit', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetCodeData4jtable(pc_app.page):
    path = "/GetCodeData4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get('filter', '')
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_code_data where f_code ~* $filter or f_category ~* $filter or f_value ~* $filter order by f_id"
            roles = list(pg.db.query(sql, vars={"filter": filter}))

            return getjTablePageRow(roles, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteCodeData4jtable(pc_app.page):
    path = "/DeleteCodeData4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_code_data', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateCodeData4jtable(pc_app.page):
    path = "/UpdateCodeData4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_code_data', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateCodeData4jtable(pc_app.page):
    path = "/CreateCodeData4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_code = data.f_code
            roles = pg.db.select('t_code_data', where="f_code='%s'" % f_code)
            result = {"Result": "ERROR", "Message": "该代码已经存在！"}

            if not roles:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_code_data', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetCodeMan4jtable(pc_app.page):
    path = "/GetCodeMan4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_code_man where f_code ~* $filter order by f_id"
            roles = list(pg.db.query(sql, vars={'filter': filter}))

            return getjTablePageRow(roles, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteCodeMan4jtable(pc_app.page):
    path = "/DeleteCodeMan4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_code_man', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateCodeMan4jtable(pc_app.page):
    path = "/UpdateCodeMan4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_code_man', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateCodeMan4jtable(pc_app.page):
    path = "/CreateCodeMan4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_code = data.f_code
            sqls = pg.db.select('t_code_man', where="f_code='%s'" % f_code)
            result = {"Result": "ERROR", "Message": "该代码已经存在！"}

            if not sqls:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_code_man', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetLog4jtable(pc_app.page):
    path = "/GetLog4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")

            filter = input.get('filter', '')
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = "select * from t_log where f_content ~* $filter and  date(f_log_time) = date($datepicker)  order by f_id desc"
            logs = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(logs, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetCheckRecord4jtable(pc_app.page):
    path = "/GetCheckRecord4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")
            filter = input.get('filter', '')
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = "select * from t_check_record where (f_parking_code ~* $filter or f_car_no ~* $filter ) and  date(f_check_stamp) = date($datepicker)  order by f_id desc"
            records = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(records, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetEscapeRecord4jtable(pc_app.page):
    path = "/GetEscapeRecord4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = "select * from t_parking_record where f_cost_type='逃逸' and (f_key ~* $filter or f_parking_code ~* $filter) and  date(f_parking_stamp) = date($datepicker) order by f_id"
            parkings = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(parkings, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParkingCount4jtable(pc_app.page):
    path = "/GetParkingCount4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start_date = input.get("start_date", "")
            end_date = input.get("end_date", "")

            start_time = input.get("start_time", "")
            end_time = input.get("end_time", "")

            #date_range = input.get("date_range", "")
            street = input.get("street", "")
            coster = input.get("coster", "")

            where = " 1=1 "
            filters = {}

            start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            where += """
                and f_leave_stamp is not null
                and date(f_leave_stamp) between $start_date and $end_date
                and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
            """
            filters["start_date"] = start_date
            filters["end_date"] = end_date
            filters["start_time"] = start_time
            filters["end_time"] = end_time
            filters["date_range"] = "日期：" + start_date + " ～ " + end_date + "\r\n时段:" + start_time + " ~ " + end_time

            if street != "":
                where += " and f_street_id = $street"
                filters["street"] = int(street)

            if coster != "":
                where += " and f_coster_id = $coster"
                filters["coster"] = int(coster)

            sql = """
                select
                    $date_range as f_date_range
                    ,sum(f_act_cost) as f_act_cost
                    ,f_coster_id
                    ,f_street_id
                from t_parking_record
                where %s
                group by f_coster_id, f_street_id
                order by f_street_id, f_coster_id
                """ % where

            result = list(pg.db.query(sql, vars=filters))
            json_data = {'Result': "OK", 'Records': result, 'TotalRecordCount': len(result)}
            return json.dumps(json_data, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParkingTypeCount4jtable(pc_app.page):
    path = "/GetParkingTypeCount4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start_date = input.get("start_date", "")
            end_date = input.get("end_date", "")

            start_time = input.get("start_time", "")
            end_time = input.get("end_time", "")

            #date_range = input.get("date_range", "")
            street = input.get("street", "")
            coster = input.get("coster", "")
            cost_type = input.get("cost_type", "")

            where = " 1=1 "
            filters = {}

            start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            where += """
                and f_leave_stamp is not null
                and date(f_leave_stamp) between $start_date and $end_date
                and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
            """
            filters["start_date"] = start_date
            filters["end_date"] = end_date
            filters["start_time"] = start_time
            filters["end_time"] = end_time
            filters["date_range"] = u"日期：" + start_date + " ～ " + end_date + u" 时段:" + start_time + " ~ " + end_time

            if street != "":
                where += " and f_street_id = $street"
                filters["street"] = int(street)

            if coster != "":
                where += " and f_coster_id = $coster"
                filters["coster"] = int(coster)

            if cost_type != "":
                where += " and f_cost_type = $cost_type"
                filters["cost_type"] = cost_type

            sql = """
                select
                    $date_range as f_date_range
                    ,f_street_id
                    ,f_coster_id
                    ,f_cost_type
                    ,count(*) as f_parking_times
                    ,sum(f_cost) as f_cost
                    ,sum(f_act_cost) as f_act_cost
                from t_parking_record
                where %s
                group by f_coster_id, f_cost_type, f_street_id
                order by f_street_id, f_cost_type, f_coster_id
                """ % where

            result = list(pg.db.query(sql, vars=filters))
            json_data = {'Result': "OK", 'Records': result, 'TotalRecordCount': len(result)}
            return json.dumps(json_data, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParkingDayCount4jtable(pc_app.page):
    path = "/GetParkingDayCount4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start_date = input.get("start_date", "")
            end_date = input.get("end_date", "")

            start_time = input.get("start_time", "")
            end_time = input.get("end_time", "")

            street = input.get("street", "")
            coster = input.get("coster", "")

            where = " 1=1 "
            filters = {}

            start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            where += """
                and f_leave_stamp is not null
                and date(f_leave_stamp) between $start_date and $end_date
                and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
            """
            filters["start_date"] = start_date
            filters["end_date"] = end_date
            filters["start_time"] = start_time
            filters["end_time"] = end_time

            if street != "":
                where += " and f_street_id = $street"
                filters["street"] = int(street)

            if coster != "":
                where += " and f_coster_id = $coster"
                filters["coster"] = int(coster)

            sql = """ select
                    ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as f_date_range
                    ,date(f_leave_stamp) as f_day_range
                    ,f_street_id
                    ,f_coster_id
                    ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as f_cost_times
                    ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as f_cost_range
                    ,sum(case when f_cost_type = '正常缴费' then f_act_cost else  0::money end) as f_act_cost
                    ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as f_free_times
                    ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as f_free_range
                    ,sum(case when f_cost_type = '逃逸' then 1 else 0 end) as f_escape_times
                    ,sum(case when f_cost_type = '逃逸' then f_cost else 0::money end) as f_escape_cost
                from t_parking_record tpr
                where {0}
                group by date(f_leave_stamp), f_coster_id, f_street_id
                order by f_street_id, f_coster_id """.format(where)

            result = list(pg.db.query(sql, vars=filters))
            json_data = {'Result': "OK", 'Records': result, 'TotalRecordCount': len(result)}
            return json.dumps(json_data, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetParkingDetailsCount4jtable(pc_app.page):
    path = "/GetParkingDetailsCount4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            start_date = input.get("start_date", "")
            end_date = input.get("end_date", "")

            start_time = input.get("start_time", "")
            end_time = input.get("end_time", "")

            #date_range = input.get("date_range", "")
            street = input.get("street", "")
            coster = input.get("coster", "")
            cost_type = input.get("cost_type", "")
            shift = input.get("shift", "")
            parking_code = input.get("parking_code", "")

            where = " 1=1 "
            filters = {}

            start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            where += """
                and f_leave_stamp is not null
                and date(f_leave_stamp) between $start_date and $end_date
                and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
            """

            filters["start_date"] = start_date
            filters["end_date"] = end_date
            filters["start_time"] = start_time
            filters["end_time"] = end_time
            filters["date_range"] = u"日期：" + start_date + " ～ " + end_date + u" 时段:" + start_time + " ~ " + end_time

            if street != "":
                where += " and f_street_id = $street"
                filters["street"] = int(street)

            if coster != "":
                where += " and f_coster_id = $coster"
                filters["coster"] = int(coster)

            if shift != "":
                where += " and f_shift_id = $shift"
                filters["shift"] = int(shift)

            if cost_type != "":
                where += " and f_cost_type = $cost_type"
                filters["cost_type"] = cost_type

            if parking_code != "":
                where += " and f_parking_code = $parking_code"
                filters["parking_code"] = parking_code

            sql = """
                select
                    ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as f_date_range
                    ,date(f_leave_stamp) as f_day_range
                    ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as f_street_id
                    ,(select f_name from t_user ts where ts.f_id = tpr.f_coster_id) as f_coster_id
                    ,(select f_name from t_shift ts where ts.f_id = (select f_shift_id from t_user tu where tu.f_id = tpr.f_coster_id limit 1)) as f_shift_id
                    ,(select f_name from t_parking tp where tp.f_street_id = tpr.f_street_id and f_code = f_parking_code limit 1) as f_parking_code
                    ,f_car_no
                    ,f_parking_stamp as f_parking_stamp
                    ,f_leave_stamp as f_leave_stamp
                    ,f_cost_type as f_cost_type
                    ,round(abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60)::numeric,0) || '分钟' as f_cost_range
                    ,f_cost as f_cost
                    ,f_act_cost as f_act_cost
                from t_parking_record tpr
                where %s
                order by f_street_id, f_cost_type, f_coster_id
                """ % where

            result = list(pg.db.query(sql, vars=filters))
            return getjTablePageRow(result, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetReports4jtable(pc_app.page):
    path = "/GetReports4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            date_range = input.get("date_range", "")
            street = input.get("street", "")
            coster = input.get("coster", "")

            where = " 1=1 "
            filters = {}

            start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            if date_range == "":
                start_time = "2013-01-01 00:00:00"
            else:
                if date_range == "now":
                    pass
                if date_range == "week":
                    start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime((time.time() - 24 * 60 * 60 * (datetime.datetime.now().weekday()))))
                if date_range == "month":
                    start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime((time.time() - 24 * 60 * 60 * (datetime.datetime.now().day - 1))))
                if date_range == "year":
                    start_time = datetime.datetime(datetime.datetime.now().year, 1, 1).strftime('%Y-%m-%d 00:00:00')

            where += " and f_report_day >= $start_time::DATE and f_report_day <= $end_time::DATE"
            filters["start_time"] = start_time
            filters["end_time"] = end_time

            if street != "":
                where += " and f_street_id = $street"
                filters["street"] = int(street)
            if coster != "":
                where += " and f_coster_id=$coster"
                filters["coster"] = int(coster)

            sql = """
                select
                    *
                from t_reports
                where %s

                order by f_report_day desc

                """ % where

            result = list(pg.db.query(sql, vars=filters))
            json_data = {'Result': "OK", 'Records': result, 'TotalRecordCount': len(result)}
            return json.dumps(json_data, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetMessage4jtable(pc_app.page):
    path = "/GetMessage4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = "select * from t_message where (f_content ~* $filter or f_parking_code ~* $filter or f_device_code ~* $filter) and  date(f_create_time) = date($datepicker) order by f_id"
            parkings = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(parkings, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetMonitorRecord4jtable(pc_app.page):
    path = "/GetMonitorRecord4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            datepicker = input.get("datepicker", "")
            filter = input.get("filter", "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if datepicker == "":
                datepicker = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            sql = "select * from t_monitor_record where (f_data ~* $filter or f_parking_code ~* $filter or f_device_code ~* $filter ) and  date(f_stamp) = date($datepicker) order by f_id"
            records = list(pg.db.query(sql, vars={"filter": filter, "datepicker": datepicker}))

            return getjTablePageRow(records, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetMonitorRecordAll4jtable(pc_app.page):
    path = "/GetMonitorRecordAll4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            start_date = input.get("start_date", "")
            end_date = input.get("end_date", "")

            start_time = input.get("start_time", "")
            end_time = input.get("end_time", "")

            parking = input.get("parking", "")

            where = " 1=1 "
            filters = {}

            start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
            end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            where += """
                and date(f_parking_stamp) between $start_date and $end_date
                and to_char(f_parking_stamp, 'HH24:MI:SS') between $start_time and $end_time
            """

            filters["start_date"] = start_date
            filters["end_date"] = end_date
            filters["start_time"] = start_time
            filters["end_time"] = end_time

            if parking != "":
                where += " and f_parking_id = $parking"
                filters["parking"] = int(parking)

            sql = """
                select
                    *
                from t_monitor_record_all tpr
                where %s
                order by f_id desc, f_stamp desc
                """ % where

            result = list(pg.db.query(sql, vars=filters))
            return getjTablePageRow(result, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetDocument4jtable(pc_app.page):
    path = "/GetDocument4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_document order by f_id"
            shifts = list(pg.db.query(sql))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteDocument4jtable(pc_app.page):
    path = "/DeleteDocument4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_document', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateDocument4jtable(pc_app.page):
    path = "/UpdateDocument4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_document', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateDocument4jtable(pc_app.page):
    path = "/CreateDocument4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            f_name = data.f_name
            documents = pg.db.select('t_document', where="f_name='%s'" % f_name)
            result = {"Result": "ERROR", "Message": "该名称资料已经存在！"}

            if not documents:
                for k, v in data.items():
                    if v == '':
                        data[k] = None
                pg.db.insert('t_document', **data)
                result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetDevice4jtable(pc_app.page):
    path = "/GetDevice4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_device order by f_id"
            shifts = list(pg.db.query(sql))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteDevice4jtable(pc_app.page):
    path = "/DeleteDevice4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_document', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateDevice4jtable(pc_app.page):
    path = "/UpdateDevice4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_device', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateDevice4jtable(pc_app.page):
    path = "/CreateDevice4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            #f_code = data.f_code
            #shifts = pg.db.select('t_device', where="f_code='%s'" % f_code)
            #result = {"Result": "ERROR", "Message": "该设备编号已经存在！"}

            #if not shifts:
            for k, v in data.items():
                if v == '':
                    data[k] = None
            pg.db.insert('t_device', **data)
            result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetCommand4jtable(pc_app.page):
    path = "/GetCommand4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)
            sql = "select * from t_command order by f_id"
            shifts = list(pg.db.query(sql))

            return getjTablePageRow(shifts, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class DeleteCommand4jtable(pc_app.page):
    path = "/DeleteCommand4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            count = pg.db.delete('t_command', where="f_id=%d" % id)
            result = {"Result": "ERROR", "Message": "删除失败！"}
            if count == 1:
                result = {"Result": "OK"}
            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '删除数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class UpdateCommand4jtable(pc_app.page):
    path = "/UpdateCommand4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            id = int(data.f_id)

            columns = {}
            for k, v in data.items():
                columns[k] = v
                if v == '':
                    columns[k] = None
            count = pg.db.update('t_command', where="f_id=%d" % id, **columns)
            result = {"Result": "ERROR", "Message": "更新失败！"}
            if count == 1:
                result = {"Result": "OK"}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '更新数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class CreateCommand4jtable(pc_app.page):
    path = "/CreateCommand4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            data = web.input()
            for k, v in data.items():
                if v == '':
                    data[k] = None
            pg.db.insert('t_command', **data)
            result = {"Result": "OK", "Record": data}

            return json.dumps(result, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '新增数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class Upload4KindEditor(pc_app.page):
    path = "/upload4kindeditor"
    ext_arr = {
        'image': ['jpg', 'gif', 'png', 'tif', 'bmp'],
        'flash': ['swf', 'flv'],
        'media': ['swf', 'flv', 'mp3', 'wav', 'wma', 'wmv', 'mid', 'avi', 'mpg', 'asf', 'rm', 'rmvb'],
        'file': ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'htm', 'html', 'txt', 'zip', 'rar', 'gz', 'bz2'],
    }

    def POST(self):
        x = web.input(imgFile={})
        jerror = lambda msg: json.dumps({'error': 1, 'message': msg})

        if 'imgFile' not in x:
            return jerror('请选择文件!')

        filepath = x.imgFile.filename.replace('\\', '/')  # 客户端为windows时注意
        filename = filepath.split('/')[-1]  # 获取文件名
        ext = filename.split('.', 1)[1]  # 获取后缀

        if ext not in self.ext_arr["image"]:
            return jerror('请选择正确的文件类型!')

        homedir = os.getcwd()
        filedir = '%s/static/uploads' % homedir  # 要上传的路径
        now = datetime.datetime.now()
        t = "%d%d%d%d%d%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)  # 以时间作为文件名
        filename = t + '.' + ext

        fout = open(filedir + '/' + filename, 'wb')
        fout.write(x.imgFile.file.read())
        fout.close()

        return json.dumps({'error': 0, 'url': "/static/uploads/%s" % filename})


class LoadParkingImage(pc_app.page):
    path = "/loadparkingimage"

    def GET(self):
        input = web.input()
        key = input.get("key", "")

        images = list(pg.db.query('select * from t_parking_image where f_key=$key', vars={"key": key}))

        if images and images[0]:
            images = images[0]
            return "data:image/jpeg;charset=utf-8;base64,%s" % images.f_image

        return ""


class ExportParkingCount(pc_app.page):
    """
    导出收入统计Excel报表
    """
    path = "/exportparkingcount"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        start_date = input.get("start_date", "")
        end_date = input.get("end_date", "")

        start_time = input.get("start_time", "")
        end_time = input.get("end_time", "")

        #date_range = input.get("date_range", "")
        street = input.get("street", "")
        coster = input.get("coster", "")

        where = " 1=1 "
        filters = {}

        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        where += """
            and f_leave_stamp is not null
            and date(f_leave_stamp) between $start_date and $end_date
            and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
        """
        filters["start_date"] = start_date
        filters["end_date"] = end_date
        filters["start_time"] = start_time
        filters["end_time"] = end_time

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)

        if coster != "":
            where += " and f_coster_id = $coster"
            filters["coster"] = int(coster)

        sql = """
            select
                ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as date_range
                ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
                ,(select f_name from t_user ts where ts.f_id = tpr.f_coster_id) as coster
                ,sum(f_act_cost)::numeric::float8 as act_cost
            from t_parking_record tpr
            where %s
            group by f_coster_id, f_street_id
            order by f_street_id, f_coster_id

            """ % where

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'收入总额统计表')
        ws.write(0, 0, u"统计时段")
        ws.write(0, 1, u"路段")
        ws.write(0, 2, u"收费员")
        ws.write(0, 3, u"收入(元)")

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.date_range or "")
            ws.write(i + 1, 1, r.street or "")
            ws.write(i + 1, 2, r.coster or "")
            ws.write(i + 1, 3, r.act_cost or 0)
            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportParkingTypeCount(pc_app.page):
    """
    导出收入类型统计Excel报表
    """
    path = "/exportparkingtypecount"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        start_date = input.get("start_date", "")
        end_date = input.get("end_date", "")

        start_time = input.get("start_time", "")
        end_time = input.get("end_time", "")

        #date_range = input.get("date_range", "")
        street = input.get("street", "")
        coster = input.get("coster", "")
        cost_type = input.get("cost_type", "")

        where = " 1=1 "
        filters = {}

        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        where += """
            and f_leave_stamp is not null
            and date(f_leave_stamp) between $start_date and $end_date
            and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
        """
        filters["start_date"] = start_date
        filters["end_date"] = end_date
        filters["start_time"] = start_time
        filters["end_time"] = end_time

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)

        if coster != "":
            where += " and f_coster_id = $coster"
            filters["coster"] = int(coster)

        if cost_type != "":
            where += " and f_cost_type = $cost_type"
            filters["cost_type"] = cost_type

        sql = """
            select
                ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as date_range
                ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
                ,(select f_name from t_user ts where ts.f_id = tpr.f_coster_id) as coster
                ,f_cost_type as cost_type
                ,count(*) as parking_times
                ,sum(f_cost)::numeric::float8 as cost
                ,sum(f_act_cost)::numeric::float8 as act_cost
            from t_parking_record tpr
            where %s
            group by f_coster_id, f_cost_type, f_street_id
            order by f_street_id, f_cost_type, f_coster_id

            """ % where

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'收入总额统计表')
        ws.write(0, 0, u"统计时段")
        ws.write(0, 1, u"路段")
        ws.write(0, 2, u"收费员")
        ws.write(0, 3, u"收费类型")
        ws.write(0, 4, u"车次")
        ws.write(0, 5, u"应收(元)")
        ws.write(0, 6, u'实收(元)')  # 如果要写中文请使用UNICODE

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.date_range or "")
            ws.write(i + 1, 1, r.street or "")
            ws.write(i + 1, 2, r.coster or "")
            ws.write(i + 1, 3, r.cost_type or "")
            ws.write(i + 1, 4, r.parking_times or 0)
            ws.write(i + 1, 5, r.cost or 0)
            ws.write(i + 1, 6, r.act_cost or 0)
            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportParkingDayCount(pc_app.page):
    """
    导出收入日报统计Excel报表
    """
    path = "/exportparkingdaycount"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        start_date = input.get("start_date", "")
        end_date = input.get("end_date", "")

        start_time = input.get("start_time", "")
        end_time = input.get("end_time", "")

        #date_range = input.get("date_range", "")
        street = input.get("street", "")
        coster = input.get("coster", "")

        where = " 1=1 "
        filters = {}

        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        where += """
            and f_leave_stamp is not null
            and date(f_leave_stamp) between $start_date and $end_date
            and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
        """
        filters["start_date"] = start_date
        filters["end_date"] = end_date
        filters["start_time"] = start_time
        filters["end_time"] = end_time

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)

        if coster != "":
            where += " and f_coster_id = $coster"
            filters["coster"] = int(coster)

        sql = """
           select
                ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as date_range
                ,date(f_leave_stamp) as day_range
                ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
                ,(select f_name from t_user ts where ts.f_id = tpr.f_coster_id) as coster
                ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as cost_times
                ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as cost_range
                ,sum(case when f_cost_type = '正常缴费' then f_act_cost else  0::money end)::numeric::float8 as act_cost
                ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as free_times
                ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as free_range
                ,sum(case when f_cost_type = '逃逸' then 1 else 0 end) as escape_times
                ,sum(case when f_cost_type = '逃逸' then f_cost else 0::money end)::numeric::float8 as escape_cost
            from t_parking_record tpr
            where {0}
            group by date(f_leave_stamp), f_coster_id, f_street_id
            order by f_street_id, f_coster_id
            """.format(where)

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'收入总额统计表')
        ws.write(0, 0, u"统计时段")
        ws.write(0, 1, u"日期")
        ws.write(0, 2, u"路段")
        ws.write(0, 3, u"收费员")
        ws.write(0, 4, u"收费车次")
        ws.write(0, 5, u"收费时长")
        ws.write(0, 6, u"收费金额(元)")
        ws.write(0, 7, u"免费车次")
        ws.write(0, 8, u'免费时长')  # 如果要写中文请使用UNICODE
        ws.write(0, 9, u'逃逸车次')
        ws.write(0, 10, u'逃逸应收金额(元)')
        ws.write(0, 11, u'收费员签字')
        ws.write(0, 12, u'备注')

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.date_range or "")
            ws.write(i + 1, 1, str(r.day_range))
            ws.write(i + 1, 2, r.street or "")
            ws.write(i + 1, 3, r.coster or "")
            ws.write(i + 1, 4, r.cost_times or 0)
            ws.write(i + 1, 5, r.cost_range or "")
            ws.write(i + 1, 6, r.act_cost or 0)
            ws.write(i + 1, 7, r.free_times or 0)
            ws.write(i + 1, 8, r.free_range or "")
            ws.write(i + 1, 9, r.escape_times or 0)
            ws.write(i + 1, 10, r.escape_cost or 0)
            ws.write(i + 1, 11, "")
            ws.write(i + 1, 12, "")

            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportParkingDetailsCount(pc_app.page):
    """
    导出收入明细统计Excel报表
    """
    path = "/exportparkingdetailscount"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        start_date = input.get("start_date", "")
        end_date = input.get("end_date", "")

        start_time = input.get("start_time", "")
        end_time = input.get("end_time", "")

        #date_range = input.get("date_range", "")
        street = input.get("street", "")
        coster = input.get("coster", "")
        cost_type = input.get("cost_type", "")
        shift = input.get("shift", "")
        parking_code = input.get("parking_code", "")

        where = " 1=1 "
        filters = {}

        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":59"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        where += """
            and f_leave_stamp is not null
            and date(f_leave_stamp) between $start_date and $end_date
            and to_char(f_leave_stamp, 'HH24:MI:SS') between $start_time and $end_time
        """
        filters["start_date"] = start_date
        filters["end_date"] = end_date
        filters["start_time"] = start_time
        filters["end_time"] = end_time

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)

        if coster != "":
            where += " and f_coster_id = $coster"
            filters["coster"] = int(coster)

        if shift != "":
            where += " and f_shift_id = $shift"
            filters["shift"] = int(shift)

        if cost_type != "":
            where += " and f_cost_type = $cost_type"
            filters["cost_type"] = cost_type

        if parking_code != "":
            where += " and f_parking_code = $parking_code"
            filters["parking_code"] = parking_code

        sql = """
            select
                ('日期：' || $start_date || ' ～ ' || $end_date || ' 时段:' || $start_time || ' ~ ' || $end_time) as date_range
                ,date(f_leave_stamp) as day_range
                ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
                ,(select f_name from t_user ts where ts.f_id = tpr.f_coster_id) as coster
                ,(select f_name from t_shift ts where ts.f_id = (select f_shift_id from t_user tu where tu.f_id = tpr.f_coster_id limit 1)) as shift
                ,(select f_name from t_parking tp where tp.f_street_id = tpr.f_street_id and f_code = f_parking_code limit 1) as parking_code
                ,f_car_no as car_no
                ,f_parking_stamp as parking_stamp
                ,f_leave_stamp as leave_stamp
                ,f_cost_type as cost_type
                ,round(abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60)::numeric,0) || '分钟' as cost_range
                ,f_cost::numeric::float8 as cost
                ,f_act_cost::numeric::float8 as act_cost
            from t_parking_record tpr
            where {0}
            order by f_street_id, f_cost_type, f_coster_id
            """.format(where)

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'收入明细流水表')
        ws.write(0, 0, u"统计时段")
        ws.write(0, 1, u"日期")
        ws.write(0, 2, u"路段")
        ws.write(0, 3, u"收费员")
        ws.write(0, 4, u"班次")
        ws.write(0, 5, u"车位号")
        ws.write(0, 6, u"车牌号")
        ws.write(0, 7, u"停车时间")
        ws.write(0, 8, u"离开时间")
        ws.write(0, 9, u"收费类型")
        ws.write(0, 10, u"计费时长")
        ws.write(0, 11, u"应收金额(元)")
        ws.write(0, 12, u'实收金额(元)')  # 如果要写中文请使用UNICODE

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.date_range or "")
            ws.write(i + 1, 1, str(r.day_range))
            ws.write(i + 1, 2, r.street or "")
            ws.write(i + 1, 3, r.coster or "")
            ws.write(i + 1, 4, r.shift or "")
            ws.write(i + 1, 5, r.parking_code or "")
            ws.write(i + 1, 6, r.car_no or "")
            ws.write(i + 1, 7, str(r.parking_stamp) or "")
            ws.write(i + 1, 8, str(r.leave_stamp) or "")
            ws.write(i + 1, 9, r.cost_type or "")
            ws.write(i + 1, 10, r.cost_range or "")
            ws.write(i + 1, 11, r.cost or 0)
            ws.write(i + 1, 12, r.act_cost or 0)

            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportReports(pc_app.page):
    """
    导出日报结帐确认查询结果
    """
    path = "/exportreports"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        date_range = input.get("date_range", "")
        street = input.get("street", "")
        coster = input.get("coster", "")

        where = " 1=1 "
        filters = {}

        start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        if date_range == "":
            start_time = "2013-01-01 00:00:00"
            filters["date_range"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        else:
            if date_range == "now":
                pass
            if date_range == "week":
                start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime((time.time() - 24 * 60 * 60 * (datetime.datetime.now().weekday()))))
            if date_range == "month":
                start_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime((time.time() - 24 * 60 * 60 * (datetime.datetime.now().day - 1))))
            if date_range == "year":
                start_time = datetime.datetime(datetime.datetime.now().year, 1, 1).strftime('%Y-%m-%d 00:00:00')

        where += " and f_report_day >= $start_time::DATE and f_report_day <= $end_time::DATE"
        filters["start_time"] = start_time
        filters["end_time"] = end_time
        filters["date_range"] = start_time[0:10] + "~" + end_time[0:10]

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)
        if coster != "":
            where += " and f_coster_id=$coster"
            filters["coster"] = int(coster)

        sql = """
            SELECT
            f_id
            ,(select f_name from t_user where f_id = f_coster_id ) as f_coster_name
            ,f_report_day
            ,(select f_name from t_user where f_id = f_group_leader_id) as f_leader_name
            ,(case when f_is_confirm > 0 then '是' else '否' end) as f_is_confirm
            ,f_cost
            ,f_act_cost
            ,f_cost_times
            ,f_free_times
            ,f_escape_times
            ,(select f_name from t_street where f_id = f_street_id) as f_street_name
            ,f_confirm_day
            FROM t_reports
            where %s
            order by f_street_id, f_report_day
            """ % where

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'日报确认表')
        ws.write(0, 0, u"序号")
        ws.write(0, 1, u"收费人员")
        ws.write(0, 2, u"日报日期")
        ws.write(0, 3, u'组长')  # 如果要写中文请使用UNICODE
        ws.write(0, 4, u"是否已确认")
        ws.write(0, 5, u"应缴金额")
        ws.write(0, 6, u"实缴金额")
        ws.write(0, 7, u'收费车次')  # 如果要写中文请使用UNICODE
        ws.write(0, 8, u"免费车次")
        ws.write(0, 9, u"逃逸车次")
        ws.write(0, 10, u"所属路段")
        ws.write(0, 11, u'确认日期')  # 如果要写中文请使用UNICODE

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.f_id or "")
            ws.write(i + 1, 1, r.f_coster_name or "")
            ws.write(i + 1, 2, str(r.f_report_day))
            ws.write(i + 1, 3, r.f_leader_name or "")
            ws.write(i + 1, 4, r.f_is_confirm)
            ws.write(i + 1, 5, r.f_cost or "")
            ws.write(i + 1, 6, r.f_act_cost or "")
            ws.write(i + 1, 7, r.f_cost_times or "")
            ws.write(i + 1, 8, r.f_free_times or "")
            ws.write(i + 1, 9, r.f_escape_times or "")
            ws.write(i + 1, 10, r.f_street_name or "")
            ws.write(i + 1, 11, str(r.f_confirm_day) if r.f_confirm_day else "")

            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportParkingDetails(pc_app.page):
    """
    导出停车统计明细Excel表
    """
    path = "/exportparkingdetails"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')  # 指定返回的类型
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        cost_type = input.get("cost_type", "")
        street = input.get("street", "")
        shift = input.get("shift", "")
        coster = input.get("coster", "")

        where = " 1=1 "
        filters = {}

        if cost_type != "":
            where += " and f_cost_type=$cost_type"
            filters["cost_type"] = cost_type

        start_time = input.get("start_time", "2013-01-01 00:00")
        end_time = input.get("end_time", time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())))
        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":00"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        where += " and f_leave_stamp between $start_time and $end_time"
        filters["start_time"] = start_time
        filters["end_time"] = end_time
        filters["date_range"] = start_time + "~" + end_time

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)
        if shift != "":
            where += " and f_shift_id=$shift"
            filters["shift"] = int(shift)
        if coster != "":
            where += " and f_coster_id=$coster"
            filters["coster"] = int(coster)

        sql = """
            select
             (select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
              ,(select
                  (select f_name from t_user tu where tu.f_id = ts.f_leader_id)
                  from t_shift ts where ts.f_id = tpr.f_shift_id) as leader
              ,(select f_name from t_user tu where tu.f_id = tpr.f_coster_id) as coster
              ,to_char(f_leave_stamp,'YYYY-MM-DD HH24:MI:SS') as stamp
              ,(select f_name from t_shift ts where ts.f_id = tpr.f_shift_id) as shift
              ,f_car_no as car_no
              ,to_char(f_parking_stamp,'YYYY-MM-DD HH24:MI:SS') as parking_stamp
              ,to_char(f_leave_stamp,'YYYY-MM-DD HH24:MI:SS') as leave_stamp
              ,round(abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60)::numeric,0) || '分钟' as stamp_range
              ,f_act_cost as act_cost
            from t_parking_record tpr
            where %s
            """ % where

        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'收费流水明细表')
        ws.write(0, 0, u"路段")
        ws.write(0, 1, u"组长")
        ws.write(0, 2, u"收费员")
        ws.write(0, 3, u'日期')
        ws.write(0, 4, u"班次")
        ws.write(0, 5, u"车牌号码")
        ws.write(0, 6, u"停车时间")
        ws.write(0, 7, u'离开时间')
        ws.write(0, 8, u"计费时长")
        ws.write(0, 9, u"收费金额")

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.street or "")
            ws.write(i + 1, 1, r.leader or "")
            ws.write(i + 1, 2, r.coster or "")
            ws.write(i + 1, 3, r.stamp or "")
            ws.write(i + 1, 4, r.shift or "")
            ws.write(i + 1, 5, r.car_no or "")
            ws.write(i + 1, 6, r.parking_stamp or "")
            ws.write(i + 1, 7, r.leave_stamp or "")
            ws.write(i + 1, 8, r.stamp_range or "")
            ws.write(i + 1, 9, r.act_cost or "")

            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class ExportParkingDay(pc_app.page):
    """
    导出停车统计日报表
    """
    path = "/exportparkingday"

    def GET(self):
        web.header('Content-type', 'application/vnd.ms-excel')  # 指定返回的类型
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment;filename="export.xls"')

        input = web.input()
        cost_type = input.get("cost_type", "")
        street = input.get("street", "")
        shift = input.get("shift", "")
        coster = input.get("coster", "")

        where = " 1=1 "
        filters = {}

        if cost_type != "":
            where += " and f_cost_type=$cost_type"
            filters["cost_type"] = cost_type

        start_time = input.get("start_time", "2013-01-01 00:00")
        end_time = input.get("end_time", time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())))
        start_time = start_time + ":00"  # time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
        end_time = end_time + ":00"  # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        where += " and f_leave_stamp between '%s' and '%s'" % (start_time, end_time,)
        print "where is : %s " % where

        if street != "":
            where += " and f_street_id = $street"
            filters["street"] = int(street)
        if shift != "":
            where += " and f_shift_id=$shift"
            filters["shift"] = int(shift)
        if coster != "":
            where += " and f_coster_id=$coster"
            filters["coster"] = int(coster)

        sql = """
             select
             to_char(f_leave_stamp,'YYYY-MM-DD') as stamp
              ,(select f_name from t_street ts where ts.f_id = tpr.f_street_id) as street
              ,(select f_name from t_user tu where tu.f_id = tpr.f_coster_id) as coster
              ,(select f_name from t_shift ts where ts.f_id = tpr.f_shift_id) as shift
              ,sum(case when f_cost_type = '正常缴费' then 1 else 0 end) as cost_times
              ,round(sum(case when f_cost_type = '正常缴费' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as parking_range
              ,sum(f_act_cost) as act_cost
              ,sum(case when f_cost_type like '%免费%' then 1 else 0 end) as free_times
              ,round(sum(case when f_cost_type like '%免费%' then abs(extract(epoch from f_leave_stamp - f_parking_stamp)/60) else 0 end)::numeric,0) || '分钟' as free_range
            from t_parking_record tpr
            where """

        sql = sql + where + " group by to_char(f_leave_stamp,'YYYY-MM-DD'), f_coster_id, f_shift_id, f_street_id, f_cost_type"
        print sql
        result = list(pg.db.query(sql, vars=filters))

        wb = pyExcelerator.Workbook()
        ws = wb.add_sheet(u'停车统计日报表')
        ws.write(0, 0, u"日期")
        ws.write(0, 1, u"路段")
        ws.write(0, 2, u"收费员")
        ws.write(0, 3, u"班次")
        ws.write(0, 4, u'收费车次')
        ws.write(0, 5, u"收费时长")
        ws.write(0, 6, u"收费金额(元)")
        ws.write(0, 7, u'免费车次')
        ws.write(0, 8, u"免费时长")
        ws.write(0, 9, u"收费员签字")
        ws.write(0, 10, u"备注")

        i = 0
        for r in result:
            ws.write(i + 1, 0, r.stamp or "")
            ws.write(i + 1, 1, r.street or "")
            ws.write(i + 1, 2, r.coster or "")
            ws.write(i + 1, 3, r.shift or "")
            ws.write(i + 1, 4, r.cost_times or "")
            ws.write(i + 1, 5, r.parking_range or "")
            ws.write(i + 1, 6, r.act_cost or 0)
            ws.write(i + 1, 7, r.free_times or "")
            ws.write(i + 1, 8, r.free_range or "")
            i = i + 1

        sio = StringIO.StringIO()
        wb.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()


class GetParkingRecordDetails4jtable(pc_app.page):
    path = "/GetParkingRecordDetails4jtable"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            record_id = input.get('record_id', "")
            start = input.get('jtStartIndex', 0)
            limit = input.get('jtPageSize', 20)

            if record_id is None or record_id == "":
                record_id = -1

            sql = "select *, (select f_image from t_parking_image where t_parking_image.f_key = t_parking_record.f_key limit 1 ) as f_image from t_parking_record where f_id=$record_id"
            parkings = list(pg.db.query(sql, vars={"record_id": record_id}))

            return getjTablePageRow(parkings, start, limit)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetRoleZTreeNodes(pc_app.page):
    path = "/getroleztreenodes"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            userid = input.get('userid', "")

            sql = "select *, (select count(f_role_id) from t_user_role tur where tur.f_role_id = tr.f_id and f_user_id = $userid) as count from t_role tr "
            roles = list(pg.db.query(sql, vars={"userid": userid}))

            results = []
            for role in roles:
                r = {"id": role.f_id, "pid": "", "name": role.f_name, "checked": "true" if role.count > 0 else "false"}
                results.append(r)

            print results
            return json.dumps(results, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'Result': "ERROR", 'Message': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class SaveUserRole(pc_app.page):
    path = "/saveuserrole"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            userid = int(input.get('userid', "-1"))
            roleids = input.get("roleids", "-1")

            print "userid is %s" % repr(userid)

            pg.db.delete("t_user_role", where="f_user_id=%d" % userid)

            roles = roleids.split(",")

            for roleid in roles:
                pg.db.insert("t_user_role", f_user_id=userid, f_role_id=int(roleid))

            results = {"success": True}
            return json.dumps(results, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': False, 'error': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUnitZTreeNodes(pc_app.page):
    path = "/getunitztreenodes"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            roleid = input.get('roleid', "")

            sql = "select *, (select count(f_unit_id) from t_role_unit tru where tru.f_unit_id = tu.f_id and f_role_id = $roleid) as count from t_unit tu order by f_index desc "
            units = list(pg.db.query(sql, vars={"roleid": roleid}))

            results = []
            for unit in units:
                u = {"id": unit.f_id, "pid": unit.f_parent_id, "name": unit.f_name, "checked": "true" if unit.count > 0 else "false"}
                results.append(u)
            return json.dumps(results, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': False, 'error': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class SaveRoleUnit(pc_app.page):
    path = "/saveroleunit"

    def POST(self):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        try:
            input = web.input()
            roleid = int(input.get('roleid', "-1"))
            unitids = input.get("unitids", "")

            pg.db.delete("t_role_unit", where="f_role_id=%d" % roleid)

            units = unitids.split(",")

            for unitid in units:
                pg.db.insert("t_role_unit", f_role_id=roleid, f_unit_id=int(unitid))

            results = {"success": True}
            return json.dumps(results, cls=ExtendedEncoder)
        except Exception:
            # 输出错误信息
            msg = traceback.print_exc()
            json_data = {'success': False, 'error': '获取数据失败,详细信息:%s' % msg}
            return json.dumps(json_data, cls=ExtendedEncoder)


class GetUserParkingList(pc_app.page):
    """
    获取某个收费人员负责的车位列表
    """

    path = "/ajax/getuserparkinglist/(\d+)"

    def GET(self, user_id):
        sql = """
            SELECT
               up.f_parking_id, up.f_user_id,
               u.f_name,
               p.f_name as f_parking_name,
               s.f_name as f_street_name
            FROM
               t_user_parking up,
               t_user u,
               t_parking p,
               t_street s
            WHERE
               u.f_id = up.f_user_id AND
               u.f_id = $user_id AND
               p.f_id = up.f_parking_id AND 
               s.f_id = p.f_street_id
            order by up.f_parking_id
        """

        parking_list = pg.db.query(sql, vars=locals())
        return json.dumps(list(parking_list))


class GetStreetParkingList(pc_app.page):
    """
    获取某条街道上的所有车位
    """
    
    path = "/ajax/getstreetparkinglist"

    def GET(self):
        street_id = web.input().get("street_id")
        user_id = web.input().get("user_id")

        street_id = int(street_id)
        user_id = int(user_id)

        sql_parking_list = "select * from t_parking where (f_street_id = %d and f_id not in (select f_parking_id from t_user_parking where f_user_id = %d) )order by f_id"%(street_id,user_id)
        parking_list = list(pg.db.query(sql_parking_list))

        return json.dumps(parking_list)

class GetUnusedParkingList(pc_app.page):
    """
    获取未分配额的车位列表
    """

    path = "/ajax/getunusedparkinglist"

    def GET(self):
        sql_unused_parking = "select * from t_parking where f_id not in (select f_parking_id from t_user_parking) order by f_id"
        unused_parking_list = list(pg.db.query(sql_unused_parking))

        return json.dumps(unused_parking_list)


class GetUnusedUserList(pc_app.page):
    
    path = "/ajax/getunuseduserlist"

    def GET(self):
        sql_unused_user = "select * from t_user where f_type = '收费人员' and f_id not in (select f_user_id from t_user_parking) order by f_id"
        unused_user_list = list(pg.db.query(sql_unused_user))

        return json.dumps(unused_user_list)

        

class Parking2UserIndex(pc_app.page):
    """
    收费排班管理页面
    """

    path = "/sort"

    def GET(self):
        sql_street = """select f_id as "Value", f_name as "DisplayText" from t_street"""
        streets = list(pg.db.query(sql_street))
        sql_user = """select f_id as "Value",f_name as "DisplayText" from t_user where f_type='收费人员' """
        users = list(pg.db.query(sql_user))

        return render.rendeHtml("pc/parking2user", users=users,streets=streets,title="未分配车位")

    
class Parking2User(pc_app.page):
    """
    关联车位到某个收费人员
    """
    
    path = "/ajax/mapparking2user"

    def POST(self):
        ret = {
            "error": 1
        }

        try:
            user = isLogin()
        except Exception:
            ret["errorMsg"] = "请选登陆"
            return json.dumps(ret)
        
        data = web.input()

        if not data:
            ret["errorMsg"] = "提交的数据无效啊亲!"
            return json.dumps(ret)


        user_id = data.get("user_id", None)
        parking_ids = data.get("parking_ids", "").split(",")

        if user_id is None:
            ret["errorMsg"] = "无效的用户ID"
            return json.dumps(ret)

        user_id = int(user_id)

        for parking_id in parking_ids:
                pg.db.insert("t_user_parking", f_user_id=user_id, f_parking_id=int(parking_id))

        ret["error"] = 0
        return json.dumps(ret)


class RemoveParking4User(pc_app.page):
    """
    删除用记跟车位的映射关系
    """

    path = "/ajax/removeparking4user"
    
    def POST(self):
        ret = {
            "error": 1
        }

        try:
            user = isLogin()
        except Exception:
            ret["errorMsg"] = "请选登陆"
            return json.dumps(ret)
        
        data = web.input()

        if not data:
            ret["errorMsg"] = "提交的数据无效啊亲!"
            return json.dumps(ret)


        user_id = data.get("user_id", None)
        parking_ids = data.get("parking_ids", "").split(",")

        if user_id is None:
            ret["errorMsg"] = "无效的用户ID"
            return json.dumps(ret)

        user_id = int(user_id)

        for parking_id in parking_ids:
            pg.db.delete("t_user_parking",where="f_user_id=%d and f_parking_id =%d"%(user_id,int(parking_id)))

        ret["error"] = 0
        return json.dumps(ret)
        

class Image(pc_app.page):
    """
    Done Message
    """
    path = "/image/(\w+)"

    def GET(self, key):
        sql = "select * from t_parking_image where f_key = $key"
        images = list(pg.db.query(sql, vars={"key": key}))
        return render.rendeHtml("pc/image", images=images)


if __name__ == '__main__':
    import pdb
    pdb.set_trace()
    sql_units = "select * from t_unit where f_key like 'PC.%%' order by f_index desc"
    units = list(pg.db.query(sql_units))
    models = [u for u in units if u.f_type == u"Model"]

    for m in models:
        m.funcs = [f for f in units if f.f_type == "Func" and f.f_parent_id == m.f_id]

    print models
