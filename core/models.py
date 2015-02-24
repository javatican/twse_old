from django.db import models
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _


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
    pass
    
class TradingDateQuerySet(QuerySet, TradingDateMixin):
    pass

class TradingDateManager(models.Manager, TradingDateMixin):
    def get_queryset(self):
        return TradingDateQuerySet(self.model, using=self._db)
    
class Trading_Date(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    day_of_week = models.PositiveIntegerField(default=9, verbose_name=_('day_of_week'))
    is_future_delivery_day = models.BooleanField(default=False, verbose_name=_('is_future_delivery_day')) 
    first_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('first_trading_day_of_month')) 
    last_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('last_trading_day_of_month')) 
    is_market_closed = models.BooleanField(default=False, verbose_name=_('is_market_closed')) 
    
    objects= TradingDateManager()
           
class StockItemMixin(object):
    def need_to_process(self): 
        return self.filter(data_ok=False, data_downloaded=True, parsing_error=False)
    def data_not_yet_download(self):
        return self.filter(data_downloaded=False)
    
class StockItemQuerySet(QuerySet, StockItemMixin):
    pass

class StockItemManager(models.Manager, StockItemMixin):
    def get_queryset(self):
        return StockItemQuerySet(self.model, using=self._db)
    def get_by_symbol(self, symbol):
        return self.get(symbol=symbol)
    
_TYPE_CHOICES = (
        ('1', _('stock_type_1')),
        ('2', _('stock_type_2')),)

def get_stock_item_type(type_name):
    if type_name ==  _TYPE_CHOICES[0][1]:
        return _TYPE_CHOICES[0][0]
    elif type_name == _TYPE_CHOICES[1][1]:
        return _TYPE_CHOICES[1][0]
    else:
        return None
    
class Stock_Item(Model):
    symbol=models.CharField(default='', max_length=10, verbose_name=_('stock_symbol'))
    short_name=models.CharField(default='', max_length=20, verbose_name=_('stock_short_name'))
    name=models.CharField(default='', max_length=100, verbose_name=_('stock_name'))
    type_code = models.CharField(max_length=1, default='1', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))
    market_category=models.CharField(default='', max_length=50, verbose_name=_('market_category'))
    notes=models.CharField(default='', max_length=100, verbose_name=_('notes'))
    data_ok = models.BooleanField(default=False, verbose_name=_('data_ok')) 
    data_downloaded = models.BooleanField(default=False, verbose_name=_('data_downloaded')) 
    parsing_error = models.BooleanField(default=False, verbose_name=_('parsing_error')) 
    is_etf = models.BooleanField(default=False, verbose_name=_('is_etf')) 
    etf_target = models.CharField(default='', max_length=100, verbose_name=_('etf_target'))

    objects= StockItemManager()
        
    def is_stock_type_1(self): 
        return self.type_code == _TYPE_CHOICES[0][0]
    def is_stock_type_2(self): 
        return self.type_code == _TYPE_CHOICES[1][0]
    
class WarrantItemMixin(object):
    def need_to_process(self): 
        return self.filter(data_ok=False, data_downloaded=True, parsing_error=False)
    def data_not_yet_download(self):
        return self.filter(data_downloaded=False)
        
class WarrantItemQuerySet(QuerySet, WarrantItemMixin):
    pass

class WarrantItemManager(models.Manager, WarrantItemMixin):
    def get_queryset(self):
        return WarrantItemQuerySet(self.model, using=self._db)
    def stocks_has_warrants(self):
        return self.filter(data_ok=True).distinct().values_list('target_stock__symbol', flat=True)
    
_CALL = '1'
_PUT = '2' 
_EXERCISE_STYLE_CHOICES = (
        ('1', _('European')),
        ('2', _('American')),)
_CLASSIFICATION_CHOICES = (
        (_CALL, _('call')),
        (_PUT, _('put')),)
 
CLASSIFICATION_CODE = {'CALL':_CALL, 'PUT': _PUT}

def get_warrant_exercise_style(exercise_style):
    if exercise_style ==  _EXERCISE_STYLE_CHOICES[0][1]:
        return _EXERCISE_STYLE_CHOICES[0][0]
    elif exercise_style == _EXERCISE_STYLE_CHOICES[1][1]:
        return _EXERCISE_STYLE_CHOICES[1][0]
    else:
        return None
    
