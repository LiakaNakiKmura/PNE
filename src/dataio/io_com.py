# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 22:51:07 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module
from context import src # path setting

# interface
from src.interface.intfc_com import PathAsk

class PathDialog(PathAsk):
    def get_path(self):
        pass