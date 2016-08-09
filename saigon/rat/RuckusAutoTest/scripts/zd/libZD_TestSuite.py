import os
import sys
import re

debug_tslib = True if os.environ.has_key('RAT_DEBUG_TESTSUITE') else False

from django.core.management import setup_environ
rat_path = os.path.realpath(os.path.join(os.getcwd(), "../../.."))
sys.path.insert(0, rat_path)

import settings
setup_environ(settings)

if debug_tslib:
    pfmt = "%12s: %s"
    print "\ntslib.py Runtime environment:\n"
    print pfmt % ('RUN DIR', os.getcwd())
    print pfmt % ('DATABASE', settings.DATABASE_NAME)
    print pfmt % ('TSLIB', __file__)

from django.core.exceptions import ObjectDoesNotExist

from RuckusAutoTest.models import Testbed, TestbedType, TestCase, TestSuite, TestRun
from RuckusAutoTest.testbeds import * # 'testbeds' is a package, so it should be 'import *'
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import lib_Constant as const

def getZoneDirectorAPsDict(zdcfg):
    cfg = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(zdcfg)

    sm = cfg['selenium_mgr'] = SeleniumManager()
    zd = ZoneDirector(cfg)
    zd.start()

    ap_sym_dict = zd.get_all_ap_sym_dict()

    sm.shutdown()

    return ap_sym_dict


def showApSymList(ap_sym_dict):
    print ""
    for k in sorted(ap_sym_dict.keys()):
        print "%s : mac=%s; model=%s; status=%s" % (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['model'], ap_sym_dict[k]['status'])

# This function is moved from addtestsuite_ZD_Mesh_Configuration.py
# return AP models from testbed's ap_sym_dict
# Example:
#   get_ap_modelList(ap_sym_dict.itervalues())
def get_ap_modelList(ap_list):
    model_list = []
    for ap in ap_list:
        if ap['model'] not in model_list:
            model_list.append(ap['model'])

    return sorted(model_list)

def getApSymModelDict(ap_sym_dict):
    models = {}
    for apid, apinfo in ap_sym_dict.items():
        aModel = apinfo['model']
        if models.has_key(aModel):
            models[aModel].append(apid)
        else:
            models[aModel] = [apid]
    return models

# Example:
#
#   showApSymListByModel(tbcfg['ap_sym_dict'])
#
def showApSymListByModel(ap_sym_dict, models = None):
    if not models:
        models = getApSymModelDict(ap_sym_dict)
    for aModel in sorted(models.keys()):
        print "AP model %s" % aModel
        for k in models[aModel]:
            print "   %s : mac=%s; status=%s" % (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['status'])

def getApSymListByModel(ap_sym_dict, models = None):
    if not models:
        models = getApSymModelDict(ap_sym_dict)
    aplist = []
    for aModel in sorted(models.keys()):
        for k in models[aModel]:
            aplist.append(k)
    return aplist

def getTargetStation(sta_ip_list, message = ""):
    ip_list = []
    for i in range(len(sta_ip_list)):
        ip_list.append("  %d - %s" % (i, sta_ip_list[i]))
    print "Station IP list:"
    print ";".join(ip_list)
    if not message:
        message = "Pick an IP in the list above: "
    id = raw_input(message)
    try:
        target_sta = sta_ip_list[int(id)]
    except:
        target_sta = ""
    return target_sta

def get_target_sta_radio(message = ""):
    radio_list = [radio for radio, id in const._radio_id.items()]
    sta_radio_list = []
    for i in range(len(radio_list)):
        sta_radio_list.append("  %d - %s\n" % (i, radio_list[i]))
    print "Station Radio list:"
    print "".join(sta_radio_list)
    if not message:
        message = "Pick an radio in the list above for target station: "
    id = raw_input(message)
    try:
        sta_radio = radio_list[int(id)]
    except:
        sta_radio = ""
    return sta_radio


