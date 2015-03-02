import datetime
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
import json

from core2.cron import gt_bulk_download_warrant_info_job, \
    gt_bulk_process_warrant_info_job, gt_manage_stock_info_job, \
    gt_manage_warrant_info_job, gt_manage_warrant_info_use_other_url_job, \
    gt_daily_trading_job, gt_daily_summary_price_job
from warrant_app.utils import dateutil


def gt_daily_trading(request, qdate_str):
    try:
        if qdate_str:
            # format yyyymmdd
            qdate = dateutil.convertToDate(qdate_str)
        else: 
            qdate = datetime.datetime.now().date()
        gt_daily_trading_job(qdate)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_trading2(request):
    qdate_str = datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_trading(request, qdate_str)
 
def gt_daily_summary_price(request, qdate_str):
    try:
        if qdate_str:
            # format yyyymmdd
            qdate = dateutil.convertToDate(qdate_str)
        else: 
            qdate = datetime.datetime.now().date()
        gt_daily_summary_price_job(qdate)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_summary_price2(request):
    qdate_str = datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_summary_price(request, qdate_str)

def gt_manage_stock_info(request):
    try:        
        gt_manage_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_manage_warrant_info(request):
    try:        
        gt_manage_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_manage_warrant_info_use_other_url(request):
    try:        
        gt_manage_warrant_info_use_other_url_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_bulk_download_warrant_info(request):
    try:        
        gt_bulk_download_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_bulk_process_warrant_info(request):
    try:        
        gt_bulk_process_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

