import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(baseId, offId):
    return u'TCID:06.01.03.%02d' % (baseId + offId)

# each test_params is a tuple with 2 elements: (<test_params dict>, <TCID>)
def makeTestParameter(tbcfg, attrs = {}):
    serv_ip = testsuite.getTestbedServerIp(tbcfg)
    default = {'rad_server':serv_ip, \
              'rad_port':'18120', \
              'rad_secret':'1234567890', \
              'ad_server':'192.168.0.250', \
              'ad_port':'389', \
              'ad_domain':'rat.ruckuswireless.com'}
    test_params = {}
    if attrs["interactive_mode"]:
        new_rad_server = raw_input('Input radius server, press Enter to default(%s)' % default['rad_server'])
        new_rad_port = raw_input('Input radius port, press Enter to default(%s)' % default['rad_port'])
        new_rad_secret = raw_input('Input radius secret, press Enter to default(%s)' % default['rad_secret'])
        new_ad_server = raw_input('Input ad server, press Enter to default(%s)' % default['ad_server'])
        new_ad_port = raw_input('Input ad port, press Enter to default(%s)' % default['ad_port'])
        new_ad_domain = raw_input('Input ad domain, press Enter to default(%s)' % default['ad_domain'])
    else:
        new_rad_server = ""
        new_rad_port = ""
        new_rad_secret = ""
        new_ad_server = ""
        new_ad_port = ""
        new_ad_domain = ""

    rad_server = default['rad_server'] if new_rad_server == "" else new_rad_server
    rad_port = default['rad_port'] if new_rad_port == "" else new_rad_port
    rad_secret = default['rad_secret'] if new_rad_secret == "" else new_rad_secret
    ad_server = default['ad_server'] if  new_ad_server == "" else new_ad_server
    ad_port = default['ad_port'] if  new_ad_port == "" else new_ad_port
    ad_domain = default['ad_domain'] if new_ad_domain == "" else new_ad_domain
    _base_id = 0
    test_params[1] = (dict(ip = serv_ip),
                       _tcid(_base_id, 1))
    _base_id = 1
    test_params[2] = (dict(ip = serv_ip, username = 'ras.local.user', password = 'ras.local.user',
                            ras_ip_addr = rad_server, ras_port = rad_port, ras_secret = rad_secret,
                            ad_ip_addr = '', ad_port = '', ad_domain = ''),
                       _tcid(_base_id, 1))
    _base_id = 2
    test_params[3] = (dict(ip = serv_ip, username = 'ras.local.user', password = 'ras.local.user',
                            ras_ip_addr = '', ras_port = '', ras_secret = '', ad_ip_addr = ad_server,
                            ad_port = ad_port, ad_domain = ad_domain),
                       _tcid(_base_id, 1))
    _base_id = 3
    test_params[4] = (dict(ip = serv_ip, expiration_time = "One day"),
                       _tcid(_base_id, 1))
    _base_id = 4
    test_params[5] = (dict(ip = serv_ip, expiration_time = "One week"),
                       _tcid(_base_id, 1))
    _base_id = 5
    test_params[6] = (dict(ip = serv_ip, expiration_time = "Two weeks"),
                       _tcid(_base_id, 1))
    _base_id = 6
    test_params[7] = (dict(ip = serv_ip, expiration_time = "One month"),
                       _tcid(_base_id, 1))
    _base_id = 7
    test_params[8] = (dict(ip = serv_ip, expiration_time = "Two months"),
                       _tcid(_base_id, 1))
    _base_id = 8
    test_params[9] = (dict(ip = serv_ip, expiration_time = "Three months"),
                       _tcid(_base_id, 1))
    _base_id = 9
    test_params[10] = (dict(ip = serv_ip, expiration_time = "Half a year"),
                       _tcid(_base_id, 1))
    _base_id = 10
    test_params[11] = (dict(ip = serv_ip, expiration_time = "One year"),
                       _tcid(_base_id, 1))
    _base_id = 11
    test_params[12] = (dict(ip = serv_ip, expiration_time = "Two years"),
                       _tcid(_base_id, 1))

    return test_params

def getCommonName(tcid, test_param):
    """
    Return a tuple with 2 elemens: (<common_name>, <test_name>)
    """
    test_name = ''
    common_name = '%s - Zero-IT Activation - Misc: %s'
    desc = ''
    if test_param.has_key('expiration_time'):
        desc = 'Dynamic PSK expiration = %s' % test_param['expiration_time']
        test_name = 'ZD_Dynamic_PSK_Expiration'
    elif test_param.has_key('ras_ip_addr') and test_param['ras_ip_addr']:
        desc = 'authenticate against Radius server'
        test_name = 'ZD_ZeroIT_Authentication'
    elif test_param.has_key('ad_domain') and test_param['ad_domain']:
        desc = 'authenticate against AD'
        test_name = 'ZD_ZeroIT_Authentication'
    else:
        desc = 'enable on 8 BSSIDs'
        test_name = 'ZD_ZeroIT_8BSSIDs'

    common_name = common_name % (tcid, desc)

    return (common_name, test_name)

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)

    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'Zero-IT Activation - Misc'
    ts = testsuite.get_testsuite(ts_name,
                      'Verify the functionality of the Zero-IT tool',
                      interactive_mode = attrs["interactive_mode"])
    test_cfgs = makeTestParameter(tbcfg, attrs)

    test_order = 1
    test_added = 0
    for test_params, test_id in test_cfgs.itervalues():
        test_params['target_station'] = target_sta
        test_params['target_sta_radio'] = target_sta_radio
        testcase_id = test_id
        testcase_id = "%s.%d" %(testcase_id, const.get_radio_id(target_sta_radio))
        common_name, test_name = getCommonName(testcase_id, test_params)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

