# coding: utf-8
from core.cron import twse_daily_trading_job, twse_daily_summary_price_job
from core.models import Trading_Date



q_date_list=Trading_Date.objects.filter(trading_date__lte='2014-11-30', trading_date__gte='2014-11-01').values_list('trading_date', flat=True)

for  q_date in q_date_list:
    print "processing date %s" % q_date
    twse_daily_trading_job(q_date, process_stock_only=True)
    twse_daily_summary_price_job(q_date, process_stock_only=True)
