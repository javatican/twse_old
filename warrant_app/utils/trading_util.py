import json
import math
import matplotlib
from matplotlib.finance import candlestick_ohlc
import os

from core.models import Trading_Date, Stock_Item
import numpy as np
from warrant_app.utils.dateutil import convertToDate, DateEncoder


def moving_avg(input_array, DAY_AVERAGE):
    item_count = input_array.size
    if item_count < DAY_AVERAGE: 
        raise Exception
    avg_array = np.zeros(item_count - DAY_AVERAGE + 1)
    for j in np.arange(DAY_AVERAGE):
        sli = slice(j, item_count - DAY_AVERAGE + j + 1)
        avg_array = avg_array + input_array[sli]
    avg_array = avg_array / DAY_AVERAGE
    return avg_array
def calc_stochastic_oscillator_for_stock(stock, trading_item_list=None, LOOK_BACK_PERIOD=14, K_SMOOTHING=3, D_MOVING_AVERAGE=3):
    # this function is used to recalculate stochastic_oscillator values for a specific stock
    # if trading_item_list are given, will be used for calculation. Otherwise hit the DB and get all trading items for the stock.
    # default parameters are for 14-day stochastic oscillator
    strategy_items_to_update = []
    if trading_item_list:
        items = trading_item_list
    else:
        items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date')
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    for item in items:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array(highest_price_list)
    lowest_array = np.array(lowest_price_list)
    closing_array = np.array(closing_price_list)
    k_array, d_array = _calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD, K_SMOOTHING, D_MOVING_AVERAGE)
    # ryan note: 
    # 1. the size of k_array is the same as that of d_array
    # 2. the size of k_array is 'LOOK_BACK_PERIOD + K_SMOOTHING + D_MOVING_AVERAGE - 3' shorter than that of items
    for j, item in enumerate(items[LOOK_BACK_PERIOD + K_SMOOTHING + D_MOVING_AVERAGE - 3:]):
        tts = item.strategy
        if LOOK_BACK_PERIOD==14:
            tts.fourteen_day_k = k_array[j]
            tts.fourteen_day_d = d_array[j]
        else:
            tts.seventy_day_k = k_array[j]
            tts.seventy_day_d = d_array[j]
        strategy_items_to_update.append(tts)
    return strategy_items_to_update
                        
def _calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD=14, K_SMOOTHING=3, D_MOVING_AVERAGE=3):
    item_count = closing_array.size
    #print "item_count=%s" % item_count
    min_item_count = LOOK_BACK_PERIOD + K_SMOOTHING - 1 + D_MOVING_AVERAGE - 1
    if item_count < min_item_count: 
        raise Exception
    k_array = np.zeros(item_count - LOOK_BACK_PERIOD + 1)
    for j, item in enumerate(closing_array[LOOK_BACK_PERIOD - 1:]):
        highest_price = np.max(highest_array[j:LOOK_BACK_PERIOD + j])
        #print "highest_price=%s" % highest_price
        lowest_price = np.min(lowest_array[j:LOOK_BACK_PERIOD + j])
        #print "lowest_price=%s" % lowest_price
        if highest_price - lowest_price > 0:
            k_value = 100 * (item - lowest_price) / (highest_price - lowest_price)
            #print "closing_price=%s" % item
            #print "k_value=%s" % k_value
            k_array[j] = k_value
        else:
            print "highest_price=lowest_price @ %s" % lowest_price
            continue
        # calculate moving averages of 'K_SMOOTHING' values of K
        smoothed_k_array = moving_avg(k_array, K_SMOOTHING)
        # calculate moving averages of smoothed K (ie. D)
        d_array = moving_avg(smoothed_k_array, D_MOVING_AVERAGE)
    return np.around(smoothed_k_array[D_MOVING_AVERAGE - 1:], 2), np.around(d_array, 2)

