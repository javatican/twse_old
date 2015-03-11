# coding: utf-8
from core.cron import twse_daily_trading_job, twse_daily_summary_price_job, \
    twse_manage_warrant_info_job, twse_trading_post_processing_job, \
    twse_black_scholes_calc_job, twse_manage_warrant_info_use_other_url_job
from warrant_app.utils.dateutil import string_to_date


q_date_list=[string_to_date('2015/03/03'),
             string_to_date('2015/03/04'),
             string_to_date('2015/03/05'),
             string_to_date('2015/03/06'),
             string_to_date('2015/03/09'),
             string_to_date('2015/03/10'),
             ]

for  q_date in q_date_list:
    twse_daily_trading_job(q_date)
    twse_daily_summary_price_job(q_date)
#
twse_manage_warrant_info_job()
twse_manage_warrant_info_use_other_url_job()
twse_trading_post_processing_job()
twse_black_scholes_calc_job()