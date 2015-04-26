# coding: utf-8
# This program is used to plot stock price(boxs and whiskers) and volume(bars)
# I use matplotlib.finance packages to do the candlestick plot. But there are problems
# with gaps within trading_date data.
# Originally I use the matplotlib.dates modules to show ticks, but there are gaps 
# between trading_dates which can not be removed from plot. 
# So I have to do the ticks my own way. 
import json
import math
import matplotlib  
from matplotlib.finance import candlestick_ohlc
import os

from core.models import Stock_Item, Trading_Date
import numpy as np
from warrant_app.utils.dateutil import DateEncoder, convertToDate

from matplotlib.font_manager import FontProperties
font = FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size = 14)

_USE_LATEST_DATA=True
_FORCE_REGEN = False
_INTERACTIVE = True
_SHOW_LEGEND=False
# _INTERACTIVE=False
#***preparing data
stock_symbol='2317'
if _USE_LATEST_DATA:
    date_list = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[:120]
    start_date=date_list[len(date_list)-1]
    end_date=date_list[0]
else:
    end_date = '20150401'
    end_date=convertToDate(end_date)
    date_list = Trading_Date.objects.filter(trading_date__lte=end_date).values_list('trading_date', flat=True).order_by('-trading_date')[:120]
    start_date=date_list[len(date_list)-1]
    end_date=date_list[0]
directory="ipython/stock_strategy/inspect/%s" % end_date.strftime("%Y%m%d")
if not os.path.exists(directory):
    os.makedirs(directory)
fname = "%s/%s_stoch_osci_%s_%s" % (directory, stock_symbol, start_date, end_date)
filename = '%s.txt' % fname
trading_date_list = None
if _FORCE_REGEN or not os.path.isfile(filename):
    stock=Stock_Item.objects.get_by_symbol(stock_symbol)
    entries = stock.twse_trading_list.filter(trading_date__gte=start_date, 
                                             trading_date__lte=end_date,
                                             strategy__seventy_day_k__isnull=False).select_related('strategy').order_by('trading_date') 
    price_data=[]
    long_kd_data=[]
    short_kd_data=[]    
    adx_data=[]          
    for entry in entries:                    
        price_data.append((entry.trading_date, 
                   float(entry.opening_price), 
                   float(entry.highest_price), 
                   float(entry.lowest_price), 
                   float(entry.closing_price), 
                   float(entry.trade_volume),
                   float(entry.year_volume_avg) if entry.year_volume_avg else None))
        long_kd_data.append((entry.trading_date, 
                   float(entry.strategy.seventy_day_k), 
                   float(entry.strategy.seventy_day_d)))
        short_kd_data.append((entry.trading_date, 
                   float(entry.strategy.fourteen_day_k), 
                   float(entry.strategy.fourteen_day_d)))
        adx_data.append((entry.trading_date, 
                   float(entry.strategy.pdi14), 
                   float(entry.strategy.ndi14),
                   float(entry.strategy.adx)))
    # write to file
    json_data = {'stock_name': stock.short_name,
                 '%s_price' % stock_symbol : price_data, 
                 '%s_70kd' % stock_symbol : long_kd_data, 
                 '%s_14kd' % stock_symbol : short_kd_data, 
                 '%s_adx' % stock_symbol : adx_data }
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
stock_name=json_data['stock_name']
print stock_name
price_data = json_data['%s_price' % stock_symbol ] 
long_kd_data = json_data['%s_70kd' % stock_symbol ] 
short_kd_data = json_data['%s_14kd' % stock_symbol ] 
adx_data = json_data['%s_adx' % stock_symbol ] 
#***preparing plot
# interactive mode for pyplot
if not _INTERACTIVE:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    import matplotlib.pyplot as plt
    plt.ion()

fig, ax = plt.subplots()
trading_date_list = [] 
volume_list = []
year_volume_avg_list = [] 
opening_price_list = []
closing_price_list = []
for i, item in enumerate(price_data):
    trading_date_list.append(item[0])
    opening_price_list.append(item[1])
    closing_price_list.append(item[4])
    volume_list.append(item[5]/1000)
    year_volume_avg_list.append(item[6]/1000 if item[6] else None)
    # store a list of continuous integers for the 'float' date.
    # This is needed for finance lib candlestick_ohlc() to show continuous bar and whiskers without gap.
    item[0] = i + 1
candlestick_ohlc(ax, price_data, width=0.8, colorup='r', colordown='g')
N = len(trading_date_list)
x_pos = np.arange(1, N + 1)
#
ax.set_ylabel('price')
ax.set_title('%s(%s) price chart' % (stock_symbol, stock_name), fontproperties = font)
ax.set_xticks(x_pos[::10])
ax.set_xticks(x_pos, minor=True)
ax.set_xticklabels(trading_date_list[::10], rotation=45)
ax.grid(color='c', linestyle='--', linewidth=1)
# to show several axes objects in the same figure, here adjust the y limits of the first axes, so there is space at the bottom to show other axes.
pad = 1.2
yl = ax.get_ylim()
y_tick_gap=math.ceil((yl[1]-yl[0])/5)
ax.yaxis.set_ticks(np.arange(yl[0], yl[1], y_tick_gap))
#ax.locator_params(tight=True, axis='y',nbins=4)
ax.set_ylim(yl[0] - (yl[1] - yl[0]) * pad, yl[1])
# add a 2nd axes for volumes
# axes position paramters here:
X_START=0.125
X_END=0.9
Y_START=0.52
Y_RANGE=0.1
Y_GAP=0.0
ax2 = ax.twinx()
ax2.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
# change into nd array
opening_price_arr = np.asarray(opening_price_list)
closing_price_arr = np.asarray(closing_price_list)
volume_arr = np.asarray(volume_list)
down = opening_price_arr - closing_price_arr > 0
up = opening_price_arr - closing_price_arr < 0
no_change = opening_price_arr - closing_price_arr == 0
year_volume_avg_arr = np.array(year_volume_avg_list, dtype=np.float)
has_avg_data = ~np.isnan(year_volume_avg_arr)
ax2.bar(x_pos[up], volume_arr[up], color='red', width=0.8, align='center')
ax2.bar(x_pos[down], volume_arr[down], color='green', width=0.8, align='center')
ax2.bar(x_pos[no_change], volume_arr[no_change], color='yellow', width=0.8, align='center')
ax2.plot(x_pos[has_avg_data], year_volume_avg_arr[has_avg_data], 'r-', label='year avg vol')

