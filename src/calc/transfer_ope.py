# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 18:27:45 2017
copied from stack overflow
https://stackoverflow.com/questions/35304245/multiply-scipy-lti-transfer-functions
@author: LiNaK
"""

from scipy.signal.ltisys import TransferFunction as TransFun
from numpy import polymul,polyadd

#TODO: ADD test

class ltimul(TransFun):
    def get_transfunc(self):
        return TransFun(self.num, self.den)
    
    def __neg__(self):
        return ltimul(-self.num,self.den)

    def __mul__(self,other):
        if type(other) in [int, float]:
            return ltimul(self.num*other,self.den)
        elif type(other) in [TransFun, ltimul]:
            numer = polymul(self.num,other.num)
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __truediv__(self,other):
        if type(other) in [int, float]:
            return ltimul(self.num,self.den*other)
        if type(other) in [TransFun, ltimul]:
            numer = polymul(self.num,other.den)
            denom = polymul(self.den,other.num)
            return ltimul(numer,denom)

    def __rdiv__(self,other):
        if type(other) in [int, float]:
            return ltimul(other*self.den,self.num)
        if type(other) in [TransFun, ltimul]:
            numer = polymul(self.den,other.num)
            denom = polymul(self.num,other.den)
            return ltimul(numer,denom)

    def __add__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(self.num,self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(self.num,other.den),polymul(other.den,self.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __sub__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(self.num,-self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(self.num,other.den),-polymul(other.den,self.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __rsub__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(-self.num,self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(other.num,self.den),-polymul(self.den,other.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    # sheer laziness: symmetric behaviour for commutative operators
    __rmul__ = __mul__
    __radd__ = __add__
    
    
if __name__ == '__main__':
    num1 = [1, 3, 3]
    den1 = [1, 2, 1]
    num2 = [1]
    den2 = [1, 0]
    T1 = ltimul(num1, den1)
    T2 = ltimul(num2, den2)
    T3 = T1*T2
    T4 = T1/T2
    T5 = 4*T1
    Ts = [T3, T4, T5]
    for T, i in zip(Ts, range(len(Ts))):
        print('T{}, num ={}, den={}'.format(i+3, T.num, T.den))
    
