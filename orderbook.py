
import numpy as np
import pandas as pd
import random as rd
import datetime as dt
from tabulate import tabulate
import os.path
import sys
import subprocess
import time

# implement pip as a subprocess and adding/installing external lib named tabulate:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tabulate'])


######### NAOURES PART - GENERATING 5000 RANDOM ORDERS ###########

def getRandomDate():
    now_date = dt.datetime.now();
    hours = rd.randint(1, 24);
    minutes = rd.randint(1, 60)
    seconds = rd.randint(1, 60)
    delta_date = dt.timedelta(hours = hours,minutes= minutes, seconds= seconds) 
    return now_date + delta_date


def generateOrderBook():
    orderBook = np.empty((0,6))
    orderBook = np.append(orderBook,[['#ID','Time','Size','Price','type','action']],axis = 0)
    _type = np.random.permutation(('LMT', 'MKT')*2500)
    _BC =  np.random.permutation(('BUY','SELL')*2500)
    
    
    for i in range(5000):
        i=i+1
        price = 0
        randomType = _type[i-1]
        randomAction = _BC[i-1]
        if randomType == "LMT" and randomAction == "BUY": price = round(rd.uniform(100, 100.04),2)
        elif randomType == "LMT" and randomAction == "SELL": price = round(rd.uniform(100.06, 100.1),2)
        else: price = "-"
        
        now = dt.datetime.now()
        order=np.array(
            [
                [
                    'B'+str(i),
                    getRandomDate().strftime("%H:%M:%S"),
                    rd.randint(500,3000),
                    price,
                    randomType,
                    randomAction]
                ]
            )
        orderBook=np.append(orderBook,order,axis = 0)    
    return orderBook


#################################################################
#########         MEHDI PART - MATCHING ENGINE        ###########

ask = []
bid = []

