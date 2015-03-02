# coding=utf8
from bs4 import BeautifulSoup
import codecs
import datetime
from django.db import transaction
import logging
import os
import re
import requests
import sys

from core.cron import bulk_download_warrant_info, \
    bulk_process_warrant_info, manage_warrant_info_2, manage_stock_info, \
    manage_warrant_info
from core.models import Cron_Job_Log, Trading_Date
from core2.models import Gt_Trading, Gt_Warrant_Item, Gt_Stock_Item, \
    Gt_Market_Summary_Type, Gt_Market_Summary, \
    Gt_Market_Highlight, Gt_Trading_Warrant, Gt_Trading_Processed, \
    Gt_Summary_Price_Processed
from warrant_app.settings import GT_DOWNLOAD_3, TPEX_TRADING_DOWNLOAD_URL, GT_DOWNLOAD_1, \
    TPEX_STATS_DOWNLOAD_URL, GT_DOWNLOAD_C, TPEX_HIGHLIGHT_DOWNLOAD_URL, \
    GT_DOWNLOAD_D, TPEX_PRICE_DOWNLOAD_URL, GT_DOWNLOAD_0
from warrant_app.utils import dateutil
from warrant_app.utils.dateutil import western_to_roc_year, roc_year_to_western, \
    is_third_wednesday
from warrant_app.utils.logutil import log_message
from warrant_app.utils.stringutil import is_float
from warrant_app.utils.warrant_util import check_if_warrant_item


# from django.utils.translation import ugettext as _
logger = logging.getLogger('warrant_app.cronjob')
# below function is called once to exact twse trading date since 2014/1
def _download_trading_date():
    serviceUrl = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_index/st41_print.php'
    year = 104
    for month in range(2, 3):
        year_month = "%s/%s" % (year, month)
        parameters = {'d': year_month, 'l':'zh-tw', 's':'0,asc,0'}
        try:        
            httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
            httpResponse.encoding = "utf-8"
        except requests.HTTPError, e:
            result = e.read()
            raise Exception(result)
        
        soup = BeautifulSoup(httpResponse.text, 'lxml')
        tbody_element = soup.find('tbody')
        tr_list = tbody_element.find_all('tr')
        j = 0
        for row in tr_list:
            i = 0
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    tdate = Trading_Date()
                    tdate.trading_date = roc_year_to_western(dt_data)
                    # date.weekday(): Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
                    tdate.day_of_week = tdate.trading_date.weekday() + 1
                    if j == 0:
                        # first trading date of the month
                        tdate.first_trading_day_of_month = True
                    if j == len(tr_list) - 1:
                        tdate.last_trading_day_of_month = True
                    if is_third_wednesday(tdate.trading_date):
                        tdate.is_future_delivery_day = True
                    tdate.save() 
                    break
                i += 1

            j += 1

def gt_manage_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_manage_stock_info_job.__name__ 
    try:    
        items = Gt_Stock_Item.objects.data_not_ok()
        if manage_stock_info(items, is_gt=True):
            job.success()
        else:
            job.error_message = 'process runs with interruption'
            raise Exception(job.error_message)
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        for item in items:
            item.save()
        job.save()
        
def gt_manage_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_manage_warrant_info_job.__name__ 

    try:    
        items = Gt_Warrant_Item.objects.data_not_ok()
        if manage_warrant_info(items, is_gt=True):
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

