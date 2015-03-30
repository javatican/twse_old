# coding: utf-8
# This program is used to inspect warrant price 
# Answer questions like ' What is the percentage of making profits (within a 3-day window)
# for warrants?'
#
import json
import matplotlib 
import os

from core.models import Twse_Trading_Processed, Warrant_Item
import numpy as np
from warrant_app.utils.dateutil import DateEncoder
from warrant_app.utils.mpl_util import get_weekday_array, color_bar_by_weekday, \
    add_twse_index_axes


_FORCE_REGEN=False
_INTERACTIVE = True
#_INTERACTIVE=False
#number of day average in future
DAY_AVERAGE=3
#***preparing data
fname="ipython/warrant_price_stats/price_stats_20141201_20150310"
filename = '%s.txt' % fname
trading_date_list = None
if _FORCE_REGEN or not os.path.isfile(filename):
    # first get all the trading_date which has trading_warrant
    trading_date_list = Twse_Trading_Processed.objects.get_dates()
    trading_date_count = len(trading_date_list)
    # get all warrants
    warrant_list = Warrant_Item.objects.all()
    warrant_count=len(warrant_list)
    #initialize 2d array( trading data from one warrant is on the same row)
    diff_arr_by_warrant=np.zeros((warrant_count, trading_date_count-DAY_AVERAGE))
    for i, warrant in enumerate(warrant_list):
# Select trading_warrant entries which have trade_value.
# Also select trade_volume, so average price can be calculated.
        a_list = warrant.get_trading_warrant_list().filter(trade_value__isnull=False).order_by('trading_date').values_list('trading_date','trade_value','trade_volume')
#         a_list = warrant.get_trading_warrant_list().filter(trade_value__isnull=False, 
#                                                            moneyness__gt=-0.15,
#                                                            moneyness__lt=0.15,
#                                                            time_to_maturity__gt=0.1,
#                                                            trade_transaction__gt=3,
#                                                            ).order_by('trading_date').values_list('trading_date','trade_value','trade_volume')

        #create a dict to store (date,average_price) pair
        a_dict={}
        for item in a_list:
            #trade_value, trade_volume (from Django model ) is Decimal type, need to change it to float type
            #item: ('trading_date','trade_value','trade_volume') tuple
            a_dict[item[0]]=float(item[1])/float(item[2])
        #use dict.get(), with default option, set the empty price values to np.nan
        # so now price_list has 'complete' list of values(one for each trading date, the non-existing ones set to np.nan)
        price_list=[a_dict.get(trading_date, np.nan) for trading_date in trading_date_list]
        price_array = np.array(price_list) 
        # calc average of price values for the future 'DAY_AVERAGE' days
        future_avg_array=np.zeros(trading_date_count-DAY_AVERAGE)
#
        for j in np.arange(DAY_AVERAGE):
            sli=slice(j+1, trading_date_count-DAY_AVERAGE+j+1)
            future_avg_array=future_avg_array+price_array[sli]
        # any np.nan value will still be np.nan after addition, division operations.
        future_avg_array=future_avg_array/DAY_AVERAGE
        price_diff=price_array[:-1*DAY_AVERAGE] - future_avg_array
        diff_arr_by_warrant[i]=price_diff
    # write to file (only store 2 decimal digits for price data)
    # remember to call .tolist() for changing np arrays to list, in order to save in json format
    json_data = {'trading_date_list':list(trading_date_list)[:-1*DAY_AVERAGE],
               'price_diff_list' :np.around(diff_arr_by_warrant,decimals=2).tolist()}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
trading_date_list = json_data['trading_date_list']
trading_date_count = len(trading_date_list)
price_diff_list = json_data['price_diff_list'] 
#***preparing plot
trading_date_list = np.array(trading_date_list)
price_diff_array = np.array(price_diff_list) 
#
price_increase_sum=np.zeros(trading_date_count)
price_decrease_sum=np.zeros(trading_date_count)
price_unchange_sum=np.zeros(trading_date_count)
for item in price_diff_array:
    price_increase=item < 0
    price_decrease=item > 0
    price_unchange=item == 0
    price_increase=price_increase.astype(int)
    price_decrease=price_decrease.astype(int)
    price_unchange=price_unchange.astype(int)
    price_increase_sum=price_increase_sum+price_increase
    price_decrease_sum=price_decrease_sum+price_decrease
    price_unchange_sum=price_unchange_sum+price_unchange
price_increase_percentage = 100.0*price_increase_sum/(price_increase_sum+price_decrease_sum+price_unchange_sum)
# get weekday array
mon,tue,wed,thr,fri,sat = get_weekday_array(trading_date_list)
# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    import matplotlib.pyplot as plt
    plt.ion()

# number of data point
N = len(trading_date_list)
x_pos = np.arange(1, N + 1)
width = 0.8
fig, axarr = plt.subplots(2, sharex=True)
#
color_bar_by_weekday(axarr[0], x_pos-width/2, price_increase_percentage, mon, tue, wed,thr, fri,sat, width)
axarr[0].set_ylabel('Warrant price increase percentage')
axarr[0].set_title('Analysis of Warrant price vs 3-day future averages')
axarr[0].set_xticks(x_pos[::5])
axarr[0].set_xticks(x_pos, minor=True)
axarr[0].set_xticklabels(trading_date_list[::5], rotation=45)
axarr[0].grid(color='c', linestyle='--', linewidth=1)
#display twse_index
start_date, end_date = trading_date_list[0], trading_date_list[-1]
add_twse_index_axes(axarr[1],start_date, end_date)

fig.set_size_inches(18.5, 10.5)
# water mark position bottom right
fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
         fontsize=50, color='gray',
         ha='right', va='bottom', alpha=0.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
