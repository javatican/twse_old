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
import traceback

from core.models import Cron_Job_Log, Twse_Trading, \
    Warrant_Item, Stock_Item, get_stock_item_type, get_warrant_exercise_style, \
    get_warrant_classification, select_warrant_type_code, Twse_Summary_Price_Processed, \
    Index_Item, Index_Change_Info, Market_Summary_Type, Market_Summary, \
    Stock_Up_Down_Stats, Twse_Trading_Warrant, Twse_Trading_Processed, \
    Trading_Date, Twse_Index_Stats, Twse_Trading_Strategy
from core2.models import Gt_Stock_Item, Gt_Warrant_Item
import numpy as np
from warrant_app.settings import TWSE_DOWNLOAD_1, TWSE_DOWNLOAD_2, \
    TWSE_DOWNLOAD_3, TWSE_DOWNLOAD_4, TWSE_DOWNLOAD_5, TWSE_TRADING_DOWNLOAD_URL, \
    TWSE_PRICE_DOWNLOAD_URL, TWSE_DOWNLOAD_0, TWSE_DOWNLOAD_A, \
    TWSE_DOWNLOAD_B, TWSE_DOWNLOAD_C, TWSE_DOWNLOAD_D, GT_DOWNLOAD_2, \
    GT_DOWNLOAD_4, GT_DOWNLOAD_3, SLEEP_TIME_SHORT, SLEEP_TIME_LONG
from warrant_app.utils import dateutil
from warrant_app.utils.black_scholes import option_price_implied_volatility_call_black_scholes_newton, \
    option_price_implied_volatility_put_black_scholes_newton, \
    option_price_delta_call_black_scholes, option_price_delta_put_black_scholes, \
    option_price_call_black_scholes, option_price_put_black_scholes
from warrant_app.utils.dateutil import roc_year_to_western, western_to_roc_year, \
    convertToDate, is_third_wednesday, roc_year
from warrant_app.utils.logutil import log_message
from warrant_app.utils.stringutil import is_float
from warrant_app.utils.trading_util import moving_avg, \
    calc_stochastic_oscillator_for_stock, recalc_all_di_adx_for_stock, \
    update_di_adx_for_stock, pre_filtering_bull, breakout_list_bull, \
    breakout2_list_bull, breakout3_list_bull, watch_list_bull, \
    pre_filtering_bear, breakout_list_bear, breakout2_list_bear, \
    breakout3_list_bear, watch_list_bear, stochastic_pop_drop_plot
from warrant_app.utils.warrant_util import check_if_warrant_item, to_dict


# from django.utils.translation import ugettext as _
logger = logging.getLogger('warrant_app.cronjob')

# Below code is one time use, so comment out.
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

#below function is used to insert 'IX0001','IX0027', 'IX0039' index_change_info data into twse_trading
# only run once
def update_twse_trading_for_index():
    check_list=[]
    stocks=Stock_Item.objects.all()
    for stock in stocks:
        if not stock.twse_trading_list.exists():
            check_list.append(stock)
    strategy_objects_to_save=[]
    for item in check_list:
        if item.symbol=='IX0001':
            #IX0001 stock symbol is 'IDXWT' index wearn symbol
            index_item=Index_Item.objects.get(wearn_symbol='IDXWT')
        elif item.symbol=='IX0027':
            # IX0027 is 'IDX23'
            index_item=Index_Item.objects.get(wearn_symbol='IDX23')
        elif item.symbol=='IX0039':
            # IX0039 is 'IDX28'
            index_item=Index_Item.objects.get(wearn_symbol='IDX28')
            #
        ici_list=index_item.index_change_list.all()
        for ici_item in ici_list:
            trading_item=Twse_Trading()
            trading_item.stock_symbol=item
            trading_item.trading_date=ici_item.trading_date
            trading_item.trade_value=ici_item.trade_value
            trading_item.opening_price=ici_item.opening_price
            trading_item.highest_price=ici_item.highest_price
            trading_item.lowest_price=ici_item.lowest_price
            trading_item.closing_price=ici_item.closing_price
            trading_item.price_change=ici_item.change
            trading_item.save()
            #create strategy object
            tts = Twse_Trading_Strategy()
            tts.trading = trading_item
            tts.trading_date = trading_item.trading_date
            tts.stock_symbol= trading_item.stock_symbol
            strategy_objects_to_save.append(tts)     
                    
            #
    Twse_Trading_Strategy.objects.bulk_create(strategy_objects_to_save)
    
    
    
def download_twse_various_index_job(year=None, month_list=None):
    # This job is used to download various twse index (open,high, low, close) from wearn site 
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = download_twse_various_index_job.__name__ 
    try:    
        last_data_date=Index_Change_Info.objects.get_last_trading_date_for_trade_value()
        today = datetime.date.today()
        if not year:
            #default: this year
            year = today.year
        if not month_list:
            month_list = []
            month_list.append(today.month)
        # need stock object references for symbols 'IX0001', 'IX0027', 'IX0039' for inserting twse_trading entries in DB 
        stock_IX0001=Stock_Item.objects.get(symbol='IX0001')
        stock_IX0027=Stock_Item.objects.get(symbol='IX0027')
        stock_IX0039=Stock_Item.objects.get(symbol='IX0039')
        strategy_objects_to_save=[]
        # the year parameter is in ROC year , month with 2 digits
        for n in month_list:
            if n < 10:
                month = "0%s" % n
            else:
                month = n
                #
            index_list=Index_Item.objects.get_index_with_wearn_symbol()
            for index_entry in index_list:
                index_symbol=index_entry.wearn_symbol
                try:        
                    serviceUrl = 'http://stock.wearn.com/adata.asp?Year=%s&month=%s&kind=%s' % (roc_year(year) , month, index_symbol)
                    print serviceUrl
                    httpResponse = requests.get(serviceUrl)
                    httpResponse.encoding = "big5"
                except requests.HTTPError, e:
                    result = e.read()
                    raise Exception(result)
                
                soup = BeautifulSoup(httpResponse.text, 'lxml')              
                div_element = soup.find('div', class_='stockalllist')
                table_element = div_element.find('table')
                tr_list = table_element.find_all('tr')
                #skip 2 rows
                for j, row in enumerate(tr_list[2:]): 
                    ici_item=None
                    for i, td_element in enumerate(row.find_all('td', recursive=False)):
                        dt_data = td_element.string.strip()
                        # dt_data contains some &nbsp; characters, need to remove them
                        dt_data=dt_data.replace('&nbsp;', '')
                        if i == 0:
                            trading_date = roc_year_to_western(dt_data)
                            # if data's trading_date is before last_data_date, skip it.
                            if trading_date <= last_data_date: break
                            # assuming the Index_Change_Info instance is already in the DB, if not, skip it.
                            try:
                                ici_item = Index_Change_Info.objects.get(twse_index=index_entry, trading_date=trading_date)
                            except Index_Change_Info.DoesNotExist: 
                                break                               
                        elif i == 1:
                            ici_item.opening_price = float(dt_data.replace(',', ''))
                        elif i == 2:
                            ici_item.highest_price = float(dt_data.replace(',', ''))
                        elif i == 3:
                            ici_item.lowest_price = float(dt_data.replace(',', ''))
                            # closing_price no need to update , since it is already there.
