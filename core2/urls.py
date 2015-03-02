from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^gt_daily_trading/(?P<qdate_str>\d+)/$', 'core2.views.gt_daily_trading', name='gt_daily_trading'),
    url(r'^gt_daily_trading/$', 'core2.views.gt_daily_trading2', name='gt_daily_trading2'),
    url(r'^gt_manage_stock_info/$', 'core2.views.gt_manage_stock_info', name='gt_manage_stock_info'),
    url(r'^gt_manage_warrant_info/$', 'core2.views.gt_manage_warrant_info', name='gt_manage_warrant_info'),
    url(r'^gt_manage_warrant_info_use_other_url/$', 'core2.views.gt_manage_warrant_info_use_other_url', name='gt_manage_warrant_info_use_other_url'),
    url(r'^gt_bulk_download_warrant_info/$', 'core2.views.gt_bulk_download_warrant_info', name='gt_bulk_download_warrant_info'),
    url(r'^gt_bulk_process_warrant_info/$', 'core2.views.gt_bulk_process_warrant_info', name='gt_bulk_process_warrant_info'),
    url(r'^gt_daily_summary_price/(?P<qdate_str>\d+)/$', 'core2.views.gt_daily_summary_price', name='gt_daily_summary_price'),
    url(r'^gt_daily_summary_price/$', 'core2.views.gt_daily_summary_price2', name='gt_daily_summary_price2'),
    )
