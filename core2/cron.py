# coding=utf8
from bs4 import BeautifulSoup
import codecs
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import logging
import os
import re
from requests import Session
import requests
import sys
import time

from core.cron import download_stock_info, process_stock_info, \
    download_warrant_info, process_warrant_info, bulk_download_warrant_info, \
    bulk_process_warrant_info
from core.models import Cron_Job_Log
from core2.models import Gt_Trading_Downloaded, Gt_Trading, \
    Gt_Warrant_Item, Gt_Stock_Item, get_stock_item_type, get_warrant_exercise_style, \
    get_warrant_classification, select_warrant_type_code, Gt_Summary_Price_Downloaded, \
    Gt_Market_Summary_Type, Gt_Market_Summary, \
    Gt_Market_Highlight, Gt_Trading_Warrant
from warrant_app.settings import TWSE_DOWNLOAD_1, TWSE_DOWNLOAD_2, \
    TWSE_DOWNLOAD_3, TWSE_DOWNLOAD_4, TWSE_DOWNLOAD_5, TWSE_TRADING_DOWNLOAD_URL, \
    TWSE_PRICE_DOWNLOAD_URL, TWSE_DOWNLOAD_0, TWSE_DOWNLOAD_A, \
    TWSE_DOWNLOAD_B, TWSE_DOWNLOAD_C, TWSE_DOWNLOAD_D, GT_DOWNLOAD_2, \
    GT_DOWNLOAD_4, GT_DOWNLOAD_3, TPEX_TRADING_DOWNLOAD_URL, GT_DOWNLOAD_1, \
    TPEX_STATS_DOWNLOAD_URL, GT_DOWNLOAD_C, TPEX_HIGHLIGHT_DOWNLOAD_URL, \
    GT_DOWNLOAD_D, TPEX_PRICE_DOWNLOAD_URL, GT_DOWNLOAD_0
from warrant_app.utils import dateutil
from warrant_app.utils.black_scholes import option_price_implied_volatility_call_black_scholes_newton, \
    option_price_implied_volatility_put_black_scholes_newton, \
    option_price_delta_call_black_scholes, option_price_delta_put_black_scholes, \
    option_price_call_black_scholes, option_price_put_black_scholes
from warrant_app.utils.dateutil import roc_year_to_western, western_to_roc_year
from warrant_app.utils.logutil import log_message
from warrant_app.utils.stringutil import is_float
from warrant_app.utils.warrant_util import check_if_warrant_item


# from django.utils.translation import ugettext as _
logger = logging.getLogger('warrant_app.cronjob')

def gt_download_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_download_stock_info_job.__name__ 
    try:    
        items = Gt_Stock_Item.objects.data_not_yet_download()
        if download_stock_info(items, is_gt=True):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        for item in items:
            item.save()
        job.save()
        
def gt_process_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_process_stock_info_job.__name__ 
    items = []
    try:    
        items = Gt_Stock_Item.objects.need_to_process()
        for item in items:            
            filename = "%s/stock_info_%s" % (GT_DOWNLOAD_2, item.symbol)
            try:
                with codecs.open(filename, 'r', encoding="utf8") as fd:
                    if process_stock_info(item, fd): 
                        item.data_ok = True
                    else: 
                        item.parsing_error = True
            except IOError:
                item.data_downloaded = False
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise 
    finally:
        for item in items:
            item.save()
        job.save()

def gt_download_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_download_warrant_info_job.__name__ 

    try:    
        items = Gt_Warrant_Item.objects.data_not_yet_download()
        if download_warrant_info(items,is_gt=True):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed() 
        raise 
    finally:        
        for item in items:
            item.save()
        job.save()

def gt_process_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_process_warrant_info_job.__name__ 
    items = []
    try:    
        items = Gt_Warrant_Item.objects.need_to_process()
        for item in items:            
            filename = "%s/warrant_info_%s" % (GT_DOWNLOAD_4, item.symbol)
            try:
                with codecs.open(filename, 'r', encoding="utf8") as fd:                            
                    if process_warrant_info(item, fd):                     
                        item.data_ok = True
                    else:
                        item.parsing_error = True
            except IOError:
                item.data_downloaded = False
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        for item in items:
            item.save()
        job.save()

