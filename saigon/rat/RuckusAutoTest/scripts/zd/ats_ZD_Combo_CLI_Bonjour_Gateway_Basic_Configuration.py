'''
Created on Mar 21, 2014

@author: chen.tao@odc-ruckuswireless.com
5 testcases

[bonjour gateway default value]
[rules add and del] 
[rules edit]
[rules del]
[rules max 1024]

'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg():
    test_cfgs = []
    
    ######bonjour gateway default value######
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[bonjour gateway default value] Try to del all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))     

    test_name = 'CB_ZD_CLI_Disable_Bonjour_Gateway'
    common_name = '[bonjour gateway default value] Try to disable bonjour gateway.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '[bonjour gateway default value] Check default value is disabled.'
    test_params = {'bonjour_gw_value':'disabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   
 
    test_name = 'CB_ZD_CLI_Enable_Bonjour_Gateway'
    common_name = '[bonjour gateway default value] Try to turn on bonjour gateway before add rules.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '[bonjour gateway default value] Check BG value is enabled.'
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   
    
    ######rules add######
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules add and del] Try to del all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))     
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules add and del] Add a new rule.'
    test_params = {'tag_new':True, 'service':'AirDisk', 'from_vlan':100, 'to_vlan':200, 'note':'Add first service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
   
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules add and del] Try to add the same rule.'
    test_params = {'tag_new':True, 'tag_nagative':True, 'service':'AirDisk', 'from_vlan':100, 'to_vlan':200, 'note':'Add the same service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules add and del] Del the existing rule.'
    test_params = {'tag_del':True, 'service':'AirDisk', 'from_vlan':100, 'to_vlan':200}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules add and del] Try to del all rules after test.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))     
    ######rules edit######
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Try to del all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Add a new rule for editing.'
    test_params = {'tag_new':True, 'service':'AirPlay', 'from_vlan':10, 'to_vlan':20, 'note':'Add first service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
      
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Change service type.'
    test_params = {'tag_edit':True, 'service':'AirPlay', 'from_vlan':10, 'to_vlan':20, 
                   'service_changeto':'AirPrint', 'from_vlan_changeto':10, 'to_vlan_changeto':20, 
                   'note':'Edit the existing service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Change from-vlan.'
    test_params = {'tag_edit':True, 'service':'AirPrint', 'from_vlan':10, 'to_vlan':20, 
                   'service_changeto':'AirPrint', 'from_vlan_changeto':100, 'to_vlan_changeto':20, 
                   'note':'Edit the existing service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Change to-vlan.'
    test_params = {'tag_edit':True, 'service':'AirPrint', 'from_vlan':100, 'to_vlan':20, 
                   'service_changeto':'AirPrint', 'from_vlan_changeto':100, 'to_vlan_changeto':200, 
                   'note':'Edit the existing service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Edit the existing rule with wrong parameter.'
    test_params = {'tag_edit':True, 'tag_nagative':True, 'service':'AirPrint', 'from_vlan':100, 'to_vlan':200, 
                   'service_changeto':'AirPrint', 'from_vlan_changeto':30, 'to_vlan_changeto':30, 
                   'note':'Edit the existing service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules edit] Try to del all rules after test.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
    ######rules del######    

    #CLI has problem on version 9.7.0.0.157
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules del] Try to del all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules del] Try to del the nonexisting rule, it should fail.'
    test_params = {'tag_del':True, 'tag_nagative':True, 'input_rule_id':1}
    test_cfgs.append((test_params, test_name, common_name, 2, False))      
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules del]Add a rule.'
    test_params = {'tag_new':True, 'service':'AirPlay', 'from_vlan':10, 'to_vlan':20, 'note':'Add service rule the second times.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules del] Add another rule.'
    test_params = {'tag_new':True, 'service':'AirPrint', 'from_vlan':10, 'to_vlan':20, 'note':'Add another service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Enable_Bonjour_Gateway'
    common_name = '[rules del] Turn on bonjour gateway.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '[rules del] Check value is enabled.'
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules del] Del all rules to disable bonjour gateway.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '[rules del] Check default value is not disabled after remove all rules.'
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))  
    
    ######rules max 1024######
    ###Chen.tao 2014-09-19, in bug ZF-5523, it is modified from 1024 to 128
    ###The testcase name is changed accordingly
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules max num]Try to del all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_CLI_Mutiple_Services_Rule'
    common_name = '[rules max num]Continuously add rules to the max num.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))

    #On CLI, service rules can reach more than 1024, it's a bug.
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules max num]Try to add one more rules, it should fail.'
    test_params = {'tag_new':True, 'tag_nagative':True, 'service':'AirPlay', 'from_vlan':4000, 'to_vlan':4001, 'note':'Add one more service rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules max num]Del an existing rule.'
    test_params = {'tag_del':True, 'service':'AirPlay', 'from_vlan':10, 'to_vlan':20}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules max num]Add the deleted rule.'
    test_params = {'tag_new':True, 'service':'AirPlay', 'from_vlan':10, 'to_vlan':20, 'note':'Add the deleted rule.'}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_CLI_Enable_Bonjour_Gateway'
    common_name = '[rules max num] Turn on bonjour gateway.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '[rules max num] Check value is enabled.'
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '[rules max num]Try to del all rules after test.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
    
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
        ts_name = "Bonjour_Gateway_Basic_Configuration" 
            
    ts = testsuite.get_testsuite(ts_name,'Bonjour_Gateway_Basic_Configuration',combotest=True)
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



