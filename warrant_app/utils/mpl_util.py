from datetime import timedelta
from matplotlib import mlab

from warrant_app.utils.dateutil import string_to_date,DateEncoder, convertToDate

import json
import matplotlib  
from matplotlib.finance import candlestick_ohlc
import os
from core.models import Twse_Index_Stats
import numpy as np 

# used with matplotlib.cbook.violin_stats function 
def kde_method(X, coords):
    kde = mlab.GaussianKDE(X, 'scott')
    return kde.evaluate(coords)

# based on trading_date list , return 'weekday' list
def get_weekday_array(trading_date_list, between_gap_flag=False):
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
    if between_gap_flag:
        return (mon, tue, wed, thr, fri, sat, between_gap, others)
    else:
        return (mon, tue, wed, thr, fri, sat)

# for coloring violin plot based on weekdays
def color_violin_by_weekday(polycoll_list, mon, tue, wed, thr, fri, sat):
    for n in mon: 
        polycoll_list[n].set_facecolor('r')
        polycoll_list[n].set_label('Mon')
    for n in tue: 
        polycoll_list[n].set_facecolor('y')
        polycoll_list[n].set_label('Tue')
    for n in wed: 
        polycoll_list[n].set_facecolor('b')
        polycoll_list[n].set_label('Wed')
    for n in thr: 
        polycoll_list[n].set_facecolor('g')
        polycoll_list[n].set_label('Thr')
    for n in fri: 
        polycoll_list[n].set_facecolor('m')
        polycoll_list[n].set_label('Fri')
    if len(sat) > 0 :
        for n in sat: 
            polycoll_list[n].set_facecolor('c')
            polycoll_list[n].set_label('Sat')
            
# for coloring violin plot based on 'between_gap and others'
def color_violin_by_btw_gap(polycoll_list, between_gap, others):
    # important: need to plot others first, then between_gap
    for n in others: 
        polycoll_list[n].set_facecolor('0.8')
        polycoll_list[n].set_label('others')
    for n in between_gap: 
        polycoll_list[n].set_facecolor('k')
        polycoll_list[n].set_label('Before/after trading gap')
        
def color_bar_by_weekday(ax, x_pos, y_pos, mon, tue, wed, thr, fri, sat, width):
    rect_mon = ax.bar(x_pos[mon], y_pos[mon], width, color='r')
    rect_tue = ax.bar(x_pos[tue], y_pos[tue], width, color='y')
    rect_wed = ax.bar(x_pos[wed], y_pos[wed], width, color='b')
    rect_thr = ax.bar(x_pos[thr], y_pos[thr], width, color='g')
    rect_fri = ax.bar(x_pos[fri], y_pos[fri], width, color='m')
    if len(sat) > 0 : rect_sat = ax.bar(x_pos[sat], y_pos[sat], width, color='c')
    if len(sat) > 0:
        ax.legend((rect_mon[0], rect_tue[0], rect_wed[0], rect_thr[0], rect_fri[0], rect_sat[0]),
                    ('Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat'),
                    ncol=6,
                    loc='upper left')
    else:
        ax.legend((rect_mon[0], rect_tue[0], rect_wed[0], rect_thr[0], rect_fri[0]),
                    ('Mon', 'Tue', 'Wed', 'Thr', 'Fri'),
                    ncol=5,
                    loc='upper left')

def color_bar_btw_gap(ax, x_pos, y_pos, between_gap, others, width):
    rect_others = ax.bar(x_pos[others], y_pos[others], width, color='0.8')
    rect_btw_gap = ax.bar(x_pos[between_gap], y_pos[between_gap], width, color='k')
    ax.legend((rect_btw_gap[0], rect_others[0]),
                ('Before/after trading gap', 'others'),
                ncol=2,
                loc='upper left')

def add_twse_index_axes(ax, start_date, end_date):
    if '-' in start_date:
        start_date=start_date.replace('-','')
    if '-' in end_date:
        end_date=end_date.replace('-','')
    fname = "ipython/twse_index/twse_index_%s_%s" % (start_date, end_date)
    filename = '%s.txt' % fname
    if not os.path.isfile(filename):
        entries = Twse_Index_Stats.objects.ohlc_between_dates(convertToDate(start_date), convertToDate(end_date))
        # write to file
        json_data = {'twse_index_stats': entries, }
        with open(filename, 'w') as fp:
            json.dump(json_data, fp, cls=DateEncoder)
    #
    with open(filename, 'r') as fp:
        json_data = json.load(fp) 
    twse_index_stats = json_data['twse_index_stats'] 
    
    trading_date_list = [] 
    volume_list = [] 
    opening_price_list = []
    closing_price_list = []
    for i, item in enumerate(twse_index_stats):
        trading_date_list.append(item[0])
        opening_price_list.append(item[1])
        closing_price_list.append(item[4])
        volume_list.append(item[5])
        # store a list of continuous integers for the 'float' date.
        item[0] = i + 1
    candlestick_ohlc(ax, twse_index_stats, width=0.8, colorup='r', colordown='g')
    N = len(trading_date_list)
    x_pos = np.arange(1, N + 1)
    #
    ax.set_ylabel('TWSE Index')
    ax.set_title('TWSE Index')
    ax.set_xticks(x_pos[::5])
    ax.set_xticks(x_pos, minor=True)
    ax.set_xticklabels(trading_date_list[::5], rotation=45)
    ax.grid(color='c', linestyle='--', linewidth=1)
    #
    pad = 0.35
    yl = ax.get_ylim()
    ax.set_ylim(yl[0] - (yl[1] - yl[0]) * pad, yl[1])
    # add a 2nd axes for volumes
    ax2 = ax.twinx()
    ax2.set_position(matplotlib.transforms.Bbox([[0.125, 0.1], [0.9, 0.2]]))
    # change into nd array
    opening_price_arr = np.asarray(opening_price_list)
    closing_price_arr = np.asarray(closing_price_list)
    volume_arr = np.asarray(volume_list)
    down = opening_price_arr - closing_price_arr > 0
    up = opening_price_arr - closing_price_arr < 0
    no_change = opening_price_arr - closing_price_arr == 0
    ax2.bar(x_pos[up], volume_arr[up], color='red', width=0.8, align='center')
    ax2.bar(x_pos[down], volume_arr[down], color='green', width=0.8, align='center')
    ax2.bar(x_pos[no_change], volume_arr[no_change], color='yellow', width=0.8, align='center')
  
    
