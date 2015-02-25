from django.utils import timezone
import calendar
import datetime

def string_to_date(date_string, date_format='%Y/%m/%d'):
    return datetime.datetime.strptime(date_string,date_format).date()

def is_third_wednesday(d): 
    return d.weekday() == 2 and 14 < d.day < 22

def roc_year_to_western(roc_date_string):
    #roc date format : year/month/day
    #first split the string into year, month, day
    data_list=roc_date_string.split('/')
    year=int(data_list[0])
    month=int(data_list[1])
    day=int(data_list[2])
    return datetime.date(year+1911, month, day)

def western_to_roc_year(date_string):
    #western format : year/month/day
    #first split the string into year, month, day
    #return a string
    data_list=date_string.split('/')
    year=int(data_list[0])
    month=data_list[1]
    day=data_list[2]
    return "%s/%s/%s" % (year-1911, month, day)

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

def getLastDayPrevMonth(today=None):
    if not today:
        today = datetime.date.today()
    year = today.year
    mon = today.month
    time = datetime.time(0, 0, 0)
    #
    mon = mon - 1
    if mon <= 0:
        year = year - 1
        mon = mon + 12
    #prev_month_1st = datetime.datetime.combine(datetime.date(year, mon, 1), time).replace(tzinfo=timezone.get_current_timezone())
    prev_month_last = datetime.datetime.combine(datetime.date(year, mon, calendar.monthrange(year, mon)[1]), time).replace(tzinfo=timezone.get_current_timezone()) + datetime.timedelta(seconds=86399)
    # return a timezone aware object
    return prev_month_last

def getFirstDayPrevMonth(today=None):
    if not today:
        today = datetime.date.today()
    year = today.year
    mon = today.month
    time = datetime.time(0, 0, 0)
    #
    mon = mon - 1
    if mon <= 0:
        year = year - 1
        mon = mon + 12
    prev_month_1st = datetime.datetime.combine(datetime.date(year, mon, 1), time).replace(tzinfo=timezone.get_current_timezone())
    # return a timezone aware object
    return prev_month_1st

def convertToDateTime(date_string):
    #convert a string of format 'yyyymmdd' to date object
    year = int(date_string[:4])
    mon= int(date_string[4:6])
    day = int(date_string[6:8])
    #print year,mon,day
    time = datetime.time(0, 0, 0)
    return datetime.datetime.combine(datetime.date(year, mon, day), time).replace(tzinfo=timezone.get_current_timezone())
    
def convertToDate(date_string):
    return string_to_date(date_string, date_format='%Y%m%d')