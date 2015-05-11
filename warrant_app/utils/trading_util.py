from __future__ import unicode_literals

import datetime
import json
import math
import matplotlib
from matplotlib.finance import candlestick_ohlc
from matplotlib.font_manager import FontProperties
import os
import requests
from requests.sessions import Session

from core.models import Trading_Date, Stock_Item
import numpy as np
from warrant_app.utils.dateutil import convertToDate, DateEncoder, \
    string_to_time 
    
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

def calc_stochastic_oscillator(input_list=None, LOOK_BACK_PERIOD=14, K_SMOOTHING=3, D_MOVING_AVERAGE=3):
    # this general function is used to recalculate stochastic_oscillator values for a specific trading data (eg. stock, index)
    # For instance, Twse_Trading entries are used for 'stock', Index_Change_Info entries are used for 'index'
    # Default parameters are for 14-day stochastic oscillator
    items_to_update = []
    if not input_list:
        # input_list can  not be empty
        raise Exception
    else:        
        items = input_list
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
        # get the strategy object
        tts = item.get_trading_strategy()
        if LOOK_BACK_PERIOD == 14:
            tts.fourteen_day_k = k_array[j]
            tts.fourteen_day_d = d_array[j]
        else:
            tts.seventy_day_k = k_array[j]
            tts.seventy_day_d = d_array[j]
        items_to_update.append(tts)
    return items_to_update

class NotEnoughTradingDataException(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
def _calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD=14, K_SMOOTHING=3, D_MOVING_AVERAGE=3):
    item_count = closing_array.size
    # print "item_count=%s" % item_count
    min_item_count = LOOK_BACK_PERIOD + K_SMOOTHING - 1 + D_MOVING_AVERAGE - 1
    if item_count < min_item_count: 
        raise NotEnoughTradingDataException
    k_array = np.zeros(item_count - LOOK_BACK_PERIOD + 1)
    for j, item in enumerate(closing_array[LOOK_BACK_PERIOD - 1:]):
        highest_price = np.max(highest_array[j:LOOK_BACK_PERIOD + j])
        # print "highest_price=%s" % highest_price
        lowest_price = np.min(lowest_array[j:LOOK_BACK_PERIOD + j])
        # print "lowest_price=%s" % lowest_price
        if highest_price - lowest_price > 0:
            k_value = 100 * (item - lowest_price) / (highest_price - lowest_price)
            # print "closing_price=%s" % item
            # print "k_value=%s" % k_value
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

def recalc_all_di_adx(input_list=None, SMOOTHING_FACTOR=14):
    # this general function is used to recalculate 'all' ADX related values for a specific trading data (eg. stock, index)
    # For instance, Twse_Trading entries are used for 'stock', Index_Change_Info entries are used for 'index'
    strategy_items_to_update = []
    if not input_list :
        raise Exception
    else:
        items = input_list
        
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
    tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array = _calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
    # ryan note:
    # 1. the size of tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array are the same
    # 2. the size of adx_array is '2*SMOOTHING_FACTOR-1' shorter than that of items
    for j, item in enumerate(items[SMOOTHING_FACTOR + SMOOTHING_FACTOR - 1:]):
        tts = item.get_trading_strategy()
        tts.tr14 = tr14_array[j]
        tts.pdm14 = pdm14_array[j]
        tts.ndm14 = ndm14_array[j]
        if not math.isnan(pdi14_array[j]): tts.pdi14 = pdi14_array[j]
        if not math.isnan(ndi14_array[j]): tts.ndi14 = ndi14_array[j]
        if not math.isnan(adx_array[j]): tts.adx = adx_array[j]                        
        strategy_items_to_update.append(tts)
    return strategy_items_to_update

def update_di_adx(input_list=None, SMOOTHING_FACTOR=14):
    # this general function is used to update missing ADX related values for a specific trading data (eg. stock, index)
    # For instance, Twse_Trading entries are used for 'stock', Index_Change_Info entries are used for 'index'
    
    # input_list[0]'s 'strategy instance' (maybe the object itself) is assumed to contain tr14, pdm14, ndm14, adx values, and will be used to calculate the following missing values.
    # input_list can not be null. 
    strategy_items_to_update = []
    if not input_list:
        raise Exception
    else:
        items = input_list
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
    previous_strategy = items[0].get_trading_strategy()
    tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array = _calc_di_adx_pairwise(highest_array, lowest_array, closing_array, previous_strategy, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
#
    for j, item in enumerate(items[1:]):
        tts = item.get_trading_strategy()
        tts.tr14 = tr14_array[j]
        tts.pdm14 = pdm14_array[j]
        tts.ndm14 = ndm14_array[j]
        if not math.isnan(pdi14_array[j]): tts.pdi14 = pdi14_array[j]
        if not math.isnan(ndi14_array[j]): tts.ndi14 = ndi14_array[j]
        if not math.isnan(adx_array[j]): tts.adx = adx_array[j]                        
        strategy_items_to_update.append(tts)
    return strategy_items_to_update      
                      
def _calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=14):
    # Average True Range: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr
    # Average Directional Index: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
    item_count = closing_array.size
    min_item_count = SMOOTHING_FACTOR + SMOOTHING_FACTOR
    if item_count < min_item_count: 
        raise NotEnoughTradingDataException                      
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
    
