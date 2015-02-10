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

from core.models import Cron_Job_Log, Twse_Trading_Downloaded, Twse_Trading, \
    Warrant_Item, Stock_Item, get_stock_item_type, get_warrant_exercise_style, \
    get_warrant_classification, select_warrant_type_code, Twse_Summary_Price_Downloaded, \
    Index_Item, Index_Change_Info, Market_Summary_Type, Market_Summary, \
    Stock_Up_Down_Stats, Twse_Trading_Warrant
from warrant_app.settings import TWSE_DOWNLOAD_1, TWSE_DOWNLOAD_2, \
    TWSE_DOWNLOAD_3, TWSE_DOWNLOAD_4, TWSE_DOWNLOAD_5, TWSE_TRADING_DOWNLOAD_URL, \
    TWSE_PRICE_DOWNLOAD_URL, TWSE_DOWNLOAD_0, TWSE_DOWNLOAD_A, \
    TWSE_DOWNLOAD_B, TWSE_DOWNLOAD_C, TWSE_DOWNLOAD_D
from warrant_app.utils import dateutil
from warrant_app.utils.black_scholes import option_price_implied_volatility_call_black_scholes_newton, \
    option_price_implied_volatility_put_black_scholes_newton, \
    option_price_delta_call_black_scholes, option_price_delta_put_black_scholes, \
    option_price_call_black_scholes, option_price_put_black_scholes
from warrant_app.utils.dateutil import roc_year_to_western, western_to_roc_year
from warrant_app.utils.logutil import log_message
from warrant_app.utils.stringutil import is_float


# from django.utils.translation import ugettext as _
logger = logging.getLogger('warrant_app.cronjob')

# Below code is one time use, so comment out.
 
# def migration_job():
#     items = Twse_Trading.objects.filter(warrant_symbol__isnull=False).select_related('warrant_symbol')
#     for item in items:
#         create_trading_warrant(item)
# 
#         
# def create_trading_warrant(from_item):
#         instance = Twse_Trading_Warrant()
#         for field in instance._meta.get_all_field_names(): 
#             # make sure id is not copied...
#             if field == 'id': continue
#             if getattr(from_item, field, None):
#                 setattr(instance, field, getattr(from_item, field))  
#         instance.save()
#         return instance
# # below code uses bulk creation, should be more efficient than above code
# # not tested yet
# def batch_create_trading_warrant_job():
#     items = Twse_Trading.objects.filter(warrant_symbol__isnull=False).select_related('warrant_symbol')
#     items_to_create = []
#     for item in items:
#         instance = Twse_Trading_Warrant()
#         for field in instance._meta.get_all_field_names(): 
#             # make sure id is not copied...
#             if field == 'id': continue
#             if getattr(item, field, None):
#                 setattr(instance, field, getattr(item, field)) 
#         items_to_create.append(instance)
#     Twse_Trading_Warrant.objects.bulk_create(items_to_create)
#     
    
    
# def _check_warrant_symbol():
#     items = Warrant_Item.objects.all()
#     for item in items:        
#         if not _check_if_warrant_item(item.symbol):
#             print "correcting warrant item:  %s" % item.symbol
#             stock_item=Stock_Item.objects.create(symbol=item.symbol)
#             #
#             for trading_record in Twse_Trading.objects.by_warrant_symbol(item):
#                 print "update dealer trading record : %s" % trading_record.id
#                 trading_record.warrant_symbol=None
#                 trading_record.stock_symbol=stock_item
#                 trading_record.save()
#             item.delete()
#             

def _check_if_warrant_item(symbol):
    # use the rule defined since 2010/5/17 ( see http://www.tej.com.tw/webtej/doc/warnt.htm )
    if len(symbol) != 6: 
        return False
    elif symbol[0] == '0' and symbol[1] in ['3', '4', '5', '6', '7', '8']:
        return True
    elif symbol[0] == '7' and symbol[1] in ['0', '1', '2', '3']:
        return True
    else:
        return False
                
def twse_download_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_download_stock_info_job.__name__ 
    try:    
        items = Stock_Item.objects.data_not_yet_download()
        if _download_stock_info(items):
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
                
def _download_stock_info(items): 
    originUrl = 'http://mops.twse.com.tw/mops/web/t05st03'
    ajaxUrl = 'http://mops.twse.com.tw/mops/web/ajax_quickpgm' 
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
        gen = (item for item in items if item.data_downloaded == False)
        for item in gen:
            parameters = {'encodeURIComponent': 1,
                      'firstin':'true',
                      'step':4,
                      'checkbtn':1,
                      'queryName':'co_id',
                      'TYPEK2':'',
                      'code1':'',
                      'keyword4':item.symbol, }
        
            httpResponse = session.post(
                                        url=ajaxUrl,
                                        data=parameters,
                                        headers={
                                                 'Referer': originUrl, })
