'''
9.5 Xian Feature
Manual Available Channel Selection
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = [] 
    test_name = 'CB_ZD_Set_Parameter_For_Manual_Available_Channel_Selection'
    common_name = 'init test parameter for Manual channel selection'
    param_cfg = {'tftp_dir':tcfg['tftp_dir']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Create_AP_Group'
    common_name = 'create one ap group %s'%tcfg['ap_group_name']
    param_cfg = {'name':tcfg['ap_group_name'],'an':{},'gn':{}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_case_name = '[Signal Band AP Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'single_band_ap_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    
    test_case_name = '[Dule Band AP Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'dule_band_ap_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Outdoor ap test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'outdoor_ap_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'allow_indoor_channel':True,'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[US Dfs Channel Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'US_dfs_channel_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Dfs Channel Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'dfs_channel_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Cband Channel Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'cband_channel_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[UK Cband Channel Test]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'uk_cband_channel_test_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Set Up Precedence and Move AP Between Groups]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'precedency_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sverify channel display and deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Backup and Restore]'
    test_name = 'CB_ZD_Get_Manual_Available_Channel_Selection_Parameter'
    common_name = '%sget test parameter for test'%test_case_name
    param_cfg = {'para_key':'backup_para'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sset country code'%test_case_name
    param_cfg = {'unfix_ap':False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%sbackup zd configuration and verify channel deployment'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Restore'
    common_name = '%srestore zd configuration by restore everything'%test_case_name
    param_cfg = {'restore_type':'restore_everything'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deployment_After_Restore'
    common_name = '%sverify channel setting after restore everything'%test_case_name
    param_cfg = {'restore_type':'restore_everything'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Clear_Env_For_Manual_Available_Channel_Selection_test'
    common_name = '%sclear ap channel setting after full restore'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Restore'
    common_name = '%srestore zd configuration by restore everything except ip'%test_case_name
    param_cfg = {'restore_type':'restore_everything_except_ip'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deployment_After_Restore'
    common_name = '%sverify channel setting after restore everything except ip'%test_case_name
    param_cfg = {'restore_type':'restore_everything_except_ip'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Clear_Env_For_Manual_Available_Channel_Selection_test'
    common_name = '%sclear ap channel setting after restore everything except ip'%test_case_name
    param_cfg = {'ap_group':tcfg['ap_group_name']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Restore'
    common_name = '%srestore zd configuration by basic configuration'%test_case_name
    param_cfg = {'restore_type':'restore_basic_config'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deployment_After_Restore'
    common_name = '%sverify channel setting after restore basic config'%test_case_name
    param_cfg = {'restore_type':'restore_basic_config'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Mesh cannot be set up when aps use different channel range]'
    test_name = 'CB_ZD_Manual_Available_Channel_Selection_test'
    common_name = '%smesh test'%test_case_name
    param_cfg = {'mesh_ap_mac':tcfg['mesh_ap_mac'],'root_ap_mac':tcfg['root_ap_mac'],'test_type':'mesh_test'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sZD set Factory to disable mesh' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'set country code'
    param_cfg = {'unfix_ap':False,'country_code':'United states','get_cty_code_from_carribag':False}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    return test_cfgs

def choose_same_model_ap_mac(ap_sym_dict):
    for k1 in ap_sym_dict:
        for k2 in ap_sym_dict:
            if (not k1==k2) and  (ap_sym_dict[k1]['model']==ap_sym_dict[k2]['model']):
                return [ap_sym_dict[k1]['mac'],ap_sym_dict[k2]['mac']]
    raise 'no same model aps to do mesh'

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="Manual Available Channel Selection"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    
    ap_sym_dict = tb_cfg['ap_sym_dict']
    root_ap_mac,mesh_ap_mac=choose_same_model_ap_mac(ap_sym_dict)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="Manual Available Channel Selection"
    default_tftp_dir='D:\\sr_sync\\xml_tar_file'
    tftp_dir = raw_input('please makesure there is tftp server in your TE,please input your tftp server dir,enter directly=[%s]'%default_tftp_dir)
    if not tftp_dir:
        tftp_dir=default_tftp_dir
    tcfg={'tftp_dir':tftp_dir,
          'ap_group_name':'apg_channel_selection',
          'root_ap_mac':root_ap_mac,
          'mesh_ap_mac':mesh_ap_mac,
          }
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "Manual Available Channel Selection", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