def matchingEngine(ordersList):
    # Removing ordersList header with names.
    sortList = np.delete(ordersList, 0, axis=0)
    
    # Sorting list by time.
    sortList = sortList[sortList[:, 1].argsort()]
    
    # Starting iteration on each element of the orders list

    for order in sortList: 
        # Acquiring values 
        orderID, tradeDate, quantity, price, orderType, orderBS = order[0], order[1], order[2], order[3], order[4], order[5]
        
        
        ## CHECKING ORDERS BY : 1)ORDER TYPE , MARKET OR LIMI. 2) BUY OR SELL. 3) LIST LENGTH.        
        MKTBUY0 = (orderType == 'MKT') and (orderBS =='BUY') and (len(ask) == 0)
        MKTBUY1 = (orderType == 'MKT') and (orderBS =='BUY') and (len(ask) > 0)
        MKTSELL0 = (orderType == 'MKT') and (orderBS =='SELL') and (len(bid) == 0)
        MKTSELL1 = (orderType == 'MKT') and (orderBS =='SELL') and (len(bid) > 0)
        LMTBUY0 = (orderType == 'LMT') and (orderBS =='BUY') and (len(ask) == 0)
        LMTBUY1 = (orderType == 'LMT') and (orderBS =='BUY') and (len(ask) > 0)
        LMTSELL0 = (orderType == 'LMT') and (orderBS =='SELL') and (len(bid) == 0)
        LMTSELL1 = (orderType == 'LMT') and (orderBS =='SELL') and (len(bid) > 0)
       
        # ORDER WITHS NO COUNTERPARTS ARE EITHER CANCELED IF MARKET , OR ADDED TO THE PENDING EXEC LIST IF LIMIT ORDERS
        if MKTBUY0: print("/!\ ORDER", orderID, "CANCELED BY EXCHANGE - NO AVAILABLE COUNTERPART")
        if MKTSELL0: print("/!\ ORDER", orderID, "CANCELED BY EXCHANGE - NO AVAILABLE COUNTERPART")
        if LMTBUY0 : bid.append(list(order))
        if LMTSELL0 : ask.append(list(order))
        
         # ORDERS WITH COUNTERPARTS
         
        # MARKET ORDER (BUY OR SELL) - LOGIC IS AS FOLLOW : FILL ORDER QUANTITY UNTIL LEFT QUANTITY CANNOT BE FILLED. MAXIMUM WILL BE FILLED, AND IF NO MATCH AFTERTHAT, REMAINS ARE CANCELED.

        if MKTBUY1:  
            # PARTIAL EXECUTION FLAG NECESSARY FOR DECISION TREE
            partialExec = 0
            while True:                
                if len(ask) == 0 and partialExec == 1:
                    print(orderID, "REMAINING BUY ORDER WITH" , quantity, "LOTS CANNOT BE FILLED - NO AVAILABLE COUNTERPART")
                    break
                if len(ask) == 0 and partialExec == 0:
                    print("/!\ ORDER", orderID, "CANCELED BY EXCHANGE - NO AVAILABLE COUNTERPART")
                    break
                if len(ask) > 0:
                    sortedAsk = sorted(ask, key=lambda x: (x[3], x[1]), reverse=False)
                    sortedAskPrice = float(sortedAsk[0][3])
                    sortedAskSize = int(sortedAsk[0][2])
                    sortedAskID = str(sortedAsk[0][0])
                    qtyDelta = sortedAskSize - int(quantity)
                    if qtyDelta > 0: 
                        print(orderID, "BUY @MKT", sortedAskPrice, "QTY", quantity, "FILLED ||| MATCHED ORDER", sortedAskID, "AvailQty", sortedAskSize , "Price", sortedAskPrice)
                        sortedAsk[0][2] = qtyDelta
                        txtOutput(tradeDate, sortedAskPrice, "transactions.txt")                      
                        ask.clear()
                        for asks in sortedAsk: ask.append(asks)                        
                        break                        
                    else:
                        print(orderID, "BUY @MKT", sortedAskPrice, "QTY", quantity, "PARTIAL FILL" , abs(qtyDelta),"LOTS REMAINING ||| MATCHED ORDER", sortedAskID, "AvailQty", sortedAskSize , "Price", sortedAskPrice)                    
                        quantity = abs(qtyDelta)
                        sortedAsk = sortedAsk[1:]
                        txtOutput(tradeDate, sortedAskPrice, "transactions.txt") 
                        ask.clear()
                        for asks in sortedAsk: ask.append(asks)   
                        partialExec = 1 
                  

        if MKTSELL1: 
            partialExec = 0
            while True:                
                if len(bid) == 0 and partialExec == 1:
                    print(orderID, "REMAINING SELL ORDER WITH" , quantity, "LOTS CANNOT BE FILLED - NO AVAILABLE COUNTERPART")
                    break
                if len(bid) == 0 and partialExec == 0:
                    print("/!\ ORDER", orderID, "CANCELED BY EXCHANGE - NO AVAILABLE COUNTERPART")
                    break
                if len(bid) > 0:
                    sortedBid = sorted(bid, key=lambda x: (-float(x[3]), x[1]), reverse=False)
                    sortedBidPrice = float(sortedBid[0][3])
                    sortedBidSize = int(sortedBid[0][2])
                    sortedBidID = str(sortedBid[0][0])
                    qtyDelta = sortedBidSize - int(quantity)
                    if qtyDelta > 0: 
                        print(orderID, "SELL @MKT", sortedBidPrice, "QTY", quantity, "FILLED ||| MATCHED ORDER", sortedBidID, "AvailQty", sortedBidSize , "Price", sortedBidPrice)
                        sortedBid[0][2] = qtyDelta
                        txtOutput(tradeDate, sortedBidPrice, "transactions.txt")  
                        bid.clear()
                        for bids in sortedBid: bid.append(bids)                        
                        break                        
                    else:
                        print(orderID, "SELL @MKT", sortedBidPrice, "QTY", quantity, "PARTIAL FILL" , abs(qtyDelta),"LOTS REMAINING ||| MATCHED ORDER", sortedBidID, "AvailQty", sortedBidSize , "Price", sortedBidPrice)                
                        quantity = abs(qtyDelta)
                        sortedBid = sortedBid[1:]
                        txtOutput(tradeDate, sortedBidPrice, "transactions.txt")
                        bid.clear()
                        for bids in sortedBid: bid.append(bids)  
                        partialExec = 1 

                        
        # LIMIT ORDER (BUY OR SELL) - LOGIC IS AS FOLLOW : IF PRICE IS LOWER/HIGHER THAN BEST ASK/BID THEN APPEND ORDER TO THE BID/ASK PENDING LIST.
        # ELSE LIMIT ORDER IS REJECTED 
        if LMTBUY1 :
            # checking best ask price , if limit buy order is lower than best ask then append order to the pending list. 
            sortedAsk = sorted(ask, key=lambda x: (x[3], x[1]), reverse=False)      
            if price < sortedAsk[0][3]: bid.append(list(order))

            
        if LMTSELL1 : 
            # checking best ask price , if limit buy order is higher than best ask then append order to the pending list. 
            sortedBid = sorted(bid, key=lambda x: (-float(x[3]), x[1]), reverse=False)
            if price > sortedBid[0][3]: ask.append(list(order))

        
        obupdate(bid,ask,tradeDate)


