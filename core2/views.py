import datetime
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
import json
from core2.cron import gt_daily_trading_download_job, \
    gt_daily_trading_process_job, gt_download_stock_info_job, \
    gt_process_stock_info_job, gt_bulk_download_warrant_info_job, \
    gt_bulk_process_warrant_info_job, gt_download_warrant_info_job, \
    gt_process_warrant_info_job, gt_daily_summary_price_download_job, \
    gt_daily_price_process_job, gt_market_summary_process_job, \
    gt_market_highlight_process_job

from warrant_app.utils import dateutil


def gt_daily_trading_download(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        gt_daily_trading_download_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_trading_download2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_trading_download(request,q_date)

def gt_daily_trading_process(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        gt_daily_trading_process_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_trading_process2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_trading_process(request,q_date)
 
def gt_daily_summary_price_download(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        gt_daily_summary_price_download_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_summary_price_download2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_summary_price_download(request,q_date)

def gt_daily_summary_price_process(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        gt_daily_price_process_job(q_date)
        gt_market_summary_process_job(q_date)
        gt_market_highlight_process_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_daily_summary_price_process2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return gt_daily_summary_price_process(request,q_date)

def gt_download_stock_info(request):
    try:        
        gt_download_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')
def gt_process_stock_info(request):
    try:        
        gt_process_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_download_warrant_info(request):
    try:        
        gt_download_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def gt_process_warrant_info(request):
    try:        
        gt_process_warrant_info_job()
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

