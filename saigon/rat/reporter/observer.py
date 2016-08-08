'''
Request for listener information including AutoExectuion, TestBeds, TestSuites.
Created on Apr 25, 2013
@author: cwang
'''
from datetime import datetime

import json_response
from RuckusAutoTest import models as dbhlp

def get_test_suites_name_list(request):
    '''
    Get suites name list for comparison.
    '''    
    return json_response.json_response([obj.name 
                                        for obj in dbhlp.TestSuite.objects.only('name')])

def get_test_suites_by_name_list(request):
    '''
    Get test suites.
    '''
    names = request.POST.getlist('suites')    
    _ll = []    
    for name in names:
        obj = dbhlp.TestSuite.objects.filter(name=name)
        if obj:
            obj = obj[0]
            _ll.append((obj.name, obj.description, obj.config, obj.xtype))
    
    print _ll 
    
    return json_response.json_response(_ll)

def get_test_cases_identifier_list(request):
    '''
    Identifier list including test_name, common_name, test_suite_name
    '''
    return json_response.json_response([(obj.suite.name, 
                                         obj.test_name, 
                                         obj.common_name) 
                                         for obj in dbhlp.TestCase.objects.only('test_name')])

def get_test_cases_by_identifier_list(request):
    '''
        identifiers format as:
            [(suite_name, test_name, common_name),
             (suite_name, test_name, common_name),
            ]
    '''
    identifiers = request.POST.getlist("identifiers")    
    _ll = []
    for ids in identifiers:        
        (suite_name, test_name, common_name) = eval(ids)
        obj = dbhlp.TestCase.objects.filter(suite__name=suite_name,
                                            test_name = test_name, 
                                            common_name = common_name 
                                            )
        if obj:
            obj = obj[0]
            _ll.append((suite_name, test_name, common_name, 
                        obj.test_params,
                        obj.seq,
                        1 if obj.enabled else 0,
                        obj.exc_level,
                        1 if obj.is_cleanup else 0
                        ))
    
    return json_response.json_response(_ll)
            
def get_auto_config():
    pass

def get_testbeds(request):
    '''
    Return all of Logical Testbed.
    '''
    tbs = dbhlp.Testbed.objects.all()
    _ll = []
    for tb in tbs:
        _ll.append((tb.name, 
                    tb.tbtype.name, 
                    tb.location, 
                    tb.owner, 
                    tb.resultdist, 
                    tb.description, 
                    tb.config))
        
    return json_response.json_response(_ll)


def get_daily_data(request):
    tblist = request.POST.getlist("tblist")
    for tbname in tblist:
        pass

def get_batchs_identifiers(request):
    '''
    Identifiers including:
        Testbed name, build, timestamp, start_time, end_time
    '''
    batchs = dbhlp.Batch.objects.all()    
    res = json_response.json_response([(obj.testbed.name, 
                                         obj.build.version, 
#                                         obj.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 
                                         obj.start_time.strftime("%Y-%m-%d %H:%M:%S"), 
                                         obj.end_time.strftime("%Y-%m-%d %H:%M:%S")
                                         ) 
                                        for obj in batchs])        
    return res

def get_batchs_by_identifiers(request):
    identifiers = request.POST.getlist("identifiers")  
    _ll = []    
    for id in identifiers:
        (name, version, start_time, end_time) = eval(id)
        st = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        et = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')        
        obj = dbhlp.Batch.objects.filter(testbed__name =name, 
                                         build__version = version,                                         
                                         start_time__startswith  = st,
                                         end_time__startswith = et
                                         )
        if obj:                           
            obj = obj[0]                             
            complete = "Complete: %s" % ('Y' if obj.complete else 'N')
            total_tests = 'Cases:%s' % obj.total_tests
            test_pass = 'Pass: %s' % obj.tests_pass
            tests_fail = 'Fail:%s' % obj.tests_fail
            test_errors = 'Error:%s' % obj.test_errors
            suites = obj.suite_list()
            
            result = "[%s\n%s\n%s\n%s\n%s]" % (complete, total_tests, 
                                           test_pass, tests_fail, 
                                           test_errors)
            
            _ll.append((name, version, start_time, end_time,result, suites))
            
    
    return json_response.json_response(_ll)
