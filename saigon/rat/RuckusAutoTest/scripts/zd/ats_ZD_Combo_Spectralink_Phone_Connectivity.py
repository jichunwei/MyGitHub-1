from libZD_TestSuite_Voice import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common.lib_Constant import *
from RuckusAutoTest.scripts.zd.spectralink_phone_config import *

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

def get_wgs_cfg(wgs_type):
    wgs_cfg = {'name': 'SPLK-GROUP', 'description': '', 'ap_rp': {}}
    if wgs_type =='bg':
        wgs_cfg['ap_rp']['bg'] = {'wlangroups': wgs_cfg['name']}
    elif wgs_type == 'ng':
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
    elif wgs_type == 'ng_na':
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
        wgs_cfg['ap_rp']['na'] = {'default': 'EmptyWlanGroup'}
    else:
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name'], 'channel':'36'}
        wgs_cfg['ap_rp']['ng'] = {'default': 'EmptyWlanGroup'}	
    return wgs_cfg

def define_test_cfg(**kwargs):#active_ap, wgs_type, enable_tunnel, enable_vlan, vlan_id='55'):
    fcfg = dict( data_vlan_id = '66',
                 video_vlan_id = '77',
                 voice_vlan_id = '55',
                 ap_tag = 'dut_ap',
                 sta_tag = 'bg_sta',
                 data_wlan = 'Data-Wifi',
                 video_wlan = 'Video-Wifi',
                 zapd_sta = '192.168.66.10',
                 phone_list = [])
    fcfg.update(kwargs)
    wgs_cfg = get_wgs_cfg(fcfg['wgs_type'])
    test_cfg = list()
    if fcfg['wgs_type'] in ['bg', 'ng', 'ng_na', 'na_ng']:
        test_cfg.extend(
        [ ( dict({}), 
            "CB_ZD_Remove_All_Config",
            "Remove all configuration on ZD", 0, False),
          ( dict(wgs_cfg=dict(name='EmptyWlanGroup', description='EmptyWlanGroup')),
            "CB_ZD_Create_Empty_Wlan_Group",
            "Create an empty wlan group", 0, False),
          ( dict({}),
            "CB_ZD_Assign_All_APs_To_Empty_Wlan_Group",
            "Assign all APs to empty wlan group", 0, False),
          ( dict(wgs_cfg=wgs_cfg),
            "CB_ZD_Create_Wlan_Group",
            "Create a wlan group on ZD", 0, False),
          ( dict(active_ap=fcfg['active_ap'], ap_tag=fcfg['ap_tag']),
            "CB_ZD_Create_Active_AP",
            "Verify active AP exists on ZD", 0, False),
          ( dict(ap_tag=fcfg['ap_tag']),
            "CB_ZD_Config_Wlan_Group_On_AP",
            "Assign wlan group on active AP", 0, False),
          ( get_wlan_cfg(fcfg['data_wlan'], False, True, fcfg['data_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % fcfg['data_wlan'], 0, False),
          ( get_wlan_cfg(fcfg['video_wlan'], False, True, fcfg['video_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % fcfg['video_wlan'], 0, False),
          ( dict(wlan_list=[fcfg['data_wlan'],fcfg['video_wlan']]),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Config data and video wlans on wlan group", 0, False),
          ( dict(sta_ip_addr=fcfg['sta_ip_addr'], sta_tag=fcfg['sta_tag']),
            "CB_ZD_Create_Station",
            "Create a station for back ground traffic", 0, False),
          ( dict(sta_tag = fcfg['sta_tag'], wlan_cfg=get_wlan_cfg(fcfg['data_wlan'], False, True, fcfg['data_vlan_id'])),
            "CB_ZD_Associate_Station_1",
            "Back ground station associate to data wlan", 0, False),
          ( dict(sta_tag = fcfg['sta_tag']),
            "CB_ZD_Get_Station_Wifi_Addr_1",
            "Get Wif address on back ground station", 0, False),                
        ])
        test_cfg.extend(define_test_cfg_by_phone_list(**fcfg))
        test_cfg.extend(
        [
          ( dict(wlan_list=[fcfg['data_wlan'],fcfg['video_wlan']]),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove data and video wlans on active wlan group", 0 ,False)
        ])              

    return test_cfg

def define_test_cfg_by_phone_list(**kwargs):
    fcfg = dict(voice_vlan_id = '55', 
                phone_list=['8030WEP', '8030WPA', '8030WPA2'],
                expected_dtim='2',
                expected_directed_thr='disabled',
                if_name='Wireless Network Connection')
    fcfg.update(kwargs)
    phone_test_cfg = []
    for phone in fcfg['phone_list']:
        test_phone_param = get_phone_cfg(phone)
        test_phone_param['ap_tag'] = fcfg['ap_tag']        
        phone_test_cfg.extend(
          [
          ( get_wlan_cfg(phone, fcfg['enable_tunnel'], fcfg['enable_vlan'], fcfg['voice_vlan_id']),
            "CB_ZD_Create_Single_Wlan",
            "Create a wlan [%s]" % phone, 0, False),
          ( dict(wlan_list=[phone]),
            "CB_ZD_Config_Wlan_On_Wlan_Group",
            "Config wlan[%s] on active wlan group" % phone, 0, False),            
          ( dict(sta_tag=fcfg['sta_tag'], zapd_sta=fcfg['zapd_sta'], if_name=fcfg['if_name']),
            "CB_ZD_Start_Back_Ground_Traffic",
            "Start back ground traffic for testing phone [%s]" % phone, 0, False),
          #( dict(client_mac=get_ph_mac(phone)),
          #  "CB_ZD_Delete_Client_By_Mac_Address_On_ZD",
          #  "Delete phone [%s] connectivity on ZD" % phone, 1, False),
          ( dict(phone=phone),
            "CB_ZD_Turn_On_SPLK_Phone",
            "Turn On SPLK Phone [%s]" % phone, 0, False),
          ( test_phone_param,
            "CB_ZD_Test_SPLK_Phone_Encrypt",
            "Test Phone [%s] Connectivity" % phone, 2, False),
          ( dict(expected_dtim=fcfg['expected_dtim'], ssid=phone, ap_tag=fcfg['ap_tag']),
            "CB_ZD_Verify_DTIM_On_AP",
            "Verify DTIM on AP after phone[%s] association" % phone, 2, False),
          ( dict(expected_directed_thr=fcfg['expected_directed_thr'], ssid=phone, ap_tag=fcfg['ap_tag']),
            "CB_ZD_Verify_Directed_Bcast_On_AP",
            "Verify directed Bcast on AP after phone[%s] association" % phone, 2, False),
          ( dict(sta_tag = fcfg['sta_tag']),
            "CB_ZD_Stop_Back_Ground_Traffic",
            "Stop back ground traffic on testing phone [%s]" % phone, 0, False),
          ( dict(phone=phone),
            "CB_ZD_Turn_Off_SPLK_Phone",
            "Turn Off SPLK Phone [%s]" % phone, 0, False),
          ( dict(wlan_list=[phone]),
            "CB_ZD_Remove_Wlan_On_Wlan_Group",
            "Remove wlan[%s] on activie AP" % phone, 0, False),
          ]
        )    
    return phone_test_cfg
        
    
def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 enable_tunnel = True,
                 enable_vlan = True,
                 radio_type = '2G',
                 phone_list = ['8030WEP', '8030WPA', '8030WPA2'],
                 sta_ip_addr='192.168.1.22'
                 )
    attrs.update(kwargs)
    tbi = getTestbed4(**kwargs)
    tb_cfg = getTestbedConfig(tbi)
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    if attrs['interactive_mode']:
        print "Please pick up one AP for testing"
        active_ap_list = getActiveAp(ap_sym_dict)
        print "Active AP : %s" % active_ap_list
        active_ap = active_ap_list.pop()
        sta_ip_addr = getTargetStation(tb_cfg['sta_ip_list'])
    else:
        active_ap = attrs['active_ap']
        sta_ip_addr = attrs['sta_ip_addr']
    apcfg = ap_sym_dict[active_ap]
    
    ap_model_id = get_ap_model_id(apcfg['model'])
    ap_role_id = get_ap_role_by_status(apcfg['status'])
    if apcfg['model'].find('2942') != -1: wgs_type = 'bg'
    if apcfg['model'].find('7942') != -1: wgs_type = 'ng'

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
    TCID = "TCID:38.01.%02d.%02d.%02d.%02d.%02d" % (t,v, ap_model_id, ap_role_id, radio_id)

    ts_name = "%s %s - SPLK Phone Connectivity" % (TCID, ("Tunnel" if enable_tunnel else "No Tunnel"))
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
                                sta_ip_addr=sta_ip_addr)
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
    import pdb; pdb.set_trace()
    _dict = as_dict( sys.argv[1:] )
    create_test_suite(**_dict)        
