'''
Created on 2011-2-28

@author: serena.tan

Description: This script is used to get the data(test plan, builds and assigned test cases) of a project
             from TestLink and update the relevant data(Test projects, Test plans, Project test cases,
             Plan test cases, Test builds) in rat.db.
             The main method is update_test_db().

'''


import db_env
from RuckusAutoTest.common import Ratutils as utils
from Testlink import models as TLM
from RuckusAutoTest import models as RATM
from tlc22 import TestlinkClient22 as TLC

AUTO_CASES_TOP_FOLDER_LIST = ['Automation']


def update_test_db(tlc, project_name, plan_name, email_addr = ''):
    '''
    This method is used to get the data(test plan, builds and assigned test cases) of a project
    from TestLink and update the relevant data(Test projects, Test plans, Project test cases,
    Plan test cases, Test builds) in rat.db.
    Input:
        tlc:             TestlinkClient22 object
        project_name:    name of the project in TestLink
        plan_name:       name of the plan in TestLink
    '''
    try:
        tl_p = get_plan(tlc, project_name, plan_name)

        testproject = update_test_project(tl_p['project_id'], tl_p['project_name'])

        testplan = update_test_plan(tl_p, testproject)

        update_test_builds(tlc, testplan)

        tl_cases = get_assigned_cases(tlc, tl_p['plan_id'])
        print "Totally got %d Assigned Cases in Plan{%s} from TestLink\n" % (len(tl_cases), plan_name)

        updated_suite = []
        not_existed_suite = []
        updated_case = 0
        bad_name_case = []
        
        for case in tl_cases:
            if case['tc_tree_path'][1] not in AUTO_CASES_TOP_FOLDER_LIST:
                continue

            if has_bad_name(case['tc_tree_path']):
                bad_name_case.append(case['tc_tree_path'])
                continue

            suite_name = case['tc_tree_path'][-2]            
            rattestsuite = get_rat_suite(suite_name)
            if rattestsuite == None:
                if suite_name not in not_existed_suite:
                    not_existed_suite.append(suite_name)

                continue

            projectcase = update_test_project_case(testproject, case, None)

            update_test_plan_case(case, testplan, projectcase)

            if suite_name not in updated_suite:
                updated_suite.append(suite_name)

            updated_case += 1

        if len(bad_name_case) and email_addr:
            subject = "Warning when update rat.db from TestLink"
            msg = 'There are %d bad name cases in Plan{%s} of Project{%s} in TestLink:\n' % (len(bad_name_case), plan_name, project_name)
            for i in range(len(bad_name_case)):
                msg = msg + bad_name_case[i] + '\n'
            _send_mail(email_addr, subject, body = msg)

        print '********************************************************************************'
        print 'Updated %s suites with %s cases from TestLink' % (len(updated_suite), updated_case)
        print '================================================================================'
        for suite in updated_suite:
            print suite
        print '********************************************************************************'
        
        print 'There are %s suites not in RAT database:' % len(not_existed_suite)
        print '================================================================================'
        for i in range(len(not_existed_suite)):
            print not_existed_suite[i]
        print '********************************************************************************'
        print 'There are %d bad name cases in TestLink' % len(bad_name_case)
        print '================================================================================'
        if len(bad_name_case):
            for i in range(len(bad_name_case)):
                print bad_name_case[i]
        print '********************************************************************************'

    except Exception, ex:
        if email_addr:
            subject = "Error when update rat.db from TestLink"
            msg = ex.message + '\n\n' + 'Updating blocked!'
            _send_mail(email_addr, subject, body = msg)

        raise Exception(ex.message)