# default response encoding is ISO8859-1
            httpResponse.encoding = "utf-8"
            # print httpResponse.text
            filename = "%s/stock_info_%s" % (TWSE_DOWNLOAD_2, item.symbol)
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text           
            item.data_downloaded = True
            time.sleep(5)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(180)
        return _download_stock_info(items)
    except:
        raise
        
        
def twse_process_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_process_stock_info_job.__name__ 
    items = []
    try:    
        items = Stock_Item.objects.need_to_process()
        for item in items:            
            filename = "%s/stock_info_%s" % (TWSE_DOWNLOAD_2, item.symbol)
            try:
                with codecs.open(filename, 'r', encoding="utf8") as fd:
                    if _process_stock_info(item, fd): 
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
        
def _process_stock_info(item, fd): 
    
    soup = BeautifulSoup(fd, 'lxml')
    table_element = soup.find(id='zoom') 
    if not table_element: 
        logger.warning("No table tag in file %s" % item.symbol)
        return False
    tr_element = table_element.find('tr', class_='even')
    if not tr_element: 
        logger.warning("No table row tag in file %s" % item.symbol)
        return False
    i = 0
    for td_element in tr_element.find_all('td', recursive=False):
        anchor_element = td_element.find('a')
        stock_data = anchor_element.string.strip()
        # print stock_data
        if i == 0:
            if stock_data != item.symbol: 
                logger.warning("Stock symbol is not matched in file for %s" % item.symbol)
                return False
        elif i == 1:
            item.short_name = stock_data                   
        elif i == 2:
            item.name = stock_data             
        elif i == 3:
            item.type_code = get_stock_item_type(stock_data)
        elif i == 4:
            item.market_category = stock_data
        elif i == 5:
            item.notes = stock_data                 
        else:
            break;
        i += 1
    if i == 0: 
        logger.warning("No table data tag in file %s" % item.symbol)
        return False
    return True


def twse_download_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_download_warrant_info_job.__name__ 

    try:    
        items = Warrant_Item.objects.data_not_yet_download()
        if _download_warrant_info(items):
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
        
def _download_warrant_info(items): 
    originUrl = 'http://mops.twse.com.tw/mops/web/t90sbfa01'
    ajaxUrl = 'http://mops.twse.com.tw/mops/web/ajax_t90sbfa01' 
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
        gen = (item for item in items if item.data_downloaded == False)
        for item in gen:
            type_code = select_warrant_type_code(item.symbol)
            parameters = {'encodeURIComponent': 1,
                          'step':1,
                          'ver':'1.9',
                          'TYPEK':'',
                          'market':type_code,
                          'wrn_class':'all',
                          'stock_no':'',
                          'wrn_no':item.symbol,
                          'co_id':'all',
                          'wrn_type':'all',
                          'left_month':'all',
                          'return_rate':'all',
                          'price_down':'',
                          'price_up':'',
                          'price_inout':'all',
                          'newprice_down':'',
                          'newprice_up':'',
                          'fin_down':'',
                          'fin_up':'',
                          'sort':1, }
        
            httpResponse = session.post(
                                        url=ajaxUrl,
                                        data=parameters,
                                        headers={
                                                 'Referer': originUrl, })
# default response encoding is ISO8859-1
            httpResponse.encoding = "utf-8"
            # print httpResponse.text
            filename = "%s/warrant_info_%s" % (TWSE_DOWNLOAD_4, item.symbol)
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text           
            item.data_downloaded = True
            time.sleep(5)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(180)
        return _download_warrant_info(items)
    except:
        raise
    
def twse_process_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_process_warrant_info_job.__name__ 
    items = []
    try:    
        items = Warrant_Item.objects.need_to_process()
        for item in items:            
            filename = "%s/warrant_info_%s" % (TWSE_DOWNLOAD_4, item.symbol)
            try:
                with codecs.open(filename, 'r', encoding="utf8") as fd:                            
                    if _process_warrant_info(item, fd):                     
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
        
