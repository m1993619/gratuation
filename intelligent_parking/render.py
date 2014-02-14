#encoding=utf-8
import web
from web.contrib.template import render_jinja
import os
import random
path = os.getcwd()
import public
public.setUTF8()

import time

# 默认模版路径
if "intelligent_parking" not in path:
    path += "/intelligent_parking"

class my_render_jinja:
    """Rendering interface to Jinja2 Templates

    Example:

        render= render_jinja('templates')
        render.hello(name='jinja2')
    """
    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})
        self.suffix = kwargs.pop('suffix')

        from jinja2 import Environment, FileSystemLoader
        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs), extensions=extensions)
        self._lookup.globals.update(globals)

    def __getattr__(self, name):
        # Assuming all templates end with .html
        #path = name + '.css'
        path = name + self.suffix
        t = self._lookup.get_template(path)
        return t.render

#模板上下文变量, 所有模板都会有这些变量
globals = {}

#添加上下文环境变量
# addGlobalVar(hello="world", key="value")
def addGlobalVar(**args):
    globals.update(args)

#删除上下文变量
# delGlobalVar("hello", "key")
def delGlobalVar(*keys):
    for key in keys:
        if globals.has_key(key):
            del globals[key]

#获取上下文变量
# getGlobalVar("hello", default_value)
def getGlobalVar(key, default):
    return globals.get(key, default)

def rendeHtml(template, **args):
    web.header('Content-Type', 'text/html')

    globals['v'] = time.time()
    globals['cookies'] = web.cookies()

    render = render_jinja(path + '/templates', encoding='utf-8', globals=globals)
    print path + '/templates'
    return getattr(render, template)(**args)

if __name__ == '__main__':
    print os.getcwd()
