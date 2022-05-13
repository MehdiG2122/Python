# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 14:22:07 2022

@author: Mehdi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn_extra.cluster import KMedoids
from sklearn.pipeline import make_pipeline
import tensorflow as tf


############ DATA CLEANING ############ 
# Import dataset and cleaning

spfile = pd.read_csv('sp500_with_stock.csv')
spfile.columns = [ x.replace("WIKI/", "").replace(" - Adj. Close", "") for x in spfile.columns]
spfile.index = spfile['Date']
spfile.index = pd.to_datetime(spfile.index)
spfile = spfile.drop(['Date'], axis=1)
spfile['SP500'] = pd.to_numeric(spfile['SP500'], errors='coerce')
spfile.astype('float')

########################################


############ RETURNS CALCULATION ############
# Calculating returns for spfile and sp500

returns_spfile = spfile.pct_change().fillna(0)
returns_spfile.drop(index=returns_spfile.index[0], axis=0, inplace=True)
returns_spfile.sort_index(inplace=True)

##############################################



############ ASSET SELECTION PROCESS ############

# 1  - Randomly select K assets from index assets

rand_comp = returns_spfile[returns_spfile.columns[1:]].sample(n=50,axis='columns')

# 2 -  Assets with returns that are the most correlated to SP500 returns

corrmat = returns_spfile.corr()['SP500'].sort_values(ascending=False)[1:51]
corrlist = corrmat.index
corr_comp = returns_spfile[corrlist]

# 3 - Clustering methods 
returns_kmedoids =returns_spfile.drop(columns='SP500')
Returns_K2 = returns_kmedoids.unstack().unstack()
col_name = returns_kmedoids.columns.tolist()
Portfolio = KMedoids(n_clusters=5, random_state=0)
Portfolio.fit(Returns_K2)
label = Portfolio.labels_
label = label.tolist()
df_final = pd.DataFrame({'Ticker':col_name,'Portfolio':label})
ptf = df_final['Ticker'].loc[df_final['Portfolio']==1].reset_index(drop=True)
clust_comp = returns_spfile[ptf]


# 4 - Assembling list with strategies and related names

strategies = [rand_comp, corr_comp, clust_comp]
stratnames = ['Random Assets', 'Most correlated','Clustering']

#################################################


# ############ MODEL CONSTRUCTION ###############

for strat, stratname in zip(strategies,stratnames):
    # Split train and test sets
    
    X_train, X_test, y_train, y_test = train_test_split(strat, returns_spfile['SP500'], test_size=0.20, random_state = 0)
       
                                                     
    # Model architecture
    
    ## 1 - Stochastic Gradient Descent Regressor with squared Loss
    
    reg = linear_model.SGDRegressor(loss='squared_loss', max_iter = np.ceil(10**6 / X_train.shape[0]), fit_intercept=False, learning_rate='optimal', warm_start=True)
    reg.fit(X_train,y_train)
    
    # Constraining sum of weights to 1 and applying it to the model.
    
    w = np.array(reg.coef_ / tf.reduce_sum(reg.coef_))
    reg.coef_ = w
    
    # Testing score on test sets
    
    print(f'Strategy: {stratname} - Squared loss function under constraint')
    print('Model Train score:', reg.score(X_train, y_train))
    print(f'Total allocation weight {round(sum(reg.coef_), 2)}')
    X_test.sort_index(inplace=True)
    y_test.sort_index(inplace=True)
    
    # Predicting with updated coefs 

    print('Model Test score:', reg.score(X_test, y_test))
    y_pred = pd.DataFrame(reg.predict(X_test))
    y_pred.index = X_test.index
    
    plt.figure(figsize=(20,5))
    plt.plot(y_test, color='blue', label=f'Actual returns | Avg:{round(np.average(y_test) * 100, 2)}%')
    plt.plot(y_pred, color = 'red', label=f'Predicted returns | Avg: {round(np.average(y_pred) * 100, 2)}%')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.title(f'Predicted vs Actual returns - {stratname} - Squared Error')
    plt.legend()
    
    # Evaluation metrics
    
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import max_error
    
    mse = mean_squared_error(y_test, y_pred)
    print(f'MSE : {mse}')
    print('')
    
    ## 2 - Stochastic Gradient Descent Regressor with Downside risk Loss
    
    reg2 = linear_model.SGDRegressor(loss='squared_epsilon_insensitive', max_iter = np.ceil(10**6 / X_train.shape[0]), fit_intercept=False, epsilon=0.0, learning_rate='optimal', warm_start=True)
    reg2.fit(X_train,y_train)
    
    # Constraining sum of weights to 1 and applying it to the model.
    
    w = np.array(reg2.coef_ / tf.reduce_sum(reg2.coef_))
    reg2.coef_ = w
    
    # Testing score on test sets
    
    print(f'Strategy: {stratname} - Downside Risk loss function')
    print('Model Train score:', reg2.score(X_train, y_train))
    print(f'Total allocation weight {round(sum(reg2.coef_), 2)}')
    X_test.sort_index(inplace=True)
    y_test.sort_index(inplace=True)
    
    # Predicting with updated coefs 

    print('Model Test score:', reg2.score(X_test, y_test))
    y_pred = pd.DataFrame(reg2.predict(X_test))
    y_pred.index = X_test.index
    
    plt.figure(figsize=(20,5))
    plt.plot(y_test, color='blue', label=f'Actual returns | Avg:{round(np.average(y_test) * 100, 2)}%')
    plt.plot(y_pred, color = 'red', label=f'Predicted returns | Avg: {round(np.average(y_pred) * 100, 2)}%')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.title(f'Predicted vs Actual returns - {stratname} - Downside Risk')
    plt.legend()
    
    # Evaluation metrics
    
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import max_error
    
    max_error = max_error(y_test, y_pred)
    print(f'Max error : {max_error}')
    print('')








