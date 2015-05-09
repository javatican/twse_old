from core.cron import strategy_by_stochastic_pop_drop_job, \
    strategy_by_stochastic_cross_over_job
from core.models import Trading_Date

# generate historic strategy data since 20150101
start_date='2015-01-01'
q_date_list=Trading_Date.objects.filter(trading_date__gte=start_date).values_list('trading_date', flat=True).order_by('trading_date')
for q_date in q_date_list:
    print "processing trading data for date %s " % q_date
    q_date_str=q_date.strftime('%Y%m%d')
    strategy_by_stochastic_pop_drop_job(target_date=q_date_str, 
                                        notify=False, 
                                        gen_plot=False, 
                                        store_selection=True)
    strategy_by_stochastic_cross_over_job(target_date=q_date_str, 
                                        notify=False, 
                                        gen_plot=False, 
                                        store_selection=True)