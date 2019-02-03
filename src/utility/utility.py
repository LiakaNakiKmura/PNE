# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 18:11:14 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  

def singleton_decorator(class_):
    class class_w(class_):
        _instance = None
        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(
                class_w, class_).__new__(class_, *args,**kwargs)
                class_w._instance._sealed = False
            return class_w._instance
        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
            class_w.__name__ = class_.__name__
    return class_w
    pass