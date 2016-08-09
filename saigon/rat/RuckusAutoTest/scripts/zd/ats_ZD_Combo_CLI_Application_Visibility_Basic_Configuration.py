'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg():
    test_cfgs = []

    user_app_rule_cfg = {'rule_description':'testtesttest',
                         'dest_ip':'192.168.0.252',
                         'dest_port':'12345',
                         'netmask':'255.255.255.0',
                         'protocol':'tcp'}
    port_mapping_rule_cfg = {'rule_description':'test_test','protocol':'udp','port':'3939'}
    
    denial_policy_cfg = {'policy_description': 'testtest',
                         'policy_name': 'test_app_denial_policy',
                         'rules': [{'application': 'Port', 'rule_description': 11111, 'rule_id': 1},
                                   {'application': 'HTTP hostname', 'rule_description': 'google.cn', 'rule_id': 2}]}
    
    test_name = 'CB_ZD_CLI_Del_User_Defined_App'
    common_name = '[user app with invalid parameters] Delete all user apps.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 1, False))

    user_app_rule_cfg_invalid_name_length = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_name_length['rule_description'] = 'invalid_length_012345678901234567'#33
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with the name length beyond max-length.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_name_length],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    user_app_rule_cfg_invalid_description = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_description['rule_description'] = 'invalid_description_~!@#$%^&*'    
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with invalid description content.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_description],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    user_app_rule_cfg_invalid_dst_ip = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_dst_ip['rule_description'] = 'test_invalid_dest_ip'
    user_app_rule_cfg_invalid_dst_ip['dest_ip'] = '1.1.1.'  
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with invalid destination ip.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_dst_ip],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    user_app_rule_cfg_invalid_dst_port = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_dst_port['rule_description'] = 'test_invalid_dest_port'
    user_app_rule_cfg_invalid_dst_port['dest_port'] = '65536'      
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with invalid destination port.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_dst_port],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    user_app_rule_cfg_invalid_netmask = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_netmask['rule_description'] = 'test_invalid_netmask'
    user_app_rule_cfg_invalid_netmask['netmask'] = '255.255.255.256'       
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with invalid netmask.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_netmask],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    user_app_rule_cfg_invalid_protocol = deepcopy(user_app_rule_cfg)
    user_app_rule_cfg_invalid_protocol['rule_description'] = 'test_invalid_protocol'
    user_app_rule_cfg_invalid_protocol['protocol'] = 'test'      
    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app with invalid parameters] Add a user app with invalid protocol.'
    test_params = {'user_app_cfg':[user_app_rule_cfg_invalid_protocol],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    #The maximum number of User Defined Application is 32.    
    test_name = 'CB_ZD_CLI_Del_User_Defined_App'
    common_name = '[user app max number 32] Delete all user apps.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 1, False))    

    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app max number 32] Add 32 user apps.'
    test_params = {'user_app_num':32}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '[user app max number 32] Add another user app should fail.'
    test_params = {'user_app_cfg':[user_app_rule_cfg],
                     'negative': True,}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Del_User_Defined_App'
    common_name = '[user app max number 32] Delete all user apps after test.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Del_Port_Mapping_Policy'
    common_name = '[port mapping with invalid parameters] Delete all port mapping policies.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 1, False)) 
    
    port_mapping_rule_cfg_invalid_name_length = deepcopy(port_mapping_rule_cfg)
    port_mapping_rule_cfg_invalid_name_length['rule_description'] = 'invalid_length_01234567890123456789012345678901234567890123456789'#65
    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '[port mapping with invalid parameters] Add a port mapping policy with the name length beyond max-length.'
    test_params = {'port_mapping_cfg':[port_mapping_rule_cfg_invalid_name_length],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    port_mapping_rule_cfg_invalid_protocol = deepcopy(port_mapping_rule_cfg)
    port_mapping_rule_cfg_invalid_protocol['rule_description'] = 'test_invalid_protocol'
    port_mapping_rule_cfg_invalid_protocol['protocol'] = 'test'#65
    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '[port mapping with invalid parameters] Add a port mapping policy with invalid protocol'
    test_params = {'port_mapping_cfg':[port_mapping_rule_cfg_invalid_protocol],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    port_mapping_rule_cfg_invalid_port = deepcopy(port_mapping_rule_cfg)
    port_mapping_rule_cfg_invalid_port['rule_description'] = 'test_invalid_port'
    port_mapping_rule_cfg_invalid_port['port'] = '65536'#65
    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '[port mapping with invalid parameters] Add a port mapping policy with invalid port.'
    test_params = {'port_mapping_cfg':[port_mapping_rule_cfg_invalid_port],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_CLI_Del_Port_Mapping_Policy'
    common_name = '[port mapping max number 1024] Delete all port mapping policies.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 1, False))
         
    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '[port mapping max number 1024] Add 1024 port mapping policies.'
    test_params = {'port_mapping_num':1024}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '[port mapping max number 1024] Add another port mapping policy should fail.'
    test_params = {'port_mapping_cfg':[port_mapping_rule_cfg],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))  

    test_name = 'CB_ZD_CLI_Del_Port_Mapping_Policy'
    common_name = '[port mapping max number 1024] Delete all port mapping policies after test.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))
    
    denial_policy_cfg_invalid_name_length = deepcopy(denial_policy_cfg)
    denial_policy_cfg_invalid_name_length['policy_name'] = 'invalid_name_length12345678901234'#33
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[app denial policy with invalid parameters] Add a denial policy with the name length beyond max'
    test_params = {'denial_policy_cfg':[denial_policy_cfg_invalid_name_length],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    denial_policy_cfg_invalid_desc_length = deepcopy(denial_policy_cfg)
    denial_policy_cfg_invalid_desc_length['policy_description'] = 'invalid_desc_length12345678901234'#33
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[app denial policy with invalid parameters] Add a denial policy with the description length beyond max'
    test_params = {'denial_policy_cfg':[denial_policy_cfg_invalid_desc_length],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    denial_policy_cfg_invalid_rule_app = deepcopy(denial_policy_cfg)
    denial_policy_cfg_invalid_rule_app['policy_description'] = 'test_app_denial_policy1'
    denial_policy_cfg_invalid_rule_app['policy_name'] = 'test_app_denial_policy1'
    denial_policy_cfg_invalid_rule_app['rules'][0]['application'] = 'Port1'
    denial_policy_cfg_invalid_rule_app['rules'][1]['application'] = 'HTTP hostname1'
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[app denial policy with invalid parameters] Add a denial policy with invalid rule application'
    test_params = {'denial_policy_cfg':[denial_policy_cfg_invalid_rule_app],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    denial_policy_cfg_invalid_rule_desc = deepcopy(denial_policy_cfg)
    denial_policy_cfg_invalid_rule_desc['policy_description'] = 'test_app_denial_policy2'
    denial_policy_cfg_invalid_rule_desc['policy_name'] = 'test_app_denial_policy2'
    denial_policy_cfg_invalid_rule_desc['rules'][0]['rule_description'] = '65536'
    denial_policy_cfg_invalid_rule_desc['rules'][1]['rule_description'] = 'www.123456789012345678901234.com'#32
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[app denial policy with invalid parameters] Add a denial policy with invalid rule description'
    test_params = {'denial_policy_cfg':[denial_policy_cfg_invalid_rule_desc],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    denial_policy_cfg_invalid_rule_id = deepcopy(denial_policy_cfg)
    denial_policy_cfg_invalid_rule_id['policy_description'] = 'test_app_denial_policy3'
    denial_policy_cfg_invalid_rule_id['policy_name'] = 'test_app_denial_policy3'
    denial_policy_cfg_invalid_rule_id['rules'][0]['rule_id'] = 0
    denial_policy_cfg_invalid_rule_id['rules'][1]['rule_id'] = 32
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[app denial policy with invalid parameters] Add a denial policy with invalid rule id'
    test_params = {'denial_policy_cfg':[denial_policy_cfg_invalid_rule_id],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Del_App_Denial_Policy'
    common_name = '[denial policy max number 32] Delete all app denial policies.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 1, False))
         
    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[denial policy max number 32] Add 32 app denial policies.'
    test_params = {'denial_policy_num':32}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '[denial policy max number 32] Add another app denial policy should fail.'
    test_params = {'denial_policy_cfg':[denial_policy_cfg],'negative': True}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Del_App_Denial_Policy'
    common_name = '[denial policy max number 32] Delete all app denial policies after test.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))
    
    return test_cfgs
def make_test_suite(**kwargs):

    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)
        
    test_cfgs = define_test_cfg()
#----------------------------------------------------------------------------------------------------------
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Application_Visibility_Basic_Configuration" 
            
    ts = testsuite.get_testsuite(ts_name,'Application_Visibility_Basic_Configuration',combotest=True)
#----------------------------------------------------------------------------------------------------------
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)



