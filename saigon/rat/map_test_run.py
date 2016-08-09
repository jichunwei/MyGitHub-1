"""
Copyright (C) 2011 Ruckus Wireless, Inc.
@author: An Nguyen - an.nguyen@ruckuswireless.com
@since: Mar 2011

This script support to map the current test runs on your test bed with the current project plans and builds
in Testlinks server.

Example:
    map_test_run.py testbed=odessa.sys build=9.2.0.99 # To get the testruns map for testbed in expected build stream/build no
    map_test_run.py testbed=odessa.sys # To get the testruns map for testbed
    map_test_run.py build=9.2.0.99 # To get the testruns map for expected build stream/build no
    map_test_run.py map_all=True # To get map for all currents testruns
    map_test_run.py map_all=True send_email=True cc=a@c.b;d#e.f # To get map for all currents testruns then email the result to the owner of data base and cc list.
"""

import sys
import time
import logging
from pprint import pprint

import db_env as db

from RuckusAutoTest import models as RATM
from Testlink import models as TLM
from RuckusAutoTest.common import lib_KwList as kwlist


mycfg = {'testbed': '',
         'project': '',
         'build': '',
         'map_all': True,
         'cc': '',
         'send_email': False,
         #@author: Jane.Guo @since: 2013-09 make rat report work need plan parameter
         'plan':''}

def _init(**kwargs):
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
    return mycfg

def map_test_run_for_expected_batch(mycfg):
    trs = _get_testrun_list(mycfg)
    
    matched_trs = 0
    syninfo = {}
    for testrun in trs:
        #@author: Jane.Guo @since: 2013-09 make rat report work need plan parameter
        res = db.update_match_tl_tcid(mycfg['project'], testrun, mycfg['plan'])
        if res == -1:
            print '[UNMATCHED] %s: %s' % (testrun.id, testrun.common_name)
        else:
            matched_trs +=1
            _update_info(syninfo, res)

    print '--------------------------------------------------------------'
    print '\tSync up %s test runs from %s test runs in database' % ( matched_trs, len(trs))
    print '--------------------------------------------------------------'
    pprint(syninfo, None, 1, 4)

    if mycfg['send_email']:
        db.mailSyncUpStatus(**{'cc': mycfg['cc'],
                               'send_email': mycfg['send_email'],
                               'syninfo': syninfo})

def _update_info(syninfo, res):
    key_map = {'e': 'existed',
               'eu': 'existed-unmapped',
               'a': 'added',
               'au': 'added-unmapped',
               'u': 'updated'}
    if res[2] not in syninfo.keys():
        syninfo[res[2]] = {}
    if res[3] not in syninfo[res[2]].keys():
        syninfo[res[2]][res[3]] = {}
    if key_map[res[0]] not in syninfo[res[2]][res[3]].keys():
        syninfo[res[2]][res[3]][key_map[res[0]]] = 1
    else:
        syninfo[res[2]][res[3]][key_map[res[0]]] += 1

def _get_testrun_list(mycfg):
    batch_list = []
    all_batchs = RATM.Batch.objects.all()
    print mycfg
    for batch in all_batchs:
        if mycfg['testbed'] and not mycfg['build']:
            if batch.testbed.name == mycfg['testbed']:
                if batch not in batch_list: batch_list.append(batch)
        elif not mycfg['testbed'] and mycfg['build']:
            if mycfg['build'] in batch.build.version:
                if batch not in batch_list: batch_list.append(batch)
        elif mycfg['testbed'] and mycfg['build']:
            if mycfg['build'] in batch.build.version and batch.testbed.name == mycfg['testbed']:
                if batch not in batch_list: batch_list.append(batch)

    print batch_list
    if batch_list:
        all_test_runs = []
        for batch in batch_list:
            test_runs = RATM.TestRun.objects.filter(batch=batch)
            all_test_runs.extend(test_runs)
        return all_test_runs
    elif mycfg['map_all']:
        all_test_runs = RATM.TestRun.objects.all()
        return all_test_runs

def main(**kwargs):

    try:
        cof = _init(**kwargs)
        map_test_run_for_expected_batch(cof)
    finally:
        pass

if __name__ == '__main__':
    if len(sys.argv) < 1:
        exit(1)
    kwdict = kwlist.as_dict(sys.argv[1:])

    main(**kwdict)