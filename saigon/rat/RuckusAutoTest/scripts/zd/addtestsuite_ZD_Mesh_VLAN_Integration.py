import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(baseId, offId = 0):
    return u'TCID:10.05.02.%02d' % (baseId + offId)

def makeTestParams():
    test_params_list = list()
    test_desc_list = list()
    test_name_list = list()
    test_id_list = list()

    test_params_list.append({'target_station':None, 'ip':'20.0.2.252/255.255.255.0',
                             'vlan_id':'2', 'use_valid_id':True, 'active_ap':None})
    test_desc_list.append(u"Verify a WLAN with VLAN tagging")
    test_name_list.append(u"ZD_VLAN_Configuration")
    base_id = 0
    test_id_list.append({ u"zf2925 ROOT":tcid(1, base_id), u"zf2925 MESH":tcid(4, base_id)
                        , u"zf2942 ROOT":tcid(7, base_id), u"zf2942 MESH":tcid(10, base_id)
                        , u"zf7942 ROOT":tcid(13, base_id), u"zf7942 MESH":tcid(16, base_id)
                        , u"zf2741 ROOT":tcid(19, base_id), u"zf2741 MESH":tcid(22, base_id)
                        , u"zf2925 AP":tcid(101, 0)
                        , u"zf2942 AP":tcid(102, 0)
                        , u"zf7942 AP":tcid(103, 0)
                        , u"zf2741 AP":tcid(104, 0)
                       })

    test_params_list.append({'target_station':None, 'ip':'20.0.2.252/255.255.255.0',
                             'vlan_id':'2', 'active_ap':None})
    test_desc_list.append(u"Verify a WLAN with Guest Access enabled and VLAN tagging")
    test_name_list.append(u"ZD_VLAN_GuestAccess")
    base_id = 1
    test_id_list.append({ u"zf2925 ROOT":tcid(1, base_id), u"zf2925 MESH":tcid(4, base_id)
                        , u"zf2942 ROOT":tcid(7, base_id), u"zf2942 MESH":tcid(10, base_id)
                        , u"zf7942 ROOT":tcid(13, base_id), u"zf7942 MESH":tcid(16, base_id)
                        , u"zf2741 ROOT":tcid(19, base_id), u"zf2741 MESH":tcid(22, base_id)
                        , u"zf2925 AP":tcid(111, 0)
                        , u"zf2942 AP":tcid(112, 0)
                        , u"zf7942 AP":tcid(113, 0)
                        , u"zf2741 AP":tcid(114, 0)
                       })

    test_params_list.append({'target_station':None, 'ip':'20.0.2.252/255.255.255.0',
                             'vlan_id':'2', 'active_ap':None})
    test_desc_list.append(u"Verify a WLAN with Web Authentication enabled and VLAN tagging")
    test_name_list.append(u"ZD_EncryptionTypesWebAuth")
    base_id = 2
    test_id_list.append({ u"zf2925 ROOT":tcid(1, base_id), u"zf2925 MESH":tcid(4, base_id)
                        , u"zf2942 ROOT":tcid(7, base_id), u"zf2942 MESH":tcid(10, base_id)
                        , u"zf7942 ROOT":tcid(13, base_id), u"zf7942 MESH":tcid(16, base_id)
                        , u"zf2741 ROOT":tcid(19, base_id), u"zf2741 MESH":tcid(22, base_id)
                        , u"zf2925 AP":tcid(121, 0)
                        , u"zf2942 AP":tcid(122, 0)
                        , u"zf7942 AP":tcid(123, 0)
                        , u"zf2741 AP":tcid(124, 0)
                      })

    return test_params_list, test_desc_list, test_name_list, test_id_list

def make_test_suite(**kwargs):
    mtb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts = testsuite.get_testsuite("Mesh - Integration - VLANs",
                      "Verify the functionality of WLANs with VLAN tagging enabled on mesh APs")

    target_sta = testsuite.getTargetStation(sta_ip_list)
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    test_params_list, test_desc_list, test_name_list, test_id_list = makeTestParams()

    test_order = 1
    test_added = 0
    for active_ap in sorted(active_ap_list):
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)

        for idx in range(len(test_params_list)):
            test_params_list[idx]['target_station'] = target_sta
            test_params_list[idx]['active_ap'] = active_ap

            common_name = "Mesh %s %s on %s" % (test_id_list[idx][ap_type_role],
                                                test_desc_list[idx], ap_type_role)
            
            if testsuite.addTestCase(ts, test_name_list[idx], common_name, test_params_list[idx], test_order) > 0:
                test_added += 1
            test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

# Example:
#
#    # add test cases
#    addtestsuite_ZD_Mesh_VLAN_Integration.py name='mesh'
#
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

