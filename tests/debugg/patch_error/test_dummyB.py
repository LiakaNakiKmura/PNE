# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 20:12:40 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module

# Original module  
from sample import SampleB
#import sample

if __name__=='__main__':
    import os
    print('run file = {}'.format(os.path.basename(__file__)))
    unittest.main()
