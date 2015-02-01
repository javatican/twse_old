import datetime
import re
import uuid

from django.conf import settings
from django.conf.urls import url


float_pattern = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
def is_float(input_string):
    if float_pattern.match(input_string) is None:
        return False
    else: return True
# below method is used to modify regex string in url patterns 
# to insert a subsite uri
def url_with_subsite(regex, view, kwargs=None, name=None, prefix=''):
    # modify regex
    if getattr(settings, 'SUB_SITE_URI', ''):
        regex="%s%s%s" % ('^', settings.SUB_SITE_URI, regex[1:])
    return url(regex, view, kwargs, name, prefix)


def append_and_make_unique(input_string, element):
    # the input is a comma-separated string containing unique integers
    # return a tuple, if the first element is True means it has been appended 
    if not input_string: 
        return True, str(element)
    else:
        appended = True
        a_set = set(input_string.split(','))
        a_set_length = len(a_set)
        a_set.add(str(element))
        if a_set_length == len(a_set):
            appended=False
        return appended, ','.join(a_set)
    
# below used together with above method
def remove_element(input_string, element):
    # the input is a comma-separated string containing unique integers
    # return a tuple, if the first element is True means it has been removed
    if not input_string: 
        return False, ''
    else:
        removed=True
        a_set = set(input_string.split(','))
        a_set_length = len(a_set)
        a_set.discard(str(element))
        if a_set_length == len(a_set):
            removed=False
        return removed, ','.join(a_set)
    
def concat_list(target, separator=', '):
    if(not target or len(target)==0):
        return ''
    result_list=[]
    for t in target:
        result_list.append(unicode(t))
    return '[%s]' % separator.join(result_list)

def concat_list_to_string(target, separator=','):
    if(not target or len(target)==0):
        return ''
    result_list=[]
    for t in target:
        result_list.append(unicode(t))
    return '%s' % separator.join(result_list)
 
def unique_id(today=True, the_format="%y%m%d", digit=6):
    uuid_str=uuid.uuid4().hex[:digit].upper()
    if today:
        today_str=datetime.date.today().strftime(the_format)
        return today_str+uuid_str
    else:
        return uuid_str
# below for testing purpose if the duplicated ids are taken care correctly.

#global ids
#global counter   
#ids = ['111111','111111','111111','111111','111111','111111','222222']
#counter = 0
#def unique_id(today=True, format="%y%m%d", digit=6):
#    #uuid_str=uuid.uuid4().hex[:digit].upper()
#    global counter
#    global ids
#    uuid_str = ids[counter]
#    counter = counter+1
#    if today:
#        today_str=datetime.date.today().strftime(format)
#        return today_str+uuid_str
#    else:
#        return uuid_str