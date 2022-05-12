#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  2 21:57:40 2022

@author: mehdi
"""

import pandas as pd
import numpy as np
from pandas_datareader import data as pdr

# Importing dataset
congres_op = pd.read_csv('./all_transactions.csv')

# Cleaning dataset
congres_op['disclosure_date'] = pd.to_datetime(congres_op['disclosure_date']) 
congres_op['transaction_date'] = pd.to_datetime(congres_op['transaction_date'], errors = 'coerce') 
congres_op['type'] = np.where(congres_op['type'] == 'purchase', 'BUY', 'SELL')
data = [congres_op['disclosure_date'], congres_op['transaction_date'] , congres_op['ticker'] ,congres_op['type'] ,congres_op['representative']]

# Working dataset
df_op = pd.concat(data, axis=1)
df_op.drop(df_op[df_op.ticker == '--'].index, inplace=True)

start_date = min(df_op.transaction_date)
end_date = max(df_op.transaction_date)
ticker_list = list(set(df_op.ticker))

market_data = pdr.get_data_yahoo(ticker_list, start=start_date, end=end_date)['Adj Close']

