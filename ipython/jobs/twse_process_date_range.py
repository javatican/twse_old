# coding: utf-8
from core.cron import twse_daily_trading_job, twse_daily_summary_price_job, \
    twse_manage_warrant_info_job, twse_trading_post_processing_job, \
    twse_black_scholes_calc_job, twse_manage_warrant_info_use_other_url_job, \
    download_twse_index_stats_job, download_twse_index_stats2_job, \
    twse_index_avg_calc_job, twse_stock_price_volume_avg_calc_job, \
    twse_stock_calc_stoch_osci_adx_job, download_twse_various_index_job, \
    twse_various_index_avg_calc_job, twse_various_index_calc_stoch_osci_adx_job
from core.models import Trading_Date, Twse_Trading_Processed, \
    Twse_Summary_Price_Processed


download_twse_index_stats_job(year=2015, month_list=[4,])
download_twse_index_stats2_job(year=2015, month_list=[4,])

last_processed_date=Twse_Trading_Processed.objects.get_last_processed()
q_date_list=Trading_Date.objects.filter(trading_date__gt=last_processed_date).values_list('trading_date', flat=True)

for q_date in q_date_list:
    print "processing trading data for date %s " % q_date
    twse_daily_trading_job(q_date)


last_processed_date=Twse_Summary_Price_Processed.objects.get_last_processed()
q_date_list=Trading_Date.objects.filter(trading_date__gt=last_processed_date).values_list('trading_date', flat=True)


for q_date in q_date_list:
    print "processing price data for date %s " % q_date
    twse_daily_summary_price_job(q_date)

download_twse_various_index_job()

twse_manage_warrant_info_job()
twse_manage_warrant_info_use_other_url_job()
twse_trading_post_processing_job()
#twse_black_scholes_calc_job()
#
twse_index_avg_calc_job()
twse_stock_price_volume_avg_calc_job()
twse_stock_calc_stoch_osci_adx_job()

twse_various_index_avg_calc_job()
twse_various_index_calc_stoch_osci_adx_job()
