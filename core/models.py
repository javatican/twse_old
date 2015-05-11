# coding=utf8
import datetime
from django.db import models
from django.db.models.aggregates import Max
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from matplotlib.dates import date2num


class Cron_Job_Log(Model):
    STATUS_CHOICES = (
        ('1', _('cron_job_success')),
        ('2', _('cron_job_failed')),)
    title = models.CharField(max_length=48, default='', verbose_name=_('cron_job_title'))
    exec_time = models.DateTimeField(auto_now_add=True, verbose_name=_('cron_job_exec_time'))       
    status_code = models.CharField(default='1', max_length=1, choices=STATUS_CHOICES, verbose_name=_('cron_job_status'))
    error_message = models.CharField(max_length=120, default='', verbose_name=_('cron_job_error_message'))
    
    def success(self):
        self.status_code = '1'
    def failed(self):
        self.status_code = '2'
        
class TradingDateMixin(object):
    def since_which_date(self, qdate): 
        return self.filter(trading_date__gte=qdate)
    def between_dates(self, start_date, end_date): 
        return self.filter(trading_date__gte=start_date, trading_date__lte=end_date)
    
class TradingDateQuerySet(QuerySet, TradingDateMixin):
    pass

class TradingDateManager(models.Manager, TradingDateMixin):
    def get_queryset(self):
        return TradingDateQuerySet(self.model, using=self._db)
    def get_last_trading_date(self):
        data = self.all().aggregate(Max('trading_date'))
        return data['trading_date__max']

    
class Trading_Date(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, unique=True, verbose_name=_('trading_date')) 
    day_of_week = models.PositiveIntegerField(default=9, verbose_name=_('day_of_week'))
    is_future_delivery_day = models.BooleanField(default=False, verbose_name=_('is_future_delivery_day')) 
    first_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('first_trading_day_of_month')) 
    last_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('last_trading_day_of_month')) 
    is_market_closed = models.BooleanField(default=False, verbose_name=_('is_market_closed')) 
    
    objects = TradingDateManager()
           
class StockItemMixin(object):
    def data_not_ok(self): 
        return self.filter(data_ok=False)
    
class StockItemQuerySet(QuerySet, StockItemMixin):
    pass

class StockItemManager(models.Manager, StockItemMixin):
    def get_queryset(self):
        return StockItemQuerySet(self.model, using=self._db)
    def get_by_symbol(self, symbol):
        return self.get(symbol=symbol)

_TYPE_TWSE = '1'
_TYPE_GT = '2'
_TYPE_CHOICES = (
        (_TYPE_TWSE, u'上市'),
        (_TYPE_GT, u'上櫃'),)

def get_stock_item_type(type_name):
    if type_name == u'上市':
        return _TYPE_CHOICES[0][0]
    elif type_name == u'上櫃' or type_name == u'興櫃' or type_name == u'公開發行' :
        return _TYPE_CHOICES[1][0] 
    else:
        return None
    
def select_warrant_type_code(symbol):
    if symbol[0] == '0' and symbol[1] in ['3', '4', '5', '6', '7', '8']:
        return _TYPE_TWSE
    elif symbol[0] == '7' and symbol[1] in ['0', '1', '2', '3']:
        return _TYPE_GT
    else:
        return False    
    
class Stock_Item(Model):
    symbol = models.CharField(default='', max_length=10, verbose_name=_('stock_symbol'))
    short_name = models.CharField(default='', max_length=20, verbose_name=_('stock_short_name'))
    name = models.CharField(default='', max_length=100, verbose_name=_('stock_name'))
    type_code = models.CharField(max_length=1, default='1', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))
    market_category = models.CharField(default='', max_length=50, verbose_name=_('market_category'))
    notes = models.CharField(default='', max_length=100, verbose_name=_('notes'))
    data_ok = models.BooleanField(default=False, verbose_name=_('data_ok')) 
    is_etf = models.BooleanField(default=False, verbose_name=_('is_etf')) 
    etf_target = models.CharField(default='', max_length=100, verbose_name=_('etf_target'))

    objects = StockItemManager()
        
    def is_twse_stock(self): 
        return self.type_code == _TYPE_TWSE
    def is_gt_stock(self): 
        return self.type_code == _TYPE_GT 
    
