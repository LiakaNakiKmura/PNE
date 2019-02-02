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
from src.transaction.pncombiner import PNDataReader
from src.transaction.pncombiner import PNDataWriter

#from src.calc.pncalc import PNCalc
from src.transaction.pncombiner import PNCalc

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
                               (PNDataReader, Reader),
                               (PNDataWriter, Writer),
                               (PNCalc, PN_TF_Calc)
                               )
        for subc, parc in sub_par_class_pairs:
            self.assertTrue(issubclass(subc, parc))    
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """

        with patch('src.transaction.pncombiner.PNDataReader') as Reader_Mock,\
        patch('src.transaction.pncombiner.PNDataWriter') as Wruter_Mock,\
        patch('src.transaction.pncombiner.PNCalc') as PNCalc_Mock:
            
            # Make instance. 
            pnc = PNCombiner()
            pnc.execute()
            
            # Following class is called when above instance is made.
            Reader_Mock.assert_called()
            Wruter_Mock.assert_called()
            PNCalc_Mock.assert_called()


class TestCombineRead(unittest.TestCase):
    """
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    """
    def test_readdata(self):
        pass
    

if __name__=='__main__':
    unittest.main()