# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 20:48:55 2019

@author: LiNaK
"""

# Standard module
import unittest
from unittest.mock import patch
from pathlib import Path
import sys
import os

# 3rd party's module
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from pandas.testing import assert_frame_equal

# Original module  
# utlities.
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import (Inheration_test_base)

# target class
import src.dataio.csvio as csvio
from src.dataio.csvio import CSVIO
from src.dataio.io_com import (PathDialog)

# interface
from src.interface.intfc_com import (Reader, Writer, PathAsk)


@add_msg
class TestCSVIOInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs =((csvio.CSVIO, Reader), 
                           (PathDialog, PathAsk),
                           (csvio.CSVIO, Writer)
                           )
    raise()


@add_msg
class Test_rading(unittest.TestCase):
    def test_data_rading(self):
        self.ddft=DummyDataForTest()
        dummy_path = self.ddft.get_dummy_data_path()
        with patch('src.dataio.io_com.PathDialog.get_path') as get_path_mock:
            get_path_mock.return_value = dummy_path
            cio = csvio.CSVIO()
            data = cio.read('Asking message')
            assert_frame_equal(data, self.ddft.inputdata)

class DummyDataForTest():
    def __init__(self):
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000], 
                      name = 'freq')
        phasenoise = Series([-60,-80,-100,-120,-140, -160, -174, -174],
                            name = 'phasenoise')
        self.inputdata = pd.concat([freq, phasenoise], axis = 1)
        
    def get_dummy_data_path(self):
        module_path = Path(os.path.abspath(__file__)).parent
        dummy_data_foleder_name = 'dummy_data'
        _dummy_data_file_name = 'test_csv_reader.csv'
        return str(module_path / dummy_data_foleder_name / _dummy_data_file_name)

if __name__=='__main__':
    unittest.main()