def _process_warrant_info(item, fd): 
    soup = BeautifulSoup(fd, 'lxml')
    tr_element = soup.find('tr', class_='even')
    if not tr_element: 
        logger.warning("No table row tag in file %s" % item.symbol)
        return False
    i = 0
    for td_element in tr_element.find_all('td', recursive=False):
        warrant_data = td_element.string.strip()
        # print warrant_data
        if i == 0:
            item.type_code = select_warrant_type_code(item.symbol)
        elif i == 1:
            item.name = warrant_data                   
        elif i == 2:
            item.exercise_style = get_warrant_exercise_style(warrant_data)            
        elif i == 3:
            item.classification = get_warrant_classification(warrant_data)
        elif i == 4:
            item.issuer = warrant_data     
        elif i == 7:                    
            item.listed_date = roc_year_to_western(warrant_data)   
        elif i == 8:                    
            item.last_trading_date = roc_year_to_western(warrant_data)   
        elif i == 9:                    
            item.expiration_date = roc_year_to_western(warrant_data)
        elif i == 11:
            item.issued_volume = int(warrant_data.replace(',', ''))   
        elif i == 12:            
            stock_item, created = Stock_Item.objects.get_or_create(symbol=warrant_data)
            item.target_stock = stock_item
            item.target_symbol = stock_item.symbol                  
        elif i == 15:
            item.exercise_ratio = int(warrant_data.replace(',', ''))
        elif i == 16:
            item.strike_price = float(warrant_data.replace(',', '')) 
        i += 1
    if i == 0: 
        logger.warning("No table data tag in file %s" % item.symbol)
        return False
    return True

def twse_bulk_download_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_bulk_download_warrant_info_job.__name__ 
    try:    
        stocks = Twse_Trading.objects.stocks_has_hedge_trade()
        for stock in stocks:
            filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, stock['stock_symbol__symbol'])
            if os.path.isfile(filename):
                stock['data_downloaded'] = True
            else:
                stock['data_downloaded'] = False
        if _bulk_download_warrant_info(stocks):
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
                
def _bulk_download_warrant_info(items): 
    originUrl = 'http://mops.twse.com.tw/mops/web/t90sbfa01'
    ajaxUrl = 'http://mops.twse.com.tw/mops/web/ajax_t90sbfa01' 
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
        gen = (item for item in items if item['data_downloaded'] == False)
        for item in gen:
            parameters = {'encodeURIComponent': 1,
                          'step':1,
                          'ver':'1.9',
                          'TYPEK':'',
                          'market':item['stock_symbol__type_code'],
                          'wrn_class':'all',
                          'stock_no':item['stock_symbol__symbol'],
                          'wrn_no':'',
                          'co_id':'all',
                          'wrn_type':'all',
                          'left_month':'all',
                          'return_rate':'all',
                          'price_down':'',
                          'price_up':'',
                          'price_inout':'all',
                          'newprice_down':'',
                          'newprice_up':'',
                          'fin_down':'',
                          'fin_up':'',
                          'sort':1, }
        
            httpResponse = session.post(
                                        url=ajaxUrl,
                                        data=parameters,
                                        headers={
                                                 'Referer': originUrl, })
# default response encoding is ISO8859-1
            httpResponse.encoding = "utf-8"
            # print httpResponse.text
            filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, item['stock_symbol__symbol'])
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text           
            item['data_downloaded'] = True
            time.sleep(5)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(180)
        return _bulk_download_warrant_info(items)
    except:
        raise
        
        
def twse_bulk_process_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_bulk_process_warrant_info_job.__name__ 
    try:    
        stocks = Twse_Trading.objects.stocks_has_hedge_trade(type_code=False)
        stocks_processed = Warrant_Item.objects.stocks_has_warrants()
        
        for stock in stocks:
            if stock['stock_symbol__symbol'] in stocks_processed: continue
            filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, stock['stock_symbol__symbol'])
            if os.path.isfile(filename):
                _bulk_process_warrant_info(stock['stock_symbol__symbol'])
        job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        job.save()
        
def has_css_class(css_class):
    return css_class == 'even' or css_class == "odd"

def _bulk_process_warrant_info(stock_symbol): 
    stock_item = Stock_Item.objects.get_by_symbol(stock_symbol)
    filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, stock_symbol)
    with codecs.open(filename, 'r', encoding="utf8") as fd:              
        soup = BeautifulSoup(fd, 'lxml')
        tr_element_list = soup.find_all('tr', class_=has_css_class)
        if len(tr_element_list) == 0: 
            logger.warning("No warrant data in %s" % filename)
            return
        i = 0
        i_processed = 0
        for tr_element in tr_element_list:
            # python doesn't have breaking outer loop syntax, so need to put the inner loop code into a separate function
            result = _process_td_elements(tr_element, stock_item)
            if result:  
                i_processed += 1              
            i += 1
        logger.warning("Total %s tr elements" % i)
        logger.warning("Total %s warrant data processed" % i_processed)
        return True
    
