# coding: utf-8
# This program is used to plot stock price(boxs and whiskers) and volume(bars)
# I use matplotlib.finance packages to do the candlestick plot. But there are problems
# with gaps within trading_date data.
# Originally I use the matplotlib.dates modules to show ticks, but there are gaps 
# between trading_dates which can not be removed from plot. 
# So I have to do the ticks my own way. 

from core.models import Stock_Item
from warrant_app.utils.trading_util import Strategy_Plot_By_Stoch_Pop_For_Stock


stock_symbol='2002'
stock=Stock_Item.objects.get_by_symbol(stock_symbol)
plot_obj = Strategy_Plot_By_Stoch_Pop_For_Stock(stock, category='inspect', interactive_mode=True)
plot_obj.do()
        