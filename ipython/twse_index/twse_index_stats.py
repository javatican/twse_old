# coding: utf-8
# This program is used to plot twse index(boxs and whiskers) and volume(bars)
# I use matplotlib.finance packages to do the candlestick plot. But there are problems
# with gaps within trading_date data.
# Originally I use the matplotlib.dates modules to show ticks, but there are gaps 
# between trading_dates which can not be removed from plot. 
# So I have to do the ticks my own way. 
import json
import matplotlib  
from matplotlib.finance import candlestick_ohlc
import os

from core.models import Twse_Index_Stats
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, string_to_date 

_FORCE_REGEN=False
_INTERACTIVE = True
#_INTERACTIVE=False
#***preparing data
fname="ipython/twse_index/twse_index_20141201_20150310"
filename = '%s.txt' % fname
trading_date_list = None
if _FORCE_REGEN or not os.path.isfile(filename):
    start_date=string_to_date('2014/12/1')
    end_date=string_to_date('2015/3/10')
    entries = Twse_Index_Stats.objects.ohlc_between_dates(start_date, end_date)
    # write to file
    json_data = {'twse_index_stats': entries,}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
twse_index_stats = json_data['twse_index_stats'] 
#***preparing plot
# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    import matplotlib.pyplot as plt
    plt.ion()

fig, ax = plt.subplots(2, sharex=True)
trading_date_list=[] 
volume_list=[] 
opening_price_list=[]
closing_price_list=[]
for i, item in enumerate(twse_index_stats):
    trading_date_list.append(item[0])
    opening_price_list.append(item[1])
    closing_price_list.append(item[4])
    volume_list.append(item[5])
    # store a list of continuous integers for the 'float' date.
    item[0]=i+1
candlestick_ohlc(ax[0], twse_index_stats, width=0.8, colorup='r', colordown='g')
N = len(trading_date_list)
x_pos = np.arange(1,N+1)
#
ax[0].set_ylabel('TWSE Index')
ax[0].set_title('TWSE Index')
# ax[0].set_xticks(x_pos[::5])
# ax[0].set_xticks(x_pos, minor=True)
# ax[0].set_xticklabels(trading_date_list[::5], rotation=45)
ax[0].grid(color='c', linestyle='--', linewidth=1)
#
# add a 2nd axes for volumes
#change into nd array
opening_price_arr = np.asarray(opening_price_list)
closing_price_arr = np.asarray(closing_price_list)
volume_arr = np.asarray(volume_list)
down=opening_price_arr-closing_price_arr>0
up=opening_price_arr-closing_price_arr<0
no_change=opening_price_arr-closing_price_arr==0
ax[1].bar(x_pos[up],volume_arr[up],color='red',width=0.8,align='center')
ax[1].bar(x_pos[down],volume_arr[down],color='green',width=0.8,align='center')
ax[1].bar(x_pos[no_change],volume_arr[no_change],color='yellow',width=0.8,align='center')
ax[1].set_xticks(x_pos[::5])
ax[1].set_xticks(x_pos, minor=True)
ax[1].set_xticklabels(trading_date_list[::5], rotation=45)
ax[1].grid(color='c', linestyle='--', linewidth=1)
fig.set_size_inches(18.5, 10.5)
# water mark position bottom right
fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
         fontsize=50, color='gray',
         ha='right', va='bottom', alpha=0.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
