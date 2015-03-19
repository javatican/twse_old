# coding: utf-8
# This program is used to inspect implied volatility variations over weekday. 
#
# This is the 6th version. display difference of IV values from its average in a violin plot
# only include data whose difference is -3%<diff<3%, the other are excluded to avoid violin plot 'stretching' by outliers.
import json
import matplotlib 
from matplotlib.cbook import violin_stats
import os

from core.models import Twse_Trading_Processed, Warrant_Item
import numpy as np
from warrant_app.utils.dateutil import DateEncoder
from warrant_app.utils.mpl_util import get_weekday_array, kde_method, set_colors, \
    set_colors_2

_FORCE_REGEN=False
_INTERACTIVE = True
#_INTERACTIVE=False
#number of day average
DAY_AVERAGE=3
#***preparing data
fname="ipython/iv_stats/iv_stats_6_violin_20141201_20150310"
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
    iv_diff_arr_by_warrant=np.zeros((warrant_count, trading_date_count-DAY_AVERAGE))
    for i, warrant in enumerate(warrant_list):
#       
        a_list = warrant.get_trading_warrant_list().filter(implied_volatility__isnull=False).order_by('trading_date').values_list('trading_date','implied_volatility')
#         a_list = warrant.get_trading_warrant_list().filter(implied_volatility__isnull=False, 
#                                                            moneyness__gt=-0.15,
#                                                            moneyness__lt=0.15,
#                                                            time_to_maturity__gt=0.1,
#                                                            trade_transaction__gt=3,
#                                                            ).order_by('trading_date').values_list('trading_date','implied_volatility')

        #create a dict to store (date,iv) pair
        a_dict={}
        for item in a_list:
            #implied_volatility (from Django model ) is Decimal type, need to change it to float type
            #item: ('trading_date','implied_volatility') pair
            a_dict[item[0]]=float(item[1])
        #use dict.get(), with default option, set the empty iv values to np.nan
        # so now iv_list has 'complete' list of IV values(one for each trading date, the non-existing ones set to np.nan)
        iv_list=[a_dict.get(trading_date, np.nan) for trading_date in trading_date_list]
        iv_array = np.array(iv_list) 
        # calc average of iv values 
        avg_array=np.zeros(trading_date_count-DAY_AVERAGE)
#
        for j in np.arange(DAY_AVERAGE):
            sli=slice(j, -1*DAY_AVERAGE+j)
            avg_array=avg_array+iv_array[sli]
        # any IV of np.nan value will still be np.nan after addition, division operations.
        avg_array=avg_array/DAY_AVERAGE
        # iv_diff as percentage
        iv_diff=(iv_array[DAY_AVERAGE:] - avg_array)*100
        iv_diff_arr_by_warrant[i]=iv_diff
    # write to file (only store 2 decimal digits for iv data)
    # remember to call .tolist() for changing np arrays to list, in order to save in json format
    json_data = {'trading_date_list':list(trading_date_list)[DAY_AVERAGE:],
               'iv_diff_list' :np.around(iv_diff_arr_by_warrant,decimals=2).tolist()}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
trading_date_list = json_data['trading_date_list']
iv_diff_list = json_data['iv_diff_list'] 
#***preparing plot
trading_date_list = np.array(trading_date_list)
iv_diff_array = np.array(iv_diff_list) 
# get weekday array
mon,tue,wed,thr,fri,sat, between_gap, others = get_weekday_array(trading_date_list, between_gap_flag=True)
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
fig, axarr = plt.subplots(2, sharex=True)
#Transpose iv_diff_array(each row stores data for each trading_date) and remove np.nan
iv_diff_array=iv_diff_array.T 
iv_diff_data=[]
for i in xrange(N):
    i_data = iv_diff_array[i]
    #i_data_r=i_data[~np.isnan(i_data)]
    i_data_r=i_data[np.logical_and(i_data<3, i_data>-3)] 
    iv_diff_data.append(i_data_r)
v_stats = violin_stats(iv_diff_data, kde_method, points=200)

result = axarr[0].violin(v_stats, positions=x_pos, vert=True, widths=0.95, showextrema=False, showmedians=True)
#get list of matplotlib.collections.PolyCollection
set_colors(result['bodies'], mon,tue,wed,thr,fri,sat)

axarr[0].set_ylabel('Difference from average')
axarr[0].set_title('Distribution of Warrant IV variation from averages')
axarr[0].set_xticks(x_pos[::5])
axarr[0].set_xticks(x_pos, minor=True)
axarr[0].set_xticklabels(trading_date_list[::5], rotation=45)
axarr[0].grid(color='c', linestyle='--', linewidth=1)
if len(sat) > 0:
    axarr[0].legend(ncol=6,
                loc='upper left')
else:
    axarr[0].legend(ncol=5,
                loc='upper left')
    
result = axarr[1].violin(v_stats, positions=x_pos, widths=0.95,
                      showextrema=False, showmedians=True)
set_colors_2(result['bodies'], between_gap, others)
        
axarr[1].set_xticks(x_pos[::5])
axarr[1].set_xticks(x_pos, minor=True)
axarr[1].set_xticklabels(trading_date_list[::5], rotation=45)
axarr[1].grid(color='c', linestyle='--', linewidth=1)
axarr[1].legend(ncol=2,
                loc='upper left')
#
fig.set_size_inches(18.5, 10.5)
# water mark position bottom right
fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
         fontsize=50, color='gray',
         ha='right', va='bottom', alpha=0.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
