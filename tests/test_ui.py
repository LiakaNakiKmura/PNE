# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 21:46:07 2019

@author: LiNaK
"""

# Standard module
import unittest
from unittest.mock import patch
from pathlib import Path
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
from src.dataio.cui import ValueAskCUI
import src.dataio.csvio as csvio
from src.dataio.io_com import (LoadPathDialog, SavePathDialog)
from src.dataio.functional_ui import FixPathAskGenerater

# interface
from src.interface.intfc_com import (ValueAsk)
from src.interface.intfc_com import (Reader, Writer, PathAsk)

@add_msg
class TestCSVIOInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs =((ValueAskCUI, ValueAsk),
                           (csvio.CSVIO, Reader), 
                           (LoadPathDialog, PathAsk),
                           (SavePathDialog, PathAsk),
                           (csvio.CSVIO, Writer)
                           )
@add_msg
class Test_CUI_ValueAsk(unittest.TestCase):
    def test_data_reading(self):
        self.vac = ValueAskCUI()
        if __name__=='__main__':
            '''
            This is only active by main.
            This is irregular test because user interface. Then check by hand.
            '''
            
            inputval = 'input'
            msg = 'Please input "{}" to test {} class.'\
            .format(inputval, self.vac.__class__)
            val = self.vac.get_value(msg)
            self.assertEqual(inputval, val)

@add_msg
class Test_reading(unittest.TestCase):
    def test_data_reading(self):
        self.ddft=DummyDataForTest()
        dummy_path = self.ddft.get_dummy_read_data_path()
        #with patch('src.dataio.io_com.PathDialog.get_load_path')\
        with patch('src.dataio.io_com.LoadPathDialog.get_path')\
        as get_load_path_mock:
            get_load_path_mock.return_value = dummy_path
            cio = csvio.CSVIO()
            data = cio.read('Asking message')
            assert_frame_equal(data, self.ddft.inputdata)


@add_msg
class Test_writing(unittest.TestCase):
    def test_data_writing(self):
        self.ddft=DummyDataForTest()
        dummy_path = self.ddft.get_dummy_write_data_path()
        #with patch('src.dataio.io_com.PathDialog.get_save_path')\
        with patch('src.dataio.io_com.SavePathDialog.get_path')\
        as get_save_path_mock:
            get_save_path_mock.return_value = dummy_path
            cio = csvio.CSVIO()
            cio.write('Asking message', self.ddft.outputdata)
            data = pd.read_csv(dummy_path)
            assert_frame_equal(data, self.ddft.outputdata)


class DummyDataForTest():
    def __init__(self):
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000], 
                      name = 'freq')
        phasenoise_read = Series([-60,-80,-100,-120,-140, -160, -174, -174],
                            name = 'phasenoise')
        phasenoise_write = phasenoise_read + 20
        self.inputdata = pd.concat([freq, phasenoise_read], axis = 1)
        self.outputdata = pd.concat([freq, phasenoise_write], axis = 1)
        
    def get_dummy_read_data_path(self):
        module_path = Path(os.path.abspath(__file__)).parent
        dummy_data_foleder_name = 'dummy_data'
        _dummy_data_file_name = 'test_csv_reader.csv'
        return str(module_path / dummy_data_foleder_name / _dummy_data_file_name)

    def get_dummy_write_data_path(self):
        module_path = Path(os.path.abspath(__file__)).parent
        dummy_data_foleder_name = 'dummy_data'
        _dummy_data_file_name = 'test_csv_writer.csv'
        return str(module_path / dummy_data_foleder_name / _dummy_data_file_name)

@add_msg
class TestFixPathAskGenerater(unittest.TestCase):
    def test_generation(self):
        '''
        1. set dummy path
        2. get class which return fixed path. 
        '''
        dummy_path = self._get_dummy_path()
        fixpathgen = FixPathAskGenerater()
        fixpathgen.set_fixpath(dummy_path)
        PathClass = fixpathgen.generate_class()
        
        self.assertTrue(issubclass(PathClass, PathAsk))
        pathclass = PathClass()
        msg='Nothing'
        
        self.assertEqual(dummy_path, pathclass.get_path(msg))

    def test_init_set(self):
        '''
        1. set dummy path when instance is generated.
        2. get class which return fixed path. 
        '''
        dummy_path = self._get_dummy_path()
        fixpathgen = FixPathAskGenerater(dummy_path)
        PathClass = fixpathgen.generate_class()
        pathclass = PathClass()
        msg='Nothing'
        
        self.assertEqual(dummy_path, pathclass.get_path(msg))

    def test_repeat_generation(self):
        '''
        Fixed path is static.
        If reset dummy path and recreate, new class reflects new dummy path.
        Old class' path doesn't be changed.
        '''
        dummy_path = self._get_dummy_path()
        dummy_path2 = 'dummypath2'
        fixpathgen = FixPathAskGenerater(dummy_path)
        PathClass1 = fixpathgen.generate_class()
        fixpathgen.set_fixpath(dummy_path2)
        PathClass2 = fixpathgen.generate_class()
        
        pathclass1 = PathClass1()
        pathclass2 = PathClass2()
        msg='Nothing'
        
        self.assertEqual(dummy_path, pathclass1.get_path(msg))
        self.assertEqual(dummy_path2, pathclass2.get_path(msg))
        
    def _get_dummy_path(self):
        module_path = Path(os.path.abspath(__file__)).parent
        dummy_data_file_name = 'dummydata.txt'
        return str(module_path / dummy_data_file_name)

if __name__=='__main__':
    unittest.main()