def get_plan(tlc, project_name, plan_name):
    '''
    This method is used to get the information of a plan in a project from TestLink.
    Input:
        tlc:             TestlinkClient22 object
        project_name:    name of the project in TestLink
        plan_naem:       name of the plan in TestLink
    Output:
        a dict of the plan information
    '''
    t_pp = {'project_name': project_name, 'plan_name': plan_name}
    t_plans = tlc.get_plan_by_name(**t_pp)
    for i in range(len(t_plans)):
        if 'message' in t_plans[i].keys():
            raise Exception('Except when get plan from TestLink: %s' % t_plans)

    t_pp['project_id'] = t_plans[0]['testproject_id']
    t_pp['plan_id'] = t_plans[0]['id']
    print "Got Plan{%s} in Project{%s} from TestLink: %s\n" % (t_pp['plan_name'], t_pp['project_name'], t_pp)

    return t_pp


def get_assigned_cases(tlc, plan_id):
    '''
    This method is used to get the assigned cases of a plan from TestLink.
    Input:
        tlc:        a TestlinkClient22 object
        plan_id:    id of the plan in TestLink
    Output:
        a list of the assigned cases in the plan.
    '''
    assigned_cases = tlc.get_assigned_tcinfo_brief(plan_id)
    for i in range(len(assigned_cases)):
        if 'message' in assigned_cases[i].keys():
            raise Exception('Except when get assigned test cases from TestLink: %s' % assigned_cases)

    return assigned_cases


def get_rat_suite(suite_name):
    '''
    This method is used to get a suite from rat.db.
    Input:
        suite_name: name of the suite
    Output:
        a TestSuite object
        None: the suite does not exist in this rat.db
    '''
    ratsuites = RATM.TestSuite.objects.filter(name = suite_name.strip())
    if len(ratsuites) == 0:
        return None

    return ratsuites[0]


def get_rat_case(testsuite, common_name):
    '''
    This method is used to get a case from rat.db.
    Input:
        testsuite:     the TestSuite object which the case belongs to
        common_name:   the common name of the case
    Output:
        a TestCase object
        None: the case does not exist in this rat.db
    '''
    ratcases = RATM.TestCase.objects.filter(suite = testsuite, common_name = common_name)
    if len(ratcases) == 0:
        return None

    return ratcases[0]


def update_test_project(project_id, project_name):
    '''
    This method is used to update the project in 'Test projects' table in rat.db.
    If the project already exists, update it; otherwise, create a new one.
    Input:
        project_id:    id of the project in TestLink
        project_name:  name of the project in TestLink
    Output:
        the TestProject object updated in rat.db
    '''
    cfg = dict(project_id = project_id, project_name = project_name)
    testprojects = TLM.TestProject.objects.filter(project_name = project_name)
    if len(testprojects) > 0:
        print "Project{%s} already exists: %s\n" % (testprojects[0].project_name, testprojects[0])

        tmp = testprojects[0]
        if tmp.project_id != cfg['project_id']:
            tmp.project_id = cfg['project_id']
            tmp.save()

        return tmp

    tproject = TLM.TestProject(**cfg)
    tproject.save()
    print "Added Project{%s}: %s\n" % (tproject.project_name, tproject)

    return tproject


def update_test_project_case(testproject, case, rattestcase = None):
    '''
    The method is used to update the case in 'Project test cases' table in rat.db.
    If the project case already exists, update it; otherwise, create a new one.
    Input:
        testproject:  the TestProject object in rat.db which the project case belongs to
        case:         the assigned case got from TestLink
        rattestcase:  the TestCase object in rat.db which the project case maps to
    Output:
        the ProjectTestCase object updated in rat.db
    '''
    cfg = dict(project = testproject, external_id = case['tc_external_id'], version = case['version'],
               rattestcase = rattestcase, project_name = testproject.project_name, suite_name = case['tc_tree_path'][-2],
               common_name = case['tc_tree_path'][-1], suite_path = str(case['tc_tree_path'][1:-2]))

    projectcases = TLM.ProjectTestCase.objects.filter(external_id = case['tc_external_id'])
    if len(projectcases) > 0:
        tmp = projectcases[0]
        print "ProjectCase{%s} already exists: %s\n" % (str(tmp.external_id), tmp)

        if tmp.project != cfg['project']:
            tmp.project = cfg['project']

        if tmp.rattestcase != cfg['rattestcase']:
            tmp.rattestcase = cfg['rattestcase']

        if str(tmp.version) != cfg['version']:
            tmp.version = cfg['version']

        if tmp.project_name != cfg['project_name']:
            tmp.project_name = cfg['project_name']

        if tmp.suite_name != cfg['suite_name']:
            tmp.suite_name = cfg['suite_name']

        if tmp.common_name != cfg['common_name']:
            tmp.common_name = cfg['common_name']

        if tmp.suite_path != cfg['suite_path']:
            tmp.suite_path = cfg['suite_path']

        tmp.save()
        return tmp

    tprojectcase = TLM.ProjectTestCase(**cfg)
    tprojectcase.save()
    print "Added ProjectCase{%s}: %s\n" % (tprojectcase.common_name, tprojectcase)

    return tprojectcase


