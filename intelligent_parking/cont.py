#!/usr/bin/env python
#encoding=utf-8
import render
import web
import json
import time
import hashlib

render.addGlobalVar(version=3)

class Main:
    def GET(self):
        os = web.input().get("os", "pc")
        version = int(web.input().get("version", "0"))

        web.setcookie(name='os', value=os, domain=None, secure=False)

        v = render.getGlobalVar("version", 0)

        if version < v and os != "pc":
            raise web.seeother("/download")

        if os == "pc":
            raise web.seeother("/pc/login")
        else:
            return render.rendeHtml("mobile/main", os=os)

class Download:
    """
    客户端下载
    """
    def GET(self):
        return render.rendeHtml("mobile/download")

if __name__ == '__main__':
    pass