'''
Listen request from observer:
    1) Request for AutoExectuion, Testsuites, TestBeds etc.
    2) Update test requirement.
Created on Apr 25, 2013
@author: cwang
'''

import logging
from datetime import datetime
import urllib

from httplib import HTTPConnection
from django.core import serializers
from django.http import QueryDict

from RuckusAutoTest import models as dbhlp
from reporter import models as DBR

def fetch_test_suites(host='127.0.0.1', port=8009):
    conn = HTTPConnection(host, port)
    try:
        conn.request("get", "/usage/suite_name_list/")    
        res = conn.getresponse()
        data = res.read()    
        suite_name_list = eval(data)
        
        def get_test_suites(suite_name_list):
            not_existed_list = []
            for name in suite_name_list:
                obj = dbhlp.TestSuite.objects.filter(name=name)
                if not obj:
                    not_existed_list.append(name)
            return not_existed_list
        
        q = QueryDict('suites=1').copy()
        q.setlist("suites", 
                  get_test_suites(suite_name_list))   
        conn.request("POST", "/usage/suite_list/", q.urlencode())
        res = conn.getresponse()
        suites = res.read()
        
        def update_test_suites(suites):      
            for (name, description, config, xtype) in suites:        
                ts = dbhlp.TestSuite()
                ts.name = name
                ts.description = description
                ts.config = config
                ts.xtype = xtype
                ts.save(force_insert=True)
                logging.info('Add Test Suite %s' % ts)                        
        
        update_test_suites(eval(suites))
        logging.info('%s: Test Suites Updated DONE.' % host)
    finally:
        conn.close()
    
        
def fetch_test_cases(host='127.0.0.1', port=8009):
    conn = HTTPConnection(host, port)
    try:
        conn.request("get", "/usage/tc_name_list/")    
        res = conn.getresponse()
        data = res.read()        
        tc_name_list = eval(data)
        
        def get_tcs(tc_name_list):
            tcs = []           
            for (suite_name, case_name, common_name) in tc_name_list:
                obj = dbhlp.TestCase.objects.filter(suite__name = suite_name, 
                                                    test_name = case_name,
                                                    common_name = common_name)
                if not obj:
                    tcs.append((suite_name, 
                                case_name, 
                                common_name))
            
            return tcs
        
        
        q = QueryDict('identifiers=1').copy()
        q.setlist("identifiers", 
                  get_tcs(tc_name_list))   
        conn.request("POST", "/usage/tc_list/", q.urlencode())
        res = conn.getresponse()
        test_cases = res.read()        
        test_cases = eval(test_cases)
        
        def update_test_cases(test_cases):
            for (suite_name, 
                 test_name, 
                 common_name, 
                 test_params,
                 seq,
                 enabled,
                 exc_level,
                 is_cleanup) in test_cases:
                suite = dbhlp.TestSuite.objects.filter(name=suite_name)[0]
                tc = dbhlp.TestCase()
                tc.suite = suite
                tc.test_name = test_name
                tc.common_name = common_name
                tc.test_params = test_params
                tc.seq = seq
                tc.enabled = enabled
                tc.exc_level = exc_level
                tc.is_cleanup = is_cleanup
                tc.save(force_insert=True)
                logging.info('Add test case %s' % tc)                             
        
        update_test_cases(test_cases)
        
        logging.info('%s: Update test cases DONE.' % host)
    finally:
        conn.close()

def fetch_batches(host='127.0.0.1', port=8009):
    conn =HTTPConnection(host, port)
    try:
        conn.request('get', "/usage/batch_name_list/")
        res = conn.getresponse()
        data = res.read()        
        batch_name_list = eval(data)        
        def get_batches(batch_name_list):
            not_existed_list = []
            for (tbname, 
                 version,                  
                 start_time, 
                 end_time) in batch_name_list:                
                obj=dbhlp.Batch.objects.filter(testbed__name = tbname,
                                               build__version = version,
                                               start_time__startswith = datetime.strptime(start_time, 
                                                                              "%Y-%m-%d %H:%M:%S"),                                            
                                               end_time__startswith = datetime.strptime(end_time, 
                                                                            "%Y-%m-%d %H:%M:%S")
                                               )
                if not obj:
                    not_existed_list.append((tbname, version, start_time, end_time))
            
            return not_existed_list
    
        
        not_existed_list = get_batches(batch_name_list)
        q = QueryDict('identifiers=1').copy()
        q.setlist("identifiers", 
                  not_existed_list)
        conn.request("POST", "/usage/batch_list/", q.urlencode())
        res = conn.getresponse()
        batchs = res.read()           
        batchs = eval(batchs)
        
        def update_daily_status(batchs, host):            
            for(name, version, start_time, 
                end_time, result, suites) in batchs:
                st = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")                                           
                et = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                
                _ds = DBR.DailyStatus.objects.filter(name = name, 
                                                     version = version,                                                     
                                                     ) 
                if _ds:
                    obj = _ds[0]                                                       
                else: 
                    obj = DBR.DailyStatus()
#                tb = dbhlp.Testbed.objects.filter(name=name)[0]                
#                obj.logicaltb = tb
                obj.name = name
                obj.ipaddr = host                
                obj.version = version                
                obj.start_time = st if st else None                                
                obj.end_time = et if et else None
                obj.status = result
                obj.suites = suites
                                   
                if _ds:#existed, then update it
                    obj.save(force_insert=False, force_update=True)
                    logging.info('Update %s, %s DONE.'  %(name, version))
                else:
                    obj.save(force_insert=True, force_update=False)
                    logging.info('Add %s, %s DONE.'  %(name, version))
                                                
        update_daily_status(batchs, host)
        logging.info('Update [%s:%s] daily status DONE.' % (host, port))
                
    finally:
        conn.close()

def fetch_testbeds(host='127.0.0.1', port=8009):
    conn = HTTPConnection(host, port)
    try:
        conn.request("get", "/usage/tb_list/")    
        res = conn.getresponse()
        data = res.read()
        tbs = eval(data)
        
        def update_testbeds(tbs, host, port):
            for (name, 
                tbtype, 
                location, 
                owner, 
                resultdist, 
                description, 
                config) in tbs:
                tbobj = DBR.LogicalTB.objects.filter(name=name)
                if tbobj:
                    logging.info("Testbed %s existed" % name)
                    continue
                
                tbobj = DBR.LogicalTB()                                
                obj = DBR.PhysicalTB.objects.filter(ipaddr = host, port = port)[0]                                    
                tbobj.name = name
                tbobj.physical = obj
                tbobj.location = location
                tbobj.owner = owner
                tbobj.resultdist = resultdist
                tbobj.description = description
                tbobj.config =config
                try:                    
                    tbobj.save(force_insert=True)
                    logging.info('Add test bed %s DONE.' % name)
                except Exception, e:
                    logging.debug(e.message)                
        
        update_testbeds(tbs, host, port)
           
        logging.info("%s: Update all Testbed DONE." % host)
        
    finally:
        conn.close()

def test():
    print fetch_test_suites()

if __name__ == '__main__':
    test()

            