class WarrantItemMixin(object):
    def data_not_ok(self):
        return self.filter(data_ok=False)
    def expired_trading_list_not_set(self):
        today = datetime.datetime.now().date()
        return self.filter(last_trading_date__lt=today, trading_list__isnull=True)
    def call_list(self):
        return self.filter(classification=_CALL)
    def put_list(self):
        return self.filter(classification=_PUT)
class WarrantItemQuerySet(QuerySet, WarrantItemMixin):
    pass

class WarrantItemManager(models.Manager, WarrantItemMixin):
    def get_queryset(self):
        return WarrantItemQuerySet(self.model, using=self._db)
    def stocks_has_warrants(self):
        return self.filter(data_ok=True).distinct().values_list('target_stock__symbol', flat=True)
    
_EXERCISE_STYLE_CHOICES = (
        ('1', u'歐式'),
        ('2', u'美式'),)

def get_warrant_exercise_style(exercise_style):
    if exercise_style == _EXERCISE_STYLE_CHOICES[0][1]:
        return _EXERCISE_STYLE_CHOICES[0][0]
    elif exercise_style == _EXERCISE_STYLE_CHOICES[1][1]:
        return _EXERCISE_STYLE_CHOICES[1][0]
    else:
        return None
    
_CALL = '1'
_PUT = '2' 

_CLASSIFICATION_CHOICES = (
        (_CALL, u'認購'),
        (_PUT, u'認售'),)
 
CLASSIFICATION_CODE = {'CALL':_CALL, 'PUT': _PUT}

def get_warrant_classification(classification):
    if classification == _CLASSIFICATION_CHOICES[0][1]:
        return _CLASSIFICATION_CHOICES[0][0]
    elif classification == _CLASSIFICATION_CHOICES[1][1]:
        return _CLASSIFICATION_CHOICES[1][0]
    else:
        return None
    
class Warrant_Item(Model):
    symbol = models.CharField(default='', max_length=10, verbose_name=_('warrant_symbol'))
    name = models.CharField(default='', max_length=20, verbose_name=_('warrant_name'))
    target_stock = models.ForeignKey("core.Stock_Item", null=True, related_name="warrant_item_list", verbose_name=_('target_stock'))
    target_symbol = models.CharField(default='', max_length=10, verbose_name=_('target_symbol'))
    exercise_style = models.CharField(max_length=1, default=1, choices=_EXERCISE_STYLE_CHOICES, verbose_name=_('exercise_style'))
    classification = models.CharField(max_length=1, default=1, choices=_CLASSIFICATION_CHOICES, verbose_name=_('classification'))
    issuer = models.CharField(default='', max_length=20, verbose_name=_('issuer'))
    listed_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('listed_date')) 
    last_trading_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('last_trading_date')) 
    expiration_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('expiration_date')) 
    issued_volume = models.PositiveIntegerField(default=0, verbose_name=_('issued_volume')) 
    exercise_ratio = models.PositiveIntegerField(default=0, verbose_name=_('exercise_ratio')) 
    strike_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('strike_price'))
    data_ok = models.BooleanField(default=False, verbose_name=_('data_ok')) 
    type_code = models.CharField(max_length=1, default='1', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))
    trading_list = models.TextField(null=True, verbose_name=_('trading_list'))

    objects = WarrantItemManager() 
    def is_call(self):
        return self.classification == CLASSIFICATION_CODE['CALL']
    def is_put(self):
        return self.classification == CLASSIFICATION_CODE['PUT']
    
    def is_twse_stock(self): 
        return self.type_code == _TYPE_TWSE
    def is_gt_stock(self): 
        return self.type_code == _TYPE_GT  
    
    def get_trading_warrant_list(self):
        if self.trading_list == None:
            return  self.twse_trading_warrant_list.all()
        else:
            trading_list_str = self.trading_list.split(',')
            return Twse_Trading_Warrant.objects.filter(id__in=trading_list_str)
class TwseTradingMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_symbol(self, symbol):
        return self.filter(stock_symbol=symbol)
    def by_date_and_symbol(self, trading_date, symbol):
        return self.filter(trading_date=trading_date, stock_symbol=symbol)
    def by_date_and_symbol_id(self, trading_date, symbol_id):
        return self.filter(trading_date=trading_date, stock_symbol_id=symbol_id)
    
    def lte_date(self, target_date):
        # used together with by_symbol() or RelatedManager 'twse_trading_list'
        return self.filter(trading_date__lte=target_date)
    def get_missing_avg(self):
        # used together with by_symbol() or RelatedManager 'twse_trading_list'
        return self.filter(week_avg__isnull=True)
        
class TwseTradingQuerySet(QuerySet, TwseTradingMixin):
    pass

class TwseTradingManager(models.Manager, TwseTradingMixin):
    def get_queryset(self):
        return TwseTradingQuerySet(self.model, using=self._db)

    def stocks_has_hedge_trade(self, type_code=True):
        if type_code:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0) | Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol', 'stock_symbol__type_code')
        else:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0) | Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol')
    
    def ohlc_between_dates(self, start_date, end_date, date_as_num=False):
        # this method should be used together with by_symbol() or RelatedManager 'twse_trading_list'
        # return list of tuples containing d, open, high, low, close, volume
        entries = self.filter(trading_date__gte=start_date, trading_date__lte=end_date)
        if date_as_num:
            result = [(date2num(entry.trading_date),
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_volume)) for entry in entries]
        else:
            result = [(entry.trading_date,
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_volume)) for entry in entries]
        return result

    def price_volume_lte_date(self, target_date):
        # used together with by_symbol() or RelatedManager 'twse_trading_list'
        return self.lte_date(target_date).values_list('closing_price', 'trade_volume')
    
    
class Twse_Trading(Model):
    stock_symbol = models.ForeignKey("core.Stock_Item", null=True, related_name="twse_trading_list", verbose_name=_('stock_symbol'))
    total_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('total_diff')) 
    fi_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_buy')) 
    fi_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_sell')) 
    fi_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_diff')) 
    sit_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_buy')) 
    sit_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_sell')) 
    sit_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_diff'))     
    proprietary_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_buy')) 
    proprietary_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_sell')) 
    proprietary_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_diff')) 
    hedge_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_buy')) 
    hedge_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_sell')) 
    hedge_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_diff')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
#
    trade_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trade_value = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    opening_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('opening_price'))
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('highest_price'))
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('lowest_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('closing_price'))
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price_change'))
    last_best_bid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_bid_price'))
    last_best_bid_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('last_best_bid_volume'))
    last_best_ask_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_ask_price'))
    last_best_ask_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('last_best_ask_volume'))
#
    week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('week_avg'))
    two_week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('two_week_avg'))
    month_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('month_avg'))
    quarter_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('quarter_avg'))
    half_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('half_avg'))
    year_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('year_avg'))
    year_volume_avg = models.DecimalField(max_digits=15, decimal_places=0, null=True, verbose_name=_('year_volume_avg'))


    objects = TwseTradingManager() 
