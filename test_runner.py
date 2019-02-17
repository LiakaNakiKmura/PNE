# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 21:47:24 2018
This is for CI testing.
Call all tests in test folder which name is stated with 'test_'
If this module is not __main__, do nothing

@author: LiNaK
"""
import unittest 
test_suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
unittest.TextTestRunner().run(test_suite)