#                         elif i == 4:
#                             ici_item.closing_price = float(dt_data.replace(',', ''))   
                        elif i == 5:
                            ici_item.trade_value = float(dt_data.replace(',', ''))*1000  
                    if ici_item:
                        ici_item.save()
                        # if index_symbol is 'IDXWT', 'IDX23', 'IDX28' --> create twse_trading items in DB
                        if index_symbol=="IDXWT":                          
                            trading_item=Twse_Trading()
                            trading_item.stock_symbol=stock_IX0001
                            trading_item.trading_date=ici_item.trading_date
                            trading_item.trade_value=ici_item.trade_value
                            trading_item.opening_price=ici_item.opening_price
                            trading_item.highest_price=ici_item.highest_price
                            trading_item.lowest_price=ici_item.lowest_price
                            trading_item.closing_price=ici_item.closing_price
                            trading_item.price_change=ici_item.change
                            trading_item.save()
                            #create strategy object
                            tts = Twse_Trading_Strategy()
                            tts.trading = trading_item
                            tts.trading_date = trading_item.trading_date
                            tts.stock_symbol= trading_item.stock_symbol
                            strategy_objects_to_save.append(tts)
                        elif index_symbol=="IDX23":                          
                            trading_item=Twse_Trading()
                            trading_item.stock_symbol=stock_IX0027
                            trading_item.trading_date=ici_item.trading_date
                            trading_item.trade_value=ici_item.trade_value
                            trading_item.opening_price=ici_item.opening_price
                            trading_item.highest_price=ici_item.highest_price
                            trading_item.lowest_price=ici_item.lowest_price
                            trading_item.closing_price=ici_item.closing_price
                            trading_item.price_change=ici_item.change
                            trading_item.save()
                            #create strategy object
                            tts = Twse_Trading_Strategy()
                            tts.trading = trading_item
                            tts.trading_date = trading_item.trading_date
                            tts.stock_symbol= trading_item.stock_symbol
                            strategy_objects_to_save.append(tts)
                        elif index_symbol=="IDX28":                          
                            trading_item=Twse_Trading()
                            trading_item.stock_symbol=stock_IX0039
                            trading_item.trading_date=ici_item.trading_date
                            trading_item.trade_value=ici_item.trade_value
                            trading_item.opening_price=ici_item.opening_price
                            trading_item.highest_price=ici_item.highest_price
                            trading_item.lowest_price=ici_item.lowest_price
                            trading_item.closing_price=ici_item.closing_price
                            trading_item.price_change=ici_item.change
                            trading_item.save()
                            #create strategy object
                            tts = Twse_Trading_Strategy()
                            tts.trading = trading_item
                            tts.trading_date = trading_item.trading_date
                            tts.stock_symbol= trading_item.stock_symbol
                            strategy_objects_to_save.append(tts)
        if len(strategy_objects_to_save)>0: 
            Twse_Trading_Strategy.objects.bulk_create(strategy_objects_to_save)
#
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
        
def download_twse_index_stats_job(year=None, month_list=None):
    # this job is used to download twse index open,high, low, close index
    # as well as create Trading_Date entry
    _CREATE_TRADING_DATE_OBJECT = True
    _CHECK_LAST_TRADING_DATE = True
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = download_twse_index_stats_job.__name__ 
    try:    
        serviceUrl = 'http://www.twse.com.tw/ch/trading/indices/MI_5MINS_HIST/MI_5MINS_HIST.php'
        if _CHECK_LAST_TRADING_DATE:
            last_trading_date = Trading_Date.objects.get_last_trading_date()
        today = datetime.date.today()
        if not year:
            #default: this year
            year = today.year
        if not month_list:
            month_list = []
            month_list.append(today.month)
            
        # the year parameter is in ROC year , month with 2 digits
        for n in month_list:
            if n < 10:
                month = "0%s" % n
            else:
                month = n
            parameters = {'myear': roc_year(year) , 'mmon': month}
            try:        
                httpResponse = requests.post(serviceUrl, params=parameters, stream=True)
                httpResponse.encoding = "big5"
            except requests.HTTPError, e:
                result = e.read()
                raise Exception(result)
            
            soup = BeautifulSoup(httpResponse.text, 'lxml')
            table_element = soup.find('table', class_='board_trad')
            tr_list = table_element.find_all('tr', class_='gray12')
            trading_date_to_create = []
            twse_index_stats_to_create = []
            j = 0
            for row in tr_list:
                i = 0
                for td_element in row.find_all('td', recursive=False):
                    dt_data = td_element.string.strip()
                    if i == 0:
                        trading_date = roc_year_to_western(dt_data)
                        if _CHECK_LAST_TRADING_DATE:
                            if trading_date <= last_trading_date: break
                            
                        if _CREATE_TRADING_DATE_OBJECT:
                            tdate = Trading_Date()
                            tdate.trading_date = trading_date
                            # date.weekday(): Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
                            tdate.day_of_week = tdate.trading_date.weekday() + 1
                            if j == 0:
                                # first trading date of the month
                                tdate.first_trading_day_of_month = True
#                             if j == len(tr_list) - 1:
#                                 tdate.last_trading_day_of_month = True
                            if is_third_wednesday(tdate.trading_date):
                                tdate.is_future_delivery_day = True
                            trading_date_to_create.append(tdate)
 # 
                        twse_index_stats = Twse_Index_Stats()
                        twse_index_stats.trading_date = trading_date
                    elif i == 1:
                        twse_index_stats.opening_price = float(dt_data.replace(',', ''))
                    elif i == 2:
                        twse_index_stats.highest_price = float(dt_data.replace(',', ''))
                    elif i == 3:
                        twse_index_stats.lowest_price = float(dt_data.replace(',', ''))
                    elif i == 4:
                        twse_index_stats.closing_price = float(dt_data.replace(',', ''))
                        twse_index_stats_to_create.append(twse_index_stats)                     
                    i += 1
                j += 1
            if _CREATE_TRADING_DATE_OBJECT: 
                if trading_date_to_create: Trading_Date.objects.bulk_create(trading_date_to_create)          
            if twse_index_stats_to_create: Twse_Index_Stats.objects.bulk_create(twse_index_stats_to_create)
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()

def download_twse_index_stats2_job(year=None, month_list=None):
    # this job is used to update Twse_Index_Stats's 
    # trade_volume, trade_transaction, trade_value data.
    # Need to be run after download_twse_index_stats_job
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = download_twse_index_stats2_job.__name__ 
    try:  
        today = datetime.date.today()
        if not year:
            #default: this year
            year = today.year
        if not month_list:
            month_list = []
            month_list.append(today.month)
            
        # the year parameter is in ROC year , month with 2 digits
        for n in month_list:
            if n < 10:
                month = "0%s" % n
            else:
                month = n
            try:        
                serviceUrl = 'http://www.twse.com.tw/ch/trading/exchange/FMTQIK/genpage/Report%s%s/%s%s_F3_1_2.php?STK_NO=&myear=%s&mmon=%s' % (year, month, year, month, year, month)
                httpResponse = requests.get(serviceUrl)
                httpResponse.encoding = "big5"
            except requests.HTTPError, e:
                result = e.read()
                raise Exception(result)
            
            soup = BeautifulSoup(httpResponse.text, 'lxml')
            table_element = soup.find('table', class_='board_trad')
            tr_list = table_element.find_all('tr', class_='basic2')
            twse_index_stats_to_update = []
            j = 0
            for row in tr_list[1:]:
                i = 0
                for td_element in row.find_all('td', recursive=False):
                    dt_data = td_element.string.strip()
                    if i == 0:
                        trading_date = roc_year_to_western(dt_data)
                        try:
                            twse_index_stats = Twse_Index_Stats.objects.by_date(trading_date)
                            if twse_index_stats.trade_volume > 0: 
                                break
                        except:
                            break
                    elif i == 1:
                        twse_index_stats.trade_volume = float(dt_data.replace(',', ''))
                    elif i == 2:
                        twse_index_stats.trade_value = float(dt_data.replace(',', ''))
                    elif i == 3:
                        twse_index_stats.trade_transaction = float(dt_data.replace(',', ''))
                        twse_index_stats_to_update.append(twse_index_stats)  
                        break                   
                    i += 1
                j += 1   
            if twse_index_stats_to_update: 
                for item in twse_index_stats_to_update:
                    item.save()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()
        
def twse_index_avg_calc_job():
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_index_avg_calc_job.__name__ 
    UPDATE_MODE = True 
    try:
        if UPDATE_MODE:
            missing_items = Twse_Index_Stats.objects.get_missing_avg().order_by('trading_date')
            for item in missing_items:
                # get prices by descending order on 'trading_date'
                price_list = Twse_Index_Stats.objects.price_lte_date(item.trading_date).order_by('-trading_date')[:240]
                price_list_count = len(price_list)
                #
                fieldname_list = ['week_avg', 'two_week_avg', 'month_avg', 'quarter_avg', 'half_avg', 'year_avg']
                DAY_AVERAGE_LIST = [5, 10, 20, 60, 120, 240]
                for fieldname, DAY_AVERAGE in zip(fieldname_list, DAY_AVERAGE_LIST):
                    if price_list_count < DAY_AVERAGE:
                        break
                    else:
                        # calc avg
                        avg_price = np.average(np.array([float(price) for price in price_list[:DAY_AVERAGE]]))
                        setattr(item, fieldname, avg_price) 
                item.save()                       
        else:
            # this will recalc all avg values for all Twse_Index_Stats entries in DB
            items = Twse_Index_Stats.objects.all().order_by('trading_date')
            price_list = []
            for item in items:
                price_list.append(float(item.closing_price))
            price_array = np.array(price_list) 
            fieldname_list = ['week_avg', 'two_week_avg', 'month_avg', 'quarter_avg', 'half_avg', 'year_avg']
            DAY_AVERAGE_LIST = [5, 10, 20, 60, 120, 240]
            for fieldname, DAY_AVERAGE in zip(fieldname_list, DAY_AVERAGE_LIST):
                try:
                    avg_array = moving_avg(price_array, DAY_AVERAGE)
                except:
                    break
                # update fields
                for item, price in zip(items[DAY_AVERAGE - 1:], avg_array):
                    setattr(item, fieldname, price) 
            for item in items:
                item.save()
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)

