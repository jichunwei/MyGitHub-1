from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(subid, baseid):
    return u'TCID:01.06.%02d.%02d' % (subid, baseid)

def _description():
    desc = list()
    desc.append("%sGHz - Receive multicast frame from Multicast router and trasmit multicast frame to the Adapter")
    desc.append("%sGHz multicast streaming and Ethernet port is tagged")
    desc.append("%sGHz multicast streaming and Ethernet port is untagged")
    desc.append("%sGHz unicast/VoD streaming and Ethernet port is tagged")
    desc.append("%sGHz unicast/VoD streaming and Ethernet port is untagged")
    desc.append("%sGHz multicast streaming with matched ToS value and Ethernet port is tagged")
    desc.append("%sGHz multicast streaming with matched ToS value and Ethernet port is untagged")
    desc.append("%sGHz video on-demand using tcp protocol with port matching filter")
    desc.append("%sGHz unicast/VoD streaming with port matching filter and Ethernet port is tagged")
    desc.append("%sGHz unicast/VoD streaming with port matching filter and Ethernet port is untagged")

    return desc

def _allDescription():
    desc = _description()
    all_desc = list()
    for each in desc:
        for radio in ["5", "2.4"]:
            desc_tmp = each % radio
            all_desc.append(desc_tmp)

    return all_desc

def _getCommonName():
    all_desc = _allDescription()
    common_name_list = list()
    count = 0
    for subid in [1,2,3,4]:
        if subid == 1:
            for baseid in range(1,16):
                if not baseid in range(3,12):
                    common_name_list.append("%s - %s" % (_tcid(subid, baseid), all_desc[count]))
                    count += 1
        elif subid == 2:
            for baseid in range(2,6):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), all_desc[count]))
                count += 1
        elif subid == 3:
            for baseid in range(1,5):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), all_desc[count]))
                count += 1
        else:
            for baseid in range(1,7):
                common_name_list.append("%s - %s" % (_tcid(subid, baseid), all_desc[count]))
                count += 1

    return common_name_list

def _defineTestParams():
    params = list()
    # TC 1.6.1.1 & 1.6.1.2
    params.append(dict(verify_igmp_query=True,
                       igmp_query_file='igmp_query.pcap',
                       src_igmp_query='192.168.50.254',
                       allhost_mcast='224.0.0.1',
                 )
    )

    # TC 1.6.1.12 & 1.6.1.13
    params.append(dict(use_vlan=True,
                       vlan_tagged=True,
                       streaming=True,
                       multicast=True,
                       mcast_group='239.255.0.1',
                       queue='video'
                )
    )
    # TC 1.6.1.14 & 1.6.1.15
    params.append(dict(use_vlan=True,
                       vlan_tagged=False,
                       streaming=True,
                       multicast=True,
                       mcast_group='239.255.0.2',
                       queue='video'
                )
    )
    # TC 1.6.2.2 & 1.6.2.3
    params.append(dict(use_vlan=True,
                       vlan_tagged=True,
                       streaming=True,
                       heuristics=True,
                       queue='voice'
                )
    )
    # TC 1.6.2.4 & 1.6.2.5
    params.append(dict(use_vlan=True,
                       vlan_tagged=False,
                       streaming=True,
                       heuristics=True,
                       queue='video'
                )
    )
    # TC 1.6.3.1 & 1.6.3.2
    params.append(dict(use_vlan=True,
                       vlan_tagged=True,
                       streaming=True,
                       multicast=True,
                       mcast_group='239.255.0.3',
                       verify_tos=True,
                       tos_value='0x28',
                       queue='voice'
                )
    )
    # TC 1.6.3.3 & 1.6.3.4
    params.append(dict(use_vlan=True,
                       vlan_tagged=False,
                       streaming=True,
                       multicast=True,
                       mcast_group='239.255.0.4',
                       verify_tos=True,
                       tos_value='0x28',
                       queue='voice'
                )
    )

    # TC 1.6.4.1 & 1.6.4.2
    params.append(dict(streaming=True,
                       port_matching=True,
                       use_tcp_proto=True,
                       port='5001',
                       action='tos',
                       proto='tcp',
                       queue='voice'
                )
    )
    # TC 1.6.4.3 & 1.6.4.4
    params.append(dict(use_vlan=True,
                       vlan_tagged=True,
                       streaming=True,
                       port_matching=True,
                       port='5001',
                       action='tos',
                       proto='udp',
                       queue='voice'
                )
    )
    # TC 1.6.4.5 & 1.6.4.6
    params.append(dict(use_vlan=True,
                       vlan_tagged=False,
                       streaming=True,
                       port_matching=True,
                       port='5001',
                       action='tos',
                       proto='udp',
                       queue='video'
                )
    )

    return params

def _getAllParams():
    all_params = list()

    params_list = _defineTestParams()
    for each in params_list:
        for wlanif in ['wlan8', 'wlan0']:
            temp = each.copy()
            temp['wlan_if'] = wlanif
            all_params.append(temp)

    return all_params

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)

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

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        #louis.lou@ruckuswireless.com for split suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        ts_name = '%s - IPTV Miscellaneous' % ap_model
        test_cfgs = _getAllParams()
        common_name_list = _getCommonName()
        ts = get_testsuite(ts_name, 'Verify stuffs related to IPTV Streaming beside QoS features')

        test_order = 1
        test_added = 0
        test_name = "IPTV_Miscellaneous"

        default_params = dict(active_ap=active_ap,
                              local_station=local_station,
                              remote_linux_sta=remote_linux_sta
                              )

        ans = raw_input("Is this the single band AP? [n/Y] ")
        for i in range(len(test_cfgs)):
            if ans.lower() == 'y':
                test_cfgs[i]['ap_channel'] = '6'
                test_cfgs[i]['ad_linux'] = 'ad_04'
                if i % 2 != 0:
                    # Just add test case run on 2.4GHz
                    temp = default_params.copy()
                    temp.update(test_cfgs[i])
                    print "\n--------"
                    addTestCase(ts, test_name, common_name_list[i], temp, test_order)
                    test_added += 1
                    test_order += 1
            else:
                if i % 2 != 0:
                    test_cfgs[i]['ap_channel'] = '6'
                    test_cfgs[i]['ad_linux'] = 'ad_04'
                else:
                    test_cfgs[i]['ap_channel'] = '100'
                    test_cfgs[i]['ad_linux'] = 'ad_02'

                temp = default_params.copy()
                temp.update(test_cfgs[i])
                print "\n--------"
                addTestCase(ts, test_name, common_name_list[i], temp, test_order)
                test_added += 1
                test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases in to test suite %s" % (active_ap, test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

