# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 21:34:32 2019

@author: LiNaK
This is the test for interface classes which has specific abstract method.

"""

# Standard module
import unittest
from unittest.mock import patch

# 3rd party's module

# Original module  
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg

from src.interface.intfc_com import (Transaction, Reader, Writer, PathAsk, 
                                     ValueAsk, TF_Maker)

class TestForMethodExist():
    '''
    Check that class has specified method for especially abstract class.
    _class_method_pairs is set as ((class1, mrthod1),(class2, method2)...)
    _class_attr_pairs is set as ((class1, attribute1),(class2, attribute2)...)
    '''
    _class_method_pairs =(())
    _class_attr_pairs = (())
    
    def test_class_method_pairs(self):
        for cl, mth in self._class_method_pairs:
            self.assertTrue(callable(getattr(cl, mth)))
    
    def test_class_attr_pairs(self):
        for cl, attr in self._class_attr_pairs:
            self.assertTrue(hasattr(cl, attr))

@add_msg
class TestCombinePN(TestForMethodExist, unittest.TestCase):
    _class_method_pairs=((Transaction,'execute'),
                         (Reader,'read'),
                         (Writer,'write'),
                         (PathAsk,'get_path'),
                         (ValueAsk, 'get_value'),
                         (TF_Maker, 'get_tf')
                         )

if __name__=='__main__':
    unittest.main()