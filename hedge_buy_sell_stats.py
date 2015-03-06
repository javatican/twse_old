# coding: utf-8
import json
import os
from core.models import Twse_Trading_Warrant, Twse_Trading_Processed
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, string_to_date
import matplotlib 
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
i=0
for trading_date_str in trading_date_list:
    trading_date=string_to_date(trading_date_str, date_format='%Y-%m-%d')
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
    i+=1
# interactive mode for pyplot
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#plt.ion()
# number of data point
N=len(trading_date_list)
x_pos=np.arange(N)
width=0.35
fig, ax = plt.subplots()
#
rect_mon = ax.bar(x_pos[mon], hedge_diff[mon], width, color='r')
rect_tue = ax.bar(x_pos[tue], hedge_diff[tue], width, color='y')
rect_wed = ax.bar(x_pos[wed], hedge_diff[wed], width, color='b')
rect_thr = ax.bar(x_pos[thr], hedge_diff[thr], width, color='g')
rect_fri = ax.bar(x_pos[fri], hedge_diff[fri], width, color='m')
rect_sat = ax.bar(x_pos[sat], hedge_diff[sat], width, color='c')
ax.set_ylabel('TWD')
ax.set_title('Warrant Hedge Buy and Sell Diff Values')
ax.set_xticks(x_pos[::5])
ax.set_xticks(x_pos, minor=True)
ax.set_xticklabels(trading_date_list[::5], rotation=45)
ax.grid(color='c', linestyle='--', linewidth=1)
ax.legend((rect_mon[0], rect_tue[0], rect_wed[0], rect_thr[0],rect_fri[0],rect_sat[0]), ('Mon', 'Tue', 'Wed', 'Thr', 'Fri','Sat'))
#plt.show()
fig.savefig("hedge_buy_sell_stats.png")

