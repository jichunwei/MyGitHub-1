""" Test Execution Agent:
    A test runner executes a python module that has a main() function
    with input are modified in rltea_cfg.py.

Usage:

    rltea.py 
    

Interactive Examples:

The configure file (rltea_cfg.py) include the below information:
    #[tl] for the test link auto reports
    server_url = 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php'
    project = 'Zone Director'
    build = '9.5.0.0.36'
    dev_key =  '038812301d663e2712bbbbd3cd28ffa6'
    plan = 'ZD Real life Automation'
    
    #[cf] the email list that the script will email out the results
    mail_server = ''
    mail_to = []
    
    #[tc] the test case list information, base on the usage of the normal tea program's usage
    testcases = {'test case name': 'script_name parameter=parameter',
                 'test case 1 name': 'script1_name parameter=parameter'}

@since 2013
@modified: An Nguyen

"""
import sys
import logging
import inspect
import traceback
import pdb
from pprint import pprint, pformat

import ratenv
from RuckusAutoTest.common import lib_KwList as kwlist
from RatLogger import RatLogger

from update_test_db import *
#from rltea_cfg import *
import rltea_cfg as tcfg


MYNAME = inspect.currentframe().f_code.co_filename


# return module instance
def load_te_module(te_module_name, fromlist = [''], te_root = 'te'):
    if te_module_name.find('.') > 0:
        te_module_path = te_module_name
    elif te_root:
        te_module_path = '%s.%s' % (te_root, te_module_name)
    else:
        te_module_path = te_module_name

    te_module = __import__(te_module_path, fromlist = fromlist)

    return te_module


def main(te_module_name, **kwargs):
    tcfg = dict(idebug = False, rat_log_id = 'tea')
    tcfg.update(kwargs)

    rat_log_id = tcfg['rat_log_id']
    del(tcfg['rat_log_id'])

    if tcfg['idebug']:
        pdb.set_trace()

    del(tcfg['idebug'])

    if tcfg.has_key('te_root'):
        te_root = tcfg['te_root']
        te_module = load_te_module(te_module_name, te_root = te_root)
        del tcfg['te_root']

    elif te_module_name.find('.') > 0:
        te_module = load_te_module(te_module_name, te_root = '')

    else:
        te_module = load_te_module(te_module_name)

    if not hasattr(te_module, 'main'):
        raise Exception('Expected main function in TE module %s' % (te_module_name))

    RatLogger.init_logger(rat_log_id + '_' + te_module_name)

    logging.info("[TEA.Module %s] tcfg:\n%s" % (te_module_name, pformat(tcfg, 4, 120)))

    test_result_tuple = te_module.main(**tcfg)

    logging.info("[TEA.Module %s] Result:\n%s" % (te_module_name, pformat(test_result_tuple, 4, 120)))

    RatLogger.close_logger()

    return test_result_tuple

def update_result_to_testlink(tlc, tcname, result):
    tbuilds = tlc.get_builds_by_plan_name(tcfg.project_name, tcfg.plan_name)
    build_id = ''
    plan_id = ''
    for b in tbuilds:
        if b['name'] == tcfg.build_no:
            build_id = b['id']
            plan_id = b['testplan_id']
    if not build_id or not plan_id:
        return
    
    tcase_id = ''
    tcases = get_assigned_cases(tlc, plan_id)
    for case in tcases:
        if case['tc_tree_path'][-1] == tcname:
            tcase_id = case['tc_id']
            break
    
    if not tcase_id:
        return
    
    res_cfg = {'plan_id': plan_id,
               'build_id': build_id,
               'tc_id': tcase_id,
               'status': 'p' if result == 'PASS' else 'f'}
    
    tlc.report_case_result(**res_cfg)

import time
sender = 'rlauto@ruckuswireless.com'

def send_result_email(tcname, result):
    subject = '%s %s' % (result[0], tcname)
    recver = tcfg.mail_to
    host_info = _get_host_info()
    body = "Dears Testers,\n\n Below is the test result for test case \"%s\":\n" % tcname
    body += 'Time: %s\n' % time.strftime("%Y%m%d%H%M")
    body += 'Result: %s\n' % result[0]
    body += 'Note: %s\n' % result[1]
    body += 'Thanks!'
    try:
        print 'mail subject:"TE:%s %s" to:"%s"' % (host_info, subject, recver)
        utils.send_mail(tcfg.mail_server, recver, sender, subject, body)
    except Exception, e:
        print 'Send mail failed: %s' % (e.message)

def send_error_email(message):
    recver = tcfg.mail_to
    host_info = _get_host_info()
    subject = 'Error alert!'
    body = "Dears Testers,\n\n Please take a look at test bed \"%s\":\n" % host_info
    body += 'Time: %s\n' % time.strftime("%Y%m%d%H%M")
    body += 'Note: %s\n' % message
    body += 'Thanks!'
    try:
        print 'mail subject:"TE:%s %s" to:"%s"' % (host_info, subject, recver)
        utils.send_mail(tcfg.mail_server, recver, sender, subject, body)
    except Exception, e:
        print 'Send mail failed: %s' % (e.message)

def _get_host_info():
    import socket

    hostname = socket.gethostname()
    slist = socket.getaddrinfo(hostname, 80)
    hinfo = [x for x in slist if x[4][0].startswith('172')]
    hinfo = hinfo[0] if hinfo else slist[0]
    if not hinfo:
        return '[%s 0.0.0.0]' % (hostname,)

    return '[%s %s]' % (hostname, hinfo[4][0])

if __name__ == "__main__":
    
    while True:
        reload(tcfg)
        tlc = get_tlc(tcfg.dev_key, tcfg.server_url)
        for name in tcfg.testcases.keys():
            tc_name = name
            tc_info = tcfg.testcases[name].split()
            te_module_name = tc_info[0]
            kwdict = kwlist.as_dict(tc_info[1:])
             
            try:
                test_result_tuple = main(te_module_name, **kwdict)
                try:
                    send_result_email(tc_name, test_result_tuple)
                    update_result_to_testlink(tlc, tc_name, test_result_tuple[0])
                    print "[TEA.TESTRESULT %s]" % (test_result_tuple[0])
                except:
                    raise

            except Exception, e:
                msg = '[%s][Error]: %s' %(tc_name, e.message)
                send_error_email(msg)
                print "\n\n%s" % ('!' * 68)
                ex = traceback.format_exc()
                print ex
            
            time.sleep(tcfg.interval)
        del tlc