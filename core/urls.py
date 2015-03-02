from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^twse_manage_stock_info/$', 'core.views.twse_manage_stock_info', name='twse_manage_stock_info'),
    url(r'^twse_manage_warrant_info/$', 'core.views.twse_manage_warrant_info', name='twse_manage_warrant_info'),
    url(r'^twse_manage_warrant_info_use_other_url/$', 'core.views.twse_manage_warrant_info_use_other_url', name='twse_manage_warrant_info_use_other_url'),
    url(r'^twse_bulk_download_warrant_info/$', 'core.views.twse_bulk_download_warrant_info', name='twse_bulk_download_warrant_info'),
    url(r'^twse_bulk_process_warrant_info/$', 'core.views.twse_bulk_process_warrant_info', name='twse_bulk_process_warrant_info'),
    url(r'^twse_daily_trading/(?P<qdate_str>\d+)/$', 'core.views.twse_daily_trading', name='twse_daily_trading'),
    url(r'^twse_daily_trading/$', 'core.views.twse_daily_trading2', name='twse_daily_trading2'),
    url(r'^twse_daily_summary_price/(?P<qdate_str>\d+)/$', 'core.views.twse_daily_summary_price', name='twse_daily_summary_price'),
    url(r'^twse_daily_summary_price/$', 'core.views.twse_daily_summary_price2', name='twse_daily_summary_price2'),
    url(r'^test_black_scholes/(?P<warrant_symbol>\w+)/date/(?P<qdate_str>\d+)/$', 'core.views.test_black_scholes', name='test_black_scholes'),
    )
