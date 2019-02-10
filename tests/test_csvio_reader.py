# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 20:48:55 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module

# Original module  
# utlities.
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import (Inheration_test_base)

# target class
# from src.dataio.csvio import (CSVIO)
import src.dataio.csvio as csvio
from src.dataio.io_com import (PathDialog)

# interface
from src.interface.intfc_com import (Reader, Writer, PathAsk)


@add_msg
class TestCombinePNInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs =((csvio.CSVIO, Reader), (PathDialog, PathAsk))
 
class Test_rading(unittest.TestCase):
    pass

if __name__=='__main__':
    unittest.main()