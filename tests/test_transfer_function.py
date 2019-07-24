# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 20:56:22 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from pandas import DataFrame, Series
from pandas.testing import assert_series_equal, assert_frame_equal
from scipy import signal

# Original module  
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg 

# Target class
from src.interface.intfc_com import TF_Maker
from src.calc.transfer_function import LCRLPF, UnitManger, TimeDomainConv

@add_msg
class TestFilTF():
    '''
    This is the test for transfer function. Filters for PLL.
    '''
    TargetClass = TF_Maker
    parameter = {'C':1e6, 'L': 10e6, 'R':100}
    den = np.array([])
    num = np.array([])
    
    def setUp(self):
        self._reshape_num_den()
    
    def test_inheratance(self):
        self.assertTrue(issubclass(self.TargetClass, TF_Maker))
    
    def test_get_transferfunction(self):
        target = self.TargetClass()
        target.set_parameter(**self.parameter)
        lti = target.get_tf()
        assert_array_equal(lti.den, self.den)
        assert_array_equal(lti.num, self.num)
    
    def _reshape_num_den(self):
        norm = self.den[0]
        self.den =self.den/norm
        self.num =self.num/norm

@add_msg
class TestLCRLPF(TestFilTF, unittest.TestCase):
    TargetClass = LCRLPF
    
    C = 1e6 #[pF]
    L = 10e6 #[uH]
    R = 100 #[Ohm]
    parameter = {'C':C, 'L': L, 'R':R}
    num = np.array([1])
    den = np.array([L*1e-6*C*1e-12, R*C*1e-12, 1])
    for p in [C, L, R]:
        del(p)

@add_msg
class TestTimeDomainConv(unittest.TestCase):
    def test_step_responce(self):
        tau = 1e-3
        tf = signal.TransferFunction([1],[tau, 1, 0])
        # This is the multiple of step function and Low pass fiter transfer 
        # function. 1/s * 1/(1+tau*s)
        
        # laplace trnasorm of  y = u(t) - e^(t/tau). step response of LPF.
        td_func = lambda t: 1 - np.exp(-t/tau)
        tdc = TimeDomainConv()
        
        t_in = np.linspace(0, tau)
        
        tdc.set_tf(tf)
        tdc.set_time_arry(t_in)
        t_out, y= tdc.get_td_data()
        
        '''
        # Following is used for debug the data.
        import matplotlib.pyplot as plt
        plt.plot(t_out, td_func(t_out))
        plt.plot(t_out, y)
        '''
        
        assert_array_almost_equal(y, td_func(t_out), decimal=7)
        
@add_msg
class TestUnitManager(unittest.TestCase):
    def setUp(self):
        self.um = UnitManger()
    
    def test_get_prefix_num(self):
        kinds_var_pairs = {'R':1, 'L': 1e-6, 'C': 1e-12}
        for kind, var in kinds_var_pairs.items():
            self.assertEqual(self.um.get_prefix_num(kind), var)

if __name__=='__main__':
    unittest.main()