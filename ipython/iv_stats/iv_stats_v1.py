# coding: utf-8
# This program is used to inspect implied volatility variations over weekday. 
# Does iv correlated with hedge buy/sell value difference of warrants?
#
# This is the first version : only select warrants that has 'full' set of IV entries
# (ie. for every available trading_date). Therefore, the sample data are too small( hundreds ).
#
# Also allow selection of trading_date period
import json
import matplotlib 
import os

from core.models import Twse_Trading_Processed, Warrant_Item
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, string_to_date
from datetime import timedelta
# _INTERACTIVE = True
_INTERACTIVE=False
_DATE_RANGE=True
#number of day average
DAY_AVERAGE=3
#***preparing data
fname="iv_stats_20150205_0302"
filename = '%s.txt' % fname
if _DATE_RANGE:
    date_start=string_to_date('2015-02-05', date_format='%Y-%m-%d')
    date_end=string_to_date('2015-03-02', date_format='%Y-%m-%d')
trading_date_list = None
iv_above_sum = None
iv_below_sum = None
if not os.path.isfile(filename):
    # first get all the trading_date which has trading_warrant
    trading_date_list = Twse_Trading_Processed.objects.get_dates()
    if _DATE_RANGE : trading_date_list = trading_date_list.filter(trading_date__gte=date_start, trading_date__lte=date_end)
    trading_date_count = len(trading_date_list)
    iv_above_sum=np.zeros(trading_date_count-DAY_AVERAGE)
    iv_below_sum=np.zeros(trading_date_count-DAY_AVERAGE)
    iv_flat_sum=np.zeros(trading_date_count-DAY_AVERAGE)
    # get all warrants
    warrant_list = Warrant_Item.objects.all()
    i=0
    for warrant in warrant_list:
        iv_list = warrant.twse_trading_warrant_list.filter(implied_volatility__isnull=False).order_by('trading_date').values_list('implied_volatility', flat=True)
        if _DATE_RANGE : iv_list = iv_list.filter(trading_date__gte=date_start, trading_date__lte=date_end)
        iv_count = len(iv_list)
        #only select warrants that has full list of iv entries
        if iv_count != trading_date_count: continue
        # calc average of iv values 
        # need to do below because iv_list's element type is Decimal object, change it to float
        iv_array = np.zeros(iv_count)
        for n, el in enumerate(iv_list): 
            iv_array[n] = float(el)
            
        avg_array=np.zeros(iv_count-DAY_AVERAGE)
#
        for j in np.arange(DAY_AVERAGE):
            sli=slice(j, -1*DAY_AVERAGE+j)
            avg_array=avg_array+iv_array[sli]
        avg_array=avg_array/DAY_AVERAGE
        iv_above=iv_array[DAY_AVERAGE:] > avg_array
        iv_above=iv_above.astype(int)
        iv_below=iv_array[DAY_AVERAGE:] < avg_array
        iv_below=iv_below.astype(int)
        iv_flat=iv_array[DAY_AVERAGE:] == avg_array
        iv_flat=iv_flat.astype(int)
        iv_above_sum=iv_above_sum+iv_above
        iv_below_sum=iv_below_sum+iv_below
        iv_flat_sum=iv_flat_sum+iv_flat
#
        i+=1
    print "total warrants that have full list of iv entries: %s" % i
    # write to file
    json_data = {'total_warrant_count':i,
                 'trading_date_list':list(trading_date_list)[DAY_AVERAGE:],
               'iv_above_sum' :iv_above_sum.tolist(),
               'iv_below_sum':iv_below_sum.tolist(),
               'iv_flat_sum' :iv_flat_sum.tolist()}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
trading_date_list = json_data['trading_date_list']
iv_above_sum = json_data['iv_above_sum']
iv_below_sum = json_data['iv_below_sum']
#***preparing plot
trading_date_list = np.array(trading_date_list)
iv_above_sum = np.array(iv_above_sum)
iv_below_sum = np.array(iv_below_sum) 
iv_diff = iv_above_sum - iv_below_sum
mon = []
tue = []
wed = []
thr = []
fri = []
sat = []
#
between_gap = [] 
others = []
i = 0
previous_date = None
for trading_date_str in trading_date_list:
    trading_date = string_to_date(trading_date_str, date_format='%Y-%m-%d')
    day_of_week = trading_date.weekday() + 1
    if day_of_week == 1:
        mon.append(i)
    elif day_of_week == 2:
        tue.append(i)
    elif day_of_week == 3:
        wed.append(i)
    elif day_of_week == 4:
        thr.append(i)
    elif day_of_week == 5:
        fri.append(i)
    elif day_of_week == 6:
        sat.append(i)
    if i > 0:
        if trading_date > previous_date + timedelta(days=1):
            # gap greater than 1 day
            between_gap.append(i - 1)
            between_gap.append(i)
        else:
            others.append(i - 1)
            others.append(i)
    previous_date = trading_date
    i += 1
#

# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
if _INTERACTIVE:
    plt.ion()

# number of data point
N = len(trading_date_list)
x_pos = np.arange(N)
width = 0.35
fig, axarr = plt.subplots(2, sharex=True)
#
rect_mon = axarr[0].bar(x_pos[mon], iv_diff[mon], width, color='r')
rect_tue = axarr[0].bar(x_pos[tue], iv_diff[tue], width, color='y')
rect_wed = axarr[0].bar(x_pos[wed], iv_diff[wed], width, color='b')
rect_thr = axarr[0].bar(x_pos[thr], iv_diff[thr], width, color='g')
rect_fri = axarr[0].bar(x_pos[fri], iv_diff[fri], width, color='m')
if len(sat) > 0 : rect_sat = axarr[0].bar(x_pos[sat], iv_diff[sat], width, color='c')
axarr[0].set_ylabel('Counts')
axarr[0].set_title('Warrant IV values compared to its averages')
axarr[0].set_xticks(x_pos[::5])
axarr[0].set_xticks(x_pos, minor=True)
axarr[0].set_xticklabels(trading_date_list[::5], rotation=45)
axarr[0].grid(color='c', linestyle='--', linewidth=1)
if len(sat) > 0:
    axarr[0].legend((rect_mon[0],rect_tue[0],rect_wed[0],rect_thr[0],rect_fri[0],rect_sat[0]),
                ('Mon','Tue','Wed','Thr','Fri','Sat'),
                ncol=6,
                loc='upper left')
else:
    axarr[0].legend((rect_mon[0],rect_tue[0],rect_wed[0],rect_thr[0],rect_fri[0]),
                ('Mon','Tue','Wed','Thr','Fri'),
                ncol=5,
                loc='upper left')
rect_others = axarr[1].bar(x_pos[others], iv_diff[others], width, color='0.8')
rect_btw_gap = axarr[1].bar(x_pos[between_gap], iv_diff[between_gap], width, color='k')
axarr[1].legend((rect_btw_gap[0], rect_others[0]),
                ('Between day gap', 'others'),
                ncol=2,
                loc='upper left')
fig.set_size_inches(18.5, 10.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
