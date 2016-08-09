from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme


def defineTestConfiguration(build_stream):
    test_cfgs = []

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'video'}, "IPTV_Multicast_Streaming",
                      "Streaming with no ToS value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'voice', 'media':'voice', 'tos_matching':True,
                       'tos_classify_value':'0xE0'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched ToS [Voice] value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'video', 'media':'video', 'tos_matching':True,
                       'tos_classify_value':'0x28'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched ToS [Video] value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'video', 'tos_matching':False, 'tos_classify_value':'0x18'},
                        "IPTV_Multicast_Streaming",
                       "Streaming with no matched ToS value and ToS classification Enabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'queue':'video'}, "IPTV_Multicast_Streaming",
                      "Streaming with no ToS value and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'queue':'video', 'media':'voice', 'tos_matching':True,
                       'tos_classify_value':'0x28'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched ToS [Voice] value and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'queue':'video', 'media':'video', 'tos_matching':True,
                       'tos_classify_value':'0x28'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched ToS [Video] value and ToS classification Disabled",))

    test_cfgs.append(({'tos_classify_enable':False, 'queue':'video', 'tos_matching':False, 'tos_classify_value':'0x18'},
                       "IPTV_Multicast_Streaming",
                       "Streaming with no matched ToS value and ToS classification Disabled",))

    test_cfgs.append(({'queue':'video', 'port_matching_filter':True, 'media':'voice'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched port with action is tos and media is voice",))

    test_cfgs.append(({'queue':'video', 'port_matching_filter':True, 'media':'video'}, "IPTV_Multicast_Streaming",
                       "Streaming with matched port with action is tos and media is video",))

    test_cfgs.append(({'queue':'data', 'directed_multicast':False}, "IPTV_Multicast_Streaming",
                       "Streaming with Mcast disabled",))

    test_cfgs.append(({'queue':'video', 'directed_multicast':True}, "IPTV_Multicast_Streaming",
                       "Streaming with Mcast enabled",))

    test_cfgs.append(({'tos_classify_enable':True, 'igmp_snooping':False}, "IPTV_Multicast_Streaming",
                       "Streaming with IGMP snooping disabled",))

    test_cfgs.append(({'dead_station':True}, "IPTV_Multicast_Streaming",
                       "Streaming with Dead Station Count",))

    test_cfgs.append(({'max_igmp_group':32, 'packet_replay_file':'32_igmp_groups.pcap'}, "IPTV_Multicast_Streaming",
                       "Streaming with Max IGMP group",))

    test_cfgs.append(({'igmp_version':3, 'packet_replay_file':'32_igmp_v3_groups.pcap'}, "IPTV_Multicast_Streaming",
                       "Streaming with IGMP V3",))

    test_cfgs.append(({'port_matching_filter_tos':False, 'queue':'video', 'tos_classify_enable':True},
                      "IPTV_Multicast_Streaming", "Streaming with Port matching filter",))

    test_cfgs.append(({'heuristics_enable':False, 'queue':'video', 'tos_classify_enable':True, 'tos_matching':False,
                       'tos_classify_value':'0x18'},
                       "IPTV_Multicast_Streaming", "Streaming with heuristics disabled and non-matching TOS value",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':True, 'directed_bcast':False, 'queue':'video',
                       'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "No ToS value, IGMP snooping ENABLE, directed Mcast ENABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':True, 'directed_bcast':False, 'queue':'video',
                       'tos_matching':False, 'tos_classify_value':'0x18', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Non-matching ToS value, IGMP snooping ENABLE, directed Mcast ENABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':True, 'directed_bcast':False, 'queue':'voice',
                       'tos_matching':True, 'tos_classify_value':'0x18', 'media':'voice', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Matching ToS value, IGMP snooping ENABLE, directed Mcast ENABLE, directed bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':False, 'directed_bcast':False, 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "No ToS value, IGMP snooping ENABLE, directed Mcast DISABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':False, 'directed_bcast':False, 'tos_matching':False,
                       'tos_classify_value':'0x18', 'build_stream':build_stream}, "IPTV_Multicast_Combination",
                       "Non-matching ToS value, IGMP snooping ENABLE, directed Mcast DISABLE, directed bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':True, 'directed_mcast':False, 'directed_bcast':False, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'voice', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Matching ToS value, IGMP snooping ENABLE, directed Mcast DISABLE, directed bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':True, 'directed_bcast':False, 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "No ToS value, IGMP snooping DISABLE, directed Mcast ENABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':True, 'directed_bcast':False, 'tos_matching':False,
                       'tos_classify_value':'0x18', 'build_stream':build_stream}, "IPTV_Multicast_Combination",
                       "Non-matching ToS value, IGMP snooping DISABLE, directed Mcast ENABLE, directed bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':True, 'directed_bcast':False, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'voice', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Matching ToS value, IGMP snooping DISABLE, directed Mcast ENABLE, directed bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':True, 'queue':'data',
                       'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "No ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast ENABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':True, 'queue':'data',
                       'tos_matching':False, 'tos_classify_value':'0x18', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Non-matching ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast ENABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':True, 'queue':'data',
                       'tos_matching':True, 'tos_classify_value':'0x18', 'media':'voice', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Matching ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast ENABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':False, 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "No ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':False, 'tos_matching':False,
                       'tos_classify_value':'0x18', 'build_stream':build_stream}, "IPTV_Multicast_Combination",
                       "Non-matching ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'igmp_snooping':False, 'directed_mcast':False, 'directed_bcast':False, 'tos_matching':True,
                       'tos_classify_value':'0x18', 'media':'voice', 'build_stream':build_stream},
                       "IPTV_Multicast_Combination",
                       "Matching ToS value, IGMP snooping DISABLE, directed Mcast DISABLE, directed Bcast DISABLE",))

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'video', 'stream_with_multi_sta':True,
                       'stream_with_same_group':True}, "IPTV_Multicast_Streaming",
                       "Streaming with multiple stations to the different groups",))

    test_cfgs.append(({'tos_classify_enable':True, 'queue':'video', 'stream_with_multi_sta':True,
                       'stream_with_same_group':False, 'win_multicast_group':'239.255.0.100'},
                       "IPTV_Multicast_Streaming",
                       "Streaming with multiple stations to the same group",))

    test_cfgs.append(({'verify_bcast_threshold':True, 'bcast_threshold':'1', 'ipsrc_bcast':'192.168.2.12',
                       'ipdst_bcast':'192.168.2.255', 'packet_replay_file':'BROADCAST.pcap',
                       'build_stream':build_stream}, "IPTV_Multicast_Combination",
                       "Verify Directed Threshold"))

    if not build_stream:
        test_cfgs.append(({'queue':'data', 'unknown_mcast_drop':False, 'unknown_multicast_group': '239.255.0.200'},
                          "IPTV_Multicast_Streaming", "Streaming with unknown multicast drop disabled",))

        test_cfgs.append(({'queue':'data', 'unknown_mcast_drop':True, 'unknown_multicast_group': '239.255.0.200'},
                          "IPTV_Multicast_Streaming", "Streaming with unknown multicast drop enabled",))

        test_cfgs.append(({'well_known_multicast': True, 'packet_replay_file':'SSDP.pcap',
                           'multicast_address_src': '192.168.0.2',
                           'multicast_address_dst':'239.255.255.250'}, "IPTV_Multicast_Streaming",
                           "Streaming with Well known Mcast forward Enabled / Disabled",))

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
    remote_linux_sta = sta_ip_list[int(id)]
    id = raw_input("Pick up a Windows station behind the Adapter: ")
    remote_win_sta = sta_ip_list[int(id)]
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
        
        id_5g = raw_input("Run AP with 5.0GHz band? [n/Y]: ")
        if id_5g.upper() == "Y":
            ts_name = "%s - IPTV_Multicast_Streaming - 5G" % ap_model
        else:
            ts_name = "%s - IPTV_Multicast_Streaming " % ap_model
            
        ts = get_testsuite(ts_name, 'Verify stuffs related to IPTV Multicast Streaming with %s [%s]' % (active_ap, ap_model))

        active_ad = ''
        ap_channel = ''
        build_stream = False
        id = raw_input("Is AP image version from 8.0 and higher? [Y/n]: ")
        if id.upper() == "Y":
            build_stream = True
