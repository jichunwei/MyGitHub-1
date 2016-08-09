from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def defineTestConfiguration(remote_win_sta, remote_linux_sta, active_ap, active_ad, passive_ad):
    test_cfgs = []

    test_cfgs.append(({'ip': '192.168.2.11',
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'target_station':remote_linux_sta},
                       "AD_MGMT_Enable_Disable",
                       'Enable/Disable Link-Local Adapter Management by Super User',)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'video_network':True,
                       'super_user':True},
                       "AD_MGMT_LoginWebUI",
                       "Login to adapter WebUI from AP WebUI by Super user in Video network",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'video_network':False,
                       'super_user':True},
                       "AD_MGMT_LoginWebUI",
                       "Login to adapter WebUI from AP WebUI by Super user in Data network",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'video_network':True,
                       'super_user':True,
                       'ad_sta_mgmt_enable':False},
                       "AD_MGMT_LoginWebUI",
                       "Login to adapter WebUI from AP WebUI in case Link-Local Adapter management is disabled on adapter",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'video_network':True,
                       'super_user':False,
                       'home_username':'',
                       'home_password':''},
                       "AD_MGMT_LoginWebUI",
                       "Login to adapter WebUI from AP WebUI by Home user in Video network",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'video_network':False,
                       'super_user':False,
                       'home_username':'',
                       'home_password':''},
                       "AD_MGMT_LoginWebUI",
                       "Login to adapter WebUI from AP WebUI by Home user in Data network",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'verify_status':True},
                       "AD_MGMT_Configuration",
                       "Configure/view status of device and Home Settings Protection",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'verify_status':False,
                       'change_ssid':True},
                       "AD_MGMT_Configuration",
                       "Change SSID for both Adapter and AP",)
    )
    test_cfgs.append(({'remote_win_sta': remote_win_sta,
                       'remote_linux_sta': remote_linux_sta,
                       'active_ap':active_ap,
                       'active_ad':active_ad,
                       'passive_ad':passive_ad,
                       'ip':'192.168.2.11',
                       'verify_status':False,
                       'change_ssid':False},
                       "AD_MGMT_Configuration",
                       "Change encryption method for both adapter and AP",))
    return test_cfgs

def createTestSuite(**kwargs):
    tb = getTestbed(**kwargs)
    tbcfg = eval(tb.config)

    # Get tested stations
    ip_list = []
    sta_ip_list = getSta_list(tbcfg)
    for i in range(len(sta_ip_list)):
        ip_list.append("%d - %s" % (i, sta_ip_list[i]))
    print "\nStation IP list:"
    print "\n".join(ip_list)
    id = raw_input("Pick up a Linux station behind the Adapter: ")
    linux_station = sta_ip_list[int(id)]
    id = raw_input("Pick up a Windows station behind the adapter: ")
    windows_station = sta_ip_list[int(id)]

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        test_order = 1
        #louis.lou@ruckuswireless.com for split suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        ts_name = "%s - IPTV_Adapter_MGMT" % ap_model
        ts = get_testsuite(ts_name, 'Verify stuffs related to IPTV Adapter MGMT with %s [%s]' % (active_ap, ap_model))

        id = raw_input("The tested Adapters is VF7111 model? [n/Y]: ")
        if id.upper() == "N":
            active_ad = 'ad_04'
            passive_ad = 'ad_03'
        else:
            active_ad = 'ad_02'
            passive_ad = 'ad_01'

        username = raw_input("Enter username of home user: ")
        password = raw_input("Enter password of home user: ")

        test_cfgs = defineTestConfiguration(windows_station, linux_station, active_ap, active_ad, passive_ad)
        for test_params, test_name, common_name in test_cfgs:
            temp = "TCID: 01.01.04.%02d" % test_order
            common_name = temp + " - " + common_name
            if test_params.has_key('home_username'): test_params['home_username'] = username
            if test_params.has_key('home_password'): test_params['home_password'] = password

            addTestCase(ts, test_name, common_name, str(test_params), test_order)
            test_order += 1

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    createTestSuite(**_dict)