def update_test_plan(tl_p, testproject):
    '''
    The method is used to update the plan in 'Test plans' table in rat.db.
    If the plan already exists, update it; otherwise, create a new one.
    Input:
        tl_p:          a dict of the plan information in TestLink
        testproject:   the TestProject object in rat.db which the plan belongs to
    Output:
        the TestPlan object updated in rat.db
    '''
    cfg = dict(project = testproject, plan_id = tl_p['plan_id'], plan_name = tl_p['plan_name'])
    testplans = TLM.TestPlan.objects.filter(**cfg)
    if len(testplans) > 0:
        print "Plan{%s} already exists: %s\n" % (testplans[0].plan_name, testplans[0])

        return testplans[0]

    tplan = TLM.TestPlan(**cfg)
    tplan.save()
    print "Added Plan{%s}: %s\n" % (tplan.plan_name, tplan)

    return tplan


def update_test_plan_case(tl_case, testplan, projectcase):
    '''
    The method is used to update the case in 'Plan test cases' table in rat.db.
    If the case already exists, update it; otherwise, create a new one.
    Input:
        tl_case:      the assigned case got from TestLink
        testplan:     the TestPlan object in rat.db which the case belongs to
        projectcase:  the ProjectTestCase object in rat.db which the case maps to
    Output:
        the PlanTestCase object updated in rat.db
    '''
    cfg = dict(plan = testplan,
               testcase = projectcase,
               tc_id = tl_case['tc_id'],
               version = tl_case['version'],
               tcv_id = tl_case['tcv_id'],
               is_open = tl_case['is_open'],
               active = tl_case['active'],
               )
    plancases = TLM.PlanTestCase.objects.filter(plan = testplan, testcase = projectcase)
    if len(plancases) > 0 :
        tmp = plancases[0]
        print "PlanCase{%s} already exists: %s\n" % (str(tmp.tc_id), tmp)

        if str(tmp.tc_id) != tl_case['tc_id']:
            tmp.tc_id = tl_case['tc_id']

        if str(tmp.version) != cfg['version']:
            tmp.version = cfg['version']

        if str(tmp.tcv_id) != cfg['tcv_id']:
            tmp.tcv_id = cfg['tcv_id']

        if str(tmp.is_open) != cfg['is_open']:
            tmp.is_open = cfg['is_open']

        if str(tmp.active) != cfg['active']:
            tmp.active = cfg['active']

        tmp.save()
        return tmp

    tplancase = TLM.PlanTestCase(**cfg)
    tplancase.save()
    print "Added PlanTest{%s}: %s\n" % (str(tplancase.tc_id), tplancase)

    return tplancase


