#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 17:23:47 2022

@author: mehdi
"""
from __future__ import division
import math
from scipy.stats import norm


# VARIABLE DECLARATION

S = 101 # Current underlying spot price
K = 100 # Strike price
r = 0.03 # Risk free rate
t = 1 # Time to maturity
sigma = 0.15 # underlying volatility
div = 0 # Dividend yield

d1 = (math.log(S/K) + (r + ((sigma**2) / 2) ) * t) / ( sigma * math.sqrt(t))
d2 = d1 - sigma * math.sqrt(t)

N_d1 = norm.cdf(d1)
N_d2 = norm.cdf(d2)

Np_d1 = math.exp((-d1**2) / 2 ) * ( 1 / math.sqrt(2*math.pi))



Call_option = S * math.exp(-div*t) * norm.cdf(d1) - K * math.exp(-r*t) * norm.cdf(d2)
Put_option = K * math.exp(-r*t) * norm.cdf(-d2) - S * math.exp(-div*t) * norm.cdf(-d1)

print('Call Price:', Call_option)
print('Put Price:', Put_option)

# Greeks calculation

# For a Call

c_Delta = norm.cdf(d1)
c_Gamma = ( norm.pdf(d1)) / (S * sigma * math.sqrt(t))
c_Vega  = (S * Np_d1 * math.sqrt(t))
c_Rho   = (K * t * math.exp(-r*t) * norm.cdf(d2)) 
c_Theta =  ( -(S * Np_d1 * sigma / (2 * math.sqrt(t))) - (r * K * math.exp(-r*t) * norm.cdf(d2)) ) 


# For a Put

p_Delta = - norm.cdf(-d1)
p_Gamma = ( norm.pdf(d1)) / (S * sigma * math.sqrt(t))
p_Vega  = (S * Np_d1 * math.sqrt(t)) 
p_Rho   = (- K * t * math.exp(-r*t) * norm.cdf(-d2)) 
p_Theta = ( -(S * Np_d1 * sigma / (2 * math.sqrt(t))) + (r * K * math.exp(-r*t) * norm.cdf(-d2))) 

