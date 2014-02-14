#!/usr/bin/env python
#encoding=utf-8
import web


def loginUser(uid, account=""):
    """
    标记用户为已登陆状态

    Arguments:
    - `uid`:用户id
    - `account`:帐号
    """
    web.setcookie(name='mobile_user_id', value=uid, domain=None, secure=False)
    web.setcookie(name='mobile_user_account', value=account, domain=None, secure=False)


def mobileLoginRequired(func):
    """
    手机登陆验证, 保护需要登陆的页面

    Arguments:
    - `func`:
    """

    def wapper(*args, **kwargs):
        user = web.cookies().get("mobile_user_id", None)
        if user is None:
            raise web.seeother("/login")
            pass
        return func(*args, **kwargs)

    return wapper


def getUserId():
    """
    返回已登陆用户的ID
    """
    return web.cookies().get("mobile_user_id")



def getUserAccount():
    """
    返回已登陆用户的帐号
    """
    return web.cookies().get("mobile_user_account")
