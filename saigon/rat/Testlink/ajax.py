'''
Which is used for handling asynchronized request
Created on Feb 18, 2011
@author: cwang@ruckuswireless.com
'''
import random
import logging
from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from Testlink import models as tl_m
from RuckusAutoTest import models as rat_m


def load_mgmt_setting(request, tr_id, chk):
    '''
    loading management VLAN from database, search rule as:
        ZD management VLAN contains: none, 301, 328 or other.
        AP management VLAN contains: none, 302 or other.
    '''
    if not chk:
        return simplejson.dumps({'zd_mgmt':'none', 'ap_mgmt':'none'})

    try:
        tr = rat_m.TestRun.objects.get(id=tr_id)
        ts_config = tr.batch.testbed.config
        tbi_config = ts_config.replace('\n' , '').replace('\r', '')
        tb_cfg = eval(tbi_config)
        zd_mgmt = 'none'
        ap_mgmt = 'none'
        fnd = False
        if 'Mgmt-vlan NONE' in tb_cfg.keys():
            fnd = True
            zd_mgmt = 'none'
            ap_mgmt = 'none'
        elif 'Mgmt-vlan AP302' in tb_cfg.keys():
            fnd = True
            zd_mgmt = 'none'
            ap_mgmt = '302'
        elif 'Mgmt-vlan ZD301 AP302' in tb_cfg.keys():
            fnd = True
            zd_mgmt = '301'
            ap_mgmt = '302'
        elif 'Mgmt-vlan ZD328' in tb_cfg.keys():
            fnd = True
            zd_mgmt = '328'
            ap_mgmt = 'none'
        elif 'Mgmt-vlan ZD328 AP302' in tb_cfg.keys():
            fnd = True
            zd_mgmt = '328'
            ap_mgmt = '302'

        if not fnd:
            ts_name = tr.batch.testbed.name
            if ts_name.lower().find('zd301')>=0:
                zd_mgmt = '301'
                fnd = True
            elif ts_name.lower().find('zd328')>=0:
                zd_mgmt='328'
                fnd = True

            if ts_name.lower().find('ap302')>=0:
                ap_mgmt='302'
                fnd = True
        if not fnd:
            print "Doesn't find any management VLAN configuraton from test bed, sustain as ZD:none, AP:none"

        return simplejson.dumps({'zd_mgmt':zd_mgmt, 'ap_mgmt':ap_mgmt})

    except Exception, e:
        print e
        return simplejson.dumps({'message':'Search failure'})

dajaxice_functions.register(load_mgmt_setting)

def filter_tl_rat_test_run(request, name, match_case, zd_mgmt, ap_mgmt):

    try:
        if match_case:
            tc_list = tl_m.ProjectTestCase.objects.all()
            tc_list = filter(lambda x: x.common_name.find(name)>=0, tc_list)
        else:
            tc_list = tl_m.ProjectTestCase.objects.filter(common_name__icontains=name)

        tc_list = filter(lambda x: eval(x.suite_path)[1].lower().find(zd_mgmt.lower())>=0, tc_list)
        tc_list = filter(lambda x: eval(x.suite_path)[1].lower().find(ap_mgmt.lower())>=0, tc_list)

        map_list = [{'xid': x.external_id, 'id':x.id, 'name':x.common_name, 'suite_path':x.suite_path} for x in tc_list]
        return simplejson.dumps({'map_list':map_list})
    except Exception, e:
        print e
        return simplejson.dumps({'message':'Search failure'})

dajaxice_functions.register(filter_tl_rat_test_run)

def search_test_run_map(request, batch_id, chk):
    try:
        batch = rat_m.Batch.objects.filter(id=batch_id)[0]
        tc_list = rat_m.TestRun.objects.filter(batch=batch)
        tcid_list = [tc.id for tc in tc_list]
        tc_map_list = tl_m.TestRunMap.objects.all()
        map_list = filter(lambda x: x.testrun.id in tcid_list, tc_map_list)
        sid_list = list(set([(x.testrun.suite.id, x.testrun.suite.name) for x in map_list]))
        map_list = sorted(map_list, key=lambda x: x.testrun.suite.id)

        if chk:
            map_list = [{'sid':x.testrun.suite.id,
                         'id':x.id,
                         'testrun_id':x.get_testrun_id(),
                     'testcase_tc_id':x.get_plantestcase_tc_id(),
                     'common_name':x.get_testrun_common_name(),
                     'plan_name':'',
                     'status':x.get_testrun_result()} for x in map_list if not x.plantestcase]
        else:
            map_list = [{'sid':x.testrun.suite.id,
                         'id':x.id,
                         'testrun_id':x.get_testrun_id(),
                     'testcase_tc_id':x.get_plantestcase_tc_id(),
                     'common_name':x.get_testrun_common_name(),
                     'plan_name':x.get_plantestcase_plan_name(),
                     'status':x.get_testrun_result()} for x in map_list]

        return simplejson.dumps({'map_list':map_list, 'suite_list':sid_list})
    except Exception, e:
       return simplejson.dumps({'message':'Search failure'})

dajaxice_functions.register(search_test_run_map)

