import sys, os, types, copy, re
from pprint import pformat
from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tb_config = getTestbedConfig(tbi)

    test_order = 1
    test_name_lst = ["AP_Default_Config_Belgacom","AP_Default_Config_Telsur",
                     "AP_Default_Config_TeliaSonera","AP_Default_Config_Singtel",
                     "AP_Default_Config_Swisscom","AP_Default_Config_PCCW_4bss",
                     "AP_Default_Config_Pioneer"]
    tc_params_lst = [{'description':'Belgacom - Ruckus 03 with custom profile','active_ap': '192.168.50.192', 'custom_profile':'belgacom'},
                     {'description':'Telsur - Ruckus 03 ID with custom profile','active_ap': '192.168.50.191', 'custom_profile':'telsur'},
                     {'description':'Telia Sonera - Ruckus ID with custom profile','active_ap': '192.168.50.193', 'custom_profile':'telia_sonera'},
                     {'description':'Singtel - Route 01 ID with custom profile','active_ap': '192.168.50.194', 'custom_profile':'singtel'},
                     {'description':'Swisscom - Ruckus with Custom profile','active_ap': '192.168.50.195', 'custom_profile':'swisscom'},
                     {'description':'PCCW - hz-4bss and 4bss ID','active_ap': '192.168.50.198', 'custom_profile':'pccw_4bss'},
                     {'description':'Pionner - Ruckus 05 ID','active_ap': '192.168.7.2', 'custom_profile':'pioneer'}]

    for i in range(len(test_name_lst)):
        common_name = "1.1.1.%d Verify AP default config for customer %s" % \
                      (test_order, test_name_lst[i].split('_')[-1])

        test_added = 0
        for ap_name, ap_cfg in tb_config['ap_sym_dict'].items():
            if  test_name_lst[i].split("AP_Default_Config_")[-1].lower() in ap_name.lower():
                # Add default test cases & test suite.
                ts_name = test_name_lst[i]
                print "Adding TestSuite \"%s\" " % ts_name
                try:
                    ts = TestSuite.objects.get(name=ts_name)
                    print "TestSuite '%s' is already in database." % ts_name
                except ObjectDoesNotExist:
                    print "TestSuite '%s' is not found in database; adding...\n" % ts_name
                    ts = TestSuite(
                        name=ts_name,
                        description="Verify AP Default Configuration and Custom Profile on AP"
                    )
                    ts.save()

                print "Adding test cases to TestSuite %s" % ts.name

                active_ap = ap_cfg["ip_addr"]
                tc_params = {'active_ap':active_ap}
                tc_params_lst[i].update(tc_params)

                if addTestCase(
                    ts, test_name_lst[i], common_name, str(tc_params_lst[i]), test_order
                ) > 0:
                    test_added += 1

                test_order += 1

                print "\n-- Summary: added %d test cases into test suite '%s'" %\
                      (test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)
