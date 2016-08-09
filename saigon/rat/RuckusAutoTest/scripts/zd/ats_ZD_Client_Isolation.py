import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def getRadioMode(ap_model, sta_type):
    if re.search("(7942|7962)", ap_model): 
        if re.search('n', sta_type):
            return "n"
        else:
            return "g"
    return ''

def _tcid(tctypid,aptcid,description):
    return u'TCID:04.01.%02d.%02d - %s' % (tctypid,aptcid,description)

def defineTestConfiguration1(target_sta):
    # non-AP specific tests
    test_cfgs = \
    [  (  {  'target_station':target_sta},
          _tcid(1,0,"Wireless clients cannot talk to each other"),
          "ZD_Wireless_Client_Isolation",),
       (  {  'target_station':target_sta},
          _tcid(2,0,"Wireless clients cannot reach ZD's default subnet"),
          "ZD_Wireless_Client_ZD_Default_Subnet_Isolation",),
       (  {  'target_station':target_sta,
             'ip':'172.21.0.252',
             'restricted_ip_list':['172.21.0.0/16']},
          _tcid(3,0,"Wireless clients cannot reach non-default restricted subnets"),
          "ZD_Wireless_Client_ZD_nonDefault_Subnet_Isolation",),
    ]
    return test_cfgs

# change TCID to include AP model
def defineTestConfiguration2(target_sta, sta_type, active_ap, ap_model, skip_11g=False, debug=False):
    # AP specific tests
    tcfg = []
    if not target_sta: return tcfg

    aptcid = const.get_ap_model_id(ap_model)
    ap_model = ap_model.upper()
    radio_mode = getRadioMode(ap_model, sta_type)
    if radio_mode == "n":
        tcfg = (  {  'target_station':target_sta,
                     'ip_of_non_default_subnet':'172.21.0.252',
                     'active_ap': active_ap,
                     'restricted_ip_list':['172.21.0.0/16'],
                     'radio_mode':radio_mode},
                  _tcid(4,aptcid,"Verify wireless client isolation on 11n client and %s" % ap_model),
                  "ZD_Wireless_Client_Isolation_For_Specific_AP",)
    elif not skip_11g:
        tcfg = (  {  'target_station':target_sta,
                     'ip_of_non_default_subnet':'172.21.0.252',
                     'active_ap':active_ap,
                     'restricted_ip_list':['172.21.0.0/16'],
                     'radio_mode':radio_mode},
                  _tcid(3,aptcid,"Verify wireless client isolation on 11g client and %s" % ap_model),
                  "ZD_Wireless_Client_Isolation_For_Specific_AP",)
    else:
        return []

    return [tcfg]

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    while True:
        target_sta_11g = testsuite.getTargetStation(sta_ip_list, "Pick an IP for 11g client: ")
        target_sta_11n = testsuite.getTargetStation(sta_ip_list, "Pick an IP for 11n client: ")
        if (target_sta_11g or target_sta_11n): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        
    ts = testsuite.get_testsuite('WLAN Options - Wireless Client Isolation',
                      'Verify the feature Wireless Client Isolation')

    # add non-AP specific test cases
    target_sta = target_sta_11g if target_sta_11g else target_sta_11n
    test_cfgs = defineTestConfiguration1(target_sta)
    test_order = 1
    test_added = 0
    for test_params, common_name, test_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    # add AP specific test cases
    for active_ap in sorted(active_ap_list):
        ap_cfg = ap_sym_dict[active_ap]
        ap_model = ap_cfg['model']
        test_cfgs = defineTestConfiguration2(target_sta_11g, '11g', active_ap, ap_model, False)
        test_cfgs.extend(defineTestConfiguration2(target_sta_11n, '11n', active_ap, ap_model, True))
        for test_params, common_name, test_name in test_cfgs:
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

