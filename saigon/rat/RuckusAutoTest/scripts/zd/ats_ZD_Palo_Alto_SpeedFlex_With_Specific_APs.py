import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

pp = pprint.PrettyPrinter(indent=4)

def getDescription(id , sta_os = '', sta_radio = '', ap_radio = ''):
    description_list = [
        'Download the SpeedFlex into %s laptop and check performance test' % sta_os,
        'SpeedFlex running with 11%s client associated to 11%s AP' % (sta_radio, ap_radio),
    ]

    return description_list[id]

def getCommonName(id, ap_model_id, ap_role_id, description, ap_type):
    return "TCID:25.01.%02d.%s.%s - %s - %s" % (id, ap_model_id, ap_role_id, description, ap_type)

def getActiveAPsByRadioMode(ap_sym_dict, mode):
    print "-------------------------------------------------------"
    print "Please select APs that support 802.11%s to test: " % mode
    print "-------------------------------------------------------"
    active_aps = testsuite.getActiveAp(ap_sym_dict)
    print "-------------------------------------------------------"
    return active_aps

def getTargetStationByOs(sta_ip_list, os):
    sta_ip = ''
    radio_mode = []
    while True:
        sta_ip = testsuite.getTargetStation(sta_ip_list, "Pick a %s wireless station: " % os)
        if sta_ip:
            modes = raw_input('Select the radio modes that the station supporting (g/n separate by space): ')
            radio_mode = modes.strip().split()
            break
    return dict(ip = sta_ip, mode = radio_mode) if sta_ip and radio_mode else None

def defineTestParameter(ap_sym_dict, active_aps_11g_list, active_aps_11n_list, vista_station, xp_station):
    all_active_aps = []
    all_active_aps.extend(active_aps_11g_list)
    all_active_aps.extend(active_aps_11n_list)
    test_cfgs = []

    for sta in [vista_station, xp_station]:
        if not sta:
            continue

        for ap in all_active_aps:
            active_ap_conf = ap_sym_dict[ap]
            ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
            ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
            ap_type = testsuite.getApTargetType(ap, active_ap_conf)
            sta_os = 'Vista' if sta == vista_station else 'XP'
            sta_radio = vista_station['mode']
            ap_radio = 'n' if ap in active_aps_11n_list else 'g'
            temp_para = {'target_station': vista_station['ip'],
                         'sta_radio': sta_radio, 'sta_os': sta_os,
                         'active_ap': ap, 'ap_radio': ap_radio}
            description = getDescription(0, sta_os, sta_radio, ap_radio)
            test_params = temp_para.copy()
            test_params['testcase'] = 'test_download'
            if sta_os == 'Vista':
                test_cfgs.append((test_params, getCommonName(1, ap_model_id, ap_role_id, description, ap_type)))
            else:
                test_cfgs.append((test_params, getCommonName(2, ap_model_id, ap_role_id, description, ap_type)))

            test_params['testcase'] = 'test_running'
            if 'g' in sta_radio:
                description = getDescription(1, sta_os, 'g', ap_radio)
                test_cfgs.append((test_params, getCommonName(4, ap_model_id, ap_role_id, description, ap_type)))

            if 'n' in sta_radio:
                description = getDescription(1, sta_os, 'n', ap_radio)
                test_cfgs.append((test_params, getCommonName(5, ap_model_id, ap_role_id, description, ap_type)))

    return test_cfgs

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_aps_11g_list = getActiveAPsByRadioMode(ap_sym_dict, 'g')
    active_aps_11n_list = getActiveAPsByRadioMode(ap_sym_dict, 'n')
    vista_station = getTargetStationByOs(sta_ip_list, 'Vista')
    xp_station = getTargetStationByOs(sta_ip_list, 'XP')

    test_order = 1
    test_added = 0
    test_name = 'ZD_SpeedFlex'
    ts_description = 'Test Zone Director\'s SpeedFlex Functionality'
    speedflex_ts = testsuite.get_testsuite('SpeedFlex', ts_description)

    for test_params, common_name in defineTestParameter(ap_sym_dict, active_aps_11g_list, active_aps_11n_list,
                                                        vista_station, xp_station):
        testsuite.addTestCase(speedflex_ts, test_name, common_name, test_params, test_order)
        test_added = test_added + 1
        test_order = test_order + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, speedflex_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
