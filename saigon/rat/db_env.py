import re
import sys

#
# setup django environment
#
from django.core import management;
import settings as settings;
management.setup_environ(settings)

from django.contrib.auth.models import User

from RuckusAutoTest.common import Ratutils as utils
from Testlink import models as TLM

AUTO_CASES_TOP_FOLDER_LIST = ['Automation']

tb_map_tl_suite = {
    'Mgmt-vlan NONE': {
        'zd_vlan': None,
        'ap_vlan': None,
    },
    'Mgmt-vlan AP302': {
        'zd_vlan': None,
        'ap_vlan': 302,
    },
    'Mgmt-vlan ZD301 AP302': {
        'zd_vlan': 301,
        'ap_vlan': 302,
    },
    'Mgmt-vlan ZD328': {
        'zd_vlan': 328,
        'ap_vlan': None,
    },
    'Mgmt-vlan ZD328 AP302': {
        'zd_vlan': 328,
        'ap_vlan': 302,
    },    
}

def get_tl_suite_name(testbed):
    '''
    '''
    tb_cof = eval(testbed.config.replace('\n', '').replace('\r', ''))
    if not tb_cof.has_key('mgmt_vlan_config'):
        return 'Mgmt-vlan NONE'

    for key in tb_map_tl_suite.keys():
        if tb_map_tl_suite[key] == tb_cof['mgmt_vlan_config']:
            return key

    return 'Mgmt-vlan NONE'



def get_tl_test_build(project_name, build_ver, plan=""):
    '''
    '''
    all_builds = TLM.TestBuild.objects.all()
    for build in all_builds:
#        if build.build_name == build_ver and build.plan.plan_name == project_name:
        #@author: Jane.Guo @since: 2013-09 make rat report work need plan parameter
        if build.build_name == build_ver and re.match(plan,build.plan.plan_name):  
            return True, build

    return False, build_ver


def get_project_testcase(top_suite, tb_suite, tb_name, common_name, suite_name):
    '''
    '''
    #jluh updated by 2013-09-17
    all_projects_testcases = TLM.ProjectTestCase.objects.all()
    for testcase in all_projects_testcases:
        suite_path = eval(testcase.suite_path)
        
        if suite_path[0] == top_suite and \
        suite_path[1] == tb_suite and \
        suite_path[2] == tb_name and \
        testcase.suite_name == suite_name:
            #added to the prompt of common name from test link and testbed's case.
            #jluh updated by 2013-11-01
            print "+=========================+"
            print "Testlink common name: " + testcase.common_name
            print "Testbed common name: " + common_name
            if testcase.common_name == common_name:
                return True, testcase
            elif 'TCID:' in testcase.common_name and testcase.common_name in common_name:
                return True, testcase
            elif re.search(r'(TCID:.*)\s+\-+\s+(ZF|zf\d+)$', testcase.common_name):
                if re.search(r'(TCID:.*)\s+\-+\s+(ZF|zf\d+)$', testcase.common_name).group(1) in common_name:
                    return True, testcase
            elif re.search(r'(TCID:.*)\s*\-+\s*(ZF|zf\d+)$', testcase.common_name):
                if re.search(r'(TCID:.*)\s*\-+\s*(ZF|zf\d+)$', testcase.common_name).group(1) in common_name:
                    return True, testcase
            elif re.search(r'(TCID:.*)\s*\-*\s*(ZF|zf\d+)$', testcase.common_name):
                if re.search(r'(TCID:.*)\s*\-*\s*(ZF|zf\d+)$', testcase.common_name).group(1) in common_name:
                    return True, testcase
            elif common_name.find('[')!=-1:
                expected_name = _get_combo_name(common_name)            
                if testcase.common_name == expected_name:
                    return True, testcase

    return False, common_name

def get_plantestcase(build, project_testcase):
    '''
    '''
    all_plantestcases = TLM.PlanTestCase.objects.filter(testcase = project_testcase)
    for testcase in all_plantestcases:
        if testcase.plan == build.plan:
            return True, testcase

    return False, build.plan.plan_name



_trm_info = "%s   Testrun ID: [%s]\n       common_name: [%s]\n       tc_id: [%s]"

def update_test_run_map(config):
    '''
    '''
    result = -1
    
    unmapped_combo_case(config)
    
    try:
        exist_cases = TLM.TestRunMap.objects.filter(testrun = config['testrun'])
        
        if len(exist_cases) > 0 and config.has_key('plantestcase'):
            for case in exist_cases:
                if case.plantestcase == config['plantestcase']:
                    result = ['e', case.id, case.plantestcase.plan.plan_name,
                              case.testrun.batch.build.version]
                    print _trm_info % ('EXISTED',
                                       config['testrun'].id,
                                       config['testrun'].common_name,
                                       config['plantestcase'].tc_id)

                else:
                    case.plantestcase = config['plantestcase']
                    case.save()
                    result = ['u', case.id, case.plantestcase.plan.plan_name,
                              case.testrun.batch.build.version]
                    print _trm_info % ('UPDATED',
                                       config['testrun'].id,
                                       config['testrun'].common_name,
                                       config['plantestcase'].tc_id)


        elif len(exist_cases) > 0 and not config.has_key('plantestcase'):
            for case in exist_cases:
                if not case.plantestcase:
                    result = ['eu', case.id, 'None', case.testrun.batch.build.version]
                    print _trm_info % ('EXISTED - UNMAPPED',
                                       config['testrun'].id,
                                       config['testrun'].common_name,
                                       'None')

                else:
                    result = ['e', case.id, case.plantestcase.plan.plan_name,
                              case.testrun.batch.build.version]
                    print _trm_info % ('EXISTED',
                                       config['testrun'].id,
                                       config['testrun'].common_name,
                                       case.plantestcase.tc_id)

        else:
            case = TLM.TestRunMap(**config)
            case.save()
            if case.plantestcase:
                result = ['a', case.id, case.plantestcase.plan.plan_name,
                          case.testrun.batch.build.version]
                status = 'ADDED - MAPPED'
                tcid = config['plantestcase'].tc_id

            else:
                result = ['au', case.id, 'None',
                          case.testrun.batch.build.version]
                status = 'ADDED - UNMAPPED'
                tcid = 'None'

            print _trm_info % (status,
                               config['testrun'].id,
                               config['testrun'].common_name,
                               tcid)

        return result

    except Exception, e:
        print '-------------------------------'
        print e.message
        print '-------------------------------'
        return result

