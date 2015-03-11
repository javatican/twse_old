# coding: utf-8
# This program is used to inspect implied volatility graph over trading dates.
# Either display all warrants, or warrants for a specific target stock
import json
import matplotlib 
import os

from core.models import Twse_Trading_Processed, Warrant_Item, Stock_Item
import numpy as np
from warrant_app.utils.dateutil import DateEncoder

_INTERACTIVE = True
#_INTERACTIVE=False
#***preparing data
fname="iv_graph"
filename = '%s.txt' % fname
trading_date_list = None 
if not os.path.isfile(filename):
    # first get all the trading_date which has trading_warrant
    trading_date_list = Twse_Trading_Processed.objects.get_dates()
    trading_date_count = len(trading_date_list) 
    iv_data=[]
    # get all warrants
    warrant_list = Warrant_Item.objects.all()
    # Or select warrants for the specific target stock (eg. 2312)  
    #warrant_list = Stock_Item.objects.get(symbol='2312').warrant_item_list.all()
    for warrant in warrant_list:
        #get warrant's trading entries
        a_list = warrant.twse_trading_warrant_list.filter(implied_volatility__isnull=False).order_by('trading_date').values_list('trading_date','implied_volatility')
        #create a dict to store (date,iv) pair
        a_dict={}
        for item in a_list:
            #implied_volatility is Decimal object, need to change it to float
            #item: ('trading_date','implied_volatility') pair
            a_dict[item[0]]=float(item[1])
        #use dict.get(), with default option, set the empty iv values to np.nan
        iv_list=[a_dict.get(trading_date, np.nan) for trading_date in trading_date_list]
        iv_data.append(iv_list)
    # write to file
    json_data = {'trading_date_list':list(trading_date_list),
                 'iv_data': iv_data}
    with open(filename, 'w') as fp:
        json.dump(json_data, fp, cls=DateEncoder)
#
with open(filename, 'r') as fp:
    json_data = json.load(fp) 
trading_date_list = json_data['trading_date_list']
iv_data = json_data['iv_data'] 
        
#***preparing plot

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
linewidth = 1
#
fig=plt.figure()
ax=fig.add_subplot(111)
for iv_list in iv_data:
    iv_array = np.array(iv_list) 
    #for IV of value np.nan will be excluded from the graph.
    bool_mask=~np.isnan(iv_array)
    x=x_pos[bool_mask]
    y=iv_array[bool_mask]
    ax.plot(x,y, '--', linewidth=linewidth) 
    
ax.set_ylabel('IV')
ax.set_title('Warrant IV graphs')
ax.set_xticks(x_pos[::5])
ax.set_xticks(x_pos, minor=True)
ax.set_xticklabels(trading_date_list[::5], rotation=45)
ax.grid(color='c', linestyle='--', linewidth=1) 

fig.set_size_inches(18.5, 10.5)
if _INTERACTIVE:
    plt.show()
else:
    fig.savefig('%s.png' % fname)