def twse_stock_price_avg_calc_job():
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_stock_price_avg_calc_job.__name__ 
    UPDATE_MODE = True 
    try:
        if UPDATE_MODE:
            stock_items = Stock_Item.objects.all()
            for stock in stock_items:
                missing_items = stock.twse_trading_list.get_missing_avg().order_by('trading_date')
                
                for item in missing_items:
                    # get prices by descending order on 'trading_date'
                    price_list = stock.twse_trading_list.price_lte_date(item.trading_date).order_by('-trading_date')[:240]
                    price_list_count = len(price_list)
 #
                    fieldname_list = ['week_avg', 'two_week_avg', 'month_avg', 'quarter_avg', 'half_avg', 'year_avg']
                    DAY_AVERAGE_LIST = [5, 10, 20, 60, 120, 240]
                    for fieldname, DAY_AVERAGE in zip(fieldname_list, DAY_AVERAGE_LIST):
                        if price_list_count < DAY_AVERAGE:
                            break
                        else:
                            # calc avg
                            avg_price = np.average(np.array([float(price) for price in price_list[:DAY_AVERAGE]]))
                            setattr(item, fieldname, avg_price) 
                    item.save()                       
        else:
            # this will recalc all avg values for all Twse_trading entries in DB
            # first get all stock_items
            stock_items = Stock_Item.objects.all()
            for stock in stock_items:
                items = stock.twse_trading_list.all().order_by('trading_date')
                price_list = []
                for item in items:
                    price_list.append(float(item.closing_price))
                price_array = np.array(price_list) 
                fieldname_list = ['week_avg', 'two_week_avg', 'month_avg', 'quarter_avg', 'half_avg', 'year_avg']
                DAY_AVERAGE_LIST = [5, 10, 20, 60, 120, 240]
                for fieldname, DAY_AVERAGE in zip(fieldname_list, DAY_AVERAGE_LIST):
                    try:
                        avg_array = moving_avg(price_array, DAY_AVERAGE)
                    except:
                        break
                    # update fields
                    for item, price in zip(items[DAY_AVERAGE - 1:], avg_array):
                        setattr(item, fieldname, price) 
                for item in items:
                    item.save()
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
def twse_stock_calc_stoch_osci_adx_job():
# This job is for calculating stochastic oscillator(long term(70-day and short term(14-day)) and ADX values
# for each Twse stock.
# Two modes are implemented. 
# 1. 'all' mode: recalculate the stoch_osci and ADX values for all the trading data. 
# This mode is for first time and only need to run once.
# 2. 'update' mode: calculate any missing stoch_osci and ADX values once new  trading data is available.
# This mode can be run frequently or daily. 
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_stock_calc_stoch_osci_adx_job.__name__ 
    UPDATE_MODE = True 
    try:
        if UPDATE_MODE:
            stock_items = Stock_Item.objects.all()
            #stock_items = Stock_Item.objects.filter(symbol='3008')
            for stock in stock_items:
                # calculate 14-day stochastic oscillator
                # parameters
                LOOK_BACK_PERIOD = 14
                K_SMOOTHING = 3
                D_MOVING_AVERAGE = 3
                # first get the last trading_date which has the fourteen_day_k calculated
                is_exist = stock.twse_trading_list.filter(strategy__fourteen_day_k__isnull=False).exists()
                if is_exist: 
                    last_not_null = stock.twse_trading_list.filter(strategy__fourteen_day_k__isnull=False).values_list('trading_date', flat=True).order_by('-trading_date')[0]                
                    
                    #print "last_not_null=%s" % last_not_null
                    # get the starting date after which their trading data are needed to update stoch_osci values for new trading data
                    n = LOOK_BACK_PERIOD + K_SMOOTHING + D_MOVING_AVERAGE - 3
                    start_date = stock.twse_trading_list.filter(trading_date__lte=last_not_null).values_list('trading_date', flat=True).order_by('-trading_date')[n - 1]
                    # get trading items and related model objects 'strategy'
                    items = stock.twse_trading_list.filter(trading_date__gte=start_date).select_related('strategy').order_by('trading_date')     
                else:
                    # no fourteen_day_k data previously, so back to the 'all' mode
                    items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date') 
                # do the calculation                            
                try:                    
                    strategy_items_to_update = calc_stochastic_oscillator_for_stock(stock, 
                                                                                      trading_item_list=items, 
                                                                                      LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, 
                                                                                      K_SMOOTHING=K_SMOOTHING, 
                                                                                      D_MOVING_AVERAGE=D_MOVING_AVERAGE)                                    
                except:
                    logger.warning("Error when calculating stochastic_oscillator with parameters(%s,%s,%s) for stock pk= %s" % (LOOK_BACK_PERIOD, K_SMOOTHING, D_MOVING_AVERAGE, stock.id))
                    print traceback.format_exc()
                    # continue for the next stock
                    continue  
                # update model in DB    
                for item in strategy_items_to_update:
                    item.save()
                # calculate 70-day stoch osci with the same logic as 14-day one
                LOOK_BACK_PERIOD = 70
                K_SMOOTHING = 3
                D_MOVING_AVERAGE = 3
                is_exist = stock.twse_trading_list.filter(strategy__seventy_day_k__isnull=False).exists()
                if is_exist: 
                    last_not_null = stock.twse_trading_list.filter(strategy__seventy_day_k__isnull=False).values_list('trading_date', flat=True).order_by('-trading_date')[0]
                    n = LOOK_BACK_PERIOD + K_SMOOTHING + D_MOVING_AVERAGE - 3
                    start_date = stock.twse_trading_list.filter(trading_date__lte=last_not_null).values_list('trading_date', flat=True).order_by('-trading_date')[n - 1]
                    items = stock.twse_trading_list.filter(trading_date__gte=start_date).select_related('strategy').order_by('trading_date')     
                else:
                    items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date')                             
                try:                    
                    strategy_items_to_update = calc_stochastic_oscillator_for_stock(stock, 
                                                                                      trading_item_list=items, 
                                                                                      LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, 
                                                                                      K_SMOOTHING=K_SMOOTHING, 
                                                                                      D_MOVING_AVERAGE=D_MOVING_AVERAGE)
                except:
                    logger.warning("Error when calculating stochastic_oscillator with parameters(%s,%s,%s) for stock pk= %s" % (LOOK_BACK_PERIOD, K_SMOOTHING, D_MOVING_AVERAGE, stock.id))
                    print traceback.format_exc()
                    continue                                        
                for item in strategy_items_to_update:
                    item.save()
                #calculate ADX
                SMOOTHING_FACTOR = 14  
                is_exist = stock.twse_trading_list.filter(strategy__adx__isnull=False).exists()
                if is_exist: 
                    last_not_null = stock.twse_trading_list.filter(strategy__adx__isnull=False).values_list('trading_date', flat=True).order_by('-trading_date')[0]
                    start_date=last_not_null
                    items = stock.twse_trading_list.filter(trading_date__gte=start_date).select_related('strategy').order_by('trading_date')   
                    try:                    
                        strategy_items_to_update = update_di_adx_for_stock(stock, trading_item_list=items, SMOOTHING_FACTOR=SMOOTHING_FACTOR)                
                    except:
                        print traceback.format_exc()
                        logger.warning("Error when calculating average directional index with for stock pk= %s" % stock.id)
                        continue  
                                                              
                    for item in strategy_items_to_update:
                        item.save()
                else:
                    items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date')   
                    try:
                        strategy_items_to_update = recalc_all_di_adx_for_stock(stock, trading_item_list=items, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
                    except:
                        print traceback.format_exc()
                        logger.warning("Error when calculating average directional index with for stock pk= %s" % stock.id)
                        continue
                    for item in strategy_items_to_update:
                        item.save()
        else:
            # this will recalc all stoch_osci and ADX values for all Twse_trading entries in DB
            # first get all stock_items
            stock_items = Stock_Item.objects.all()
            # stock_items = Stock_Item.objects.filter(symbol='2312')
            for stock in stock_items:
                # Use a set here to store strategy items needed for update (for dealing duplicates)
                strategy_items_to_update = set()
                items = stock.twse_trading_list.all().select_related('strategy').order_by('trading_date')
                # 14-day stochastic oscillator
                try:
                    LOOK_BACK_PERIOD = 14
                    K_SMOOTHING = 3
                    D_MOVING_AVERAGE = 3
                    result = calc_stochastic_oscillator_for_stock(stock, trading_item_list=items, LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, K_SMOOTHING=K_SMOOTHING, D_MOVING_AVERAGE=D_MOVING_AVERAGE)    
                    #result is a list            
                    strategy_items_to_update.update(set(result))
                except:
                    logger.warning("Error when calculating stochastic_oscillator with parameters(%s,%s,%s) for stock pk= %s" % (LOOK_BACK_PERIOD, K_SMOOTHING, D_MOVING_AVERAGE, stock.id))
                    print traceback.format_exc()
                    continue
                # 70-day stochastic oscillator
                try:                   
                    LOOK_BACK_PERIOD = 70
                    K_SMOOTHING = 3
                    D_MOVING_AVERAGE = 3
                    result = calc_stochastic_oscillator_for_stock(stock, trading_item_list=items, LOOK_BACK_PERIOD=LOOK_BACK_PERIOD, K_SMOOTHING=K_SMOOTHING, D_MOVING_AVERAGE=D_MOVING_AVERAGE)                
                    strategy_items_to_update.update(set(result))
                except:
                    logger.warning("Error when calculating stochastic_oscillator with parameters(%s,%s,%s) for stock pk= %s" % (LOOK_BACK_PERIOD, K_SMOOTHING, D_MOVING_AVERAGE, stock.id)) 
                    print traceback.format_exc()                   
                    continue
                # calculate +DI14, -DI14, ADX for each trading date
                try:                    
                    SMOOTHING_FACTOR = 14                        
                    result = recalc_all_di_adx_for_stock(stock, trading_item_list=items, SMOOTHING_FACTOR=SMOOTHING_FACTOR)
                    strategy_items_to_update.update(set(result))
                except:
                    logger.warning("Error when calculating average directional index with for stock pk= %s" % stock.id)
                    print traceback.format_exc()
                    continue
                # update tts
                for item in strategy_items_to_update:
                    item.save()
                
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)

        
def twse_manage_stock_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_manage_stock_info_job.__name__ 
    try:    
        items = Stock_Item.objects.data_not_ok()
        if manage_stock_info(items):
            job.success()
        else:
            job.error_message = 'process runs with interruption'
            raise Exception(job.error_message)
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        for item in items:
            item.save()
        job.save()
        