def getActiveAp(ap_sym_dict):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic APs from above list, separated by space (enter all for all APs): """
    while (True):
        showApSymList(ap_sym_dict)
        active_ap_list = raw_input(select_tips).split()
        if not active_ap_list: continue
        if re.match(r'^all$', active_ap_list[0], re.M):
            return sorted(ap_sym_dict.keys())
        if _list_in_dict(active_ap_list, ap_sym_dict):
            return active_ap_list

# return requested sym AP in list of pair. Example output:
#
#       [(AP_02, AP_01), (AP_05, AP_06)]
#
def getActiveApByModel(ap_sym_dict, interactive_mode = False):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic APs from above list, separated by space (enter all for all APs): """
    models = getApSymModelDict(ap_sym_dict)
    if interactive_mode:        
        while (True):
            showApSymListByModel(ap_sym_dict, models)
            active_ap_list = raw_input(select_tips).split()
            if not active_ap_list: continue
            if re.match(r'^all$', active_ap_list[0], re.M):
                return _list_as_pair(getApSymListByModel(ap_sym_dict, models))
            if _list_in_dict(active_ap_list, ap_sym_dict):
                return _list_as_pair(active_ap_list)
    else:
        return _list_as_pair(getApSymListByModel(ap_sym_dict, models))

def _list_in_dict(_list, _dict):
    for _l in _list:
        if not _dict.has_key(_l):
            return False
    return True

def _list_as_pair(_list):
    x = 0
    y = x + 1
    list_of_pair = []
    while y < len(_list):
        list_of_pair.append((_list[x], _list[y]))
        x = y + 1
        y = x + 1
    return list_of_pair

# return a string with 2 words, the first one is the AP model in lower case,
# the 2nd one is either ROOT or MESH or AP [Tikona project: neither rootAP nor meshAP]
def getApTargetType(active_ap, apcfg, interactive_mode = False,ap_tag = False):
    mfmt = '\nactive_ap(%s): model: %s; mac: %s; status: %s; is (rootAP | meshAP | AP)? '
    msg = mfmt % (active_ap, apcfg['model'], apcfg['mac'], apcfg['status'])
    if ap_tag:
        ap_model = active_ap#@author:yuyanan @since:2014-8-6 zf-9348 ap_tag substitute for ap_model
    else:
        ap_model = apcfg['model'].lower()
    ap_status = apcfg['status']
    if interactive_mode:
        while True:
            what = raw_input(msg).lower()
            if re.match(r'^(r|0)', what):
                return '%s ROOT' % ap_model
            elif re.match(r'^(m|1)', what):
                return '%s MESH' % ap_model
            elif re.match(r'^(a|2)', what):
                return '%s AP' % ap_model
            elif re.match(r'^(q|x)', what):
                raise 'User abort adding test case'
            elif re.match(r'^(s)', what):
                return ''
            elif len(what) == 0:
                if re.search(r'root', ap_status, re.I):
                    return '%s ROOT' % ap_model
                if re.search(r'mesh', ap_status, re.I):
                    return '%s MESH' % ap_model
                return '%s AP' % ap_model
    else:
        if re.search(r'root', ap_status, re.I):
            return '%s ROOT' % ap_model
        if re.search(r'mesh', ap_status, re.I):
            return '%s MESH' % ap_model
        return '%s AP' % ap_model

def get_testsuite(ts_name, description, interactive_mode = False, combotest = False):
    if interactive_mode:
        print "\nYou can assign test suite name to same set of test case.\nUse test suite to group your test cases."
        _name = raw_input("Testsuite name: [enter='%s'] " % ts_name)
    else:
        print "Testsuite name: %s" % ts_name
        _name = ts_name
    if not _name:
        _name = ts_name
    print "Adding TestSuite %s " % _name
    try:
        ts = TestSuite.objects.get(name = _name)
        print "TestSuite '%s' is already in database." % _name
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % _name
        if combotest:
            ts = TestSuite(name = _name, description = description, xtype = TestSuite.TS_COMBO)
        else:
            ts = TestSuite(name = _name, description = description)
        ts.save()
    print "Adding test cases to TestSuite %s " % ts.name
    return ts

def _getAtrVal(name, atrs, default):
    val = atrs[name] if atrs.has_key(name) else default
    return val