#
    def notify_msg(self):
        s1= 'Previouis Trading data: (fi_buy,fi_sell,fi_diff = %s, %s, %s) \n' % (self.fi_buy, self.fi_sell, self.fi_diff)
        s2= '(sit_buy,sit_sell,sit_diff = %s, %s, %s) \n' % (self.sit_buy, self.sit_sell,  self.sit_diff)
        s3= '(prop_buy,prop_sell,prop_diff = %s, %s, %s) \n' % ( self.proprietary_buy, self.proprietary_sell, self.proprietary_diff)
        s4= '(hedge_buy,hedge_sell,hedge_diff = %s, %s, %s) \n' % (self.hedge_buy, self.hedge_sell, self.hedge_sell) 
        s5= '(trade_volume,opening_price,lowest_price,highest_price, closing_price, price_change = %s,%s,%s,%s,%s,%s) \n' % (self.trade_volume,self.opening_price,self.lowest_price,self.highest_price,self.closing_price,self.price_change)
        s6= '(year_volume_avg, week_avg, 2_week_avg, month_avg, quarter_avg, half_avg, year_avg= %s,%s,%s,%s,%s,%s,%s) \n' % (self.year_volume_avg, self.week_avg,self.two_week_avg,self.month_avg,self.quarter_avg,self.half_avg,self.year_avg)   
        return '%s %s %s %s %s %s' % (s1,s2,s3,s4,s5,s6)
    class Meta:
        unique_together = ("stock_symbol", "trading_date")
    # below method is required to return the 'strategy' instance, because it holds stochastic oscillator/ADX related strategy fields in it.
    def get_trading_strategy(self):
        return self.strategy
        
        
class TwseTradingStrategyMixin(object): 
    pass
class TwseTradingStrategyQuerySet(QuerySet, TwseTradingStrategyMixin):
    pass

class TwseTradingStrategyManager(models.Manager, TwseTradingStrategyMixin):
    def get_queryset(self):
        return TwseTradingStrategyQuerySet(self.model, using=self._db)

class Twse_Trading_Strategy(Model): 
    trading = models.OneToOneField(Twse_Trading, primary_key=True, related_name="strategy")
    stock_symbol = models.ForeignKey("core.Stock_Item", null=False, related_name="twse_trading_strat_list", verbose_name=_('stock_symbol'))
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    fourteen_day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('fourteen_day_k'))
    fourteen_day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('fourteen_day_d'))
    seventy_day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('seventy_day_k'))
    seventy_day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('seventy_day_d'))
    tr14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('tr14'))
    pdm14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('pdm14'))
    ndm14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('ndm14'))
    #
    pdi14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('pdi14'))
    ndi14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('ndi14'))
    adx = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('adx'))
#   
#   
    objects = TwseTradingStrategyManager() 
    def notify_msg(self):
        return  'Previous K/D and ADX: ks_70=%s, da_70=%s, ks_14=%s, da_14=%s, ADX=%s(pdi14=%s, ndi14=%s))' % (self.seventy_day_k,
                                                                                                                self.seventy_day_d,
                                                                                                                self.fourteen_day_k,
                                                                                                                self.fourteen_day_d,
                                                                                                                self.adx,
                                                                                                                self.pdi14,
                                                                                                                self.ndi14)             
class SelectionStrategyTypeMixin(object): 
    pass
class SelectionStrategyTypeQuerySet(QuerySet, SelectionStrategyTypeMixin):
    pass

class SelectionStrategyTypeManager(models.Manager, SelectionStrategyTypeMixin):
    def get_queryset(self):
        return SelectionStrategyTypeQuerySet(self.model, using=self._db)
    def get_by_symbol(self, symbol):
        return self.get(symbol=symbol)
    
class Selection_Strategy_Type(Model):
    symbol = models.CharField(default='', max_length=50, verbose_name=_('strategy_symbol'))
    name = models.CharField(default='', max_length=100, verbose_name=_('strategy_name'))
    is_bull = models.NullBooleanField(null=True, verbose_name=_('is_bull')) 
    objects = SelectionStrategyTypeManager() 
  
class SelectionStockItemMixin(object): 
    def by_trading_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def with_warrant(self):
        return self.filter(has_warrant=True)
    
class SelectionStockItemQuerySet(QuerySet, SelectionStockItemMixin):
    pass

class SelectionStockItemManager(models.Manager, SelectionStockItemMixin):
    def get_queryset(self):
        return SelectionStockItemQuerySet(self.model, using=self._db)

