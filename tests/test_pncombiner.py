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

# 3rd party's module
import pandas as pd
from pandas import Series, DataFrame
from pandas.testing import assert_series_equal, assert_frame_equal

import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

# Original module


# Target class
from src.transaction.pncombiner import (PNCombiner,PNDataReader, PNDataWriter, 
                                        PNCalc, PNDataBase, PNPrmtrMng,
                                        IndivDataBase)

# utlities.
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import (Signletone_test_base, Inheration_test_base)
from test_interface import TestForMethodExist

# interface
from src.interface.intfc_com import (Transaction, Reader, Writer)
import src.interface.intfc_com as intfc_com
#from src.interface.calc_data import (PN_TF_Calc)

# tool class
from src.dataio.csvio import (CSVIO)


@add_msg
class TestCombinePNInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs = ((PNCombiner, Transaction),
                               (PNDataReader, Transaction),
                               (PNDataWriter, Transaction),
                               (PNCalc, Transaction)
                               )


@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for combining phase noise from each component data.
    """
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """

        with patch('src.transaction.pncombiner.PNDataReader') as Reader_Mock,\
        patch('src.transaction.pncombiner.PNDataWriter') as Writer_Mock,\
        patch('src.transaction.pncombiner.PNCalc') as PNCalc_Mock:
            
            # Make instance. 
            pnc = PNCombiner()
            pnc.execute()
            
            # Following class is called when above instance is made.
            Reader_Mock.assert_called()
            Writer_Mock.assert_called()
            PNCalc_Mock.assert_called()
            del Reader_Mock
            
    def test_database_method(self):
        # Test interface has abstract method.
        method_names=('set_noise','get_noise', 'set_transfer_func',
                      'get_transfer_func', 'set_combined_noise',
                      'get_combined_noise')
        for  mth in method_names:
            self.assertTrue(callable(getattr(PNDataBase, mth)))

@add_msg
class TestIndivisualDataBase(TestForMethodExist, unittest.TestCase):
    _class_method_pairs=((IndivDataBase,'set_data'),
                         (IndivDataBase,'get_data')
                         )
    _class_attr_pairs = ((IndivDataBase, 'index_freq'),
                         (IndivDataBase, 'index_val')
                         )