def _calc_di_adx_pairwise(highest_array, lowest_array, closing_array, previous_strategy, SMOOTHING_FACTOR=14):
    # This function is used to calculate DI and ADX for a range of trading date assuming there were existing values for DI and ADX before the trading date range.
    # That is if we are calculating data from date1 to date2,  DI, ADX for 'date1-1day' is existed  and will be used for calculating DI, ADX for date1. 
    # highest_array, lowest_array, closing_array do include values from previous_trading
    
    # Average True Range: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr
    # Average Directional Index: refer to http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
    item_count = closing_array.size
    min_item_count = 2
    if item_count < min_item_count: 
        raise NotEnoughTradingDataException
    tr_array = np.zeros(item_count - 1)
    pdm_array = np.zeros(item_count - 1)
    ndm_array = np.zeros(item_count - 1)
    tr14_array = np.zeros(item_count - 1)
    pdm14_array = np.zeros(item_count - 1)
    ndm14_array = np.zeros(item_count - 1)  
    adx_array = np.zeros(item_count - 1)
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
    # Subsequent Values = Prior TR14 - (Prior TR14/14) + Current TR1
    for i in np.arange(item_count - 1):
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
    for i in np.arange(item_count - 1):
        if i == 0:
            adx = wilder_smoothing(float(previous_strategy.adx), dx_array[i], use_sum=False)
        else:
            adx = wilder_smoothing(adx_array[i - 1], dx_array[i], use_sum=False)
        adx_array[i] = adx
    
    return tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array
    

def stoch_pop_pre_filtering_bull(data_array, LONG_K_LEVEL, ADX_LEVEL):
    # Bull candidate target: long term bull but in consolidating lately
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: adx are below ADX_LEVEL(eg 15)
    long_k = data_array[0]
    adx = data_array[6]
    for data in long_k:
        if data < LONG_K_LEVEL: return False 
    for data in adx:
        if data > ADX_LEVEL: return False 
    return True

def stoch_drop_pre_filtering_bear(data_array, LONG_K_LEVEL, ADX_LEVEL):
    # Bear candidate target: long term bear but in consolidating lately
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: adx are below ADX_LEVEL(eg 15)
    long_k = data_array[0]
    adx = data_array[6]
    for data in long_k:
        if data > LONG_K_LEVEL: return False 
    for data in adx:
        if data > ADX_LEVEL: return False 
    return True

def stoch_pop_breakout3_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout 3rd day target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last 3 days' k are above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k = data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    if short_k[-2] < SHORT_K_LEVEL: return False
    if short_k[-3] < SHORT_K_LEVEL: return False
    if short_k.size > 3:
        for data in short_k[:-3]:
            if data >= SHORT_K_LEVEL: return False
    return True

def stoch_drop_breakout3_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout 3rd day target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last 3 days' k are below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k = data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    if short_k[-2] > SHORT_K_LEVEL: return False
    if short_k[-3] > SHORT_K_LEVEL: return False
    if short_k.size > 3:
        for data in short_k[:-3]:
            if data <= SHORT_K_LEVEL: return False 
    return True

def stoch_pop_breakout2_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout 2nd day target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last two days' k are above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k = data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    if short_k[-2] < SHORT_K_LEVEL: return False
    for data in short_k[:-2]:
        if data >= SHORT_K_LEVEL: return False
    return True

def stoch_drop_breakout2_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout 2nd day target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last two days' k are below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k = data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    if short_k[-2] > SHORT_K_LEVEL: return False
    for data in short_k[:-2]:
        if data <= SHORT_K_LEVEL: return False 
    return True

def stoch_pop_breakout_list_bull(data_array, SHORT_K_LEVEL):
    # Bull breakout target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last k is above SHORT_K_LEVEL(eg 80) and the others are below SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    short_k = data_array[2]
    if short_k[-1] < SHORT_K_LEVEL: return False
    for data in short_k[:-1]:
        if data >= SHORT_K_LEVEL: return False
    return True

def stoch_drop_breakout_list_bear(data_array, SHORT_K_LEVEL):
    # Bear breakout target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's , the last k is below SHORT_K_LEVEL(eg 20) and the others are above SHORT_K_LEVEL
    # 3rd criteria: adx are below ADX_LEVEL(eg 15) 
    short_k = data_array[2]  
    if short_k[-1] > SHORT_K_LEVEL: return False
    for data in short_k[:-1]:
        if data <= SHORT_K_LEVEL: return False 
    return True

def stoch_pop_watch_list_bull(data_array, SHORT_K_LEVEL):
    # Bull watch target
    # 1st criteria: long(70-day) k's are above LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's, all are below  SHORT_K_LEVEL(eg 80) but the last k is between SHORT_K_LEVEL(eg 80) and SHORT_K_LEVEL-SHORT_K_WINDOW(eg 65)
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    SHORT_K_WINDOW = 15
    short_k = data_array[2]
    for data in short_k:
        if data > SHORT_K_LEVEL: return False 
    if short_k[-1] < SHORT_K_LEVEL - SHORT_K_WINDOW: return False
    return True

def stoch_drop_watch_list_bear(data_array, SHORT_K_LEVEL):
    # Bear watch target
    # 1st criteria: long(70-day) k's are below LONG_K_LEVEL(eg 50)
    # 2nd criteria: for short(14-day) k's, all are above  SHORT_K_LEVEL(eg 20) but the last k is between SHORT_K_LEVEL(eg 20) and SHORT_K_LEVEL+SHORT_K_WINDOW(eg 35)
    # 3rd criteria: adx are below ADX_LEVEL(eg 15)
    SHORT_K_WINDOW = 15
    short_k = data_array[2]
    for data in short_k:
        if data < SHORT_K_LEVEL: return False 
    if short_k[-1] > SHORT_K_LEVEL + SHORT_K_WINDOW: return False
    return True

def predict_breakout_price(stock, SHORT_K_LEVEL):
    LOOK_BACK_PERIOD = 14
    trading_entries = stock.twse_trading_list.all().order_by('-trading_date')[:LOOK_BACK_PERIOD + 1]
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    for item in trading_entries:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array(highest_price_list)
    lowest_array = np.array(lowest_price_list)
    closing_array = np.array(closing_price_list)
    # calculate k1
    highest_price = np.max(highest_array[1:])
    lowest_price = np.min(lowest_array[1:])
    k1 = 100 * (closing_array[1] - lowest_price) / (highest_price - lowest_price)
    # calculate k2
    highest_price = np.max(highest_array[:-1])
    lowest_price = np.min(lowest_array[:-1])
    k2 = 100 * (closing_array[0] - lowest_price) / (highest_price - lowest_price)
    # calculate breakout price
    # only consider the highest/lowest price within '13-day' window 
    highest_price = np.max(highest_array[:-2])
    lowest_price = np.min(lowest_array[:-2])
    k3 = 3 * SHORT_K_LEVEL - k1 - k2
    breakout_price = round(k3 * (highest_price - lowest_price) / 100 + lowest_price, 2)
    return breakout_price

