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
import re
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
                                        PNCalc, PNDataBase, CommonParameter,
                                        IndivDataBase, NoiseDataBase,
                                        TransferfuncDataBase, 
                                        CloseLoopDataBase,
                                        NoiseTransfuncPairsManager,
                                        ParameterManager, RefParameter,
                                        VCOParameter, OpenLoopParameter,
                                        TotalOutParameter,
                                        DataReader, DataWriter,
                                        PhaseNoiseCalculator)

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
from src.utility.calc import MagLogUtil

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
                               (DataReader, Transaction),
                               (DataWriter, Transaction)
                               )

@add_msg
class TestFuncExists(TestForMethodExist, unittest.TestCase):
    _class_method_pairs=((IndivDataBase,'set_data'),
                         (IndivDataBase,'get_data'),
                         (ParameterManager,'get_dataname'),
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

class TestCombinPN_Excution(UsingPNDataBase, unittest.TestCase):
    '''
    Excute total Phase noise combining program.
    '''
    
    _db_prm_path_pairs=[[NoiseDataBase, RefParameter, 
                         'tests.dummy_data.data1.Ref.csv'],
                        [NoiseDataBase, VCOParameter,
                         'tests.dummy_data.data1.VCO.csv'],
                        [TransferfuncDataBase, RefParameter,
                         'tests.dummy_data.data1.Open_loop.csv'],
                        [TransferfuncDataBase, VCOParameter,
                         'tests.dummy_data.data1.VCOtf.csv'],
                        [TransferfuncDataBase, OpenLoopParameter,
                         'tests.dummy_data.data1.Open_loop.csv']]
    # Pairs of DataBase, Parameter, dummy path. 
    _corret_data_path = 'tests.dummy_data.data1.correct_data.csv'
    
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self.ugmfpm = UtilityGettingMessageFromParameterManager()
    
    def _test_combine(self):
        mock_path ='src.dataio.io_com.PathDialog.get_load_path'
        with patch(mock_path) as read_mock:
            read_mock.return_value = dummydata
        pass
    
    def _return_target_path(self, DataBase, ParameterManagerClass):
        # TODO: Check This function
        '''
        return the function: return the matched path to the message.
        '''
        msg_path_pairs = {}
        for DataBase, PramaterManagerClass, path in self._db_prm_path_pairs:
            self.ugmfpm.set_database(DataBase)
            self.ugmfpm.set_parametermanager(ParameterManagerClass)
            msg = self.ugmfpm.get_message()
            msg_path_pairs[msg] = path
        
        def mock_path(msg):
            print(msg_path_pairs[msg])
            return msg_path_pairs[msg]
    
    def _make_msg_path_pairs(self):
        # Make matrix to search message and corresponded path.
        df = DataFrame([], columns = ['db', 'prm', 'path'])
        """
        for num, pairs in enumerate(self._db_prm_path_pairs):
            DB, PRM, path = *pairs
            #DataBase, ParameterManeger, path.
            db = DB()
            prm = PRM()
            df.loc[num,:]=[db.index_val, prm, path]
        """
        #FIXME

class MakeDummyDataForDataBase():
    '''
    This class make dummy data. That fits normal format.
    '''
    def __init__(self, DataBaseClass = None):
        if DataBaseClass is not None:
            self.database = DataBaseClass()
        else:
            self.database = None
    
    def get_dummydata(self, DataBaseClass=None, length = 10):
        if DataBaseClass is not None:
            self.database = DataBaseClass()
            
        freq = Series([10**i for i in range(length)], 
                       name = self.database.index_freq)
        val = Series(-20/np.sort(np.random.rand(length))[::-1] , 
                     name = self.database.index_val)
        
        return  DataFrame([freq, val]).T
    
@add_msg    
class TestIndivisualDataBaseInheriting(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs = ((NoiseDataBase, IndivDataBase),
                            (TransferfuncDataBase, IndivDataBase),
                            (CloseLoopDataBase,  IndivDataBase)
                            )

@add_msg  
class TestIndivDataBaseCommon(UsingPNDataBase, unittest.TestCase):
    def test_indiv_index_val(self):
        # Each database index value must be indivisual.
        database_list = [NoiseDataBase, TransferfuncDataBase, CloseLoopDataBase]
        indices =[db().index_val for db in database_list]
        self.assertEqual(len(indices), len(set(indices)))

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
        DataBase returns set of names of resitored data.
        return value is list
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
        self.assertEqual(type(test_database.get_names()), list)

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

@add_msg
class TestParameterManagerTotal(UsingPNDataBase,unittest.TestCase):
    def test_original_name(self):
        """
        name must be indivisual in each other for parameter manager.
        """
        _parameter_list=[OpenLoopParameter, RefParameter, VCOParameter,
                         TotalOutParameter]
        # TODO: Is needed to be parameter list to pncombiner.
        names = [p.name for p in _parameter_list]
        self.assertEqual(len(names), len(set(names)))

class TestParameterManager(UsingPNDataBase):
    '''
    Test for ParameterManager class.
    ParameterManager class has its name and dataname that is used to ask user.
    '''
    
    #Parameter for inirited class.
    _ClassForTest = None
    _acceptable_databases = None
    
    #common parameter
    _total_database_list = [NoiseDataBase, TransferfuncDataBase,
                            CloseLoopDataBase]
    # FIXME: Change names if PLL name is different.
    
    def setUp(self):
        super().setUp()
        self.test_class = self._ClassForTest()
    
    def test_inerated(self):
        self.assertIsInstance(self.test_class, ParameterManager)
    
    def test_get_parameter_name(self):
        self.assertIsWord(self.test_class.name)
        
    def test_get_parameter_dataname(self):
        # data name must be words.
        self.assertIsWord(self.test_class.get_dataname())
    
    def assertIsWord(self, data):
        self.assertIsInstance(data, str)
        self.assertTrue(len(data) > 0)
    
    def test_set_type(self):
        # Prameter Manager return the dataname by setting types.
        # If data is not acceptable, raise valueerror.
        self._make_unacceptable_databases()
        
        for DB in self._acceptable_databases:
            # This will not raise error.
            db = DB()
            self.test_class.set_type(db.index_val)
        
        for DB in self._unacceptable_databases:
            # This will raise error.
            db = DB()
            self.assertRaises(ValueError, self.test_class.set_type, 
                              db.index_val)
    
    def _make_unacceptable_databases(self):
        self._unacceptable_databases = self._total_database_list.copy()
        for db in self._acceptable_databases:
            self._unacceptable_databases.remove(db)

@add_msg
class TestOpenLoopParameter(TestParameterManager, unittest.TestCase):
    _ClassForTest = OpenLoopParameter
    _acceptable_databases = [TransferfuncDataBase]
    
@add_msg
class TestRefParameter(TestParameterManager, unittest.TestCase):
    _ClassForTest = RefParameter
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]

@add_msg
class TestVCOParameter(TestParameterManager, unittest.TestCase):
    _ClassForTest = VCOParameter
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]

