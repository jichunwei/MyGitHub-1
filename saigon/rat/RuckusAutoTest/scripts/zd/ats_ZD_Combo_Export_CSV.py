"""
Verify AP can insert DHCP option82 subopt into DHCP packages.

    Verify AP can insert DHCP option82 subopt into DHCP packages.
    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
    Test Data:
        
    
    expect result: All steps should result properly.
    
    How to:
        1) Remove all configuraton of ZD
        2) Disable all APs' WLAN service
        3) Disable SW DHCP relay
        4) Enable ZD DHCP relay
        5) Create AP instance and enable its WLAN service
        6) Create station.
        7) Create WLAN and enable subopt randomly
        8) Start Tshark on DHCP server and station
        9) Associate station to WLAN, and authenticate if need
        10) Verify station connection
        11) Stop Tshark on DHCP server and station
        12) Verify DHCP package on DHCP server and station
        13) Edit WLAN to disable subopt
        14) jump to step 8 to 12
        15) Enable DHCP relay on SW
        16) Disable DHCP relay on ZD
        15) Enable all APs' WLAN service
    
Created on 2014-03-03
@author: liu.anzuo@odc-ruckuswireless.com
"""

import sys

import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_test_cfg(cfg):
    test_cfgs = []
    
    if cfg.get('access_vlan'):
        pass    

    std_wlan_cfg = {"name" : "opt82-subopt-std-open-none",
                    "ssid" : "opt82-subopt-std-open-none",
                    "auth" : "open",
                    "encryption" : "none",
                    "vlan_id": cfg.get('access_vlan'),
                    }
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% cfg['mesh_ap_tag']
    test_cfgs.append(({'mesh_ap_list':[cfg['mesh_ap_tag']],
                       'for_upgrade_test':False},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP %s' % (cfg['root_ap_tag'])
    test_cfgs.append(({'active_ap': cfg['root_ap_tag'],
                       'ap_tag': cfg['root_ap_tag']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg.get('target_station')}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = 'Create standard open/none WLAN configuration'
    test_cfgs.append(({'wlan_conf':std_wlan_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = 'Associate client to WLAN'
    test_cfgs.append(({'sta_tag': 'sta1',
                        'wlan_cfg': std_wlan_cfg,
                        'start_browser': False,
                        'get_sta_wifi_ip': True,
                        'verify_ip_subnet': False,
                        'is_restart_adapter':False,
                        }, 
                        test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Station_Connectivity'
    common_name = 'Verify client connect to WLAN'
    test_cfgs.append(({'sta_tag': 'sta1',
                       'wlan_cfg': std_wlan_cfg,
                       'status': 'Authorized',
                      }, 
                      test_name, common_name, 0, False))
    

    tc_common_name = 'Verify Exported CSV of currently managed APs'
    
    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = '[%s]edit AP attribute' % tc_common_name
    test_cfgs.append(({'ap_cfg': {'device_name': 'AP_CSV',
                                  'description': 'AP for CSV',
                                  'location': 'ODC Lab',
                                  'mesh_mode': 'root-ap',
                                  'radio_a':{'channel':'153'},  'radio_ng':{'channel':'11'}, 'mac_addr':''},
                       'ap_tag': cfg['root_ap_tag'], 
                       'update_time': 30,},
                      test_name, common_name, 1, False))

    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '[%s]wait all APs connected to ZD' % (tc_common_name)
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Export_Current_Managed_AP_CSV'
    common_name = '[%s]export to CSV' % tc_common_name
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Current_Managed_AP_CSV'
    common_name = '[%s]check CSV' % tc_common_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    tc_common_name = 'Edit columns of currently managed APs'
    
    test_name = 'CB_ZD_Edit_Current_Managed_AP_Columns'
    common_name = '[%s]edit columns' % tc_common_name
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Export_Current_Managed_AP_CSV'
    common_name = '[%s]export to CSV' % tc_common_name
    test_cfgs.append(({'filter': True}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Current_Managed_AP_CSV'
    common_name = '[%s]check CSV' % tc_common_name
    test_cfgs.append(({'filter': True}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Edit_Current_Managed_AP_Columns'
    common_name = '[%s]recover columns' % tc_common_name
    test_cfgs.append(({'show_all':True}, 
                      test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = 'restore AP attribute'
    test_cfgs.append(({'ap_cfg': {'device_name': 'RuckusAP',
                                  'description': '',
                                  'location': '',
                                  'mesh_mode': 'auto',
                                  ''
                                  'radio_a':{'channel':'Auto'},  'radio_ng':{'channel':'Auto'}, 'mac_addr':''},
                       'ap_tag': cfg['root_ap_tag'], 
                       'update_time': 30,},
                      test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station'
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, True))  
    
    return test_cfgs

def _select_ap(ap_sym_dict, ap_type):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic AP from above list for %s: """ % ap_type
    while (True):
        testsuite.showApSymList(ap_sym_dict)
        active_ap = raw_input(select_tips)
        
        if active_ap:
            return active_ap

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    zd1_gui_tag = 'zd1'
    zd1_cli_tag = 'ZDCLI1'

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    if ts_cfg["interactive_mode"]:
        root_ap = _select_ap(ap_sym_dict, 'Root AP')
        mesh_ap = _select_ap(ap_sym_dict, 'Mesh AP')

    tcfg = {'target_station':'%s' % target_sta,
            'all_ap_mac_list': all_ap_mac_list,
            'radio_mode': target_sta_radio,
            'target_ip_list': [server_ip_addr],
            'zd1_gui_tag': zd1_gui_tag,
            'zd1_cli_tag': zd1_cli_tag,
            'ap_default_vlan': '0',
            'mesh_ap_tag': mesh_ap,
            'root_ap_tag': root_ap,
           }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "ZD GUI - Export Currently Managed APs info to CSV"

    ts = testsuite.get_testsuite(ts_name, "ZD GUI - Export Currently Managed APs info to CSV", combotest = True)

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
