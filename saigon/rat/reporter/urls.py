'''
Created on Mar 27, 2013
@author: cwang
'''
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'demo/', 'reporter.views.fetch'),
    (r'demo2/', 'reporter.views.test'),
    (r'suite_name_list/', 'reporter.observer.get_test_suites_name_list'), 
    (r'suite_list/', 'reporter.observer.get_test_suites_by_name_list'),
    (r'tc_name_list/', 'reporter.observer.get_test_cases_identifier_list'),
    (r'tc_list/', 'reporter.observer.get_test_cases_by_identifier_list'),
    (r'tb_list/', 'reporter.observer.get_testbeds'),
    (r'batch_name_list/', 'reporter.observer.get_batchs_identifiers'),
    (r'batch_list/', 'reporter.observer.get_batchs_by_identifiers'),
#    (r'weeks/', 'reporter.views.build_weeks'),
)