def wilder_smoothing(prev, curr, SMOOTHING_FACTOR=14, use_sum=True):
    if use_sum:
        return prev - (prev / SMOOTHING_FACTOR) + curr
    else:
        return (prev * (SMOOTHING_FACTOR - 1) + curr) / SMOOTHING_FACTOR
    
def recalc_all_di_adx_for_stock(stock, trading_item_list=None, SMOOTHING_FACTOR=14):
    # this function is used to recalculate 'all' ADX related values for a specific stock
    # if trading_item_list are given, will be used for calculation. Otherwise hit the DB and get all trading items for the stock.
    strategy_items_to_update = []
    if trading_item_list:
        items = trading_item_list
    else:
        items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date')
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    for item in items:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array(highest_price_list)
    lowest_array = np.array(lowest_price_list)
    closing_array = np.array(closing_price_list)
    tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array = calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
    # ryan note:
    # 1. the size of tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array are the same
    # 2. the size of adx_array is '2*SMOOTHING_FACTOR-1' shorter than that of items
    for j, item in enumerate(items[SMOOTHING_FACTOR + SMOOTHING_FACTOR - 1:]):
        tts = item.strategy
        tts.tr14 = tr14_array[j]
        tts.pdm14 = pdm14_array[j]
        tts.ndm14 = ndm14_array[j]
        if not math.isnan(pdi14_array[j]): tts.pdi14 = pdi14_array[j]
        if not math.isnan(ndi14_array[j]): tts.ndi14 = ndi14_array[j]
        if not math.isnan(adx_array[j]): tts.adx = adx_array[j]                        
        strategy_items_to_update.append(tts)
    return strategy_items_to_update