def update_test_builds(tlc, testplan):
    '''
    The method is used to update the build in 'Test builds' table in rat.db.
    If the build already exists, update it; otherwise, create a new one.
    Input:
        tlc:      a TestlinkClient22 object
        testplan: the TestPlan object in rat.db which the build belongs to
    '''
    tl_builds = tlc.get_builds_by_plan_name(testplan.project.project_name, testplan.plan_name)
    for i in range(len(tl_builds)):
        if 'message' in tl_builds[i].keys():
            raise Exception('Except when get plan from TestLink: %s' % tl_builds)

    print 'Totally got %d Builds in Plan{%s} from TestLink\n.' % (len(tl_builds), testplan.plan_name)
    for build in tl_builds:
        cfg = dict(plan = testplan, build_id = build['id'], build_name = build['name'])
        testbuilds = TLM.TestBuild.objects.filter(**cfg)
        if len(testbuilds) > 0:
            print "Build{%s} already exists: %s\n" % (testbuilds[0].build_name, testbuilds[0])
            continue

        tbuild = TLM.TestBuild(**cfg)
        tbuild.save()
        print "Added Build{%s}: %s\n" % (tbuild.build_name, tbuild)


def has_bad_name(str_list):
    '''
    The method is used to verify whether there is bad chars(chars of 0x00 to 0x08)
    in the string list or not.
    Input:
        str_list:    a list of strings which need to verify
    Output:
        True:    there is bad chars is the string list
        False:   there isn't bad chars in the string list
    '''
    for i in range(len(str_list)):
        for c in range(0x00, 0x09):
            if chr(c) in str_list[i]:
                return True

    return False


def get_tlc(devkey, svrurl):
    '''
    The method is used to create a TestlinkClient22 object to the TestLink server.
    Input:
        devkey: develop key of the TestLink
        svrurl: URL of the TestLink server
    Output:
        the TestlinkClient22 object created
    '''
    tlc = TLC.tlc22(devKey = devkey, server_url = svrurl)
    return tlc


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs

def _send_mail(recver, subject = '', body = '', **kwargs):
    tcfg = dict(mailserver = '172.16.100.20', sender = 'zd.rat@ruckuswireless.com')
    tcfg.update(kwargs)
    host_info = _get_host_info()
    try:
        print 'mail subject:"TE:%s %s" to:"%s"' % (host_info, subject, recver)
        utils.send_mail(tcfg['mailserver'], recver, tcfg['sender'], subject, body)
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


def _help():
    print """
    Description:
        This script is used to get the data(builds and assigned test cases)
    of a plan in a project from TestLink and update the relevant tables(Test
    projects, Test plans, Project test cases, Plan test cases, Test builds)
    in rat.db.

    Procedure:
        + Create a TestLinkClient to the TestLink Server.
        + Get the information of the plan from TestLink.
        + Update the 'Test projects' table in rat.db.
        + Update the 'Test plans' table in rat.db.
        + Get the information of the builds in the plan from TestLink.
        + Update the 'Test builds' table in rat.db.
        + Get assigned cases of the plan from TestLink.
        + Update the 'Project test cases' table in rat.db.
        + Update the 'Plan test cases ' table in rat.db.

    Usage: update_test_db.py [<args>]

    Where <args> are keyword=[value] pair:
        Keyword         What is represent
        -------------   -------------------------------------------------------
        devkey          develop key of TestLink;
                        default='RAT-Testlink-DevKey-22'.
        svrurl          URL of TestLink server;
                        default='http://qa-tms.tw.video54.local/testlink/lib
                        /api22/xmlrpc.php'.
        project_name    name of the project in TestLink;
                        default='Zone Director'.
        plan_name       name of the plan in TestLink;
                        default='Udaipur 9.2'.
        email_addr      the address to which the message will be sent when error
                        occurs.
        help            print the help information
    """


if __name__ == "__main__":
    import sys
    from RuckusAutoTest.common.lib_KwList import as_dict

    conf = dict(devkey = 'RAT-Testlink-DevKey-22',
                svrurl = 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php',
                project_name = 'Zone Director',
                plan_name = 'Udaipur 9.6',
                email_addr = ''
                )

    _dict = as_dict(sys.argv[1:])
    conf.update(_dict)

    if conf.has_key('help'):
        _help()
        sys.exit(1)

    tlc = get_tlc(conf['devkey'], conf['svrurl'])
    update_test_db(tlc, conf['project_name'], conf['plan_name'], conf['email_addr'])

