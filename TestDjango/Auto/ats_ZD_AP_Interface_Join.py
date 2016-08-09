import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils


def tcid(base_id, description, ap_model):
    aptcid = const.get_ap_model_id(ap_model)
    ap_model = ap_model.upper()
    return u'TCID:11.02.%02d.%02d - %s - %s' % (base_id, aptcid, description, ap_model)


def get_test_cfgByApModel(active_ap, ap_model, add_if_ip, if_mask, if_vlan):
    test_cfgs = [
        (   {'auto_approval':'True', 'active_ap': active_ap,
             'interface': {'en_mgmt_interface':True,
                           'add_if_ip':add_if_ip,
                           'if_mask':if_mask, 'if_vlan':''}
             },
             tcid(1, "AP cannot join external interface of ZD",ap_model),
             "ZD_AP_If_Join"

         ),

         (   {'auto_approval':'True', 'active_ap': active_ap,
             'interface': {'en_mgmt_interface':True,
                           'add_if_ip':add_if_ip,
                           'if_mask':if_mask, 'if_vlan':''},
             'vlan':2,
             'new_ip': '20.0.2.200',
             'mgmt_vlan': dict(enabled = True, vlan_id = str(2))
             },
             tcid(2, "Set internal VLAN, AP cannot join external interface of ZD ",ap_model),
             "ZD_AP_If_Join"

         ),

        (   {'auto_approval':'True', 'active_ap': active_ap,
             'interface': {'en_mgmt_interface':True,
                           'add_if_ip':add_if_ip,
                           'if_mask':if_mask, 'if_vlan':'2'},
             'vlan':2,
             'new_ip': '20.0.2.200',
             'mgmt_vlan': dict(enabled = True, vlan_id = str(2))
             },
             tcid(3, "Set internal and external VLAN, AP cannot join external interface of ZD ",ap_model),
             "ZD_AP_If_Join"

         ),

        (   {'auto_approval':'True', 'active_ap': active_ap,
             'interface': {'en_mgmt_interface':True,
                           'add_if_ip':add_if_ip,
                           'if_mask':if_mask, 'if_vlan':''},
             'wlan_conf':{'auth':'open', 'encryption':"WEP-64", 'ssid':'rat-ratelimit'
                            , 'key_index' : "1" , 'key_string' : utils.make_random_string(10, "hex")
                            , 'do_tunnel':True, 'dvlan': True,},
             },
             tcid(4, "AP cannot join external interface of ZD, join internal interface and get correct wlan ",ap_model),
             "ZD_AP_If_Join"

         ),
    ]
    return test_cfgs

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = None,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    add_if_ip = raw_input("External interface IP : ").lower()
    if_mask = raw_input("External interface mask : ").lower()
    if_vlan = raw_input("External interface vlan : ").lower()

    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "Mgmt - Multiple Management IP"
    ts = testsuite.get_testsuite(ts_name,
                      'Verify when ZD enable  "additional management interface"',
                      interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for active_ap in sorted(active_ap_list):
        ap_cfg = ap_sym_dict[active_ap]
        test_cfgs = get_test_cfgByApModel(active_ap, ap_cfg['model'], add_if_ip, if_mask, if_vlan)
        for test_params, common_name, test_name in test_cfgs:
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