def gt_manage_warrant_info_use_other_url_job():
# different url , for 'finished' warrants 
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_manage_warrant_info_use_other_url_job.__name__ 
    try:    
        items = Gt_Warrant_Item.objects.data_not_ok() 
        if manage_warrant_info_2(items, is_gt=True):
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
def gt_daily_trading_job(qdate=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_trading_job.__name__  
    try:
        if not qdate: 
            qdate = datetime.datetime.now().date()
        qdate_str = qdate.strftime("%Y/%m/%d")
        # check if processed
        if Gt_Trading_Processed.objects.check_processed(qdate):
            job.error_message = 'Trading data for date %s have already been processed.' % qdate_str
            raise Exception(job.error_message)
        if _get_day_trading(qdate_str):
            #call processing here
            if _process_day_trading(qdate_str):
                Gt_Trading_Processed.objects.create(trading_date=qdate)
            else:
                job.error_message = 'Trading data for date %s have problems when processing.' % qdate_str
                raise Exception(job.error_message)
        else:
            job.error_message = 'Trading data for date %s have problems when downloading.' % qdate_str
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
def _get_day_trading(qdate_str):
    logger.info("downloading gt trading data...")
    datarow_count = 0 
    # used to flag if data is available (if count >0)
    serviceUrl = TPEX_TRADING_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_str_roc = western_to_roc_year(qdate_str)
    parameters = {'d': qdate_str_roc, 
                  'l':'zh-tw', 
                  's':'0,asc,0', 
                  't':'D'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/trading_%s" % (GT_DOWNLOAD_1, re.sub('/', '', qdate_str))
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
        logger.info("There are %s trading records in file" % datarow_count)
        return True
  
def _process_day_trading(qdate_str):
    logger.info("processing gt trading data...")
    filename = "%s/trading_%s_datarow" % (GT_DOWNLOAD_1, re.sub('/', '', qdate_str))
    trading_items_to_save = []
    trading_warrant_items_to_save = []
    record_stored = 0
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("Reading %s trading records in file" % len(rows))
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
                    dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')
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
            if i > 0: record_stored += 1
    count1 = len(trading_warrant_items_to_save)
    count2 = len(trading_items_to_save) 
    if  count1 > 0: Gt_Trading_Warrant.objects.bulk_create(trading_warrant_items_to_save)
    if  count2 > 0: Gt_Trading.objects.bulk_create(trading_items_to_save)
    logger.info("There are %s trading records processed ( %s warrant items, %s stock items)" % (record_stored, count1, count2))
    return True

def gt_daily_summary_price_job(qdate=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = gt_daily_summary_price_job.__name__  
    try:
        if not qdate: 
            qdate = datetime.datetime.now().date()
        qdate_str = qdate.strftime("%Y/%m/%d")
        # check if processed
        if Gt_Summary_Price_Processed.objects.check_processed(qdate):
            job.error_message = 'Summary and price data for date %s have already been processed.' % qdate_str
            raise Exception(job.error_message)
        # for any specific date, the gt_daily_trading_job need to be run first
        # so check if above mentioned job has been done
        if not Gt_Trading_Processed.objects.check_processed(qdate):
            job.error_message = "Trading data need to be processed before summary/price data"
            raise Exception(job.error_message)
        else:
            if _get_summary_and_price(qdate_str):
            # processing 
                if (_process_price(qdate_str) and 
                    _process_market_summary(qdate_str) and 
                    _process_market_highlight(qdate_str)):
                    Gt_Summary_Price_Processed.objects.create(trading_date=qdate)
                else:
                    job.error_message = 'Summary and price data for date %s have problems when processing.' % qdate_str
                    raise Exception(job.error_message)
            else:
                job.error_message = 'Summary and price data for date %s have problems when downloading.' % qdate_str
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
def _get_summary_and_price(qdate_str):
    logger.info("downloading gt summary and price data...")
    # below are used to flag if data is available (if count >0)
    datarow_count_1c = 0 
    datarow_count_1d = 0 
    datarow_count = 0
    # get tpex market stats
    serviceUrl = TPEX_STATS_DOWNLOAD_URL
    # transform qdate to roc year
    qdate_str_roc = western_to_roc_year(qdate_str)
    parameters = {'d': qdate_str_roc, 
                  'l':'zh-tw'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename1c = "%s/tpex_stats_%s" % (GT_DOWNLOAD_C, re.sub('/', '', qdate_str))
    with codecs.open(filename1c, 'wb', encoding="utf8") as fd:
        soup = BeautifulSoup(httpResponse.text , 'lxml')
        tbody_element = soup.find('tbody')
        # check if data is available for market stats
        if tbody_element == None: 
            logger.warning("No tbody tag in market stats")
            return False
        for tag in tbody_element.find_all('tr'):
            datarow_count_1c += 1
            print >> fd, unicode(tag)
        logger.info("%s market stats records downloaded" % datarow_count_1c)
    # get tpex market highlight
    serviceUrl = TPEX_HIGHLIGHT_DOWNLOAD_URL
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename1d = "%s/tpex_highlight_%s" % (GT_DOWNLOAD_D, re.sub('/', '', qdate_str))
    with codecs.open(filename1d, 'wb', encoding="utf8") as fd:
        soup = BeautifulSoup(httpResponse.text , 'lxml')
        tbody_element = soup.find('tbody')
        # check if data is available for market highlight
        if tbody_element == None: 
            logger.warning("No tbody tag in market highlight")
            return False
        for tag in tbody_element.find_all('tr'):
            datarow_count_1d += 1
            print >> fd, unicode(tag)
        logger.info("%s market highlight records downloaded" % datarow_count_1d)
    # get tpex daily prices
    serviceUrl = TPEX_PRICE_DOWNLOAD_URL
    parameters = {'d': qdate_str_roc, 
                  'l':'zh-tw', 
                  's':'0,asc,0'}
    try:        
        httpResponse = requests.get(serviceUrl, params=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)   
    filename = "%s/price_%s" % (GT_DOWNLOAD_0, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)   
            
    filename2 = "%s_datarow" % filename
    with codecs.open(filename, 'r', encoding="utf8") as fd3:
        soup = BeautifulSoup(fd3, 'lxml')
        tbody_element = soup.find('tbody')
        if tbody_element == None: 
            logger.warning("No tbody tag in price records")
            return False
        with codecs.open(filename2, 'wb', encoding="utf8") as fd2:
            for tag in tbody_element.find_all('tr'):
                datarow_count += 1
                print >> fd2, unicode(tag)
        logger.info("%s price records downloaded" % datarow_count)
        #
    if(datarow_count_1c == 0 or datarow_count_1d == 0 or datarow_count <= 1):
        logger.warning("Summary or price data are not available yet")
        os.remove(filename)
        os.remove(filename1c)
        os.remove(filename1d)
        os.remove(filename2)
        return False
    else:
        logger.info("Finish downloading summary and price records")
        return True
        
def _process_price(qdate_str):
    logger.info("processing gt price data...")
    filename = "%s/price_%s_datarow" % (GT_DOWNLOAD_0, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s price records in file" % len(rows))
        record_stored = 0
        stock_count = 0
        warrant_count = 0
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
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        # create model objects
                        if check_if_warrant_item(symbol):
                            warrant_item, created = Gt_Warrant_Item.objects.get_or_create(symbol=symbol)
                            dt_item, created = Gt_Trading_Warrant.objects.get_or_create(warrant_symbol=warrant_item, trading_date=dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d'))
                            warrant_count += 1
                        else:                  
                            stock_item, created = Gt_Stock_Item.objects.get_or_create(symbol=symbol)
                            dt_item, created = Gt_Trading.objects.get_or_create(stock_symbol=stock_item, trading_date=dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d'))                  
                            stock_count += 1
                        
                        dt_item.closing_price = float(temp_data)
                    else:
                        break               
                elif i == 3:  
                    dt_item.price_change = _check_up_or_down(dt_data.replace(',', ''))  
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
        logger.info("There are %s price records processed ( %s warrant items, %s stock items)" % (record_stored, warrant_count, stock_count))
    return True
        
def _process_market_summary(qdate_str):
    logger.info("processing gt market summary data...")
    filename = "%s/tpex_stats_%s" % (GT_DOWNLOAD_C, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        # tbody_element = soup.find('tbody')
        rows = soup.find_all('tr')
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
                    dt_item.summary_type = type_item
                    dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')  
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
        logger.info("There are %s summary records processed." % record_stored)
    return True

def _process_market_highlight(qdate_str):
    logger.info("processing gt market highlight data...")
    filename = "%s/tpex_highlight_%s" % (GT_DOWNLOAD_D, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        # tbody_element = soup.find('tbody')
        rows = soup.find_all('tr')
        logger.info("There are %s market highlight records in file." % len(rows))
        #
        dt_item = Gt_Market_Highlight()
        dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')  
        # process rows[0]
        cells = rows[0].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.listed_companies = dt_data 
        # process rows[1]
        cells = rows[1].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.capitals = int(dt_data) * 1000000
        # process rows[2]
        cells = rows[2].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.market_capitalization = int(dt_data) * 1000000
        # process rows[3]
        cells = rows[3].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.trade_value = int(dt_data) * 1000000
        # process rows[4]
        cells = rows[4].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.trade_volume = int(dt_data) * 1000
        # process rows[5]
        cells = rows[5].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.closing_index = float(dt_data)
        dt_data = cells[3].string.strip().replace(',', '')
        dt_item.change = float(dt_data)
        dt_item.change_in_percentage = (dt_item.change / dt_item.closing_index) * 100.0
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
    logger.info("gt market highlight data processed...")
    return True

def _check_up_or_down(data):
    if data[0] == u'+': 
        return float(data[1:])
    elif data[0] == u'-': 
        return -1 * float(data[1:])
    else: 
        return 0

