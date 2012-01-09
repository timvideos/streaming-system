#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import math
import random

import mechanize
import cookielib


def _get_output(output):
    for line in output:
        exec(line)
    r = locals()
    del r['output']
    del r['line']
    return r


class TelstraEliteStatus(object):
    """Returns details about the Telstra Elite network strength."""

    username = 'admin'
    password = 'admin'

    def __init__(self):
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.set_handle_referer(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_refresh(False)
        self.login()

    def login(self):
        self.br.open("http://192.168.0.1")
        self.br.open("http://192.168.0.1/login.asp")


        self.br.select_form(name="loginFrm")

        self.br.form["user"]=self.username
        self.br.form["psw"]=self.password

        # Do the luck number
        lucknum = str(int(math.floor(random.random() * 1000000)))
        self.br.form.find_control("lucknum").readonly = False
        self.br.form["lucknum"]=lucknum
        self.br.set_cookie("lucknum=%s" % lucknum)

        self.br.submit(id="LoginButton")

    def __call__(self):
        self.br.open("http://192.168.0.1/index.asp")
        self.br.follow_link(url="content.asp")
        self.br.follow_link(url="logo.asp")

        output = []
        for line in self.br.response().readlines():
            if line.startswith("var "):
                output.append(line[4:-1].replace('//', '#'))
        return _get_output(output)

if __name__ == "__main__":
    import time
    a = TelstraEliteStatus()
    while True:
        print time.time(), a()
        print
        time.sleep(30)
