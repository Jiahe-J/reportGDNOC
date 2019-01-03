#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/11/22
"""
import base64


# 保存base64编码为本地文件
def save_base64(imgstr, filename):
    with open('utils/export_docx/image/' + filename, 'wb') as f:
        f.write(base64.b64decode(imgstr.split('data:image/png;base64,')[1]))
