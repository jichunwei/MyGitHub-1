from libZD_TestSuite_Voice import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common.lib_Constant import *
from RuckusAutoTest.scripts.zd.spectralink_phone_config import *
from copy import deepcopy, copy

def get_wlan_cfg(ckey, enable_tunnel, enable_vlan, vlan_id):
    wlan_cfg = splk_ph_cfg[ckey].copy()
    if wlan_cfg.has_key('radio'):
        wlan_cfg.pop('radio')
    if wlan_cfg.has_key('mac_addr'):
        wlan_cfg.pop('mac_addr')
    if enable_tunnel:
        wlan_cfg['do_tunnel'] = True
    if enable_vlan:
        wlan_cfg['vlan_id'] = vlan_id
    return wlan_cfg
    
def get_phone_cfg(ckey):
    phone_cfg = {}
    tmp_cfg = splk_ph_cfg.get(ckey)
    for ikey in ['radio', 'ssid', 'mac_addr']:
        phone_cfg[ikey] = tmp_cfg[ikey]
    return phone_cfg

def get_support_dual_band(ap_model):
    if re.search("(7962|7762)", ap_model, re.I):
        return True
    return False

def get_radio_mode_by_ap_model(ap_model):
    rlist = []
    if re.search("(2925|2942|2741)", ap_model, re.I):
        rlist.append('g')
    if re.search("(7942)", ap_model, re.I):
        rlist.append('n')
    if re.search("(7962|7762)", ap_model, re.I):
        rlist.append('n')
        rlist.append('na')
    return rlist
    
def get_wgs_type_by_radio_and_ap_model(radio_mode, ap_model):
    if radio_mode == 'g':
        wgs_type = 'bg'
    elif radio_mode == 'n':
        if re.search("(7962|7762)", ap_model):
            wgs_type = 'ng_na'
        else:
            wgs_type = 'ng'
    elif radio_mode == 'na':
        wgs_type = 'na_ng'
    return wgs_type

def get_wgs_cfg(wgs_type, name='SPLK-GROUP',channel='11'):
    wgs_cfg = {'name':name, 'description':'', 'ap_rp':{}}
    if wgs_type =='bg':
        wgs_cfg['ap_rp']['bg'] = dict(wlangroups=name,channel=channel)
    elif wgs_type == 'ng':
        wgs_cfg['ap_rp']['ng'] = dict(wlangroups=name,channel=channel)
    elif wgs_type == 'ng_na':
        wgs_cfg['ap_rp']['ng'] = dict(wlangroups=name,channel=channel)
        wgs_cfg['ap_rp']['na'] = dict(default='EmptyWlanGroup')
    else:
        wgs_cfg['ap_rp']['na'] = dict(wlangroups=name,channel=channel)
        wgs_cfg['ap_rp']['ng'] = dict(default='EmptyWlanGroup')
    return wgs_cfg