class Selection_Stock_Item(Model):
    strategy_type = models.ForeignKey("core.Selection_Strategy_Type", null=False, related_name="selection_list", verbose_name=_('strategy_type'))
    stock_symbol = models.ForeignKey("core.Stock_Item", null=False, related_name="selection_list2", verbose_name=_('stock_symbol'))
    trading = models.ForeignKey("core.Twse_Trading", null=False, related_name="selection_list3", verbose_name=_('trading'))
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    has_warrant = models.NullBooleanField(null=True, verbose_name=_('has_warrant')) 
    low_volume = models.NullBooleanField(null=True, verbose_name=_('low_volume')) 
    volume_change = models.DecimalField(max_digits=11, decimal_places=0, null=True, verbose_name=_('volume_change')) 
    performance_3day = models.DecimalField(max_digits=7, decimal_places=1, null=True, verbose_name=_('performance_3day')) 
    performance_5day = models.DecimalField(max_digits=7, decimal_places=1, null=True, verbose_name=_('performance_5day')) 
    performance_10day = models.DecimalField(max_digits=7, decimal_places=1, null=True, verbose_name=_('performance_10day')) 
    performance_20day = models.DecimalField(max_digits=7, decimal_places=1, null=True, verbose_name=_('performance_20day')) 
    objects = SelectionStockItemManager() 
    def notify_msg(self):
        return  'Selection data: strategy_type_symbol=%s, has_warrant=%s, low_volume=%s, volume_change_percent=%s' % (self.strategy_type.symbol,
                                                                                                                self.has_warrant,
                                                                                                                self.low_volume,
                                                                                                                self.volume_change) 
    def check_notify_msg(self, stock_quote, selection_strategy_class):
        stock_item=self.stock_symbol
        selection_strategy_obj=selection_strategy_class(stock_item=stock_item,
                                                        selection_stock_item=self, 
                                                        stock_quote=stock_quote, 
                                                        trading=self.trading, 
                                                        strategy_param=self.trading.strategy)
        return selection_strategy_obj.check_message()
       
            
class TwseTradingWarrantMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_warrant_symbol(self, symbol):
        return self.filter(warrant_symbol=symbol)
    def no_target_trading_info(self, trading_date):
        return self.filter(trading_date=trading_date, target_stock_trading__isnull=True).select_related('warrant_symbol')
    def no_bs_info(self, trading_date):
        return self.filter(trading_date=trading_date, time_to_maturity__isnull=True, not_converged__isnull=True).select_related('warrant_symbol', 'target_stock_trading')
        
class TwseTradingWarrantQuerySet(QuerySet, TwseTradingWarrantMixin):
    pass

class TwseTradingWarrantManager(models.Manager, TwseTradingWarrantMixin):
    def get_queryset(self):
        return TwseTradingWarrantQuerySet(self.model, using=self._db)
    def get_date_with_missing_bs_info(self):
        return self.filter(time_to_maturity__isnull=True, not_converged__isnull=True).distinct().values_list('trading_date', flat=True)
    def get_date_with_missing_target_trading_info(self):
        return self.filter(target_stock_trading__isnull=True).distinct().values_list('trading_date', flat=True)
    def get_trade_info_by_date(self, trading_date):
        return self.filter(trade_volume__isnull=False, trading_date=trading_date).values_list('trade_volume', 'trade_transaction', 'trade_value')
class Twse_Trading_Warrant(Model):
    warrant_symbol = models.ForeignKey("core.Warrant_Item", null=True, related_name="twse_trading_warrant_list", verbose_name=_('warrant_symbol'))
    target_stock_symbol = models.ForeignKey("core.Stock_Item", null=True, related_name="twse_trading_warrant_list2", verbose_name=_('target_stock_symbol'))
    target_stock_trading = models.ForeignKey("core.Twse_Trading", null=True, related_name="twse_trading_warrant_list3", verbose_name=_('target_stock_trading'))
    total_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('total_diff')) 
    fi_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_buy')) 
    fi_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_sell')) 
    fi_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('fi_diff')) 
    sit_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_buy')) 
    sit_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_sell')) 
    sit_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('sit_diff'))     
    proprietary_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_buy')) 
    proprietary_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_sell')) 
    proprietary_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('proprietary_diff')) 
    hedge_buy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_buy')) 
    hedge_sell = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_sell')) 
    hedge_diff = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('hedge_diff')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