def update_di_adx_for_stock(stock, trading_item_list=None, SMOOTHING_FACTOR=14):
    # this function is used to update missing ADX related values for a stock
    # trading_item_list[0] is assumed to contain tr14, pdm14, ndm14, adx values, and will be used to calculate the following missing values.
    # trading_item_list can not be null. 
    strategy_items_to_update = []
    if not trading_item_list:
        raise Exception
    else:
        items = trading_item_list
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    for item in items:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array(highest_price_list)
    lowest_array = np.array(lowest_price_list)
    closing_array = np.array(closing_price_list)
    previous_strategy=items[0].strategy
    tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array = calc_di_adx_pairwise(highest_array, lowest_array, closing_array, previous_strategy, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
#
    for j, item in enumerate(items[1:]):
        tts = item.strategy
        tts.tr14 = tr14_array[j]
        tts.pdm14 = pdm14_array[j]
        tts.ndm14 = ndm14_array[j]
        if not math.isnan(pdi14_array[j]): tts.pdi14 = pdi14_array[j]
        if not math.isnan(ndi14_array[j]): tts.ndi14 = ndi14_array[j]
        if not math.isnan(adx_array[j]): tts.adx = adx_array[j]                        
        strategy_items_to_update.append(tts)
    return strategy_items_to_update                       
                        
def calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=14):
    # Average True Range: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr
    # Average Directional Index: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
    item_count = closing_array.size
    min_item_count = SMOOTHING_FACTOR + SMOOTHING_FACTOR
    if item_count < min_item_count: 
        raise Exception
    # tr(True Range) array, pdm(Plus Directional Movement) array and ndm(Minus Directional Movement) array are calculated pairwise, so
    # the size of them are 'item_count-1'
    tr_array = np.zeros(item_count - 1)
    pdm_array = np.zeros(item_count - 1)
    ndm_array = np.zeros(item_count - 1)
    # below are arrays to store the smoothed tr,pdm,ndm values(14-day SMOOTHING_FACTOR)
    # so their sizes are '(item_count-1)-(SMOOTHING_FACTOR-1)' which is equal to 'item_count-SMOOTHING_FACTOR'
    tr14_array = np.zeros(item_count - SMOOTHING_FACTOR)
    pdm14_array = np.zeros(item_count - SMOOTHING_FACTOR)
    ndm14_array = np.zeros(item_count - SMOOTHING_FACTOR)
    # adx_array store the smoothed DX values(14-day SMOOTHING_FACTOR)
    # so its size is '(item_count-SMOOTHING_FACTOR)-(SMOOTHING_FACTOR-1)'   
    adx_array = np.zeros(item_count - SMOOTHING_FACTOR - SMOOTHING_FACTOR + 1)
    #
    for i in np.arange(1, item_count):
        # Calculate True Range
        # TR is defined as the greatest of the following:
        # Method 1: Current High less the current Low
        # Method 2: Current High less the previous Close (absolute value)
        # Method 3: Current Low less the previous Close (absolute value)
        tr = max(highest_array[i] - lowest_array[i],
               abs(highest_array[i] - closing_array[i - 1]),
               abs(lowest_array[i] - closing_array[i - 1]))
        # Calculate Plus Directional Movement(+DM)
        # Directional movement is positive (plus) when the current high minus the prior high is greater than 
        # the prior low minus the current low. 
        # This so-called Plus Directional Movement (+DM) then equals the current high minus the prior high, 
        # provided it is positive. A negative value would simply be entered as zero.
        pdm = 0
        if highest_array[i] - highest_array[i - 1] > lowest_array[i - 1] - lowest_array[i]:
            pdm = max(highest_array[i] - highest_array[i - 1], 0)
        # Calculate Minus Directional Movement(-DM)
        # Directional movement is negative (minus) when the prior low minus the current low is greater than 
        # the current high minus the prior high. 
        # This so-called Minus Directional Movement (-DM) equals the prior low minus the current low, 
        # provided it is positive. A negative value would simply be entered as zero.
        ndm = 0
        if lowest_array[i - 1] - lowest_array[i] > highest_array[i] - highest_array[i - 1] :
            ndm = max(lowest_array[i - 1] - lowest_array[i], 0)
        tr_array[i - 1] = tr
        pdm_array[i - 1] = pdm
        ndm_array[i - 1] = ndm
    # Smooth TR,+DM,-DM using the Wilder's smoothing techniques. 
    # First TR14 = Sum of first 14 periods of TR1
    # Second TR14 = First TR14 - (First TR14/14) + Current TR1
    # Subsequent Values = Prior TR14 - (Prior TR14/14) + Current TR1
    for i in np.arange(tr14_array.size):
        if i == 0:
            tr14 = np.sum(tr_array[:SMOOTHING_FACTOR])
            pdm14 = np.sum(pdm_array[:SMOOTHING_FACTOR])
            ndm14 = np.sum(ndm_array[:SMOOTHING_FACTOR])
        else:
            tr14 = wilder_smoothing(tr14_array[i - 1], tr_array[SMOOTHING_FACTOR + i - 1])
            pdm14 = wilder_smoothing(pdm14_array[i - 1], pdm_array[SMOOTHING_FACTOR + i - 1])
            ndm14 = wilder_smoothing(ndm14_array[i - 1], ndm_array[SMOOTHING_FACTOR + i - 1])
        tr14_array[i] = tr14
        pdm14_array[i] = pdm14
        ndm14_array[i] = ndm14
        # Calculate +DI14, -DI14
        # Divide the 14-day smoothed Plus Directional Movement (+DM) by the 14-day smoothed True Range 
        # to find the 14-day Plus Directional Indicator (+DI14). Multiply by 100 to move the decimal point two places. 
        # The same for -DI14
    pdi14_array = 100 * pdm14_array / tr14_array
    ndi14_array = 100 * ndm14_array / tr14_array
    # Calculate DX
    # The Directional Movement Index (DX) equals the absolute value of +DI14 less -DI14 
    # divided by the sum of +DI14 and -DI14.
    dx_array = 100 * np.abs(pdi14_array - ndi14_array) / (pdi14_array + ndi14_array) 
    # Calculate ADX
    # The first ADX value is simply a 14-day average of DX. 
    # Subsequent ADX values are smoothed by multiplying the previous 14-day ADX value by 13, 
    # adding the most recent DX value and dividing this total by 14.
    for i in np.arange(adx_array.size):
        if i == 0:
            adx = np.average(dx_array[:SMOOTHING_FACTOR]) 
        else:
            adx = wilder_smoothing(adx_array[i - 1], dx_array[SMOOTHING_FACTOR + i - 1], use_sum=False)
        adx_array[i] = adx
    
    return tr14_array[SMOOTHING_FACTOR - 1:], pdm14_array[SMOOTHING_FACTOR - 1:], ndm14_array[SMOOTHING_FACTOR - 1:], pdi14_array[SMOOTHING_FACTOR - 1:], ndi14_array[SMOOTHING_FACTOR - 1:], adx_array
    