@add_msg
class TestPNparameter(unittest.TestCase):
    
    def test_parameter_exist(self):
        '''
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = PNPrmtrMng()
        
        pn = Parameter_Names()
        attrnames = pn.get_parameter_names()
        for n in attrnames:
            prmtr = getattr(pnpm,n)
            self.assertTrue(isinstance(prmtr, str))
            self.assertTrue(0<len(prmtr))
            self.assertRaises(AttributeError, setattr, *(pnpm, n, 'a'))
            # Raise error if property value is changed.

    def test_data_terms_exist(self):
        '''
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = PNPrmtrMng()
        
        pn = Parameter_Names()
        attrnames = pn.get_data_terms()
        for n in attrnames:
            parameter = getattr(pnpm,n)
            self.assertTrue(isinstance(parameter, str))
            self.assertTrue(0<len(parameter))
            self.assertRaises(AttributeError, setattr, *(pnpm, n, 'a'))
            # Raise error if property value is changed.
            
            pnpm.get_index(parameter, pn.data_index_freq)
            pnpm.get_index(parameter, pn.data_index_value)
            
    def test_file_message_exist(self):
        '''
        Test of Parameter message for reading data.
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = PNPrmtrMng()
        
        pn = Parameter_Names()
        msg_parameters = {'r': pn.get_read_msg_parameters(),
                          'w':  pn.get_write_msg_parameters()}
        for usage, name_msg_pairs in msg_parameters.items():
            for name in name_msg_pairs :
                prmtr = getattr(pnpm,name) 
                prmtr_msg = pnpm.get_message(usage, prmtr)
                self.assertTrue(isinstance(prmtr_msg, str))
                self.assertTrue(0<len(prmtr_msg))
        

class Parameter_Names():
    _names = ['ref', 'vco', 'pd']
    _reading_msg_names = ['ref', 'vco', 'pd', 'open_loop_gain']
    _reading_lists = ['ref', 'vco', 'pd', 'open_loop_gain']
    _writing_msg_names = ['total']
    _writing_lists = ['total']
    _data_terms = ['noise', 'tf', 'combpn']
    data_index_freq = 'freq'
    data_index_value = 'val'
    # Data kinds for database.
    
    def __init__(self):
        self.pnpm = PNPrmtrMng()
    
    def get_parameter_names(self):
        return self._names
    
    def get_read_msg_parameters(self):
        return self._reading_msg_names

    def get_write_msg_parameters(self):
        return self._writing_msg_names
    
    def get_data_terms(self):
        return self._data_terms
    
    def get_read_msg_dict(self):
        prmtrs = [getattr(self.pnpm, n) for n in self._reading_msg_names]
        return {prmtr: self.pnpm.get_message('r', prmtr) for prmtr in prmtrs}
    
    def get_reading_list(self):
        return [getattr(self.pnpm, name) for name in self._reading_lists]
 
    def get_write_msg_dict(self):
        prmtrs = [getattr(self.pnpm, n) for n in self._writing_msg_names]
        return {prmtr: self.pnpm.get_message('w', prmtr) for prmtr in prmtrs}
    
    def get_writing_list(self):
        return [getattr(self.pnpm, name) for name in self._writing_lists]
    

      

@add_msg
class Test_database_as_singleton(Signletone_test_base, unittest.TestCase):
    """
    Test PNDataBase is singleton.
    """
    _cls = PNDataBase


class UsingPNDataBase(object):
    '''
    Setting for data base 
    '''
    def setUp(self):        
        self.pndb = PNDataBase()
    
    def tearDown(self):
        self.pndb.reflesh_all()
        '''
        reflesh PNDataBase for next test.
        '''

@add_msg  
class Test_database_detail(UsingPNDataBase, unittest.TestCase):
    def test_database_inputput(self):
        inputdatas = {'noise0':DataFrame(np.zeros((5,2))),
                      'noise1':DataFrame(np.ones((5,2))),
                      'noise2':DataFrame([[],[]]),
                  }
        addv = 2 #add value
        
        for n, d in inputdatas.items():
            self.pndb.set_noise(n,d)
        
        for n, d in inputdatas.items():
            assert_frame_equal(self.pndb.get_noise(n), d)
            #check the input data = output data
            
            self.pndb.set_noise(n,d+addv)
            #rewrite the data
        
        for n, d in inputdatas.items():
            assert_frame_equal(self.pndb.get_noise(n), d+addv)
            # check the rewrite data
    
    def test_reflesh(self):
        '''
        Check the data is deleted after reflesh pndb.
        '''
        dummydata = DataFrame(np.zeros((5,2))) 
        key = 'dummy data'
        setters = [self.pndb.set_noise, self.pndb.set_transfer_func,
                   self.pndb.set_combined_noise]
        getters = [self.pndb.get_noise, self.pndb.get_transfer_func,
                   self.pndb.get_combined_noise]
        
        for s in setters:
            s(key, dummydata)
        
        for g in getters:
            assert_frame_equal(dummydata, g(key))
        
        self.pndb.reflesh_all()
        for g in getters:
            self.assertRaises(KeyError, g, key)
        
    def test_noise_names(self):
        '''
        test getting noise names
        '''
        dummydata = {'a':list(range(4)), 'b': np.zeros(10), 'c':np.ones(5)}
        for key, val in dummydata.items():
            self.pndb.set_noise(key, val)
        self.assertEqual(self.pndb.get_noise_names(), dummydata.keys())

@add_msg
class TestCombineRead(UsingPNDataBase, unittest.TestCase):
    '''
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    '''
    # Message of calling to read the data.
    
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._set_ask_word()
        self._make_dummy_inputs()
    
    def _set_ask_word(self):
        pn = Parameter_Names()
        self._reading_message_dict = pn.get_read_msg_dict()  
        self._reading_list = pn.get_reading_list()
        # Message of calling to read the data.

    def _make_dummy_inputs(self):
        '''
        Make dummy data which match the message of reader is passed.
        '''
        self._msg_para = dict((v,k) for k,v in 
                              self._reading_message_dict.items())
        self._inputdata = {}
        for i, parameter in enumerate(self._reading_list):
            self._inputdata[parameter] = DataFrame([[4*1,4*i+1],[4*i+2,4*i+3]])

            
    def _input_side_effect_generator(self):
        """
        Generate the side_effect function which return the value match input
        message of reader.
        """
        
        def _side_effect(message):
            '''
            return the dummy data of self._inputdata. The data is chosen by 
            message. message is transformed into parameter in self._msg_para.
            '''
            return self._inputdata[self._msg_para[message]]
        return _side_effect
    

    def test_readdata(self):           
        with patch('src.dataio.csvio.CSVIO.read') as read_mock:
            read_mock.side_effect =self._input_side_effect_generator()
            
            pndata = PNDataReader()
            pndata.execute()
            
            for prmtr in self._reading_list:
                assert_frame_equal(self.pndb.get_noise(prmtr), 
                                   self._inputdata[prmtr])


@add_msg 
class TestCombineWrite(UsingPNDataBase,unittest.TestCase):  
    """
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    """
    # Message of calling to read the data.

    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._set_ask_word()
        self._make_dummy_inputs()
       
    def _set_ask_word(self):
        pn = Parameter_Names()
        self._writing_message_dict = pn.get_write_msg_dict()  
        self._writing_list = pn.get_writing_list()
        # Message of calling to read the data.

    def _make_dummy_inputs(self):
        '''
        Make dummy data which match the message of reader is passed.
        '''
        self._inputdata = {}
        for i, parameter in enumerate(self._writing_list):
            self._inputdata[parameter] = DataFrame([[4*1,4*i+1],[4*i+2,4*i+3]])

    def test_savedata(self):      
        '''
        Test data is saved correctry.
        '''
        with patch('src.dataio.csvio.CSVIO.write') as write_mock:
            
            for parameter, dummydata in self._inputdata.items():
                self.pndb.set_combined_noise(parameter, dummydata)
            
            pndatawriter = PNDataWriter()
            pndatawriter.execute()
            self.assertTrue(len(write_mock.call_args_list) > 0)
            # If not called raise error.
            
            for call, key, data in zip(write_mock.call_args_list,
                                       self._inputdata.keys(),
                                       self._inputdata.values()):
                args, kwargs =call
                self.assertTrue(args[0]==self._writing_message_dict[key])
                assert_frame_equal(args[1],data)

@add_msg 
class TestCombiningData(UsingPNDataBase,unittest.TestCase):
    
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._dummydatamng =DummyTransfuncNoiseData()
        self.pnpm = PNPrmtrMng()
        self.pnc = PNCombiner()
        
    
    def _test_calc(self):
        self.pnc = PNCalc()
        self._dummydatamng.set_dummydata1()
        collectdata = self._dummydatamng.set_data_and_get_value()
        
        self.pnc.execute()
        assert_array_almost_equal(collectdata, 
                                  self.pndb.get_combined_noise(self.pnpm.total))
        
    
class DummyTransfuncNoiseData():
    def __init__(self):
        self.pnpm = PNPrmtrMng()
    
    def set_dummydata1(self):
        self._make_dummy_pn_1()
    
    def set_data_and_get_value(self):
        self._set_data()
        return self.combined_noise
    
    def _set_data(self):
        pndb = PNDataBase()
        for key, noise in self.noise_set.items():
            pndb.set_noise(key, noise)
            
        for key, noise in self.tf_set.items():
            pndb.set_transfer_func(key, noise)   
    
    def _make_dummy_pn_1(self):
        self.noise_set ={}
        self.tf_set = {}
        freq_index = self.pnpm.get_index(self.pnpm.noise, self.pnpm.index_type_freq)
        noise_index =  self.pnpm.get_index(self.pnpm.noise, self.pnpm.index_type_val)
        tf_index =  self.pnpm.get_index(self.pnpm.tf, self.pnpm.index_type_val)
        combpn_index =  self.pnpm.get_index(self.pnpm.combpn, self.pnpm.index_type_val)
        
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000], 
                      name = freq_index)
        ref_noise = Series([-60, -90, -120, -150, -174, -174, -174, -174],
                            name = noise_index)
        vco_noise = Series([20, -10, -40, -70, -100, -120, -140, -160],
                            name = noise_index)
        MULT = 300
        vco_tf = Series(np.ones(len(vco_noise))*MULT+0j, name = tf_index)
        
        _amp = np.array([718589961.970159, 7185906.60906246, 71866.0551081057, 
                         725.615560869816, 12.3726308452402, 1.00031528765996, 
                         0.0588871802344158, 0.000723899599203854])
        _rad = np.deg2rad(np.array([-179.992047600053, -179.920476052613, 
                                    -179.204812606648, -172.099601076092, 
                                    -126.297374340824, -101.982202912406, 
                                    -144.636561700446, -175.919922754962]))
        total_noise = Series([-10.4575748935194, -40.4575736967748, 
                              -70.4574531198877, -100.436554942521, 
                              -119.544591133846, -120.670402823308, 
                              -139.069482677279, -159.985579375285], 
                              name = combpn_index)

        openloop_amp = Series(_amp*np.exp(1j*_rad), name = tf_index)
        # Make complex transfer function 

        self.noise_set[self.pnpm.ref] = pd.concat([freq, ref_noise], axis = 1)
        self.noise_set[self.pnpm.vco] = pd.concat([freq, vco_noise], axis = 1)
        self.combined_noise= pd.concat([freq, total_noise], axis = 1)
        
        self.tf_set[self.pnpm.open_loop_gain] =\
        pd.concat([freq, openloop_amp], axis = 1)
        self.tf_set[self.pnpm.ref] = self.tf_set[self.pnpm.open_loop_gain] 
        self.tf_set[self.pnpm.vco] = pd.concat([freq, vco_tf], axis = 1) 
        
        

if __name__=='__main__':
    unittest.main()