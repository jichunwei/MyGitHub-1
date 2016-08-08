from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(subid, baseid):
    return u'TCID:01.12.%02d.%02d' % (subid, baseid)

dev_list = ["zf2942", "zf7942", "zf7962", "zf7762", "zf7363", "zf7361", "zf7343", "zf7341"]
def _description(ap_model):
    desc = list()

    desc.append("Manual update - Verify firmware update command in CLI")
    desc.append("Manual update - Update firmware using CLI")
    desc.append("Manual update - Update firmware using WebUI")
    desc.append("Manual update - Upgrade from the latest release %s" % ap_model)

    desc.append("Auto update - Verify auto firmware update through both Ethernet ports")
    desc.append("Auto update - Verify firmware update while traffic online")
    desc.append("Auto update - Verify corrupted main firmaware ---> boot with backup image")
    desc.append("Auto update - Upgrade from the latest release %s" % ap_model)

    return desc

def _getCommonName(ap_model):
    desc = _description(ap_model)
    common_name_list = list()
    count = 0
    for subid in [1, 2]:
        if subid == 1:
            for baseid in range(1,5):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), desc[count]))
                count += 1
        elif subid == 2:
            for baseid in range(1,5):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), desc[count]))
                count += 1

    return common_name_list

def _defineTestParams(latest_build, up_from_build, ap_model):
    params = list()

    # Test case 1.7.5.1 to 1.7.5.14
    params.append(dict(cli_command=True, latest_build=latest_build))
    params.append(dict(up_cli=True, latest_build= latest_build))
    params.append(dict(up_webui=True, latest_build=latest_build))
    params.append(dict(manual=True, ap_model=ap_model, latest_build=latest_build, up_from_build=up_from_build))

    params.append(dict(auto_up=True, latest_build=latest_build))
    params.append(dict(auto_up_traffic=True, latest_build=latest_build))
    params.append(dict(corrupted_img=True,latest_build=latest_build))
    params.append(dict(auto=True, ap_model=ap_model, latest_build=latest_build, up_from_build=up_from_build))
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
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)
    #louis.lou@ruckuswireless.com for split suite with ap model.
     
#    latest_build = raw_input ("The current test build: ")
#    up_from_build = raw_input ("The build the ap upgrade from: ")
#    ap_model = raw_input("Enter the model of the AP to test upgrade [%s]: " % dev_list)
#
#    ad_input = raw_input("Is the tested AD in 5GHz band? [Y/n]")
#    if ad_input.lower() == "y": 
#        active_ad = 'ad_02'
#        ts_name = 'Firmware Upgrade - 5G'
#    else: 
#        active_ad = 'ad_04'
#        ts_name = 'Firmware Upgrade '
        
    for active_ap in active_ap_list:
        latest_build = raw_input ("The AP [%s] current test build: " % active_ap)
        up_from_build = raw_input ("The build the ap [%s] upgrade from: " % active_ap)
        ap_model = raw_input("Enter the model of the AP [%s] to test upgrade [%s]: " % (active_ap, dev_list))
    
        ad_input = raw_input("Is the tested AD in 5GHz band? [Y/n]")
        if ad_input.lower() == "y": 
            active_ad = 'ad_02'
            ts_name = '%s - Firmware Upgrade - 5G' % ap_model
        else: 
            active_ad = 'ad_04'
            ts_name = '%s - Firmware Upgrade ' % ap_model
            
        test_cfgs = _defineTestParams(latest_build, up_from_build, ap_model)
        common_name_list = _getCommonName(ap_model)
        ts = get_testsuite(ts_name, 'Verify Function Firmware Upgrade of the AP')

        test_order = 1
        test_added = 0
        test_name = "Firmware_Upgrade"

        default_params = dict(active_ap = active_ap, local_station = local_station, active_ad = active_ad,
                              remote_station = remote_station)

        for i in range(len(test_cfgs)):
            print "\n--------"
            temp = default_params.copy()
            temp.update(test_cfgs[i])
            addTestCase(ts, test_name, common_name_list[i], temp, test_order)

            test_added += 1
            test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases in to test suite %s" % (active_ap, test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