@add_msg
class TestTotalOutParameter(TestParameterManager, unittest.TestCase):
    _ClassForTest = TotalOutParameter
    _acceptable_databases = [CloseLoopDataBase]
    
class UtilityGettingMessageFromParameterManager():    
    def set_database(self, DataBase):
        assert issubclass(DataBase, IndivDataBase),\
        'Parameter Manager class must be subclass of InidivDataBase'
        
        self._db =DataBase()
    
    def set_parametermanager(self, ParameterManagerClass):
        assert issubclass(ParameterManagerClass, ParameterManager),\
        'Parameter Manager class must be subclass of ParameterManager'
        
        self._prm =ParameterManagerClass()
    
    def get_message(self):
        self._prm.set_type(self._db.index_val)
        return self._prm.get_dataname()

@add_msg
class TestDataReader(UsingPNDataBase, unittest.TestCase):
    _DataBase  = None
    _set_class_pairs=[[CSVIO, NoiseDataBase, RefParameter], 
                      [CSVIO, TransferfuncDataBase, VCOParameter], 
                      [CSVIO, NoiseDataBase, VCOParameter],
                      [CSVIO, TransferfuncDataBase, OpenLoopParameter]
                      ]
    _Reader_mockpath_pairs={CSVIO:'src.dataio.csvio.CSVIO.read'}
    
    def setUp(self):
        super().setUp()
        self.dummydata_maker = MakeDummyDataForDataBase()
    
    def test_data_reader(self):
        for pair in self._set_class_pairs:
            self._test_each_data(*pair)
    
    def _test_each_data(self, _Reader, _DataBase, _ParamaterManager):
        # test DataReader read data from _Reader with Parameter Manager name.
        # set to Reader.
        
        # Make instances
        db = _DataBase()
        paramng = _ParamaterManager()
        dummydata = self.dummydata_maker.get_dummydata(_DataBase)
        
        data_reader = DataReader(_Reader, _DataBase, _ParamaterManager)
        self._test_DataReader_exe(self._Reader_mockpath_pairs[_Reader],
                                  dummydata, data_reader)
        assert_frame_equal(db.get_data(paramng.name), dummydata) 
    
    def _test_DataReader_exe(self, mock_path, dummydata, data_reader):
        with patch(mock_path) as read_mock:
            read_mock.return_value = dummydata
            data_reader.execute()              
            return read_mock
    
    def test_none_df_data_set(self):
        # If none df data is set, raise error.
        _Reader = CSVIO
        _DataBase = NoiseDataBase
        _ParamaterManager = RefParameter
        
        dummydata = [[1,10,100], [-20,-40,-60]]        
        data_reader = DataReader(_Reader, _DataBase, _ParamaterManager)
        with patch(self._Reader_mockpath_pairs[_Reader]) as read_mock:
            read_mock.return_value = dummydata
            self.assertRaises(TypeError, data_reader.execute)

    def test_diff_test_name(self):
        # Test call pattern is different when data base is changed to the same
        # parameter.
        _DataBases =  [NoiseDataBase, TransferfuncDataBase]
        dummydata = self.dummydata_maker.get_dummydata(_DataBases[0])
        mock_path ='src.dataio.csvio.CSVIO.read'
        calls = []

        for DB in _DataBases:
            data_reader = DataReader(CSVIO, DB, RefParameter)            
            read_mock = self._test_DataReader_exe(mock_path, dummydata, 
                                                  data_reader)
            calls.append(list(read_mock.call_args))
        
        first_call = calls.pop(0)
        for call in calls:
            # different data name is called.
            # data name is first argument.
            self.assertNotEqual(first_call[0], call[0])

