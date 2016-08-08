# coding:utf-8
from django.test import TestCase

# Create your tests here.


import os
import django
import sys
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TestDjango.settings")
django.setup()

from Auto.models import *
from django.core.exceptions import ObjectDoesNotExist

_tc_info = "%4s   testsuite: [%s]\n       test_name: [%s]\n     common_name: [%s]"
_radio_id = {
    'bg': 1,
    'ng': 2,
    'a':  3, #'a' alone? should be 'na'
    'na': 4,
}



# ----get data from models-------
def get_objects():
    conf = dict(
            tb=Testbed.objects.all(),
            first_tb=Testbed.objects.first(),
            last_tb=Testbed.objects.last(),
            count=Testbed.objects.count(),

    )
    return conf


# ----insert data to models----------
def insert_objects():
    lc = []
    nv = raw_input("please input your tbname and tbtpye(separated by spaces ):").split()
    if type(nv) != list:
        print "you enter string is wrong"
        return False
    else:
        # 添加testtype
        tp = TestbedType(name='type' + str(nv[1]))
        try:
            tp.save()
            lc.append(tp.name)
        except Exception as e:
            raise e
        # 添加testbed
        tb = Testbed(name=nv[0], tbtype=tp, location='odc', owner='xx@xx.com',
                     resultdist='xx@xx.com')
        try:
            tb.save()
            lc.append(tb.name)
        except Exception, e:
            raise e
        return lc


def _getAtrVal(name, atrs, default):
    val = atrs[name] if atrs.has_key(name) else default
    return val


def getTestbed():
    atrs = {'zd_ip_addr': '192.168.0.2', 'svr_ip_addr': '192.168.0.252', 'tbtype': 'ZD_Stations',
            'zd_username': 'admin', 'zd_password': 'admin', 'shell_key': ''}
    # atrs.update(kwargs)
    tb_name = atrs['name'] if atrs.has_key('name') \
        else raw_input("Your test bed name: ")

    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:  # 对象不存在异常
        # 创建新的testbed
        tb_location = atrs['location'] if atrs.has_key('location') \
            else raw_input("Testbed location: ")
        tb_owner = atrs['owner'] if atrs.has_key('owner') else raw_input("Testbed owner: ")
        sta_ip_list = atrs['sta_ip_list'] if atrs.has_key('sta_ip_list') \
            else raw_input("Station IP address list (separated by spaces): ").split()

        ap_sym_dict = {}
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            # ap_sym_dict = getZoneDirectorAPsDict({'ip_addr': atrs['zd_ip_addr'],
            #                                       'username': atrs['zd_username'],
            #                                       'password': atrs['zd_password']})
            # ap_mac_list = [ x['mac'] for x in ap_sym_dict.values() ]
            ap_mac_list = []
        else:
            ap_mac_list = atrs['ap_mac_list'] if atrs.has_key('ap_mac_list') \
                else raw_input("AP MAC address list (separated by spaces): ").split()

        zd_conf = _getAtrVal('zd_conf', atrs,
                             {'browser_type': 'firefox',
                              'ip_addr': atrs['zd_ip_addr'],
                              'username': atrs['zd_username'],
                              'password': atrs['zd_password'],
                              'shell_key': atrs['shell_key'],
                              })

        shell_key = zd_conf['shell_key'] if zd_conf.has_key('shell_key') \
            else raw_input("shell key:(!v54!)")
        if shell_key is None or shell_key is '':
            shell_key = '!v54!'
        zd_conf['shell_key'] = shell_key

        sta_conf = _getAtrVal('sta_conf', atrs, {})
        srv_conf = _getAtrVal('srv_conf', atrs,
                              {'ip_addr': atrs['svr_ip_addr'],
                               'user': 'lab',
                               'password': 'lab4man1',
                               'root_password': 'lab4man1',
                               })

        tb_config = {"ZD": zd_conf,
                     "sta_conf": sta_conf,
                     "server": srv_conf,
                     "ap_mac_list": ap_mac_list,
                     "sta_ip_list": sta_ip_list,
                     }
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            tb_config['ap_sym_dict'] = ap_sym_dict

        if atrs.has_key('L3Switch'):
            if not atrs['L3Switch']:
                atrs['L3Switch'] = {'ip_addr': '192.168.0.253',
                                    'username': 'admin',
                                    'password': '',
                                    'enable_password': '',
                                    }
            tb_config['L3Switch'] = atrs['L3Switch']

        # ATTN: case sense for keywords
        for opt_key in ['Mesh', 'APConnMode', 'RoutingVLANs']:
            if atrs.has_key(opt_key):
                tb_config[opt_key] = atrs[opt_key]

        m = re.match(r'^([^@]+)@(|[^\s]+)', tb_owner)  # 匹配邮箱
        if not m:
            tb_owner = tb_owner + '@ruckuswireless.com'
        elif len(m.group(2)) < 1:
            tb_owner = m.group(1) + '@ruckuswireless.com'

        testbed = {'name': tb_name,
                   'tbtype': TestbedType.objects.get(name=atrs['tbtype']),
                   'location': tb_location,
                   'owner': tb_owner,
                   'resultdist': tb_owner,
                   'config': str(tb_config),
                   }

        tb = Testbed(**testbed)
        tb.save()
    return tb


