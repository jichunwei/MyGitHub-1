from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(mainid, subid, baseid):
    return u'TCID: 01.%02d.%02d.%02d' % (mainid, subid, baseid)

def _description():
    desc = list()
    desc.append("Power cycle continuously for 24 hours")
    desc.append("Reboot AP from CLI console continuously for 24 hours")
    desc.append("AP out of box (automatically)")
    desc.append("Manually boot with main image")
    desc.append("Manually boot with bkup image")
    desc.append("Boot from network")
    desc.append("Create boot script")
    desc.append("Reboot from bootrom continuously for 24 hours")
    desc.append("Boarddata - Board Type")
    desc.append("Boarddata - Antenna Info")
    desc.append("2.4GHz - Measuring boot up time of AP while having traffic ingress at Ethernet port")
    desc.append("5GHz - Measuring boot up time of AP while having traffic ingress at Ethernet port")
    desc.append("Measuring DFS scan time")

    return desc

def _getCommonName():
    desc = _description()

    common_name_list = list()
    order = 0
    for i in [1,3]:
        if i == 1:
            for k in range(8):
                if k != 2: common_name_list.append("%s - %s" % (_tcid(i, 2, k+1), desc[order]))
                order += 1
            for k in [2,3]:
                common_name_list.append("%s - %s" % (_tcid(i, 4, k), desc[order]))
                order += 1
        elif i == 3:
            for j in range(3):
                common_name_list.append("%s - %s" % (_tcid(i, 5, j+1), desc[order]))
                order += 1

    return common_name_list

def _defineTestParams():
    params = list()

    params.append(dict(power_cycle=True,period=24))
    params.append(dict(reboot_from_cli=True,period=24))
    params.append(dict(manual_boot_main=True))
    params.append(dict(manual_boot_bkup=True))
    params.append(dict(boot_from_network=True))
    params.append(dict(boot_script=True))
    params.append(dict(bootrom=True,period=24))
    params.append(dict(boardtype=None))
    params.append(dict(antenna=None))
    params.append(dict(bootup_time=True, wlan_if='wlan0'))
    params.append(dict(bootup_time=True, isAP5GHz=True, wlan_if='wlan8'))
    params.append(dict(dfs_scan=True, wlan_if='wlan8', isAP5GHz=True))

    return params

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)

    # Get tested stations
    ip_list = []
    sta_ip_list = getSta_list(tbcfg)
    for i in range(len(sta_ip_list)):
        ip_list.append("%d - %s" % (i, sta_ip_list[i]))
    print "\nStation IP list:"
    print "\n".join(ip_list)
    id = raw_input("Pick up a station behind the AP: ")
    local_sta = sta_ip_list[int(id)]
    id = raw_input("Pick up a Linux station behind the Adapter: ")
    remote_sta = sta_ip_list[int(id)]

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        test_cfgs = _defineTestParams()
        common_name_list = _getCommonName()
        
#        ts = get_testsuite('Hardware Verification',
#                          'Verify stuffs related to Hardware features (reboot/bootrom)')

        test_order = 1
        test_added = 0
        test_name = "Reboot_BootRom"
        
        #louis.lou@ruckuswireless.com for split suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        ts_name = '%s - Hardware Verification' % ap_model
        ts = get_testsuite(ts_name,
                          'Verify stuffs related to Hardware features (reboot/bootrom)')
        
        port = raw_input("Enter AP's port number on Power Management: ")
        ans = raw_input("Is this test running on 5GHz? [Y/n] ")

        boardtype = raw_input("Enter Boardtype of the active AP: ")
        antenna = raw_input("Enter antenna info of the active AP: ")

        td = dict(local_sta=local_sta, remote_sta=remote_sta)
        default_params = dict(active_ap=active_ap)
        for i in range(len(test_cfgs)):
            temp = default_params.copy()
            temp.update(test_cfgs[i])
            if temp.has_key('power_cycle'): temp['port'] = int(port)
            if temp.has_key('bootup_time'):
                temp.update(td)
                if ans.lower() == 'y' and temp.has_key('isAP5GHz'):
                    temp['ad_linux'] = 'ad_02'
                else: temp['ad_linux'] = 'ad_04'
            if temp.has_key('boardtype'): temp['boardtype'] = boardtype
            if temp.has_key('antenna'): temp['antenna'] = antenna

            print "\n--------"
            addTestCase(ts, test_name, common_name_list[i], temp, test_order)
            test_added += 1
            test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases in to test suite %s" % (active_ap,
                                                                                         test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)
