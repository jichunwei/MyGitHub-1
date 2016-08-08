'''
Device View

5    ZF2925 8.0 wireless Authentication
5.1    Open System
5.2.1    Open-WEP-64-5 ascii
5.2.2    Open-WEP-64-10 hex
5.3.1    Open-WEP-128-13 ascii
5.3.2    Open-WEP-128-26 hex
5.4    Shared-WEP-64
5.5    Shared-WEP-128
5.6    WPA-PSK-TKIP
5.7    WPA-PSK-AES
5.8    WPA2-PSK-TKIP
5.9    WPA2-PSK-AES
5.10    WPA-TKIP
5.11    WPA-AES
5.12    WPA2-TKIP
5.13    WPA2-AES

'''

import sys

from libFM_TestSuite import make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    tc_map = '03.01.02'

    tc_templates = [
            'TCID:%s- Search by Serial number in 12 digits and MAC address in Device View of FM' % tc_map,
            'FMDV_DeviceSearch', {
                'Note': 'No need config for this test case',
            }
    ]


    #tbCfg = eval(kwa['testbed'].config)
    #aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg))
    #client_ip = select_client(tbCfg)

    print 'Generate testcases for Device Seach by Serial/MAC for all models'

    test_cfgs = {}
    test_cfgs['03.01.02'] = tc_templates

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - Search By Serial and MAC', [test_cfgs[k] for k in keys]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if not _dict.has_key('define_ts_cfg'): _dict['define_ts_cfg'] = define_ts_cfg
    # This testsuite doesn't need model
    _dict['ignoreModel'] = True

    make_test_suite(**_dict)
