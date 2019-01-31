# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 22:58:00 2019

@author: LiNaK
"""

"""
Tests of pncombiner callables.
because import 
"""

# Standard module
import unittest
import imp
from unittest.mock import patch

# 3rd party's module
from numpy.testing import (assert_array_equal, assert_array_almost_equal, 
                           assert_almost_equal)
from numpy.random import randint

# Original module
from context import src # path setting
from test_utility.unittest_util import cls_startstop_msg as add_msg

# Target class
from src.transaction.pncombiner import PNCombiner

# Support Class
from src.csv_io.csvio import CSVReader
from src.csv_io.csvio import CSVWriter
from src.calc.pncalc import PNCalc

@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for combining phase noise from each small data.
    """
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """
        with patch('src.csv_io.csvio.CSVReader') as CSVR, patch(
                'src.csv_io.csvio.CSVWriter') as CSVW, patch(
                'src.calc.pncalc.PNCalc') as PNCalc:     
            
            imp.reload(src.transaction.pncombiner)
            """
            pncombiner MUST be reloaded because patch class is called when 
            pncombiner module is called.
            if not reload, classes imported in pncombiner is not patched.
            """
            
            pnc = PNCombiner()
            pnc.execute()
            

            
            CSVR.assert_called()
            CSVW.assert_called()
            PNCalc.assert_called()
            """            
            instance = MockClass.return_value
            instance.method.return_value = 'foo'
            assert Class() is instance
            assert Class().method() == 'foo'
            """
        

if __name__=='__main__':
    unittest.main()