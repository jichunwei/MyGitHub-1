import re
import os
import sys

import libZD_TestSuite as testsuite

from RuckusAutoTest.common import Ratutils
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(cfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_Initial_ENV'
    common_name = 'Initial testing environment'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_Scaling_Download_SIMAP_Image'
    common_name = 'Download SIMAP image from version server.'
    param_cfg = dict(simap_build_stream=cfg['simap_build_stream'],
                     simap_bno=cfg['simap_bno'],
                     file_path=cfg['file_path'],
                     )    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Find_SimAP_Server'
    common_name = 'Find a SimAP Server'
    param_cfg = dict(vm_ip_addr=cfg['vm_ip_addr']                                                        
                     )    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_Resolve_RuckusAP_Models'
    common_name = 'Resolve models of RuckusAPs'
    param_cfg = dict(vm_ip_addr=cfg['vm_ip_addr'],
                     tftpserver=cfg['tftpserver'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
                
    test_name = 'CB_Scaling_Install_SIMAPs_By_Models'
    common_name = 'Install SIMAPs by models of RuckusAPs'
    param_cfg = dict(vm_ip_addr=cfg['vm_ip_addr'],
                     tftpserver=cfg['tftpserver'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_WLANs'
    common_name = 'Different WLANs can work under different SimAPs'
    param_cfg = dict(wlans=cfg['wlans'],
                     target_station=cfg['target_sta'],)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_Scaling_Initial_ENV'
    common_name = 'Clean testing environment'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
            
    return test_cfgs

def create_test_suite(**kwargs):
    attrs = dict (
        interactive_mode=True,
        sta_id=0,
        targetap=False,
        testsuite_name=""
    )
    cfg = {}
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    create_test_parameters(tbcfg, attrs, cfg)
    ts_name = 'Sanity check SIMAPs'
    ts = testsuite.get_testsuite(ts_name, 'Verify Basic WLANs can perform to SIMAPs and client can assocaite to RuckusAPs', combotest=True)
    test_cfgs = define_test_configuration(cfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
def generate_wlans():    
    wlans = ['psk-wpa-tkip',
             'share-wep128',
             'share-wep64',
             'open-wep64',
             'open-none',
             'open-wep128',
             'psk-wpa-aes',
              ]    
    return wlans 
    
def create_test_parameters(tbcfg, attrs, cfg):
    sta_ip_list = tbcfg['sta_ip_list']    
       
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_ap_list = getActiveAp(ap_sym_dict)        
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    cfg['target_sta'] = target_sta
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else:
        ts_name = "Scaling - daily sanity check"
    
    cfg['testsuite_name'] = ts_name
    
    cfg['wlans'] = generate_wlans()
    
    simap_build_stream = None
    while True:
        simap_build_stream = raw_input("Enter buildstream of simap[i.e, SIM-AP_8.2.0.0_production or SIM-AP_mainline]:")
        
        if re.match('^SIM-AP_([\d\.]+)_production$', simap_build_stream, re.I):
            break;
        
        elif re.match('^SIM-AP_mainline$', simap_build_stream, re.I):
            break
        
        else:
            print "Invalid version:[%s]:" % simap_build_stream
            
    cfg['simap_build_stream'] = simap_build_stream
    
    simap_bno = None
    while True:
        simap_bno = raw_input("Enter build no of SIMAP[i.e 5]:")
        
        if re.match("^[\d]+$", simap_bno):
            break
        else:
            print "Invalid bno[%s]" % simap_bno

    cfg['simap_bno'] = simap_bno            

    vm_ip_addr = None
    while True:
        vm_ip_addr = raw_input("Enter the IP address of SIMAP Server:")
        res = Ratutils.ping(vm_ip_addr)
        
        if res.find("Timeout") == -1:
            break
        else:
            print "Invalid IP address [%s]" % vm_ip_addr

    cfg['vm_ip_addr'] = vm_ip_addr           
            
    tftpserver = None
    while True:
        tftpserver = raw_input("Enter the IP address of tftpserver:")    
        res = Ratutils.ping(tftpserver)
        
        if res.find("Timeout") == -1:
                break
        else:
            print "Invalid IP address [%s]" % tftpserver
    
    cfg['tftpserver'] = tftpserver
    
    file_path = "d:\\\\"
    while True:
        file_path = raw_input("Enter root folder of tftpserver location[%s]" % file_path)
        if not file_path:
            file_path = escape(file_path)
        else:
            file_path = "d:\\\\"
            
        if not os.path.exists(file_path) :
            print "The file[%s] is invalid" % file_path
        else:
            break
    
    cfg['file_path'] = file_path
            

def escape(file_path):
    expr = "[/|\\^\\\\]"
    return re.sub(expr, "\\\\", file_path)
    
if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)