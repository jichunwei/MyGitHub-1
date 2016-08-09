from libATT_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme


def _defineTestParams():
    params = []
    template = [ 'TCID:%s - Verify info %s - %s',
        'CB_VerifyATTInfo',
        {'info':'%s', 'type' : '%s', 'path' : '%s',
         'exc_level' : '%s', 'is_cleanup' : '%s' }
    ]

    params.append(['TCID:1.1.1 - Set up environment for ATT',
        'CB_SetUpATTEnvironment',
        {'exc_level' : 0, 'is_cleanup' : False}])

    params.append(['TCID:1.1.2 - Send traffic for window stations',
        'CB_SendIperfTraffic',
        {'exc_level' : 1, 'is_cleanup' : False, 'timeout' : 300}])

    params.append(['TCID:1.1.3 - AP does not response to a request with wrong URL',
        'CB_ATT_GetXmlFile',
        {'exc_level' : 2, 'is_cleanup' : False, 'testcase': 'request_with_wrong_url'}])

    params.append(['TCID:1.1.4 - AP does not response to a request with wrong user info',
        'CB_ATT_GetXmlFile',
        {'exc_level' : 2, 'is_cleanup' : False, 'testcase': 'request_with_wrong_user'}])

    params.append(['TCID:1.1.5 - AP does not response to a request with wrong password info',
        'CB_ATT_GetXmlFile',
        {'exc_level' : 2, 'is_cleanup' : False, 'testcase': 'request_with_wrong_password'}])

    params.append(['TCID:1.1.6 - AP does not response to a request with wrong branch name',
        'CB_ATT_GetXmlFile',
        {'exc_level' : 2, 'is_cleanup' : False, 'testcase': 'request_with_wrong_branchname'}])

    params.append(['TCID:1.1.7 - Able to receive XML content when using correct request header',
        'CB_ATT_GetXmlFile',
        {'exc_level' : 2, 'is_cleanup' : False, 'testcase': 'with_correct_request_header'}])


    dict_testsuites = {
        'device_info' : '1.2',
        'device_time' : '1.3',
        'lan_info' : '1.4',
        'lan_host_conf' : '1.5',
        'lan_host_conf_interface' : '1.6',
        'wlan_conf_info' : '1.7',
        'wlan_conf_wlanstat' : '1.8',
        'associate_device' : '1.9',
        'station_ethernet_mac' : '1.10',
        'associate_client_stat' : '1.11',
    }

    dict_type_info = {
        'device_info' : ['X_001392_STATS_INTERVAL', 'X_001392_STATS_INTERVAL_BINS',
                        'ModelName', 'SerialNumber', 'SoftwareVersion', 'UpTime'],

        'device_time' : ['CurrentLocalTime'],

        'lan_info' : ['X_001392_LAN_Index', 'LANWLANConfigurationNumberOfEntries'],

        'lan_host_conf' : ['IPInterfaceNumberOfEntries'],

        'lan_host_conf_interface' : ['X_001392_IP_INTERFACE_Index', 'Enable',
                                     'X_001392_MGT_MAC', 'IPInterfaceIPAddress'],

        'wlan_conf_info' : ['X_001392_WLAN_Index', 'X_001392_WLAN_NAME',
                            'Enable', 'Channel', 'SSID', 'BeaconType',
                            'Standard', 'WPAEncryptionModes', 'TotalAssociations'],

        'wlan_conf_wlanstat' : ['X_001392_WLAN_STATS_Index', 'X_001392_WLAN_NF',
                                'X_001392_WLAN_RX_PKTS', 'X_001392_WLAN_RX_OCTETS',
                                'X_001392_WLAN_TX_PKTS', 'X_001392_WLAN_TX_OCTETS'],

        'associate_device' : ['X_001392_STA_Index', 'AssociatedDeviceMACAddress',
                              'X_001392_STA_NUM_ETHERNET'],

        'station_ethernet_mac' : ['X_001392_STA_ETHER_Index', 'X_001392_STA_ETHER_ADDR'],

        'associate_client_stat' : ['X_001392_STA_STATS_Index', 'X_001392_STA_TX_RSSI',
                                'X_001392_STA_THROUGHPUT_EST', 'X_001392_STA_RX_PKTS',
                                'X_001392_STA_TX_PKTS_XMIT', 'X_001392_STA_TX_PKTS_QUEUED',
                                'X_001392_STA_TX_PKTS_DROP_OVERFLOW', 'X_001392_STA_TX_PKTS_DROP_XRETRIES',
                                'X_001392_STA_TX_PKTS_DROP_OVERDUE']
    }

    dict_type_path = {
        'device_info' : {"name" : "DeviceInfo", "index" : 0},

        'device_time' : {"name" : "Time", "index" : 0},

        'lan_info' : {"name" : "LANDevice", "index" : 0},

        'lan_host_conf' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "LANHostConfigManagement", "index" : 0}},

        'lan_host_conf_interface' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "LANHostConfigManagement", "index" : 0,
            "child" : {"name" : "IPInterface", "index" : 0}}},

        'wlan_conf_info' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "WLANConfiguration", "index" : 0}},

        'wlan_conf_wlanstat' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "WLANConfiguration", "index" : 0,
            "child" : {"name" : "X_001392_WLANStats", "index" : 0}}},

        'associate_device' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "WLANConfiguration", "index" : 0,
            "child" : {"name" : "AssociatedDevice", "index" : 0}}},

        'associate_client_stat' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "WLANConfiguration", "index" : 0,
            "child" : {"name" : "AssociatedDevice", "index" : 0,
            "child" : {"name" : "X_001392_ClientStats", "index" : 0}}}},

        'station_ethernet_mac' : {"name" : "LANDevice", "index" : 0,
            "child" : {"name" : "WLANConfiguration", "index" : 0,
            "child" : {"name" : "AssociatedDevice", "index" : 0,
            "child" : {"name" : "X_001392_STA_ETHER_MAC", "index" : 0}}}},
    }

    # create list testcase name and their id
    dict_testcases = {}
    for testsuite in dict_testsuites.keys():
        index = 1
        for testcase in dict_type_info[testsuite]:
            tc_id = dict_testsuites[testsuite] + '.' + str(index)
            dict_testcases[testcase] = tc_id
            index += 1

    for type in dict_type_info.keys():
        list_info = dict_type_info[type]
        for info in list_info:
            temp = copy.deepcopy(template)
            temp[0] = temp[0] % (dict_testcases[info], info, type)
            temp[2]['info'] = info
            temp[2]['type'] = type
            temp[2]['path'] = dict_type_path[type]
            temp[2]['exc_level'] = 2
            temp[2]['is_cleanup'] = False
            params.append(temp)

    return params


