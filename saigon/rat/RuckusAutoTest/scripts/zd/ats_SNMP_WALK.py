

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,snmp_version,mib_list):
    test_cfgs = []

    snmp_cfg = tcfg['snmp_cfg']
    snmp_agent_cfg = tcfg['set_snmp_agent_cfg']
    snmp_cfg.update(snmp_agent_cfg)
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V%s'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, 
                      test_name, common_name, 0, False))

    for item in mib_list:       
        test_case_name = item['oid']
        mib_nodes = []
        mib_nodes.append(item)
        test_cfgs.extend(test_process_walk(test_case_name,snmp_cfg,mib_nodes))

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V%s after test'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg': {'version': snmp_version, 'enabled': False}}, 
                      test_name, common_name, 0, False))  

    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs
    
def test_process_walk(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []
    
    test_name = 'CB_SNMP_WALK'
    common_name = '[%s]SNMP WALK'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes},
                      test_name, common_name, 1, False))

    return tcs_cfgs
                          
def define_test_parameters(tbcfg,snmp_version):
    set_snmp_agent_cfg_v2 = {'version': 2,
                             'enabled': True,
                             'ro_community': 'public',
                             'rw_community': 'private',
                             'contact': 'support@ruckuswireless.com',
                             'location': 'shenzhen',
                            }
    set_snmp_agent_cfg_v3 = {'version': 3,
                             'enabled': True,
                             'ro_sec_name': 'ruckus-read',
                             'ro_auth_protocol': 'MD5',
                             'ro_auth_passphrase': '12345678',
                             'ro_priv_protocol': 'DES',
                             'ro_priv_passphrase': '12345678',
                             'rw_sec_name': 'ruckus-write',
                             'rw_auth_protocol': 'MD5',
                             'rw_auth_passphrase': '12345678',
                             'rw_priv_protocol': 'DES',
                             'rw_priv_passphrase': '12345678',
                            }
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
        
    tcfg = {'snmp_cfg': snmp_cfg,             
           }
    if snmp_version ==2:
        tcfg['set_snmp_agent_cfg'] = set_snmp_agent_cfg_v2                
    else:
        tcfg['set_snmp_agent_cfg'] = set_snmp_agent_cfg_v3
       
    
    return tcfg

def get_mib_list(zd_version):
    mib_list = [   
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemInfo'},
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemExpInfo'},
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIPTable'},
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-AP-MIB','oid':'ruckusZDAPConfigTable'},
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANIfTable'},
        {'zd_version':['9.7'],'model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTable'},      
        ]  
    for mib_node in mib_list:
        if zd_version not in mib_node['zd_version']:
            mib_list.remove(mib_node)
    return mib_list
         
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    zd_version_list = ['9.7']
    snmp_version_list = [2,3]
    for zd_version in zd_version_list:
        mib_list = get_mib_list(zd_version)
        for snmp_version in snmp_version_list:    
            tcfg = define_test_parameters(tbcfg,snmp_version)
            ts_name = '%s SNMP WALK Test - SNMP V%s'%(zd_version,snmp_version)
            ts = testsuite.get_testsuite(ts_name, 'SNMP WALK Test - SNMP V%s'%snmp_version, combotest=True)
            test_cfgs = define_test_cfg(tcfg,snmp_version,mib_list)

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
    create_test_suite(**_dict)
    