def manage_stock_info(items, is_gt=False): 
    originUrl = 'http://mops.twse.com.tw/mops/web/t05st03'
    ajaxUrl = 'http://mops.twse.com.tw/mops/web/ajax_quickpgm' 
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
        gen = (item for item in items if item.data_ok == False)
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
            if is_gt:
                filename = "%s/stock_info_%s" % (GT_DOWNLOAD_2, item.symbol)
            else:
                filename = "%s/stock_info_%s" % (TWSE_DOWNLOAD_2, item.symbol)
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text     
            # process the file
            with codecs.open(filename, 'r', encoding="utf8") as fd:
                if _process_stock_info(item, fd): 
                    item.data_ok = True
                else:  
                    logger.info("Error processing stock info : %s" % item.symbol)
            time.sleep(SLEEP_TIME_SHORT)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(SLEEP_TIME_LONG)
        return manage_stock_info(items, is_gt)
    except:
        raise
    
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
        if anchor_element.string == None:
            # means <a> tag contains more than 1 child tags
            stock_data = ' '.join(anchor_element.stripped_strings)
        else:
            stock_data = anchor_element.string.strip()
        print stock_data
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

def twse_manage_warrant_info_job():
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_manage_warrant_info_job.__name__ 

    try:    
        items = Warrant_Item.objects.data_not_ok()
        if manage_warrant_info(items):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed() 
        raise 
    finally:        
        for item in items:
            item.save()
        job.save()
        
def manage_warrant_info(items, is_gt=False): 
    originUrl = 'http://mops.twse.com.tw/mops/web/t90sbfa01'
    ajaxUrl = 'http://mops.twse.com.tw/mops/web/ajax_t90sbfa01' 
    try: 
        session = Session()
        # HEAD requests ask for *just* the headers, which is all you need to grab the
        # session cookie
        session.head(originUrl)
        gen = (item for item in items if item.data_ok == False)
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
            if is_gt:
                filename = "%s/warrant_info_%s" % (GT_DOWNLOAD_4, item.symbol)
            else:
                filename = "%s/warrant_info_%s" % (TWSE_DOWNLOAD_4, item.symbol)
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text 
            # process data
            with codecs.open(filename, 'r', encoding="utf8") as fd:                            
                if _process_warrant_info(item, fd):                     
                    item.data_ok = True
                else:
                    logger.info("Error processing warrant info : %s" % item.symbol)
            time.sleep(SLEEP_TIME_SHORT)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(SLEEP_TIME_LONG)
        return manage_warrant_info(items, is_gt)
    except:
        raise
 
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
            if item.is_twse_stock():
                stock_item, created = Stock_Item.objects.get_or_create(symbol=warrant_data)
            else:
                stock_item, created = Gt_Stock_Item.objects.get_or_create(symbol=warrant_data)
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
      
def twse_manage_warrant_info_use_other_url_job():
# different url , for 'finished' warrants 
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_manage_warrant_info_use_other_url_job.__name__ 
    try:    
        items = Warrant_Item.objects.data_not_ok()
        if manage_warrant_info_2(items):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed() 
        raise 
    finally:        
        for item in items:
            item.save()
        job.save()
        
def manage_warrant_info_2(items, is_gt=False): 
    # different url , for 'finished' warrants 
    gen = (item for item in items if item.data_ok == False)
    try: 
        for item in gen:
            serviceUrl = 'http://www.cnyes.com/twstock/Wbasic/%s.htm' % item.symbol
            httpResponse = requests.get(serviceUrl)
            httpResponse.encoding = "utf-8"
            if is_gt:
                filename = "%s/Wwarrant_info_%s" % (GT_DOWNLOAD_4, item.symbol)
            else:
                filename = "%s/Wwarrant_info_%s" % (TWSE_DOWNLOAD_4, item.symbol)
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                soup = BeautifulSoup(httpResponse.text , 'lxml')
                table_element = soup.find(id='ctl00_ContentPlaceHolder1_htb1')
                if table_element == None: 
                    logger.warning("No table tag in warrant info")
                    time.sleep(SLEEP_TIME_SHORT)
                    continue
#
                for tag in table_element.find_all('tr'):
                    print >> fd, unicode(tag) 
            # next do the process         
            with codecs.open(filename, 'r', encoding="utf8") as fd:                            
                if _process_warrant_info_2(item, fd):   
                    item.data_ok = True
                else:
                    logger.info("Error processing warrant info : %s" % item.symbol)
            time.sleep(SLEEP_TIME_SHORT)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(SLEEP_TIME_LONG)
        return manage_warrant_info_2(items, is_gt)
    except:
        raise
          
def _process_warrant_info_2(item, fd): 
    # go along with manage_warrant_info_2, ie. different url , for 'finished' warrants 
    soup = BeautifulSoup(fd, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) == 0: 
        logger.warning("No table row tag in file %s" % item.symbol)
        return False
    # row 0
    td_elements = rows[0].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip()
    if item.symbol != warrant_data: 
        return False
    item.type_code = select_warrant_type_code(item.symbol)
    warrant_data = td_elements[1].string.strip()
    if item.is_twse_stock():
        stock_item, created = Stock_Item.objects.get_or_create(symbol=warrant_data)
    else:
        stock_item, created = Gt_Stock_Item.objects.get_or_create(symbol=warrant_data)
    item.target_stock = stock_item
    item.target_symbol = stock_item.symbol     
    # row 1
    td_elements = rows[1].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip()
    item.name = warrant_data        
    # row 3
    td_elements = rows[3].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip()
    item.classification = get_warrant_classification(warrant_data[:2])  
    warrant_data = td_elements[1].string.strip()
    item.issued_volume = int(warrant_data.replace(',', ''))   
    # row 5
    td_elements = rows[5].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip() 
    item.listed_date = convertToDate(warrant_data)   
    # row 6
    td_elements = rows[6].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip() 
    item.expiration_date = convertToDate(warrant_data)
    # row 7
    td_elements = rows[7].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip() 
    item.last_trading_date = convertToDate(warrant_data)
    # row 8
    td_elements = rows[8].find_all('td', recursive=False)
    warrant_data = td_elements[1].string.strip() 
    item.exercise_ratio = int(float(warrant_data.replace(',', '')))
    # row 9
    td_elements = rows[9].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip() 
    item.strike_price = float(warrant_data.replace(',', '')) 
    # row 11
    td_elements = rows[11].find_all('td', recursive=False)
    warrant_data = td_elements[0].string.strip() 
    item.exercise_style = get_warrant_exercise_style(warrant_data)  
    warrant_data = td_elements[1].string.strip() 
    item.issuer = warrant_data