def stoch_cross_level_list_bull(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # Bull cross level target    
    # criteria: for short(14-day) k's, k1 is below SHORT_K_LEVEL(eg 20) and k2 is above  SHORT_K_LEVEL
    short_k = data_array[2]
    for data in short_k[:-1]:
        if data >= SHORT_K_LEVEL: return False 
    if short_k[-1] < SHORT_K_LEVEL: return False
    return True

def stoch_cross_level_watch_list_bull(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # Bull cross level watch target    
    # criteria: for short(14-day) k's, k1,k2 are below SHORT_K_LEVEL(eg 20) and k2 is above k1
    short_k = data_array[2]
    for data in short_k:
        if data >= SHORT_K_LEVEL: return False 
    if short_k[-1] < short_k[-2]: return False
    return True

def stoch_golden_cross_list_bull(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # Bull golden cross target    
    # criteria: for short(14-day) k's and  d's, k1,k2 are below 80 and k1<d1, k2>d2
    short_k = data_array[2]
    short_d = data_array[3]
    for data in short_k:
        if data >= 80: return False 
    if short_k[-2] > short_d[-2]: return False
    if short_k[-1] < short_d[-1]: return False
    return True

def stoch_golden_cross_watch_list_bull(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # Bull golden cross watch target    
    # criteria: for short(14-day) k's and d's, k1<d1<80, k2<d2<80 and d1-k1>d2-k2 and d2-k2<10
    short_k = data_array[2]
    short_d = data_array[3]
    for data in short_k:
        if data >= 80: return False 
    for data in short_d:
        if data >= 80: return False 
    if short_k[-2] >= short_d[-2]: return False
    if short_k[-1] >= short_d[-1]: return False
    if short_d[-2] - short_k[-2] <= short_d[-1] - short_k[-1]: return False
    if short_d[-1] - short_k[-1] >= 10: return False
    return True

def stoch_cross_level_list_bear(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # bear cross level target    
    # criteria: for short(14-day) k's, k1 is above SHORT_K_LEVEL(eg 80) and k2 is below SHORT_K_LEVEL
    short_k = data_array[2]
    for data in short_k[:-1]:
        if data <= SHORT_K_LEVEL: return False 
    if short_k[-1] >= SHORT_K_LEVEL: return False
    return True

def stoch_cross_level_watch_list_bear(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # bear cross level watch target    
    # criteria: for short(14-day) k's, k1,k2 are above SHORT_K_LEVEL(eg 80) and k2 is below k1
    short_k = data_array[2]
    for data in short_k:
        if data < SHORT_K_LEVEL: return False 
    if short_k[-1] >= short_k[-2]: return False
    return True

def stoch_death_cross_list_bear(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # bear death cross target    
    # criteria: for short(14-day) k's and  d's, k1,k2 are above 20 and k1>d1, k2<d2
    short_k = data_array[2]
    short_d = data_array[3]
    for data in short_k:
        if data <= 20: return False 
    if short_k[-2] <= short_d[-2]: return False
    if short_k[-1] >= short_d[-1]: return False
    return True

def stoch_death_cross_watch_list_bear(data_array, LONG_K_LEVEL, SHORT_K_LEVEL):
    # bear death cross watch target    
    # criteria: for short(14-day) k's and d's, k1>d1>20, k2>d2>20 and k1-d1>k2-d2 and k2-d2<10
    short_k = data_array[2]
    short_d = data_array[3]
    for data in short_k:
        if data <= 20: return False 
    for data in short_d:
        if data <= 20: return False 
    if short_k[-2] <= short_d[-2]: return False
    if short_k[-1] <= short_d[-1]: return False
    if short_k[-2] - short_d[-2] <= short_k[-1] - short_d[-1]: return False
    if short_k[-1] - short_d[-1] >= 10: return False
    return True

def _is_incrementing(data_array):
    # assuming input array is 1D
    array_1 = data_array[1:]
    array_2 = data_array[:-1]
    diff = array_1 - array_2
    count = np.sum((diff >= 0).astype(int))
    if count != array_1.size: 
        return False
    else:
        return True
    
def _is_decrementing(data_array):
    # assuming input array is 1D
    array_1 = data_array[1:]
    array_2 = data_array[:-1]
    diff = array_1 - array_2
    count = np.sum((diff <= 0).astype(int))
    if count != array_1.size: 
        return False
    else:
        return True
    
def volume_over_average_ratio(stock_quote, trading):
    year_volume_avg = float(trading.year_volume_avg)
    #trade_volume from stock_quote is in 1000-share unit
    trade_volume = stock_quote.trade_volume*1000
    trading_time = stock_quote.trading_time
    time_since_start = string_to_time(trading_time) - string_to_time('09:00:00')
    time_since_in_secs = time_since_start.total_seconds()
    # time_overall=string_to_time("13:30:00")-string_to_time('09:00:00')
    # time_overall_in_secs=time_overall.total_seconds()
    time_overall_in_secs = 16200.0
    ratio = round(trade_volume / (year_volume_avg * time_since_in_secs / time_overall_in_secs),2)
    return ratio


class Selection_Strategy:
    def __init__(self, stock_item, selection_stock_item, stock_quote, trading, strategy_param):
        self.stock_item=stock_item
        self.selection_stock_item = selection_stock_item
        self.stock_quote = stock_quote
        self.trading = trading
        self.strategy_param = strategy_param
    def is_triggered(self):
        raise NotImplementedError("Please Implement this method")
    def notify_message(self):
        raise NotImplementedError("Please Implement this method")
    def check_message(self):
        if self.is_triggered():
            return self.notify_message()
        else:
            return None
        
class Strategy_Stoch_Pop_Watch(Selection_Strategy):        
    def is_triggered(self):
        # conditions to notify
        # 1. ks_14>80
        # 2. volume > year_volume_avg
        self.k_d=tell_me_current_kd_2(self.stock_quote)
        triggered = False
        #print self.k_d.ks_14
        if self.k_d.ks_14 >= 80:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            #print self.ratio
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)
    
class Strategy_Stoch_Drop_Watch(Selection_Strategy):
    def is_triggered(self):
        self.k_d = tell_me_current_kd_2(self.stock_quote)
        # conditions to notify
        # 1. ks_14<20
        # 2. volume > year_volume_avg
        triggered = False
        #print self.k_d.ks_14
        if self.k_d.ks_14 <= 20:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            #print self.ratio
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)

class Strategy_Stoch_Pop_Breakout(Selection_Strategy):
    def is_triggered(self):
        self.k_d = tell_me_current_kd_2(self.stock_quote)
        # conditions to notify
        # 1. ks_14<80
        # 2. volume > year_volume_avg
        triggered = False
        if self.k_d.ks_14 < 80:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)

class Strategy_Stoch_Drop_Breakout(Selection_Strategy):
    def is_triggered(self):
        self.k_d = tell_me_current_kd_2(self.stock_quote)
        # conditions to notify
        # 1. ks_14>20
        # 2. volume > year_volume_avg
        triggered = False
        if self.k_d.ks_14 > 20:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)

class Strategy_Stoch_Golden_Cross_Watch(Selection_Strategy):
    #stoch_golden_cross_watch
    def is_triggered(self):
        self.k_d = tell_me_current_kd_2(self.stock_quote)
        # conditions to notify
        # 1. ks_14 > da_14
        # 2. volume > year_volume_avg
        triggered = False
        if self.k_d.ks_14 > self.k_d.da_14:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)

class Strategy_Stoch_Death_Cross_Watch(Selection_Strategy):
    #stoch_golden_cross_watch
    def is_triggered(self):
        self.k_d = tell_me_current_kd_2(self.stock_quote)
        # conditions to notify
        # 1. ks_14 < da_14
        # 2. volume > year_volume_avg
        triggered = False
        if self.k_d.ks_14 < self.k_d.da_14:
            self.ratio = volume_over_average_ratio(self.stock_quote, self.trading)
            if self.ratio > 1.0:
                triggered = True
        return triggered
    
    def notify_message(self):
        msg_list = []
        msg_list.append("*** stock symbol (%s, %s)***" % (self.stock_item.symbol, self.stock_item.short_name))
        msg_list.append(self.stock_quote.notify_msg())
        msg_list.append(self.selection_stock_item.notify_msg())
        msg_list.append(self.k_d.notify_msg())
        msg_list.append(self.strategy_param.notify_msg())
        msg_list.append(self.trading.notify_msg())
        msg_list.append("volume over year average ratio : %s" % self.ratio)
        return "\n".join(msg_list)
SELECTION_STRATEGY_DICT={ 'stoch_pop_watch' : Strategy_Stoch_Pop_Watch,
                         'stoch_drop_watch' : Strategy_Stoch_Drop_Watch,
                         'stoch_pop_breakout': Strategy_Stoch_Pop_Breakout,
                         'stoch_drop_breakout': Strategy_Stoch_Drop_Breakout,
                         'stoch_pop_breakout2': Strategy_Stoch_Pop_Breakout,
                         'stoch_drop_breakout2': Strategy_Stoch_Drop_Breakout,
                         'stoch_pop_breakout3': Strategy_Stoch_Pop_Breakout,
                         'stoch_drop_breakout3': Strategy_Stoch_Drop_Breakout,
                         'stoch_cross_bull_level_watch': Strategy_Stoch_Drop_Breakout,
                         'stoch_cross_bull_level': Strategy_Stoch_Drop_Watch,
                         'stoch_cross_bear_level_watch': Strategy_Stoch_Pop_Breakout,
                         'stoch_cross_bear_level': Strategy_Stoch_Pop_Watch,
                         'stoch_golden_cross_watch': Strategy_Stoch_Golden_Cross_Watch,
                         'stoch_golden_cross':Strategy_Stoch_Death_Cross_Watch,
                         'stoch_death_cross_watch':Strategy_Stoch_Death_Cross_Watch,
                         'stoch_death_cross':Strategy_Stoch_Golden_Cross_Watch,
                         }

class Strategy_Plot:
    def __init__(self, model_instance):
        self.model_instance = model_instance
        
    def prepare_input_data(self):
        raise NotImplementedError("Please Implement this method")
    
    def plot_data(self, **input_data):
        raise NotImplementedError("Please Implement this method")
    
    def do(self):
        input_data = self.prepare_input_data()
        return self.plot_data(**input_data)
        
class Strategy_Plot_By_Stoch_Pop(Strategy_Plot): 
    OUTPUT_ROOT_PATH = "ipython/stock_strategy/stoch_osci/data"
    
    # end_date format : eg. '20150401'
    def __init__(self, model_instance, category=None, end_date=None, day_range=120, interactive_mode=False, force_regen_input=False):
        Strategy_Plot.__init__(self, model_instance)
        self.category = category
        self.end_date = end_date
        self.day_range = day_range
        self.interactive_mode = interactive_mode
        self.force_regen_input = force_regen_input

    def plot_data(self, **input_data):
        plot_title = input_data['title']
        candlestick_label = input_data['candlestick_label']
        volume_label = input_data['volume_label']
        output_plot_filename = input_data['output_plot_filename']
        price_data = input_data['price_data']
        long_kd_data = input_data['long_kd_data']
        short_kd_data = input_data['short_kd_data']
        adx_data = input_data['adx_data']
        
        #***preparing plot
        if not self.interactive_mode:
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        else:
            import matplotlib.pyplot as plt
            plt.ion()
    
        # setting for the font            
        font = FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size=14)
        _SHOW_LEGEND = False
#
        fig, ax = plt.subplots()
        trading_date_list = [] 
        volume_list = []    
        year_volume_avg_list = [] 
        opening_price_list = []
        closing_price_list = []
        for i, item in enumerate(price_data):
            trading_date_list.append(item[0])
            opening_price_list.append(item[1])
            closing_price_list.append(item[4])
            volume_list.append(item[5] / 1000)
            year_volume_avg_list.append(item[6] / 1000 if item[6] else None)
            # store a list of continuous integers for the 'float' date.
            # This is needed for finance lib candlestick_ohlc() to show continuous bar and whiskers without gap.
            item[0] = i + 1
        # plot axes #1 for candlesticks
        candlestick_ohlc(ax, price_data, width=0.8, colorup='r', colordown='g')
        N = len(trading_date_list)
        x_pos = np.arange(1, N + 1)
        #
        ax.set_ylabel(candlestick_label)
        ax.set_title('%s chart' % plot_title, fontproperties=font)
        ax.set_xticks(x_pos[::10])
        ax.set_xticks(x_pos, minor=True)
        ax.set_xticklabels(trading_date_list[::10], rotation=45)
        ax.grid(color='c', linestyle='--', linewidth=1)
        # to show several axes objects in the same figure, here adjust the y limits of the first axes, so there is space at the bottom to show other axes.
        pad = 1.2
        yl = ax.get_ylim()
        y_tick_gap = math.ceil((yl[1] - yl[0]) / 5)
        ax.yaxis.set_ticks(np.arange(yl[0], yl[1], y_tick_gap))
        # ax.locator_params(tight=True, axis='y',nbins=4)
        ax.set_ylim(yl[0] - (yl[1] - yl[0]) * pad, yl[1])
        # add a 2nd axes for volumes
        # axes position parameters here:
        X_START = 0.125
        X_END = 0.9
        Y_START = 0.52
        Y_RANGE = 0.1
        Y_GAP = 0.0
        ax2 = ax.twinx()
        ax2.set_position(matplotlib.transforms.Bbox([[X_START, Y_START - Y_RANGE], [X_END, Y_START]]))
        # change into nd array
        opening_price_arr = np.asarray(opening_price_list)
        closing_price_arr = np.asarray(closing_price_list)
        volume_arr = np.asarray(volume_list)
        down = opening_price_arr - closing_price_arr > 0
        up = opening_price_arr - closing_price_arr < 0
        no_change = opening_price_arr - closing_price_arr == 0
        # need to specify dtype , so any None value in year_volume_avg_list will be transformed into a nan
        year_volume_avg_arr = np.array(year_volume_avg_list, dtype=np.float)
        has_avg_data = ~np.isnan(year_volume_avg_arr)
        ax2.bar(x_pos[up], volume_arr[up], color='red', width=0.8, align='center')
        ax2.bar(x_pos[down], volume_arr[down], color='green', width=0.8, align='center')
        ax2.bar(x_pos[no_change], volume_arr[no_change], color='yellow', width=0.8, align='center')
        ax2.plot(x_pos[has_avg_data], year_volume_avg_arr[has_avg_data], 'r-', label='year avg vol')
        ax2.locator_params(tight=True, axis='y', nbins=4)
        ax2.set_ylabel(volume_label)
        ax2.grid(color='0.8', linestyle='--', linewidth=1)
        # add a 3rd axes for 70-day k/d
        ax3 = ax.twinx()
        Y_START = Y_START - Y_RANGE - Y_GAP
        ax3.set_position(matplotlib.transforms.Bbox([[X_START, Y_START - Y_RANGE], [X_END, Y_START]]))
        seventy_k = []
        seventy_d = []
        for i, item in enumerate(long_kd_data):
            seventy_k.append(item[1])
            seventy_d.append(item[2])
            
        # change into nd array
        seventy_k_arr = np.asarray(seventy_k)
        seventy_d_arr = np.asarray(seventy_d)
        # blue line for 70-day k,  red line for 70-day d
        line_70k = ax3.plot(x_pos, seventy_k_arr, 'b-', label='%K(70,3)')
        line_70d = ax3.plot(x_pos, seventy_d_arr, 'r-', label='%D(3)')
        # black horizontal line for 50 mark
        line_50_mark = ax3.plot([x_pos[0], x_pos[-1]], [50, 50], 'y-', linewidth=2)
        #
        ax3.locator_params(tight=True, axis='y', nbins=5)
        ax3.grid(color='c', linestyle='--', linewidth=1)
        ax3.set_ylabel('STO(70)')
        if _SHOW_LEGEND:
            ax3.legend(handles=[line_70k[0], line_70d[0]], ncol=2, loc='upper left', prop={'size':10})
        
        # add a 4th axes for 14-day k/d
        ax4 = ax.twinx()
        Y_START = Y_START - Y_RANGE - Y_GAP
        ax4.set_position(matplotlib.transforms.Bbox([[X_START, Y_START - Y_RANGE], [X_END, Y_START]]))
        fourteen_k = []
        fourteen_d = []
        for i, item in enumerate(short_kd_data):
            fourteen_k.append(item[1])
            fourteen_d.append(item[2])
            
        # change into nd array
        fourteen_k_arr = np.asarray(fourteen_k)
        fourteen_d_arr = np.asarray(fourteen_d)
        # blue line for 14-day k,  red line for 14-day d
        line_14k = ax4.plot(x_pos, fourteen_k_arr, 'b-', label='%K(14,3)')
        line_14d = ax4.plot(x_pos, fourteen_d_arr, 'r-', label='%D(3)')
        # black horizontal line for 80 and 20 mark
        line_80_mark = ax4.plot([x_pos[0], x_pos[-1]], [80, 80], 'y-', linewidth=2)
        line_20_mark = ax4.plot([x_pos[0], x_pos[-1]], [20, 20], 'y-', linewidth=2)
        #
        ax4.locator_params(tight=True, axis='y', nbins=5)
        ax4.grid(color='c', linestyle='--', linewidth=1)
        ax4.set_ylabel('STO(14)')
        if _SHOW_LEGEND:
            ax4.legend(handles=[line_14k[0], line_14d[0]], ncol=2, loc='upper left', prop={'size':10})
        # add a 5th axes for ADX
        ax5 = ax.twinx()
        Y_START = Y_START - Y_RANGE - Y_GAP
        ax5.set_position(matplotlib.transforms.Bbox([[X_START, Y_START - Y_RANGE], [X_END, Y_START]]))
        pdi14 = []
        ndi14 = []
        adx = []
        for i, item in enumerate(adx_data):
            pdi14.append(item[1])
            ndi14.append(item[2])
            adx.append(item[3])
            
        # change into nd array
        pdi14_arr = np.asarray(pdi14)
        ndi14_arr = np.asarray(ndi14)
        adx_arr = np.asarray(adx)
        # blue line for 14-day k,  red line for 14-day d
        line_pdi14 = ax5.plot(x_pos, pdi14_arr, 'g-', label='+DI')
        line_ndi14 = ax5.plot(x_pos, ndi14_arr, 'r-', label='-DI')
        line_adx = ax5.plot(x_pos, adx_arr, 'k-', label='ADX(14)')
        # black horizontal line for 20 mark
        line_20_mark = ax5.plot([x_pos[0], x_pos[-1]], [20, 20], 'y-', linewidth=2)
        #
        ax5.locator_params(tight=True, axis='y', nbins=5)
        ax5.grid(color='c', linestyle='--', linewidth=1)
        ax5.set_ylabel('ADX')
        if _SHOW_LEGEND:
            ax5.legend(handles=[line_pdi14[0], line_ndi14[0], line_adx[0]], ncol=3, loc='upper left', prop={'size':10})
        
        fig.set_size_inches(18.5, 10.5)
        # water mark position bottom right
        fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
                 fontsize=50, color='gray',
                 ha='right', va='bottom', alpha=0.5)
        
        
        if self.interactive_mode:
            plt.show()
            return None
        else:
            fig.savefig('%s.png' % output_plot_filename, dpi=60)
            plt.close(fig)
            return '%s.png' % output_plot_filename
            
