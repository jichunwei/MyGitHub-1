import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(id):
    return "TCID:03.03.%02d" % (id)

def getTestCfg(target_sta):
    test_cfgs = []

    # Default params
    wlan_cfg = \
        {'ssid': 'wlan-dpsk',
         'auth': 'PSK',
         'wpa_ver': 'WPA',
         'encryption': 'AES',
         'type': 'standard',
         'key_string': '1234567890',
         'key_index': '',
         'auth_svr': '',
         'do_zero_it': True,
         'do_dynamic_psk': True,
         }

    test_params_default = \
        {
         'testcase': '',
         'wlan_cfg': wlan_cfg,
         'auth_server_type': 'local',
         'auth_server_info': {},
         'psk_expiration': 'One day',
         'number_of_dpsk': 5,
         'max_dpsk_allowable': 1000,
         'expected_response_time': 20,
         'target_station_ip': '192.168.1.11',
         }
    
    test_name = 'ZD_WLAN_DPSK_Generation'


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'batch-dpsk',
                        'psk_expiration': 'Unlimited',
                        'number_of_dpsk': 10,
                        })
    common_name = 'Generate batch of %s PSKs via ZD web UI' % test_params['number_of_dpsk']
    test_cfgs.append((test_params, test_name, common_name, tcid(1)))

    
    test_params = test_params_default.copy()
    test_params.update({'testcase': 'delete-dpsk',
                        'psk_expiration': 'One year',
                        })
    common_name = 'Verify generated PSKs can be deleted'
    test_cfgs.append((test_params, test_name, common_name, tcid(3)))
    

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'export-dpsk',
                        'psk_expiration': 'Three months',
                        })
    common_name = 'Verify generated PSKs can be exported to CSV file'
    test_cfgs.append((test_params, test_name, common_name, tcid(4)))
    
    
    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import-dpsk',
                        'psk_expiration': 'Half a year',
                        })
    common_name = 'Generate batch of Dynamic PSKs using pre-defined CSV file'
    test_cfgs.append((test_params, test_name, common_name, tcid(6)))
    
    
    test_params = test_params_default.copy()
    test_params.update({'testcase': 'dpsk-expiration',
                        'number_of_dpsk': 3,
                        'psk_expiration': 'Two weeks',
                        'check_status_timeout': 150,
                        'target_ping_ip': '192.168.0.252',
                        })
    common_name = 'Verify generated PSKs can be used to associate to WLAN and the key is expired correctly'
    test_cfgs.append((test_params, test_name, common_name, tcid(9)))
    
    
    test_params = test_params_default.copy()
    test_params.update({'testcase': 'dpsk-scalability',
                        'number_of_dpsk': 100,
                        'expected_response_time': 30,
                        'psk_expiration': 'One week',
                        })
    common_name = 'Verify the scalability of ZD on batch Dynamic PSKs generating'
    test_cfgs.append((test_params, test_name, common_name, tcid(10)))

    
    test_params = test_params_default.copy()
    test_params.update({'testcase': 'max-dpsk',
                        'number_of_dpsk': 100,
                        'expected_response_time': 30,
                        'psk_expiration': 'Two years',
                        })
    common_name = 'Generate large number of Dynamic PSKs'
    #test_cfgs.append((test_params, test_name, common_name, tcid(11)))
    

    return test_cfgs


def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    
    ts = testsuite.get_testsuite("Batch Generation of Dynamic PSKs", "Verify Batch Generation of Dynamic PSKs")
    
    target_sta = testsuite.getTargetStation(sta_ip_list)

    test_order = 1
    test_added = 0
    
    test_cfgs = getTestCfg(target_sta)
    
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

