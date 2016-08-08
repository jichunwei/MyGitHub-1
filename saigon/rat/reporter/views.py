'''
Views for grab data from testbeds and do integrate.
Created on Mar 27, 2013
@author: cwang
'''
from datetime import datetime
import logging
import traceback

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse

from reporter import models as DB

def build_weeks(request):
    '''
    Give start_date and end_date, filter data from database.
    
    '''

def build_days(request):
    '''    
    '''
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    st = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    et = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')        
    obj = DB.DailyStatus.objects.filter(start_time__startswith  = st,
                                        end_time__startswith = et)
        