def gt_bulk_download_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_bulk_download_warrant_info_job.__name__ 
    try:
        stocks = Gt_Trading.objects.stocks_has_hedge_trade()
        for stock in stocks:
            filename = "%s/bulk_warrant_info_%s" % (GT_DOWNLOAD_3, stock['stock_symbol__symbol'])
            if os.path.isfile(filename):
                stock['data_downloaded'] = True
            else:
                stock['data_downloaded'] = False
        if bulk_download_warrant_info(stocks, is_gt=True):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        job.save()
        
def gt_bulk_process_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_bulk_process_warrant_info_job.__name__ 
    try:    
        stocks = Gt_Trading.objects.stocks_has_hedge_trade(type_code=False)
        stocks_processed = Gt_Warrant_Item.objects.stocks_has_warrants()
        
        for stock in stocks:
            if stock['stock_symbol__symbol'] in stocks_processed: continue
            filename = "%s/bulk_warrant_info_%s" % (GT_DOWNLOAD_3, stock['stock_symbol__symbol'])
            if os.path.isfile(filename):
                bulk_process_warrant_info(stock['stock_symbol__symbol'], is_gt=True)
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        job.save()
        
def gt_daily_trading_download_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_trading_download_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y/%m/%d")
        # check if downloaded
        try:
            ob = Gt_Trading_Downloaded.objects.by_trading_date(q_date)
            # downloaded previously(but may contain no data yet), and then check if data is available
            if(not ob.data_available):
                # data is not available, so retry download
                if _get_day_trading(qdate):
                    ob.data_available = True
                    ob.save()
                else:
                    job.error_message = 'Trading data are not yet available'
                    raise Exception(job.error_message)
        except Gt_Trading_Downloaded.DoesNotExist:
            # not previously downloaded
            if _get_day_trading(qdate):
                Gt_Trading_Downloaded.objects.create(trading_date=q_date)
            else:
                # data is not yet available
                Gt_Trading_Downloaded.objects.create(trading_date=q_date, data_available=False)
                job.error_message = 'Trading data are not yet available'
                raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
