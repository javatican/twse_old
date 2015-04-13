import math

import numpy as np


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
    min_item_count = LOOK_BACK_PERIOD + K_SMOOTHING - 1 + D_MOVING_AVERAGE - 1
    if item_count < min_item_count: 
        raise Exception
    k_array = np.zeros(item_count - LOOK_BACK_PERIOD + 1)
    for j, item in enumerate(closing_array[LOOK_BACK_PERIOD - 1:]):
        highest_price = np.max(highest_array[j:LOOK_BACK_PERIOD + j])
        lowest_price = np.min(lowest_array[j:LOOK_BACK_PERIOD + j])
        if highest_price - lowest_price > 0:
            k_value = 100 * (item - lowest_price) / (highest_price - lowest_price)
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
    
