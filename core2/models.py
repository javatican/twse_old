# coding=utf8
from django.db import models
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _

      
class GtStockItemMixin(object):
    def need_to_process(self): 
        return self.filter(data_ok=False, data_downloaded=True, parsing_error=False)
    def data_not_yet_download(self):
        return self.filter(data_downloaded=False)
    
class GtStockItemQuerySet(QuerySet, GtStockItemMixin):
    pass

class GtStockItemManager(models.Manager, GtStockItemMixin):
    def get_queryset(self):
        return GtStockItemQuerySet(self.model, using=self._db)
    def get_by_symbol(self, symbol):
        return self.get(symbol=symbol)
    
_TYPE_CHOICES = (
        ('1', u'上市'),
        ('2', u'上櫃'),)

def get_stock_item_type(type_name):
    if type_name ==  _TYPE_CHOICES[0][1]:
        return _TYPE_CHOICES[0][0]
    elif type_name == _TYPE_CHOICES[1][1]:
        return _TYPE_CHOICES[1][0]
    else:
        return None
    
class Gt_Stock_Item(Model):
    symbol=models.CharField(default='', max_length=10, verbose_name=_('stock_symbol'))
    short_name=models.CharField(default='', max_length=20, verbose_name=_('stock_short_name'))
    name=models.CharField(default='', max_length=100, verbose_name=_('stock_name'))
    type_code = models.CharField(max_length=1, default='2', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))
    market_category=models.CharField(default='', max_length=50, verbose_name=_('market_category'))
    notes=models.CharField(default='', max_length=100, verbose_name=_('notes'))
    data_ok = models.BooleanField(default=False, verbose_name=_('data_ok')) 
    data_downloaded = models.BooleanField(default=False, verbose_name=_('data_downloaded')) 
    parsing_error = models.BooleanField(default=False, verbose_name=_('parsing_error')) 
    is_etf = models.BooleanField(default=False, verbose_name=_('is_etf')) 
    etf_target = models.CharField(default='', max_length=100, verbose_name=_('etf_target'))

    objects= GtStockItemManager()
    def is_stock_type_1(self): 
        return self.type_code == _TYPE_CHOICES[0][0]
    def is_stock_type_2(self): 
        return self.type_code == _TYPE_CHOICES[1][0]
    
class GtWarrantItemMixin(object):
    def need_to_process(self): 
        return self.filter(data_ok=False, data_downloaded=True, parsing_error=False)
    def data_not_yet_download(self):
        return self.filter(data_downloaded=False)
    def data_need_other_download_url(self):
        return self.filter(parsing_error=True)
        
class GtWarrantItemQuerySet(QuerySet, GtWarrantItemMixin):
    pass

class GtWarrantItemManager(models.Manager, GtWarrantItemMixin):
    def get_queryset(self):
        return GtWarrantItemQuerySet(self.model, using=self._db)
    def stocks_has_warrants(self):
        return self.filter(data_ok=True).distinct().values_list('target_stock__symbol', flat=True)
    

_CALL = '1'
_PUT = '2' 
_EXERCISE_STYLE_CHOICES = (
        ('1', u'歐式'),
        ('2', u'美式'),)
_CLASSIFICATION_CHOICES = (
        (_CALL, u'認購'),
        (_PUT, u'認售'),)

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

class Gt_Warrant_Item(Model):
    symbol=models.CharField(default='', max_length=10, verbose_name=_('warrant_symbol'))
    name=models.CharField(default='', max_length=20, verbose_name=_('warrant_name'))
    target_stock=models.ForeignKey("core2.Gt_Stock_Item", null=True, related_name="warrant_item_list", verbose_name=_('target_stock'))
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
    type_code = models.CharField(max_length=1, default='2', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))

    objects = GtWarrantItemManager() 
    def is_call(self):
        return self.classification == CLASSIFICATION_CODE['CALL']
    def is_put(self):
        return self.classification == CLASSIFICATION_CODE['PUT']
    
    def is_stock_type_1(self): 
        return self.type_code == _TYPE_CHOICES[0][0]
    def is_stock_type_2(self): 
        return self.type_code == _TYPE_CHOICES[1][0]

class GtTradingMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_warrant_symbol(self, symbol):
        return self.filter(warrant_symbol=symbol)
        
class GtTradingQuerySet(QuerySet, GtTradingMixin):
    pass

class GtTradingManager(models.Manager, GtTradingMixin):
    def get_queryset(self):
        return GtTradingQuerySet(self.model, using=self._db)
    def stocks_has_hedge_trade(self, type_code=True):
        if type_code:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0)|Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol','stock_symbol__type_code')
        else:
            return self.filter(Q(stock_symbol__isnull=False), Q(hedge_buy__gt=0)|Q(hedge_sell__gt=0)).distinct().values('stock_symbol__symbol')

class Gt_Trading(Model):
    stock_symbol = models.ForeignKey("core2.Gt_Stock_Item", null=True, related_name="gt_trading_list", verbose_name=_('stock_symbol'))
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
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('average_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('closing_price'))
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price_change'))
    last_best_bid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_bid_price'))
    last_best_ask_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('last_best_ask_price'))
    objects = GtTradingManager() 
#
    class Meta:
        unique_together = ("stock_symbol", "trading_date")

class GtTradingWarrantMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_warrant_symbol(self, symbol):
        return self.filter(warrant_symbol=symbol)
        
class GtTradingWarrantQuerySet(QuerySet, GtTradingWarrantMixin):
    pass

class GtTradingWarrantManager(models.Manager, GtTradingWarrantMixin):
    def get_queryset(self):
        return GtTradingWarrantQuerySet(self.model, using=self._db)
   
