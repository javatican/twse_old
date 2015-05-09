# coding=utf8
from core.models import Selection_Stock_Item 


selection_list = Selection_Stock_Item.objects.all().select_related('trading')
for sel in selection_list:
    trade_volume=sel.trading.trade_volume
    year_volume_avg=sel.trading.year_volume_avg
    volume_change= float(trade_volume-year_volume_avg)*100.0/float(year_volume_avg)  if year_volume_avg else None
    sel.volume_change=volume_change
    sel.save()