@add_msg
class TestDataWriter(UsingPNDataBase, unittest.TestCase):
    # This is the test for DataWriter.
    # Data Writer write data dicleared in input class pairs.
    # Tested in some pairs of classes.
    _set_class_pairs=[[CSVIO, NoiseDataBase, RefParameter], 
                      [CSVIO, TransferfuncDataBase, VCOParameter], 
                      [CSVIO, NoiseDataBase, VCOParameter],
                      [CSVIO, TransferfuncDataBase, OpenLoopParameter],
                      [CSVIO, CloseLoopDataBase, TotalOutParameter]
                      ]
    
    _Writer_mockpath_pairs={CSVIO:'src.dataio.csvio.CSVIO.write'}
    
    # args in call object is first data.
    _data_arg_order =0
    # Order of data in args is (message, data)
    _num_of_msgdata_in_args = 0
    _num_of_dummy_data_in_args = 1
    
    def setUp(self):
        super().setUp()
        self.dummydata_maker = MakeDummyDataForDataBase()
        
    def test_data_writer(self):
        for pair in self._set_class_pairs:
            self._test_each_data(*pair)
    
    def _test_each_data(self, _Reader, _DataBase, _ParamaterManager):
        # test DataReader read data from _Reader with Parameter Manager name.
        # set to Reader.
        
        # Make instances
        db = _DataBase()
        paramng = _ParamaterManager()
        dummydata = self.dummydata_maker.get_dummydata(_DataBase)
        paramng.set_type(db.index_val)
        db.set_data(paramng.name, dummydata)
        
        data_writer = DataWriter(_Reader, _DataBase, _ParamaterManager)
        args = self._test_DataWriter_exe(self._Writer_mockpath_pairs[_Reader],
                                         dummydata, data_writer)
        
        msg = args[self._num_of_msgdata_in_args]
        # writing message must contain the dataname of parameter manager.
        self.assertTrue(re.match(paramng.get_dataname(),msg) is not None)
        
        write_data = args[self._num_of_dummy_data_in_args]
        assert_frame_equal(dummydata, write_data)
    
    def _test_DataWriter_exe(self, mock_path, dummydata, data_writer):
        with patch(mock_path) as write_mock:
            data_writer.execute()
            kall = write_mock.call_args_list
            
            # writer class is just call once.
            self.assertTrue(len(kall) == 1)
            
            # Return args of first call, drop kwargs of call.
            first_call = 0
        return kall[first_call][self._data_arg_order]
        