class Gt_Trading_Warrant(Model):
    warrant_symbol = models.ForeignKey("core2.Gt_Warrant_Item", null=True, related_name="gt_trading_warrant_list", verbose_name=_('warrant_symbol'))
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
    objects = GtTradingWarrantManager() 
    #
    class Meta:
        unique_together = ("warrant_symbol", "trading_date")
class GtTradingDownloadedMixin(object):
    def not_processed(self):
        return self.filter(is_processed=False, data_available=True)
    
class GtTradingDownloadedQuerySet(QuerySet, GtTradingDownloadedMixin):
    pass

class GtTradingDownloadedManager(models.Manager, GtTradingDownloadedMixin):
    def get_queryset(self):
        return GtTradingDownloadedQuerySet(self.model, using=self._db)
    def by_trading_date(self, trading_date):
        return self.get(trading_date=trading_date) 
    def available_and_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, is_processed=False, data_available=True) 
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date, is_processed=True).exists()

class Gt_Trading_Downloaded(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    is_processed = models.BooleanField(default=False, verbose_name=_('is_processed')) 
    data_available = models.BooleanField(default=True, verbose_name=_('data_available')) 
    objects = GtTradingDownloadedManager() 

class GtSummaryPriceDownloadedMixin(object):
    def summary_not_processed(self):
        return self.filter(summary_processed=False, data_available=True)
    def highlight_not_processed(self):
        return self.filter(highlight_processed=False, data_available=True)
    def price_not_processed(self):
        return self.filter(price_processed=False, data_available=True)
 
class GtSummaryPriceDownloadedQuerySet(QuerySet, GtSummaryPriceDownloadedMixin):
    pass

class GtSummaryPriceDownloadedManager(models.Manager, GtSummaryPriceDownloadedMixin):
    def get_queryset(self):
        return GtSummaryPriceDownloadedQuerySet(self.model, using=self._db)
    def by_trading_date(self, trading_date):
        return self.get(trading_date=trading_date) 
    def available_and_summary_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, summary_processed=False, data_available=True) 
    def available_and_highlight_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, highlight_processed=False, data_available=True) 
    def available_and_price_unprocessed(self, trading_date):
        return self.get(trading_date=trading_date, price_processed=False, data_available=True) 

class Gt_Summary_Price_Downloaded(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    summary_processed = models.BooleanField(default=False, verbose_name=_('summary_processed')) 
    highlight_processed = models.BooleanField(default=False, verbose_name=_('highlight_processed')) 
    price_processed = models.BooleanField(default=False, verbose_name=_('price_processed')) 
    data_available = models.BooleanField(default=True, verbose_name=_('data_available')) 
    objects = GtSummaryPriceDownloadedManager() 
        
class GtMarketSummaryTypeMixin(object):
    pass
    
class GtMarketSummaryTypeQuerySet(QuerySet, GtMarketSummaryTypeMixin):
    pass

class GtMarketSummaryTypeManager(models.Manager, GtMarketSummaryTypeMixin):
    def get_queryset(self):
        return GtMarketSummaryTypeQuerySet(self.model, using=self._db)
    def get_by_name(self, name):
        return self.get(name=name)
    
class Gt_Market_Summary_Type(Model):
    name=models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name'))
    name_en=models.CharField(default='', max_length=100, verbose_name=_('market_summary_type_name_en'))

    objects= GtMarketSummaryTypeManager()
    
class GtMarketSummaryMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    
class GtMarketSummaryQuerySet(QuerySet, GtMarketSummaryMixin):
    pass

class GtMarketSummaryManager(models.Manager, GtMarketSummaryMixin):
    def get_queryset(self):
        return GtMarketSummaryQuerySet(self.model, using=self._db)
    
class Gt_Market_Summary(Model):
    summary_type = models.ForeignKey("core2.Gt_Market_Summary_Type", related_name="summary_list", verbose_name=_('summary_type'))
    trade_value = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    trade_volume = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trading_date = models.DateField(auto_now_add=False, null=False, verbose_name=_('trading_date')) 
    
    objects= GtMarketSummaryManager()
 #
    class Meta:
        unique_together = ("summary_type", "trading_date")
          
class GtMarketHighlightMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    
class GtMarketHighlightQuerySet(QuerySet, GtMarketHighlightMixin):
    pass

class GtMarketHighlightManager(models.Manager, GtMarketHighlightMixin):
    def get_queryset(self):
        return GtMarketHighlightQuerySet(self.model, using=self._db)
    
class Gt_Market_Highlight(Model):
    
    listed_companies = models.PositiveIntegerField(default=0, verbose_name=_('listed_companies')) 
    capitals = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('capitals')) 
    market_capitalization = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('market_capitalization')) 
    trade_value = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    trade_volume = models.DecimalField(max_digits=17, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    closing_index = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('closing_index')) 
    change = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('change')) 
    change_in_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('change_in_percentage')) 
    stock_up = models.PositiveIntegerField(default=0, verbose_name=_('stock_up')) 
    stock_up_limit = models.PositiveIntegerField(default=0, verbose_name=_('stock_up_limit')) 
    stock_down = models.PositiveIntegerField(default=0, verbose_name=_('stock_down')) 
    stock_down_limit = models.PositiveIntegerField(default=0, verbose_name=_('stock_down_limit')) 
    stock_unchange = models.PositiveIntegerField(default=0, verbose_name=_('stock_unchange')) 
    stock_unmatch = models.PositiveIntegerField(default=0, verbose_name=_('stock_unmatch')) 
    trading_date = models.DateField(auto_now_add=False, unique=True, null=False, verbose_name=_('trading_date')) 
    objects= GtMarketHighlightManager()