#
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
        if bulk_download_warrant_info(stocks):
            job.success()
        else:
            job.error_message = 'Download process runs with interruption'
            raise Exception(job.error_message)
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        job.save()
                
def bulk_download_warrant_info(items, is_gt=False): 
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
            if is_gt:
                filename = "%s/bulk_warrant_info_%s" % (GT_DOWNLOAD_3, item['stock_symbol__symbol'])
            else:
                filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, item['stock_symbol__symbol'])
            with codecs.open(filename, 'wb', encoding="utf8") as fd:
                print >> fd, httpResponse.text           
            item['data_downloaded'] = True
            time.sleep(SLEEP_TIME_SHORT)
        return True
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result) 
    except requests.ConnectionError:
        logger.info("*** Sleep 180 secs before trying downloading again")
        time.sleep(SLEEP_TIME_LONG)
        return bulk_download_warrant_info(items, is_gt)
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
                bulk_process_warrant_info(stock['stock_symbol__symbol'])
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise
    finally:
        job.save()
        
def _has_css_class(css_class):
    return css_class == 'even' or css_class == "odd"

def bulk_process_warrant_info(stock_symbol, is_gt=False): 
    if is_gt:
        stock_item = Gt_Stock_Item.objects.get_by_symbol(stock_symbol)
        filename = "%s/bulk_warrant_info_%s" % (GT_DOWNLOAD_3, stock_symbol)
    else:
        stock_item = Stock_Item.objects.get_by_symbol(stock_symbol)
        filename = "%s/bulk_warrant_info_%s" % (TWSE_DOWNLOAD_3, stock_symbol)
# 
    with codecs.open(filename, 'r', encoding="utf8") as fd:              
        soup = BeautifulSoup(fd, 'lxml')
        tr_element_list = soup.find_all('tr', class_=_has_css_class)
        if len(tr_element_list) == 0: 
            logger.warning("No warrant data in %s" % filename)
            return
        i = 0
        i_processed = 0
        for tr_element in tr_element_list:
            # python doesn't have breaking outer loop syntax, so need to put the inner loop code into a separate function
            result = _process_td_elements(tr_element, stock_item, is_gt)
            if result:  
                i_processed += 1              
            i += 1
        logger.warning("Total %s tr elements" % i)
        logger.warning("Total %s warrant data processed" % i_processed)
        return True
    
def _process_td_elements(tr_element, stock_item, is_gt=False): 
    i = 0
    warrant_item = None
    for td_element in tr_element.find_all('td', recursive=False):
        warrant_data = td_element.string.strip()
        # print warrant_data
        if i == 0:
            if is_gt:
                warrant_item, created = Gt_Warrant_Item.objects.get_or_create(symbol=warrant_data)
            else:
                warrant_item, created = Warrant_Item.objects.get_or_create(symbol=warrant_data)
#
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
                    stock.save()
                    logger.info("ETF stock info %s is updated" % symbol.encode(encoding='utf-8'))
                except Stock_Item.DoesNotExist:
                    logger.warning("ETF symbol %s not found" % symbol.encode(encoding='utf-8'))
            job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed() 
        raise 
    finally:
        job.save()
#
def twse_daily_trading_job(qdate=None, process_stock_only=False):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_trading_job.__name__  
    try:
        if not qdate: 
            qdate = datetime.datetime.now().date()
        qdate_str = qdate.strftime("%Y/%m/%d")
        # check if processed
        if Twse_Trading_Processed.objects.check_processed(qdate):
            job.error_message = 'Trading data for date %s have already been processed.' % qdate_str
            raise Exception(job.error_message)
        if _get_day_trading(qdate_str):
            # call processing here
            if _process_day_trading(qdate_str, process_stock_only):
                Twse_Trading_Processed.objects.create(trading_date=qdate)
            else:
                job.error_message = 'Trading data for date %s have problems when processing.' % qdate_str
                raise Exception(job.error_message)
        else:
            job.error_message = 'Trading data for date %s have problems when downloading.' % qdate_str
            raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
            
def _get_day_trading(qdate_str):
    logger.info("downloading twse trading data...")
    datarow_count = 0 
    # used to flag if data is available (if count >0)
    serviceUrl = TWSE_TRADING_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_str_roc = western_to_roc_year(qdate_str)
    parameters = {'input_date': qdate_str_roc,
                  'select2':'ALL',
                  'sorting':'by_stkno',
                  'login_btn':''}
    try:        
        httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
        httpResponse.encoding = "big5"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/trading_%s" % (TWSE_DOWNLOAD_1, re.sub('/', '', qdate_str))
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
    if(datarow_count <= 1):
        logger.warning("No trading data available yet")
        os.remove(filename)
        os.remove(filename2)
        return False
    else:
        logger.info("There are %s trading records in file" % (datarow_count - 1))
        return True
    
def _process_day_trading(qdate_str, process_stock_only=False):
    logger.info("processing twse trading data...")
    filename = "%s/trading_%s_datarow" % (TWSE_DOWNLOAD_1, re.sub('/', '', qdate_str))
    trading_items_to_save = []
    trading_warrant_items_to_save = []
    record_stored = 0
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr', class_='basic2')
        logger.info("Reading %s trading records in file" % (len(rows) - 1))
        for row in rows[1:]:
            i = 0
            dt_item = None
            for td_element in row.find_all('td', recursive=False):
                dt_data = td_element.string.strip()
                if i == 0:
                    if check_if_warrant_item(dt_data):
                        if process_stock_only: break
                        warrant_item, created = Warrant_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Twse_Trading_Warrant()
                        trading_warrant_items_to_save.append(dt_item)
                        dt_item.warrant_symbol = warrant_item
                    else:                  
                        stock_item, created = Stock_Item.objects.get_or_create(symbol=dt_data)
                        dt_item = Twse_Trading()
                        trading_items_to_save.append(dt_item)
                        dt_item.stock_symbol = stock_item
                    dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')
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
            if i > 0: record_stored += 1
    count1 = len(trading_warrant_items_to_save)
    count2 = len(trading_items_to_save) 
    if  count1 > 0: Twse_Trading_Warrant.objects.bulk_create(trading_warrant_items_to_save)
    if  count2 > 0: Twse_Trading.objects.bulk_create(trading_items_to_save)
    logger.info("There are %s trading records processed ( %s warrant items, %s stock items)" % (record_stored, count1, count2))
    return True
#
def twse_daily_summary_price_job(qdate=None, process_stock_only=False):
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_daily_summary_price_job.__name__  
    try:
        if not qdate: 
            qdate = datetime.datetime.now().date()
        qdate_str = qdate.strftime("%Y/%m/%d")
        # check if processed
        if Twse_Summary_Price_Processed.objects.check_processed(qdate):
            job.error_message = 'Summary and price data for date %s have already been processed.' % qdate_str
            raise Exception(job.error_message)
        # for any specific date, the twse_daily_trading_job need to be run first
        # so check if above mentioned job has been done
        if not Twse_Trading_Processed.objects.check_processed(qdate):
            job.error_message = "Trading data need to be processed before summary/price data"
            raise Exception(job.error_message)
        else:
            if _get_summary_and_price(qdate_str):
                # processing 
                if (_process_price(qdate_str, process_stock_only) and 
                _process_index(qdate_str) and 
                _process_tri_index(qdate_str) and 
                _process_summary(qdate_str) and 
                _process_updown_stats(qdate_str)):
                    Twse_Summary_Price_Processed.objects.create(trading_date=qdate)
                else:
                    job.error_message = 'Summary and price data for date %s have problems when processing.' % qdate_str
                    raise Exception(job.error_message)
            else:
                job.error_message = 'Summary and price data for date %s have problems when downloading.' % qdate_str
                raise Exception(job.error_message)
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
        
