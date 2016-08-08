'''
Created on 2014-1-24
@author: cwang@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from copy import deepcopy

ldap_server = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
#        'ldap_search_base':'dc=example,dc=net',
        'admin_domain_name': 'cn=Manager,dc=example,dc=net',
        'admin_password': 'lab4man1',
        'type'       :'ldap'
    }

radius_server = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_secret': '1234567890',
        'server_port': '1812',
        'type'       :'radius-auth'
    }

radius_acc_server = {
        'server_name': 'RADIUS Accounting',
        'server_addr': '192.168.0.252',
        'radius_acct_secret': '1234567890',
        'server_port': '1813',
        'type'       :'radius-acct'
    }

ad_server = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'example.net',
        'type'       :'ad'
    }

def build_tcs():
    tcs = []
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Delete All AAA Servers',
                0,
                False
                ))
    
    #AD
    cfg = ad_server
    tcs.extend(gen_ptests(cfg, ttype='AD'))
    
    #LDAP
    cfg = ldap_server
    tcs.extend(gen_ptests(cfg, ttype='LDAP'))          
    

    #Radius
    cfg = radius_server
    tcs.extend((gen_ntests(cfg, ttype='RADIUS')))
    
    #Radius-Account
    cfg = radius_acc_server
    tcs.extend((gen_ntests(cfg, ttype='RADIUS-ACCT')))
    
    #TACACSPlus
#    cfg = {}
#    tcs.extend((gen_ntest(cfg, ttype='TACACSPlus')))
#   

    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Cleanup All AAA Servers',
                0,
                True
                )) 
    return tcs   


def gen_ntests(cfg, ttype='RADIUS'):
    tcs = []
    tcid = "[Test %s without grp-search]" % ttype
    cfg['grp_search']=True
    tcs.append(({'server_cfg_list':[cfg]},
                'CB_ZD_CLI_Test_Negative_AAA',
                '%sCreate %s' % (tcid, ttype),
                1,
                False
                ))
    return tcs

def gen_ptests(cfg, ttype='AD'):
    tcs = []
    tcid = "[Test %s with grp-search enable by default]" % ttype
    tcs.append(({'server_cfg_list':[cfg]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                '%sCreate %s' % (tcid,ttype),
                1,
                False
                ))
    
    tcs.append(({'server_name':cfg['server_name']},
                'CB_ZD_CLI_Get_AAA_Server_By_Name',
                '%sGet %s profile' % (tcid,ttype),
                2,
                False
                ))
    
    tcs.append(({'server_conf':cfg},
                'CB_ZD_CLI_Verify_AAA_Server',
                '%sVerify %s profile' % (tcid,ttype),
                2,
                False
                ))
    
    #@author: tanshixiong #@since: 2015-1-12 @bug: ZF-11605
    cfg_first_copy = deepcopy(cfg)
    cfg_first_copy['grp_search']=False
    tcid = "[Test %s with grp-search disable]" % ttype
    tcs.append(({'server_cfg_list':[cfg_first_copy]},            
                'CB_ZD_CLI_Configure_AAA_Servers',
                '%sUpdate %s' % (tcid, ttype),
                1,
                False
                ))
    
    tcs.append(({'server_name':cfg['server_name']},
                'CB_ZD_CLI_Get_AAA_Server_By_Name',
                '%sGet %s profile' % (tcid, ttype),
                2,
                False
                ))
   
    tcs.append(({'server_conf':cfg_first_copy},
                'CB_ZD_CLI_Verify_AAA_Server',
                '%sVerify %s profile' % (tcid, ttype),
                2,
                False
                ))
    

    #@author: tanshixiong #@since: 2015-1-12 @bug: ZF-11605
    cfg_second_copy = deepcopy(cfg)
    cfg_second_copy['grp_search'] = True
    tcid = "[Test %s with grp-search enable]" % ttype
    tcs.append(({'server_cfg_list':[cfg_second_copy]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                '%sUpdate %s' % (tcid, ttype),
                1,
                False
                ))
    
    tcs.append(({'server_name':cfg['server_name']},
                'CB_ZD_CLI_Get_AAA_Server_By_Name',
                '%sGet %s profile' % (tcid, ttype),
                2,
                False
                ))       
    tcs.append(({'server_conf':cfg_second_copy},
                'CB_ZD_CLI_Verify_AAA_Server',
                '%sVerify %s profile' % (tcid, ttype),
                2,
                False
                ))
    
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "GroupSearchAttribute-Configuration",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)    
    
    ts_name_list = [
                    ('AD or LDAP group search configuration',build_tcs),                                                                          
                    ]    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn()
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
            
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