#
    trade_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trade_value = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    opening_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('opening_price'))
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('highest_price'))
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('lowest_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('closing_price'))
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price_change'))
    last_best_bid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_bid_price'))
    last_best_bid_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('last_best_bid_volume'))
    last_best_ask_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_ask_price'))
    last_best_ask_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('last_best_ask_volume'))
# Black Scholes data
    time_to_maturity = models.DecimalField(max_digits=6, decimal_places=4, null=True, verbose_name=_('time_to_maturity')) 
    implied_volatility = models.DecimalField(max_digits=6, decimal_places=4, null=True, verbose_name=_('implied_volatility')) 
    delta = models.DecimalField(max_digits=7, decimal_places=4, null=True, verbose_name=_('delta')) 
    leverage = models.DecimalField(max_digits=7, decimal_places=2, null=True, verbose_name=_('leverage')) 
    calc_warrant_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, verbose_name=_('calc_warrant_price'))
    not_converged = models.NullBooleanField(null=True, verbose_name=_('not_converged'))  
# others
    moneyness = models.DecimalField(max_digits=9, decimal_places=3, null=True, verbose_name=_('moneyness')) 
    
    
    objects = TwseTradingWarrantManager() 
    #
    class Meta:
        unique_together = ("warrant_symbol", "trading_date")

class IndexItemMixin(object):
    def get_index_with_wearn_symbol(self):
        return self.filter(wearn_symbol__isnull=False)
    
class IndexItemQuerySet(QuerySet, IndexItemMixin):
    pass

class IndexItemManager(models.Manager, IndexItemMixin):
    def get_queryset(self):
        return IndexItemQuerySet(self.model, using=self._db)
    def get_by_name(self, name):
        return self.get(name=name)
    def get_by_tri_name(self, name):
        return self.get(name=name, is_total_return_index=True)
    def get_wearn_symbols(self):
        return self.filter(wearn_symbol__isnull=False).values_list('wearn_symbol', flat=True)
    
class Index_Item(Model):
    name = models.CharField(default='', max_length=100, verbose_name=_('index_name'))
    name_en = models.CharField(default='', max_length=100, verbose_name=_('index_name_en'))
    is_total_return_index = models.BooleanField(default=False, verbose_name=_('is_total_return_index'))  
    wearn_symbol = models.CharField(max_length=15, null=True, verbose_name=_('wearn_symbol'))
    
    objects = IndexItemManager()

class IndexChangeInfoMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_index(self, twse_index):
        return self.filter(twse_index=twse_index)
    def get_missing_avg(self):
        # used together with by_index() or RelatedManager 'index_change_list'
        return self.filter(week_avg__isnull=True)
    def lte_date(self, target_date):
        return self.filter(trading_date__lte=target_date)
        
class IndexChangeInfoQuerySet(QuerySet, IndexChangeInfoMixin):
    pass

class IndexChangeInfoManager(models.Manager, IndexChangeInfoMixin):
    def get_queryset(self):
        return IndexChangeInfoQuerySet(self.model, using=self._db)
    def get_last_trading_date_for_trade_value(self):
        data = self.filter(trade_value__isnull=False).aggregate(Max('trading_date'))
        return data['trading_date__max']
    def price_value_lte_date(self, target_date):
        # used together with by_index() or RelatedManager 'index_change_list'
        return self.lte_date(target_date).values_list('closing_price', 'trade_value')
    
