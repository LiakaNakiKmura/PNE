# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 20:56:22 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module
import numpy as np
from numpy.testing import assert_array_almost_equal
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
    def test_a(self):
        import matplotlib.pyplot as plt
        tau = 1e3
        tf = signal.TransferFunction([1],[1/tau, 1])
        # laplace trnasorm of  y = e^(t/1000)
        td_func = lambda t, u: np.exp(-t/tau)/tau*u
        tdc = TimeDomainConv()
        
        t_in = np.linspace(0, 1/tau)
        u = np.ones_like(t_in)
        
        tdc.set_tf(tf)
        tdc.set_init_arry(u)
        tdc.set_time_arry(t_in)
        t_out, y, x = tdc.get_td_data()
        #assert_array_almost_equal(y, td_func(t_out, u))
        #plt.plot(t_out, td_func(t_out, u))
        #plt.plot(t_out, y)
        #FIXME
        


if __name__=='__main__':
    unittest.main()