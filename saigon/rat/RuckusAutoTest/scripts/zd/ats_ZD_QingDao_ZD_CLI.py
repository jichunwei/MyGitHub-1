import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:32.%02d" % tcid

def defineTestConfiguration(target_station):
    test_cfgs = []
    test_name = 'ZD_CLI_Testing'

    common_name = 'wlaninfo -V: show VAP info'
    test_cfgs.append(({'testcase':'wlaninfo_v'}, test_name, common_name, tcid(1)))

    common_name = 'wlaninfo -S: show station info'
    test_cfgs.append(({'testcase':'wlaninfo_s', 'target_station':target_station}, test_name, common_name, tcid(2)))

    common_name = 'wlaninfo -T: show timer'
    test_cfgs.append(({'testcase':'wlaninfo_t'}, test_name, common_name, tcid(3)))

    common_name = 'wlaninfo -C: show configured APs'
    test_cfgs.append(({'testcase':'wlaninfo_c'}, test_name, common_name, tcid(4)))

    common_name = 'wlaninfo -R: show Rogue devices'
    test_cfgs.append(({'testcase':'wlaninfo_r'}, test_name, common_name, tcid(5)))

    common_name = 'wlaninfo -W: show WLAN info'
    test_cfgs.append(({'testcase':'wlaninfo_w'}, test_name, common_name, tcid(6)))

    common_name = 'wlaninfo -U: show users info'
    test_cfgs.append(({'testcase':'wlaninfo_u'}, test_name, common_name, tcid(8)))

    common_name = 'wlaninfo -M: show Mesh entries'
    test_cfgs.append(({'testcase':'wlaninfo_m'}, test_name, common_name, tcid(9)))

    common_name = 'apmgrinfo -a: Display APs info'
    test_cfgs.append(({'testcase':'apmgrinfo_a'}, test_name, common_name, tcid(11)))

    common_name = 'apmgrinfo -p: ping APMgr'
    test_cfgs.append(({'testcase':'apmgrinfo_p'}, test_name, common_name, tcid(13)))

    common_name = 'ping: ping to a destination'
    test_cfgs.append(({'testcase':'ping'}, test_name, common_name, tcid(15)))

    common_name = 'stp: enable/disable STP'
    test_cfgs.append(({'testcase':'stp'}, test_name, common_name, tcid(16)))

    common_name = 'upnp: enable/disable UPNP'
    test_cfgs.append(({'testcase':'upnp'}, test_name, common_name, tcid(17)))

    common_name = 'wlaninfo -A: show all active APs'
    test_cfgs.append(({'testcase':'wlaninfo_a'}, test_name, common_name, tcid(23)))

    common_name = 'wlaninfo --system: show system parameters'
    test_cfgs.append(({'testcase':'wlaninfo_system'}, test_name, common_name, tcid(24)))

    common_name = 'wlaninfo --dos: show all DOS entries'
    test_cfgs.append(({'testcase':'wlaninfo_dos'}, test_name, common_name, tcid(25)))

    common_name = 'wlaninfo --web-auth: show all authorized clients'
    test_cfgs.append(({'testcase':'wlaninfo_web_auth', 'target_station':target_station}, test_name, common_name, tcid(26)))

    common_name = 'wlaninfo --all-dpsk: show all dynamic PSK'
    test_cfgs.append(({'testcase':'wlaninfo_dpsk', 'target_station':target_station}, test_name, common_name, tcid(28)))

    common_name = 'wlaninfo --dcert: show all dynamic certificate'
    test_cfgs.append(({'testcase':'wlaninfo_dcert', 'target_station':target_station}, test_name, common_name, tcid(29)))

    common_name = 'wlaninfo --acl: show all L2 ACL'
    test_cfgs.append(({'testcase':'wlaninfo_acl'}, test_name, common_name, tcid(30)))

    common_name = 'wlaninfo --role: show all role'
    test_cfgs.append(({'testcase':'wlaninfo_role'}, test_name, common_name, tcid(31)))

    common_name = 'wlaninfo --auth: show all Authentication servers'
    test_cfgs.append(({'testcase':'wlaninfo_auth'}, test_name, common_name, tcid(32)))

    common_name = 'wlaninfo --pmk-cache: show all PMK cache'
    test_cfgs.append(({'testcase':'wlaninfo_pmk', 'target_station':target_station}, test_name, common_name, tcid(33)))

    common_name = 'wlaninfo --mesh-ap: show Mesh APs'
    test_cfgs.append(({'testcase':'wlaninfo_mesh_ap'}, test_name, common_name, tcid(34)))

    common_name = 'wlaninfo --mesh-topology: show Mesh Topology'
    test_cfgs.append(({'testcase':'wlaninfo_mesh_topology'}, test_name, common_name, tcid(35)))

    common_name = 'wlaninfo --mesh-history: show Mesh History'
    test_cfgs.append(({'testcase':'wlaninfo_mesh_history'}, test_name, common_name, tcid(36)))

    common_name = 'wlaninfo --all-wlangroup: show all WLAN group'
    test_cfgs.append(({'testcase':'wlaninfo_wlangroup'}, test_name, common_name, tcid(37)))

    common_name = 'wlaninfo -all-apgroup: show all AP groups'
    test_cfgs.append(({'testcase':'wlaninfo_apgroup'}, test_name, common_name, tcid(38)))

    common_name = 'wlaninfo --all-disc-ap: show all disconnected APs'
    test_cfgs.append(({'testcase':'wlaninfo_disc_ap'}, test_name, common_name, tcid(39)))

    common_name = 'show ap: show all active APs'
    test_cfgs.append(({'testcase': 'show_ap'}, test_name, common_name, tcid(41)))

    common_name = 'show ap: show all stations'
    test_cfgs.append(({'testcase': 'show_station', 'target_station': target_station},
                      test_name, common_name, tcid(42)))



    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    target_station = testsuite.getTargetStation(sta_ip_list)

    ts_name = 'ZD CLI'
    ts = testsuite.get_testsuite(ts_name, 'ZD CLI')
    test_cfgs = defineTestConfiguration(target_station)

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