class Index_Change_Info(Model):
    twse_index = models.ForeignKey("core.Index_Item", related_name="index_change_list", verbose_name=_('twse_index'))
    trade_value = models.DecimalField(max_digits=15, decimal_places=0, null=True, verbose_name=_('trade_value')) 
    opening_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('opening_price'))
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('highest_price'))
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('lowest_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('closing_price')) 
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('change')) 
    change_in_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name=_('change_in_percentage')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
#
    week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('week_avg'))
    two_week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('two_week_avg'))
    month_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('month_avg'))
    quarter_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('quarter_avg'))
    half_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('half_avg'))
    year_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('year_avg'))
    year_value_avg = models.DecimalField(max_digits=15, decimal_places=0, null=True, verbose_name=_('year_value_avg'))
#   
    fourteen_day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('fourteen_day_k'))
    fourteen_day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('fourteen_day_d'))
    seventy_day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('seventy_day_k'))
    seventy_day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('seventy_day_d'))
    tr14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('tr14'))
    pdm14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('pdm14'))
    ndm14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('ndm14'))
    #
    pdi14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('pdi14'))
    ndi14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('ndi14'))
    adx = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('adx'))
    
    objects = IndexChangeInfoManager()
#
    class Meta:
        unique_together = ("twse_index", "trading_date")
    # below method is required to return the instance itself, because it holds stochastic oscillator/ADX related strategy fields in its own model.
    def get_trading_strategy(self):
        return self
  
class MarketSummaryTypeMixin(object):
    pass
    
class MarketSummaryTypeQuerySet(QuerySet, MarketSummaryTypeMixin):
    pass

class MarketSummaryTypeManager(models.Manager, MarketSummaryTypeMixin):
    def get_queryset(self):
        return MarketSummaryTypeQuerySet(self.model, using=self._db)
    def get_by_name(self, name):
        return self.get(name=name)
    
class Market_Summary_Type(Model):
    name = models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name'))
    name_en = models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name_en'))

    objects = MarketSummaryTypeManager()
    
class MarketSummaryMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    
class MarketSummaryQuerySet(QuerySet, MarketSummaryMixin):
    pass

class MarketSummaryManager(models.Manager, MarketSummaryMixin):
    def get_queryset(self):
        return MarketSummaryQuerySet(self.model, using=self._db)
    
class Market_Summary(Model):
    summary_type = models.ForeignKey("core.Market_Summary_Type", related_name="summary_list", verbose_name=_('summary_type'))
    trade_value = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    trade_volume = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    
    objects = MarketSummaryManager()

    class Meta:
        unique_together = ("summary_type", "trading_date")
          
class StockUpDownStatsMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    
class StockUpDownStatsQuerySet(QuerySet, StockUpDownStatsMixin):
    pass

class StockUpDownStatsManager(models.Manager, StockUpDownStatsMixin):
    def get_queryset(self):
        return StockUpDownStatsQuerySet(self.model, using=self._db)
    
class Stock_Up_Down_Stats(Model):
    total_up = models.PositiveIntegerField(default=0, verbose_name=_('total_up')) 
    total_up_limit = models.PositiveIntegerField(default=0, verbose_name=_('total_up_limit')) 
    stock_up = models.PositiveIntegerField(default=0, verbose_name=_('stock_up')) 
    stock_up_limit = models.PositiveIntegerField(default=0, verbose_name=_('stock_up_limit')) 
    total_down = models.PositiveIntegerField(default=0, verbose_name=_('total_down')) 
    total_down_limit = models.PositiveIntegerField(default=0, verbose_name=_('total_down_limit')) 
    stock_down = models.PositiveIntegerField(default=0, verbose_name=_('stock_down')) 
    stock_down_limit = models.PositiveIntegerField(default=0, verbose_name=_('stock_down_limit')) 
    total_unchange = models.PositiveIntegerField(default=0, verbose_name=_('total_unchange')) 
    stock_unchange = models.PositiveIntegerField(default=0, verbose_name=_('stock_unchange')) 
    total_unmatch = models.PositiveIntegerField(default=0, verbose_name=_('total_unmatch')) 
    stock_unmatch = models.PositiveIntegerField(default=0, verbose_name=_('stock_unmatch')) 
    total_na = models.PositiveIntegerField(default=0, verbose_name=_('total_na')) 
    stock_na = models.PositiveIntegerField(default=0, verbose_name=_('stock_na'))  
    trading_date = models.DateField(auto_now_add=False, unique=True, null=False, verbose_name=_('trading_date')) 
    objects = StockUpDownStatsManager()
    
    