def get_warrant_classification(classification):
    if classification ==  _CLASSIFICATION_CHOICES[0][1]:
        return _CLASSIFICATION_CHOICES[0][0]
    elif classification == _CLASSIFICATION_CHOICES[1][1]:
        return _CLASSIFICATION_CHOICES[1][0]
    else:
        return None
    
def select_warrant_type_code(symbol):
    if symbol[0] == '0' and symbol[1] in ['3','4','5','6','7','8']:
        return _TYPE_CHOICES[0][0]
    elif symbol[0] == '7' and symbol[1] in ['0','1','2','3']:
        return _TYPE_CHOICES[1][0]
    else:
        return False    
    
class Warrant_Item(Model):
    symbol=models.CharField(default='', max_length=10, verbose_name=_('warrant_symbol'))
    name=models.CharField(default='', max_length=20, verbose_name=_('warrant_name'))
    target_stock=models.ForeignKey("core.Stock_Item", null=True, related_name="warrant_item_list", verbose_name=_('target_stock'))
    target_symbol=models.CharField(default='', max_length=10, verbose_name=_('target_symbol'))
    exercise_style = models.CharField(max_length=1, default=1, choices=_EXERCISE_STYLE_CHOICES, verbose_name=_('exercise_style'))
    classification = models.CharField(max_length=1, default=1, choices=_CLASSIFICATION_CHOICES, verbose_name=_('classification'))
    issuer=models.CharField(default='', max_length=20, verbose_name=_('issuer'))
    listed_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('listed_date')) 
    last_trading_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('last_trading_date')) 
    expiration_date = models.DateField(auto_now_add=False, null=True, verbose_name=_('expiration_date')) 
    issued_volume = models.PositiveIntegerField(default=0, verbose_name=_('issued_volume')) 
    exercise_ratio = models.PositiveIntegerField(default=0, verbose_name=_('exercise_ratio')) 
    strike_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('strike_price'))
    data_ok = models.BooleanField(default=False, verbose_name=_('data_ok')) 
    data_downloaded = models.BooleanField(default=False, verbose_name=_('data_downloaded')) 
    parsing_error = models.BooleanField(default=False, verbose_name=_('parsing_error')) 
    type_code = models.CharField(max_length=1, default='1', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))

    objects = WarrantItemManager() 
    def is_call(self):
        return self.classification == CLASSIFICATION_CODE['CALL']
    def is_put(self):
        return self.classification == CLASSIFICATION_CODE['PUT']

    def is_stock_type_1(self): 
        return self.type_code == _TYPE_CHOICES[0][0]
    def is_stock_type_2(self): 
        return self.type_code == _TYPE_CHOICES[1][0]
    
class TwseTradingMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_warrant_symbol(self, symbol):
        return self.filter(warrant_symbol=symbol)
        
class TwseTradingQuerySet(QuerySet, TwseTradingMixin):
    pass

class TwseTradingManager(models.Manager, TwseTradingMixin):
    def get_queryset(self):
        return TwseTradingQuerySet(self.model, using=self._db)
    def stocks_has_hedge_trade(self, type_code=True):
        if type_code:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0)|Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol','stock_symbol__type_code')
        else:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0)|Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol')

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
    objects = TwseTradingManager() 
#
    class Meta:
        unique_together = ("stock_symbol", "trading_date")

class TwseTradingWarrantMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_warrant_symbol(self, symbol):
        return self.filter(warrant_symbol=symbol)
        
class TwseTradingWarrantQuerySet(QuerySet, TwseTradingWarrantMixin):
    pass

class TwseTradingWarrantManager(models.Manager, TwseTradingWarrantMixin):
    def get_queryset(self):
        return TwseTradingWarrantQuerySet(self.model, using=self._db)
   
class Twse_Trading_Warrant(Model):
    warrant_symbol = models.ForeignKey("core.Warrant_Item", null=True, related_name="twse_trading_warrant_list", verbose_name=_('warrant_symbol'))
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
    objects = TwseTradingWarrantManager() 
    #
    class Meta:
        unique_together = ("warrant_symbol", "trading_date")
class TwseTradingDownloadedMixin(object):
    def not_processed(self):
        return self.filter(is_processed=False, data_available=True)
    
class TwseTradingDownloadedQuerySet(QuerySet, TwseTradingDownloadedMixin):
    pass