def unmapped_combo_case(config):    
    try:
        if config.has_key('plantestcase'):
            testplan_mapped_cases = TLM.TestRunMap.objects.filter(plantestcase = config['plantestcase'])
            for mapped_case in testplan_mapped_cases:
                if mapped_case == config['testrun']:
                    continue
                if _get_combo_name(mapped_case.testrun.common_name) != _get_combo_name(config['testrun'].common_name):
                    continue
                if mapped_case.testrun.batch != config['testrun'].batch:
                    continue
                if mapped_case.testrun.result == config['testrun'].result:
                    if config['testrun'].result == 'PASS':
                        if config['testrun'].seq > mapped_case.testrun.seq:
#                            import pdb
#                            pdb.set_trace()
#                            mapped_case.plantestcase = ''
                            mapped_case.save()
                    else:
                        if config['testrun'].seq < mapped_case.testrun.seq:
#                            mapped_case.plantestcase = ''
                            mapped_case.save()
                else:
                    if mapped_case.testrun.result == 'PASS':
#                       mapped_case.plantestcase = ''
                       mapped_case.save()
    
    except Exception, e:
        print '-------------------------------'
        print e.message
        print '-------------------------------'

def update_match_tl_tcid(project_name, rat_testrun, plan = ""):
    '''
    #@author: Jane.Guo @since: 2013-09 make rat report work need plan parameter
    '''
    tl_suite_name = get_tl_suite_name(rat_testrun.batch.testbed)
    bs_name = rat_testrun.batch.build.build_stream.name
    rat_suite_name = rat_testrun.suite.name
    top_suite = AUTO_CASES_TOP_FOLDER_LIST[0]
#    top_suite = 'Automation-%s' % bs_name.split('_')[0] if bs_name else 'Automation'        
    res1, tl_build = get_tl_test_build(project_name, rat_testrun.batch.build.version, plan)
    res2, matched_project_testcase = get_project_testcase(
        top_suite.strip(), tl_suite_name, 
        rat_testrun.batch.testbed.name, 
        rat_testrun.common_name,
        rat_suite_name
    )
    if res1 and res2:
        res, matched_plantestcase = get_plantestcase(tl_build, matched_project_testcase)
        if not res:
            config = dict(testrun = rat_testrun)

        else:
            config = dict(testrun = rat_testrun, plantestcase = matched_plantestcase)

    else:
        config = dict(testrun = rat_testrun)

    return update_test_run_map(config)

def update_combo_map():
    """
    """
    all_mapped_cases = TLM.TestRunMap.objects.all()

def getHostInfo():
    '''
    '''
    import socket
    hostname = socket.gethostname()
    slist = socket.getaddrinfo(hostname, 80)
    hinfo = [x for x in slist if x[4][0].startswith('172')]
    hinfo = hinfo[0] if hinfo else slist[0]
    if not hinfo: return '[%s 0.0.0.0]' % (hostname,)

    return '[%s %s]' % (hostname, hinfo[4][0])


def mailSyncUpStatus(subject = 'Sync up RAT test runs completed', body = '', **kwargs):
    '''
    '''
    tcfg = dict(mailserver = '172.16.100.20', sender = 'zd.rat@ruckuswireless.com',
                report = False, cc=False)
    tcfg.update(kwargs)
    if not tcfg['report']: return

    te_info = getHostInfo()
    all_user = User.objects.all()

    recver = [user.email for user in all_user]
    if tcfg['cc']: recver.extend(tcfg['user'].strip().split(';'))

    try:
        print 'mail subject:"TE:%s %s" to:"%s"' % (te_info, subject, recver)
        body = body + '\n--------------------------------------------------------------'
        body = body + '\n      Sync up test runs with plan test cases completed'
        body = body + '\n--------------------------------------------------------------'
        for plan in tcfg['syninfo'].keys():
            body = body + '\n    Plan: %s' % plan
            for build in tcfg['syninfo'][plan].keys():
                body = body + '\n        Build: %s' % build
                for key in tcfg['syninfo'][plan][build].keys():
                    body = body + '\n            %s mapped test runs %s' % \
                    (tcfg['syninfo'][plan][build][key], key)

        body = body + '\n--------------------------------------------------------------'
        print body
        utils.send_mail(tcfg['mailserver'], recver, tcfg['sender'], subject, body)

    except Exception, e:
        print 'sendMail failed: %s' % (e.message)


def _get_combo_name(common_name):
    b_index = common_name.find('[')
    e_index = common_name.find(']')
    if b_index >=0 and e_index > b_index:
        return common_name[b_index+1:e_index]
    else:
        return '' 
