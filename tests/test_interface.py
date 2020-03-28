# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 21:34:32 2019

@author: LiNaK
This is the test for interface classes which has specific abstract method.

"""

# Standard module
import unittest

# 3rd party's module

# Original module  
from context import src # path setting

class TestForMethodExist():
    '''
    Check that class has specified method for especially abstract class.
    _class_method_pairs is set as ((class1, mrthod1),(class2, method2)...)
    _class_attr_pairs is set as ((class1, attribute1),(class2, attribute2)...)
    '''
    _class_method_pairs =(())
    _class_attr_pairs = (())
    
    def test_class_method_pairs(self):
        istype =lambda cl,m: self.assertTrue(callable(getattr(cl,m)))
        self.check_sth_in_cls(self._class_method_pairs, istype)
    
    def test_class_attr_pairs(self):
        istype =lambda cl,a: self.assertTrue(hasattr(cl,a))
        self.check_sth_in_cls(self._class_attr_pairs, istype)
    
    def check_sth_in_cls(self, cls_sth_pairs, istype):
        for cl, sth in cls_sth_pairs:
            if isinstance(sth, list) or isinstance(sth, tuple):
                for s in sth:
                    istype(cl, s)
            else:
                istype(cl, sth)
        pass
    
    

if __name__=='__main__':
    unittest.main()