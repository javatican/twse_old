from math import *

import numpy as np
import scipy.stats as ss

#Black and Scholes from http://gosmej1977.blogspot.tw/2013/02/black-and-scholes-formula.html
def d1(S0, K, r, sigma, T):
    return (np.log(S0/K) + (r + sigma**2 / 2) * T)/(sigma * np.sqrt(T))
 
def d2(S0, K, r, sigma, T):
    return (np.log(S0 / K) + (r - sigma**2 / 2) * T) / (sigma * np.sqrt(T))
 
def BlackScholes(type,S0, K, r, sigma, T):
    if type=="C":
        return S0 * ss.norm.cdf(d1(S0, K, r, sigma, T)) - K * np.exp(-r * T) * ss.norm.cdf(d2(S0, K, r, sigma, T))
    else:
        return K * np.exp(-r * T) * ss.norm.cdf(-d2(S0, K, r, sigma, T)) - S0 * ss.norm.cdf(-d1(S0, K, r, sigma, T))
   

def option_price_delta_call_black_scholes(S, K, r, sigma, time):  
    """Black Scholes formula (Put) 
    Black and Scholes (1973) and Merton (1973) 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param sigma: volatility  
    @param time: time to maturity  
    @return: delta
     """       
    #added by ryan Nieh 
#     if sigma <= 0.0: 
#         return 0.0 
    time_sqrt = sqrt(time)  
    d1 = (log(S/K)+r*time)/(sigma*time_sqrt) + 0.5*sigma*time_sqrt  
    delta = N(d1)
    return delta

def option_price_delta_put_black_scholes(S, K, r, sigma, time):  
    """Black Scholes formula (Put) 
    Black and Scholes (1973) and Merton (1973) 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param sigma: volatility  
    @param time: time to maturity  
    @return: delta
     """      
    #added by ryan Nieh 
#     if sigma <= 0.0: 
#         return 0.0 
    time_sqrt = sqrt(time)  
    d1 = (log(S/K)+r*time)/(sigma*time_sqrt) + 0.5*sigma*time_sqrt  
    delta = -N(-d1)
    return delta

def option_price_implied_volatility_call_black_scholes_newton(S, K, r, time, option_price):  
    """Calculates implied volatility for the Black Scholes formula using 
    the Newton-Raphson formula 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    (NOTE: In the original code a large negative number was used as an 
    exception handling mechanism.  This has been replace with a generic 
    'Exception' that is thrown.  The original code is in place and commented 
    if you want to use the pure version of this code) 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param time: time to maturity  
    @param option_price: The price of the option 
    @return: Sigma (implied volatility) 
    """                                 
#     if (option_price<0.99*(S-K*exp(-time*r))): # check for arbitrage violations. Option price is too low if this happens  
#         return 0.0
#   
    MAX_ITERATIONS = 100
    ACCURACY = 1.0e-3 
    t_sqrt = sqrt(time)  
  
    #sigma = (option_price/S)/(0.398*t_sqrt) # find initial value
    initial_sigma_values=[0.5, 0.2, 0.8]  
    for sigma in initial_sigma_values:
        #print 'initial sigma=%s' %sigma
        try:
            for i in xrange(0, MAX_ITERATIONS):  
                price = option_price_call_black_scholes(S,K,r,sigma,time) 
                #print 'cycle %s: price=%s' %(i,price)
                diff = option_price -price  
                if (abs(diff)<ACCURACY):  
                    return sigma 
                d1 = (log(S/K)+r*time)/(sigma*t_sqrt) + 0.5*sigma*t_sqrt  
                vega = S * t_sqrt * N(d1)  
                sigma = sigma + diff/vega  
                #print 'cycle %s: sigma=%s' %(i,sigma)
        except:
            continue
    raise Exception("Implied volatility calculation is not converged.")

def option_price_implied_volatility_put_black_scholes_newton(S, K, r, time, option_price):  
    """Calculates implied volatility for the Black Scholes formula using 
    the Newton-Raphson formula 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    (NOTE: In the original code a large negative number was used as an 
    exception handling mechanism.  This has been replace with a generic 
    'Exception' that is thrown.  The original code is in place and commented 
    if you want to use the pure version of this code) 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param time: time to maturity  
    @param option_price: The price of the option 
    @return: Sigma (implied volatility) 
    """                                   
#
    MAX_ITERATIONS = 100
    ACCURACY = 1.0e-3  
    t_sqrt = sqrt(time)  
    #sigma = (option_price/S)/(0.398*t_sqrt) # find initial value
    initial_sigma_values=[0.5, 0.2, 0.8]  
    for sigma in initial_sigma_values:
        try:
            for i in xrange(0, MAX_ITERATIONS):  
                price = option_price_put_black_scholes(S,K,r,sigma,time) 
                diff = option_price -price  
                if (abs(diff)<ACCURACY): 
                    return sigma
                d1 = (log(S/K)+r*time)/(sigma*t_sqrt) + 0.5*sigma*t_sqrt  
                vega = S * t_sqrt * N(d1)  
                sigma = sigma + diff/vega
        except:
            continue
    raise Exception("Implied volatility calculation is not converged.")

def option_price_call_black_scholes(S, K, r, sigma, time):  
    """Black Scholes formula (Call) 
    Black and Scholes (1973) and Merton (1973) 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param sigma: volatility  
    @param time: time to maturity  
    @return: Option price 
    """                                                                      
    time_sqrt = sqrt(time)  
    d1 = (log(S/K)+r*time)/(sigma*time_sqrt)+0.5*sigma*time_sqrt  
    d2 = d1-(sigma*time_sqrt)  
    #print "d1=%s, d2=%s" %(d1,d2)
    return S*N(d1) - K*exp(-r*time)*N(d2)  
  
  
def option_price_put_black_scholes(S, K, r, sigma, time):  
    """Black Scholes formula (Put) 
    Black and Scholes (1973) and Merton (1973) 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    @param S: spot (underlying) price 
    @param K: strike (exercise) price, 
    @param r: interest rate 
    @param sigma: volatility  
    @param time: time to maturity  
    @return: Option price 
    """ 
    time_sqrt = sqrt(time)  
    d1 = (log(S/K)+r*time)/(sigma*time_sqrt) + 0.5*sigma*time_sqrt  
    d2 = d1-(sigma*time_sqrt)  
    return K*exp(-r*time)*N(-d2) - S*N(-d1)  
  
  
def N(z):  
    """Cumulative normal distribution 
    Abramowiz and Stegun approximation (1964) 
    Converted to Python from "Financial Numerical Recipes in C" by: 
    Bernt Arne Odegaard 
    http://finance.bi.no/~bernt/gcc_prog/index.html 
    @param z: Value to twse_process 
    @return: Cumulative normal distribution 
    """  
    if (z >  6.0):  # this guards against overflow   
        return 1.0   
    if (z < -6.0):  
        return 0.0  
  
    b1 =  0.31938153   
    b2 = -0.356563782  
    b3 =  1.781477937  
    b4 = -1.821255978  
    b5 =  1.330274429  
    p  =  0.2316419  
    c2 =  0.3989423  
  
    a=abs(z)   
    t = 1.0/(1.0+a*p)   
    b = c2*exp((-z)*(z/2.0))  
    n = ((((b5*t+b4)*t+b3)*t+b2)*t+b1)*t  
    n = 1.0-b*n   
    if ( z < 0.0 ):   
        n = 1.0 - n   
    return n  