class Strategy_Plot_By_Stoch_Pop_For_Stock(Strategy_Plot_By_Stoch_Pop):
    def prepare_input_data(self):
        if not self.end_date:
            date_list = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[:self.day_range]            
        else:                    
            end_date = convertToDate(self.end_date)
            date_list = Trading_Date.objects.filter(trading_date__lte=end_date).values_list('trading_date', flat=True).order_by('-trading_date')[:self.day_range]
        start_date = date_list[len(date_list) - 1]
        end_date = date_list[0]
        directory = "%s/%s" % (Strategy_Plot_By_Stoch_Pop.OUTPUT_ROOT_PATH, end_date.strftime("%Y%m%d"))        
        if self.category:
            directory = "%s/%s" % (directory, self.category)
        if not os.path.exists(directory):
            os.makedirs(directory)
        fname = "%s/%s_stoch_osci_%s_%s" % (directory, self.model_instance.symbol, start_date, end_date)
        filename = '%s.txt' % fname
        if self.force_regen_input or not os.path.isfile(filename):
            entries = self.model_instance.twse_trading_list.filter(trading_date__gte=start_date,
                                                     trading_date__lte=end_date,
                                                     strategy__seventy_day_k__isnull=False).select_related('strategy').order_by('trading_date') 
            price_data = []
            long_kd_data = []
            short_kd_data = []    
            adx_data = []          
            for entry in entries:     
                # not every trading data has year_volume_avg               
                price_data.append((entry.trading_date,
                           float(entry.opening_price),
                           float(entry.highest_price),
                           float(entry.lowest_price),
                           float(entry.closing_price),
                           float(entry.trade_volume),
                           float(entry.year_volume_avg) if entry.year_volume_avg else None))
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
            json_data = {'stock_symbol': self.model_instance.symbol,
                         'stock_name': self.model_instance.short_name,
                         'price' : price_data,
                         '70kd' : long_kd_data,
                         '14kd' : short_kd_data,
                         'adx' : adx_data }
            with open(filename, 'w') as fp:
                json.dump(json_data, fp, cls=DateEncoder)
        #
        with open(filename, 'r') as fp:
            json_data = json.load(fp) 
        stock_symbol = json_data['stock_symbol'] 
        stock_name = json_data['stock_name'] 
        price_data = json_data['price'] 
        long_kd_data = json_data['70kd'] 
        short_kd_data = json_data['14kd'] 
        adx_data = json_data['adx'] 
        return {'title': "%s(%s)" % (stock_symbol, stock_name),
                'candlestick_label': 'Price',
                'volume_label': 'Volume',
                'output_plot_filename': fname,
                'price_data': price_data,
                'long_kd_data': long_kd_data,
                'short_kd_data': short_kd_data,
                'adx_data': adx_data,
                }
        
