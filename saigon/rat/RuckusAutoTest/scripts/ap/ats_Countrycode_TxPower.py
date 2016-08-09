from libIPTV_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common import lib_Debug as bugme

def _tcid(subid, baseid):
    return u'TCID:01.13.%02d.%02d' % (subid, baseid)

def _getCommonName(countrycode_list):
    common_name_list = list()
    subid = 2
    desc = "Configure country code [%s] on the AP and verify corresponding Tx-Power"

    for idx in range(len(countrycode_list)):
        common_name_list.append("%s - %s" % (_tcid(subid, idx+1),
                                             desc % countrycode_list[idx]))

    return common_name_list

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)

    filename = "./RuckusAutoTest/common/CountryMatrix.xls"
    countrycode_list = get_country_code_list(filename)

    # Get active AP
    print "\n"
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = getActiveAP(ap_sym_dict)

    for active_ap in active_ap_list:

        test_order = 1
        test_added_ts1st = 0
        test_added_ts2nd = 0
        test_name = "Countrycode_TxPower"
        common_name_list = _getCommonName(countrycode_list)
        #louis.lou@ruckuswireless.com for split suite with ap model.
        model = raw_input("Enter AP's model (e.g 7962): ")
        ts_name1 = '%s - Countrycode-TxPower_1st' % model
        ts_name2 = '%s - Countrycode-TxPower_2nd' % model
        ts_1st = get_testsuite(ts_name1, 'Verify stuffs related to Country Code and Tx-Power')
        ts_2nd = get_testsuite(ts_name2, 'Verify stuffs related to Country Code and Tx-Power')

#        model = raw_input("Enter AP's model (e.g 7962): ")
        ans = raw_input("Enter wlan interface to test (seperated by space): ")
        wlanlist = ans.split(' ')

        if model.startswith('73'): model = '73XX'
        default_params = dict(active_ap=active_ap,
                              countrycode='',
                              wlanlist=wlanlist,
                              filename=filename,
                              model = model
                              )
        total_1st = 0

        for i in range(len(countrycode_list)):
            print "\n--------"
            temp = default_params.copy()
            temp['countrycode'] = countrycode_list[i]
            if i >= 60:
                addTestCase(ts_2nd, test_name, common_name_list[i], temp, test_order)
                test_added_ts2nd += 1
            else:
                addTestCase(ts_1st, test_name, common_name_list[i], temp, test_order)
                test_added_ts1st += 1
            test_order += 1

        print "\n-- AP[symbolic=%s] Summary: added %d test cases into test suite %s" % (active_ap,
                                                                                        test_added_ts1st, ts_1st.name)
        print "\n-- AP[symbolic=%s] Summary: added %d test cases into test suite %s" % (active_ap,
                                                                                        test_added_ts2nd, ts_2nd.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)




