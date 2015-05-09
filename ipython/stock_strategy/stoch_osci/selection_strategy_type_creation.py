# coding=utf8
from core.models import Selection_Strategy_Type

#create selection strategy type

sst=Selection_Strategy_Type()
sst.symbol='stoch_pop_watch'
sst.name='Stochastic Pop Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_pop_breakout'
sst.name='Stochastic Pop Breakout - First Day'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_pop_breakout2'
sst.name='Stochastic Pop Breakout - Second Day'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_pop_breakout3'
sst.name='Stochastic Pop Breakout - Third Day'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_drop_watch'
sst.name='Stochastic Drop Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_drop_breakout'
sst.name='Stochastic Drop Breakout - First Day'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_drop_breakout2'
sst.name='Stochastic Drop Breakout - Second Day'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_drop_breakout3'
sst.name='Stochastic Drop Breakout - Third Day'
sst.save()
#
sst=Selection_Strategy_Type()
sst.symbol='stoch_cross_bull_level_watch'
sst.name='Stochastic Cross Bull Level Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_cross_bull_level'
sst.name='Stochastic Cross Bull Level'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_golden_cross_watch'
sst.name='Stochastic Golden Cross Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_golden_cross'
sst.name='Stochastic Golden Cross'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_cross_bear_level_watch'
sst.name='Stochastic Cross Bear Level Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_cross_bear_level'
sst.name='Stochastic Cross Bear Level'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_death_cross_watch'
sst.name='Stochastic Death Cross Watch'
sst.save()
sst=Selection_Strategy_Type()
sst.symbol='stoch_death_cross'
sst.name='Stochastic Death Cross'
sst.save()

