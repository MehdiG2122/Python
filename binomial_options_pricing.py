# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 11:22:44 2022
@author: Ghaouti_M
"""

import math
import matplotlib.pyplot as plt
import pandas as pd

# CONSTANT DECLARTION
N = [1,10, 50,100,500,1000] # where N is an array with the number of steps
S0 = 50 # Where S0 is the spot price
K = 50 # where K is the strike price 
SIGMA = 0.2 # where SIGMA is the volatility
R = 0.02 # where R is the risk free rate
T = 10 # where T is the maturity

# temporary lists to hold the number of steps plus call/put price for later use
call_prices=[]
put_prices=[]

for N in N:
    
    # VARIABLES DECLARATION    
    U = math.exp(SIGMA * math.sqrt((T / N)))
    D = math.exp(-SIGMA * math.sqrt((T / N)))
    P = (math.exp((R * T) / N) - D) / (U - D)

    # Summing up call and put payoff outputs     
    c_sum = 0
    p_sum = 0
    for k in reversed(range(0, N+1)):
        c_sum += (math.factorial(N) / (math.factorial(k) * math.factorial(N-k))) * (P**k) * ((1-P)**(N-k)) * max(((U**k) * (D**(N-k)) * S0) - K, 0 )
        p_sum += (math.factorial(N) / (math.factorial(k) * math.factorial(N-k))) * (P**k) * ((1-P)**(N-k)) * max(K - (S0 * (U**k) * (D**(N-k))),0)
    
    # Calculating final Call and put price per steps
    C = (math.exp(-R*T)) * c_sum
    call_prices.append([N, C])
    
    P = (math.exp(-R*T)) * p_sum
    put_prices.append([N, P])




df_call = pd.DataFrame(call_prices)
df_put = pd.DataFrame(put_prices)    
    
plt.plot(df_call[0], df_call[1], color='green')
plt.show()

plt.plot(df_put[0], df_put[1], color='red')
plt.show()