def calc_di_adx_pairwise(highest_array, lowest_array, closing_array, previous_strategy, SMOOTHING_FACTOR=14):
    # This function is used to calculate DI and ADX for a range of trading date assuming there were existing values for DI and ADX before the trading date range.
    # That is if we are calculating data from date1 to date2,  DI, ADX for 'date1-1day' is existed  and will be used for calculating DI, ADX for date1. 
    # highest_array, lowest_array, closing_array do include values from previous_trading
    
    # Average True Range: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr
    # Average Directional Index: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
    item_count = closing_array.size
    min_item_count = 2
    if item_count < min_item_count: 
        raise Exception
    tr_array = np.zeros(item_count-1)
    pdm_array = np.zeros(item_count-1)
    ndm_array = np.zeros(item_count-1)
    tr14_array = np.zeros(item_count-1)
    pdm14_array = np.zeros(item_count-1)
    ndm14_array = np.zeros(item_count-1)  
    adx_array = np.zeros(item_count-1)
    #
    for i in np.arange(1,item_count):
        # Calculate True Range
        # TR is defined as the greatest of the following:
        # Method 1: Current High less the current Low
        # Method 2: Current High less the previous Close (absolute value)
        # Method 3: Current Low less the previous Close (absolute value)
        tr = max(highest_array[i] - lowest_array[i],
               abs(highest_array[i] - closing_array[i - 1]),
               abs(lowest_array[i] - closing_array[i - 1]))
        # Calculate Plus Directional Movement(+DM)
        # Directional movement is positive (plus) when the current high minus the prior high is greater than 
        # the prior low minus the current low. 
        # This so-called Plus Directional Movement (+DM) then equals the current high minus the prior high, 
        # provided it is positive. A negative value would simply be entered as zero.
        pdm = 0
        if highest_array[i] - highest_array[i - 1] > lowest_array[i - 1] - lowest_array[i]:
            pdm = max(highest_array[i] - highest_array[i - 1], 0)
        # Calculate Minus Directional Movement(-DM)
        # Directional movement is negative (minus) when the prior low minus the current low is greater than 
        # the current high minus the prior high. 
        # This so-called Minus Directional Movement (-DM) equals the prior low minus the current low, 
        # provided it is positive. A negative value would simply be entered as zero.
        ndm = 0
        if lowest_array[i - 1] - lowest_array[i] > highest_array[i] - highest_array[i - 1] :
            ndm = max(lowest_array[i - 1] - lowest_array[i], 0)
        tr_array[i - 1] = tr
        pdm_array[i - 1] = pdm
        ndm_array[i - 1] = ndm
    # Smooth TR,+DM,-DM using the Wilder's smoothing techniques. 
    # Subsequent Values = Prior TR14 - (Prior TR14/14) + Current TR1
    for i in np.arange(item_count-1):
        if i == 0:
            tr14 = wilder_smoothing(float(previous_strategy.tr14), tr_array[i])
            pdm14 = wilder_smoothing(float(previous_strategy.pdm14), pdm_array[i])
            ndm14 = wilder_smoothing(float(previous_strategy.ndm14), ndm_array[i])
        else:
            tr14 = wilder_smoothing(tr14_array[i - 1], tr_array[i])
            pdm14 = wilder_smoothing(pdm14_array[i - 1], pdm_array[i])
            ndm14 = wilder_smoothing(ndm14_array[i - 1], ndm_array[i])
        tr14_array[i] = tr14
        pdm14_array[i] = pdm14
        ndm14_array[i] = ndm14
        # Calculate +DI14, -DI14
        # Divide the 14-day smoothed Plus Directional Movement (+DM) by the 14-day smoothed True Range 
        # to find the 14-day Plus Directional Indicator (+DI14). Multiply by 100 to move the decimal point two places. 
        # The same for -DI14
    pdi14_array = 100 * pdm14_array / tr14_array
    ndi14_array = 100 * ndm14_array / tr14_array
    # Calculate DX
    # The Directional Movement Index (DX) equals the absolute value of +DI14 less -DI14 
    # divided by the sum of +DI14 and -DI14.
    dx_array = 100 * np.abs(pdi14_array - ndi14_array) / (pdi14_array + ndi14_array) 
    # Calculate ADX
    # The first ADX value is simply a 14-day average of DX. 
    # Subsequent ADX values are smoothed by multiplying the previous 14-day ADX value by 13, 
    # adding the most recent DX value and dividing this total by 14.
    for i in np.arange(item_count-1):
        if i == 0:
            adx = wilder_smoothing(float(previous_strategy.adx), dx_array[i], use_sum=False)
        else:
            adx = wilder_smoothing(adx_array[i - 1], dx_array[i], use_sum=False)
        adx_array[i] = adx
    
    return tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array
    

