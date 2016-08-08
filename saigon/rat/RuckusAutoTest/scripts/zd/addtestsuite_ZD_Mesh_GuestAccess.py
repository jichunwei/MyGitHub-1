import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_Debug as bugme

def tcid(base_id, ap_model_id, ap_role, sta_radio):
    return u'TCID:10.05.05.%02d.%d.%d.%d' % (base_id,ap_model_id, ap_role, const.get_radio_id(sta_radio))

def defineTestID(base_id, sta_radio):
    id_dict = dict()
    for ap_model, ap_model_id in const._ap_model_id.items():
        for ap_role, ap_role_id in const._ap_role_id.items():
            id_dict["%s %s" % (ap_model, ap_role.upper())] = tcid(base_id,ap_model_id, ap_role_id, sta_radio)

    return id_dict

def getTestCfg(target_ip = '172.126.0.252'):
    """
    """
    test_params = {}
    restricted_ip_list = ['172.21.0.252', '172.22.0.252', '172.23.0.252', '172.24.0.252', '172.25.0.252']
    test_params[1] = dict(ip = target_ip, use_guest_auth = True , use_tou = False, redirect_url = '')
    test_params[2] = dict(ip = target_ip, use_guest_auth = True , use_tou = False, redirect_url = 'http://www.example.net/')
    test_params[3] = dict(ip = target_ip, use_guest_auth = True , use_tou = True , redirect_url = '')
    test_params[4] = dict(ip = target_ip, use_guest_auth = True , use_tou = True , redirect_url = 'http://www.example.net/')
    test_params[5] = dict(ip = target_ip, use_guest_auth = False, use_tou = False, redirect_url = '')
    test_params[6] = dict(ip = target_ip, use_guest_auth = False, use_tou = False, redirect_url = 'http://www.example.net/')
    test_params[7] = dict(ip = target_ip, use_guest_auth = False, use_tou = True , redirect_url = '')
    test_params[8] = dict(ip = target_ip, use_guest_auth = False, use_tou = True , redirect_url = 'http://www.example.net/')
    test_params[9] = dict(allowed_ip = target_ip, zd_ip = '192.168.0.2', restricted_ip_list = restricted_ip_list)

    return test_params

def makeCommonName(ap_type, base_id, test_param, sta_radio):
    """
    """
    test_name = ''
    common_name = ''
    testcase_id = defineTestID(base_id, sta_radio)[ap_type]

    if test_param.has_key('restricted_ip_list'):
        test_name = 'ZD_RestrictedSubnetAccess'
        common_name = 'Mesh %s -  Restricted Subnet Access - %s' % (testcase_id, ap_type)

    else:
        auth_msg = 'Auth' if test_param['use_guest_auth'] else 'No_Auth'
        tou_msg = 'TOU' if test_param['use_tou'] else 'No_TOU'
        redir_msg = 'Redir' if test_param['redirect_url'] else 'No_Redir'
        test_name = 'ZD_GuestAccess'
        common_name = 'Mesh %s - %s/%s/%s - %s' % (testcase_id, auth_msg, tou_msg, redir_msg, ap_type)

    return (test_name, common_name)

# Add test suite
def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "Mesh - Integration - Guest Access"
    )
    attrs.update(kwargs)
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    ts = testsuite.get_testsuite(ts_name,
                      'Verify that the ZD performs guest access policy on mesh network properly',
                      interactive_mode = attrs["interactive_mode"])



    test_cfgs = getTestCfg()
    test_order = 1
    test_added = 0

    for active_ap in active_ap_list:
        baseId = 0
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)

        for test_params in test_cfgs.itervalues():
            test_params['target_station'] = target_sta
            test_params['active_ap'] = active_ap
            test_params['target_sta_radio'] = target_sta_radio

            test_name, common_name = makeCommonName(ap_type_role, baseId, test_params, target_sta_radio)
            baseId += 1

            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

