# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 21:00:17 2018

@author: LiAkaNaKiKMura
"""
# Standard module
import tkinter as tk
import tkinter.ttk as ttk
import unittest
import random
import string

# 3rd psrty's module
from pandas import DataFrame

# path setting                           
from context import src

# orginal module 
from testing_utility.unittest_util import cls_startstop_msg as add_msg

# target class
from src.ui.tk_ui.value_entry_tk import (ValueEntryTk, TkParametersListReader)

from src.ui.interface.input_value_mediator import (InputValueMediator, 
                                                   InputCallee,
                                                   ReadMediator)

from src.ui.interface.mediator import (Caller)


class DataForTest(object):
    _NUM = 20 
    # Make data for testing.
    def __init__(self):
        # Test list for integer, real number, string.
        self.testlists = [[random.randrange(1000) for _ in range(self._NUM)],
                           self.get_random_num_list(self._NUM),
                           [self._make_random_str(10) for _ in range(self._NUM)]
                           ]
        self.random_str = [self._make_random_str(10) for _ in range(self._NUM)]
        
    def _make_random_str(self, N):
        return ''.join(random.choice(string.ascii_letters + string.digits) 
                       for _ in range(N))
    def get_random_num_list(self, N):
        return [random.random()*10**5 for _ in range(N)]

class MockCallee(InputCallee):
    def __init__(self, *args, **kwargs):
        self.value = None
        super().__init__(*args, **kwargs)
        
    def call(self, value):
        self.value = value
    
    def isinvalid(self, value):
        return False

class MockCaller(Caller):
    def call_mediator(self):
        if self._mediator is not None:
            return self._mediator.call()
            

@add_msg   
class TestValueEntry(unittest.TestCase):
    _InputClass = ValueEntryTk
    def setUp(self):
        self.dft = DataForTest()
        
    def test_default_value(self):
        master = tk.Frame()
        for lists in self.dft.testlists:
            tks = self._InputClass('test',master, lists[0])
            self.assertEqual(tks.value, lists[0])
            tks.destroy()
    
    def test_tk(self):
        master =  tk.Frame()
        tks = self._InputClass('test', master)
        self.assertIsInstance(tks, ttk.Frame)
        tks.destroy()
    
    def test_no_master(self):
        master =  tk.Frame()
        tks = self._InputClass('test')
        tks.master = master
        tks.destroy()
        

@add_msg
class TestParameterWidgetsTkFrame(unittest.TestCase):
    def setUp(self):
        self.top =  tk.Toplevel()
        self.dft =  DataForTest()
        self.caller = MockCaller()
        self.tk_plist_reader = TkParametersListReader(self.dft.random_str, 
                                                      self.top)
        self.psm = ReadMediator(self.tk_plist_reader, self.caller)
        self.tk_plist_reader.pack()

    def tearDown(self):
        self.top.destroy()
        pass
    
    def test_setup(self):
        pass
    
    def test_getvalue(self):
        random_val = self.dft.get_random_num_list(len(self.dft.random_str))
        random_set = {d:n for d,n in zip(self.dft.random_str, random_val)}
        self.tk_plist_reader.set_values(random_set)
        value_dict = self.caller.call_mediator()
        for k,val in value_dict.items():
            self.assertEqual(val, str(random_set[k]))
    
    def test_set_again(self):
        random_val = self.dft.get_random_num_list(len(self.dft.random_str))
        random_set = {d:n for d,n in zip(self.dft.random_str, random_val)}
        random_set[1413] = 4134151
        self.tk_plist_reader.set_values(random_set)
        value_dict = self.caller.call_mediator()
        for k,val in value_dict.items():
            self.assertEqual(val, str(random_set[k]))
            
        random_val = self.dft.get_random_num_list(len(self.dft.random_str))
        random_set = {d:n for d,n in zip(self.dft.random_str, random_val)}
        self.tk_plist_reader.set_values(random_set)
        value_dict = self.caller.call_mediator()
        for k,val in value_dict.items():
            self.assertEqual(val, str(random_set[k]))
            
    # TODO: test init value from caller.

if __name__=='__main__':
    unittest.main()
    #top =  tk.Toplevel()
    #frame = ttk.Frame(top)
    frame = ttk.Frame()
    vet1 = ValueEntryTk (master = frame, name = 'chk gui', init_value='init')
    vet2 = ValueEntryTk (master = frame, name = 'chk gui2')
    vet1.grid(column = 0, row=0, sticky =(tk.S, tk.W,  tk.E, tk.N))
    vet2.grid(column = 0, row=1, sticky =(tk.S, tk.W,  tk.E, tk.N))
    dft =  DataForTest()
    tk_plist_reader = TkParametersListReader(dft.random_str, frame)
    random_val = dft.get_random_num_list(len(dft.random_str))
    random_set = {d:n for d,n in zip(dft.random_str, random_val)}
    tk_plist_reader.set_values(random_set)
    tk_plist_reader.grid(column = 0, row=2, sticky =( tk.S, tk.W,  tk.E, tk.N))
    
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)
    frame.columnconfigure(0, weight=1)
    
    frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
    frame.master.rowconfigure(0, weight=1)
    frame.master.columnconfigure(0, weight=1)
    frame.master.title("Test GUI")
    
    frame.mainloop()
    print(tk_plist_reader.call())