class TwseTradingDownloadedManager(models.Manager, TwseTradingDownloadedMixin):
    def get_queryset(self):
        return TwseTradingDownloadedQuerySet(self.model, using=self._db)
    def by_trading_date(self, trading_date):
        return self.get(trading_date=trading_date) 
    def available_and_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, is_processed=False, data_available=True) 
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date, is_processed=True).exists()

class Twse_Trading_Downloaded(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    is_processed = models.BooleanField(default=False, verbose_name=_('is_processed')) 
    data_available = models.BooleanField(default=True, verbose_name=_('data_available')) 
    objects = TwseTradingDownloadedManager() 

class TwseSummaryPriceDownloadedMixin(object):
    def index_not_processed(self):
        return self.filter(index_processed=False, data_available=True)
    def tri_index_not_processed(self):
        return self.filter(tri_index_processed=False, data_available=True)
    def summary_not_processed(self):
        return self.filter(summary_processed=False, data_available=True)
    def updown_not_processed(self):
        return self.filter(updown_processed=False, data_available=True)
    def price_not_processed(self):
        return self.filter(price_processed=False, data_available=True)
 
class TwseSummaryPriceDownloadedQuerySet(QuerySet, TwseSummaryPriceDownloadedMixin):
    pass

class TwseSummaryPriceDownloadedManager(models.Manager, TwseSummaryPriceDownloadedMixin):
    def get_queryset(self):
        return TwseSummaryPriceDownloadedQuerySet(self.model, using=self._db)
    def by_trading_date(self, trading_date):
        return self.get(trading_date=trading_date) 
    def available_and_index_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, index_processed=False, data_available=True) 
    def available_and_tri_index_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, tri_index_processed=False, data_available=True) 
    def available_and_summary_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, summary_processed=False, data_available=True) 
    def available_and_updown_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, updown_processed=False, data_available=True) 
    def available_and_price_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, price_processed=False, data_available=True) 

class Twse_Summary_Price_Downloaded(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    index_processed = models.BooleanField(default=False, verbose_name=_('index_processed')) 
    tri_index_processed = models.BooleanField(default=False, verbose_name=_('tri_index_processed')) 
    summary_processed = models.BooleanField(default=False, verbose_name=_('summary_processed')) 
    updown_processed = models.BooleanField(default=False, verbose_name=_('updown_processed')) 
    price_processed = models.BooleanField(default=False, verbose_name=_('price_processed')) 
    data_available = models.BooleanField(default=True, verbose_name=_('data_available')) 
    objects = TwseSummaryPriceDownloadedManager() 
    
    
    
class IndexItemMixin(object):
    pass
    
class IndexItemQuerySet(QuerySet, IndexItemMixin):
    pass

class IndexItemManager(models.Manager, IndexItemMixin):
    def get_queryset(self):
        return IndexItemQuerySet(self.model, using=self._db)
    def get_by_name(self, name):
        return self.get(name=name)
    def get_by_tri_name(self, name):
        return self.get(name=name, is_total_return_index=True)
    
    
class Index_Item(Model):
    name=models.CharField(default='', max_length=100, verbose_name=_('index_name'))
    name_en=models.CharField(default='', max_length=100, verbose_name=_('index_name_en'))
    is_total_return_index = models.BooleanField(default=False, verbose_name=_('is_total_return_index'))  

    objects= IndexItemManager()

class IndexChangeInfoMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    
class IndexChangeInfoQuerySet(QuerySet, IndexChangeInfoMixin):
    pass

class IndexChangeInfoManager(models.Manager, IndexChangeInfoMixin):
    def get_queryset(self):
        return IndexChangeInfoQuerySet(self.model, using=self._db)
    
class Index_Change_Info(Model):
    twse_index = models.ForeignKey("core.Index_Item", related_name="index_change_list", verbose_name=_('twse_index'))
    closing_index = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('closing_index')) 
    change = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('change')) 
    change_in_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('change_in_percentage')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    
    objects= IndexChangeInfoManager()
#
    class Meta:
        unique_together = ("twse_index", "trading_date")
        
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
    name=models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name'))
    name_en=models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name_en'))

    objects= MarketSummaryTypeManager()
    
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
    
    objects= MarketSummaryManager()
 #
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
    objects= StockUpDownStatsManager()