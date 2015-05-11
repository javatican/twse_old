import calendar
import datetime
from django.utils import timezone
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
#usage: json.dumps(data, cls=DateEncoder)
def today_at_1330():
    today_str=datetime.datetime.today().strftime('%Y-%m-%d')
    datetime_str="%sT13:30:00" % today_str
    return datetime.datetime.strptime(datetime_str,'%Y-%m-%dT%H:%M:%S')
def string_to_date(date_string, date_format='%Y/%m/%d'):
    return datetime.datetime.strptime(date_string,date_format).date()

# the date is default to 1900/1/1
def string_to_time(time_string, date_format='%H:%M:%S'):
    return datetime.datetime.strptime(time_string,date_format)

def is_third_wednesday(d): 
    return d.weekday() == 2 and 14 < d.day < 22

def roc_year(western_year):
    return western_year-1911
    
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
    
def convertToDate(date_string, date_format='%Y%m%d'):
    return string_to_date(date_string, date_format)