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
import abc

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
                                        IndivDataBase, NoiseDataBase,
                                        TransferfuncDataBase, 
                                        CloseLoopDataBase,
                                        NoiseTransfuncPairsManager,
                                        ParameterManager, RefParameter,
                                        VCOParameter, OpenLoopParameter,
                                        DataSetter, 
                                        DataGetter, RefTFCalcDataGetter,
                                        ReadingDataGetter)

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

class UsingPNDataBase(object):
    '''
    All test class that use database must inhirate this class.
    This class reflesh data base in each test method.
    '''
    def setUp(self):        
        self.pndb = PNDataBase()
    
    def tearDown(self):
        self.pndb.reflesh_all()
        '''
        reflesh PNDataBase for next test.
        '''

@add_msg
class TestCombinePNInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs = ((PNCombiner, Transaction),
                               (PNDataReader, Transaction),
                               (PNDataWriter, Transaction),
                               (PNCalc, Transaction),
                               (NoiseDataBase, IndivDataBase),
                               (TransferfuncDataBase, IndivDataBase),
                               (CloseLoopDataBase, IndivDataBase),
                               (DataSetter, Transaction)
                               )

@add_msg
class TestFuncExists(TestForMethodExist, unittest.TestCase):
    _class_method_pairs=((IndivDataBase,'set_data'),
                         (IndivDataBase,'get_data'),
                         (ParameterManager,'get_dataname'),
                         (DataGetter, 'get_data'),
                         (ReadingDataGetter, 'set_target_name')
                         )
    _class_attr_pairs = ((IndivDataBase, 'index_freq'),
                         (IndivDataBase, 'index_val')
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
                      'get_transfer_func', 'set_closeloop_noise',
                      'get_closeloop_noise')
        for  mth in method_names:
            self.assertTrue(callable(getattr(PNDataBase, mth)))


