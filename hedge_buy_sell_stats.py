# coding: utf-8
# This program is used to calculation the hedge buy/sell value difference of warrants from Securities Dealer.
# It is used to inspect the 'buy vs sell' values of warrants for each week day.
# We can see significant buy before the weekend(Fri) and sell after the weekend(Mon). 
# The questions to ask are:
# 1.  Is Intrinsic Volatility of warrants also correlated with the hedge buy/sell values?
# 2.  Are the hedge buy/sell values of target stocks also correlated with the hedge buy/sell values of warrants?
from datetime import timedelta
import json
import matplotlib 
import os

from core.models import Twse_Trading_Warrant, Twse_Trading_Processed
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, string_to_date


_INTERACTIVE=True
#_INTERACTIVE=False
#***preparing data
filename='hedge_buy_sell_stats.txt'
trading_date_list =[]
hedge_buy_data=[]
hedge_sell_data=[]
if not os.path.isfile(filename):
    # first get all the trading_date which has trading_warrant
    trading_date_list = Twse_Trading_Processed.objects.get_dates()
    for trading_date in trading_date_list:
        trading_warrant_list = Twse_Trading_Warrant.objects.by_date(trading_date)
        hedge_buy_sum=0.0
        hedge_sell_sum=0.0
        for item in trading_warrant_list:
            #averge price
            avg_price = float(item.trade_value)/float(item.trade_volume)
            # hedge_buy value
            hedge_buy_sum+=float(item.hedge_buy)*avg_price
            hedge_sell_sum+=float(item.hedge_sell)*avg_price
        hedge_buy_data.append(hedge_buy_sum)
        hedge_sell_data.append(hedge_sell_sum)
    #write to file
    json_data={'trading_date_list':list(trading_date_list),
               'hedge_buy_data' :hedge_buy_data,
               'hedge_sell_data':hedge_sell_data}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
else:
    with open(filename, 'r') as fp:
        json_data=json.load(fp) 
    trading_date_list =json_data['trading_date_list']
    hedge_buy_data=json_data['hedge_buy_data']
    hedge_sell_data=json_data['hedge_sell_data']
#***preparing plot
trading_date_list=np.array(trading_date_list)
hedge_buy_data=np.array(hedge_buy_data)
hedge_sell_data=np.array(hedge_sell_data)
hedge_diff=hedge_buy_data-hedge_sell_data
mon=[]
tue=[]
wed=[]
thr=[]
fri=[]
sat=[]
#
between_gap=[] 
others=[]
i=0
previous_date=None
for trading_date_str in trading_date_list:
    if isinstance(trading_date_str,str):
        trading_date = string_to_date(trading_date_str, date_format='%Y-%m-%d')
    else:
        trading_date = trading_date_str
    day_of_week= trading_date.weekday()+1
    if day_of_week==1:
        mon.append(i)
    elif day_of_week==2:
        tue.append(i)
    elif day_of_week==3:
        wed.append(i)
    elif day_of_week==4:
        thr.append(i)
    elif day_of_week==5:
        fri.append(i)
    elif day_of_week==6:
        sat.append(i)
    if i>0:
        if trading_date>previous_date+timedelta(days=1):
            #gap greater than 1 day
            between_gap.append(i-1)
            between_gap.append(i)
        else:
            others.append(i-1)
            others.append(i)
    previous_date=trading_date
    i+=1
#

# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
if _INTERACTIVE:
    plt.ion()

# number of data point
N=len(trading_date_list)
x_pos=np.arange(N)
width=0.35
fig, axarr = plt.subplots(2, sharex=True)
#
rect_mon = axarr[0].bar(x_pos[mon], hedge_diff[mon], width, color='r')
rect_tue = axarr[0].bar(x_pos[tue], hedge_diff[tue], width, color='y')
rect_wed = axarr[0].bar(x_pos[wed], hedge_diff[wed], width, color='b')
rect_thr = axarr[0].bar(x_pos[thr], hedge_diff[thr], width, color='g')
rect_fri = axarr[0].bar(x_pos[fri], hedge_diff[fri], width, color='m')
rect_sat = axarr[0].bar(x_pos[sat], hedge_diff[sat], width, color='c')
axarr[0].set_ylabel('TWD')
axarr[0].set_title('Warrant Hedge Buy and Sell Diff Values')
axarr[0].set_xticks(x_pos[::5])
axarr[0].set_xticks(x_pos, minor=True)
axarr[0].set_xticklabels(trading_date_list[::5], rotation=45)
axarr[0].grid(color='c', linestyle='--', linewidth=1)
axarr[0].legend((rect_mon[0], rect_tue[0], rect_wed[0], rect_thr[0],rect_fri[0],rect_sat[0]), 
                ('Mon', 'Tue', 'Wed', 'Thr', 'Fri','Sat'), 
                ncol=6,
                loc='upper left')
rect_others = axarr[1].bar(x_pos[others], hedge_diff[others], width, color='0.8')
rect_btw_gap = axarr[1].bar(x_pos[between_gap], hedge_diff[between_gap], width, color='k')
axarr[1].legend((rect_btw_gap[0], rect_others[0]),  
                ('Between day gap', 'others'), 
                ncol=2,
                loc='upper left')
fig.set_size_inches(18.5,10.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig("hedge_buy_sell_stats.png")