#
# Deal with TestCase record creating
#
_tc_info = "%4s   testsuite: [%s]\n       test_name: [%s]\n     common_name: [%s]"
def insertTestCase(testcase, unique = True):
    if unique:
        tclist = TestCase.objects.filter(suite = testcase.suite
                                        , test_name = testcase.test_name
                                        , common_name = testcase.common_name
                                        )
                                        # test_params=testcase.test_params
        if len(tclist) > 0:
            print _tc_info % ('SKIP', testcase.suite, testcase.test_name, testcase.common_name)
            return (-1 * tclist[0].id)
    print _tc_info % ('ADD', testcase.suite, testcase.test_name, testcase.common_name)
    testcase.save()
    return testcase.id

def update_test_case(config):
    '''
    . updating the testcase and its generated testruns if the testcase is exist
    . otherwise, just add it in
    '''
    result = -1
    try:
        tclist = TestCase.objects.filter(suite = config['suite']
                                     , test_name = config['test_name']
                                     , common_name = config['common_name'])
        if len(tclist) > 0:            
            for tc in tclist:                 
                tc.test_params = config['test_params']
                tc.save()
                print _tc_info % ('UPDATE', tc.suite, tc.test_name, tc.common_name)
                result = tc.id
        else:
            tc = TestCase(**config)
            tc.save()
            result = tc.id
            print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])            
                
    except ObjectDoesNotExist:
        tc = TestCase(**config)
        tc.save()
        result = tc.id
        print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])

    trs = TestRun.objects.filter(suite = config['suite'])
    if trs:
        for tr in trs:
            if tr.common_name == config['common_name']:  
                tr.test_params = config['test_params']
                tr.save()
                print _tc_info % ('UPDATE', tr.suite, tr.test_name, tr.common_name)
                result = tr.id
    return result


def add_test_case(config):
    tc = TestCase(**config)
    tc.save()
    result = tc.id
    print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])
    return result    

# called testTestCase() is prefered then insertTestCase()
def addTestCase(test_suite, test_name, common_name, test_param, test_order = 0, exc_level = 0 , is_cleanup = False, is_update = True):
    cfg = dict(suite = test_suite,
               test_name = 'zd.%s' % test_name,
               seq = test_order,
               test_params = str(test_param),
               common_name = common_name,
               exc_level = exc_level,
               is_cleanup = is_cleanup)
    if is_update:
        return update_test_case(cfg)
    else:
        return add_test_case(cfg)      


def delTestCasesByTestSuite(test_suite):    
    try:
        tc_list = TestCase.objects.filter(suite=test_suite)
        if len(tc_list) > 1:
            for tc in tc_list:
                tc.delete()
                print 'delete test case [%s] against test suite [%s]' % (tc.test_name, test_suite.name)
    except ObjectDoesNotExist:
        raise

def isTestCaseEq(tc1, tc2):
    if tc1.suite != tc2.suite: return 1
    if tc1.test_name != tc2.test_name: return 2
    if tc1.common_name != tc2.common_name: return 3
    if tc1.test_params != tc2.test_params: return 4
    return 0

# avoid hardcode, call this method to get Linux Server IP address
def getTestbedServerIp(tbcfg):
    try:
        ip = tbcfg['server']['ip_addr']
    except:
        ip = '192.168.0.252'
    return ip

#
# tb7 = getTestbed(zd_ip_addr='192.168.0.7', ApUseSym=True)
# tb8 = getMeshTestbed(L3Switch={'ip_addr':'192.168.0.243'}}
# # mesh_layout = [['AP_01', ['AP_02']], ['AP_03', ['AP_04']], ['AP_05', ['AP_06', 'AP_07]]]
# # rootAP are AP_01, AP_03, and AP_05
# tb9 = getMeshTestbed(Mesh={'enable': True, 'name':'mesh-fanout', 'layout': mesh_layout})
# tbB = getMeshTestbed(name='mesh d4', owner='mesh4', sta_ip_list=['192.168.1.11', '192.168.1.12',])
# tbC = getMeshTestbed(name='mesh', sta_ip_list=['192.168.1.11'])
#
# Default values defined here:
#
#    zd_ip_addr=192.168.0.2, svr_ip_addr=192.168.0.252, tbtype=ZD_Stations
#    L3Switch->ip_addr=192.168.0.253
#    and zd_conf and srv_conf
#

def getTestbedSwitchIp(tbcfg):
    try:
        ip = tbcfg['L3Switch']['ip_addr']
    except:
        ip = '192.168.0.253'
    return ip

