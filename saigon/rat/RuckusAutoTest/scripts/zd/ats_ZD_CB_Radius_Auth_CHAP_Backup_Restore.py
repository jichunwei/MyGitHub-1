'''
'''

import sys
import random
import time
import os

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(cfg):
    test_cfgs = []
    ras_cfg = cfg['ras_cfg']

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create RADIUS CHAP authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]},test_name, common_name, 0, False))
    
    #### Full Backup ###
    test_name = 'CB_ZD_Backup'
    common_name = '[Full Backup]Backup System'
    test_cfgs.append(({},test_name, common_name,1,False)) 
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = '[Full Backup]Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Restore'
    common_name = '[Full Backup]Restore the backup file'
    test_cfgs.append(({'restore_type':'restore_everything'},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = '[Full Backup]Verify if authentication server is restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    #### Failover Backup ###
    test_name = 'CB_ZD_Change_System_Name'
    common_name = '[Failover Backup]Change System Name to ruckus-before-backup'
    test_cfgs.append(({'system_name':'ruckus-before-backup'},test_name,common_name,1,False))

    test_name = 'CB_ZD_Backup'
    common_name = '[Failover Backup]Backup System'
    test_cfgs.append(({},test_name, common_name,2,False)) 

    test_name = 'CB_ZD_Change_System_Name'
    common_name = '[Failover Backup]Change System Name to original Ruckus'
    test_cfgs.append(({'system_name':'Ruckus'},test_name,common_name,2,False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = '[Failover Backup]Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Restore'
    common_name = '[Failover Backup]Restore the backup file'
    test_cfgs.append(({'restore_type':'restore_everything_except_ip'},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = '[Failover Backup]Verify if authentication server is restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_System_Name'
    common_name = '[Failover Backup]Verify System Name can not restore'
    test_cfgs.append(({'before_system_name':'ruckus-before-backup','system_name_change':False},test_name, common_name,2,False))
    
    #### Policy Backup ###
    test_name = 'CB_ZD_Change_System_Name'
    common_name = '[Policy Backup]Change System Name to ruckus-before-backup'
    test_cfgs.append(({'system_name':'ruckus-before-backup'},test_name,common_name,1,False))

    test_name = 'CB_ZD_Backup'
    common_name = '[Policy Backup]Backup System'
    test_cfgs.append(({},test_name, common_name,2,False)) 

    test_name = 'CB_ZD_Change_System_Name'
    common_name = '[Policy Backup]Change System Name to original Ruckus'
    test_cfgs.append(({'system_name':'Ruckus'},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = '[Policy Backup]Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Restore'
    common_name = '[Policy Backup]Restore the backup file'
    test_cfgs.append(({'restore_type':'restore_basic_config'},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = '[Policy Backup]Verify if authentication server is restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_System_Name'
    common_name = '[Policy Backup]Verify System Name can not restore'
    test_cfgs.append(({'before_system_name':'ruckus-before-backup','system_name_change':False},test_name, common_name,2,False))

    #clear configuration    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server after test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs


def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'Backup and Restore with radius CHAP configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZD can backup restore by all modes with radius chap configuration', combotest=True)

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)
    
    tcfg = {'ras_cfg': {'server_addr': ras_ip_addr,
                        'server_port' : '1812',
                        'server_name' : ras_name,
                        'radius_auth_secret': '1234567890',
                        'radius_auth_method': 'chap',
                        },
            }
    
    test_cfgs = defineTestConfiguration(tcfg)

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
    createTestSuite(**_dict)