def _process_td_elements(tr_element, stock_item):
    i = 0
    warrant_item = None
    for td_element in tr_element.find_all('td', recursive=False):
        warrant_data = td_element.string.strip()
        # print warrant_data
        if i == 0:
            warrant_item, created = Warrant_Item.objects.get_or_create(symbol=warrant_data)
            if warrant_item.data_ok: 
                logger.warning("Warrant data (%s) exists!" % warrant_item.symbol)
                return False
            warrant_item.target_stock = stock_item
            warrant_item.target_symbol = stock_item.symbol
            warrant_item.type_code = select_warrant_type_code(warrant_item.symbol)
        elif i == 1:
            warrant_item.name = warrant_data                   
        elif i == 2:
            warrant_item.exercise_style = get_warrant_exercise_style(warrant_data)            
        elif i == 3:
            warrant_item.classification = get_warrant_classification(warrant_data)
        elif i == 4:
            warrant_item.issuer = warrant_data     
        elif i == 7:                    
            warrant_item.listed_date = roc_year_to_western(warrant_data)   
        elif i == 8:                    
            warrant_item.last_trading_date = roc_year_to_western(warrant_data)   
        elif i == 9:                    
            warrant_item.expiration_date = roc_year_to_western(warrant_data)
        elif i == 11:
            warrant_item.issued_volume = int(warrant_data.replace(',', ''))            
        elif i == 15:
            warrant_item.exercise_ratio = int(warrant_data.replace(',', ''))
        elif i == 16:
            warrant_item.strike_price = float(warrant_data.replace(',', ''))     
        i += 1
    if i == 0: 
        logger.warning("no td in the tr element")
        return False
    # query and update warrant item
    warrant_item.data_ok = True
    warrant_item.data_downloaded = True
    warrant_item.save()
    return True

def twse_update_etf_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_update_etf_stock_info_job.__name__ 
    try:    
        originUrl = 'http://www.twse.com.tw/ETF/ETFlist.php'
        httpResponse = requests.get(originUrl)
        # print httpResponse.encoding
        httpResponse.encoding = "big5"
        filename = "%s/ETF_info" % TWSE_DOWNLOAD_5
        with codecs.open(filename, 'wb', encoding="utf8") as fd:
            print >> fd, httpResponse.text           
        with codecs.open(filename, 'r', encoding="utf8") as fd: 
            # print "Processing %s" % filename            
            data_list = []
            soup = BeautifulSoup(fd, 'lxml')
            for table_element in soup.find_all('table', class_='board_prod'):
                for tr_element in table_element.find_all('tr', recursive=False):
                    data = {}
                    i = 0
                    for td_element in tr_element.find_all('td', recursive=False):
                        td_data = td_element.string.strip()
                        if i == 0:
                            data['name'] = td_data
                        elif i == 1:
                            data['short_name'] = td_data
                        elif i == 2:
                            data['symbol'] = td_data
                        elif i == 3:
                            data['etf_target'] = td_data
                        i += 1
                    data_list.append(data)
                    # print data
            for data_item in data_list:
                if 'symbol' not in data_item.keys(): continue
                symbol = data_item['symbol']
                try:
                    stock = Stock_Item.objects.get_by_symbol(symbol)
                    if stock.data_ok: continue
                    stock.is_etf = True
                    stock.name = data_item['name']
                    stock.short_name = data_item['short_name']
                    stock.etf_target = data_item['etf_target']
                    stock.data_ok = True
                    stock.data_download = True
                    stock.parsing_error = False
                    stock.save()
                    logger.info("ETF stock info %s is updated" % symbol.encode(encoding='utf-8'))
                except Stock_Item.DoesNotExist:
                    logger.warning("ETF symbol %s not found" % symbol.encode(encoding='utf-8'))
            job.success()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed() 
        raise 
    finally:
        job.save()
        
def twse_daily_trading_download_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_trading_download_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y/%m/%d")
        # check if downloaded
        try:
            ob = Twse_Trading_Downloaded.objects.by_trading_date(q_date)
            # downloaded previously(but may contain no data yet), and then check if data is available
            if(not ob.data_available):
                # data is not available, so retry download
                if _get_day_trading(qdate):
                    ob.data_available = True
                    ob.save()
                else:
                    job.error_message = 'Trading data are not yet available'
                    raise Exception(job.error_message)
        except Twse_Trading_Downloaded.DoesNotExist:
            # not previously downloaded
            if _get_day_trading(qdate):
                Twse_Trading_Downloaded.objects.create(trading_date=q_date)
            else:
                # data is not yet available
                Twse_Trading_Downloaded.objects.create(trading_date=q_date, data_available=False)
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
    serviceUrl = TWSE_TRADING_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_roc = western_to_roc_year(qdate)
    parameters = {'input_date': qdate_roc, 'select2':'ALL', 'sorting':'by_stkno', 'login_btn':''}
    try:        
        httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
        httpResponse.encoding = "big5"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/trading_%s" % (TWSE_DOWNLOAD_1, re.sub('/', '', qdate))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)
    filename2 = "%s_datarow" % filename
    with codecs.open(filename2, 'wb', encoding="utf8") as fd2:
        with codecs.open(filename, 'r', encoding="utf8") as fd3:
            soup = BeautifulSoup(fd3, 'lxml')
            for tag in soup.find_all('tr', class_='basic2'):
                datarow_count += 1
                print >> fd2, unicode(tag)
    if(datarow_count == 0):
        logger.warning("No trading data available yet")
        os.remove(filename)
        os.remove(filename2)
        return False
    else:
        return True
    