class Strategy_Plot_By_Stoch_Pop_For_Index(Strategy_Plot_By_Stoch_Pop):
    def prepare_input_data(self):
        if not self.end_date:
            date_list = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[:self.day_range]            
        else:                    
            end_date = convertToDate(self.end_date)
            date_list = Trading_Date.objects.filter(trading_date__lte=end_date).values_list('trading_date', flat=True).order_by('-trading_date')[:self.day_range]
        start_date = date_list[len(date_list) - 1]
        end_date = date_list[0]
        directory = "%s/%s" % (Strategy_Plot_By_Stoch_Pop.OUTPUT_ROOT_PATH, end_date.strftime("%Y%m%d"))        
        if self.category:
            directory = "%s/%s" % (directory, self.category)
        if not os.path.exists(directory):
            os.makedirs(directory)
        fname = "%s/%s_stoch_osci_%s_%s" % (directory, self.model_instance.wearn_symbol, start_date, end_date)
        filename = '%s.txt' % fname
        if not os.path.isfile(filename):
            entries = self.model_instance.index_change_list.filter(trading_date__gte=start_date,
                                                     trading_date__lte=end_date,
                                                     seventy_day_k__isnull=False).order_by('trading_date') 
            price_data = []
            long_kd_data = []
            short_kd_data = []    
            adx_data = []          
            for entry in entries:     
                # not every trading data has year_volume_avg               
                price_data.append((entry.trading_date,
                           float(entry.opening_price),
                           float(entry.highest_price),
                           float(entry.lowest_price),
                           float(entry.closing_price),
                           float(entry.trade_value),
                           float(entry.year_value_avg) if entry.year_value_avg else None))
                long_kd_data.append((entry.trading_date,
                           float(entry.seventy_day_k),
                           float(entry.seventy_day_d)))
                short_kd_data.append((entry.trading_date,
                           float(entry.fourteen_day_k),
                           float(entry.fourteen_day_d)))
                adx_data.append((entry.trading_date,
                           float(entry.pdi14),
                           float(entry.ndi14),
                           float(entry.adx)))
            # write to file
            json_data = {'index_wearn_symbol': self.model_instance.wearn_symbol,
                         'index_name': self.model_instance.name,
                         'price' : price_data,
                         '70kd' : long_kd_data,
                         '14kd' : short_kd_data,
                         'adx' : adx_data }
            with open(filename, 'w') as fp:
                json.dump(json_data, fp, cls=DateEncoder)
        #
        with open(filename, 'r') as fp:
            json_data = json.load(fp) 
        index_wearn_symbol = json_data['index_wearn_symbol'] 
        index_name = json_data['index_name'] 
        price_data = json_data['price'] 
        long_kd_data = json_data['70kd'] 
        short_kd_data = json_data['14kd'] 
        adx_data = json_data['adx'] 
        return {'title': "%s(%s)" % (index_wearn_symbol, index_name),
                'candlestick_label': 'Index',
                'volume_label': 'Trade Value',
                'output_plot_filename': fname,
                'price_data': price_data,
                'long_kd_data': long_kd_data,
                'short_kd_data': short_kd_data,
                'adx_data': adx_data, }

