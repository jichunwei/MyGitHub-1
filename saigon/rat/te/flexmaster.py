"""
This module call ZoneDirector.ZoneDirector and change its NetworkManagement' FlexMaster attribiutes.

Examples:

   tep.py flexmaster url=192.168.0.252 zd_ip_addr="192.168.0.2" enabled=False

   tep.py flexmaster url=192.168.1.101 zd_ip_addr_list="['192.168.2.1','192.168.2.2','192.168.2.3']"

   # for ZD behind termserver or firewall that using port forwarding
   tep.py flexmaster url=192.168.1.101 zd_ip_addr=172.17.18.121:1001
   tep.py flexmaster url=172.17.18.101 zd_ip_addr="['172.17.18.121:1001', '172.17.18.121:1002']"
   tep.py flexmaster url=192.168.1.101 zd_ip_addr=172.17.18.121 zd_ip_port=1001
   tep.py flexmaster url=192.168.1.101 zd_ip_addr=172.17.18.121 zd_ip_port="[1001,1002]"
   tep.py flexmaster url=172.17.18.199 zd_ip_addr=172.17.18.121 zd_ip_port=range(1001,1011)
   tep.py flexmaster url=172.17.18.101 zd_ip_addr=172.17.18.121 zd_ip_port=range(1001,1011) interval=10

"""

#import os
import time
import logging
from pprint import pformat

#import ratenv
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import system_zd as ZSYS
import RuckusAutoTest.common.lib_Debug as bugme


def create_zd(conf):
    logging.info("Starting up ZoneDirector [%s]" % conf['zd_ip_addr'])
    cfg = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(conf)

    sm = SeleniumManager()
    zd = ZoneDirector(cfg)
    zd.start()

    return zd


def make_zd_ip_port_list(zd_ip_list, zd_port_list=[]):
    if not zd_port_list:
        return zd_ip_list

    if type(zd_port_list) is not list:
        zd_port_list = [zd_port_list]

    new_zd_ip_list = []

    for zd_ip in zd_ip_list:
        for zd_port in zd_port_list:
            if type(zd_port) is not str:
                zd_port = str(zd_port)
            new_zd_ip_list.append("%s:%s" % (zd_ip, zd_port))

    return new_zd_ip_list


def do_flexmaster(zd_ip_addr, fm_mgmt, tcfg, tm0=None):
    if not tm0:
        tm0 = time.time()
    tm1 = time.time()
    fm_mgmt2 = {'zd_ip_addr': zd_ip_addr}

    try:
        zd = create_zd(tcfg)
        fm_mgmt2 = ZSYS.set_fm_mgmt_info(zd, fm_mgmt)
        fm_mgmt2['xResult'] = 'PASS'
        zd.stop()

    except Exception:
        import traceback
        print "\n\n%s" % ('!' * 68)
        ex =  traceback.format_exc()
        print ex
        fm_mgmt2['xResult'] = 'FAIL'

    tm2 = time.time()
    fm_mgmt2['runtime.sec'] = int(tm2 - tm1)
    fm_mgmt2['totalexe.sec'] = int(tm2 - tm0)

    return fm_mgmt2


def main(**kwargs):
    tm0 = time.time()
    tcfg = dict(
        debug=False,
        zd_ip_addr='192.168.0.2',
        zd_ip_port='',
        x_loadtime=2.1,
        username='admin',
        password='admin'
    )



    tcfg.update({'enabled':True, 'url':None, 'interval':0})
    tcfg.update(kwargs)

    if tcfg['debug']:
        logging.info("[initConfig ZD.FlexMaster]: %s" % pformat(tcfg, 4, 120))

    if tcfg['enabled'] and not tcfg['url']:
        raise Exception("ZD.FlexMaster arg 'url' is required when eanbling it." )

    fm_mgmt = dict(enabled=tcfg['enabled'], url=tcfg['url'])

    if tcfg['interval']:
        fm_mgmt['interval'] = tcfg['interval']

    if tcfg.has_key('zd_ip_addr_list'):
        zd_ip_addr_list = tcfg['zd_ip_addr_list']

    else:
        zd_ip_addr_list = tcfg['zd_ip_addr']
        if type(zd_ip_addr_list) is str:
            zd_ip_addr_list = [zd_ip_addr_list]
        # old schema return list of <zd_ipaddr>:<port>
        zd_ip_addr_list = make_zd_ip_port_list(zd_ip_addr_list, tcfg['zd_ip_port'])

    RunResults = {'PASS': {}, 'FAIL': {}}

    run_count = 0
    for zd_ip_addr in zd_ip_addr_list:
        run_count += 1
        bugme.do_trace("TRACE_TE_FM")
        fm_mgmt_2 = do_flexmaster(zd_ip_addr, fm_mgmt, tcfg, tm0)
        logging.info("[TestResult.flexmaster #%d] for [ZD %s]:\n%s" % (run_count, zd_ip_addr, pformat(fm_mgmt_2, 4, 120)))
        RunResults[fm_mgmt_2['xResult']][zd_ip_addr] = fm_mgmt_2

    if len(RunResults['FAIL']) > 0:
        logging.info('There are %d failures; redo them' % len(RunResults['FAIL']))
        for zd_ip_addr in RunResults['FAIL'].keys():
            run_count += 1
            bugme.do_trace("TRACE_TE_FM")
            logging.info('[ReExecute setFlexMasterAttr] [ip_addr %s] ' % zd_ip_addr)
            fm_mgmt_2 = do_flexmaster(zd_ip_addr, fm_mgmt, tcfg, tm0)
            if fm_mgmt_2['xResult'] == 'PASS':
                del(RunResults['FAIL'][zd_ip_addr])
            else:
                RunResults[fm_mgmt_2['xResult']][zd_ip_addr] = fm_mgmt_2
            logging.info("[TestResult.flexmaster #%d] for [ZD %s]:\n%s" % (run_count, zd_ip_addr, pformat(fm_mgmt_2, 4, 120)))

    if len(RunResults['FAIL']) > 0:
        return ('FAIL', RunResults['FAIL'].keys())

    return ('PASS', RunResults['PASS'].keys())