def getTestbed(**kwargs):
    atrs = {'zd_ip_addr':'192.168.0.2', 'svr_ip_addr':'192.168.0.252', 'tbtype':'ZD_Stations',
            'zd_username':'admin', 'zd_password':'admin', 'shell_key': ''}
    atrs.update(kwargs)
    tb_name = atrs['name'] if atrs.has_key('name') \
              else raw_input("Your test bed name: ")

    try:
        tb = Testbed.objects.get(name = tb_name)
    except ObjectDoesNotExist:
        tb_location = atrs['location'] if atrs.has_key('location') \
                      else raw_input("Testbed location: ")
        tb_owner = atrs['owner'] if atrs.has_key('owner') else raw_input("Testbed owner: ")
        sta_ip_list = atrs['sta_ip_list'] if atrs.has_key('sta_ip_list') \
                      else raw_input("Station IP address list (separated by spaces): ").split()
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            ap_sym_dict = getZoneDirectorAPsDict({'ip_addr': atrs['zd_ip_addr'],
                                                  'username': atrs['zd_username'],
                                                  'password': atrs['zd_password']})
            ap_mac_list = [ x['mac'] for x in ap_sym_dict.values() ]
        else:
            ap_mac_list = atrs['ap_mac_list'] if atrs.has_key('ap_mac_list') \
                          else raw_input("AP MAC address list (separated by spaces): ").split()

        zd_conf = _getAtrVal('zd_conf', atrs,
                  { 'browser_type':'firefox'
                  , 'ip_addr': atrs['zd_ip_addr']
                  , 'username': atrs['zd_username']
                  , 'password': atrs['zd_password']
                  , 'shell_key': atrs['shell_key']
                  })

        shell_key = zd_conf['shell_key'] if zd_conf.has_key('shell_key') else raw_input("shell key:(!v54!)")
        if shell_key is None or shell_key is '':
            shell_key = '!v54!'
        zd_conf['shell_key'] = shell_key

        sta_conf = _getAtrVal('sta_conf', atrs, {})
        srv_conf = _getAtrVal('srv_conf', atrs,
                   { 'ip_addr': atrs['svr_ip_addr']
                   , 'user': 'lab'
                   , 'password': 'lab4man1'
                   , 'root_password': 'lab4man1'
                   })

        tb_config = { "ZD": zd_conf
                    , "sta_conf": sta_conf
                    , "server": srv_conf
                    , "ap_mac_list": ap_mac_list
                    , "sta_ip_list": sta_ip_list
                    }
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            tb_config['ap_sym_dict'] = ap_sym_dict

        if atrs.has_key('L3Switch'):
            if not atrs['L3Switch']:
                atrs['L3Switch'] = { 'ip_addr': '192.168.0.253'
                                   , 'username': 'admin'
                                   , 'password': ''
                                   , 'enable_password': ''
                                   }
            tb_config['L3Switch'] = atrs['L3Switch']

        # ATTN: case sense for keywords
        for opt_key in ['Mesh', 'APConnMode', 'RoutingVLANs']:
            if atrs.has_key(opt_key):
                tb_config[opt_key] = atrs[opt_key]

        m = re.match(r'^([^@]+)@(|[^\s]+)', tb_owner)
        if not m:
            tb_owner = tb_owner + '@ruckuswireless.com'
        elif len(m.group(2)) < 1:
            tb_owner = m.group(1) + '@ruckuswireless.com'

        # Only ask the user for info to initiate testbed into
        # a mesh topology at the time of creating testbed.
        testbedInitToMesh(tb_config)

        testbed = { 'name':tb_name
                  , 'tbtype': TestbedType.objects.get(name = atrs['tbtype'])
                  , 'location':tb_location
                  , 'owner':tb_owner
                  , 'resultdist':tb_owner
                  , 'config':str(tb_config)
                  }

        tb = Testbed(**testbed)
        tb.save()
    return tb