def tell_me_current_smoothed_14k(stock_symbol, current_price, max_price=None, min_price=None):
    LOOK_BACK_PERIOD = 14
    stock = Stock_Item.objects.get(symbol=stock_symbol)
    trading_entries = stock.twse_trading_list.all().order_by('-trading_date')[:LOOK_BACK_PERIOD + 1]
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    for item in trading_entries:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array(highest_price_list)
    lowest_array = np.array(lowest_price_list)
    closing_array = np.array(closing_price_list)
    # calculate k1
    highest_price = np.max(highest_array[1:])
    lowest_price = np.min(lowest_array[1:])
    k1 = 100 * (closing_array[1] - lowest_price) / (highest_price - lowest_price)
    # calculate k2
    highest_price = np.max(highest_array[:-1])
    lowest_price = np.min(lowest_array[:-1])
    k2 = 100 * (closing_array[0] - lowest_price) / (highest_price - lowest_price)
    # based on current_price and calculate k3
    # only consider the highest/lowest price within '13-day' window 
    highest_price = np.max(highest_array[:-2])
    lowest_price = np.min(lowest_array[:-2])
    if max_price and max_price > highest_price: 
        highest_price = max_price
    if min_price and min_price < lowest_price: 
        lowest_price = min_price
    k3 = 100 * (current_price - lowest_price) / (highest_price - lowest_price)
    if k3 > 100:
        k3 = 100
    elif k3 < 0: 
        k3 = 0
    smoothed_14k = round((k1 + k2 + k3) / 3 , 2)
    return smoothed_14k
    
