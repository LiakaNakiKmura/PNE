# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:04 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  
from src.csv_io.csvio import CSVReader
from src.csv_io.csvio import CSVWriter
from src.calc.pncalc import PNCalc


class PNCombiner():
    def __init__(self):
        csvr = CSVReader()
        csvw = CSVWriter()
        pnc = PNCalc()
    
    def execute(self):
        csvr = CSVReader()
        pass