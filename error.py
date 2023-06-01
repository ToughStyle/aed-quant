# -*- coding:utf-8 -*-

"""
错误信息

Author: CyberQuant
Date:   2023/06/01
"""


class Error:

    def __init__(self, msg):
        self._msg = msg

    @property
    def msg(self):
        return self._msg

    def __str__(self):
        return str(self._msg)

    def __repr__(self):
        return str(self)
