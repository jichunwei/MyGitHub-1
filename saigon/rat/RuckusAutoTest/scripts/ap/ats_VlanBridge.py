from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(subid, baseid):
    return u'TCID:01.07.%02d.%02d' % (subid, baseid)

dev_list = ["zf2942", "zf2925", "zf7942", "zf7962", "zf7762"]
latest_release = []
upgraded_build = []
upgraded_ap_list = []

def _description():
    desc = list()
    for dev in dev_list:
        desc.append("Upgrade from the latest release %s" % dev.upper())

    desc.append("Adding new vlan")
    desc.append("Setting VLAN name")
    desc.append("Changing VLAN ID")
    desc.append("Duplicate VLAN port setting")
    desc.append("Swap VLAN - Verify with ping/DHCP traffic")
    desc.append("Adding untag Ethernet port to VLAN - Verify with ping/DHCP traffic")
    desc.append("Adding tagged Ethernet port to VLAN - Verify with ping/DHCP traffic")
    desc.append("Adding untag WLAN to VLAN - Verify with ping/DHCP traffic")
    desc.append("Removing untag Ethernet port from VLAN - Verify with ping/DHCP traffic")
    desc.append("Removing tagged Ethernet port from VLAN - verify with ping/DHCP traffic")
    desc.append("Removing untag WLAN from VLAN - verify with ping/DHCP traffic")
    desc.append("Create maximum VLANs")
    desc.append("Delete a VLAn - Verify with ping/DHCP traffic")
    desc.append("Check status of Ethernet port in a VLAN after removing/adding it")

    return desc

def _getCommonName():
    desc = _description()
    common_name_list = list()
    count = 0
    for subid in [1, 5]:
        if subid == 1:
            for baseid in range(1,6):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), desc[count]))
                count += 1
        elif subid == 5:
            for baseid in range(1,15):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), desc[count]))
                count += 1

    return common_name_list

def _defineTestParams():
    params = list()

    # Test case 1.7.1.1 to 1.7.1.5
    for i in range(len(dev_list)):
        params.append(dict(ap_model=dev_list[i],
                           latest_build=latest_release[i],
                           upgraded_build=upgraded_build[i],
                           active_ap=upgraded_ap_list[i]
                     )
        )

    # Test case 1.7.5.1 to 1.7.5.14
    params.append(dict(vlan_add=True, vlan_id='100'))
    params.append(dict(vlan_name='testvlan', vlan_id='100'))
    params.append(dict(vlan_id_change='20', vlan_id='100'))
    params.append(dict(vlan_id_clone='20', vlan_id='100'))
    params.append(dict(vlan_swap='20', vlan_id='100'))
    params.append(dict(eth_native_add=True, vlan_id='100'))
    params.append(dict(eth_tagged_add=True, vlan_id='100'))
    params.append(dict(wlan_native_add=True, vlan_id='100'))
    params.append(dict(eth_native_rem=True, vlan_id='100'))
    params.append(dict(eth_tagged_rem=True, vlan_id='100'))
    params.append(dict(wlan_native_rem=True, vlan_id='100'))
    params.append(dict(max_vlan=True, vlan_id='100'))
    params.append(dict(rem_vlan=True, vlan_id='100'))
    params.append(dict(status_port=True, vlan_id='100'))

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
    local_station = sta_ip_list[int(id)]
    id = raw_input("Pick up a Linux station behind the Adapter: ")
    remote_station = sta_ip_list[int(id)]

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = showApSymList(ap_sym_dict)

    for i in range(len(dev_list)):
        print "\n#####################"
        ans = raw_input("Pick up an AP %s to test upgrade [Enter if not choose]: " % dev_list[i].upper())
        if ans:
            release = raw_input("Enter the latest release of this model: ")
            latest_release.append(release)
            build = raw_input("Enter the upgraded build for this model: ")
            upgraded_build.append(build)
            upgraded_ap_list.append(ans)
        else:
            latest_release.append('')
            upgraded_build.append('')
            upgraded_ap_list.append('')

    print "\n#####################"
    active_ap = raw_input('Pick up an AP to verify VLAN function: ')
    id = raw_input("Run AP [symbolic=%s] with 5.0GHz band? [n/Y]: " % active_ap)
    if id.upper() == "N":
        wlan_if = 'wlan0'
        ap_channel = '6'
        active_ad = 'ad_04'
    else:
        ap_channel = '100'
        wlan_if = 'wlan8'
        active_ad = 'ad_02'

    # Add test cases
    test_order = 1
    test_added = 0
    test_cfgs = _defineTestParams()
    common_name_list = _getCommonName()
    ts = get_testsuite('Vlan Bridge', 'Verify stuffs related to VLAN Bridge stuff')

    if upgraded_ap_list:
        test_name = 'Vlan_Upgrade'
        for i in range(len(upgraded_ap_list)):
            if upgraded_ap_list[i]:
                print "\n--------"
                addTestCase(ts, test_name, common_name_list[i], test_cfgs[i], test_order)
                test_order += 1
                test_added += 1

    test_name = "Vlan_Configuration"
    default_params = dict(active_ap=active_ap,
                          local_station=local_station,
                          remote_station=remote_station,
                          active_ad=active_ad,
                          wlan_if=wlan_if,
                          ap_channel=ap_channel
                          )

    for i in range(len(test_cfgs)):
        if i >= 5:
            temp = default_params.copy()
            temp.update(test_cfgs[i])
            addTestCase(ts, test_name, common_name_list[i], temp, test_order)
            test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases in to test suite %s" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

