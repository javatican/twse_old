from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^gt_daily_trading_download/(?P<qdate>\d+)/$', 'core2.views.gt_daily_trading_download', name='gt_daily_trading_download'),
    url(r'^gt_daily_trading_download/$', 'core2.views.gt_daily_trading_download2', name='gt_daily_trading_download2'),
    url(r'^gt_daily_trading_process/(?P<qdate>\d+)/$', 'core2.views.gt_daily_trading_process', name='gt_daily_trading_process'),
    url(r'^gt_daily_trading_process/$', 'core2.views.gt_daily_trading_process2', name='gt_daily_trading_process2'),
    url(r'^gt_download_stock_info/$', 'core2.views.gt_download_stock_info', name='gt_download_stock_info'),
    url(r'^gt_process_stock_info/$', 'core2.views.gt_process_stock_info', name='gt_process_stock_info'),
    url(r'^gt_download_warrant_info/$', 'core2.views.gt_download_warrant_info', name='gt_download_warrant_info'),
    url(r'^gt_process_warrant_info/$', 'core2.views.gt_process_warrant_info', name='gt_process_warrant_info'),
    url(r'^gt_bulk_download_warrant_info/$', 'core2.views.gt_bulk_download_warrant_info', name='gt_bulk_download_warrant_info'),
    url(r'^gt_bulk_process_warrant_info/$', 'core2.views.gt_bulk_process_warrant_info', name='gt_bulk_process_warrant_info'),
    url(r'^gt_daily_summary_price_download/(?P<qdate>\d+)/$', 'core2.views.gt_daily_summary_price_download', name='gt_daily_summary_price_download'),
    url(r'^gt_daily_summary_price_download/$', 'core2.views.gt_daily_summary_price_download2', name='gt_daily_summary_price_download2'),
    url(r'^gt_daily_summary_price_process/(?P<qdate>\d+)/$', 'core2.views.gt_daily_summary_price_process', name='gt_daily_summary_price_process'),
    url(r'^gt_daily_summary_price_process/$', 'core2.views.gt_daily_summary_price_process2', name='gt_daily_summary_price_process2'),
    )