def _get_summary_and_price(qdate_str):
    logger.info("downloading twse summary and price data...")
    # below are used to flag if data is available (if count >0)
    datarow_count_1a = 0 
    datarow_count_1b = 0 
    datarow_count_1c = 0 
    datarow_count_1d = 0 
    datarow_count2 = 0 
#
    serviceUrl = TWSE_PRICE_DOWNLOAD_URL
    # need to call the TWSE using ROC year, so transform qdate to roc year
    qdate_str_roc = western_to_roc_year(qdate_str)
    parameters = {'qdate': qdate_str_roc,
                  'selectType':'ALL',
                  'download':''}
    try:        
        httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
        httpResponse.encoding = "utf-8"
    except requests.HTTPError, e:
        result = e.read()
        raise Exception(result)
    filename = "%s/price_%s" % (TWSE_DOWNLOAD_0, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'wb', encoding="utf8") as fd:
        for chunk in httpResponse.iter_content(chunk_size=1000, decode_unicode=True):
            fd.write(chunk)            
    filename1a = "%s/twse_index_%s" % (TWSE_DOWNLOAD_A, re.sub('/', '', qdate_str))
    filename1b = "%s/twse_total_return_index_%s" % (TWSE_DOWNLOAD_B, re.sub('/', '', qdate_str))
    filename1c = "%s/market_summary_%s" % (TWSE_DOWNLOAD_C, re.sub('/', '', qdate_str))
    filename1d = "%s/market_up_down_stats_%s" % (TWSE_DOWNLOAD_D, re.sub('/', '', qdate_str))
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
        logger.info("%s price records downloaded" % (datarow_count2 - 2))
    if(datarow_count_1a == 0 or datarow_count_1b == 0 or datarow_count_1c == 0 or datarow_count_1d == 0 or datarow_count2 == 0):
        logger.warning("Summary or price data are not available yet")
        os.remove(filename)
        os.remove(filename1a)
        os.remove(filename1b)
        os.remove(filename1c)
        os.remove(filename1d)
        os.remove(filename2)
        return False
    else:
        logger.info("Finish downloading summary and price records")
        return True
    
def _process_price(qdate_str, process_stock_only=False):
    logger.info("processing twse price data...")
    filename = "%s/price_%s_datarow" % (TWSE_DOWNLOAD_0, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s price records in file" % (len(rows) - 2))
        record_stored = 0
        stock_count = 0
        warrant_count = 0
        strategy_objects_to_save = []
        # skip two rows
        for row in rows[2:]:
            up_or_down = 0
            dt_item = None
            created = False
            symbol = None
            for i, td_element in enumerate(row.find_all('td', recursive=False)):
                if td_element.string == None:
                    # td_element contains no text or ontains more than 1 child tags
                    # in any case skip processing it. 
                    continue
                else:
                    dt_data = td_element.string.strip()
                if i == 0:                                        
                    symbol = dt_data
                elif i == 2:
                    # if there is no trade volume --> no need to store this price record.
                    # therefore delay creation of model objects until we are sure there is volume data.
                    trade_volume = int(dt_data.replace(',', '')) 
                    if trade_volume == 0 : break
                    # create model objects
                    if check_if_warrant_item(symbol):
                        if process_stock_only: break
                        warrant_item, created = Warrant_Item.objects.get_or_create(symbol=symbol)
                        dt_item, created = Twse_Trading_Warrant.objects.get_or_create(warrant_symbol=warrant_item, trading_date=dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d'))
                        warrant_count += 1
                    else:                  
                        stock_item, created = Stock_Item.objects.get_or_create(symbol=symbol)
                        dt_item, created = Twse_Trading.objects.get_or_create(stock_symbol=stock_item, trading_date=dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d'))  
                        stock_count += 1
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

            if dt_item: 
                # remove the item if closing_price is 0 
                # -->means only has transactions of trade volume less than 1000.
                if dt_item.closing_price == 0:
                    dt_item.delete()
                    logger.info("Trading item of symbol %s is removed because there is no closing_price info" % symbol)
                    continue                   
                dt_item.save()
                # create a Twse_Trading_Strategy object if item is type Twse_Trading
                if dt_item.__class__.__name__ == "Twse_Trading":
                    tts = Twse_Trading_Strategy()
                    tts.trading = dt_item
                    tts.trading_date = dt_item.trading_date
                    tts.stock_symbol_id = dt_item.stock_symbol_id
                    strategy_objects_to_save.append(tts)     
#         
                record_stored += 1
        if len(strategy_objects_to_save) > 0 : Twse_Trading_Strategy.objects.bulk_create(strategy_objects_to_save)
        logger.info("There are %s price records processed ( %s warrant items, %s stock items)" % (record_stored, warrant_count, stock_count))
    return True
       
def _process_index(qdate_str):
    logger.info("processing twse index data...")
    filename = "%s/twse_index_%s" % (TWSE_DOWNLOAD_A, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s index records in file." % len(rows))
        record_stored = 0
        for row in rows:
            up_or_down = 0
            dt_item = None
            for i, td_element in enumerate(row.find_all('td', recursive=False)):
                if td_element.string == None:
                    # td_element contains no text or ontains more than 1 child tags
                    # in any case skip processing it. 
                    continue
                else:
                    dt_data = td_element.string.strip()
            
                if i == 0:
                    # create model objects
                    index_item, created = Index_Item.objects.get_or_create(name=dt_data)
                    dt_item = Index_Change_Info()
                    dt_item.twse_index = index_item
                    dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')             
                elif i == 1: 
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.closing_price = float(temp_data)                
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
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s index records processed." % record_stored)
    return True
       
def _process_tri_index(qdate_str):
    logger.info("processing twse total return index data...")
    filename = "%s/twse_total_return_index_%s" % (TWSE_DOWNLOAD_B, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s tri index records in file." % len(rows))
        record_stored = 0
        for row in rows:
            up_or_down = 0
            dt_item = None
            for i, td_element in enumerate(row.find_all('td', recursive=False)):
                if td_element.string == None:
                    # td_element contains no text or ontains more than 1 child tags
                    # in any case skip processing it. 
                    continue
                else:
                    dt_data = td_element.string.strip()
                if i == 0:
                    # create model objects
                    index_item, created = Index_Item.objects.get_or_create(name=dt_data, is_total_return_index=True)
                    dt_item = Index_Change_Info()
                    dt_item.twse_index = index_item
                    dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')  
                elif i == 1: 
                    temp_data = dt_data.replace(',', '')
                    if is_float(temp_data): 
                        dt_item.closing_price = float(temp_data)                       
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
            if dt_item: 
                dt_item.save()
                record_stored += 1
        logger.info("There are %s tri index records processed." % record_stored)
    return True
        
def _process_summary(qdate_str):    
    logger.info("processing twse market summary data...")
    filename = "%s/market_summary_%s" % (TWSE_DOWNLOAD_C, re.sub('/', '', qdate_str))
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
        
def _process_updown_stats(qdate_str):
    logger.info("processing twse up/down stats data...")
    filename = "%s/market_up_down_stats_%s" % (TWSE_DOWNLOAD_D, re.sub('/', '', qdate_str))
    with codecs.open(filename, 'r', encoding="utf8") as fd:
        soup = BeautifulSoup(fd, 'lxml')
        rows = soup.find_all('tr')
        logger.info("There are %s up_down_stats records in file." % len(rows))
        #
        dt_item = Stock_Up_Down_Stats()
        dt_item.trading_date = dateutil.convertToDate(qdate_str, date_format='%Y/%m/%d')  
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
    logger.info("Twse up/down stats data processed...")
    return True

def check_up_or_down(data):
    if data == u'＋': return 1
    elif data == u'－': return -1
    else: return 0
    
def _split_string(s_data):
    pos = s_data.find('(')
    part1 = s_data[:pos]
    part2 = s_data[pos + 1:len(s_data) - 1]
    return (part1, part2)

def test_calc_black_scholes():
    exercise_ratio = 1.0
    spot_price = 58
    strike_price = 58
    INTEREST_RATE = 0.0136
    time_to_maturity = 0.25
    option_price = 3.7
    sigma = option_price_implied_volatility_call_black_scholes_newton(spot_price, strike_price, INTEREST_RATE, time_to_maturity,
                                                              option_price)
    delta = option_price_delta_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity) 
    warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity)
    #
    logger.info(" spot_price = %s, strike_price= %s, option_price= %s" % (spot_price, strike_price, option_price * exercise_ratio))
    logger.info(" time_to_maturity= %s" % time_to_maturity)
    logger.info(" intrinsic volatility= %s, delta= %s" % (sigma, delta * exercise_ratio))
    logger.info(" warrant price= %s" % (warrant_price * exercise_ratio))
    
    warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma - 0.01, time_to_maturity)
    logger.info(" warrant price(IV-1%%)= %s" % (warrant_price * exercise_ratio))
    warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma + 0.01, time_to_maturity)
    logger.info(" warrant price(IV+1%%)= %s" % (warrant_price * exercise_ratio))
    warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma + 0.02, time_to_maturity)
    logger.info(" warrant price(IV+2%%)= %s" % (warrant_price * exercise_ratio))
    warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma + 0.03, time_to_maturity)
    logger.info(" warrant price(IV+3%%)= %s" % (warrant_price * exercise_ratio))

