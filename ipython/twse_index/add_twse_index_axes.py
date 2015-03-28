# coding: utf-8
import json
import matplotlib  
from matplotlib.finance import candlestick_ohlc
import os

from core.models import Twse_Index_Stats
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, convertToDate

def add_twse_index_axes(ax, start_date, end_date):
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