def getTargetStation(sta_ip_list, message=""):
    ip_list = []
    for i in range(len(sta_ip_list)):
        ip_list.append("  %d - %s" % (i, sta_ip_list[i]))
    print "Station IP list:"
    print ";".join(ip_list)
    if not message:
        message = "Pick an IP in the list above: "
    id = raw_input(message)
    try:
        target_sta = sta_ip_list[int(id)]
    except:
        target_sta = ""
    return target_sta


def get_target_sta_radio(message=""):
    radio_list = [radio for radio, id in _radio_id.items()]
    sta_radio_list = []
    for i in range(len(radio_list)):
        sta_radio_list.append("  %d - %s\n" % (i, radio_list[i]))
    print "Station Radio list:"
    print "".join(sta_radio_list)
    if not message:
        message = "Pick an radio in the list above for target station: "
    id = raw_input(message)
    try:
        sta_radio = radio_list[int(id)]
    except:
        sta_radio = ""
    return sta_radio


def _list_in_dict(_list, _dict):
    for _l in _list:
        if not _dict.has_key(_l):
            return False
    return True


def getActiveAp(ap_sym_dict):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic APs from above list, separated by space (enter all for all APs): """
    while (True):
        showApSymList(ap_sym_dict)
        active_ap_list = raw_input(select_tips).split()
        if not active_ap_list: continue
        if re.match(r'^all$', active_ap_list[0], re.M):
            return sorted(ap_sym_dict.keys())
        if _list_in_dict(active_ap_list, ap_sym_dict):
            return active_ap_list


def showApSymList(ap_sym_dict):
    print ""
    for k in sorted(ap_sym_dict.keys()):
        print "%s : mac=%s; model=%s; status=%s" % \
              (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['model'], ap_sym_dict[k]['status'])


def get_testsuite(ts_name, description, interactive_mode = False, combotest = False):
    if interactive_mode:
        print "\nYou can assign test suite name to same set of test case.\nUse test suite to group your test cases."
        _name = raw_input("Testsuite name: [enter='%s'] " % ts_name)
    else:
        print "Testsuite name: %s" % ts_name
        _name = ts_name
    if not _name:
        _name = ts_name
    print "Adding TestSuite %s " % _name
    try:
        ts = TestSuite.objects.get(name = _name)
        print "TestSuite '%s' is already in database." % _name
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % _name
        if combotest:
            ts = TestSuite(name = _name, description = description, xtype = TestSuite.TS_COMBO)
        else:
            ts = TestSuite(name = _name, description = description)
        ts.save()
    print "Adding test cases to TestSuite %s " % ts.name
    return ts


def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = 'Configure ZD Access Point Policies'
    test_cfgs.append(({'auto_approve':False}, test_name, common_name, 0, False))

    test_name = 'CB_ZDCLI_Remove_AP'
    common_name = 'Remove AP from zd ap list'
    test_cfgs.append(({'ap_mac_list':cfg['all_ap_mac_list']}, test_name, common_name, 0, False))

    ap1_tag = "AP_01"
    ap2_tag = 'AP_02'
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_01'
    test_cfgs.append(({'active_ap': ap1_tag,
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_02'
    test_cfgs.append(({'active_ap': ap2_tag,
                       'ap_tag': ap2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_AP_SHELL_Get_Config_Wlan_Psk'
    common_name = 'Get Psk for the AP2 via AP1.'
    test_cfgs.append(({'ap_tag':ap1_tag,'get_psk_ap':ap2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))

    tc_combo_name = "Verify deactive/active config-wlan via wired port"

    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]1.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.2 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'wait_time':10,'force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.3 Disable config-wlan in cli via wired port' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'set state wlan102 down','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.4 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'sta_tag': 'sta1', 'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.5 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.6 Enable config-wlan in cli via wired port' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'set state wlan102 up','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.7 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))

    #ap2_config_wlan = "island-%s" % ap2_mac.replace('-','').replace(':','')[6:].upper()
    #cfg['wlan_cfg']['name'] = ap2_config_wlan
    #cfg['wlan_cfg']['ssid'] = ap2_config_wlan
    #test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    #common_name = '[%s]1.8 STA connect to the wlan.' % tc_combo_name
    #test_cfgs.append(({'sta_tag': 'sta1',"auth_deny":True, 'config_wlan_ap':ap2_tag, 'wlan_ssid': ap2_config_wlan,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.9 Disable config-wlan in shell' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'wrad_cli goto -','force_ssh':True,'cmd_pmt':'shell','expect_value':'current state=-'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.10 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'config_wlan_ap':ap2_tag,'sta_tag': 'sta1','wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.11 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.12 Enable config-wlan in shell' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'wrad_cli goto P','force_ssh':True,'cmd_pmt':'shell','expect_value':'current state=P'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.13 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True,'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    tc_combo_name = "Verify deactive config-wlan after OTA-Conf-Reboot"

    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]2.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]2.2 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True, 'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_Station_AP_Exec_Command'
    common_name = '[%s]2.3 Create and enable a service wlan through CLI via config-wlan' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','ap_cfg':{'cmd_text' : "set ssid wlan0 new_test_ssid_898",'ip_addr':'169.254.1.1', 'port' : 22,'username' : 'super','password' : 'sp-admin'}}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]2.4 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Reboot_All_AP'
    common_name = '[%s]2.5 Reboot AP' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]2.6 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'config_wlan_ap':ap2_tag,'sta_tag': 'sta1','wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]2.7 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))

    tc_combo_name = "Verify deactive config-wlan after OTA-Conf-Disconnect"

    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]3.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]3.2 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True,'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_Station_AP_Exec_Command'
    common_name = '[%s]3.3 Set AP2 an director ip via cli on station' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','ap_cfg':{'cmd_text' : "set director ip 192.18.0.2",'ip_addr':'169.254.1.1', 'port' : 22,'username' : 'super','password' : 'sp-admin'}}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]3.4 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]3.5 Disconnect from config-wlan' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]3.6 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))

    tc_combo_name = "Verify deactive config-wlan after Non-OTA-Conf"

    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]4.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))

    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]4.2 Set director ip via wired port' % tc_combo_name
    test_cfgs.append(({'cmd_text' : "set director ip 192.18.0.2",'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]4.3 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))

    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = 'Cleanup - Configure ZD Access Point Policies'
    test_cfgs.append(({'auto_approve':True}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = 'Cleanup - Set AP2 default factory.'
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_CLI_Wait_AP_Connect'
    common_name = 'Cleanup -  Check AP2 join ZD.'
    test_cfgs.append(({'ap_tag': ap2_tag}, test_name, common_name, 0, True))
    return test_cfgs

def update_test_case(config):
    '''
    . updating the testcase and its generated testruns if the testcase is exist
    . otherwise, just add it in
    '''
    result = -1
    try:
        tclist = TestCase.objects.filter(suite = config['suite']
                                     , test_name = config['test_name']
                                     , common_name = config['common_name'])
        if len(tclist) > 0:
            for tc in tclist:
                tc.test_params = config['test_params']
                tc.save()
                print _tc_info % ('UPDATE', tc.suite, tc.test_name, tc.common_name)
                result = tc.id
        else:
            tc = TestCase(**config)
            tc.save()
            result = tc.id
            print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])

    except ObjectDoesNotExist:
        tc = TestCase(**config)
        tc.save()
        result = tc.id
        print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])

    trs = TestRun.objects.filter(suite = config['suite'])
    if trs:
        for tr in trs:
            if tr.common_name == config['common_name']:
                tr.test_params = config['test_params']
                tr.save()
                print _tc_info % ('UPDATE', tr.suite, tr.test_name, tr.common_name)
                result = tr.id
    return result


def add_test_case(config):
    tc = TestCase(**config)
    tc.save()
    result = tc.id
    print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])
    return result

def addTestCase(test_suite, test_name, common_name, test_param, test_order = 0,\
                exc_level = 0 , is_cleanup = False, is_update = True):
    cfg = dict(suite = test_suite,
               test_name = 'zd.%s' % test_name,
               seq = test_order,
               test_params = str(test_param),
               common_name = common_name,
               exc_level = exc_level,
               is_cleanup = is_cleanup)
    if is_update:
        return update_test_case(cfg)
    else:
        return add_test_case(cfg)


def create_test_suite():
    ts_cfg = dict(interactive_mode=True,
                  station=(0, "g"),
                  targetap=False,
                  testsuite_name="",
                  )
    tb = getTestbed()
    tbcfg = getTestbedConfig(tb)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    if ts_cfg["interactive_mode"]:
        target_sta = getTargetStation(sta_ip_list)
        target_sta_radio = get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap_list = getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]

    if active_ap_list != []:
        tc_dict = {'target_station': '%s' % target_sta,
                   'active_ap_list': active_ap_list,
                   'all_ap_mac_list': all_ap_mac_list,
                   'radio_mode': target_sta_radio,
                   'active_ap': active_ap
                   }

    tcfg = define_test_parameters()
    tcfg.update(tc_dict)

    ts_name = 'AP OTA - Active Deactive Config-Wlan'
    ts = get_testsuite(ts_name, 'Verify AP OTA', combotest=True)
    test_cfgs = define_test_cfg(tcfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    return ts_cfg


def getTestbedConfig(tbi):
    tbi_config = tbi.config.replace('\n' , '').replace('\r', '')
    tbconfig = eval(tbi_config)
    return tbconfig


def define_test_parameters():
    cfg = {}

    """
       wlan_cfg_list
    """
    cfg['wlan_cfg'] = {
        "name": '',
        "ssid": '',
        "type": "standard-usage",
        "auth": "PSK",
        "wpa_ver": "WPA2",
        "encryption": "AES",
        "key_string": ''}

    """
        expected_station_info
    """
    cfg['expected_station_info'] = {'status': u'Authorized'}

    return cfg


if __name__ == '__main__':
    value = get_objects()
    print value

    # #插入数据库
    # res = insert_objects()
    # print res

    create_test_suite()
    #
    # tb = getTestbed()
    # print tb.name