def test_black_scholes_job(warrant_symbol, qdate, use_closing_price=False):
    # get the warrant_item and trading_warrant and target_stock model instances
    try:
        warrant_item = Warrant_Item.objects.select_related('target_stock').get(symbol=warrant_symbol)
        trading_warrant_item = Twse_Trading_Warrant.objects.get(warrant_symbol=warrant_item, trading_date=qdate)
        trading_item = Twse_Trading.objects.get(stock_symbol=warrant_item.target_stock, trading_date=qdate)
        # or use closing_price
        exercise_ratio = warrant_item.exercise_ratio * 1.0 / 1000.0
        spot_price = float(trading_item.last_best_bid_price)
        if use_closing_price:        
            spot_price = float(trading_item.closing_price)
        strike_price = float(warrant_item.strike_price)
        INTEREST_RATE = 0.0136
        expiration_date = warrant_item.expiration_date
        diff = expiration_date - qdate 
        time_to_maturity = float(diff.days) / 365.0
        # or use closing_price
        option_price = float(trading_warrant_item.last_best_bid_price) / exercise_ratio
        if use_closing_price:        
            option_price = float(trading_warrant_item.closing_price) / exercise_ratio
            
        if warrant_item.is_call():
            sigma = option_price_implied_volatility_call_black_scholes_newton(spot_price, strike_price, INTEREST_RATE, time_to_maturity,
                                                              option_price)
            delta = option_price_delta_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity) 
            warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity)
        else:
            sigma = option_price_implied_volatility_put_black_scholes_newton(spot_price, strike_price, INTEREST_RATE, time_to_maturity,
                                                              option_price)
            delta = option_price_delta_put_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity) 
            warrant_price = option_price_put_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity)
        gearing = spot_price / option_price
        leverage = gearing * delta
        logger.info("Warrant item %s: spot_price = %s, strike_price= %s, option_price= %s" % (warrant_symbol, spot_price, strike_price, option_price * exercise_ratio))
        logger.info("Warrant item %s: expiration_date = %s, time_to_maturity= %s" % (warrant_symbol, expiration_date, time_to_maturity))
        logger.info("Warrant item %s: intrinsic volatility= %s, delta= %s" % (warrant_symbol, sigma, delta * exercise_ratio))
        logger.info("Warrant item %s: warrant price= %s" % (warrant_symbol, warrant_price * exercise_ratio))
        logger.info("Warrant item %s: gearing= %s, leverage= %s" % (warrant_symbol, gearing, leverage))
    except ObjectDoesNotExist:
        logger.warning("Warrant symbol %s not found" % warrant_symbol)
        raise
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        raise

def twse_trading_post_processing_job():
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_trading_post_processing_job.__name__  
    try:
        # first get all the dates of trading_warrant entries which have missing target trading
        date_list = Twse_Trading_Warrant.objects.get_date_with_missing_target_trading_info()
        # loop over the date list 
        for a_date in date_list:
            print a_date 
            # get trading_warrant entries for the date
            trading_warrant_list = Twse_Trading_Warrant.objects.no_target_trading_info(a_date)
            # get all the trading entries for the date and put into a dictionary with stock_symbol_id as key, trading pk(id) as the value
            trading_dict = to_dict(Twse_Trading.objects.by_date(a_date).values_list('stock_symbol_id', 'id'))
            # loop over trading warrant entries
            for item in trading_warrant_list:
                warrant_item = item.warrant_symbol
                if warrant_item.target_stock != None:
                    item.target_stock_symbol_id = warrant_item.target_stock_id
                    # some trading_warrant entries may not have corresponding stock trading entry (eg. IX0001)
                    item.target_stock_trading_id = trading_dict.get(item.target_stock_symbol_id, None)
                    item.save()  
                else: 
                    logger.warning("No target_stock info available for warrant item: %s" % warrant_item.symbol)       
            transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)

def twse_black_scholes_calc_job():
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = twse_black_scholes_calc_job.__name__  
    try:
        # first get all the dates of trading_warrant entries which have missing bs data
        date_list = Twse_Trading_Warrant.objects.get_date_with_missing_bs_info()
        # loop over the date list 
        for a_date in date_list:
            print a_date 
            # get trading_warrant entries for the date
            trading_warrant_list = Twse_Trading_Warrant.objects.no_bs_info(a_date)
            # loop over trading warrant entries
            for trading_warrant_entry in trading_warrant_list:
                warrant_item = trading_warrant_entry.warrant_symbol
                stock_trading_entry = trading_warrant_entry.target_stock_trading
                if stock_trading_entry != None: 
                    # some trading_warrant entries may not have corresponding stock trading entry (eg. IX0001)
                    try:
                        # calc moneyness (not related to BS algorithm)
                        spot_price = float(stock_trading_entry.closing_price)
                        strike_price = float(warrant_item.strike_price)
                        moneyness = (spot_price - strike_price) / strike_price
                        if warrant_item.is_put():
                            moneyness = -1.0 * moneyness
                        trading_warrant_entry.moneyness = moneyness
                        time_to_maturity, implied_volatility, delta, leverage, calc_warrant_price = _calc_bs_value(trading_warrant_entry, warrant_item, stock_trading_entry)
                    except:
                        # any exception may raise, but keep the loop going
                        logger.warning("Error when calculating BS values for trading_warrant_entry: ( id=%s )" % trading_warrant_entry.id)
                        trading_warrant_entry.not_converged = True
                        trading_warrant_entry.save()  
                        continue
                    trading_warrant_entry.time_to_maturity = time_to_maturity
                    trading_warrant_entry.implied_volatility = implied_volatility
                    trading_warrant_entry.delta = delta
                    trading_warrant_entry.leverage = leverage
                    trading_warrant_entry.calc_warrant_price = calc_warrant_price
                    trading_warrant_entry.save()  
            transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)

def _calc_bs_value(trading_warrant_entry, warrant_item, stock_trading_entry):
    logger.info("***Processing trading warrant : %s" % trading_warrant_entry.id)
    exercise_ratio = warrant_item.exercise_ratio * 1.0 / 1000.0
    spot_price = float(stock_trading_entry.last_best_bid_price)
    # default use last_best_bid_price for bs calculation, if not available then use closing_price
    if spot_price <= 0.0:        
        spot_price = float(stock_trading_entry.closing_price)
    if spot_price <= 0.0:
        raise Exception("Spot price is %s" % spot_price)
#
    strike_price = float(warrant_item.strike_price)
    INTEREST_RATE = 0.0136
    diff = warrant_item.expiration_date - trading_warrant_entry.trading_date 
    time_to_maturity = float(diff.days) / 365.0
    option_price = float(trading_warrant_entry.last_best_bid_price) / exercise_ratio
    # default use last_best_bid_price for bs calculation, if not available then use closing_price
    if option_price <= 0.0:        
        option_price = float(trading_warrant_entry.closing_price) / exercise_ratio
    if option_price <= 0.0:
        raise Exception("Warrant price is %s" % option_price)
