# coding=utf8
from django.db import models
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _

      
class GtStockItemMixin(object):
    def data_not_ok(self): 
        return self.filter(data_ok=False)
    
class GtStockItemQuerySet(QuerySet, GtStockItemMixin):
    pass

class GtStockItemManager(models.Manager, GtStockItemMixin):
    def get_queryset(self):
        return GtStockItemQuerySet(self.model, using=self._db)
    def get_by_symbol(self, symbol):
        return self.get(symbol=symbol)
    
_TYPE_TWSE='1'
_TYPE_GT='2'

_TYPE_CHOICES = (
        (_TYPE_TWSE, u'上市'),
        (_TYPE_GT, u'上櫃'),)

def get_stock_item_type(type_name):
    if type_name ==  u'上市':
        return _TYPE_CHOICES[0][0]
    elif type_name == u'上櫃' or type_name == u'興櫃' or type_name == u'公開發行' :
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
    is_etf = models.BooleanField(default=False, verbose_name=_('is_etf')) 
    etf_target = models.CharField(default='', max_length=100, verbose_name=_('etf_target'))

    objects= GtStockItemManager()
    
    def is_twse_stock(self): 
        return self.type_code == _TYPE_TWSE
    def is_gt_stock(self): 
        return self.type_code == _TYPE_GT
    
class GtWarrantItemMixin(object):
    def data_not_ok(self):
        return self.filter(data_ok=False)
        
class GtWarrantItemQuerySet(QuerySet, GtWarrantItemMixin):
    pass

class GtWarrantItemManager(models.Manager, GtWarrantItemMixin):
    def get_queryset(self):
        return GtWarrantItemQuerySet(self.model, using=self._db)
    def stocks_has_warrants(self):
        return self.filter(data_ok=True).distinct().values_list('target_stock__symbol', flat=True)
    
_EXERCISE_STYLE_CHOICES = (
        ('1', u'歐式'),
        ('2', u'美式'),)

def get_warrant_exercise_style(exercise_style):
    if exercise_style ==  _EXERCISE_STYLE_CHOICES[0][1]:
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
    if classification ==  _CLASSIFICATION_CHOICES[0][1]:
        return _CLASSIFICATION_CHOICES[0][0]
    elif classification == _CLASSIFICATION_CHOICES[1][1]:
        return _CLASSIFICATION_CHOICES[1][0]
    else:
        return None

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
    type_code = models.CharField(max_length=1, default='2', choices=_TYPE_CHOICES, verbose_name=_('stock_type'))

    objects = GtWarrantItemManager() 
    def is_call(self):
        return self.classification == CLASSIFICATION_CODE['CALL']
    def is_put(self):
        return self.classification == CLASSIFICATION_CODE['PUT']
    
    def is_twse_stock(self): 
        return self.type_code == _TYPE_TWSE
    def is_gt_stock(self): 
        return self.type_code == _TYPE_GT

class GtTradingMixin(object):
    def by_date(self, trading_date):
        return self.filter(trading_date=trading_date)
    def by_symbol(self, symbol):
        return self.filter(stock_symbol=symbol)
        
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
    def get_date_with_missing_target_trading_info(self):
        return self.filter(target_stock_trading__isnull=True).distinct().values_list('trading_date', flat=True)
    def no_target_trading_info(self, trading_date):
        return self.filter(trading_date=trading_date, target_stock_trading__isnull=True).select_related('warrant_symbol')
        
class GtTradingWarrantQuerySet(QuerySet, GtTradingWarrantMixin):
    pass

class GtTradingWarrantManager(models.Manager, GtTradingWarrantMixin):
    def get_queryset(self):
        return GtTradingWarrantQuerySet(self.model, using=self._db)
   
class Gt_Trading_Warrant(Model):
    warrant_symbol = models.ForeignKey("core2.Gt_Warrant_Item", null=True, related_name="gt_trading_warrant_list", verbose_name=_('warrant_symbol'))
    target_stock_symbol = models.ForeignKey("core2.Gt_Stock_Item", null=True, related_name="gt_trading_warrant_list2", verbose_name=_('target_stock_symbol'))
    target_stock_trading = models.ForeignKey("core2.Gt_Trading", null=True, related_name="gt_trading_warrant_list3", verbose_name=_('target_stock_trading'))
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
    time_to_maturity = models.DecimalField(max_digits=6, decimal_places=4, null=True, verbose_name=_('time_to_maturity')) 
    implied_volatility = models.DecimalField(max_digits=6, decimal_places=4, null=True, verbose_name=_('implied_volatility')) 
    delta = models.DecimalField(max_digits=7, decimal_places=4, null=True, verbose_name=_('delta')) 
    leverage = models.DecimalField(max_digits=7, decimal_places=2, null=True, verbose_name=_('leverage')) 
  
    objects = GtTradingWarrantManager() 
    #
    class Meta:
        unique_together = ("warrant_symbol", "trading_date")

class GtTradingProcessedMixin(object):
    pass
    
class GtTradingProcessedQuerySet(QuerySet, GtTradingProcessedMixin):
    pass

class GtTradingProcessedManager(models.Manager, GtTradingProcessedMixin):
    def get_queryset(self):
        return GtTradingProcessedQuerySet(self.model, using=self._db)
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date).exists()

class Gt_Trading_Processed(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    objects = GtTradingProcessedManager() 

class GtSummaryPriceProcessedMixin(object):
    pass
    
class GtSummaryPriceProcessedQuerySet(QuerySet, GtSummaryPriceProcessedMixin):
    pass

class GtSummaryPriceProcessedManager(models.Manager, GtSummaryPriceProcessedMixin):
    def get_queryset(self):
        return GtSummaryPriceProcessedQuerySet(self.model, using=self._db)
    def check_processed(self, trading_date):
        return self.filter(trading_date=trading_date).exists()

class Gt_Summary_Price_Processed(Model):
    trading_date = models.DateField(null=False, unique=True, verbose_name=_('trading_date')) 
    objects = GtSummaryPriceProcessedManager() 
        
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