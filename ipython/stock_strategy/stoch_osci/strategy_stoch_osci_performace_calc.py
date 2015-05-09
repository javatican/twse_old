from core.models import Selection_Stock_Item, Stock_Item

future_range_list=[3,5,10,20]
field_name_list=['performance_3day', 'performance_5day','performance_10day','performance_20day']
# get all the stock ids that were selected in any moment
stock_id_list = Selection_Stock_Item.objects.all().values_list('stock_symbol_id', flat=True).distinct().order_by('stock_symbol_id')
for stock_id in stock_id_list:
    stock_item=Stock_Item.objects.get(id=stock_id)
    # get the selection_stock_items for the target stock 
    selection_list = stock_item.selection_list2.all().select_related('trading').order_by('trading_date')
    # get the trading date for the first selection_stock_item
    start_date=selection_list[0].trading_date
    # get the trading items for the target stock from the 'start' date
    trading_list = stock_item.twse_trading_list.filter(trading_date__gte=start_date).order_by('trading_date')
    # get all trading ids in a list, so we can locate the 'index' of the corresponding one in selection_list 
    trading_id_list =  [trading.id for trading in trading_list]
    # get all closing price in a list
    closing_price_list = [float(trading.closing_price) for trading in trading_list]
    # locate the 'index'
    for sel_item in selection_list:
        the_index=trading_id_list.index(sel_item.trading.id)
        for rg,field_name in zip(future_range_list,field_name_list):
            next_index=the_index+rg
            if next_index <len(trading_id_list):
                if closing_price_list[the_index] ==0: continue
                diff_percentage = round((closing_price_list[next_index] - closing_price_list[the_index])*100.0/closing_price_list[the_index],1)
                setattr(sel_item, field_name, diff_percentage)
        sel_item.save() 
