import datetime
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
import json

from core.cron import twse_bulk_download_warrant_info_job, \
    twse_bulk_process_warrant_info_job, test_black_scholes_job, \
    twse_manage_stock_info_job, twse_manage_warrant_info_job, \
    twse_manage_warrant_info_use_other_url_job, twse_daily_trading_job, \
    twse_daily_summary_price_job
from warrant_app.utils import dateutil


def test_black_scholes(request, warrant_symbol, qdate_str):
    try:
        #format yyyymmdd
        qdate=dateutil.convertToDate(qdate_str)
        test_black_scholes_job(warrant_symbol,qdate)
        message = _('Job execution finished2!')
    except:
        message = _('Job execution failed2!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json') 

def twse_daily_trading(request, qdate_str):
    try:
        if qdate_str:
            #format yyyymmdd
            qdate=dateutil.convertToDate(qdate_str)
        else: 
            qdate=datetime.datetime.now().date()
        twse_daily_trading_job(qdate)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_trading2(request):
    qdate_str=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_trading(request,qdate_str)
 
def twse_daily_summary_price(request, qdate_str):
    try:
        if qdate_str:
            #format yyyymmdd
            qdate=dateutil.convertToDate(qdate_str)
        else: 
            qdate=datetime.datetime.now().date()
        twse_daily_summary_price_job(qdate)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_summary_price2(request):
    qdate_str=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_summary_price(request,qdate_str)

def twse_manage_stock_info(request):
    try:        
        twse_manage_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_manage_warrant_info(request):
    try:        
        twse_manage_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_manage_warrant_info_use_other_url(request):
    try:        
        twse_manage_warrant_info_use_other_url_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_bulk_download_warrant_info(request):
    try:        
        twse_bulk_download_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_bulk_process_warrant_info(request):
    try:        
        twse_bulk_process_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