#            id = raw_input("Run AP with 5.0GHz band? [n/Y]: ")
            if id_5g.upper() == "N":
                wlan_if = 'wlan0'
                ap_channel = '6'
                active_ad = 'ad_04'
                passive_ad = 'ad_03'
            else:
                ap_channel = '36'
                wlan_if = 'wlan8'
                active_ad = 'ad_02'
                passive_ad = 'ad_01'
        else:
            id = raw_input("The tested Adapters is VF7111 model? [n/Y]: ")
            if id.upper() == "N":
                ap_channel = '6'
                active_ad = 'ad_04'
                passive_ad = 'ad_03'
            else:
                ap_channel = '36'
                active_ad = 'ad_02'
                passive_ad = 'ad_01'
            wlan_if = 'wlan0'

        common_params = {'local_station': local_station,
                         'remote_linux_sta': remote_linux_sta,
                         'remote_win_sta': remote_win_sta,
                         'active_ap':active_ap,
                         'active_ad':active_ad,
                         'passive_ad':passive_ad,
                         'wlan_if':wlan_if,
                         'ap_channel':ap_channel,
                         'capture_station':capture_station
                         }

        test_cfgs = defineTestConfiguration(build_stream)
        for test_params, test_name, common_name in test_cfgs:
            temp = "TCID: 01.01.02.%02d" % test_order
            common_name = temp + " - " + common_name
            temp = common_params.copy()
            temp.update(test_params)
            temp.update({'multicast_group': '239.255.0.%d' % (test_order+1), 'build_stream':build_stream})
            addTestCase(ts, test_name, common_name, str(temp), test_order)
            test_order += 1

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    createTestSuite(**_dict)