class TwseTradingProcessedMixin(object):
    pass
    
class TwseTradingProcessedQuerySet(QuerySet, TwseTradingProcessedMixin):
    pass

class TwseTradingProcessedManager(models.Manager, TwseTradingProcessedMixin):
    def get_queryset(self):
        return TwseTradingProcessedQuerySet(self.model, using=self._db)
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date).exists()
    def get_dates(self):
        return self.all().order_by('trading_date').values_list('trading_date', flat=True)
    def get_last_processed(self):
        return self.all().order_by('-trading_date').values_list('trading_date', flat=True)[0]
    
class Twse_Trading_Processed(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    objects = TwseTradingProcessedManager() 

class TwseSummaryPriceProcessedMixin(object):
    pass
 
class TwseSummaryPriceProcessedQuerySet(QuerySet, TwseSummaryPriceProcessedMixin):
    pass

class TwseSummaryPriceProcessedManager(models.Manager, TwseSummaryPriceProcessedMixin):
    def get_queryset(self):
        return TwseTradingProcessedQuerySet(self.model, using=self._db)
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date).exists()
    def get_last_processed(self):
        return self.all().order_by('-trading_date').values_list('trading_date', flat=True)[0]

class Twse_Summary_Price_Processed(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    objects = TwseSummaryPriceProcessedManager() 



class TwseIndexStatsMixin(object):
    def between_dates(self, start_date, end_date):
        return self.filter(trading_date__gte=start_date, trading_date__lte=start_date)
    def lte_date(self, target_date):
        return self.filter(trading_date__lte=target_date)
    def get_missing_avg(self):
        return self.filter(week_avg__isnull=True)
    
class TwseIndexStatsQuerySet(QuerySet, TwseIndexStatsMixin):
    pass

class TwseIndexStatsManager(models.Manager, TwseIndexStatsMixin):
    def get_queryset(self):
        return TwseIndexStatsQuerySet(self.model, using=self._db)
    def by_date(self, trading_date):
        return self.get(trading_date=trading_date)
    def ohlc_between_dates(self, start_date, end_date, date_as_num=False):
        # return list of tuples containing d, open, high, low, close, volume
        entries = self.filter(trading_date__gte=start_date, trading_date__lte=end_date)
        if date_as_num:
            result = [(date2num(entry.trading_date),
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_value)) for entry in entries]
        else:
            result = [(entry.trading_date,
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_value)) for entry in entries]
        return result
    
#     def get_dates_for_missing_avg(self):
#         return self.filter(week_avg__isnull=True).values_list('trading_date', flat=True)
    def price_value_lte_date(self, target_date):
        return self.lte_date(target_date).values_list('closing_price', 'trade_value')
    
class Twse_Index_Stats(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, unique=True, verbose_name=_('trading_date')) 
#
    trade_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trade_value = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    opening_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('opening_price'))
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('highest_price'))
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('lowest_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('closing_price'))
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price_change'))
#
    week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('week_avg'))
    two_week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('two_week_avg'))
    month_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('month_avg'))
    quarter_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('quarter_avg'))
    half_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('half_avg'))
    year_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('year_avg'))
    day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('day_k'))
    day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('day_d'))
    week_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('week_k'))
    week_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('week_d'))
    month_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('month_k'))
    month_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('month_d'))                                 
    year_value_avg = models.DecimalField(max_digits=15, decimal_places=0, null=True, verbose_name=_('year_value_avg'))
    
    objects = TwseIndexStatsManager() 
#
