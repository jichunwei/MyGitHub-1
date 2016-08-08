"""
from u.Testlink import t_testlink as T
tlc22 = T.get_tlc()
tlc22.say_hello()
t_pp = T.get_plan(tlc22)
(t_cases, xtime, d_cases, n_cases) = T.get_cases(tlc22, t_pp)
tplan = T.get_testplan(t_pp)
T.add_assigned_tests(tplan, t_cases)

# we can use this command, but not needed at this phase
pcases = T.get_projectestcases(tlc22, tplan)
"""

import time
import re
from db_env import *
from pprint import pprint, pformat
from tlc22 import TestlinkClient22 as TLC

# tlc22 = get_tlc()
def get_tlc():
    DEVKEY='RAT-Testlink-DevKey-22'
    PROD_SERVER_URL='http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php'
    tlc22 = TLC.tlc22(devKey=DEVKEY,server_url=PROD_SERVER_URL)
    return tlc22

def get_tlc0():
    DEVKEY='RAT-Testlink-DevKey-22'
    PROD_SERVER_URL='http://172.17.17.20/testlink/lib/api22/xmlrpc.php'
    tlc22 = TLC.tlc22(devKey=DEVKEY,server_url=PROD_SERVER_URL)
    return tlc22

def get_plan(tlc22):
    t_pp = {'project_name':'Zone Director', 'plan_name':'Udaipur 9.2'}
    t_plans = tlc22.get_plan_by_name(**t_pp)
    t_pp['project_id'] =t_plans[0]['testproject_id']
    t_pp['plan_id'] =t_plans[0]['id']
    return t_pp

def get_cases(tlc22, t_pp):
    xtime, t_cases = TLC.clockit(tlc22.get_assigned_tcinfo_brief, t_pp['plan_id'])
    d_cases, n_cases = TLC.list_as_dict(t_cases, 'tc_external_id')
    return (t_cases, xtime, d_cases, n_cases)

def get_testplan(t_pp):
    t_proj = dict(project_id=t_pp['project_id'], project_name=t_pp['project_name'])
    tproject_list = TLM.TestProject.objects.filter(**t_proj)
    if len(tproject_list) == 0:
        tproject = TLM.TestProject(**t_proj)
        tproject.save()
    else:
        tproject = tproject_list[0]
    t_plan = dict(project=tproject,
                  plan_id=t_pp['plan_id'], plan_name=t_pp['plan_name'])
    tplan = TLM.TestPlan.objects.filter(project=tproject,
                                        plan_id=t_pp['plan_id'],
                                        plan_name=t_pp['plan_name'])
    if len(tplan):
        return tplan[0]
    tplan= TLM.TestPlan(**t_plan)
    tplan.save()
    return tplan

def save_projectestcases(project_id, project_cases):
    tproject = TLM.TestProject.objects.get(project_id=project_id)


def get_projectestcases(tlc22, tp, portit=False, suites=[]):
    # get project's top level suite name
    # get test cases for test suite
    project_id = tp.project.project_id 
    top_suites = [(s['id'], s['name']) for s in tlc22.get_project_toplevel_suites(project_id)]
    project_cases = {}
    bad_cases = {}
    t1 = time.clock()
    for s in top_suites:
        s_cases = tlc22.get_cases_of_testsuite(s[0])
        if suites and not s[1] in suites:
            print ">>> skip testsuite ID=%s; NAME=%s; #tc=%d" % (str(s[0]),str(s[1]),len(s_cases))
            continue
        print ">>> process testsuite ID=%s; NAME=%s; #tc=%d" % (str(s[0]),str(s[1]),len(s_cases))
        for tc in s_cases:
            tc_id = tc['id']
            try:
                case_list = tlc22.get_case_by_id(tc_id)
            except Exception, ex:
                print "--- Getting test case (tc_id=%s): Error:\n%s" % (str(tc_id), ex)
                bad_cases[tc_id] = {'error': ex, 'suite_id':s[0], 'suite_name':s[1]}
                continue 
            case = case_list[0]
            tcv_id = case['id']
            case_path = tlc22.get_tc_tree_path(tcv_id)
            tc_external_id=case['tc_external_id']
            pjtc = {
                'tcv_id':tcv_id, 'tc_id':tc_id, 'external_id':tc_external_id,
                'version':case['version'],
                'project_name':case_path['project_name'],
                'suite_name':case_path['suite_path'][-2],
                'common_name':case['name'],
                'suite_path':case_path['suite_path'][0:-2],
                'is_open':case['is_open'], 'active':case['active'],
            }
            print "TestCase XID-%s:%s" % (str(tc_external_id),pformat(pjtc))
            project_cases[tc_external_id] = pjtc
    t2 = time.clock()
    xtime = t2 - t1 # in seconds
    return {'xtime':xtime, 'bad': bad_cases, 'cases': project_cases}

# add_assigned_tests(tp1, t_cases)
def add_assigned_tests(tplan, assigned_cases):
    for case in assigned_cases:
        pltc_list = TLM.PlanTestCase.objects.filter(plan=tplan,
                       # testcase.external_id=case['tc_external_id'],
                       tc_id=int(case['tc_id']), version=int(case['version']),
                   )
        if len(pltc_list) > 0:
            pltc = pltc_list[0]
            print "Existed PlanTest{%s}: %s" % (str(pltc.id), pltc)
            continue
        pjtc = TLM.ProjectTestCase(project=tplan.project,
                  external_id=case['tc_external_id'],
                  project_name=case['tc_tree_path'][0],
                  suite_name=case['tc_tree_path'][-2],
                  common_name=case['tc_tree_path'][-1],
                  suite_path=case['tc_tree_path'][1:-2],
              )
        pjtc.save()
        pltc = TLM.PlanTestCase(plan=tplan, testcase=pjtc,
                  tc_id=case['tc_id'], version=case['version'],
                  tcv_id=case['tcv_id'],
                  is_open=case['is_open'],
                  active=case['active'],
               )
        pltc.save()
        print "Saved PlanTest{%s}: %s" % (str(pltc.id), pltc)



