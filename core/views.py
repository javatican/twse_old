import datetime
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
import json

from core.cron import twse_daily_trading_download_job, \
    twse_daily_trading_process_job, twse_download_stock_info_job, \
    twse_process_stock_info_job, twse_bulk_download_warrant_info_job, \
    twse_bulk_process_warrant_info_job, twse_download_warrant_info_job, \
    twse_process_warrant_info_job, twse_daily_summary_price_download_job, \
    twse_daily_price_process_job, twse_daily_index_process_job, \
    twse_daily_tri_index_process_job, twse_daily_summary_process_job, \
    twse_daily_updown_process_job, test_black_scholes_job
from warrant_app.utils import dateutil


def test_black_scholes(request, warrant_symbol, qdate):
    try:
        #format yyyymmdd
        q_date=dateutil.convertToDate(qdate)
        test_black_scholes_job(warrant_symbol,q_date)
        message = _('Job execution finished2!')
    except:
        message = _('Job execution failed2!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json') 

def twse_daily_trading_download(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        twse_daily_trading_download_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_trading_download2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_trading_download(request,q_date)

def twse_daily_trading_process(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        twse_daily_trading_process_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_trading_process2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_trading_process(request,q_date)
 
def twse_daily_summary_price_download(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        twse_daily_summary_price_download_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_summary_price_download2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_summary_price_download(request,q_date)

def twse_daily_summary_price_process(request, qdate):
    try:
        if qdate:
            #format yyyymmdd
            q_date=dateutil.convertToDate(qdate)
        else: 
            q_date=datetime.datetime.now()
        twse_daily_price_process_job(q_date)
        twse_daily_index_process_job(q_date)
        twse_daily_tri_index_process_job(q_date)
        twse_daily_summary_process_job(q_date)
        twse_daily_updown_process_job(q_date)
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_daily_summary_price_process2(request):
    q_date=datetime.datetime.now().strftime("%Y%m%d")
    return twse_daily_summary_price_process(request,q_date)

def twse_download_stock_info(request):
    try:        
        twse_download_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')
def twse_process_stock_info(request):
    try:        
        twse_process_stock_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')


 

def twse_download_warrant_info(request):
    try:        
        twse_download_warrant_info_job()
        message = _('Job execution finished!')
    except:
        message = _('Job execution failed!')
    data = {}
    data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

def twse_process_warrant_info(request):
    try:        
        twse_process_warrant_info_job()
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

