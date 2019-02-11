# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 22:51:07 2019

@author: LiNaK
"""

# Standard module
from tkinter import filedialog

# 3rd party's module

# Original module
from context import src # path setting

# interface
from src.interface.intfc_com import PathAsk

class PathDialog(PathAsk):
    def __init__(self):
        pass
    
    def get_path(self, message):
        return filedialog.askopenfilenames(title = message) 

if __name__ == '__main__':
    pth_dia = PathDialog()
    print(pth_dia.get_path('Reading Test'))