#
    logger.info("exercise_ratio=%s, spot_price=%s,  strike_price=%s, diff=%s, time_to_maturity=%s, warrant_price=%s" % (exercise_ratio, spot_price, strike_price, diff, time_to_maturity, option_price))
    if warrant_item.is_call():
        sigma = option_price_implied_volatility_call_black_scholes_newton(
                              spot_price, strike_price, INTEREST_RATE, time_to_maturity, option_price)
        delta = option_price_delta_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity) 
        calc_warrant_price = option_price_call_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity)
    else:
        sigma = option_price_implied_volatility_put_black_scholes_newton(
                              spot_price, strike_price, INTEREST_RATE, time_to_maturity, option_price)
        delta = option_price_delta_put_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity) 
        calc_warrant_price = option_price_put_black_scholes(spot_price, strike_price, INTEREST_RATE, sigma, time_to_maturity)
    leverage = (spot_price / option_price) * delta
    
    logger.info("sigma=%s, delta=%s, leverage=%s, calc_warrant_price=%s" % (sigma, delta, leverage, calc_warrant_price * exercise_ratio))
#  
    return (time_to_maturity, sigma, delta, leverage, calc_warrant_price * exercise_ratio)
    
    
def update_moneyness_job(): 
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = update_moneyness_job.__name__  
    try:
        trading_date_list = Twse_Trading_Warrant.objects.filter(moneyness__isnull=True).distinct().values_list('trading_date', flat=True)
        for trading_date in trading_date_list:
            print trading_date
            trading_warrant_list = Twse_Trading_Warrant.objects.filter(trading_date=trading_date).select_related('warrant_symbol', 'target_stock_trading')
            # loop over trading warrant entries
            for trading_warrant_entry in trading_warrant_list:
                warrant_item = trading_warrant_entry.warrant_symbol
                stock_trading_entry = trading_warrant_entry.target_stock_trading
                if stock_trading_entry != None: 
                    # some trading_warrant entries may not have corresponding stock trading entry (eg. IX0001)
                    # calc moneyness (not related to BS algorithm)
                    spot_price = float(stock_trading_entry.closing_price)
                    strike_price = float(warrant_item.strike_price)
                    moneyness = (spot_price - strike_price) / strike_price
                    if warrant_item.is_put():
                        moneyness = -1.0 * moneyness
                    trading_warrant_entry.moneyness = moneyness
                    trading_warrant_entry.save()  
            transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)

def update_expired_warrant_trading_list(): 
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = update_expired_warrant_trading_list.__name__  
    try:
        warrant_list = Warrant_Item.objects.expired_trading_list_not_set()
        for warrant in warrant_list:
            trading_id_list = warrant.twse_trading_warrant_list.all().order_by('trading_date').values_list('id', flat=True)
            if len(trading_id_list) == 0: continue
            trading_id_list_str = ",".join([str(id) for id in trading_id_list])
            warrant.trading_list = trading_id_list_str
            warrant.save()  
        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)


def strategy_by_stochastic_pop_drop_job(): 
    transaction.set_autocommit(False)
    log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = strategy_by_stochastic_pop_drop_job.__name__  
    try:
        tod=datetime.datetime.today().date()
        #parameters:
        INSPECT_LATEST_DATA=True
        # trading date range to inspect the k/d, adx values
        TRADING_DATE_RANGE=3
        # long k threshold
        BULL_LONG_K_LEVEL=50
        BULL_SHORT_K_LEVEL=80
        BEAR_LONG_K_LEVEL=50
        BEAR_SHORT_K_LEVEL=20
        ADX_LEVEL=20
        #
        long_breakout_list=[]
        short_breakout_list=[]
        long_breakout2_list=[]
        short_breakout2_list=[]
        long_breakout3_list=[]
        short_breakout3_list=[]
        long_watch_list=[]
        short_watch_list=[]
        #
        stock_items = Stock_Item.objects.all()
        # calculate target trading date
        if INSPECT_LATEST_DATA:
            target_td = Trading_Date.objects.all().values_list('trading_date', flat=True).order_by('-trading_date')[TRADING_DATE_RANGE-1]
            print "Run the selection at %s" % tod
        else:
            TARGET_TRADING_DATE='20150415'
            ttd=convertToDate(TARGET_TRADING_DATE)
            target_td = Trading_Date.objects.filter(trading_date__lte=ttd).values_list('trading_date', flat=True).order_by('-trading_date')[TRADING_DATE_RANGE-1]
            print "Run the selection for %s" % TARGET_TRADING_DATE
            
        for stock in stock_items: 
            # first make sure the stocks have trading entries with non null strategy.fourteen_day_k, strategy.seventy_day_k, strategy.adx values within the trading date range
            trading_entries = stock.twse_trading_list.filter(trading_date__gte=target_td, 
                                                             strategy__fourteen_day_k__isnull=False, 
                                                             strategy__seventy_day_k__isnull=False, 
                                                             strategy__adx__isnull=False).select_related('strategy').order_by('trading_date')
            if not INSPECT_LATEST_DATA: 
                trading_entries = trading_entries.filter(trading_date__lte=ttd)
            if len(trading_entries) != TRADING_DATE_RANGE: 
                continue 
            data_list = [(float(entry.strategy.seventy_day_k),
              float(entry.strategy.seventy_day_d),
              float(entry.strategy.fourteen_day_k),
            float(entry.strategy.fourteen_day_d),
            float(entry.strategy.pdi14),
            float(entry.strategy.ndi14), 
              float(entry.strategy.adx)) for entry in trading_entries]
            data_array=np.asarray(data_list)
            data_array_t= data_array.T
            selected=False
            if pre_filtering_bull(data_array_t, BULL_LONG_K_LEVEL, ADX_LEVEL):
                if breakout_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
                    long_breakout_list.append(stock)    
                    selected=True    
                elif breakout2_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
                    long_breakout2_list.append(stock)
                    selected=True    
                elif breakout3_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
                    long_breakout3_list.append(stock)
                    selected=True    
                elif watch_list_bull(data_array_t, BULL_SHORT_K_LEVEL):
                    long_watch_list.append(stock)
                    selected=True    
                if selected:
                    #check if there are 'call' warrants available for trading
                    stock.has_warrant=stock.warrant_item_list.call_list().filter(last_trading_date__gte=tod).exists()
            elif pre_filtering_bear(data_array_t, BEAR_LONG_K_LEVEL, ADX_LEVEL):
                if breakout_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
                    short_breakout_list.append(stock)
                    selected=True
                elif breakout2_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
                    short_breakout2_list.append(stock)
                    selected=True    
                elif breakout3_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
                    short_breakout3_list.append(stock)
                    selected=True    
                elif watch_list_bear(data_array_t, BEAR_SHORT_K_LEVEL):
                    short_watch_list.append(stock)
                    selected=True 
                if selected:
                    #check if there are 'put' warrants available for trading
                    stock.has_warrant=stock.warrant_item_list.put_list().filter(last_trading_date__gte=tod).exists()
            if selected:   
                stock.last_short_k=data_array[-1][2]
                stochastic_pop_drop_plot(stock_symbol=stock.symbol)
        print "Number of bull breakout target: %s" % len(long_breakout_list)
        for stock in long_breakout_list:
            print "Found a breakout bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
        
        print "Number of bull breakout 2nd day target: %s" % len(long_breakout2_list)
        for stock in long_breakout2_list:
            print "Found a breakout 2nd day bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
            
        print "Number of bull breakout 3rd day target: %s" % len(long_breakout3_list)
        for stock in long_breakout3_list:
            print "Found a breakout 3rd day bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
            
        print "Number of bull watch target: %s" % len(long_watch_list)
        for stock in long_watch_list:
            print "Found a watch bull: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
        print "============================================================="  
        print "Number of bear breakout target: %s" % len(short_breakout_list)
        for stock in short_breakout_list:
            print "Found a breakout bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
           
        print "Number of bear breakout 2nd day target: %s" % len(short_breakout2_list)
        for stock in short_breakout2_list:
            print "Found a breakout 2nd day bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
            
        print "Number of bear breakout 3rd day target: %s" % len(short_breakout3_list)
        for stock in short_breakout3_list:
            print "Found a breakout 3rd day bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
            
        print "Number of bear watch target: %s" % len(short_watch_list)
        for stock in short_watch_list:
            print "Found a watch bear: stock symbol = %s(%s,short_k=%s), has_warrant=%s" % (stock.symbol, stock.short_name, stock.last_short_k, stock.has_warrant)
        

        transaction.commit()
        job.success()
    except: 
        print traceback.format_exc()
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        transaction.rollback()
        job.failed()
        raise
    finally:
        job.save()
        transaction.commit()
        transaction.set_autocommit(True)
