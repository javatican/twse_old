from datetime import timedelta
from matplotlib import mlab

from warrant_app.utils.dateutil import string_to_date


# used with matplotlib.cbook.violin_stats function 
def kde_method(X, coords):
    kde = mlab.GaussianKDE(X, 'scott')
    return kde.evaluate(coords)

# based on trading_date list , return 'weekday' list
def get_weekday_array(trading_date_list, between_gap_flag=False):
    mon = []
    tue = []
    wed = []
    thr = []
    fri = []
    sat = []
    #
    between_gap = [] 
    others = []
    i = 0
    previous_date = None
    for trading_date_str in trading_date_list:
        trading_date = string_to_date(trading_date_str, date_format='%Y-%m-%d')
        day_of_week = trading_date.weekday() + 1
        if day_of_week == 1:
            mon.append(i)
        elif day_of_week == 2:
            tue.append(i)
        elif day_of_week == 3:
            wed.append(i)
        elif day_of_week == 4:
            thr.append(i)
        elif day_of_week == 5:
            fri.append(i)
        elif day_of_week == 6:
            sat.append(i)
        if i > 0:
            if trading_date > previous_date + timedelta(days=1):
                # gap greater than 1 day
                between_gap.append(i - 1)
                between_gap.append(i)
            else:
                others.append(i - 1)
                others.append(i)
        previous_date = trading_date
        i += 1
    if between_gap_flag:
        return (mon,tue,wed,thr,fri,sat, between_gap, others)
    else:
        return (mon,tue,wed,thr,fri,sat)

# for coloring violin plot based on weekdays
def set_colors(polycoll_list, mon, tue, wed, thr, fri, sat):
    for n in mon: 
        polycoll_list[n].set_facecolor('r')
        polycoll_list[n].set_label('Mon')
    for n in tue: 
        polycoll_list[n].set_facecolor('y')
        polycoll_list[n].set_label('Tue')
    for n in wed: 
        polycoll_list[n].set_facecolor('b')
        polycoll_list[n].set_label('Wed')
    for n in thr: 
        polycoll_list[n].set_facecolor('g')
        polycoll_list[n].set_label('Thr')
    for n in fri: 
        polycoll_list[n].set_facecolor('m')
        polycoll_list[n].set_label('Fri')
    if len(sat) > 0 :
        for n in sat: 
            polycoll_list[n].set_facecolor('c')
            polycoll_list[n].set_label('Sat')
            
# for coloring violin plot based on 'between_gap and others'
def set_colors_2(polycoll_list, between_gap, others):
    # important: need to plot others first, then between_gap
    for n in others: 
        polycoll_list[n].set_facecolor('0.8')
        polycoll_list[n].set_label('others')
    for n in between_gap: 
        polycoll_list[n].set_facecolor('k')
        polycoll_list[n].set_label('Before/after trading gap')