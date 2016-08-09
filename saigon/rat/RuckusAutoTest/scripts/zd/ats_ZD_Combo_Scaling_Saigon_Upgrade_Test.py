'''
Created on 2010-7-30
@author: cwang@ruckuswireless.com

2011.12.15 modisied by West.Li,
    1,let zd get the upgrade img on the local pc
    2,put the downgrade procedure in front of restore zd to full configuration 
'''
import sys
import re
from string import Template
from pprint import pformat

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = 'get ap number connected with zd'
    param_cfg = dict(timeout = 120, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_case_name='[downgrade zd to a base build]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%sdowngrade zd to Baseline build' % test_case_name
    test_cfgs.append(({'image_file_path': cfg['base_img_file_path'],},
                      test_name, common_name, 0, False))

    test_case_name='[restore the zd to full configuration and make sure the configure is correct]'
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore ZD to full configurations' % test_case_name
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
            
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstal base SIMAP Image to ZD.' % test_case_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['base_sim_ap_img_name'],sim_version=cfg['base_simap_version'])    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build' % test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    #verify dpsk from webui    
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '%sVerify 9999 guest passes under zd webui at base build' % test_case_name
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 1, False))
        
    #verify dpsk from webui    
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '%sVerify 5000 dpsk under zd webui at base build'  % test_case_name    
    test_cfgs.append(( {}, test_name, common_name, 1, False))  
        
    test_case_name='[upgrade zd to target build]'
    
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%supgrade zd to target build' % test_case_name
    test_cfgs.append(({'image_file_path': cfg['target_img_file_path'],},
                      test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to ZD.' % test_case_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['target_sim_ap_img_name'],sim_version=cfg['target_simap_version'])    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_case_name='[verify the configuration after upgrade]'
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build' % test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    #verify dpsk from webui    
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '%sRe-verify 9999 guest passes under zd webui at target build'   % test_case_name  
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 2, False))
    
    
    #verify dpsk from webui    
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '%sRe-verify 5000 dpsk under zd webui at target build'   % test_case_name  
    test_cfgs.append(( {}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore ZD to empty configurations'
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
           
    return test_cfgs 
    

def define_test_params(tbcfg):
    '''
    Please set parameter to what you want, test cases will fetch parameters from it directly.
    '''
    cfg = dict()
    
    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\ZD3000_9.2.0.0.138.tar.gz" )
    cfg['base_img_file_path'] = file    
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\ZD3000_9.3.0.0.76.tar.gz" )
    cfg['target_img_file_path'] = file
    
    #tftp server cfg info    
    cfg['tftpserver'] = '192.168.0.10'
    cfg['file_path'] = 'c:\\tmp'
    cfg['sim_models'] = 'ss2942 ss2741 ss7942 ss7962'
    cfg['timeout'] = 1800 * 3
    
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\full_cfg.bak" )    
    cfg['full_config_path'] = file
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\empty_cfg.bak" )    
    cfg['empty_config_path'] = file  
    
    filename ="9.2.0.0.136.bl7"
    cfg['base_sim_ap_img_name']=filename
    filename ="9.3.0.0.76.bl7"
    cfg['target_sim_ap_img_name']=filename
    
    cfg['base_simap_version'] = '9.2.0.0.136'
    cfg['target_simap_version'] = '9.3.0.0.76'
    
    cfg['target_full_version'] = '9.3.0.0.76'
    cfg['base_full_version'] = '9.2.0.0.138'

    return cfg

def usage():
    '''
    This testsuite is used for testing between downgrade and upgrade, detail as below:
      1) Downgrade from current version[9.x] to 9.2FCS as default method.
      2) Upgrade from 8.2FCS to previous version[9.x].
    '''
    pass

 
def interactive_cfg(cfg):
    '''
    1) Set ZD/SIMAP Version including 9.x and 8.2FCS.
    2) Set simulator AP models.
    '''
    # 9.x ZD version info setting.
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure current ZD version [9.x] build stream/bno'
    print '--------------------------------------------------------------------------------'
    zd_bs_9x = 'ZD3000_9.0.0.0_production'
    tmp = raw_input('Please input current ZD [9.x] build stream default [%s]:' % zd_bs_9x)
    if tmp:
        zd_bs_9x = tmp
    
    cfg['target_build_stream'] = zd_bs_9x
    
    zd_bn_9x = '56'
    tmp = raw_input('Please input current ZD [9.x] build no default [%s]:' % zd_bn_9x)
    if tmp:
        zd_bn_9x = tmp
    
    cfg['target_build_number'] = zd_bn_9x
    
    zd_b_9x = '9.0.0.0'
    tmp = raw_input('Please input current ZD [9.x] build default [%s]:' % zd_b_9x)
    if tmp:
        zd_b_9x = tmp
    cfg['target_stream'] = zd_b_9x

    T = '''9.x ZD version configuration result:
    	build_stream=$target_build_stream,
	build_number=$target_build_number,
	stream=$target_stream
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''
    
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP version [9.x] build stream/bno'
    print '--------------------------------------------------------------------------------'
    sim_bs_9x = 'SIM-AP_9.0.0.0_production'
    tmp = raw_input('Please input current SIMAP version [9.x] build stream default [%s]:' % sim_bs_9x)
    if tmp:
	sim_bs_9x = tmp
    cfg['target_simap_build_stream'] = sim_bs_9x

    sim_bn_9x = '25'
    tmp = raw_input('Please input current SIMAP version [9.x] build no default [%s]:' % sim_bn_9x )
    
    if tmp:
	sim_bn_9x = tmp

    cfg['target_simap_bno'] = sim_bn_9x
    

    T = '''9.x SIMAP version configuration result:
    	build_stream=$target_simap_build_stream,
	build_number=$target_simap_bno,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    #8.2FCS version info setting.
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure ZD version [8.2FCS] build stream/bno'
    print '--------------------------------------------------------------------------------'    
    zd_bs_82fcs = 'ZD3000_8.2.0.1_production'
    tmp = raw_input('Please input ZD [8.2FCS] build stream default [%s]:' % zd_bs_82fcs)
    if tmp:
        zd_bs_82fcs = tmp

    cfg['base_build_stream'] = zd_bs_82fcs

    zd_bn_82fcs = '8'
    tmp = raw_input('Please input ZD [8.2FCS] build no default[%s]:' % zd_bn_82fcs)
    if tmp:
        zd_bn_82fcs = tmp
    
    cfg['base_build_number'] = zd_bn_82fcs

    zd_b_82fcs = '8.2.0.1'
    tmp = raw_input('Please input ZD [8.2FCS] build default [%s]:' % zd_b_82fcs)
    if tmp:
        zd_b_82fcs = tmp
    cfg['base_stream'] = zd_b_82fcs

    T = '''8.2FCS ZD version configuration result:
    	build_stream=$base_build_stream,
	build_number=$base_build_number,
	stream=$base_stream
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP version [8.2FCS] build stream/bno'
    print '--------------------------------------------------------------------------------'
    sim_bs_82fcs = 'SIM-AP_8.2.0.0_production'
    tmp = raw_input('Please input current SIMAP version [8.2FCS] build stream default [%s]:' % sim_bs_82fcs)
    if tmp:
        sim_bs_82fcs = tmp
    cfg['base_simap_build_stream'] = sim_bs_82fcs

    sim_bs_82fcs = '8'
    tmp = raw_input('Please input current SIMAP version [8.2FCS] build no default [%s]:' % sim_bs_82fcs)
    
    if tmp:
        sim_bs_82fcs = tmp

    cfg['base_simap_bno'] = sim_bs_82fcs


    T = '''8.2FCS SIMAP version configuration result:
    	build_stream=$base_simap_build_stream,
	build_number=$base_simap_bno,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP models'
    print '   Input as formatting: ss2942 ss7942 ss2741'
    print '   Splited by whitespace'
    print '--------------------------------------------------------------------------------'

    sim_models = 'ss2942 ss7942 ss2741'
    tmp = raw_input('Please input simulator AP models default [%s]:' % sim_models)
    if tmp:
        sim_models = tmp
    
    cfg['sim_models'] = sim_models

    T = '''8.2FCS/9.x SIMAP model configuration result:
    	models=$sim_models,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''





def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'Image downgrade upgrade with sacling'
    ts = testsuite.get_testsuite(ts_name, 'Image downgrade upgrade with sacling', combotest=True)

    
    param_cfgs = define_test_params(tbcfg)
    #change default configuration by user.
    #interactive_cfg(param_cfgs)
    test_cfgs = define_test_cfg(param_cfgs)
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
    _dict['tbtype'] = 'ZD_Scaling'
    createTestSuite(**_dict)
