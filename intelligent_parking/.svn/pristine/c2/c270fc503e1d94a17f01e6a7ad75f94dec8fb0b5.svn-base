#!/usr/bin/env python
#encoding=utf-8

import os
import sys
import web
from cont import *
from mobile import mobile_app
from pc import pc_app

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)
#    os.chdir(abspath)
urls = (
    '/', 'Main',
    '/download', "Download",
    '/mobile', mobile_app,  # 'MobileLogin',
    '/pc', pc_app,
)

web.config.debug = False
application = web.application(urls, globals())

#import web_db
#store = web.session.DBStore(web_db.db, 'sessions')
#session = web.session.Session(application, store, initializer={'count': 0})
#web.config.session_ = session


session = web.session.Session(application, web.session.DiskStore('sessions'))


def session_hook():
    web.ctx.session = session


application.add_processor(web.loadhook(session_hook))

if __name__ == '__main__':
    web.config.debug = False
    application.run()
else:
    print 'bigzhu wsgi'
    web.config.debug = False
    application = application.wsgifunc()
