# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 18:08:17 2019

@author: LiNaK
"""

# Standard module
import unittest

# 3rd party's module

# Original module  
from context import src # path setting

# Target class
from src.utility.utility import singleton_decorator
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
        
    def delete_cls(self):
        """
        If one instance of singleton is deleted, other instance will be deleted.
        """
        a = self._cls()
        b = self._cls()
        del a
        self.assertRaises(NameError, b)

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
    
if __name__=='__main__':
    unittest.main()     