import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(baseId, offId):
    return u'TCID:10.05.03.%02d' % (baseId + offId)

def makeTestCfg():
    """
    """
    test_cfg = dict()
    #_wcid = 0
    #test_cfg[1]  = ( dict(uplink_rate_limit="100 kbps", downlink_rate_limit="100 kbps", margin_of_error=0.04, number_of_ssid=1)
    #                    , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
    #                      , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
    #                      , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
    #                      , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
    #                      , u"zf2925 AP": _tcid(101, 0)
    #                      , u"zf2942 AP": _tcid(102, 0)
    #                      , u"zf7942 AP": _tcid(103, 0)
    #                      , u"zf2741 AP": _tcid(104, 0)
    #                      }
    #                   )
    _wcid = 1
    test_cfg[2]  = ( dict(uplink_rate_limit="250 kbps", downlink_rate_limit="250 kbps", margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(111, 0)
                          , u"zf2942 AP": _tcid(112, 0)
                          , u"zf7942 AP": _tcid(113, 0)
                          , u"zf2741 AP": _tcid(114, 0)
                          }
                       )
    _wcid = 2
    test_cfg[3]  = ( dict(uplink_rate_limit="500 kbps", downlink_rate_limit="500 kbps", margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(121, 0)
                          , u"zf2942 AP": _tcid(122, 0)
                          , u"zf7942 AP": _tcid(123, 0)
                          , u"zf2741 AP": _tcid(124, 0)
                          }
                       )
    _wcid = 3
    test_cfg[4]  = ( dict(uplink_rate_limit="1 mbps"  , downlink_rate_limit="1 mbps"  , margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(131, 0)
                          , u"zf2942 AP": _tcid(132, 0)
                          , u"zf7942 AP": _tcid(133, 0)
                          , u"zf2741 AP": _tcid(134, 0)
                          }
                       )
    _wcid = 4
    test_cfg[5]  = ( dict(uplink_rate_limit="2 mbps"  , downlink_rate_limit="2 mbps"  , margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(141, 0)
                          , u"zf2942 AP": _tcid(142, 0)
                          , u"zf7942 AP": _tcid(143, 0)
                          , u"zf2741 AP": _tcid(144, 0)
                          }
                       )
    _wcid = 5
    test_cfg[6]  = ( dict(uplink_rate_limit="5 mbps"  , downlink_rate_limit="5 mbps"  , margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(151, 0)
                          , u"zf2942 AP": _tcid(152, 0)
                          , u"zf7942 AP": _tcid(153, 0)
                          , u"zf2741 AP": _tcid(154, 0)
                          }
                       )
    _wcid = 6
    test_cfg[7]  = ( dict(uplink_rate_limit="10 mbps" , downlink_rate_limit="10 mbps" , margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(161, 0)
                          , u"zf2942 AP": _tcid(162, 0)
                          , u"zf7942 AP": _tcid(163, 0)
                          , u"zf2741 AP": _tcid(164, 0)
                          }
                       )
    _wcid = 7
    test_cfg[8]  = ( dict(uplink_rate_limit="20 mbps" , downlink_rate_limit="20 mbps" , margin_of_error=0.04, number_of_ssid=1)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(171, 0)
                          , u"zf2942 AP": _tcid(172, 0)
                          , u"zf7942 AP": _tcid(173, 0)
                          , u"zf2741 AP": _tcid(174, 0)
                          }
                       )
    #_wcid = 8
    #test_cfg[9]  = ( dict(uplink_rate_limit="50 mbps" , downlink_rate_limit="50 mbps" , margin_of_error=0.04, number_of_ssid=1)
    #                    , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
    #                      , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
    #                      , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
    #                      , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
    #                      , u"zf2925 AP": _tcid(181, 0)
    #                      , u"zf2942 AP": _tcid(182, 0)
    #                      , u"zf7942 AP": _tcid(183, 0)
    #                      , u"zf2741 AP": _tcid(184, 0)
    #                      }
    #                   )
    #_wcid = 9
    #test_cfg[10] = ( dict(uplink_rate_limit="100 kbps", downlink_rate_limit="2 mbps"  , margin_of_error=0.04, number_of_ssid=1)
    #                    , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
    #                      , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
    #                      , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
    #                      , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
    #                      , u"zf2925 AP": _tcid(191, 0)
    #                      , u"zf2942 AP": _tcid(192, 0)
    #                      , u"zf7942 AP": _tcid(193, 0)
    #                      , u"zf2741 AP": _tcid(194, 0)
    #                      }
    #                   )
    _wcid = 10
    #JLIN@20090113 changed number_of_ssid from 8 to 6, because ZD80 only support 6 WLANs with mesh
    test_cfg[11] = ( dict(uplink_rate_limit="10 mbps" , downlink_rate_limit="10 mbps" , margin_of_error=0.04, number_of_ssid=6)
                        , { u'zf2925 ROOT': _tcid(1,_wcid),  u'zf2925 MESH': _tcid(12,_wcid)
                          , u'zf2942 ROOT': _tcid(23,_wcid), u'zf2942 MESH': _tcid(34,_wcid)
                          , u'zf7942 ROOT': _tcid(45,_wcid), u'zf7942 MESH': _tcid(56,_wcid)
                          , u'zf2741 ROOT': _tcid(67,_wcid), u'zf2741 MESH': _tcid(78,_wcid)
                          , u"zf2925 AP": _tcid(201, 0)
                          , u"zf2942 AP": _tcid(202, 0)
                          , u"zf7942 AP": _tcid(203, 0)
                          , u"zf2741 AP": _tcid(204, 0)
                          }
                       )

    return test_cfg

def getCommonNameWithTcid(active_ap_type_role, apcfg, test_cfg):
    tcid = test_cfg[1][active_ap_type_role] if test_cfg[1].has_key(active_ap_type_role) else 'tcid:0.0.0.0'
    cname = getCommonName(test_cfg[0])
    return tcid + " - " + cname + " - " + active_ap_type_role

def getCommonName(tcfg):
    cname = "Up[%s]/Down[%s] RL on %d WLAN(s)" %  ( tcfg['uplink_rate_limit'],tcfg['downlink_rate_limit'],tcfg['number_of_ssid'])
    return cname

def make_test_suite(**kwargs):
    """
    """
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts = testsuite.get_testsuite('Mesh - Integration - Rate Limiting',
                      'Verify the ability of the ZD to control rate limit rules on mesh network properly')

    target_sta = testsuite.getTargetStation(sta_ip_list)
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    test_cfg = makeTestCfg()
    test_order = 1
    test_added = 0
    test_name = 'ZD_RateLimiting'

    for active_ap in sorted(active_ap_list):
        test_params = {}
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)
        for idx, tcfg in test_cfg.iteritems():
            test_params = tcfg[0]
            test_params['target_station'] = target_sta
            test_params['active_ap'] = active_ap
            test_params['traffic_srv_addr'] = '192.168.0.252'  #getServerIp

            common_name = "Mesh %s" % getCommonNameWithTcid(ap_type_role, apcfg, tcfg)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
