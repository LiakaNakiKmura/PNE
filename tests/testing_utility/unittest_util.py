# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 19:04:42 2017
Utilitys for unit testing 

@author: sasamura
"""

import types

def startstop_msg(func, comment=""):
    # This is the decorator to print that a wrapped function is called and 
    # finished. Unittest function is decorated this function to check the
    # timing for debugging.
    def wrap(*args, **kwds):
        def prt_msg(msg):
            # print msg with line and function name.
            print ('-'*3 + comment+ func.__name__ + ' ' +  msg + '-'*3)
        prt_msg('is started')
        func(*args, **kwds)
        prt_msg('is completed')
    return wrap

def cls_startstop_msg(class_):
    '''
    The decorator decrating unittest subclass.
    When unittest is excuted start, stop message is added to test method. 
    '''
    class class_w(class_):
        for method in dir(class_):
            attr = getattr(class_, method)
            if method[:4] == 'test' and type(attr) is types.FunctionType :
                # if method name is starte with 'test', add message.
                new_method = startstop_msg(attr, class_.__name__+'.')
                setattr(class_, method, new_method)
    return class_w


if __name__ == '__main__':
    @startstop_msg
    def func():
        print('a')
        
    func()
    # print like follwing
    # ----------func is started----------
    # a
    # ----------func ie completed----------
    
    @cls_startstop_msg
    class cls():
        test_value = 4
        def A(self):
            print('A')
            
        def test_B(self):
            print('B')
            
    c = cls()
    # print(c.__dir__())
    c.A()
    # A
    c.test_B()
    #  ----------test_B is started----------
    # B
    # ----------test_B ie completed----------