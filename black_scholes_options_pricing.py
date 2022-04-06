#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 17:23:47 2022

@author: mehdi
"""

import math
from scipy.stats import norm


# VARIABLE DECLARATION

S = 50 # Current underlying spot price
K = 45 # Strike price
r = 0.025 # Risk free rate
t = 3 # Time to maturity
sigma = 0.2 # underlying volatility
div = 0 # Dividend yield


d1 = (math.log(S/K) + (r + ((sigma**2) / 2) ) * t) / ( sigma * math.sqrt(t))
d2 = d1 - sigma * math.sqrt(t)


Call_option = S * math.exp(-div*t) * norm.cdf(d1) - K * math.exp(-r*t) * norm.cdf(d2)
Put_option = K * math.exp(-r*t) * norm.cdf(-d2) - S * math.exp(-div*t) * norm.cdf(-d1)

