'''
Which is used for handling asynchronized request  
Created on Feb 18, 2011
@author: cwang@ruckuswireless.com
'''
import random
import logging
from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from RuckusAutoTest.models import *

def test(request, chk):
    try:
        return simplejson.dumps({'message': chk})
    except:
        print 'error'    

dajaxice_functions.register(test)



def update(request, id, chk):
    try:        
        id = int(id)
        tc = TestRun.objects.filter(id=id)[0]
        tc.skip_run = chk
        tc.save()
        return simplejson.dumps({'message':'name:%s, common_name:%s, skip_run:%s' % (tc.test_name, tc.common_name, tc.skip_run)})
    except Exception, e:
        return simplejson.dumps({'message':'update failure'})
        
dajaxice_functions.register(update)    


def update_ts(request, bid, sid, chk):
    try:
        bid = int(bid)
        print sid
#        logging.debug(bid)
#        logging.debug(sid)
        ts = TestSuite.objects.filter(name = sid)[0]
        print "ts %s" % ts        
        bh = Batch.objects.filter(id=bid)[0]
        print "bh %s" % bh
        tc_list = TestRun.objects.filter(batch = bh, suite = ts)
        tcid_list = [tc.id for tc in tc_list]
#        print 'tc size:'
#        print len(tc_list)
        for tc in tc_list:
            tc.skip_run = chk
            tc.save()
        return simplejson.dumps({'message':'suite_name:%s, skip_run:%s' % (ts.name, chk), 'tcid_list':tcid_list, 'chk':chk})
    except Exception, e:
        return simplejson.dumps({'message':'update failure'}) 
    
dajaxice_functions.register(update_ts)
#@Author: chen.tao@odc-ruckuswireless.com since 2013-10-09 To support debug option in test report view.
def update_debug(request, id, chk):
    try:        
        id = int(id)
        tc = TestRun.objects.filter(id=id)[0]
        if not chk:
            debug_type = ''
        else:
            debug_type = 't_test' 
        tc.halt_if = debug_type
        tc.save()
        return simplejson.dumps({'message':'name:%s, common_name:%s, halt_if:%s' % (tc.test_name, tc.common_name, tc.halt_if)})
    except Exception, e:
        return simplejson.dumps({'message':'update failure'})
        
dajaxice_functions.register(update_debug)   
def update_ts_debug(request, bid, sid,chk=0):
    try:
        bid = int(bid)
        print sid
#        logging.debug(bid)
#        logging.debug(sid)
        ts = TestSuite.objects.filter(name = sid)[0]
        print "ts %s" % ts        
        bh = Batch.objects.filter(id=bid)[0]
        print "bh %s" % bh
        tc_list = TestRun.objects.filter(batch = bh, suite = ts)
        tcid_list = [tc.id for tc in tc_list]
#        print 'tc size:'
#        print len(tc_list)
        debug_type = ''
        for tc in tc_list:
            tc.halt_if = debug_type
            tc.save()
        return simplejson.dumps({'message':'suite_name:%s, debug_type:%s' % (ts.name, debug_type), 'tcid_list':tcid_list, 'chk':0})
    except Exception, e:
        return simplejson.dumps({'message':'update failure'}) 
    
dajaxice_functions.register(update_ts_debug) 
#@Author: chen.tao@odc-ruckuswireless.com since 2014-09-09 To support debug option in test report view.'

#@Author: chen.tao@odc-ruckuswireless.com since 2013-09-09 To support openning logs in test report view.
def show_cwd(request,tb,bld,ts):
    import os
    import itertools
    import win32api
    cwd=os.getcwd()
    cwd=cwd.replace('rat','runlog')
    ts = ts.split(' ')
    file_name = "".join(itertools.chain(ts))+'.txt'
    cwd=cwd+'\\'+tb+'\\'+bld+'\\'+file_name
    file_object = open(cwd)
    all_the_text = ''
    try:
        all_the_text = file_object.read().replace('\n','<br>').replace(' ','&nbsp;')

    finally:
        file_object.close( )

    return simplejson.dumps({'log_content':all_the_text,'tb':tb,'bld':bld,'file_name':file_name})
dajaxice_functions.register(show_cwd)
#@Author: chen.tao@odc-ruckuswireless.com since 2014-09-09 To support openning logs in test report view.