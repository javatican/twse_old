# coding: utf-8
from core.models import Trading_Date
from core.cron import twse_daily_trading_job, twse_daily_summary_price_job, \
    twse_manage_warrant_info_job, twse_trading_post_processing_job, \
    twse_black_scholes_calc_job, twse_manage_warrant_info_use_other_url_job


q_date_list=Trading_Date.objects.filter(trading_date__gt='2015-04-13').values_list('trading_date', flat=True)

for  q_date in q_date_list:
    print "processing date %s" % q_date
    twse_daily_trading_job(q_date)
    twse_daily_summary_price_job(q_date)

twse_manage_warrant_info_job()
twse_manage_warrant_info_use_other_url_job()
twse_trading_post_processing_job()
twse_black_scholes_calc_job()