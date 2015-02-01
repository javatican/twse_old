from django import db
from django.conf import settings
from django.db import connection
import inspect
import logging
import sys

def log_sql():
    #is_log=False
    is_log=True
    if settings.DEBUG and is_log:
        caller=inspect.stack()[1]
        filename=caller[1]
        line_number=caller[2]
        function_name=caller[3] 
        print >> sys.stderr, ",".join(map(str, [filename, line_number, function_name]))
        print >> sys.stderr, "\n".join(map(str, connection.queries))
        db.reset_queries()
    
def log_message(message):
    if settings.DEBUG:
        caller=inspect.stack()[1]
        filename=caller[1]
        line_number=caller[2]
        function_name=caller[3] 
        print >> sys.stderr, ",".join(map(str, [filename, line_number, function_name]))
        print >> sys.stderr, message
        
def dump_form_validation_errors(form, logger):
    for field in form:
        if field.errors:
            logger.warning(field.errors, exc_info=1) 