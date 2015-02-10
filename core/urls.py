from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^twse_daily_trading_download/(?P<qdate>\d+)/$', 'core.views.twse_daily_trading_download', name='twse_daily_trading_download'),
    url(r'^twse_daily_trading_download/$', 'core.views.twse_daily_trading_download2', name='twse_daily_trading_download2'),
    url(r'^twse_daily_trading_process/(?P<qdate>\d+)/$', 'core.views.twse_daily_trading_process', name='twse_daily_trading_process'),
    url(r'^twse_daily_trading_process/$', 'core.views.twse_daily_trading_process2', name='twse_daily_trading_process2'),
    url(r'^twse_download_stock_info/$', 'core.views.twse_download_stock_info', name='twse_download_stock_info'),
    url(r'^twse_process_stock_info/$', 'core.views.twse_process_stock_info', name='twse_process_stock_info'),
    url(r'^twse_download_warrant_info/$', 'core.views.twse_download_warrant_info', name='twse_download_warrant_info'),
    url(r'^twse_process_warrant_info/$', 'core.views.twse_process_warrant_info', name='twse_process_warrant_info'),
    url(r'^twse_bulk_download_warrant_info/$', 'core.views.twse_bulk_download_warrant_info', name='twse_bulk_download_warrant_info'),
    url(r'^twse_bulk_process_warrant_info/$', 'core.views.twse_bulk_process_warrant_info', name='twse_bulk_process_warrant_info'),
    url(r'^twse_daily_summary_price_download/(?P<qdate>\d+)/$', 'core.views.twse_daily_summary_price_download', name='twse_daily_summary_price_download'),
    url(r'^twse_daily_summary_price_download/$', 'core.views.twse_daily_summary_price_download2', name='twse_daily_summary_price_download2'),
    url(r'^twse_daily_summary_price_process/(?P<qdate>\d+)/$', 'core.views.twse_daily_summary_price_process', name='twse_daily_summary_price_process'),
    url(r'^twse_daily_summary_price_process/$', 'core.views.twse_daily_summary_price_process2', name='twse_daily_summary_price_process2'),
    url(r'^test_black_scholes/(?P<warrant_symbol>\w+)/date/(?P<qdate>\d+)/$', 'core.views.test_black_scholes', name='test_black_scholes'),
    )
