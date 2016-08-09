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
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import lib_Constant as const

def create_zd_webui(zdcfg):
    '''
    Create ZoneDirecotr webui.
    '''
    cfg = dict(
        ip_addr = '2020:db8:1::2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(zdcfg)
    
    #sm = cfg['selenium_mgr'] = SeleniumManager()
    zd = ZoneDirector(cfg)
    zd.start()
    
    return zd
    
def close_zd_webui(zd):
    '''
    Close ZoneDirecotr webui.
    '''
    zd.stop()
    zd.selenium_mgr.shutdown()

def get_zd_ap_as_dict(zd):
    '''
    Get all ap information via zd webui.
    '''
    ap_sym_dict = zd.get_all_ap_sym_dict()

    return ap_sym_dict

def get_testbed_config(tbi):
    '''
    return testbed instance's config in dictionary form
    '''
    tbi_config = tbi.config.replace('\n' , '').replace('\r', '')
    tbconfig = eval(tbi_config)
    return tbconfig


def get_zd_ip_cfg(tbcfg):
    '''
    Return ZD IP configuration in dictionary form.
    '''
    zd_ip_cfg = tbcfg['ip_cfg']['zd_ip_cfg']
    
    return zd_ip_cfg

def get_zd_ip_version(tbcfg):
    '''
    Return ZD IP version.
    '''
    zd_ip_version = get_zd_ip_cfg(tbcfg)['ip_version']
    
    return zd_ip_version
    

def get_ap_ip_cfg(tbcfg):
    '''
    Return AP IP configuration in dictionary form.
    '''
    ap_ip_cfg = tbcfg['ip_cfg']['ap_ip_cfg']
    
    return ap_ip_cfg

def get_ap_ip_version(tbcfg):
    '''
    Return AP IP version.
    '''
    ap_ip_version = get_ap_ip_cfg(tbcfg)['ip_version']
    
    return ap_ip_version

def get_ipv4_net_mask(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    
    if zd_ip_cfg.has_key(const.IPV4):
        netmask = zd_ip_cfg[const.IPV4]['netmask']
    else:
        netmask = '255.255.255.0'
    
    return netmask

def get_ipv6_gateway(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    
    if zd_ip_cfg.has_key(const.IPV6):
        gateway = zd_ip_cfg[const.IPV6]['ipv6_gateway']
    #else:
    #    netmask = '2020:db8:128::253'
    return gateway

def get_ipv4_gateway(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    if zd_ip_cfg.has_key(const.IPV4):
        gateway = zd_ip_cfg[const.IPV4]['gateway']
    return gateway

def get_ipv6_pri_dns(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    
    if zd_ip_cfg.has_key(const.IPV6):
        dns = zd_ip_cfg[const.IPV6]['ipv6_pri_dns']
    return dns

def get_ipv4_pri_dns(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    
    if zd_ip_cfg.has_key(const.IPV4):
        pri_dns = zd_ip_cfg[const.IPV4]['pri_dns']
    else:
        pri_dns = '192.168.0.252'
    return pri_dns

def get_ipv6_prefix_len(tbcfg):
    zd_ip_cfg = get_zd_ip_cfg(tbcfg)
    
    if zd_ip_cfg.has_key(const.IPV6):
        prefix_len = zd_ip_cfg[const.IPV6]['ipv6_prefix_len']
    else:
        prefix_len = '64'

    return prefix_len

def get_sta_ip_list(tbcfg):
    return tbcfg['sta_ip_list']

def get_ap_sym_dict(tbcfg):
    return tbcfg['ap_sym_dict']

def get_ap_mac_list(tbcfg):
    return tbcfg['ap_mac_list']

def get_zd_ipv6_addr(tbcfg):
    return tbcfg['ZD']['ip_addr']

def get_zd_ipv4_addr(tbcfg):
    return tbcfg['ZD']['ipv4_addr']    

def get_switch_ip_addr(tbcfg):
    if tbcfg.has_key('L3Switch'):
        switch_ip_addr = tbcfg['L3Switch']['ip_addr']
    else:
        switch_ip_addr = '192.168.0.253'
        
    return switch_ip_addr
    
def get_server_ip(tbcfg):
    '''
    Get linux server ip - ipv4.
    '''
    try:
        ip = tbcfg['server']['ip_addr']
    except:
        ip = '192.168.0.252'
    return ip

def get_server_ipv6(tbcfg):
    '''
    Get linux server ip - ipv6.
    '''
    try:
        ip = tbcfg['ipv6_server']['ip_addr']
    except:
        ip = '2020:db8:1::251'
    return ip

def show_ap_sym_list(ap_sym_dict):
    '''
    Show ap model list for the user to select.
    '''
    print ""
    for k in sorted(ap_sym_dict.keys()):
        print "%s : mac=%s; model=%s; status=%s" % (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['model'], ap_sym_dict[k]['status'])

def get_ap_model_list(ap_list):
    '''
    Get AP model list.
    '''
    model_list = []
    for ap in ap_list:
        if ap['model'] not in model_list:
            model_list.append(ap['model'])

    return sorted(model_list)

def get_ap_sym_model_dict(ap_sym_dict):
    '''
    Get ap sym model dict.
    '''
    models = {}
    for apid, apinfo in ap_sym_dict.items():
        aModel = apinfo['model']
        if models.has_key(aModel):
            models[aModel].append(apid)
        else:
            models[aModel] = [apid]
    return models

def show_ap_sym_list_by_model(ap_sym_dict, models = None):
    '''
    Show ap sym list by model.
    '''
    if not models:
        models = get_ap_sym_model_dict(ap_sym_dict)
    for aModel in sorted(models.keys()):
        print "AP model %s" % aModel
        for k in models[aModel]:
            print "   %s : mac=%s; status=%s" % (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['status'])

def get_ap_sym_list_by_model(ap_sym_dict, models = None):
    '''
    Get ap sym list by model.
    '''
    if not models:
        models = get_ap_sym_model_dict(ap_sym_dict)
    aplist = []
    for aModel in sorted(models.keys()):
        for k in models[aModel]:
            aplist.append(k)
    return aplist

def get_active_ap(ap_sym_dict):
    '''
    Get active ap.
    '''
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic APs from above list, separated by space (enter all for all APs): """
    while (True):
        show_ap_sym_list(ap_sym_dict)
        active_ap_list = raw_input(select_tips).split()
        if not active_ap_list: continue
        if re.match(r'^all$', active_ap_list[0], re.M):
            return sorted(ap_sym_dict.keys())
        if _list_in_dict(active_ap_list, ap_sym_dict):
            return active_ap_list

def get_active_ap_by_model(ap_sym_dict, interactive_mode = False):
    '''
    return requested sym AP in list of pair. Example output:
      [(AP_02, AP_01), (AP_05, AP_06)]
    '''
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic APs from above list, separated by space (enter all for all APs): """
    models = get_ap_sym_model_dict(ap_sym_dict)
    if interactive_mode:        
        while (True):
            show_ap_sym_list_by_model(ap_sym_dict, models)
            active_ap_list = raw_input(select_tips).split()
            if not active_ap_list: continue
            if re.match(r'^all$', active_ap_list[0], re.M):
                return _list_as_pair(get_ap_sym_list_by_model(ap_sym_dict, models))
            if _list_in_dict(active_ap_list, ap_sym_dict):
                return _list_as_pair(active_ap_list)
    else:
        return _list_as_pair(get_ap_sym_list_by_model(ap_sym_dict, models))

def get_target_station(sta_ip_list, message = ""):
    '''
    Get target station list.
    '''
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
    '''
    Get target station radio mode.
    '''
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

def get_testsuite(ts_name, description, interactive_mode = False, combotest = False):
    '''
    Get test suite and adding test cases.
    '''
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

#
# Deal with TestCase record creating
#
_tc_info = "%4s   testsuite: [%s]\n       test_name: [%s]\n     common_name: [%s]"
# called testTestCase() is prefered then insertTestCase()
def add_test_case(test_suite, test_name, common_name, test_param, test_order = 0, exc_level = 0 , is_cleanup = False, is_update = True):
    '''
    Add test cases.
    '''
    cfg = dict(suite = test_suite,
               test_name = 'zd.%s' % test_name,
               seq = test_order,
               test_params = str(test_param),
               common_name = common_name,
               exc_level = exc_level,
               is_cleanup = is_cleanup)
    if is_update:
        return _update_test_case(cfg)
    else:
        return _add_test_case(cfg)      

def is_test_case_eq(tc1, tc2):
    '''
    Is two test case equal.
    '''
    if tc1.suite != tc2.suite: return 1
    if tc1.test_name != tc2.test_name: return 2
    if tc1.common_name != tc2.common_name: return 3
    if tc1.test_params != tc2.test_params: return 4
    return 0

def _update_test_case(config):
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

def _add_test_case(config):
    '''
    Add test cases.
    '''
    tc = TestCase(**config)
    tc.save()
    result = tc.id
    print _tc_info % ('ADD', config['suite'], config['test_name'], config['common_name'])
    return result   

#
# tb7 = getTestbed(zd_ip_addr='2020:db8:1::2', ApUseSym=True)
#
# Default values defined here:
#
#    zd_ip_addr=2020:db8:1::2, svr_ip_addr=2020:db8:1::251, tbtype=ZD_Stations_IPV6
#    L3Switch->ip_addr=192.168.0.253
#    and zd_conf and srv_conf
#
def get_test_bed(**kwargs):
    atrs = {'L3Switch': { 'ip_addr': '192.168.0.253', 'username': 'admin', 'password': '', 'enable_password': ''},
            'ApUseSym': True,
            'zd_ip_addr':'2020:db8:1::2','zd_ipv4_addr': '192.168.0.2',
            'svr_ip_addr':'192.168.0.252', 'svr_ipv6_addr': '2020:db8:1::251',             
            'tbtype':'ZD_Stations_IPV6','zd_username':'admin', 'zd_password':'admin', 'shell_key': '',
            }
    
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
                    
        #Select ZD and AP IP version.  
        ip_version_list = [const.DUAL_STACK, const.IPV6]
    
        zd_ip_version = _get_selected_input(ip_version_list, 'Please select ZD IP version[Default is %s]' % const.DUAL_STACK)
        if not zd_ip_version:
            zd_ip_version = const.DUAL_STACK
            
        ap_ip_version = _get_selected_input(ip_version_list, 'Please select AP IP version[Default is %s]' % const.DUAL_STACK)
        if not ap_ip_version:
            ap_ip_version = const.DUAL_STACK
            
        zd_ipv4_addr = atrs['zd_ipv4_addr']
        zd_ipv6_addr = atrs['zd_ip_addr']
        
        switch_ip_addr = atrs['L3Switch']['ip_addr']
        gateway_ip_addr = atrs['svr_ip_addr']
        netmask = '255.255.255.0'
        
        gateway_ipv6_addr = atrs['svr_ipv6_addr']
        prefix_len = '64'
            
        zd_ip_cfg = _define_zd_ip_cfg(zd_ipv4_addr, zd_ipv6_addr, zd_ip_version, gateway_ip_addr, netmask, gateway_ipv6_addr, prefix_len, switch_ip_addr)
        ap_ip_cfg = _define_ap_ip_cfg(ap_ip_version)
        
        print("Create and start ZD Web UI component")
        
        zd_cfg = {'ip_addr': atrs['zd_ip_addr'],'username': atrs['zd_username'],'password': atrs['zd_password']}
        zd = create_zd_webui(zd_cfg)
        
        #Get all ap information.
        print("Get all active AP information via ZD GUI")
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            ap_sym_dict = get_zd_ap_as_dict(zd)
            ap_mac_list = [ x['mac'] for x in ap_sym_dict.values() ]
        else:
            ap_mac_list = atrs['ap_mac_list'] if atrs.has_key('ap_mac_list') \
                          else raw_input("AP MAC address list (separated by spaces): ").split()
                          
        print("Close ZD Web UI")
        close_zd_webui(zd)
        
        print("Generated testbed configuration")
        zd_conf = _get_atr_val('zd_conf', atrs, {'browser_type':'firefox',
                                                 'ip_addr': atrs['zd_ip_addr'],
                                                 'ipv4_addr': atrs['zd_ipv4_addr'],
                                                 'username': atrs['zd_username'],
                                                 'password': atrs['zd_password'],
                                                 'shell_key': atrs['shell_key'],}
                               )
        
        ip_cfg = _get_atr_val('ip_cfg', atrs, {'zd_ip_cfg': zd_ip_cfg, 
                                               'ap_ip_cfg': ap_ip_cfg,
                                               }
                              )

        shell_key = zd_conf['shell_key'] if zd_conf.has_key('shell_key') else raw_input("shell key:(!v54!)")
        if shell_key is None or shell_key is '':
            shell_key = '!v54!'
        zd_conf['shell_key'] = shell_key

        sta_conf = _get_atr_val('sta_conf', atrs, {})
        srv_conf = _get_atr_val('srv_conf', atrs, {'ip_addr': atrs['svr_ip_addr'], 
                                                   'user': 'lab', 
                                                   'password': 'lab4man1', 
                                                   'root_password': 'lab4man1',
                                                   }
                                )
        
        ipv6_srv_conf = _get_atr_val('srv_conf', atrs, {'ip_addr': atrs['svr_ipv6_addr'],
                                                        'user': 'lab',
                                                        'password': 'lab4man1',
                                                        'root_password': 'lab4man1',
                                                        }
                                     )

        tb_config = {"ZD": zd_conf,
                     "ip_cfg": ip_cfg, 
                     "sta_conf": sta_conf, 
                     "server": srv_conf, 
                     "ipv6_server": ipv6_srv_conf, 
                     "ap_mac_list": ap_mac_list, 
                     "sta_ip_list": sta_ip_list
                    }
        
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            tb_config['ap_sym_dict'] = ap_sym_dict

        if atrs.has_key('L3Switch'):
            tb_config['L3Switch'] = atrs['L3Switch']

        m = re.match(r'^([^@]+)@(|[^\s]+)', tb_owner)
        if not m:
            tb_owner = tb_owner + '@ruckuswireless.com'
        elif len(m.group(2)) < 1:
            tb_owner = m.group(1) + '@ruckuswireless.com'

        testbed = {'name':tb_name, 
                   'tbtype': TestbedType.objects.get(name = atrs['tbtype']), 'location':tb_location, 
                   'owner':tb_owner, 
                   'resultdist':tb_owner, 
                   'config':str(tb_config)
                  }

        tb = Testbed(**testbed)
        tb.save()
    return tb

def _define_zd_ip_cfg(zd_ipv4_addr, zd_ipv6_addr, zd_ip_version, server_ip_addr, netmask, server_ipv6_addr, prefix_len, switch_ip_addr):
    zd_ip_cfg = {'ip_version': zd_ip_version}
    zd_ip_cfg[const.IPV4] = {'ip_alloc': 'dhcp',
                             'ip_addr': zd_ipv4_addr,
                             'netmask': netmask,
                             'gateway': switch_ip_addr,
                             'pri_dns': server_ip_addr,
                             #'sec_dns': '',
                             }
    zd_ip_cfg[const.IPV6] ={'ipv6_alloc': 'manual', #auto, dhcp, as-is.
                            'ipv6_addr': zd_ipv6_addr,
                            'ipv6_prefix_len': prefix_len,
                            'ipv6_gateway': server_ipv6_addr,
                            'ipv6_pri_dns': server_ipv6_addr,
                            #'ipv6_sec_dns': '',
                            }
    return zd_ip_cfg
    
    
def _define_ap_ip_cfg(ap_ip_version):
    ap_ip_cfg = {'ip_version': ap_ip_version}
    ap_ip_cfg[const.IPV4] = {'ip_mode': 'dhcp'}
    ap_ip_cfg[const.IPV6] = {'ipv6_mode': 'auto'}
    
    return ap_ip_cfg

def _get_selected_input(depot = [], prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    id = raw_input(prompt)
    try:
        selection = depot[int(id)]
    except:
        selection = ""

    return selection

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

def _get_atr_val(name, atrs, default):
    val = atrs[name] if atrs.has_key(name) else default
    return val


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
        get_test_bed(**_dict)
        exit(0)