def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)

    print "\n"
    print "----------- Get AP that you want to test: ----------"
    #ap_sym_dict = tbcfg['ap_sym_dict']

    dict_aps = tbcfg['ap_sym_dict']


    active_ap_list = getActiveApUpdate(dict_aps.keys())

    for active_ap in active_ap_list:
        print "\n"
        print "----------- Get adapter associate with AP (%s) above: ----------" % active_ap
        dict_ads = tbcfg['ad_sym_dict']
        active_ad_list = getActiveApUpdate(dict_ads.keys())
        temp_for_ad = []
        for active_ad in active_ad_list:
            temp_for_station = []
            print "\n"
            print "----------- Get station associate with AD (%s): ----------" % active_ad
            list_station = getActiveStation(tbcfg)
            for station in list_station:
                temp_for_station.append({'ip_addr' : station})
            temp = {}
            temp['ip_addr'] = active_ad
            temp['local_station'] = temp_for_station
            temp_for_ad.append(temp)

        default_params = {
            'active_ap' : {
                'active_ad' : temp_for_ad
            }
        }
        #default_params['active_ap'].update(dict_aps[active_ap])
        default_params['active_ap']['ip_addr'] = active_ap
        ts = get_testsuite('ATT_DeviceInfo', 'Verify some elements related to Device Information after using JAR file to collect data')
        tc_list = _defineTestParams()
        test_order = 1
        test_added = 0
        test_name = "ATT Data Collection (Combotest)"
        for i in range(len(tc_list)):
            tc_list[i][2].update(default_params)
            exc_level = tc_list[i][2]['exc_level']
            is_cleanup = tc_list[i][2]['is_cleanup']
            del tc_list[i][2]['exc_level']
            del tc_list[i][2]['is_cleanup']
            if addTestCase(ts, tc_list[i][1], tc_list[i][0], tc_list[i][2], test_order, exc_level, is_cleanup) > 0:
                test_added += 1
                test_order += 1

    print "\n-- Summary: added %d test cases into test suite %s" % (test_added, ts.name)


if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

