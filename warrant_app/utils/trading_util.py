import numpy as np
 
def moving_avg(input_array, DAY_AVERAGE):
    item_count=input_array.size
    if item_count < DAY_AVERAGE: 
        raise Exception
    avg_array = np.zeros(item_count - DAY_AVERAGE + 1)
    for j in np.arange(DAY_AVERAGE):
        sli = slice(j, item_count - DAY_AVERAGE + j + 1)
        avg_array = avg_array + input_array[sli]
    avg_array = avg_array / DAY_AVERAGE
    return avg_array

def calc_stochastic_oscillator(highest_array, lowest_array, closing_array, LOOK_BACK_PERIOD=14, K_SMOOTHING=3, D_MOVING_AVERAGE=3 ):
    item_count=closing_array.size
    min_item_count=LOOK_BACK_PERIOD+K_SMOOTHING-1+D_MOVING_AVERAGE-1
    if item_count<min_item_count: 
        raise Exception
    k_array=np.zeros(item_count-LOOK_BACK_PERIOD+1)
    for j, item in enumerate(closing_array[LOOK_BACK_PERIOD-1:]):
        highest_price=np.max(highest_array[j:LOOK_BACK_PERIOD+j])
        lowest_price=np.min(lowest_array[j:LOOK_BACK_PERIOD+j])
        if highest_price-lowest_price>0:
            k_value=100*(item-lowest_price)/(highest_price-lowest_price)
            k_array[j]=k_value
        else:
            print "highest_price=lowest_price @ %s" % lowest_price
            continue
        # calculate moving averages of 'K_SMOOTHING' values of K
        smoothed_k_array= moving_avg(k_array, K_SMOOTHING)
        # calculate moving averages of smoothed K (ie. D)
        d_array= moving_avg(smoothed_k_array, D_MOVING_AVERAGE)
    return np.around(smoothed_k_array[D_MOVING_AVERAGE-1:],2),np.around(d_array,2)

def wilder_smoothing(prev, curr, SMOOTHING_FACTOR=14, use_sum=True):
    if use_sum:
        return prev-(prev/SMOOTHING_FACTOR)+curr
    else:
        return (prev*(SMOOTHING_FACTOR-1)+curr)/SMOOTHING_FACTOR
    
    
def calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=14):
    item_count=closing_array.size
    min_item_count=SMOOTHING_FACTOR+SMOOTHING_FACTOR
    if item_count<min_item_count: 
        raise Exception
    tr_array=np.zeros(item_count-1)
    pdm_array=np.zeros(item_count-1)
    ndm_array=np.zeros(item_count-1)
    tr14_array=np.zeros(item_count-SMOOTHING_FACTOR)
    pdm14_array=np.zeros(item_count-SMOOTHING_FACTOR)
    ndm14_array=np.zeros(item_count-SMOOTHING_FACTOR)
    adx_array=np.zeros(item_count-SMOOTHING_FACTOR-SMOOTHING_FACTOR+1)
    #
    for i in np.arange(1, item_count):
        tr=max(highest_array[i]-lowest_array[i], abs(highest_array[i]-closing_array[i-1]), abs(lowest_array[i]-closing_array[i-1]))
        pdm=0
        if highest_array[i]-highest_array[i-1] > lowest_array[i-1]-lowest_array[i]:
            pdm=max(highest_array[i]-highest_array[i-1],0)
        ndm=0
        if lowest_array[i-1]-lowest_array[i] > highest_array[i]-highest_array[i-1] :
            ndm=max(lowest_array[i-1]-lowest_array[i],0)
        tr_array[i-1]=tr
        pdm_array[i-1]=pdm
        ndm_array[i-1]=ndm
    for i in np.arange(tr14_array.size):
        if i==0:
            tr14=np.sum(tr_array[:SMOOTHING_FACTOR])
            pdm14=np.sum(pdm_array[:SMOOTHING_FACTOR])
            ndm14=np.sum(ndm_array[:SMOOTHING_FACTOR])
        else:
            tr14=wilder_smoothing(tr14_array[i-1], tr_array[SMOOTHING_FACTOR+i-1])
            pdm14=wilder_smoothing(pdm14_array[i-1], pdm_array[SMOOTHING_FACTOR+i-1])
            ndm14=wilder_smoothing(ndm14_array[i-1], ndm_array[SMOOTHING_FACTOR+i-1])
        tr14_array[i]=tr14
        pdm14_array[i]=pdm14
        ndm14_array[i]=ndm14
        #
    pdi14_array=100*pdm14_array/tr14_array
    ndi14_array=100*ndm14_array/tr14_array
    dx_array=100*np.abs(pdi14_array - ndi14_array)/(pdi14_array + ndi14_array)
#     for item in dx_array:
#         print "dx=%s" % item
    for i in np.arange(adx_array.size):
        if i==0:
            adx=np.average(dx_array[:SMOOTHING_FACTOR]) 
        else:
            adx=wilder_smoothing(adx_array[i-1], dx_array[SMOOTHING_FACTOR+i-1], use_sum=False)
        adx_array[i]=adx
    
    return pdi14_array[SMOOTHING_FACTOR-1:],ndi14_array[SMOOTHING_FACTOR-1:], adx_array
    
        