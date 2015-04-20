# coding: utf-8
# This program is used to plot stock price(boxs and whiskers) and volume(bars)
# I use matplotlib.finance packages to do the candlestick plot. But there are problems
# with gaps within trading_date data.
# Originally I use the matplotlib.dates modules to show ticks, but there are gaps 
# between trading_dates which can not be removed from plot. 
# So I have to do the ticks my own way. 
import datetime

from core.models import Stock_Item, Trading_Date
import numpy as np
from warrant_app.utils.dateutil import convertToDate
from warrant_app.utils.trading_util import watch_list_bull, \
    watch_list_bear, breakout_list_bull, breakout_list_bear, pre_filtering_bull, \
    pre_filtering_bear, breakout2_list_bull, breakout3_list_bull, \
    breakout2_list_bear, breakout3_list_bear

tod=datetime.datetime.today().date()
#parameters:
INSPECT_LATEST_DATA=True
# trading date range to inspect the k/d, adx values
TRADING_DATE_RANGE=3
# long k threshold
BULL_LONG_K_LEVEL=50
BULL_SHORT_K_LEVEL=80
BEAR_LONG_K_LEVEL=50
BEAR_SHORT_K_LEVEL=20
ADX_LEVEL=20
#
long_breakout_list=[]
short_breakout_list=[]
long_breakout2_list=[]
short_breakout2_list=[]
long_breakout3_list=[]
short_breakout3_list=[]
long_watch_list=[]
short_watch_list=[]
#
stock_items = Stock_Item.objects.all()
# calculate target trading date
if INSPECT_LATEST_DATA:
    target_td = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[TRADING_DATE_RANGE-1]
    print "Run the selection at %s" % tod
else:
    TARGET_TRADING_DATE='20150415'
    ttd=convertToDate(TARGET_TRADING_DATE)
    target_td = Trading_Date.objects.filter(trading_date__lte=ttd).values_list('trading_date', flat=True).order_by('-trading_date')[TRADING_DATE_RANGE-1]
    print "Run the selection for %s" % TARGET_TRADING_DATE
    
for stock in stock_items: 
    # first make sure the stocks have trading entries with non null strategy.fourteen_day_k, strategy.seventy_day_k, strategy.adx values within the trading date range
    trading_entries = stock.twse_trading_list.filter(trading_date__gte=target_td, 
                                                     strategy__fourteen_day_k__isnull=False, 
                                                     strategy__seventy_day_k__isnull=False, 
                                                     strategy__adx__isnull=False).select_related('strategy').order_by('trading_date')
    if not INSPECT_LATEST_DATA: 
        trading_entries = trading_entries.filter(trading_date__lte=ttd)
    if len(trading_entries) != TRADING_DATE_RANGE: 
        continue 
    data_list = [(float(entry.strategy.seventy_day_k),
      float(entry.strategy.seventy_day_d),
      float(entry.strategy.fourteen_day_k),
      float(entry.strategy.fourteen_day_d),
#      float(entry.strategy.pdi14),
#      float(entry.strategy.ndi14), 
      float(entry.strategy.adx)) for entry in trading_entries]
    data_array=np.asarray(data_list)
    data_array_t= data_array.T
    selected=False
    if pre_filtering_bull(data_array_t, BULL_LONG_K_LEVEL, ADX_LEVEL):
        if breakout_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
            long_breakout_list.append(stock)    
            selected=True    
        elif breakout2_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
            long_breakout2_list.append(stock)
            selected=True    
        elif breakout3_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
            long_breakout3_list.append(stock)
            selected=True    
        elif watch_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
            long_watch_list.append(stock)
            selected=True    
        if selected:
            #check if there are 'call' warrants available for trading
            stock.has_warrant=stock.warrant_item_list.call_list().filter(last_trading_date__gte=tod).exists()
    elif pre_filtering_bear(data_array_t, BEAR_LONG_K_LEVEL, ADX_LEVEL):
        if breakout_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
            short_breakout_list.append(stock)
            selected=True
        elif breakout2_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
            short_breakout2_list.append(stock)
            selected=True    
        elif breakout3_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
            short_breakout3_list.append(stock)
            selected=True    
        elif watch_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
            short_watch_list.append(stock)
            selected=True 
        if selected:
            #check if there are 'put' warrants available for trading
            stock.has_warrant=stock.warrant_item_list.put_list().filter(last_trading_date__gte=tod).exists()
    if selected:   
        stock.last_short_k=data_array[-1][2]
    
print "Number of bull breakout target: %s" % len(long_breakout_list)
for stock in long_breakout_list:
    print "Found a breakout bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)

print "Number of bull breakout 2nd day target: %s" % len(long_breakout2_list)
for stock in long_breakout2_list:
    print "Found a breakout 2nd day bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
    
print "Number of bull breakout 3rd day target: %s" % len(long_breakout3_list)
for stock in long_breakout3_list:
    print "Found a breakout 3rd day bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
    
print "Number of bull watch target: %s" % len(long_watch_list)
for stock in long_watch_list:
    print "Found a watch bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
print "============================================================="  
print "Number of bear breakout target: %s" % len(short_breakout_list)
for stock in short_breakout_list:
    print "Found a breakout bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
   
print "Number of bear breakout 2nd day target: %s" % len(short_breakout2_list)
for stock in short_breakout2_list:
    print "Found a breakout 2nd day bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
    
print "Number of bear breakout 3rd day target: %s" % len(short_breakout3_list)
for stock in short_breakout3_list:
    print "Found a breakout 3rd day bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
    
print "Number of bear watch target: %s" % len(short_watch_list)
for stock in short_watch_list:
    print "Found a watch bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
        

       
    
    