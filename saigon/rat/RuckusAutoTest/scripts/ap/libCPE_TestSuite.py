import sys, os, types, copy, re
from django.core.management import setup_environ
os.chdir("../../..")
sys.path.append(os.getcwd())
from RuckusAutoTest.common.Ratutils import *
import settings
setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from RuckusAutoTest.models import *
from RuckusAutoTest.components import *

def input_with_default(prompt, default):
    txt = raw_input('%s (%s): ' % (prompt, default))
    if txt.strip() == '':
        return default
    return txt

def getTestbed(**kwargs):
    tb_info_file = "./RuckusAutoTest/common/CPE_Testbed_Info_Default.inf"
    
    tb_info = load_config_file(tb_info_file)
    tb_name = raw_input("Your test bed name: ")
            
    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = tb_info['location']
        tb_owner = tb_info['owner']

        sta_ip_list  = "'sta_ip_list':%s" % tb_info['sta_ip_list']
        cfg_file_name = "'cfg_file_name':'%s'" % tb_info_file
     
        
        model_ip_dict = "'mf_ip_dict':{"
        for item_key in tb_info.keys():
            if item_key.lower().startswith('mf'):
                model_ip_dict += "'%s':%s," % (item_key, tb_info[item_key])
                
        model_ip_dict+="}"
        
        up_cfg_mf7211 = "'up_cfg_mf7211': %s" % eval(tb_info.get('up_cfg_mf7211'))
        up_cfg_mf2211 = "'up_cfg_mf2211': %s" % eval(tb_info.get('up_cfg_mf2211'))
        
        tb_config = "{%s, %s, %s, %s, %s}" % (sta_ip_list, cfg_file_name, 
                                              model_ip_dict, up_cfg_mf7211, up_cfg_mf2211)

        testbed = {'name':tb_name,
                   'tbtype': TestbedType.objects.get(name='CPE_Stations'),
                   'location':tb_location,
                   'owner':tb_owner,
                   'resultdist':tb_owner,
                   'config':tb_config,
                   }
        tb = Testbed(**testbed)
        tb.save()

    return tb

def convertFromStringToList(my_string):
    return my_string.strip('[]').split(',')

def getSta_list(tb_config):
    #sta_ip_list = tb_config['win_sta_list'] + tb_config['linux_sta_list']
    sta_ip_list = tb_config['win_sta_list']
    return sta_ip_list

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