ax2.locator_params(tight=True, axis='y',nbins=4)
ax2.set_ylabel('volume')
ax2.grid(color='0.8', linestyle='--', linewidth=1)
# add a 3rd axes for 70-day k/d
ax3 = ax.twinx()
Y_START=Y_START-Y_RANGE-Y_GAP
ax3.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
seventy_k=[]
seventy_d=[]
for i, item in enumerate(long_kd_data):
    seventy_k.append(item[1])
    seventy_d.append(item[2])
    
# change into nd array
seventy_k_arr = np.asarray(seventy_k)
seventy_d_arr = np.asarray(seventy_d)
# blue line for 70-day k,  red line for 70-day d
line_70k=ax3.plot(x_pos, seventy_k_arr, 'b-', label='%K(70,3)')
line_70d=ax3.plot(x_pos, seventy_d_arr, 'r-', label='%D(3)')
# black horizontal line for 50 mark
line_50_mark=ax3.plot([x_pos[0],x_pos[-1]], [50,50], 'y-',linewidth=2)
#
ax3.locator_params(tight=True, axis='y',nbins=5)
ax3.grid(color='c', linestyle='--', linewidth=1)
ax3.set_ylabel('STO')
if _SHOW_LEGEND:
    ax3.legend(handles=[line_70k[0],line_70d[0]], ncol=2, loc='upper left', prop={'size':10})

# add a 4th axes for 14-day k/d
ax4 = ax.twinx()
Y_START=Y_START-Y_RANGE-Y_GAP
ax4.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
fourteen_k=[]
fourteen_d=[]
for i, item in enumerate(short_kd_data):
    fourteen_k.append(item[1])
    fourteen_d.append(item[2])
    
# change into nd array
fourteen_k_arr = np.asarray(fourteen_k)
fourteen_d_arr = np.asarray(fourteen_d)
# blue line for 14-day k,  red line for 14-day d
line_14k=ax4.plot(x_pos, fourteen_k_arr, 'b-', label='%K(14,3)')
line_14d=ax4.plot(x_pos, fourteen_d_arr, 'r-', label='%D(3)')
# black horizontal line for 80 and 20 mark
line_80_mark=ax4.plot([x_pos[0],x_pos[-1]], [80,80], 'y-',linewidth=2)
line_20_mark=ax4.plot([x_pos[0],x_pos[-1]], [20,20], 'y-',linewidth=2)
#
ax4.locator_params(tight=True, axis='y',nbins=5)
ax4.grid(color='c', linestyle='--', linewidth=1)
ax4.set_ylabel('STO')
if _SHOW_LEGEND:
    ax4.legend(handles=[line_14k[0],line_14d[0]], ncol=2, loc='upper left', prop={'size':10})
# add a 5th axes for ADX
ax5 = ax.twinx()
Y_START=Y_START-Y_RANGE-Y_GAP
ax5.set_position(matplotlib.transforms.Bbox([[X_START, Y_START-Y_RANGE], [X_END, Y_START]]))
pdi14=[]
ndi14=[]
adx=[]
for i, item in enumerate(adx_data):
    pdi14.append(item[1])
    ndi14.append(item[2])
    adx.append(item[3])
    
# change into nd array
pdi14_arr = np.asarray(pdi14)
ndi14_arr = np.asarray(ndi14)
adx_arr = np.asarray(adx)
# blue line for 14-day k,  red line for 14-day d
line_pdi14=ax5.plot(x_pos, pdi14_arr, 'g-', label='+DI')
line_ndi14=ax5.plot(x_pos, ndi14_arr, 'r-', label='-DI')
line_adx=ax5.plot(x_pos, adx_arr, 'k-', label='ADX(14)')
# black horizontal line for 20 mark
line_20_mark=ax5.plot([x_pos[0],x_pos[-1]], [20,20], 'y-',linewidth=2)
#
ax5.locator_params(tight=True, axis='y',nbins=5)
ax5.grid(color='c', linestyle='--', linewidth=1)
ax5.set_ylabel('ADX')
if _SHOW_LEGEND:
    ax5.legend(handles=[line_pdi14[0],line_ndi14[0], line_adx[0]], ncol=3, loc='upper left', prop={'size':10})

fig.set_size_inches(18.5, 10.5)
# water mark position bottom right
fig.text(0.95, 0.05, 'Property of ryan.nieh@gmail.com ',
         fontsize=50, color='gray',
         ha='right', va='bottom', alpha=0.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
