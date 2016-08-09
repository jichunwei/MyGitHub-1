# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure QoS:
22.1	Sets tx failed threshold value.
22.2	Sets heuristics video inter-packet-gap min and max value.
22.3	Sets heuristics voice inter-packet-gap min and max value.
22.4	Sets heuristics video packet-length min and max value.
22.5	Sets heuristics voice packet-length min and max value.
22.6	Sets heuristics classification video packet-octet-count value.
22.7	Sets heuristics classification voice packet-octet-count value.
22.8	Sets heuristics no-classification video packet-octet-count value.
22.9	Sets heuristics no-classification voice packet-octet-count value.
22.10	Sets tos classification video value.
22.11	Sets tos classification voice value.


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def defineTestConfiguration():
    test_cfgs = []

    test_name = 'CB_ZD_CLI_Configure_QoS'
    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True}, test_name, common_name, 0, False))
    
    common_name = '[TX Failed Threshold]Sets tx failed threshold value'
    test_cfgs.append(({'qos_conf': {'tx_failure_threshold': '100'}}, test_name, common_name, 1, False))
    
    common_name = '[Inter-packet-gap]Sets heuristics video inter-packet-gap min and max value'
    test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_gap_video': '5',
                                    'heuristic_max_pkt_gap_video': '60',}}, test_name, common_name, 1, False))
    
    common_name = '[Inter-packet-gap]Sets heuristics voice inter-packet-gap min and max value'
    test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_gap_voice': '10',
                                    'heuristic_max_pkt_gap_voice': '270',}}, test_name, common_name, 1, False))
     
    common_name = '[Packet-length]Sets heuristics video packet-length min and max value'
    test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_len_video': '1100',
                                    'heuristic_max_pkt_len_video': '1500',}}, test_name, common_name, 1, False))
    
    common_name = '[Packet-length]Sets heuristics voice packet-length min and max value'
    test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_len_voice': '65',
                                    'heuristic_max_pkt_len_voice': '350',}}, test_name, common_name, 1, False))
    
    common_name = '[Classification Packet-octet-count]Sets heuristics classification video packet-octet-count value'
    test_cfgs.append(({'qos_conf': {'heuristic_octet_count_video': '55000'}}, test_name, common_name, 1, False))    
    
    common_name = '[Classification Packet-octet-count]Sets heuristics classification voice packet-octet-count value'
    test_cfgs.append(({'qos_conf': {'heuristic_octet_count_voice': '650'}}, test_name, common_name, 1, False))
    
    common_name = '[No-classification Packet-octet-count]Sets heuristics no-classification video packet-octet-count value'
    test_cfgs.append(({'qos_conf': {'no_heuristic_octet_count_video': '550000'}}, test_name, common_name, 1, False))
    
    common_name = '[No-classification Packet-octet-count]Sets heuristics no-classification voice packet-octet-count value'
    test_cfgs.append(({'qos_conf': {'no_heuristic_octet_count_voice': '15000'}}, test_name, common_name, 1, False))
    
    common_name = '[Tos Classification]Sets tos classification video value'
    test_cfgs.append(({'qos_conf': {'tos_classification_video': '0xA8'}}, test_name, common_name, 1, False))
    
    common_name = '[Tos Classification]Sets tos classification voice value'
    test_cfgs.append(({'qos_conf': {'tos_classification_voice': '0xE8'}}, test_name, common_name, 1, False))   

    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))

    return test_cfgs
  
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts_name = 'Configure QoS'
    ts = testsuite.get_testsuite(ts_name, 'Verify the Global QoS setting by ZD CLI', combotest=True)
    test_cfgs = defineTestConfiguration()

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
