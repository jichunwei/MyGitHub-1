from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(baseid):
    return u'TCID: 01.08.01.%02d' % baseid

def _description():
    desc = list()
    desc.append("Configure PSK (decryption password) from CLI")
    desc.append("Manual update custom file without omac encryption through FTP/TFTP/HTTP server")
    desc.append("Manual update custom file with omac encryption and valid PSK")
    desc.append("Manual update custom file with omac encryption and invalid PSK")
    desc.append("Auto upgrade the latest firmware and custom file from FTP/TFTP/HTTP server")
    desc.append("Auto update custom file with omac encryption and valid PSK")
    desc.append("Auto update custom file with omac encryption and invalid PSK")
    desc.append("Check AP configuration after upgrade a custom file with REGRESSIONded 'Factory Reset' command")

    return desc

def _getCommonName():
    desc = _description()

    common_name_list = list()
    for i in range(len(desc)):
        common_name_list.append("%s - %s" % (_tcid(i+1), desc[i]))

    return common_name_list

def _defineTestParams():
    params = list()

    params.append(dict(auto_upgrade=True,config_psk=True,psk="cablevision"))
    params.append(dict(auto_upgrade=False,encrypted=False))
    params.append(dict(auto_upgrade=False,encrypted=True,psk="cablevision"))
    params.append(dict(auto_upgrade=False,encrypted=True,psk="cablevision",wrong_psk="wCablevision"))
    params.append(dict(auto_upgrade=True,build="",encrypted=False))
    params.append(dict(auto_upgrade=True,psk="cablevision",encrypted=True))
    params.append(dict(auto_upgrade=True,psk="cablevision",wrong_psk="wCablevision",encrypted=True))
    params.append(dict(auto_upgrade=True,factory=True))

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

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        test_cfgs = _defineTestParams()
        common_name_list = _getCommonName()
        #louis.lou@ruckuswireless.com for splite suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        ts_name = '%s - Cablevision' % ap_model
        description = 'Verify stuffs related to Cablevision features with %s [%s]' % (active_ap, ap_model)
        
        ts = get_testsuite(ts_name, description)

        test_order = 1
        test_added = 0
        test_name = "Cablevision"

        build = raw_input("Enter the current build of the AP [This build will be used to test upgrade]: ")
        default_params = dict(active_ap=active_ap)
        for i in range(len(test_cfgs)):
            temp = default_params.copy()
            temp.update(test_cfgs[i])
            if not temp.has_key('config_psk'):
                temp.update(local_sta=local_sta)
                if temp.has_key('build'): temp['build'] = build
            print "\n--------"
            addTestCase(ts, test_name, common_name_list[i], temp, test_order)
            test_added += 1
            test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases in to test suite %s" % (active_ap,
                                                                                         test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)
