from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(baseid):
    return u'TCID: 01.05.02.%02d' % (baseid)

def _description():
    desc = list()
    desc.append("RSM CLI - QoS Group Commands")
    desc.append("RSM CLI - System Group Commands")
    desc.append("RSM CLI - Radio Group Commands")
    desc.append("RSM CLI - Vlan Group Commands")
    desc.append("RSM CLI - ACL Group Commands")
    desc.append("RSM CLI - Shaper Group Commands")

    return desc

def _getCommonName():
    desc = _description()

    common_name_list = list()
    for i in range(len(desc)):
        common_name_list.append("%s - %s" % (_tcid(i+1), desc[i]))

    return common_name_list

def _defineTestParams():
    params = list()

    params.append(dict(qosgroup=True))
    params.append(dict(systemgroup=True))
    params.append(dict(radiogroup=True, is5GHz=None))
    params.append(dict(vlangroup=True))
    params.append(dict(aclgroup=True))
    params.append(dict(shaper=True))

    return params

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:
        common_name_list = _getCommonName()
        test_cfgs = _defineTestParams()
#        ts = get_testsuite('RSM CLI Verification',
#                          'Verify stuffs related to RSM using CLI commands')
        test_order = 1
        test_added = 0
        test_name = "RSM_CLI"
        
        #louis.lou@ruckuswireless.com for split suite with ap model.
        ap_model = raw_input("Input %s model [example: zf2942]: " % active_ap)
        
        ans = raw_input("** Run AP [symbolic=%s] with 5.0GHz band? [n/Y]: " % active_ap)
        
        if ans.lower() == 'y': 
            is5ghz = True
            ts_name = '%s - RSM CLI Verification - 5G' % ap_model
        else: 
            is5ghz = False
            ts_name = '%s - RSM CLI Verification' % ap_model
        
        ts = get_testsuite(ts_name,
                          'Verify stuffs related to RSM using CLI commands')
        
        default_params = dict(active_ap=active_ap)
        for i in range(len(test_cfgs)):
            temp = default_params.copy()
            temp.update(test_cfgs[i])
            if temp.has_key('is5GHz'):
                temp['is5GHz'] = is5ghz
            print "\n--------"
            addTestCase(ts, test_name, common_name_list[i], temp, test_order)
            test_added += 1
            test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases in to test suite %s" % (active_ap,
                                                                                         test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)