def define_test_cfg(**kwargs):#active_ap, wgs_type, enable_tunnel, enable_vlan, vlan_id='55'):
    fcfg = dict( data_vlan_id = '66',
                 video_vlan_id = '77',
                 voice_vlan_id = '55',
                 ap_tag_1 = 'dut_ap_1',
                 ap_tag_2 = 'dut_ap_2',
                 sta_tag_1 = 'sniffer_sta',
                 sta_tag_2 = 'bg_sta_1',
                 sta_tag_3 = 'bg_sta_2',
                 data_wlan_1 = 'Data-Wifi-1',
                 data_wlan_2 = 'Data-Wifi-2',
                 video_wlan = 'Video-Wifi',
                 zapd_sta_1 = '192.168.66.10',
                 zapd_sta_2 = '192.168.66.20',
                 wgs_name_1 = 'SPLK_GROUP_1',
                 wgs_name_2 = 'SPLK_GROUP_2',
                 phone_list = [],
                 reset_db='0',
                 roaming_db='25',
                 repeat=10,
                 infname='airpcap_any',
                 duration=1500,
                 criterion=dict(uplink=250,downlink=250,auth=250))
    fcfg.update(kwargs)
    if fcfg['wgs_type'] in ['bg', 'ng', 'ng_na']:
        ch_list = ['1','11']
    else:
        ch_list = ['36','48']    
    wgs_cfg_1 = fcfg['wgs_cfg_1'] = get_wgs_cfg(fcfg['wgs_type'], name=fcfg['wgs_name_1'], channel=ch_list[0])
    wgs_cfg_2 = fcfg['wgs_cfg_2'] = get_wgs_cfg(fcfg['wgs_type'], name=fcfg['wgs_name_2'], channel=ch_list[1])
    test_cfg = list()
    if fcfg['wgs_type'] in ['bg', 'ng', 'ng_na', 'na_ng']:
        test_cfg.extend(
        [ ( dict({}), 
            "CB_ZD_Remove_All_Config",
            "Remove all configuration on ZD", 0, False),
          ( dict(wgs_cfg=dict(name='EmptyWlanGroup', description='EmptyWlanGroup')),
            "CB_ZD_Create_Empty_Wlan_Group",
            "Create a wlan group [EmptyWlanGroup]", 0, False),
          ( dict({}),
            "CB_ZD_Assign_All_APs_To_Empty_Wlan_Group",
            "Assign all APs to empty wlan group", 0, False),
          ( dict(wgs_cfg=wgs_cfg_1),
            "CB_ZD_Create_Wlan_Group",
            "Create a wlan group [%s] on ZD" % fcfg['wgs_name_1'], 0, False),
          ( dict(wgs_cfg=wgs_cfg_2),
            "CB_ZD_Create_Wlan_Group",
            "Create a wlan group [%s] on ZD" % fcfg['wgs_name_2'], 0, False),
          ( dict(active_ap=fcfg['shielding_box_cfg']['box1']['dut_ap'], ap_tag=fcfg['ap_tag_1']),
            "CB_ZD_Create_Active_AP",
            "Create active AP of shielding box1", 0, False),
          ( dict(active_ap=fcfg['shielding_box_cfg']['box2']['dut_ap'], ap_tag=fcfg['ap_tag_2']),
            "CB_ZD_Create_Active_AP",
            "Create active AP of shielding box2", 0, False),
          ( dict(ap_tag=fcfg['ap_tag_1'],wgs_cfg=wgs_cfg_1),
            "CB_ZD_Config_Wlan_Group_On_AP",
            "Assign wlan group on active AP of shielding box1", 0, False),
          ( dict(ap_tag=fcfg['ap_tag_2'],wgs_cfg=wgs_cfg_2),
            "CB_ZD_Config_Wlan_Group_On_AP",
            "Assign wlan group on active AP of shielding box2", 0, False),
          ( get_wlan_cfg(fcfg['data_wlan_1'], False, True, fcfg['data_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % fcfg['data_wlan_1'], 0, False),
          ( get_wlan_cfg(fcfg['data_wlan_2'], False, True, fcfg['data_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % fcfg['data_wlan_2'], 0, False),
          ( get_wlan_cfg(fcfg['video_wlan'], False, True, fcfg['video_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % fcfg['video_wlan'], 0, False),
          ( dict(wlan_list=[fcfg['data_wlan_1'],fcfg['video_wlan']],wgs_cfg=wgs_cfg_1),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Configure wlan [%s] and [%s] on wlan group [%s]" % (fcfg['data_wlan_1'], fcfg['video_wlan'], wgs_cfg_1['name']), 0, False),
          ( dict(wlan_list=[fcfg['data_wlan_2'],fcfg['video_wlan']],wgs_cfg=wgs_cfg_2),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Configure wlan [%s] and [%s] on wlan group [%s]" % (fcfg['data_wlan_2'], fcfg['video_wlan'], wgs_cfg_2['name']), 0, False),
          ( dict(sta_ip_addr=fcfg['sf_sta_ip_addr'], sta_tag=fcfg['sta_tag_1']),
            "CB_ZD_Create_Station",
            "Create a station [%s] for sniffer packets" % fcfg['sta_tag_1'], 0, False),            
          ( dict(sta_ip_addr=fcfg['bg_sta1_ip_addr'], sta_tag=fcfg['sta_tag_2']),
            "CB_ZD_Create_Station",
            "Create a station [%s] for back ground traffic " % fcfg['sta_tag_2'], 0, False),
          ( dict(sta_ip_addr=fcfg['bg_sta2_ip_addr'], sta_tag=fcfg['sta_tag_3']),
            "CB_ZD_Create_Station",
            "Create a station [%s] for back ground traffic" % fcfg['sta_tag_3'], 0, False),
          ( dict(sta_tag = fcfg['sta_tag_3'], wlan_cfg=get_wlan_cfg(fcfg['data_wlan_1'], False, True, fcfg['data_vlan_id'])),
            "CB_ZD_Associate_Station_1",
            "Back ground station [%s] associate to data wlan" % fcfg['sta_tag_3'], 0, False),
          ( dict(sta_tag = fcfg['sta_tag_3']),
            "CB_ZD_Get_Station_Wifi_Addr_1",
            "Get Wifi address on back ground station [%s]" % fcfg['sta_tag_3'], 0, False), 
          ( dict(sta_tag = fcfg['sta_tag_2'], wlan_cfg=get_wlan_cfg(fcfg['data_wlan_2'], False, True, fcfg['data_vlan_id'])),
            "CB_ZD_Associate_Station_1",
            "Back ground station [%s] associate to data wlan" % fcfg['sta_tag_2'], 0, False),
          ( dict(sta_tag = fcfg['sta_tag_2']),
            "CB_ZD_Get_Station_Wifi_Addr_1",
            "Get Wifi address on back ground station [%s]" % fcfg['sta_tag_2'], 0, False),                 
        ])
        test_cfg.extend(define_test_cfg_by_phone_list(**fcfg))
        test_cfg.extend(
        [
          ( dict(wlan_list=[fcfg['data_wlan_1'],fcfg['video_wlan']],wgs_cfg=wgs_cfg_1),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove data and video wlans on wlan group [%s]" % wgs_cfg_1['name'], 0 ,False),
          ( dict(wlan_list=[fcfg['data_wlan_2'],fcfg['video_wlan']],wgs_cfg=wgs_cfg_2),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove data and video wlans on wlan group [%s]" % wgs_cfg_2['name'], 0 ,False),
        ])              

    return test_cfg

def define_test_cfg_by_phone_list(**kwargs):
    fcfg = dict(voice_vlan_id = '55', 
                phone_list=['8020WEP', '8020WPA', '8020WPA2'],
                expected_dtim='2',
                expected_directed_thr='disabled',
                if_name='Wireless Network Connection',
                tos="0xa0",
                proto="tcp",
                up_speed=1,
                dn_speed='')
    fcfg.update(kwargs)
    phone_test_cfg = []
    roaming_cfg = deepcopy(fcfg['shielding_box_cfg'])
    roaming_cfg['box1']['db']= roaming_cfg['box2']['db'] = fcfg['roaming_db']
    roaming_cfg['repeat'] = fcfg['repeat']
    for phone in fcfg['phone_list']:
        test_phone_param = get_phone_cfg(phone)
        test_phone_param['ap_tag'] = fcfg['ap_tag_1']
        roaming_cfg['phone']=phone
        test_roaming_cfg=deepcopy(roaming_cfg)     
        phone_test_cfg.extend(
          [
          ( get_wlan_cfg(phone, fcfg['enable_tunnel'], fcfg['enable_vlan'], fcfg['voice_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % phone, 0, False),
          ( dict(wlan_list=[phone],wgs_cfg=fcfg['wgs_cfg_1']),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Config wlan[%s] on wlan group [%s]" % (phone,fcfg['wgs_cfg_1']['name']), 0, False),
          ( dict(wlan_list=[phone],wgs_cfg=fcfg['wgs_cfg_2']),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Config wlan[%s] on wlan group [%s]" % (phone,fcfg['wgs_cfg_2']['name']), 0, False),   
          ( dict(ruca_id=fcfg['shielding_box_cfg']['box1']['ruca_id'],db=fcfg['reset_db']),
            "CB_ZD_Config_Super_Ruca",
            "Configure super ruca on box1 to [%s] for testing phone [%s]" % (fcfg['reset_db'],phone), 0, False),
          ( dict(ruca_id=fcfg['shielding_box_cfg']['box2']['ruca_id'],db=fcfg['roaming_db']),
            "CB_ZD_Config_Super_Ruca",
            "Configure super ruca on box2 to [%s] for testing phone [%s]" % (fcfg['roaming_db'],phone), 0, False),
          ( dict(ap_tag=fcfg['ap_tag_1'], ssid=phone),
            "CB_ZD_Clear_Mqstats_On_AP",
            "Clear mqstats of wlan[%s] on active AP of shielding box1" % phone, 0, False ),
#          ( test_phone_param,
#            "CB_ZD_Test_SPLK_Phone_Encrypt",
#            "Test Phone [%s] Connectivity" % phone, 2, False),
          ( dict(sta_tag=fcfg['sta_tag_2'], zapd_sta=fcfg['zapd_sta_1'], if_name=fcfg['if_name'], proto=fcfg['proto'], up_speed=fcfg['up_speed'], dn_speed=fcfg['dn_speed']),
            "CB_ZD_Start_Back_Ground_Traffic",
            "Start back ground traffic on station [%s] for testing phone [%s]" % (fcfg['sta_tag_2'], phone), 0, False),
          ( dict(sta_tag=fcfg['sta_tag_3'], zapd_sta=fcfg['zapd_sta_2'], if_name=fcfg['if_name'], proto=fcfg['proto'], up_speed=fcfg['up_speed'], dn_speed=fcfg['dn_speed']),
            "CB_ZD_Start_Back_Ground_Traffic",
            "Start back ground traffic on station [%s] for testing phone [%s]" % (fcfg['sta_tag_3'], phone), 0, False),
          ( dict(infname=fcfg['infname'], duration=fcfg['duration'],ap_tag=fcfg['ap_tag_1'],sta_tag=fcfg['sta_tag_1'],phone_mac=get_ph_mac(phone),dut_phone=phone),
            "CB_ZD_Start_Sniffer_On_Station",
            "Start roaming Packets sniffer on station for testing phone [%s]" % phone, 1, False),
          ( test_roaming_cfg,
            "CB_ZD_Generate_Roaming",
            "Generate roaming repeat for testing phone [%s]" % phone, 2, False),
          ( dict(sta_tag=fcfg['sta_tag_1']),
            "CB_ZD_Stop_Sniffer_On_Station",
            "Stop roaming Packets sniffer on station for testing phone [%s]" % phone, 2, True),
          ( dict(criterion=fcfg['criterion'],dut_ap=[fcfg['ap_tag_1'],fcfg['ap_tag_2']],dut_phone=phone,sta_tag=fcfg['sta_tag_1'],phone_mac=get_ph_mac(phone)),
            "CB_ZD_Analyze_Roaming_Delay_On_Station",
            "Analyze packets and generate roaming delay report for testing phone [%s]" % phone, 2, False),
          ( dict(sta_tag = fcfg['sta_tag_2']),
            "CB_ZD_Stop_Back_Ground_Traffic",
            "Stop back ground traffic on station [%s] testing phone [%s]" % (fcfg['sta_tag_2'], phone), 0, False),
          ( dict(sta_tag = fcfg['sta_tag_3']),
            "CB_ZD_Stop_Back_Ground_Traffic",
            "Stop back ground traffic on station [%s] testing phone [%s]" % (fcfg['sta_tag_3'], phone), 0, False),
          ( dict(ap_tag=fcfg['ap_tag_1'], ssid=phone, phone_mac=get_ph_mac(phone)),
            "CB_ZD_Verify_Voice_Queue_On_AP",
            "Verify voice queue of wlan[%s] on active AP of shielding box1" % phone, 0, False),
          ( dict(wlan_list=[phone],wgs_cfg=fcfg['wgs_cfg_1']),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove wlan [%s] on Wlan Group [%s]" % (phone, fcfg['wgs_cfg_1']['name']), 0, False),
          ( dict(wlan_list=[phone],wgs_cfg=fcfg['wgs_cfg_2']),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove wlan [%s] on Wlan Group [%s]" % (phone, fcfg['wgs_cfg_2']['name']), 0, False),
          ]
        )    
    return phone_test_cfg
        
    
def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 enable_tunnel = True,
                 enable_vlan = True,
                 radio_type = '2G',
                 phone_list = ['8020WEP', '8020WPA', '8020WPA2'],
                 sf_sta_ip_addr='192.168.1.11',
                 bg_sta1_ip_addr='192.168.1.22',
                 bg_sta2_ip_addr='192.168.1.33',
                 ap_model='zf2942'
                 )
    attrs.update(kwargs)
    tbi = getTestbed4(**kwargs)
    tb_cfg = getTestbedConfig(tbi)
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    shielding_box_dict = tb_cfg["shielding_box"]
    dut_ap = {}

    if attrs['interactive_mode']:
        active_ap_list =  getActiveApByShieldingBox(ap_sym_dict, shielding_box_dict)
        print "Active AP : %s" % active_ap_list
        active_ap = active_ap_list
        dut_ap['box1'] = active_ap_list[0] if active_ap_list[0] in shielding_box_dict['box1']['active_ap'] else active_ap_list[1] 
        dut_ap['box2'] = active_ap_list[0] if active_ap_list[0] in shielding_box_dict['box2']['active_ap'] else active_ap_list[1]
        sf_sta_ip_addr = getTargetStation(tb_cfg['sta_ip_list'])
        bg_sta1_ip_addr = getTargetStation(tb_cfg['sta_ip_list'])
        bg_sta2_ip_addr = getTargetStation(tb_cfg['sta_ip_list'])

    else:
        for ap in shielding_box_dict['box1']['active_ap']:
            if ap_sym_dict[ap]['model'] == attrs['ap_model'].lower():
                dut_ap['box1'] = ap
        for ap in shielding_box_dict['box2']['active_ap']:
            if ap_sym_dict[ap]['model'] == attrs['ap_model'].lower():
                dut_ap['box2'] = ap
        active_ap = dut_ap.values()
        sf_sta_ip_addr = attrs['sf_sta_ip_addr']
        bg_sta1_ip_addr = attrs['bg_sta1_ip_addr']
        bg_sta2_ip_addr = attrs['bg_sta2_ip_addr']
    apcfg = ap_sym_dict[active_ap[0]]
    
    ap_model_id = get_ap_model_id(apcfg['model'])
    ap_role_id = get_ap_role_by_status(apcfg['status'])
    if apcfg['model'].find('2942') != -1: wgs_type = 'bg'
    if apcfg['model'].find('7942') != -1: wgs_type = 'ng'
    
    shielding_box_cfg=dict(box1=dict(ruca_id=shielding_box_dict['box1']['super_ruca_id'], ap=ap_sym_dict[dut_ap['box1']]['mac'], dut_ap=dut_ap['box1']),
                           box2=dict(ruca_id=shielding_box_dict['box2']['super_ruca_id'], ap=ap_sym_dict[dut_ap['box2']]['mac'], dut_ap=dut_ap['box2']))

    if get_support_dual_band(apcfg['model']):
        if attrs['interactive_mode']:
            bandopt = {'0':'ng_na', '1':'na_ng'}
            while 1:
                dut_band = raw_input("Please select 2.4G or 5G band you want to test[1/0] (0:2.4G, 1:5G):")
                if dut_band not in ['0', '1']:
                    print "Input Error"
                    continue
                else:
                    wgs_type = bandopt[dut_band]
                    break
        else:
            wgs_type = 'na_ng' if attrs['radio_type'].lower() == '5G'.lower() else 'ng_na'
            
    if attrs['interactive_mode']:
        enable_tunnel = raw_input("Is tunnel mode enabled? [y/n]: ").lower() == "y"  
        enable_vlan = raw_input("Is VLAN tagging enabled? [y/n]: ").lower() == "y"
    else:
        enable_tunnel = attrs['enable_tunnel']
        enable_vlan = attrs['enable_vlan']
        
    v=1 if enable_vlan else 0
    t=1 if enable_tunnel else 0
    radio_id = 2 if wgs_type == 'na_ng' else 1 
    TCID = "TCID:38.02.%02d.%02d.%02d.%02d.%02d" % (t,v, ap_model_id, ap_role_id, radio_id)

    ts_name = "%s %s - SPLK Phone Roaming" % (TCID, ("Tunnel" if enable_tunnel else "No Tunnel"))
    if enable_vlan:
        ts_name += " with VLAN"
        
    ts_name += " - %s" % apcfg['model'].upper()
    if wgs_type == 'na_ng':
        ts_name += " 5G"

    test_cfgs = define_test_cfg(active_ap=active_ap, 
                                wgs_type=wgs_type, 
                                enable_tunnel=enable_tunnel, 
                                enable_vlan=enable_vlan, 
                                phone_list=attrs['phone_list'], 
                                sf_sta_ip_addr=sf_sta_ip_addr,
                                bg_sta1_ip_addr=bg_sta1_ip_addr,
                                bg_sta2_ip_addr=bg_sta2_ip_addr,
                                shielding_box_cfg=shielding_box_cfg)
    ts = get_testsuite(ts_name,
                      "Verify different Spectralink Phone model can associate AP through different Encryption Types",
                      combotest=True)

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, exc_level, is_cleanup in test_cfgs:
        if addTestCase(ts, test_name, common_name, test_params, test_order, exc_level=exc_level, is_cleanup=is_cleanup) > 0:
            test_order += 1
            test_added += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)  

#non-interactive mode example
#ats_ZD_Combo_Spectralink_Phone_Connectivity.py name=l3.tunnel.vlan active_ap=AP_04 enable_tunnel=True enable_vlan=True radio_type=5g interactive_mode=False sta_ip_addr=192.168.1.22       
if __name__ == "__main__":
    _dict = as_dict( sys.argv[1:] )
    create_test_suite(**_dict)        
