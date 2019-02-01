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
from unittest.mock import patch
import imp

# 3rd party's module

# Original module
from context import src # path setting
from test_utility.unittest_util import cls_startstop_msg as add_msg

# Target class
from src.transaction.pncombiner import PNCombiner

# Support Class
from src.csv_io.csvio import CSVReader
from src.csv_io.csvio import CSVWriter
from src.calc.pncalc import PNCalc
from src.interface.common import (Transaction, Reader, Writer)
from src.interface.calc_data import (PN_TF_Calc)

@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for combining phase noise from each small data.
    """
    def test_interfacre(self):
        # Check using class has interface.
        sub_par_class_pairs = ((PNCombiner, Transaction),
                               (CSVReader, Reader),
                               (CSVWriter, Writer),
                               (PNCalc, PN_TF_Calc)
                               )
        for subc, parc in sub_par_class_pairs:
            self.assertTrue(issubclass(subc, parc))    
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """
        with patch('src.csv_io.csvio.CSVReader') as CSVRMock, patch(
                'src.csv_io.csvio.CSVWriter') as CSVWMock, patch(
                'src.calc.pncalc.PNCalc') as PNCalcMock:     
            
            imp.reload(src.transaction.pncombiner)
            """
            pncombiner MUST be reloaded because patch class is called when 
            pncombiner module is called.
            if not reload, classes imported in pncombiner is not patched.
            """
            
            # Make instance. 
            pnc = PNCombiner()
            pnc.execute()

            # Following class is called when above instance is made.
            CSVRMock.assert_called()
            CSVWMock.assert_called()
            PNCalcMock.assert_called()

if __name__=='__main__':
    unittest.main()