def pre_filtering_bull(data_array, LONG_K_LEVEL, ADX_LEVEL):
    # Bull candidate target: long term bull but in consolidating lately
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: adx are below ADX_LEVEL(eg 15)
    long_k=data_array[0]
    adx=data_array[6]
    for data in long_k:
        if data<LONG_K_LEVEL: return False 
    for data in adx:
        if data>ADX_LEVEL: return False 
    return True

def pre_filtering_bear(data_array, LONG_K_LEVEL, ADX_LEVEL):
    # Bear candidate target: long term bear but in consolidating lately
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: adx are below ADX_LEVEL(eg 15)
    long_k=data_array[0]
    adx=data_array[6]
    for data in long_k:
        if data>LONG_K_LEVEL: return False 
    for data in adx:
        if data>ADX_LEVEL: return False 
    return True

def breakout3_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout 3rd day target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last 3 days' k are above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k=data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    if short_k[-2] < SHORT_K_LEVEL: return False
    if short_k[-3] < SHORT_K_LEVEL: return False
    if short_k.size>3:
        for data in short_k[:-3]:
            if data >= SHORT_K_LEVEL: return False
    return True

def breakout3_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout 3rd day target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last 3 days' k are below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k=data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    if short_k[-2] > SHORT_K_LEVEL: return False
    if short_k[-3] > SHORT_K_LEVEL: return False
    if short_k.size>3:
        for data in short_k[:-3]:
            if data <= SHORT_K_LEVEL: return False 
    return True

def breakout2_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout 2nd day target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last two days' k are above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k=data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    if short_k[-2] < SHORT_K_LEVEL: return False
    for data in short_k[:-2]:
        if data >= SHORT_K_LEVEL: return False
    return True

def breakout2_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout 2nd day target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last two days' k are below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k=data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    if short_k[-2] > SHORT_K_LEVEL: return False
    for data in short_k[:-2]:
        if data <= SHORT_K_LEVEL: return False 
    return True

def breakout_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last k is above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k=data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    for data in short_k[:-1]:
        if data >= SHORT_K_LEVEL: return False
    return True

