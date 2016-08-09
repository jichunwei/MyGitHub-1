import sys, os, types, copy, re
from django.core.management import setup_environ
os.chdir("../../..")
sys.path.append(os.getcwd())
from RuckusAutoTest.common.Ratutils import *
import settings
setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from RuckusAutoTest.models import *
from RuckusAutoTest.testbeds import *
from RuckusAutoTest.components import *

def getTestbed(**kwargs):
    tb_info_file = "./RuckusAutoTest/common/IPTV_Testbed_Info_Default.inf"

    tb_info = load_config_file(tb_info_file)
    tb_name = raw_input("Your test bed name: ")
    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = tb_info['location']
        tb_owner = tb_info['owner']

        win_sta_list = "'win_sta_list':%s" % tb_info['win_sta_list']
        linux_sta_list = "'linux_sta_list':%s" % tb_info['linux_sta_list']

        sta_wifi_subnet = "'sta_wifi_subnet':%s" % tb_info['sta_wifi_subnet']
        sta_wireless_interface_info = "'sta_wireless_interface_info':%s" % tb_info['sta_wireless_intf_info']
        sta_pppoe_subnet = "'sta_pppoe_subnet':%s" % tb_info['sta_pppoe_subnet']
        ap_conf = "'ap_conf':%s" % tb_info['ap_conf']
        ftpserv = "'ftpserv':%s" % tb_info['ftpserv']
        pwr_mgmt = "'pwr_mgmt':%s" % tb_info['pwr_mgmt']

        # delete common information and keep AP & Adapter information to create testbed config
        del tb_info['name']
        del tb_info['location']
        del tb_info['owner']
        del tb_info['win_sta_list']
        del tb_info['linux_sta_list']
        del tb_info['sta_wifi_subnet']
        del tb_info['sta_wireless_intf_info']
        del tb_info['sta_pppoe_subnet']
        del tb_info['ap_conf']
        del tb_info['ftpserv']
        del tb_info['pwr_mgmt']

        ap_sym_dict = ""
        ad_sym_dict = ""
        for dev in tb_info.keys():
            if dev.lower().startswith('ap'):
                ap_sym_dict += "'%s':%s, " % (dev, tb_info[dev])
            else:
                ad_sym_dict += "'%s':%s, " % (dev, tb_info[dev])

        ap_sym_dict = "'ap_sym_dict':{%s}" % ap_sym_dict.strip().strip(',')
        ad_sym_dict = "'ad_sym_dict':{%s}" % ad_sym_dict.strip().strip(',')
        tb_config = "{%s, %s, %s, %s, %s, %s, %s, %s, %s, %s}" % (win_sta_list,
                                                                  linux_sta_list,
                                                                  sta_wifi_subnet,
                                                                  sta_wireless_interface_info,
                                                                  ap_sym_dict,
                                                                  ad_sym_dict,
                                                                  ap_conf,
                                                                  sta_pppoe_subnet,
                                                                  ftpserv,
                                                                  pwr_mgmt)

        testbed = {'name':tb_name,
                   'tbtype': TestbedType.objects.get(name='AP_IPTV'),
                   'location':tb_location,
                   'owner':tb_owner,
                   'resultdist':tb_owner,
                   'config':tb_config}
        tb = Testbed(**testbed)
        tb.save()

    return tb

def getSta_list(tb_config):
    sta_ip_list = tb_config['win_sta_list'] + tb_config['linux_sta_list']
    return sta_ip_list

def showApSymList(ap_dict):
    for k in sorted(ap_dict.keys()):
        print "%s : ip_addr=%s" % (k, ap_dict[k]['ip_addr'])

def getActiveAP(ap_dict):
    showApSymList(ap_dict)
    active_ap_list = raw_input('Select symbolic APs from above list, separated by space (enter all for all APs): ').split()
    if re.match(r'^all$', active_ap_list[0], re.M):
        return ap_dict.keys()
    return active_ap_list

def get_testsuite(ts_name, description):
    print "Adding TestSuite %s " % ts_name
    try:
        ts = TestSuite.objects.get(name=ts_name)
        print "TestSuite '%s' is already in database." % ts_name
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % ts_name
        ts = TestSuite(name=ts_name, description=description)
        ts.save()
    print "Adding test cases to TestSuite %s " % ts.name
    return ts

def getTestbedConfig(tbi):
    tbi_config = tbi.config.replace('\n', '').replace('\r', '')
    tbconfig = eval(tbi_config)
    return tbconfig

_tc_info = "%4s   testsuite: [%s]\n       test_name: [%s]\n     common_name: [%s]"
def insertTestCase(testcase, unique=True):
    if unique:
        tclist = TestCase.objects.filter( suite=testcase.suite
                                        , test_name=testcase.test_name
                                        , common_name=testcase.common_name
                                        )
                                        # test_params=testcase.test_params
        if len(tclist) > 0:
            print _tc_info % ('SKIP', testcase.suite, testcase.test_name, testcase.common_name)
            return (-1 * tclist[0].id)
    print _tc_info % ('ADD', testcase.suite, testcase.test_name, testcase.common_name)
    testcase.save()
    return testcase.id

# called testTestCase() is prefered then insertTestCase()
def addTestCase( test_suite, test_name, common_name, test_param, test_order=0):
    return insertTestCase( TestCase( suite=test_suite,
                                     test_name='ap.%s' % test_name,
                                     seq=test_order,
                                     test_params= str(test_param),
                                     common_name=common_name) )