def twse_daily_trading_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_trading_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Twse_Trading_Downloaded.objects.available_and_unprocessed(q_date)
            if _process_day_trading(qdate):
                ob.is_processed = True
                ob.save()
        except Twse_Trading_Downloaded.DoesNotExist:
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
    filename = "%s/trading_%s_datarow" % (TWSE_DOWNLOAD_1, qdate)
    trading_items_to_save = []
    trading_warrant_items_to_save = []
    record_stored = 0
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr', class_='basic2')
        logger.info("There are %s trading records in file" % (len(rows)-1))
        for row in rows[1:]:
            i = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    if _check_if_warrant_item(dt_data):
                        warrant_item, created = Warrant_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Twse_Trading_Warrant()
                        trading_warrant_items_to_save.append(dt_item)
                        dt_item.warrant_symbol = warrant_item
                    else:                  
                        stock_item, created = Stock_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Twse_Trading()
                        trading_items_to_save.append(dt_item)
                        dt_item.stock_symbol = stock_item
                    dt_item.trading_date = dateutil.convertToDate(qdate)
                elif i == 2:
                    dt_item.fi_buy = int(dt_data.replace(',', ''))                    
                elif i == 3:
                    dt_item.fi_sell = int(dt_data.replace(',', ''))  
                    dt_item.fi_diff = dt_item.fi_buy - dt_item.fi_sell                        
                elif i == 4:
                    dt_item.sit_buy = int(dt_data.replace(',', ''))                    
                elif i == 5:
                    dt_item.sit_sell = int(dt_data.replace(',', ''))  
                    dt_item.sit_diff = dt_item.sit_buy - dt_item.sit_sell          
                elif i == 6:
                    dt_item.proprietary_buy = int(dt_data.replace(',', ''))                    
                elif i == 7:
                    dt_item.proprietary_sell = int(dt_data.replace(',', ''))  
                    dt_item.proprietary_diff = dt_item.proprietary_buy - dt_item.proprietary_sell                              
                elif i == 8:
                    dt_item.hedge_buy = int(dt_data.replace(',', ''))            
                elif i == 9:
                    dt_item.hedge_sell = int(dt_data.replace(',', ''))   
                    dt_item.hedge_diff = dt_item.hedge_buy - dt_item.hedge_sell             
                elif i == 10:
                    dt_item.total_diff = int(dt_data.replace(',', ''))
                
                i += 1
            if i>0: record_stored += 1
    count1 = len(trading_warrant_items_to_save)
    count2 = len(trading_items_to_save) 
    if  count1 > 0: Twse_Trading_Warrant.objects.bulk_create(trading_warrant_items_to_save)
    if  count2 > 0: Twse_Trading.objects.bulk_create(trading_items_to_save)
    logger.info("There are %s trading records stored ( %s warrant items, %s stock items)" % (record_stored, count1, count2))
    return True

def twse_daily_summary_price_download_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_summary_price_download_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y/%m/%d")
        # check if downloaded
        try:
            ob = Twse_Summary_Price_Downloaded.objects.by_trading_date(q_date)
            # downloaded previously, and then check if data is available
            if(not ob.data_available):
                # data is not available, so retry download
                if _get_market_summary_and_day_price(qdate):
                    ob.data_available = True
                    ob.save()
                else:
                    job.error_message = 'Price/summary data are not yet available'
                    raise Exception(job.error_message)
        except Twse_Summary_Price_Downloaded.DoesNotExist:
            # not previously downloaded
            if _get_market_summary_and_day_price(qdate):
                Twse_Summary_Price_Downloaded.objects.create(trading_date=q_date)
            else:
                # data is not yet available
                Twse_Summary_Price_Downloaded.objects.create(trading_date=q_date, data_available=False)
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
    datarow_count_1a = 0 
    datarow_count_1b = 0 
    datarow_count_1c = 0 
    datarow_count_1d = 0 
    datarow_count2 = 0 