def breakout_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last k is below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k=data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    for data in short_k[:-1]:
        if data <= SHORT_K_LEVEL: return False 
    return True

def watch_list_bull(data_array, SHORT_K_LEVEL):
    # Bull watch target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's, all are below  SHORT_K_LEVEL(eg 80) but the last k is between SHORT_K_LEVEL(eg 80) and SHORT_K_LEVEL-SHORT_K_WINDOW(eg 70)
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    SHORT_K_WINDOW=10
    short_k=data_array[2]
    for data in short_k:
        if data > SHORT_K_LEVEL: return False 
    if short_k[-1] < SHORT_K_LEVEL-SHORT_K_WINDOW: return False
    return True

def watch_list_bear(data_array, SHORT_K_LEVEL):
    # Bear watch target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's, all are above  SHORT_K_LEVEL(eg 20) but the last k is between SHORT_K_LEVEL(eg 20) and SHORT_K_LEVEL+SHORT_K_WINDOW(eg 30)
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    SHORT_K_WINDOW=10
    short_k=data_array[2]
    for data in short_k:
        if data < SHORT_K_LEVEL: return False 
    if short_k[-1] > SHORT_K_LEVEL+SHORT_K_WINDOW: return False
    return True

def _is_incrementing(data_array):
    # assuming input array is 1D
    array_1=data_array[1:]
    array_2=data_array[:-1]
    diff=array_1-array_2
    count = np.sum((diff>=0).astype(int))
    if count != array_1.size: 
        return False
    else:
        return True
    
def _is_decrementing(data_array):
    # assuming input array is 1D
    array_1=data_array[1:]
    array_2=data_array[:-1]
    diff=array_1-array_2
    count = np.sum((diff<=0).astype(int))
    if count != array_1.size: 
        return False
    else:
        return True
    
    
