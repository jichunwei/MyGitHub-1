from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme


def defineTestConfiguration(build_stream):
    test_cfgs = []

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True}, "IPTV_Unicast_Streaming",
                      "Streaming with no ToS value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'voice', 'queue':'voice'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched ToS value [Voice] and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'video', 'queue':'video'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched ToS value [Video] and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True, 'tos_matching':False,
                       'tos_classify_value':'0x18'}, "IPTV_Unicast_Streaming",
                       "Streaming with no matched ToS value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'heuristics_enable': True}, "IPTV_Unicast_Streaming",
                      "Streaming with no ToS value and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'heuristics_enable': True, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'voice'}, "IPTV_Unicast_Streaming",
                       "Streaming with matched ToS value [Voice] and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'heuristics_enable': True, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'video'}, "IPTV_Unicast_Streaming",
                       "Streaming with matched ToS value [Video] and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'heuristics_enable': True, 'tos_matching':False,
                       'tos_classify_value':'0x18'}, "IPTV_Unicast_Streaming",
                       "Streaming with no matched ToS value and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True, 'tos_mark_enable':True,
                       'tos_mark_value':'0x18', 'media':'voice', 'queue':'voice', 'filter_matching':True,
                       'build_stream':build_stream},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched port and remarked ToS value [Voice] and ToS Marking Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable': True, 'tos_mark_enable':True,
                       'tos_mark_value':'0x18', 'media':'video', 'queue':'video', 'filter_matching':True,
                       'build_stream':build_stream},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched port and remarked ToS value [Video] and ToS Marking Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable':False, 'queue':'data'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with no ToS value and heuristics disabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable':False, 'tos_matching':False,
                       'tos_classify_value':'0x18', 'queue':'data'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with no matched ToS value and heuristics disabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable':False, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'queue':'voice', 'media':'voice'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched voice ToS value and heuristics disabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'heuristics_enable':False, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'queue':'video', 'media':'video'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matched video ToS value and heuristics disabled",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'video',
                       'heuristics_media':'video', 'tos_classify_enable':True},
                       "IPTV_Unicast_Streaming",
                       "Streaming with no ToS value and matching heuristics algorithm for video",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'video',
                       'heuristics_media':'video', 'tos_classify_enable':True},
                       "IPTV_Unicast_Streaming",
                       "Streaming with no ToS value and matching heuristics algorithm for voice",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'video',
                       'heuristics_media':'video', 'tos_classify_enable':True, 'tos_classify_value':'0x18'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with non-matching ToS value and matching heuristics algorithm for video",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'voice',
                       'heuristics_media':'voice', 'tos_classify_enable':True, 'tos_classify_value':'0x18'},
                       "IPTV_Unicast_Streaming",
                       "Streaming with non-matching ToS value and matching heuristics algorithm for voice",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'voice', 'media':'voice',
                       'tos_classify_enable':True, 'tos_classify_value':'0x18',  'heuristics_media':'video',
                       'tos_matching':True}, "IPTV_Unicast_Streaming",
                       "Streaming with matching voice ToS value and matching heuristics algorithm for video",))

    test_cfgs.append(({'heuristics_enable':True, 'heuristics_matching':True, 'queue':'video', 'tos_classify_enable':True,
                       'tos_classify_value':'0x18', 'media':'video', 'heuristics_media':'voice', 'tos_matching':True},
                       "IPTV_Unicast_Streaming",
                       "Streaming with matching video ToS value and matching heuristics algorithm for voice",))

    test_cfgs.append(({'tos_classify_enable':True, 'tos_classify_value':'0x18', 'tos_matching':True,
                       'filter_matching':True, 'media':'voice', 'filer_media':'video', 'heuristics_enable':True,
                       'queue':'voice'}, "IPTV_Unicast_Streaming",
                       "Streaming with matching voice ToS value and matching port filter rule for video",))

    test_cfgs.append(({'tos_classify_enable':True, 'tos_classify_value':'0x18', 'tos_matching':True,
                       'filter_matching':True, 'media':'video', 'filer_media':'voice', 'heuristics_enable':True,
                       'queue':'video'}, "IPTV_Unicast_Streaming",
                       "Streaming with matching video ToS value and matching port filter rule for voice",))

    test_cfgs.append(({}, "IPTV_Dead_Station_Count", "Streaming with Dead Station count",))

    test_cfgs.append(({}, "IPTV_Port_Filter_Drop", "Streaming with Port matching filter",))

    return test_cfgs

def createTestSuite(**kwargs):
    tb = getTestbed(**kwargs)
    tbcfg = eval(tb.config)

    # Get tested stations
    ip_list = []
    sta_ip_list = getSta_list(tbcfg)
    for i in range(len(sta_ip_list)):
        ip_list.append("%d - %s" % (i, sta_ip_list[i]))
    print "\nStation IP list:"
    print "\n".join(ip_list)
    id = raw_input("Pick up a station behind the AP: ")
    local_station = sta_ip_list[int(id)]
    id = raw_input("Pick up a Linux station behind the Adapter: ")
    remote_station = sta_ip_list[int(id)]
    id = raw_input("Pick up a capturing station: ")
    capture_station = sta_ip_list[int(id)]

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        test_order = 1
        #louis.lou@ruckuswireless.com for split suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        id_5g = raw_input("Run AP with 5.0GHz band? [N/y]: ")

        if id_5g.upper() == "Y":
            ts_name = "%s - IPTV_Unicast_Streaming - 5G" % ap_model
        else:
            ts_name = "%s - IPTV_Unicast_Streaming" % ap_model
        
        ts = get_testsuite(ts_name, ' Verify stuffs related to IPTV Unicast Streaming with %s [%s]' % (active_ap, ap_model))

        active_ad = ''
        ap_channel = ''
        bs_num = False
        id = raw_input("Is AP image version from 8.0 and higher? [Y/n]: ")
        if id.upper() == "Y":
            bs_num = True
#            id = raw_input("Run AP with 5.0GHz band? [n/Y]: ")
            if id_5g.upper() == "N":
                wlan_if = 'wlan0'
                ap_channel = '6'
                active_ad = 'ad_04'
            else:
                ap_channel = '36'
                wlan_if = 'wlan8'
                active_ad = 'ad_02'
        else:
            id = raw_input("The tested Adapters is VF7111 model? [n/Y]: ")
            if id.upper() == "N":
                active_ad = 'ad_04'
                ap_channel = '6'
            else:
                active_ad = 'ad_02'
                ap_channel = '36'
            wlan_if = 'wlan0'

        use_pppoe = False
        test_cfgs = defineTestConfiguration(bs_num)

        common_params = {'local_station': local_station,
                         'remote_station': remote_station,
                         'active_ap':active_ap,
                         'active_ad':active_ad,
                         'wlan_if':wlan_if,
                         'ap_channel':ap_channel,
                         'capture_station':capture_station
                         }

        while True:
            for test_params, test_name, common_name in test_cfgs:
                temp = "TCID: 01.01.03.%02d" % test_order
                if use_pppoe:
                    common_name += " via PPPoE Connection"
                common_name = temp + " - " + common_name
                temp = common_params.copy()
                temp['use_pppoe'] = use_pppoe
                temp.update(test_params)

                addTestCase(ts, test_name, common_name, str(temp), test_order)
                test_order += 1

            if use_pppoe: break
            text = raw_input("Do you want to add more test cases to test Unicast streaming via PPPoE connection? [Y/n]: ")
            if text.upper() == "N": break
            else:
                use_pppoe = True
                continue

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    createTestSuite(**_dict)
