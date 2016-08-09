import sys, os, types, copy, re
from django.core.management import setup_environ
os.chdir("../../..")
sys.path.append(os.getcwd())
from RuckusAutoTest.common.Ratutils import *
import settings
setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from RuckusAutoTest.models import *
from RuckusAutoTest.testbeds import AP, AP_ATT
from RuckusAutoTest.components import *

def input_with_default(prompt, default):
    txt = raw_input('%s (%s): ' % (prompt, default))
    if txt.strip() == '':
        return default
    return txt

def getTestbed(**kwargs):
    tb_info_file = "./RuckusAutoTest/common/ATT_Testbed_Info_Default.inf"

    tb_info = load_config_file(tb_info_file)
    tb_name = raw_input("Your test bed name: ")
    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = tb_info['location']
        tb_owner = tb_info['owner']

        win_sta_list = "'win_sta_list':%s" % tb_info['win_sta_list']
        ap_conf = "'ap_conf':%s" % tb_info['ap_conf']

        # delete common information and keep AP & Adapter information to create testbed config
        del tb_info['name']
        del tb_info['location']
        del tb_info['owner']
        del tb_info['win_sta_list']
        del tb_info['ap_conf']

        ap_sym_dict = ""
        ad_sym_dict = ""
        for dev in tb_info.keys():
            if dev.lower().startswith('ap'):
                ap_sym_dict += "'%s':%s, " % (dev, tb_info[dev])
            else:
                ad_sym_dict += "'%s':%s, " % (dev, tb_info[dev])

        ap_sym_dict = "'ap_sym_dict':{%s}" % ap_sym_dict.strip().strip(',')
        ad_sym_dict = "'ad_sym_dict':{%s}" % ad_sym_dict.strip().strip(',')

        tb_config = "{%s, %s, %s, %s}" % (win_sta_list, ap_sym_dict, ad_sym_dict, ap_conf)

        testbed = {'name':tb_name,
                   'tbtype': TestbedType.objects.get(name='AP_ATT'),
                   'location':tb_location,
                   'owner':tb_owner,
                   'resultdist':tb_owner,
                   'config':tb_config}
        tb = Testbed(**testbed)
        tb.save()

    return tb

def convertFromStringToList(my_string):
    return my_string.strip('[]').split(',')



def getTestbedATT(**kwargs):
    tb_name = input_with_default("Your test bed name", "ATT")
    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = kwargs['location'] if kwargs.has_key('localtion') else input_with_default("Testbed location: ", "S3")
        tb_owner = kwargs['owner'] if kwargs.has_key('owner') else input_with_default("Testbed owner: ", "tubn")
        print '\n'
        list_aps= convertFromStringToList(input_with_default("List aps for this testbed", "[192.168.2.1]"))
        dict_aps = {}
        ap_conf_flag = input_with_default("Do you want to use default config ('username': 'super','password':'sp-admin') for these aps?", "y")
        if ap_conf_flag == "y":
            for ap in list_aps:
                ap_conf = {'username': 'super','password':'sp-admin', 'ip_addr' : ap}
                dict_aps[ap] = ap_conf
        else:
            for ap in list_aps:
                username = input_with_default("Username for ap %s" % ap, "super")
                password = input_with_default("Password for this ap", "sp-admin")
                dict_aps[ap] = {'username' : username, 'password' : password, 'ip_addr' : ap}

        print '\n'
        list_ads= convertFromStringToList(input_with_default("List ads for this testbed", "[192.168.2.254]"))

        print '\n'
        list_win_stations = convertFromStringToList(input_with_default("List win stations for this testbed", "[192.168.2.4]"))

        tb_config = {
            'dict_aps' : dict_aps,
            'list_ads' : list_ads,
            'list_win_stations': list_win_stations
        }

        testbed = {'name':tb_name,
                   'tbtype': TestbedType.objects.get(name='AP_ATT'),
                   'location':tb_location,
                   'owner':tb_owner,
                   'resultdist':tb_owner,
                   'config':str(tb_config)}
        tb = Testbed(**testbed)
        tb.save()

    return tb

def getSta_list(tb_config):
    #sta_ip_list = tb_config['win_sta_list'] + tb_config['linux_sta_list']
    sta_ip_list = tb_config['win_sta_list']
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

def getActiveApUpdate(list_aps):
    list_aps_for_print = []
    for i in range(len(list_aps)):
        list_aps_for_print.append("%d - %s" % (i, list_aps[i]))

    print "AP's IP list: "
    print "\n".join(list_aps_for_print)

    list_ap_from_input = raw_input("Pick up APs, seperated by space (enter all for all APs): ").split()
    if list_ap_from_input[0] == 'all':
        result = list_aps
    else:
        result = []
        for ap_id in list_ap_from_input:
            result.append(list_aps[int(ap_id)])
    return result


def getActiveStation(tbcfg):
    ip_list = []
    sta_ip_list = getSta_list(tbcfg)
    for i in range(len(sta_ip_list)):
        ip_list.append("%d - %s" % (i, sta_ip_list[i]))

    print "\nStation IP list:"
    print "\n".join(ip_list)
    list_id = raw_input("Pick up stations behind the Adapter, seperated by space (enter all for All Stations): ").split()
    if list_id[0] == 'all':
        list_local_station = sta_ip_list
    else:
        list_local_station = []
        for id in list_id:
            list_local_station.append(sta_ip_list[int(id)])
    return list_local_station

def get_testsuite(ts_name, description, combotest = False):
    print "\nYou can assign test suite name to same set of test case.\nUse test suite to group your test cases."
    _name = raw_input("Testsuite name: [enter='%s'] " % ts_name)
    if not _name:
        _name = ts_name
    print "Adding TestSuite %s " % ts_name
    try:
        ts = TestSuite.objects.get(name=ts_name)
        print "TestSuite '%s' is already in database." % ts_name
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % ts_name
        if combotest:
            ts = TestSuite(name=_name, description=description, xtype=TestSuite.TS_COMBO)
        else:
            ts = TestSuite(name=_name, description=description)
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
def addTestCase( test_suite, test_name, common_name, test_param, test_order=0, exc_level=0 , is_cleanup=False):
    return insertTestCase( TestCase( suite=test_suite,
                                     test_name='ap.%s' % test_name,
                                     seq=test_order,
                                     test_params= str(test_param),
                                     common_name=common_name,
                                     exc_level=exc_level,
                                     is_cleanup=is_cleanup) )