def stochastic_pop_drop_plot(stock_symbol, end_date=None):
    _SHOW_LEGEND=False
    #***preparing data
    
    if not end_date:
        date_list = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[:120]
        start_date=date_list[len(date_list)-1]
        end_date=date_list[0]
    else:         
        #end_date format : eg. '20150401'
        end_date=convertToDate(end_date)
        date_list = Trading_Date.objects.filter(trading_date__lte=end_date).values_list('trading_date', flat=True).order_by('-trading_date')[:120]
        start_date=date_list[len(date_list)-1]
        end_date=date_list[0]
    directory="ipython/stock_strategy/%s" % end_date.strftime("%Y%m%d")
    if not os.path.exists(directory):
        os.makedirs(directory)
    fname = "%s/%s_stoch_osci_%s_%s" % (directory, stock_symbol, start_date, end_date)
    filename = '%s.txt' % fname
    if not os.path.isfile(filename):
        stock=Stock_Item.objects.get_by_symbol(stock_symbol)
        entries = stock.twse_trading_list.filter(trading_date__gte=start_date, 
                                                 trading_date__lte=end_date, 
                                                 strategy__seventy_day_k__isnull=False).select_related('strategy').order_by('trading_date') 
        price_data=[]
        long_kd_data=[]
        short_kd_data=[]    
        adx_data=[]          
        for entry in entries:                    
            price_data.append((entry.trading_date, 
                       float(entry.opening_price), 
                       float(entry.highest_price), 
                       float(entry.lowest_price), 
                       float(entry.closing_price), 
                       float(entry.trade_volume)))
            long_kd_data.append((entry.trading_date, 
                       float(entry.strategy.seventy_day_k), 
                       float(entry.strategy.seventy_day_d)))
            short_kd_data.append((entry.trading_date, 
                       float(entry.strategy.fourteen_day_k), 
                       float(entry.strategy.fourteen_day_d)))
            adx_data.append((entry.trading_date, 
                       float(entry.strategy.pdi14), 
                       float(entry.strategy.ndi14),
                       float(entry.strategy.adx)))
        # write to file
        json_data = {'%s_price' % stock_symbol : price_data, 
                     '%s_70kd' % stock_symbol : long_kd_data, 
                     '%s_14kd' % stock_symbol : short_kd_data, 
                     '%s_adx' % stock_symbol : adx_data }
        with open(filename, 'w') as fp:
            json.dump(json_data, fp, cls=DateEncoder)
    #
    with open(filename, 'r') as fp:
        json_data = json.load(fp) 
    price_data = json_data['%s_price' % stock_symbol ] 
    long_kd_data = json_data['%s_70kd' % stock_symbol ] 
    short_kd_data = json_data['%s_14kd' % stock_symbol ] 
    adx_data = json_data['%s_adx' % stock_symbol ] 
    #***preparing plot
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt 
#    
    fig, ax = plt.subplots()
    trading_date_list = [] 
    volume_list = [] 
    opening_price_list = []
    closing_price_list = []
    for i, item in enumerate(price_data):
        trading_date_list.append(item[0])
        opening_price_list.append(item[1])
        closing_price_list.append(item[4])
        volume_list.append(item[5]/1000)
        # store a list of continuous integers for the 'float' date.
        # This is needed for finance lib candlestick_ohlc() to show continuous bar and whiskers without gap.
        item[0] = i + 1
    candlestick_ohlc(ax, price_data, width=0.8, colorup='r', colordown='g')
    N = len(trading_date_list)
    x_pos = np.arange(1, N + 1)
    #
    ax.set_ylabel('price')
    ax.set_title('%s price chart' % stock_symbol)
    ax.set_xticks(x_pos[::10])
    ax.set_xticks(x_pos, minor=True)
    ax.set_xticklabels(trading_date_list[::10], rotation=45)
    ax.grid(color='c', linestyle='--', linewidth=1)
    # to show several axes objects in the same figure, here adjust the y limits of the first axes, so there is space at the bottom to show other axes.
    pad = 1.2
    yl = ax.get_ylim()
    y_tick_gap=math.ceil((yl[1]-yl[0])/5)
    ax.yaxis.set_ticks(np.arange(yl[0], yl[1], y_tick_gap))
    #ax.locator_params(tight=True, axis='y',nbins=4)
    ax.set_ylim(yl[0] - (yl[1] - yl[0]) * pad, yl[1])
    # add a 2nd axes for volumes
    # axes position paramters here:
    X_START=0.125
    X_END=0.9
    Y_START=0.52
    Y_RANGE=0.1
    Y_GAP=0.0
    ax2 = ax.twinx()
    ax2.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
    # change into nd array
    opening_price_arr = np.asarray(opening_price_list)
    closing_price_arr = np.asarray(closing_price_list)
    volume_arr = np.asarray(volume_list)
    down = opening_price_arr - closing_price_arr > 0
    up = opening_price_arr - closing_price_arr < 0
    no_change = opening_price_arr - closing_price_arr == 0
    ax2.bar(x_pos[up], volume_arr[up], color='red', width=0.8, align='center')
    ax2.bar(x_pos[down], volume_arr[down], color='green', width=0.8, align='center')
    ax2.bar(x_pos[no_change], volume_arr[no_change], color='yellow', width=0.8, align='center')
    ax2.locator_params(tight=True, axis='y',nbins=4)
    ax2.set_ylabel('volume')
    ax2.grid(color='0.8', linestyle='--', linewidth=1)
    # add a 3rd axes for 70-day k/d
    ax3 = ax.twinx()
    Y_START=Y_START-Y_RANGE-Y_GAP
    ax3.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
    seventy_k=[]
    seventy_d=[]
    for i, item in enumerate(long_kd_data):
        seventy_k.append(item[1])
        seventy_d.append(item[2])
        
    # change into nd array
    seventy_k_arr = np.asarray(seventy_k)
    seventy_d_arr = np.asarray(seventy_d)
    # blue line for 70-day k,  red line for 70-day d
    line_70k=ax3.plot(x_pos, seventy_k_arr, 'b-', label='%K(70,3)')
    line_70d=ax3.plot(x_pos, seventy_d_arr, 'r-', label='%D(3)')
    # black horizontal line for 50 mark
    line_50_mark=ax3.plot([x_pos[0],x_pos[-1]], [50,50], 'y-',linewidth=2)
    #
    ax3.locator_params(tight=True, axis='y',nbins=5)
    ax3.grid(color='c', linestyle='--', linewidth=1)
    ax3.set_ylabel('STO')
    if _SHOW_LEGEND:
        ax3.legend(handles=[line_70k[0],line_70d[0]], ncol=2, loc='upper left', prop={'size':10})
    
    # add a 4th axes for 14-day k/d
    ax4 = ax.twinx()
    Y_START=Y_START-Y_RANGE-Y_GAP
    ax4.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
    fourteen_k=[]
    fourteen_d=[]
    for i, item in enumerate(short_kd_data):
        fourteen_k.append(item[1])
        fourteen_d.append(item[2])
        
    # change into nd array
    fourteen_k_arr = np.asarray(fourteen_k)
    fourteen_d_arr = np.asarray(fourteen_d)
    # blue line for 14-day k,  red line for 14-day d
    line_14k=ax4.plot(x_pos, fourteen_k_arr, 'b-', label='%K(14,3)')
    line_14d=ax4.plot(x_pos, fourteen_d_arr, 'r-', label='%D(3)')
    # black horizontal line for 80 and 20 mark
    line_80_mark=ax4.plot([x_pos[0],x_pos[-1]], [80,80], 'y-',linewidth=2)
    line_20_mark=ax4.plot([x_pos[0],x_pos[-1]], [20,20], 'y-',linewidth=2)
    #
    ax4.locator_params(tight=True, axis='y',nbins=5)
    ax4.grid(color='c', linestyle='--', linewidth=1)
    ax4.set_ylabel('STO')
    if _SHOW_LEGEND:
        ax4.legend(handles=[line_14k[0],line_14d[0]], ncol=2, loc='upper left', prop={'size':10})
    # add a 5th axes for ADX
    ax5 = ax.twinx()
    Y_START=Y_START-Y_RANGE-Y_GAP
    ax5.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
    pdi14=[]
    ndi14=[]
    adx=[]
    for i, item in enumerate(adx_data):
        pdi14.append(item[1])
        ndi14.append(item[2])
        adx.append(item[3])
        
    # change into nd array
    pdi14_arr = np.asarray(pdi14)
    ndi14_arr = np.asarray(ndi14)
    adx_arr = np.asarray(adx)
    # blue line for 14-day k,  red line for 14-day d
    line_pdi14=ax5.plot(x_pos, pdi14_arr, 'g-', label='+DI')
    line_ndi14=ax5.plot(x_pos, ndi14_arr, 'r-', label='-DI')
    line_adx=ax5.plot(x_pos, adx_arr, 'k-', label='ADX(14)')
    # black horizontal line for 20 mark
    line_20_mark=ax5.plot([x_pos[0],x_pos[-1]], [20,20], 'y-',linewidth=2)
    #
    ax5.locator_params(tight=True, axis='y',nbins=5)
    ax5.grid(color='c', linestyle='--', linewidth=1)
    ax5.set_ylabel('ADX')
    if _SHOW_LEGEND:
        ax5.legend(handles=[line_pdi14[0],line_ndi14[0], line_adx[0]], ncol=3, loc='upper left', prop={'size':10})
    
    fig.set_size_inches(18.5, 10.5)
    # water mark position bottom right
    fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
             fontsize=50, color='gray',
             ha='right', va='bottom', alpha=0.5)
    
    fig.savefig('%s.png' % fname)
    plt.close(fig)