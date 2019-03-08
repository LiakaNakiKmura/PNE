# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 18:08:17 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module
import numpy as np
from numpy.testing import assert_array_almost_equal

# Original module  
from context import src # path setting

# Target class
from src.utility.utility import singleton_decorator
from src.utility.calc import MagLogUtil

from testing_utility.unittest_util import cls_startstop_msg as add_msg


class Signletone_test_base():
    """
    This class is inirated to Test class. _cls: class variable must be defined
    in inherated class as target singleton class.
    Test for singleton decorator.
    Sigleton decorator decorates class as singleton. Decorated class can 
    generate 'only' one instance. So, generated instance is all the same 
    instance.
    """
    
    _cls = None # target class defined inherated test class.
    
    def setUp(self):
        self._inst = self._cls()
    
    def tearDown(self):
        del self._inst

    def test_some_cls(self):
        """
        Test the generated instances from singleton class are the same.
        Test the generated instance from singleton class is different from 
        other instance.
        Check a generation of class.
        """
        class Dummy():pass
    
        a = self._cls()
        b = self._cls()
        d = Dummy()
        
        self.assertTrue(isinstance(a, self._cls))
        self.assertFalse(isinstance(a, Dummy))
        self.assertEqual(a, b)
        self.assertNotEqual(a, d)


@singleton_decorator
class Mock_cls():pass # mock class for testing singleton decorator.

@add_msg
class Test_singleton_decorator(Signletone_test_base, unittest.TestCase):
    """
    Test the singleton decorator.
    Mock class is defined for singleton
    """
    _cls = Mock_cls    

class Inheration_test_base():
    """
    Test for iheration of classes.
    _sub_par_class_pairs is set as ((sub class1, super class1), (subclass2,
    super class2),...)
    """
    _sub_sup_class_pairs = ((None,None))

    def test_interfacre(self):
        # Check using class has interface.
        for subc, supc in self._sub_sup_class_pairs:
            self.assertTrue(issubclass(subc, supc))

class Dummy1():pass
class Dummy2(Dummy1):pass
class Dummy3():pass
class Dummy4(Dummy3, Dummy1):pass

@add_msg
class Test_inheration(Inheration_test_base,unittest.TestCase):
    _sub_sup_class_pairs = ((Dummy2,Dummy1),
                            (Dummy4,Dummy3),
                            (Dummy4,Dummy1),
                            )

@add_msg
class TestMagLog_utility(unittest.TestCase):
    def setUp(self):
        self._make_maglog_data()
    
    
    def _make_maglog_data(self):
        log10data_list = [20,10,0,-10,-20]
        log10data = np.array(log10data_list)
        log20data = log10data*2
        log10_one_data = 30
        nulldata = []
        
        magdata_list = [100, 10, 1, 0.1, 0.01]
        magdata = np.array(magdata_list)
        mag_one_data = 1000
        
        N10 = 10
        N20 = 20
        
        self.data_list = (log10data_list,magdata_list, N10)
        self.data_10 = (log10data, magdata, N10) 
        self.data_20 = (log20data, magdata, N20)
        self.data_single_num = (log10_one_data, mag_one_data, N10)
        self.data_null = (nulldata, nulldata, N10)
    
    def test_log2Mag(self):
        mlu = MagLogUtil()
        for indata, outdata, NUM in [self.data_list, self.data_10, 
                                     self.data_20, self.data_single_num,
                                     self.data_null]:
            assert_array_almost_equal(outdata, mlu.log2mag(indata, NUM))
        self.assertRaises(TypeError, mlu.log2mag, 'a',)
    
    def test_mag2log(self):
        mlu = MagLogUtil()
        input_data = [self.data_list, self.data_10, self.data_20, 
                      self.data_single_num, self.data_null]

        for outdata, indata, NUM in input_data:
            assert_array_almost_equal(outdata, mlu.mag2log(indata, NUM))
        self.assertRaises(TypeError, mlu.mag2log, 'a',)
        
    def test_mag_deg2comp(self):
        mlu = MagLogUtil()
        self._random_data = {}
        amp = 'amp'
        deg = 'phase_deg'
        comp = 'complex'
        
        self._random_data[amp] = [7283, 6003, 4485, 3561, 6909]
        self._random_data[deg]=[55, 280, 57, 133, 271]
        self._random_data[comp] = [4177.35718594467+5965.88433855673j, 
                         1042.41001053456-5911.80094133229j,
                         2442.7060720424+3761.43749723523j,
                         -2428.59616018256+2604.35053146586j,
                         120.578676075171-6907.94772583551j]
        
        self._easy_data={}
        self._easy_data[amp]=[0, 1, 1, 10]
        self._easy_data[deg]=[0, 180, 90, 540]
        self._easy_data[comp] =[0+0j, -1+0j, 0+1j, -10+0j]
        
        for data in [self._random_data, self._easy_data]:
            calced = mlu.magdeg2comp(data[amp], data[deg])
            assert_array_almost_equal(data[comp], calced)
            
    def test_logx_y_liner_interpolate(self):
        #test linear interpolatinon for logx vs y.
        mlu = MagLogUtil()
        length = 4
        freq1 = [10.**(2*i) for i in range(length)]
        val1 = [-60.-20*i*2 for i in range(length)]
        
        intter = int(length/3)+1
        # Add invilid value to front and back.
        freq1 =  [1.E-1, -10, np.nan] + freq1[:intter] +\
        [1.E9, 0] + freq1[intter:] + [1.E9, -10]
        val1 = [np.nan, -200, -300] + val1[:intter] +\
        [np.nan, -60] + val1[intter:] + [np.nan, -200]

        freq2 = [10.**(i) for i in range(2*length-1)]
        val2 = [-60. -20*i for i in range(2*length-1)]
        # outband return the nan
        freq2 = [1-1E-3] + freq2 + [10.**(2*(length-1))+1E+3]
        val2 = [np.nan] + val2 + [np.nan]
        
        func = mlu.ylogx_interpolite(freq1, val1,bounds_error = False)
        assert_array_almost_equal(val2, func(freq2))            
    
if __name__=='__main__':
    unittest.main()     