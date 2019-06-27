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
    
    def get_load_path(self, message):
        return filedialog.askopenfilename(title = message) 
    
    def get_save_path(self, message):
        return filedialog.asksaveasfilename(title = message) 


if __name__ == '__main__':
    import tkinter
    root=tkinter.Tk() #python3
    #root.withdraw()
    pth_dia = PathDialog()
    print(pth_dia.get_load_path('Reading Test'))
    root.quit()
    root.mainloop()
    root.quit()