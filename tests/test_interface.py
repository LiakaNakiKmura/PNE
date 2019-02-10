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

from src.interface.intfc_com import (Transaction, Reader, Writer, PathAsk)
#from src.interface.calc_data import (PN_TF_Calc)

@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for interface
    """
    def test_interface_method(self):
        # Test interface has abstract method.
        class_method_pairs=((Transaction,'execute'),
                            (Reader,'read'),
                            (Writer,'write'),
                            (PathAsk,'get_path')
                            #(PN_TF_Calc,'calc')                   
                            )
        for cl, mth in class_method_pairs:
            self.assertTrue(callable(getattr(cl, mth)))

    

if __name__=='__main__':
    unittest.main()