def testbedInitToMesh(tb_cfg):
    if tb_cfg.has_key("Mesh"): return True
    enable_mesh = raw_input("Do you want to ZD_Station to configure mesh at starting up(y/n)?: ").lower() == "y"
    if enable_mesh:
        ap_sym_dict = tb_cfg['ap_sym_dict']
        tb_cfg['Mesh'] = {'enable': True}
        showApSymList(ap_sym_dict)
        layout = []
        for ap_sym_name in sorted(ap_sym_dict.keys()):
            role = raw_input("Enter a mesh role for %s (root|mesh): " % ap_sym_name).lower()
            if role == "root":
                layout.append((ap_sym_name,))
            elif role == "mesh":
                uplink_list = raw_input("Enter list of uplink APs (separated by spaces): ").split()
                layout.append((ap_sym_name, uplink_list,))
        tb_cfg['Mesh']['layout'] = layout

# return testbed instance's config in dictionary form
def getTestbedConfig(tbi):
    tbi_config = tbi.config.replace('\n' , '').replace('\r', '')
    tbconfig = eval(tbi_config)
    return tbconfig

def getTestbed2(**kwargs):
    atrs = {"ApUseSym": True}
    atrs.update(kwargs)
    return getTestbed(**atrs)

# if testbed already created, don't ask user for info to initiate ZD_Stations into mesh or not
def getMeshTestbed(**kwargs):
    atrs = {'L3Switch': {}, 'ApUseSym': True}
    atrs.update(kwargs)
    mtb = getTestbed(**atrs)
    return mtb

# add other type of testbed here
def get_fm_testbed(**kwargs):
    pass

def getApByRole(role, ap_sym_dict):
    """
    Return a generator that give the sympolic name of an AP of the given role when next() method gets called.
    If the last AP of that role is returned, the generator loops back to the first one and so on.
    """
    ap_list = sorted(ap_sym_dict.keys())
    ap_role_list = []
    for ap in ap_list:
        if role == "root" and re.search('root', ap_sym_dict[ap]['status'], re.I):
            ap_role_list.append(ap)
        elif role == "mesh" and re.search('mesh ap, 1 hop', ap_sym_dict[ap]['status'], re.I):
            ap_role_list.append(ap)
    l = len(ap_role_list)
    if not l: raise StopIteration
    i = 0
    while True:
        if i == l: i = 0
        yield ap_role_list[i]
        i += 1

def getStationSupportRadio(sta_support_radio_list, station_ip, message = ""):
    radio_list = []
    for i in range(len(sta_support_radio_list)):
        radio_list.append("  %d - %s\n" % (i, sta_support_radio_list[i]))
    print "Station Support Radio list:"
    print "".join(radio_list)
    if not message:
        message = "Pick an radio which supported by station[%s] in the list above: " % station_ip
    id = raw_input(message)
    try:
        sta_support_radio = sta_support_radio_list[int(id)]
    except:
        sta_support_radio = ""
    return sta_support_radio


# Usage
def testsuite_usage():
    u = [ ""
    , "This library is to replace all statements, in your addtestsuite_xyz.py program,"
    , "that are to deal with testbed retrival and creation."
    , "Use the 'from TestSuiteLib import *' command, so all objects/attributes in the TestSuiteLib.py"
    , "can be directly referenced by your scripts."
    , "\nExample:\n"
    , "   from TestSuiteLib import *"
    , "   tb = getTestbed()"
    , "   tbcfg = eval(tb.config)"
    , "   tbx = getMeshTestbed(name='mesh-depth-2', ap_mac_list=['00:1d:2e:16:4f:60', '00:1d:2e:0f:9e:88'])"
    , "   tby = getMeshTestbed(name='mesh d4', owner='mesh4', sta_ip_list=['192.168.1.11', '192.168.1.12'])"
    , "   tbz = getMeshTestbed(name='mesh', ApUseSym=1, sta_ip_list=['192.168.1.11'])"
    , "\nCaveat:\n"
    , "    settings.DATABASE_NAME must be in full path name."
    , "    Change DATABASE_NAME=rat.db in setting.py to\n"
    , "        import os"
    , "        DATABASE_NAME = os.path.realpath(os.path.join(os.path.dirname(__file__), 'rat.db'))"
    ]
    for x in u: print x
    print ""


if __name__ == "__main__":
    from RuckusAutoTest.common import lib_KwList as kwlist

    if len(sys.argv) < 2:
        testsuite_usage()
        exit(1)
    else:
        _dict = kwlist.as_dict(sys.argv[1:])
        getMeshTestbed(**_dict)
        exit(0)


