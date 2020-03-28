# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 20:12:25 2019

@author: LiNaK
"""

# Standard module
import unittest
from unittest.mock import patch

# 3rd party's module

# Original module  
#from sample import SampleA, SampleB
import sample
from testing_utility.unittest_util import cls_startstop_msg as add_msg

@add_msg
class TestA(unittest.TestCase):
    def test_sampling(self):
        
        def side_effect_func():
            print('mocked')
        with patch('sample.SampleB.funcb') as func:
            func.side_effect = side_effect_func
            s = sample.SampleA()
            s.funca()



if __name__=='__main__':
    import os
    print('run file = {}'.format(os.path.basename(__file__)))
    unittest.main()