def _tell_me_current_kd(stock_symbol, current_price, max_price=None, min_price=None):
    LOOK_BACK_PERIOD = 70
    stock = Stock_Item.objects.get(symbol=stock_symbol)
    trading_entries = stock.twse_trading_list.all().order_by('-trading_date')[:LOOK_BACK_PERIOD + 3]
    highest_price_list = []
    lowest_price_list = []
    closing_price_list = []
    highest_price_list.append(max_price)
    lowest_price_list.append(min_price)
    closing_price_list.append(current_price)
    for item in trading_entries:
        highest_price_list.append(float(item.highest_price))
        lowest_price_list.append(float(item.lowest_price))
        closing_price_list.append(float(item.closing_price))
    highest_array = np.array([price for price in reversed(highest_price_list)])
    lowest_array = np.array([price for price in reversed(lowest_price_list)])
    closing_array = np.array([price for price in reversed(closing_price_list)])
    
    ks_70_arr, da_70_arr = _calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, K_SMOOTHING=3, D_MOVING_AVERAGE=3)
    ks_70 = ks_70_arr[0]
    da_70 = da_70_arr[0]
    #
    LOOK_BACK_PERIOD = 14
    highest_array = np.array([price for price in reversed(highest_price_list[:LOOK_BACK_PERIOD + 4])])
    lowest_array = np.array([price for price in reversed(lowest_price_list[:LOOK_BACK_PERIOD + 4])])
    closing_array = np.array([price for price in reversed(closing_price_list[:LOOK_BACK_PERIOD + 4])])
    ks_14_arr, da_14_arr = _calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, K_SMOOTHING=3, D_MOVING_AVERAGE=3)
    ks_14 = ks_14_arr[0]
    da_14 = da_14_arr[0]
    return (ks_70, da_70, ks_14, da_14)