#
    serviceUrl = TWSE_PRICE_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_roc = western_to_roc_year(qdate)
    parameters = {'qdate': qdate_roc, 'selectType':'ALL', 'download':''}
    try:        
        httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/price_%s" % (TWSE_DOWNLOAD_0, re.sub('/', '', qdate))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)            
    filename1a = "%s/twse_index_%s" % (TWSE_DOWNLOAD_A, re.sub('/', '', qdate))
    filename1b = "%s/twse_total_return_index_%s" % (TWSE_DOWNLOAD_B, re.sub('/', '', qdate))
    filename1c = "%s/market_summary_%s" % (TWSE_DOWNLOAD_C, re.sub('/', '', qdate))
    filename1d = "%s/market_up_down_stats_%s" % (TWSE_DOWNLOAD_D, re.sub('/', '', qdate))
    filename2 = "%s_datarow" % filename
    with codecs.open(filename, 'r', encoding="utf8") as fd3:
        soup = BeautifulSoup(fd3, 'lxml')
        table_elements = soup.find_all('table')
        # should have 2 table tags, 1st contains summary data, 2nd contains price data
        if len(table_elements) == 0: 
            logger.warning("No table tag in file")
            return False
        tbody_elements = table_elements[0].find_all('tbody')
        if len(tbody_elements) == 0: 
            logger.warning("No tbody tag(summary data) in file")
            return False
        # write index
        with codecs.open(filename1a, 'wb', encoding="utf8") as fd1: 
            for tag in tbody_elements[0].find_all('tr'):           
                datarow_count_1a += 1
                print >> fd1, unicode(tag)
        logger.info("%s index records downloaded" % datarow_count_1a)
        with codecs.open(filename1b, 'wb', encoding="utf8") as fd1: 
            for tag in tbody_elements[1].find_all('tr'):           
                datarow_count_1b += 1
                print >> fd1, unicode(tag)
        logger.info("%s tri index records downloaded" % datarow_count_1b)
        with codecs.open(filename1c, 'wb', encoding="utf8") as fd1: 
            for tag in tbody_elements[2].find_all('tr'):           
                datarow_count_1c += 1
                print >> fd1, unicode(tag)
        logger.info("%s market summary records downloaded" % datarow_count_1c)
        with codecs.open(filename1d, 'wb', encoding="utf8") as fd1: 
            for tag in tbody_elements[3].find_all('tr'):           
                datarow_count_1d += 1
                print >> fd1, unicode(tag)
        logger.info("%s market up/down records downloaded" % datarow_count_1d)
        with codecs.open(filename2, 'wb', encoding="utf8") as fd2:
            for tag in table_elements[1].find_all('tr'):
                datarow_count2 += 1
                print >> fd2, unicode(tag)
        logger.info("%s price records downloaded" % datarow_count2)
    if(datarow_count_1a == 0 or datarow_count_1b == 0 or datarow_count_1c == 0 or datarow_count_1d == 0 or datarow_count2 == 0):
        os.remove(filename)
        os.remove(filename1a)
        os.remove(filename1b)
        os.remove(filename1c)
        os.remove(filename1d)
        os.remove(filename2)
        return False
    else:
        return True

_allow_partially_run = False

def twse_daily_price_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_price_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # for any specific date, the twse_daily_trading_process_job need to be run first
        # so check if above mentioned job has been done
        if not Twse_Trading_Downloaded.objects.check_processed(q_date):
            job.error_message = "Trading data need to be processed before price data"
            raise Exception(job.error_message)
        else:
            try:
                # check if downloaded and available
                ob = Twse_Summary_Price_Downloaded.objects.available_and_price_unprocessed(q_date)
                if _process_day_price(qdate):
                    ob.price_processed = True
                    ob.save()
            except Twse_Summary_Price_Downloaded.DoesNotExist:               
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
    if data == u'＋': return 1
    elif data == u'－': return -1
    else: return 0
    
