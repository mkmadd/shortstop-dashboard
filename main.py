# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:42:16 2015

@author: Administrator
"""

import bottle
import os
import re

ROW_RE = re.compile('<span>(.*?)</span>')
DOCUMENT_NAME = 'SSA Doc' # google docs name
username = os.environ['GOOG_UID'] # google/gmail login id
passwd = os.environ['GOOG_PWD'] # google/gmail login password


@bottle.route('/')
def home():
    return '<html><head></head><body>Hello world!</body></html>'

app = bottle.default_app()
