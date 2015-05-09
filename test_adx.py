# -*- coding: utf-8 -*-

"""
http://virtualizedfrog.wordpress.com/   2014


Translated from http://www.amibroker.com/library/detail.php?id=268
Requires pandas to load csv files, and matplotlib to chart the data

The main expects table.csv file. Valid files can be downloaded on Yahoo Finance
eg: http://real-chart.finance.yahoo.com/table.csv?s=%5EGSPC&ignore=.csv
"""

import numpy as np
import pandas as pd
from warrant_app.utils.trading_util import _calc_di_adx


df = pd.read_excel('cs-adx.xls', 'adx', header=1, parse_cols=[2, 3, 4])
arr = np.asarray(df).T
highest_array = arr[0]
lowest_array = arr[1]
closing_array = arr[2]
for i in np.arange(highest_array.size):
    print "highest=%s, lowest=%s, closing=%s" % (highest_array[i], lowest_array[i], closing_array[i])
tr14_array, pdm14_array, ndm14_array, pdi14_array, ndi14_array, adx_array = _calc_di_adx(highest_array, lowest_array, closing_array, SMOOTHING_FACTOR=14)
for i in np.arange(adx_array.size):
    print "tr14=%s, pdm14=%s, ndm14=%s, pdi=%s, ndi=%s, adx=%s" % (tr14_array[i], pdm14_array[i], ndm14_array[i], pdi14_array[i], ndi14_array[i], adx_array[i])