def _process_day_price(qdate):
    filename = "%s/price_%s_datarow" % (TWSE_DOWNLOAD_0, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s price records in file" % (len(rows) - 2))
        record_stored = 0
        stock_count=0
        warrant_count=0
        #skip two rows
        for row in rows[2:]:
            i = 0
            up_or_down = 0
            dt_item = None
            symbol = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:                                        
                    symbol = dt_data
                elif i == 2:
                    # if there is no trade volume --> no need to store this price record.
                    # therefore delay creation of model objects until we are sure there is volume data.
                    trade_volume = int(dt_data.replace(',', '')) 
                    if trade_volume == 0 : break
                    # create model objects
                    if _check_if_warrant_item(symbol):
                        warrant_item, created = Warrant_Item.objects.get_or_create(symbol=symbol)
                        dt_item, created = Twse_Trading_Warrant.objects.get_or_create(warrant_symbol=warrant_item, trading_date=dateutil.convertToDate(qdate))
                        warrant_count+=1
                    else:                  
                        stock_item, created = Stock_Item.objects.get_or_create(symbol=symbol)
                        dt_item, created = Twse_Trading.objects.get_or_create(stock_symbol=stock_item, trading_date=dateutil.convertToDate(qdate))                  
                        stock_count+=1
                    dt_item.trade_volume = trade_volume                 
                elif i == 3:
                    dt_item.trade_transaction = int(dt_data.replace(',', ''))              
                elif i == 4:
                    dt_item.trade_value = int(dt_data.replace(',', ''))                    
                elif i == 5:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.opening_price = float(temp_data)          
                elif i == 6:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.highest_price = float(temp_data)                
                elif i == 7:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.lowest_price = float(temp_data)                           
                elif i == 8:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.closing_price = float(temp_data)        
                elif i == 9:
                    up_or_down = check_up_or_down(dt_data) 
                elif i == 10:
                    dt_item.price_change = float(dt_data.replace(',', '')) * up_or_down
                elif i == 11:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_bid_price = float(temp_data)  
                elif i == 12:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_bid_volume = float(temp_data) 
                elif i == 13:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_ask_price = float(temp_data) 
                elif i == 14:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.last_best_ask_volume = float(temp_data)              
                i += 1
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s price records stored ( %s warrant items, %s stock items)" % (record_stored, warrant_count, stock_count))
    return True


def twse_daily_index_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_index_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Twse_Summary_Price_Downloaded.objects.available_and_index_unprocessed(q_date)
            if _process_day_index(qdate):
                ob.index_processed = True
                ob.save()
        except Twse_Summary_Price_Downloaded.DoesNotExist:
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
        
def _process_day_index(qdate):
    filename = "%s/twse_index_%s" % (TWSE_DOWNLOAD_A, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s index records in file." % len(rows))
        record_stored = 0
        for row in rows:
            i = 0
            up_or_down = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    # create model objects
                    index_item, created = Index_Item.objects.get_or_create(name=dt_data)
                    dt_item = Index_Change_Info()
                    dt_item.twse_index=index_item
                    dt_item.trading_date=dateutil.convertToDate(qdate)             
                elif i == 1: 
                    dt_item.closing_index = float(dt_data.replace(',', ''))                
                elif i == 2:
                    up_or_down = check_up_or_down(dt_data) 
                elif i == 3:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.change = float(temp_data) * up_or_down
                elif i == 4:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.change_in_percentage = float(temp_data)                             
                i += 1
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s index records stored." % record_stored)
    return True

def twse_daily_tri_index_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_tri_index_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Twse_Summary_Price_Downloaded.objects.available_and_tri_index_unprocessed(q_date)
            if _process_day_tri_index(qdate):
                ob.tri_index_processed = True
                ob.save()
        except Twse_Summary_Price_Downloaded.DoesNotExist:
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
        
def _process_day_tri_index(qdate):
    filename = "%s/twse_total_return_index_%s" % (TWSE_DOWNLOAD_B, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s tri index records in file." % len(rows))
        record_stored = 0
        for row in rows:
            i = 0
            up_or_down = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    # create model objects
                    index_item, created = Index_Item.objects.get_or_create(name=dt_data, is_total_return_index=True)
                    dt_item = Index_Change_Info()
                    dt_item.twse_index=index_item
                    dt_item.trading_date=dateutil.convertToDate(qdate)  
                elif i == 1:
                    dt_item.closing_index = float(dt_data.replace(',', ''))                         
                elif i == 2:
                    up_or_down = check_up_or_down(dt_data) 
                elif i == 3:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.change = float(temp_data) * up_or_down
                elif i == 4:
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.change_in_percentage = float(temp_data)                             
                i += 1
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s tri index records stored." % record_stored)
    return True

def twse_daily_summary_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_summary_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Twse_Summary_Price_Downloaded.objects.available_and_summary_unprocessed(q_date)
            if _process_day_summary(qdate):
                ob.summary_processed = True
                ob.save()
        except Twse_Summary_Price_Downloaded.DoesNotExist:
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
        
def _process_day_summary(qdate):
    filename = "%s/market_summary_%s" % (TWSE_DOWNLOAD_C, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
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
                    type_item, created = Market_Summary_Type.objects.get_or_create(name=dt_data)
                    dt_item = Market_Summary()
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

def twse_daily_updown_process_job(q_date=None):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_updown_process_job.__name__  
    try:
        if not q_date: 
            q_date = datetime.datetime.now()
        qdate = q_date.strftime("%Y%m%d")
        # check if downloaded and available
        try:
            ob = Twse_Summary_Price_Downloaded.objects.available_and_updown_unprocessed(q_date)
            if _process_day_updown_stats(qdate):
                ob.updown_processed = True
                ob.save()
        except Twse_Summary_Price_Downloaded.DoesNotExist:
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
        
def _split_string(s_data):
    pos = s_data.find('(')
    part1 = s_data[:pos]
    part2 = s_data[pos + 1:len(s_data) - 1]
    return (part1, part2)

def _process_day_updown_stats(qdate):
    filename = "%s/market_up_down_stats_%s" % (TWSE_DOWNLOAD_D, qdate)
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s up_down_stats records in file." % len(rows))
        #
        dt_item = Stock_Up_Down_Stats()
        dt_item.trading_date=dateutil.convertToDate(qdate)  
        # process rows[0]
        cells = rows[0].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.total_up, dt_item.total_up_limit = _split_string(dt_data)
        dt_data = cells[2].string.strip().replace(',', '')
        dt_item.stock_up, dt_item.stock_up_limit = _split_string(dt_data)
        # process rows[1]
        cells = rows[1].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.total_down, dt_item.total_down_limit = _split_string(dt_data)
        dt_data = cells[2].string.strip().replace(',', '')
        dt_item.stock_down, dt_item.stock_down_limit = _split_string(dt_data)
        # process rows[2]
        cells = rows[2].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.total_unchange = dt_data
        dt_data = cells[2].string.strip().replace(',', '')
        dt_item.stock_unchange = dt_data
        # process rows[3]
        cells = rows[3].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.total_unmatch = dt_data
        dt_data = cells[2].string.strip().replace(',', '')
        dt_item.stock_unmatch = dt_data
        # process rows[4]
        cells = rows[4].find_all('td', recursive=False)
        dt_data = cells[1].string.strip().replace(',', '')
        dt_item.total_na = dt_data
        dt_data = cells[2].string.strip().replace(',', '')
        dt_item.stock_na = dt_data
        dt_item.save()
    return True


def test_black_scholes_job(warrant_symbol, qdate):
    # get the warrant_item and trading_warrant and target_stock model instances
    try:
        warrant_item= Warrant_Item.objects.select_related('target_stock').get(symbol=warrant_symbol)
        trading_warrant_item = Twse_Trading_Warrant.objects.get(warrant_symbol=warrant_item, trading_date=qdate)
        trading_item = Twse_Trading.objects.get(stock_symbol=warrant_item.target_stock, trading_date=qdate)
        # or use closing_price
        exercise_ratio = warrant_item.exercise_ratio*1.0/1000.0
        spot_price = float(trading_item.last_best_bid_price)
        strike_price = float(warrant_item.strike_price)
        interest_rate= 0.0136
        expiration_date = warrant_item.expiration_date
        diff = expiration_date - qdate 
        time_to_maturity = float(diff.days)/365.0
        # or use closing_price
        option_price = float(trading_warrant_item.last_best_bid_price)/exercise_ratio
        if warrant_item.is_call():
            sigma = option_price_implied_volatility_call_black_scholes_newton(spot_price, strike_price, interest_rate, time_to_maturity,  
                                                              option_price)
            delta = option_price_delta_call_black_scholes(spot_price, strike_price, interest_rate, sigma, time_to_maturity)*exercise_ratio
            warrant_price = option_price_call_black_scholes(spot_price, strike_price, interest_rate, sigma, time_to_maturity)
        else:
            sigma = option_price_implied_volatility_put_black_scholes_newton(spot_price, strike_price, interest_rate, time_to_maturity,  
                                                              option_price)
            delta = option_price_delta_put_black_scholes(spot_price, strike_price, interest_rate, sigma, time_to_maturity)*exercise_ratio
            warrant_price = option_price_put_black_scholes(spot_price, strike_price, interest_rate, sigma, time_to_maturity)
        print "Warrant item %s: spot_price = %s, strike_price= %s, option_price= %s" % (warrant_symbol,spot_price,strike_price, option_price)
        print "Warrant item %s: expiration_date = %s, time_to_maturity= %s" % (warrant_symbol,expiration_date,time_to_maturity)
        print "Warrant item %s: intrinsic volatility= %s, delta= %s" % (warrant_symbol,sigma,delta)
        print "Warrant item %s: warrant price= %s" % (warrant_symbol,warrant_price)
    except ObjectDoesNotExist:
        logger.warning("Warrant symbol %s not found" % warrant_symbol)
        
    