@add_msg    
class TestIndivisualDataBaseInheriting(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs = ((NoiseDataBase, IndivDataBase),
                            (TransferfuncDataBase, IndivDataBase),
                            (CloseLoopDataBase,  IndivDataBase)
                            )


class IndivDataBaseSetGetChk(UsingPNDataBase):
    '''
    This is the test for indivisual Data Base.
    target data base is set on _ClassForTest.
    Each class is the data base for each parameter. Data is deformed and 
    transfer to the PNDataBase.
    
    Because this test class uses pndb, this class inherate UsingPNDataBase.
    '''
    
    _ClassForTest = None
    _getter_for_pndb = 'get_data'
    def test_datasetting(self):
        '''
        test set data to indivisual database is reflected to PNDataBase. 
        '''
        test_db = self._ClassForTest()
        
        data = self._make_dummy_data()
        name = 'sample'
        
        test_db.set_data(name, data)
        getter = getattr(self.pndb, self._getter_for_pndb)
        
        assert_frame_equal(getter(name), data)
    
    def test_dual_database(self):
        '''
        test set data to one of indivisual database instance is reflected to
        another indivisual database instance. 
        '''
        database1 = self._ClassForTest()
        database2 = self._ClassForTest()
        
        data = self._make_dummy_data()
        name = 'sample'
        
        database1.set_data(name, data)
        assert_frame_equal(database2.get_data(name), data)

    def _make_dummy_data(self):
        test_database = self._ClassForTest()
        freq = Series([10**i for i in range(9)], name = test_database.index_freq)
        val = Series([max(-60-20*i, -173) for i in range(9)], 
                       name = test_database.index_val)
        data_pairs = pd.concat([freq, val], axis = 1)
        return data_pairs
    
    def _make_rand_dummy_data(self, N = 10):
        test_database = self._ClassForTest()
        freq = Series([10**i for i in range(N)], name = test_database.index_freq)
        val = Series(-20/np.random.rand(N) , name = test_database.index_val)
        data_pairs = pd.concat([freq, val], axis = 1)
        return data_pairs
    
    
    def test_column_length(self):
        '''
        Data must be sets of freq and its value.
        If data column length is greater than 2.
        '''
        test_database = self._ClassForTest()
        
        data_length =10
        S1 = Series(np.ones(data_length), name = test_database.index_freq)
        S2 = Series(np.zeros(data_length), name = test_database.index_val)
        S3 = Series(np.random.rand(data_length)*(-170), name = 'unnecessary data')
        # random number from -170 to 0
        
        dummy_input = pd.concat([S1, S2, S3], axis = 1) 
        dummy_output = pd.concat([S1, S2], axis = 1)
        name = 'dummydata'
        one_length_data = DataFrame(S1)
        
        test_database.set_data(name, dummy_input)
        assert_frame_equal(dummy_output, test_database.get_data(name))
        self.assertRaises(TypeError, test_database.set_data, name, S1)
        # Only DataFrame can be used
        self.assertRaises(ValueError, test_database.set_data, 
                          name, one_length_data)


    def test_read_data_wt_freq_set(self):
        '''
        if freq range is set when get_data, return value is Linear interpolated
        with value vs log freq.
        '''
        test_database = self._ClassForTest()
        length = 10
        index_pairs = [test_database.index_freq, test_database.index_val]
        name = 'dummydata'
        
        freq1 = [10.**(2*i) for i in range(int(length/2))]
        val1 = [-60.-20*i*2 for i in range(int(length/2))]
        
        freq2 = [10.**(i-1) for i in range(length+1)]
        # outband return the nan
        val2 = [np.nan]
        val2.extend([-60.-20*i for i in range(length-1)])
        val2.append(np.nan)
        
        dummy_input = DataFrame([freq1, val1]).T
        dummy_input.columns = index_pairs
        
        dummy_output = DataFrame([freq2, val2]).T
        dummy_output.columns = index_pairs
        
        test_database.set_data(name, dummy_input)
        get_freq_range = dummy_output.loc[:, test_database.index_freq]
        assert_frame_equal(dummy_output, 
                           test_database.get_data(name, get_freq_range))
    
    def test_rename_columns(self):
        '''
        test auto renaming columns of data.
        '''
        test_database = self._ClassForTest()
        
        length = 10
        diff_names = ['First name', 'Last name']
        index_pairs = [test_database.index_freq, test_database.index_val]
        name = 'dummydata'
        
        freq1 = [10.**(i) for i in range(length)]
        val1 = [-60.-20*i for i in range(length)]
        dummy_input = DataFrame([freq1, val1]).T
        dummy_input.columns = diff_names
        
        dummy_output = DataFrame([freq1, val1]).T
        dummy_output.columns = index_pairs
        
        test_database.set_data(name, dummy_input)
        assert_frame_equal(dummy_output, test_database.get_data(name))

    def test_get_names(self):
        '''
        DataBase returns names of resitored data
        '''
        number_of_data = 30
        namelist = [chr(65 +i) for i in range(number_of_data)]
        overwritenames = [namelist[i] for i in range(0, len(namelist), 2) ]
        test_database = self._ClassForTest()
        
        for name in namelist:
            test_database.set_data(name, self._make_rand_dummy_data())
        
        for name in overwritenames:
            test_database.set_data(name, self._make_rand_dummy_data())
        
        self.assertCountEqual(namelist,  test_database.get_names())
        
    
@add_msg  
class TestNoiseDataBase(IndivDataBaseSetGetChk, unittest.TestCase):
    _ClassForTest = NoiseDataBase
    _getter_for_pndb = 'get_noise'

@add_msg  
class TestTransferFuncDataBase(IndivDataBaseSetGetChk, unittest.TestCase):
    _ClassForTest = TransferfuncDataBase
    _getter_for_pndb = 'get_transfer_func'       
    def test_set_mag_deg_data(self):
        test_database = self._ClassForTest()
        amp = [0, 1, 1, 10, 2]
        deg = [0, 180, 90, 540, 30]
        freq = [10**i for i in range(len(amp))]
        combined = [0+0j, -1+0j, 0+1j, -10+0j, 3**(1/2)+1j]
        name = 'dummy_input'
        
        input_data = DataFrame([freq, amp, deg]).T# Transpose
        output_data = DataFrame([freq, combined]).T
        
        test_database.set_mag_deg_data(name, input_data)
        assert_array_almost_equal(output_data, test_database.get_data(name))

@add_msg  
class TestCloseLoopDataBase(IndivDataBaseSetGetChk, unittest.TestCase):
    _ClassForTest = CloseLoopDataBase
    _getter_for_pndb = 'get_closeloop_noise'
    

@add_msg  
class TestCommonNamesDataBase(UsingPNDataBase, unittest.TestCase):
    def test_noisenames(self):
        ndb = NoiseDataBase()
        tfdb = TransferfuncDataBase()
        ntpm = NoiseTransfuncPairsManager()

        length = 5
        noise_names = ['a', 'b', 'c']
        tf_names = ['d', 'b']
        common_names = list(set(noise_names) & set(tf_names))
        freq = 10**np.random.rand(length)

        for name in noise_names:
            val = np.random.rand(length)
            ndb.set_data(name, DataFrame([freq, val]).T)
            
        for name in tf_names:
            val = np.random.rand(length) + np.random.rand(length)*1j
            tfdb.set_data(name, DataFrame([freq, val]).T)
            
        self.assertCountEqual(ntpm.get_pair_names(), common_names)

# FIXME: Refactoring to reading data.


class TestParameterManager():
    '''
    Test for ParameterManager class.
    ParameterManager class has its name and dataname that is used to ask user.
    '''
    _ClassForTest = None
    def setUp(self):
        self.test_class = self._ClassForTest()
    
    def test_inerated(self):
        self.assertTrue(isinstance(self.test_class, ParameterManager))
    
    def test_get_parameter_name(self):
        self.assertIsWord(self.test_class.name)
        
    def test_get_parameter_dataname(self):
        # data name must be words.
        self.assertIsWord(self.test_class.get_dataname())
    
    def assertIsWord(self, data):
        self.assertTrue(isinstance(data, str))
        self.assertTrue(len(data) > 0)

class TestOpenLoopParameter():
    _ClassForTest = OpenLoopParameter


class TestNoiseParameter(TestParameterManager):
    def test_get_parameter_dataname(self):
        dflt_data_name = self.test_class.get_dataname()
        self.test_class.set_type(self.test_class.tf)
        tf_data_name = self.test_class.get_dataname()
        self.test_class.set_type(self.test_class.noise)
        noise_data_name = self.test_class.get_dataname()
        
        for data_name in [dflt_data_name, tf_data_name, noise_data_name]:
            # All data names are words.  
            self.assertTrue(isinstance(data_name, str))
            self.assertTrue(len(data_name) > 0)
        
        self.assertNotEqual(tf_data_name, noise_data_name)
        # Datanome for transger function and noise must be different.

        self.assertEqual(dflt_data_name, noise_data_name)
        # Datanome for transger function and noise must be different.
        
        self.assertRaises(ValueError, self.test_class.set_type, None)
        # If invalid value is set to set_type, raise value erorr

@add_msg
class TestRefParameter(TestNoiseParameter, unittest.TestCase):
    _ClassForTest = RefParameter
    
@add_msg
class TestVCOParameter(TestNoiseParameter, unittest.TestCase):
    _ClassForTest = VCOParameter
        

class TestInidivDataGetter(metaclass = abc.ABCMeta):
    _ClassForTest = None
    
    def setUp(self):
        self._datagetter = self._ClassForTest()
    
    def test_inhirated(self):
        self.assertTrue(issubclass(self._ClassForTest, DataGetter))
    
    @abc.abstractmethod
    def test_get_data(self):
        pass

@add_msg
class TestRefTFCalcDataGetter(UsingPNDataBase, TestInidivDataGetter, 
                              unittest.TestCase):
    _ClassForTest = RefTFCalcDataGetter
    _data_size = [5, 2]
    def setUp(self):
        UsingPNDataBase.setUp(self)
        TestInidivDataGetter.setUp(self)
        self._tfdb = TransferfuncDataBase()
        self._pnpm = PNPrmtrMng()
    
    def test_get_data(self):
        self._set_open_loop_gain()
        data = self._datagetter.get_data()
        assert_frame_equal(data, self._dummy_loop_data)

    def _set_open_loop_gain(self):
        # Make Dummy Data of open loop gain.
        olg = [30-20*i+i/self._data_size[0]*np.pi*1j\
                      for i in range(self._data_size[0])]
        freq = [10**(i) for i in range(len(olg))]
        _dummy_loop_data = DataFrame([freq, olg]).T
        
        self._tfdb.set_data(self._pnpm.open_loop_gain, _dummy_loop_data)
        self._dummy_loop_data =  _dummy_loop_data
        self._dummy_loop_data.columns = [self._tfdb.index_freq, 
                                         self._tfdb.index_val]

@add_msg
class TestReadingDataGetter(TestInidivDataGetter, unittest.TestCase):
    _ClassForTest = ReadingDataGetter


'''
    
    """
    def _set_open_loop_gain(self):
        self._olg = [30-20*i+i/self._data_size[0]*np.pi*1j\
                      for i in range(self._data_size[0])]
        self._tfdb.set_data(self._pnpm.open_loop_gain, self._olg)
    """
    
    def _make_return_value(self):
        # name must be string of msg 
        self._return_values ={name: np.random.rand(*self._data_size)\
                              for name in self._name_str_pairs.keys()}
    
    def _side_effect_generator(self):
        def side_effect(msg):
            for name in self._return_values.keys():
                if re.match('noise', msg, flags = re.I) is not None:
                    # If matched, return not None.
                    return np.random.rand(*self._data_size)
        return side_effect
    
    def test_read_data(self):
        with patch('src.dataio.csvio.CSVIO.read') as read_mock:
            read_mock.side_effect =self._side_effect_generator()
            self._reader.execute()
    
    def test_inherited(self):
        issubclass(self._ClassForTest, DataReader)
"""
class TestRefReader(TestInidivReader, unittest.TestCase):
    _ClassForTest = RefDataReader
"""
'''

@add_msg
class TestDataSetter(unittest.TestCase):
    # TODO: add test for data setter
    def test_data_setter(self):
        refpar = RefParameter()
        ndb = NoiseDataBase()
        csvio = CSVIO()
        data_setter = DataSetter(refpar, csvio, ndb)
        with patch('src.dataio.csvio.CSVIO.read') as read_mock:
            data_setter.execute()

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
    # Data kinds for database.
    
    def __init__(self):
        self.pnpm = PNPrmtrMng()
    
    def get_parameter_names(self):
        return self._names
    
    def get_read_msg_parameters(self):
        return self._reading_msg_names

    def get_write_msg_parameters(self):
        return self._writing_msg_names
    
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
                   self.pndb.set_closeloop_noise]
        getters = [self.pndb.get_noise, self.pndb.get_transfer_func,
                   self.pndb.get_closeloop_noise]
        
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

    def test_transferfunc_names(self):
        '''
        test getting transferfunc names
        '''
        dummydata = {'a':list(range(4)), 'b': np.zeros(10), 'c':np.ones(5)}
        for key, val in dummydata.items():
            self.pndb.set_transfer_func(key, val)
        self.assertEqual(self.pndb.get_transfer_func_names(), dummydata.keys())

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
                self.pndb.set_closeloop_noise(parameter, dummydata)
            
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
        
    
    def test_calc(self):
        self.pnc = PNCalc()
        self._dummydatamng.set_dummydata1()
        collectdata = self._dummydatamng.set_data_and_get_value()
        
        self.pnc.execute()
        assert_array_almost_equal(collectdata, 
                                  self.pndb.get_closeloop_noise(self.pnpm.total))
        
    
