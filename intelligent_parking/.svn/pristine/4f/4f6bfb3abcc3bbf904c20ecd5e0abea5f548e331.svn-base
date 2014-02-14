#!/usr/bin/env python
#encoding=utf-8

from __future__ import with_statement
from contextlib import closing
import multitask
import socket
import sys
import datetime
import time
import traceback

import os
path = os.getcwd()

# 默认路径
if "intelligent_parking" not in path and "services" not in path:
    path += "/intelligent_parking"

sys.path.append(path)
sys.path.append("..")


# 默认服务路径
if "services" not in path:
    path += "/services"


import pg


def client_handler(sock):
    with closing(sock):
        while True:
            buf = (yield multitask.recv(sock, 1024))
            if not buf:
                break

            data = buf.strip()

            t = time.strftime('%Y%m', time.localtime(time.time()))
            #h = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # self.request is the TCP socket connected to the client
            file_object = open(path + '/log%s.txt' % t, 'a+')
            #file_object.writelines("Received Data:[ip:%s]%s:%s" % (sock, h, data,))

            if not data.startswith("$"):
                break

            datas = data.split(",")
            if not len(datas) == 4:
                break

            channel = datas[1]
            device_code = datas[2]
            parking_state = datas[3][0]
            sql_device = "select * from t_device where f_channel = $channel and f_code = $code"
            device = list(pg.db.query(sql_device, vars={"channel": channel, "code": device_code}))

            if device:
                device = device[0]

            sql_record = "select * from t_monitor_record where f_device_id = $device_id"
            last_record = list(pg.db.query(sql_record, vars={"device_id": device.f_id}))

            sql_command = "select * from t_command where f_is_executed=0 and f_device_id in (select f_id from t_device where f_channel = $channel) limit 1"
            commands = list(pg.db.query(sql_command, vars={"channel": channel}))

            now = datetime.datetime.now()

            # 收费管理时段, 记录地磁设备数据
            if now.hour < 23 or now.hour >= 7:

                # 判断状态变化是否在60秒，忽略60秒内地磁变化
                last_state = parking_state
                if last_record:
                    last_record = last_record[0]
                    if int((now - last_record.f_stamp).total_seconds()) >= 60:  # 忽略状态变化在60妙以内的数据
                        last_state = last_record.f_state
                        last_record.f_data = data
                        last_record.f_stamp = datetime.datetime.now()
                        if parking_state is not None:
                            last_record.f_state = parking_state

                        # 状态变更时，记录数据
                        if str(last_state) != str(parking_state):
                            if parking_state == "0":  # 更新车辆离开时间
                                last_record.f_leave_stamp = now
                            else:
                                last_record.f_parking_stamp = now
                                last_record.f_leave_stamp = None

                            pg.db.update("t_monitor_record", where="f_device_id=%s" % device.f_id, **last_record)

                            pg.his("t_monitor_record", **last_record)

                else:
                    if parking_state is not None and parking_state == "1":
                        last_record = {"f_device_id": device.f_id, "f_device_code": device.f_code, "f_data": data, "f_parking_stamp": now, "f_stamp": now, "f_parking_id": device.f_parking_id, "f_parking_code": device.f_parking_code, "f_leave_stamp": None, "f_state": parking_state, "f_street_id": device.f_street_id}
                        pg.db.insert("t_monitor_record", **last_record)
                        pg.his("t_monitor_record", **last_record)

                # create message
                message = {"f_content": None, "f_device_id": device.f_id, "f_device_code": device_code, "f_create_time": datetime.datetime.now(), "f_done_time": None, "f_parking_id": device.f_parking_id, "f_parking_code": device.f_parking_code, "f_is_done": 0, "f_done_user_id": None, "f_state": parking_state, "f_street_id": device.f_street_id}
                if str(last_state) != str(parking_state):
                    if parking_state == "0":
                        message["f_content"] = U"车位[%s]有车离开" % device.f_parking_code
                    else:
                        message["f_content"] = U"车位[%s]有车进入" % device.f_parking_code

                    pg.db.insert("t_message", **message)

            # send reset command
            if commands:
                for c in commands:
                    c.f_is_executed = 1
                    c.f_executed_time = datetime.datetime.now()
                    pg.db.update("t_command", where="f_id=%d" % c.f_id, ** c)
                    file_object.writelines("Execute Command :%s" % c.f_command)

                    yield multitask.send(sock, c.f_command)

            file_object.close()
            yield multitask.send(sock, "successful")


def echo_server(hostname, port):
    addrinfo = socket.getaddrinfo(hostname, port,
                                  socket.AF_INET,
                                  socket.SOCK_STREAM)

    (family, socketype, porot, canonname, sockaddr) = addrinfo[0]
    with closing(socket.socket(family,
                               socketype,
                               porot)) as sock:
        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_REUSEADDR, 1)
        sock.bind(sockaddr)
        sock.listen(5)
        while True:
            multitask.add(client_handler((
                yield multitask.accept(sock))[0]))

if __name__ == '__main__':
    hostname = '0.0.0.0'
    port = 1111

    if len(sys.argv) > 1:
        hostname = sys.argv[1]

    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    multitask.add(echo_server(hostname, port))

    try:
        multitask.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        # 输出错误信息
        msg = traceback.print_exc()
        print "数据接收服务发生错误，详细信息: %s" % msg
