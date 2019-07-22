# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 20:56:22 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_allclose
from pandas import DataFrame, Series
from pandas.testing import assert_series_equal, assert_frame_equal
from scipy import signal

# Original module  
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg 

# Target class
from src.interface.intfc_com import TF_Maker
from src.calc.transfer_function import LCRLPF
from src.calc.transfer_function import TimeDomainConv


class TestFilterTF(unittest.TestCase):
    '''
    This is the test for transfer function. Filters for PLL.
    '''
    def test_inheratance(self):
        self.assertTrue(issubclass(LCRLPF, TF_Maker))

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

if __name__=='__main__':
    unittest.main()