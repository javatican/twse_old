# coding: utf-8
# This program is used to inspect warrant trading in general , 
# eg.  volume distribution (violin plot)
# eg.  transaction distribution (violin plot)
import json
import matplotlib 
from matplotlib.cbook import violin_stats
import os

from core.models import Twse_Trading_Processed, \
    Twse_Trading_Warrant
import numpy as np
from warrant_app.utils.dateutil import DateEncoder
from warrant_app.utils.mpl_util import kde_method, color_violin_by_weekday, get_weekday_array


_FORCE_REGEN=False
_INTERACTIVE = True
#_INTERACTIVE=False
#  number of days
_number_of_days=10
#***preparing data
fname="ipython/warrant_trading/warrant_trading_20141201_20150310"
filename = '%s.txt' % fname
trading_date_list = None
if _FORCE_REGEN or not os.path.isfile(filename):
    # first get all the trading_date which has trading_warrant
    trading_date_list = Twse_Trading_Processed.objects.get_dates()[:_number_of_days]
    volume_list=[]
    transaction_list=[]
    value_list=[]
    for date_entry in trading_date_list:
        # trade_info_list contain : 'trade_volume','trade_transaction','trade_value'
        trade_info_list = Twse_Trading_Warrant.objects.get_trade_info_by_date(date_entry)
        temp1=[]
        temp2=[]
        temp3=[]
        for item in trade_info_list:
            # remember to transform decimal (django model field) type to float type, in order to save in json format.
            temp1.append(float(item[0]))
            temp2.append(float(item[1]))
            temp3.append(float(item[2]))
        volume_list.append(temp1)
        transaction_list.append(temp2)
        value_list.append(temp3)
            
    # write to file
    json_data = {'trading_date_list':list(trading_date_list),
               'trade_volume_data' :volume_list,
               'trade_transaction_data' :transaction_list,
               'trade_value_data' :value_list}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
trading_date_list = json_data['trading_date_list']
trade_volume_data = json_data['trade_volume_data'] 
trade_transaction_data = json_data['trade_transaction_data'] 
trade_value_data = json_data['trade_value_data'] 
#***preparing plot
trading_date_list = np.array(trading_date_list)
# get weekday array
mon,tue,wed,thr,fri,sat = get_weekday_array(trading_date_list)
#

# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    import matplotlib.pyplot as plt
    plt.ion()

# number of data point
N = len(trading_date_list)
x_pos = np.arange(N)
width = 0.35
fig, axarr = plt.subplots(3, sharex=True)
#
v_stats = violin_stats(trade_volume_data, kde_method, points=100)
result = axarr[0].violin(v_stats, positions=x_pos, vert=True, widths=0.95, showextrema=True, showmedians=True)
color_violin_by_weekday(result['bodies'], mon,tue,wed,thr,fri,sat)
#
v_stats = violin_stats(trade_transaction_data, kde_method, points=100)
result = axarr[1].violin(v_stats, positions=x_pos, vert=True, widths=0.95, showextrema=True, showmedians=True)
color_violin_by_weekday(result['bodies'], mon,tue,wed,thr,fri,sat)
#
v_stats = violin_stats(trade_value_data, kde_method, points=100)
result = axarr[2].violin(v_stats, positions=x_pos, vert=True, widths=0.95, showextrema=True, showmedians=True)
color_violin_by_weekday(result['bodies'], mon,tue,wed,thr,fri,sat)
#
       
axarr[0].set_ylabel('Trading Volume')
axarr[0].set_title('Distribution of Warrant Trading Volume')
axarr[1].set_ylabel('Trading Transaction')
axarr[1].set_title('Distribution of Warrant Trading Transaction')
axarr[2].set_ylabel('Trading Value')
axarr[2].set_title('Distribution of Warrant Trading Value')
        
for i in xrange(3):    
    axarr[i].set_xticks(x_pos[::5])
    axarr[i].set_xticks(x_pos, minor=True)
    axarr[i].set_xticklabels(trading_date_list[::5], rotation=45)
    axarr[i].grid(color='c', linestyle='--', linewidth=1)
    if len(sat) > 0:
        axarr[i].legend(ncol=6,
                    loc='upper left')
    else:
        axarr[i].legend(ncol=5,
                    loc='upper left')


fig.set_size_inches(18.5, 10.5)
# water mark position bottom right
fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
         fontsize=50, color='gray',
         ha='right', va='bottom', alpha=0.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