@add_msg
class TestPNparameter(unittest.TestCase):
    
    def test_parameter_exist(self):
        '''
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = CommonParameter()
        
        pn = Parameter_Names()
        attrnames = pn.get_parameter_names()
        for n in attrnames:
            prmtr = getattr(pnpm,n)
            self.assertIsInstance(prmtr, str)
            self.assertTrue(0<len(prmtr))
            self.assertRaises(AttributeError, setattr, *(pnpm, n, 'a'))
            # Raise error if property value is changed.
      

class Parameter_Names():
    _names = ['ref', 'vco', 'pd']
    _reading_msg_names = ['ref', 'vco', 'pd', 'open_loop_gain']
    _reading_lists = ['ref', 'vco', 'pd', 'open_loop_gain']
    _writing_msg_names = ['total']
    _writing_lists = ['total']
    # Data kinds for database.
    
    def __init__(self):
        self.pnpm = CommonParameter()
    
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
    
    _reading_db_para_pairs = ((NoiseDataBase, RefParameter), 
                              (TransferfuncDataBase, RefParameter),
                              (NoiseDataBase, VCOParameter),
                              (TransferfuncDataBase, VCOParameter),
                              (TransferfuncDataBase, OpenLoopParameter)
                              )
    
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._make_dataname_dummydata_df()

    def _make_dataname_dummydata_df(self):
        make_dummy = MakeDummyDataForDataBase()
        datanames = []
        self._dummydata ={}
        
        for DB, PRM in self._reading_db_para_pairs:
            db = DB()
            prm = PRM()
            prm.set_type(db.index_val)
            name = prm.get_dataname()
            datanames.append([DB, PRM, name])
            self._dummydata[name] = make_dummy.get_dummydata(DB)
            
        self._datanames = DataFrame(datanames, columns = ['DataBase', 
                                                          'Parameter', 
                                                          'dataname'])
            
    def _get_data_from_msg(self, msg):
        # If dataname is in msg, return matched dummydata.
        for dataname in self._dummydata.keys():
            if re.match(dataname, msg):
                return self._dummydata[dataname]
            
        # if dataname is not find in message, raise error
        raise ValueError('{} is invalid message'.format(msg))
    
    def _input_side_effect_generator(self):
        '''
        Generate the side_effect function which return the value match input
        message of reader.
        _side_effect function must be defined in this method to use mock class.
        Because _get_data_from_msg is class method and need instance "self". 
        '''
        def _side_effect(message):
            '''
            return the dummy data of self._inputdata. The data is chosen by 
            message. message is transformed into parameter in self._msg_para.
            '''
            return self._get_data_from_msg(message)
        return _side_effect
    

    def test_readdata(self):           
        with patch('src.dataio.csvio.CSVIO.read') as read_mock:
            read_mock.side_effect =self._input_side_effect_generator()
            
            pndata = PNDataReader()
            pndata.execute()
            for data in self._datanames.get_values():
                db = data[0]()
                prm = data[1]()
                assert_frame_equal(db.get_data(prm.name), 
                                   self._dummydata[data[2]])


@add_msg 
class TestPNDataWriter(UsingPNDataBase,unittest.TestCase):  
    '''
    This is the test for writing data from data base to writer.
    '''
    
    _writing_db_para_pairs = ((CloseLoopDataBase, TotalOutParameter),)
    # Pairs of writing database and parameter manager.
    
    _writer_mock_path = 'src.dataio.csvio.CSVIO.write'
    # path for writer to replace to mock..
    
    _msg_arg_order = 0
    # message is set in 1st argument for writer.
    _data_arg_order = 1
    # data is set in 2nd argument for writer.

    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._make_dataname_dummydata_df()
        
    def _make_dataname_dummydata_df(self):
        make_dummy = MakeDummyDataForDataBase()  
        self._dummydata ={} 
        
        for DB, PRM in self._writing_db_para_pairs:
            db = DB()
            prm = PRM()
            prm.set_type(db.index_val)
            name = prm.name
            dummydata = make_dummy.get_dummydata(DB)
            
            db.set_data(name, dummydata)
            self._dummydata[prm.get_dataname()] = dummydata
            
    def _get_data_from_msg(self, msg):
        # If dataname is in msg, return matched dummydata.
        for dataname in self._dummydata.keys():
            if re.match(dataname, msg):
                return self._dummydata[dataname]
            
        # if dataname is not find in message, raise error
        raise ValueError('{} is invalid message'.format(msg))
    
    def _get_argslist(self, call_arg_list):
        # Args is first data of each call list.
        return [a_call[0] for a_call in call_arg_list]

    def test_savedata(self):      
        '''
        Test data is saved correctry.
        '''
        with patch(self._writer_mock_path) as write_mock:            
            pndatawriter = PNDataWriter()
            pndatawriter.execute()
            self.assertTrue(len(write_mock.call_args_list) > 0)
            # If not called raise error.
            
            for args in self._get_argslist(write_mock.call_args_list):
                set_data = self._get_data_from_msg(args[self._msg_arg_order])
                write_data = args[self._data_arg_order]
                assert_frame_equal(set_data, write_data)

@add_msg 
class TestCombiningData(UsingPNDataBase, unittest.TestCase):
    
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self._dummydatamng =DummyTransfuncNoiseData()
        self._dummydatamng.set_dummydata()
        self.pnc = PNCombiner()
        self._cls_loop_db = CloseLoopDataBase()
        self._total_out_pmtr  = TotalOutParameter()
        
    
    def test_calc(self):
        self.pnc = PNCalc()
        self.pnc.execute()
        
        collectdata = self._dummydatamng.get_collect_data()
        calced = self._cls_loop_db.get_data(self._total_out_pmtr.name)
        
        assert_array_almost_equal(collectdata, calced)
        
class DummyTransfuncNoiseData():
    # Set dummy data for database.
    # Make collect data for test.
    def get_collect_data(self):
        self._set_combined_noise()
        return self.combined_noise
    
    def set_dummydata(self):
        DataSetClasses = [SetOpenLoopData, SetRefData, SetVCOData]
        for Class in DataSetClasses:
            dataset = Class()
            dataset.set_data()

    def _set_combined_noise(self):
        total_noise = Series([-10.4575748935194, -40.4575736967748, 
                              -70.4574531198877, -100.436554942521, 
                              -119.544591133846, -120.670402823308, 
                              -139.069482677279, -159.985579375285])
        freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])
        db = CloseLoopDataBase()
        
        self.combined_noise= pd.concat([freq, total_noise], axis = 1)
        self.combined_noise.columns = [db.index_freq, db.index_val]


class SetPNCalcData():
    '''
    Set dummy data to database for combining test. 
    Each parameter has inherated class.
    Noise Data and Transfer function is set.
    '''
    _ParameterManager = None
    _tf_name ='transferfunc'
    _noise_name = 'noise'
    _noise = Series([])
    _freq = Series([])  
    
    def __init__(self):
        self._db = {self._noise_name:NoiseDataBase(), 
                    self._tf_name:TransferfuncDataBase()}
        self._prmtr =self._ParameterManager()
        
    def set_data(self):
        self._inputs={}
        self._make_noise_data()
        self._make_tf_data()
        self._write_data()
    
    def _make_noise_data(self):
        self._inputs[self._noise_name] = DataFrame([self._freq, self._noise]).T
    
    def _make_tf_data(self):
        pass
        
    def _write_data(self):
        for name in self._inputs.keys():
            self._db[name].set_data(self._prmtr.name, self._inputs[name])


class SetRefData(SetPNCalcData):
    _ParameterManager = RefParameter
    _noise = Series([-60, -90, -120, -150, -174, -174, -174, -174])
    _freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000]) 
    _MULT = 300
    
    def __init__(self):
        super().__init__()
        self.prmtr = OpenLoopParameter()   
    
    def _make_tf_data(self):
        if not self.prmtr.name in self._db[self._tf_name].get_names():
            self._set_open_loop_data()
            
        open_loop_tf = self._db[self._tf_name].get_data(self.prmtr.name)
        self._inputs[self._tf_name] =open_loop_tf*self._MULT
    
    def _set_open_loop_data(self):
        solp = SetOpenLoopData()
        solp.set_data()
        

class SetVCOData(SetPNCalcData):
    _ParameterManager = VCOParameter
    _noise = Series([20, -10, -40, -70, -100, -120, -140, -160])
    _freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])    
        
    def _make_tf_data(self):
        tf = Series(np.ones(len(self._noise))+0j)
        self._inputs[self._tf_name] =DataFrame([self._freq,tf]).T

class SetOpenLoopData(SetPNCalcData):
    _ParameterManager = OpenLoopParameter 
    _amp = np.array([718589961.970159, 7185906.60906246, 71866.0551081057, 
                     725.615560869816, 12.3726308452402, 1.00031528765996, 
                     0.0588871802344158, 0.000723899599203854])
    _rad = np.deg2rad(np.array([-179.992047600053, -179.920476052613, 
                                -179.204812606648, -172.099601076092, 
                                -126.297374340824, -101.982202912406, 
                                -144.636561700446, -175.919922754962]))
    _freq = Series([1,10,100,1000,10000, 100000, 1000000, 10000000])
    
    def _make_noise_data(self):
        # No Noise set.
        pass
        
    def _make_tf_data(self):
        tf = Series(self._amp*np.exp(1j*self._rad))
        self._inputs[self._tf_name] =DataFrame([self._freq,tf]).T

class TestPhaseNoiseCalculator(UsingPNDataBase, unittest.TestCase):
    #TODO: Different data
    #TODO: Add data type
    #TODO: Raise Error unless enough data.
    def setUp(self):
        UsingPNDataBase.setUp(self)
        self.pnc = PhaseNoiseCalculator()
        self.mlu = MagLogUtil()
        self._setupu_columns()
        self._precise_digit = 5
        # Number of precise digit for test
    
    def _setupu_columns(self):
        freq_column = CommonParameter.index_freq        
        self._noise_columns = [freq_column, NoiseDataBase().index_val]
        self._tf_columns = [freq_column, TransferfuncDataBase().index_val]
        self._clsd_columns = [freq_column, CloseLoopDataBase().index_val]
        
    
    def test_normal_data(self):
        self._calc_combine(self._get_norm_data)
    
    def _calc_combine(self, data_reader_func):
        '''
        1. Set openloop transfer function.
        2. set transfer function of target data.
        3. set noise of target.
        4. Get the calculated data.
        '''
        
        self.pnc.set_open_loop(self._openloop_data())
        tf_data, in_data, correct_data = data_reader_func()
        self.pnc.set_tf(tf_data)
        self.pnc.set_noise(in_data)
        out_data= self.pnc.get_compressed_noise()
        assert_frame_equal(correct_data, out_data, 
                           check_less_precise = self._precise_digit)
    
    def _get_norm_data(self):
        freq = [10**i for i in range(5)]
        in_noise = [-100 for _ in range(len(freq))]
        out_noise = [-99.91270389, -99.22619035, -97.67739312, -119.22619035,
                     -139.91270389]
        tf_data = self._openloop_data().copy()
        in_data = DataFrame([freq, in_noise], index = self._noise_columns).T
        out_data = DataFrame([freq, out_noise], index = self._clsd_columns).T
        # self._noise_columns is set to INDEX brcause transposition.
        return (tf_data, in_data, out_data)
    
    def _openloop_data(self):
        freq = [10**i for i in range(5)]
        mag = [10**(2-i) for i in range(5)]
        deg = [-180, -150, -135, -150, -180]
        comp_val = self.mlu.magdeg2comp(mag, deg)
        return DataFrame([freq, comp_val], index = self._tf_columns).T

    def test_diff_range_data(self):
        self._calc_combine(self._get_norm_data)

    def _get_diff_freq_data(self):
        # TODO: Add test for diffference data.
        # test for different range, lengeth, step frequency data.
        # range: minimum range.
        # step: all set of inband.
        pass
    

if __name__=='__main__':
    print(ugm.get_message())

    unittest.main()