#################################################################
#########         ARNAUD AND THIBAULT PART - MATCHING ENGINE        ###########
def obupdate(bid, ask, tDate):
    # sorting bid and ask lists
    sbid = sorted(bid, key=lambda x: (-float(x[3]), x[1]), reverse=False)
    sask = sorted(ask, key=lambda x: (x[3], x[1]), reverse=True) 
    nb_bid = len(sbid)
    nb_ask = len(sask)
    case1= nb_bid == 0 and nb_ask == 0 
    case2= nb_bid == 0 and nb_ask > 0 
    case3= nb_bid > 0 and nb_ask == 0 
    case4= nb_bid > 0 and nb_ask > 0 
    topBids = [bids[:4] for bids in sbid]
    topAsks = [asks[:4] for asks in sask]
    if case1: print("################# LIMIT ORDER BOOK IS EMTPY ! ###############")        
    elif case2:
        print(" ")
        print("==================================================================================================")
        print('################# ASKS #################')
        print(tabulate(topAsks[-10:], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid",showindex=True))    
        print('## PRICE:', (sask[-1][3]),'|| SPREAD: - ##')
        print(tabulate([["-","-","-","-"]], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid",showindex=True))
        print('################# BIDS #################')    
        print("==================================================================================================")
        print(" ")
    elif case3:
        print(" ")
        print("==================================================================================================")
        print('################# ASKS #################')
        print(tabulate([["-","-","-","-"]], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid",showindex=True))    
        print('## PRICE:', (sbid[0][3]),'|| SPREAD: - ##')
        print(tabulate(topBids[:10], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid",showindex=True))
        print('################# BIDS #################')   
        print("==================================================================================================")
        print(" ")        
    elif case4:
        print(" ")
        print("==================================================================================================")
        print('################# ASKS #################')
        print(tabulate(topAsks[-10:], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid", showindex=True))    
        print('## PRICE:', round((float(sbid[0][3]) + float(sask[-1][3])), 2) / 2 ,'|| SPREAD:', round(abs(float(sbid[0][3]) - float(sask[-1][3])), 2),'##')
        print(tabulate(topBids[:10], headers =["Order ID", "Time", "Qty", "Price"], tablefmt="fancy_grid",showindex=True))
        print('################# BIDS #################')    
        print("==================================================================================================")
        print(" ")
        txtOutput(tDate, abs(float(sbid[0][3]) - float(sask[-1][3])), "spread.txt")
    else: print('Pas Possible')    
    

#################################################################

#################################################################
#########         ROBIN AND DANIEL PART - MATCHING ENGINE        ###########
def txtOutput(tDate, tVal, tName):
    # Check if file exists. If yes, then append line to it. Else create it and write lines.
    checkFile = os.path.isfile(tName) 
    if checkFile is False:
        with open(tName, 'w') as f:
            f.write(f'{tDate};{tVal}\n')
    else:
        with open(tName, 'a') as f:
            f.write(f'{tDate};{tVal}\n')
    
#################################################################

def excelOutput(fileName):
    
    data = pd.read_csv(fileName, sep=";", header=None)
    data.columns = ["Time", "Value"]    
    
    # Create a Pandas dataframe from the data.
    df = pd.DataFrame(data)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    excel_file = fileName.replace(".txt", ".xlsx")
    sheet_name = fileName.replace(".txt", "")
    
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    # Create a chart object.
    chart = workbook.add_chart({'type': 'area'})
    
    # Configure the series of the chart from the dataframe data.    
    chart.add_series({
        'categories': [fileName.replace(".txt", ""), 1, 0, len(df), 0],
        'values':     [fileName.replace(".txt", ""), 1, 1, len(df), 1],
    })
    
    # Configure the chart axes.
    chart.set_x_axis({'name': 'Time', 'position_axis': 'on_tick'})
    chart.set_y_axis({'name': fileName.replace(".txt", "") + " value", 'major_gridlines': {'visible': False}})
    
    # Turn off chart legend. It is on by default in Excel.
    chart.set_legend({'position': 'none'})
    
    # Insert the chart into the worksheet.
    worksheet.insert_chart('D2', chart)
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

start = time.time()
matchingEngine(generateOrderBook())
excelOutput('spread.txt')
excelOutput('transactions.txt')
print("Script executed in " , time.time() - start, " seconds")

#################################################################
