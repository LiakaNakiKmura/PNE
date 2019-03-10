# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 21:46:07 2019

@author: LiNaK
"""

# Standard module
import unittest
from unittest.mock import patch

# 3rd party's module

# Original module  
# utlities.
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import (Inheration_test_base)

# target class
from src.dataio.cui import ValueAskCUI

# interface
from src.interface.intfc_com import (ValueAsk)
@add_msg
class TestCSVIOInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs =((ValueAskCUI, ValueAsk),
                           )
@add_msg
class Test_CUI_ValueAsk(unittest.TestCase):
    def test_data_reading(self):
        self.vac = ValueAskCUI()
        if __name__=='__main__':
            '''
            This is only active by main.
            This is irregular test because user interface.
            Then check by hand.
            '''
            
            inputval = 'input'
            msg = 'Please input "{}" to test {} class.'\
            .format(inputval, self.vac.__class__)
            val = self.vac.get_value(msg)
            self.assertEqual(inputval, val)
        

if __name__=='__main__':
    unittest.main()