def tell_me_current_kd_2(stock_quote):
    stock_symbol = stock_quote.symbol
    current_price = stock_quote.closing_price
    max_price = stock_quote.highest_price
    min_price = stock_quote.lowest_price
    (ks_70, da_70, ks_14, da_14) = _tell_me_current_kd(stock_symbol, current_price, max_price, min_price)
    return K_D(symbol=stock_symbol, stock_quote=stock_quote, ks_70=ks_70, da_70=da_70, ks_14=ks_14, da_14=da_14)
    
def get_stock_realtime_quote(symbol):
    tdate = datetime.datetime.today().date().strftime('%Y%m%d')
    originUrl = 'http://mis.twse.com.tw/stock/fibest.jsp?stock=%s' % symbol
    ajaxUrl = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_%s.tw_%s&json=1&delay=0' % (symbol, tdate)
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
    
        httpResponse = session.get(url=ajaxUrl,
                                    headers={
                                             'Referer': originUrl, })
        # default response encoding is ISO8859-1
        httpResponse.encoding = "utf-8"
        # print httpResponse.json
        json_data = httpResponse.json()
        msgArray = json_data['msgArray']
        if len(msgArray) >= 0:
            opening_price = msgArray[0]['o']
            lowest_price = msgArray[0]['l']
            highest_price = msgArray[0]['h']
            closing_price = msgArray[0]['z']
            trade_volume = msgArray[0]['v']
            trading_time = msgArray[0]['t']
            # print "time: %s, opening_price=%s, highest_price=%s, lowest_price=%s, closing_price=%s, volume=%s" % (trading_time, opening_price, highest_price, lowest_price, closing_price, trade_volume)
            return (trading_time, opening_price, lowest_price, highest_price, closing_price, trade_volume)
        else:
            return None
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        result = e.read()
        raise Exception(result) 
    except:
        raise
class K_D:  
    # (symbol, stock_quote, ks_70, da_70, ks_14, da_14)
    # end_date format : eg. '20150401'
    def __init__(self, symbol=None, stock_quote=None, ks_70=None, da_70=None, ks_14=None, da_14=None):
        self.symbol = symbol
        self.stock_quote = stock_quote
        self.ks_70 = ks_70
        self.da_70 = da_70
        self.ks_14 = ks_14
        self.da_14 = da_14
        
    def __repr__(self):
        return 'Stock_Quote(symbol=%s, stock_quote=%s, ks_70=%s, da_70=%s, ks_14=%s, da_14=%s)' % (self.symbol,
                                                                                                   self.stock_quote,
                                                                                                    self.ks_70,
                                                                                                    self.da_70,
                                                                                                    self.ks_14,
                                                                                                    self.da_14)
    def notify_msg(self):
        return  'Realtime K/D: ks_70=%s, da_70=%s, ks_14=%s, da_14=%s)' % (self.ks_70,
                                                                            self.da_70,
                                                                            self.ks_14,
                                                                            self.da_14)             
class Stock_Quote:  
    
    # end_date format : eg. '20150401'
    def __init__(self, symbol=None, trading_date=None, trading_time=None, opening_price=None, lowest_price=None, highest_price=None, closing_price=None, trade_volume=None):
        self.symbol = symbol
        self.trading_date = trading_date
        self.trading_time = trading_time
        self.opening_price = opening_price
        self.lowest_price = lowest_price
        self.highest_price = highest_price
        self.closing_price = closing_price
        self.trade_volume = trade_volume
        
    def __repr__(self):
        return 'Stock_Quote(symbol=%s, trading_date=%s, trading_time=%s, opening_price=%s, lowest_price=%s, highest_price=%s, closing_price=%s, trade_volume=%s)' % (self.symbol,
                                                            self.trading_date,
                                                            self.trading_time,
                                                            self.opening_price,
                                                            self.lowest_price,
                                                            self.highest_price,
                                                            self.closing_price,
                                                            self.trade_volume)     
    def notify_msg(self):
        return  'Realtime quote: trading_time=%s, opening_price=%s, lowest_price=%s, highest_price=%s, closing_price=%s, trade_volume=%s(x1000)' % (self.trading_time,
                                                            self.opening_price,
                                                            self.lowest_price,
                                                            self.highest_price,
                                                            self.closing_price,
                                                            self.trade_volume)                                                  
    
def get_multi_stock_realtime_quote(symbol_list):
    tdate = datetime.datetime.today().date().strftime('%Y%m%d')
    if not symbol_list: return None
    #tdate = '20150508'
    originUrl = 'http://mis.twse.com.tw/stock/fibest.jsp?stock=%s' % 't00'
    sub_path_list = []
    for symbol in symbol_list:
        sub_path_list.append('tse_%s.tw_%s' % (symbol, tdate))
    sub_path_str = '|'.join(sub_path_list)
    ajaxUrl = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&json=1&delay=0' % sub_path_str
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
    
        httpResponse = session.get(url=ajaxUrl,
                                    headers={
                                             'Referer': originUrl, })
        # default response encoding is ISO8859-1
        httpResponse.encoding = "utf-8"
        # print httpResponse.json
        json_data = httpResponse.json()
        # print json_data
        if 'msgArray' in json_data:
            msgArray = json_data['msgArray']
            if len(msgArray) > 0:
                result_dict = {}
                for item in msgArray:
                    sq = Stock_Quote()
                    sq.symbol = item['c']
                    sq.opening_price = float(item['o'])
                    sq.lowest_price = float(item['l'])
                    sq.highest_price = float(item['h'])
                    sq.closing_price = float(item['z'])
                    sq.trade_volume = float(item['v'])
                    sq.trading_date = item['d']
                    sq.trading_time = item['t']
                    result_dict[sq.symbol] = sq
                return result_dict
            else:
                return None
        else:
            return None
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        result = e.read()
        raise Exception(result) 
    except:
        raise

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
