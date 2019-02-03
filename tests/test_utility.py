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

class Test_singleton_decorator(Signletone_test_base, unittest.TestCase):
    """
    Test the singleton decorator.
    Mock class is defined for singleton
    """
    _cls = Mock_cls    
    
if __name__=='__main__':
    unittest.main()     