#             
def _get_day_trading(qdate):
    datarow_count = 0 
    # used to flag if data is available (if count >0)
    serviceUrl = TPEX_TRADING_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_roc = western_to_roc_year(qdate)
    parameters = {'d': qdate_roc, 'l':'zh-tw', 's':'0,asc,0', 't':'D'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/trading_%s" % (GT_DOWNLOAD_1, re.sub('/', '', qdate))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)
    filename2 = "%s_datarow" % filename
    with codecs.open(filename2, 'wb', encoding="utf8") as fd2:
        with codecs.open(filename, 'r', encoding="utf8") as fd3:
            soup = BeautifulSoup(fd3, 'lxml')
            tbody_element = soup.find('tbody')
            for tag in tbody_element.find_all('tr'):
                datarow_count += 1
                print >> fd2, unicode(tag)
    if(datarow_count == 0):
        logger.warning("No trading data available yet")
        os.remove(filename)
        os.remove(filename2)
        return False
    else:
        return True
    
def gt_daily_trading_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_trading_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Gt_Trading_Downloaded.objects.available_and_unprocessed(q_date)
            if _process_day_trading(qdate):
                ob.is_processed = True
                ob.save()
        except Gt_Trading_Downloaded.DoesNotExist:
            job.error_message = 'Data (%s) are not yet downloaded or have been processed' % qdate
            raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
    
def _process_day_trading(qdate):
    filename = "%s/trading_%s_datarow" % (GT_DOWNLOAD_1, qdate)
    trading_items_to_save = []
    trading_warrant_items_to_save = []
    record_stored = 0
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s trading records in file" % (len(rows)-1))
        for row in rows:
            i = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    if check_if_warrant_item(dt_data):
                        warrant_item, created = Gt_Warrant_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Gt_Trading_Warrant()
                        trading_warrant_items_to_save.append(dt_item)
                        dt_item.warrant_symbol = warrant_item
                    else:                  
                        stock_item, created = Gt_Stock_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Gt_Trading()
                        trading_items_to_save.append(dt_item)
                        dt_item.stock_symbol = stock_item
                    dt_item.trading_date = dateutil.convertToDate(qdate)
                elif i == 2:
                    dt_item.fi_buy = int(dt_data.replace(',', ''))                    
                elif i == 3:
                    dt_item.fi_sell = int(dt_data.replace(',', ''))  
                    dt_item.fi_diff = dt_item.fi_buy - dt_item.fi_sell                        
                elif i == 5:
                    dt_item.sit_buy = int(dt_data.replace(',', ''))                    
                elif i == 6:
                    dt_item.sit_sell = int(dt_data.replace(',', ''))  
                    dt_item.sit_diff = dt_item.sit_buy - dt_item.sit_sell          
                elif i == 9:
                    dt_item.proprietary_buy = int(dt_data.replace(',', ''))                    
                elif i == 10:
                    dt_item.proprietary_sell = int(dt_data.replace(',', ''))  
                    dt_item.proprietary_diff = dt_item.proprietary_buy - dt_item.proprietary_sell                              
                elif i == 12:
                    dt_item.hedge_buy = int(dt_data.replace(',', ''))            
                elif i == 13:
                    dt_item.hedge_sell = int(dt_data.replace(',', ''))   
                    dt_item.hedge_diff = dt_item.hedge_buy - dt_item.hedge_sell             
                elif i == 15:
                    dt_item.total_diff = int(dt_data.replace(',', ''))
                
                i += 1
            if i>0: record_stored += 1
    count1 = len(trading_warrant_items_to_save)
    count2 = len(trading_items_to_save) 
    if  count1 > 0: Gt_Trading_Warrant.objects.bulk_create(trading_warrant_items_to_save)
    if  count2 > 0: Gt_Trading.objects.bulk_create(trading_items_to_save)
    logger.info("There are %s trading records stored ( %s warrant items, %s stock items)" % (record_stored, count1, count2))
    return True

def gt_daily_summary_price_download_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_summary_price_download_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y/%m/%d")
        # check if downloaded
        try:
            ob = Gt_Summary_Price_Downloaded.objects.by_trading_date(q_date)
            # downloaded previously, and then check if data is available
            if(not ob.data_available):
                # data is not available, so retry download
                if _get_market_summary_and_day_price(qdate):
                    ob.data_available = True
                    ob.save()
                else:
                    job.error_message = 'Price/summary data are not yet available'
                    raise Exception(job.error_message)
        except Gt_Summary_Price_Downloaded.DoesNotExist:
            # not previously downloaded
            if _get_market_summary_and_day_price(qdate):
                Gt_Summary_Price_Downloaded.objects.create(trading_date=q_date)
            else:
                # data is not yet available
                Gt_Summary_Price_Downloaded.objects.create(trading_date=q_date, data_available=False)
                job.error_message = 'Price/summary data are not yet available'
                raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
#
def _get_market_summary_and_day_price(qdate):
    # below are used to flag if data is available (if count >0)
    datarow_count = 0 
#get tpex market stats
    serviceUrl = TPEX_STATS_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_roc = western_to_roc_year(qdate)
    parameters = {'d': qdate_roc, 'l':'zh-tw'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename1c = "%s/tpex_stats_%s" % (GT_DOWNLOAD_C, re.sub('/', '', qdate))
    with codecs.open(filename1c, 'wb', encoding="utf8") as fd:
        print >> fd, httpResponse.text   
#get tpex market highlight
    serviceUrl = TPEX_HIGHLIGHT_DOWNLOAD_URL
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename1d = "%s/tpex_highlight_%s" % (GT_DOWNLOAD_D, re.sub('/', '', qdate))
    with codecs.open(filename1d, 'wb', encoding="utf8") as fd:
        print >> fd, httpResponse.text   
        
#get tpex daily quotes
    serviceUrl = TPEX_PRICE_DOWNLOAD_URL
    parameters = {'d': qdate_roc, 'l':'zh-tw', 's':'0,asc,0'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)   
    filename = "%s/price_%s" % (GT_DOWNLOAD_0, re.sub('/', '', qdate))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)   
            
    filename2 = "%s_datarow" % filename
    with codecs.open(filename, 'r', encoding="utf8") as fd3:
        soup = BeautifulSoup(fd3, 'lxml')
        tbody_element = soup.find('tbody')
        with codecs.open(filename2, 'wb', encoding="utf8") as fd2:
            for tag in tbody_element.find_all('tr'):
                datarow_count += 1
                print >> fd2, unicode(tag)
        logger.info("%s price records downloaded" % datarow_count)
    if(datarow_count <= 1):
        os.remove(filename)
        os.remove(filename1c)
        os.remove(filename1d)
        os.remove(filename2)
        return False
    else:
        return True

_allow_partially_run = False

def gt_daily_price_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_price_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # for any specific date, the gt_daily_trading_process_job need to be run first
        # so check if above mentioned job has been done
        if not Gt_Trading_Downloaded.objects.check_processed(q_date):
            job.error_message = "Trading data need to be processed before price data"
            raise Exception(job.error_message)
        else:
            try:
                # check if downloaded and available
                ob = Gt_Summary_Price_Downloaded.objects.available_and_price_unprocessed(q_date)
                if _process_daily_price(qdate):
                    ob.price_processed = True
                    ob.save()
            except Gt_Summary_Price_Downloaded.DoesNotExist:               
                job.error_message = 'Data (%s) are not yet downloaded or have been processed' % qdate
                if not _allow_partially_run: raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
def check_up_or_down(data):
    if data[0] == u'＋': 
        return float(data[1:])
    elif data[0] == u'－': 
        return -1 * float(data[1:])
    else: 
        return 0
    
def _process_daily_price(qdate):
    filename = "%s/price_%s_datarow" % (GT_DOWNLOAD_0, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s price records in file" % len(rows))
        record_stored = 0
        stock_count=0
        warrant_count=0
        for row in rows:
            i = 0
            dt_item = None
            symbol = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:                                        
                    symbol = dt_data
                elif i == 2:
                    # if there is no closing price --> no need to store this price record.
                    # therefore delay creation of model objects until we are sure there is closing price.
                    temp_data=dt_data.replace(',', '')
                    if is_float(temp_data): 
                        # create model objects
                        if check_if_warrant_item(symbol):
                            warrant_item, created = Gt_Warrant_Item.objects.get_or_create(symbol=symbol)
                            dt_item, created = Gt_Trading_Warrant.objects.get_or_create(warrant_symbol=warrant_item, trading_date=dateutil.convertToDate(qdate))
                            warrant_count+=1
                        else:                  
                            stock_item, created = Gt_Stock_Item.objects.get_or_create(symbol=symbol)
                            dt_item, created = Gt_Trading.objects.get_or_create(stock_symbol=stock_item, trading_date=dateutil.convertToDate(qdate))                  
                            stock_count+=1
                        
                        dt_item.closing_price = float(temp_data)
                    else:
                        break               
                elif i == 3:  
                    dt_item.price_change = check_up_or_down(dt_data.replace(',', ''))  
                elif i == 4:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.opening_price = float(temp_data)     
                elif i == 5:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.highest_price = float(temp_data)                
                elif i == 6:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.lowest_price = float(temp_data)                           
                elif i == 7:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.average_price = float(temp_data)        
                elif i == 8:
                    dt_item.trade_volume = int(dt_data.replace(',', ''))          
                elif i == 9:
                    dt_item.trade_value = int(dt_data.replace(',', ''))
                elif i == 10:
                    dt_item.trade_transaction = int(dt_data.replace(',', ''))      
                elif i == 11:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_bid_price = float(temp_data)  
                elif i == 12:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_ask_price = float(temp_data)           
                i += 1
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s price records stored ( %s warrant items, %s stock items)" % (record_stored, warrant_count, stock_count))
    return True

def gt_market_summary_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_market_summary_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Gt_Summary_Price_Downloaded.objects.available_and_summary_unprocessed(q_date)
            if _process_market_summary(qdate):
                ob.summary_processed = True
                ob.save()
        except Gt_Summary_Price_Downloaded.DoesNotExist:
            job.error_message = 'Data (%s) are not yet downloaded or have been processed' % qdate
            if not _allow_partially_run: raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
def _process_market_summary(qdate):
    filename = "%s/tpex_stats_%s" % (GT_DOWNLOAD_C, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        tbody_element = soup.find('tbody')
        rows = tbody_element.find_all('tr')
        logger.info("There are %s summary records in file." % len(rows))
        record_stored = 0
        for row in rows:
            i = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    # create model objects
                    type_item, created = Gt_Market_Summary_Type.objects.get_or_create(name=dt_data)
                    dt_item = Gt_Market_Summary()
                    dt_item.summary_type=type_item
                    dt_item.trading_date=dateutil.convertToDate(qdate)  
                elif i == 1: 
                    dt_item.trade_value = float(dt_data.replace(',', '')) 
                elif i == 2:
                    dt_item.trade_volume = float(dt_data.replace(',', '')) 
                elif i == 3:
                    dt_item.trade_transaction = float(dt_data.replace(',', ''))                      
                i += 1
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s summary records stored." % record_stored)
    return True

def gt_market_highlight_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_market_highlight_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Gt_Summary_Price_Downloaded.objects.available_and_highlight_unprocessed(q_date)
            if _process_market_highlight(qdate):
                ob.highlight_processed = True
                ob.save()
        except Gt_Summary_Price_Downloaded.DoesNotExist:
            job.error_message = 'Data (%s) are not yet downloaded or have been processed' % qdate
            if not _allow_partially_run: raise Exception(job.error_message)  
        transaction.commit()
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
def _process_market_highlight(qdate):
    filename = "%s/tpex_highlight_%s" % (GT_DOWNLOAD_D, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        tbody_element = soup.find('tbody')
        rows = tbody_element.find_all('tr')
        logger.info("There are %s market highlight records in file." % len(rows))
        #
        dt_item = Gt_Market_Highlight()
        dt_item.trading_date=dateutil.convertToDate(qdate)  
        # process rows[0]
        cells = rows[0].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.listed_companies = dt_data 
        # process rows[1]
        cells = rows[1].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.capitals = int(dt_data)*1000000
        # process rows[2]
        cells = rows[2].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.market_capitalization = int(dt_data)*1000000
        # process rows[3]
        cells = rows[3].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.trade_value = int(dt_data)*1000000
        # process rows[4]
        cells = rows[4].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.trade_volume = int(dt_data)*1000
        # process rows[5]
        cells = rows[5].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.closing_index = float(dt_data)
        dt_data = cells[3].string.strip().replace(',', '')
        dt_item.change = float(dt_data)
        dt_item.change_in_percentage = dt_item.change/dt_item.closing_index
        # process rows[6]
        cells = rows[6].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.stock_up = dt_data
        dt_data = cells[3].string.strip().replace(',', '')
        dt_item.stock_up_limit = dt_data 
        # process rows[7]
        cells = rows[7].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.stock_down = dt_data
        dt_data = cells[3].string.strip().replace(',', '')
        dt_item.stock_down_limit = dt_data 
        # process rows[8]
        cells = rows[8].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.stock_unchange = dt_data
        dt_data = cells[3].string.strip().replace(',', '')
        dt_item.stock_unmatch = dt_data
        dt_item.save()
    return True