class DummyTransfuncNoiseData():
    def __init__(self):
        self.pnpm = PNPrmtrMng()
    
    def set_data_and_get_value(self):
        return self.combined_noise
    
    def _set_dataset(self, freq, noise, tf, name):
        self._set_dummy_to_db(NoiseDataBase, freq, noise, name)
        self._set_dummy_to_db(TransferfuncDataBase, freq, tf, name)
    
    def _set_dummy_to_db(self, DataBase, freq_data, value_data, name):
        db =DataBase()
        dummy_data = pd.concat((freq_data, value_data), axis = 1)
        dummy_data.columns = [db.index_freq, db.index_val]
        db.set_data(name, dummy_data)    
    
    def set_dummydata1(self):
        self._set_ref_1()
        self._set_vco_1()
        self._set_combined_1()
        pass
    
    def _openloop1(self):
        amp = np.array([718589961.970159, 7185906.60906246, 71866.0551081057, 
                        725.615560869816, 12.3726308452402, 1.00031528765996, 
                        0.0588871802344158, 0.000723899599203854])
        rad = np.deg2rad(np.array([-179.992047600053, -179.920476052613, 
                                   -179.204812606648, -172.099601076092, 
                                   -126.297374340824, -101.982202912406, 
                                   -144.636561700446, -175.919922754962]))
        return Series(amp*np.exp(1j*rad))

    def _set_ref_1(self):
        noise = Series([-60, -90, -120, -150, -174, -174, -174, -174])
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])
        MULT = 300
        tf = self._openloop1()*MULT
        self._set_dataset(freq, noise, tf, self.pnpm.ref)
    
    def _set_vco_1(self):
        noise = Series([20, -10, -40, -70, -100, -120, -140, -160])
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])
        tf = Series(np.ones(len(noise))+0j)
        self._set_dataset(freq, noise, tf, self.pnpm.vco)
    
    def _set_combined_1(self):
        total_noise = Series([-10.4575748935194, -40.4575736967748, 
                              -70.4574531198877, -100.436554942521, 
                              -119.544591133846, -120.670402823308, 
                              -139.069482677279, -159.985579375285])
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])
        db = CloseLoopDataBase()
        
        self.combined_noise= pd.concat([freq, total_noise], axis = 1)
        self.combined_noise.columns = [db.index_freq, db.index_val]
        
        self._set_dummy_to_db(TransferfuncDataBase, freq, self._openloop1(),
                              self.pnpm.open_loop_gain)

if __name__=='__main__':
    unittest.main()