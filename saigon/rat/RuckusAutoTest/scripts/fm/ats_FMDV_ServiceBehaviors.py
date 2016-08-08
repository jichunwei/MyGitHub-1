'''
Device View

4. ZF2925 8.0 Services behavior check

4.1      AP Standalone mode
4.1.1    ACS Available
4.1.1.1  TR069 in AUTO mode
4.1.1.2  TR069 in FlexMaster Only mode
4.1.1.3  TR069 in SNMP Only mode

4.1.2    ACS Unavailable
4.1.2.1  TR069 in AUTO mode
4.1.2.2  TR069 in FlexMaster Only mode
4.1.2.3  TR069 in SNMP Only mode

4.1.3    ACS Available
4.1.3.1  SNMP in AUTO mode
4.1.3.2  SNMP in FlexMaster Only mode
4.1.3.3  SNMP in SNMP Only mode

4.1.4    ACS Unavailable
4.1.4.1  SNMP in AUTO mode
4.1.4.2  SNMP in FlexMaster Only mode
4.1.4.3  SNMP in SNMP Only mode

4.1.5    ACS Available
4.1.5.1  APMGR in AUTO mode
4.1.5.2  APMGR in FlexMaster Only mode
4.1.5.3  APMGR in SNMP Only mode

4.1.6    ACS Unavailable
4.1.6.1  APMGR in AUTO mode
4.1.6.2  APMGR in FlexMaster Only mode
4.1.6.3  APMGR in SNMP Only mode

4.2      Provisioning from FM Device View
'''

import sys
import copy
import re

from libFM_TestSuite import model_map, make_test_suite, select_ap_by_model, \
        get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.common.utils import log


# model_map is in libFM_TestSuite.py
tc_id = ['04.01.01', '04.01.02', '04.01.03', '04.01.04', '04.01.05', '04.01.06',
            '04.02.01', '04.02.02', '04.02.03', ]

def fill_tc_tmpl_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    #log(tc[0])

    tc_cfg = tc[2]
    tc_cfg['prov_from'] = tc_cfg['prov_from'] % cfg
    return tc


def fill_tc_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    log(tc[0])

    tc_cfg = tc[2]
    tc_cfg['ap_ip'] = tc_cfg['ap_ip'] % cfg
    return tc


def init_tc_templates():
    prov_from = [('Provisioning from AP', 'ap'), ('Provisioning from FM Device View', 'fm')]
    acses = ['available', 'unavailable']
    modes = ['Auto', 'FlexMaster', 'SNMP']

    # accessing this by [acs][mode]
    # each item is (precfg, cfg, expected)
    # these are used for both case: fm prov/ap prov
    test_cfg = [
        [ ( dict(remote_mode='fm', inform_interval='1m',),
            dict(remote_mode='auto',),
            dict(tr069=True, snmp=False, apmgr=True), ),

          ( dict(remote_mode='auto', inform_interval='1m',),
            dict(remote_mode='fm',),
            dict(tr069=True, snmp=False, apmgr=True), ),

          ( dict(remote_mode='auto', inform_interval='1m',),
            dict(remote_mode='snmp',),
            dict(tr069=False, snmp=True, apmgr=True), ),
        ],
        # acs unavail: using invalid fm_url
        [ ( dict(remote_mode='fm', inform_interval='1m',),
            dict(remote_mode='auto',
                 fm_url='http://192.168.0.252/intune/server',),
            dict(tr069=True, snmp=True, apmgr=True), ),

          ( dict(remote_mode='auto', inform_interval='1m',),
            dict(remote_mode='fm',
                 fm_url='http://192.168.0.252/intune/server',),
            dict(tr069=True, snmp=False, apmgr=True), ),

          ( dict(remote_mode='auto', inform_interval='1m',),
            dict(remote_mode='snmp',
                 fm_url='http://192.168.0.252/intune/server',),
            dict(tr069=False, snmp=True, apmgr=True), ),
        ],
    ]

    tcid_tmpl = '04.%02d.%02d'
    tc_tmpls = {}

    tmpl = [
        'TCID:%(tcid)s.%(model_id)s - %(prov_from_txt)s: ACS %(acs)s: TR069, SNMP, APMGR in %(mode)s mode - %(model)s',
        'FMDV_ServiceBehaviors',
        dict(
            ap_ip='%(ap_ip)s',
            precfg={},
            cfg={},
            prov_from='%(prov_from)s',
            expected={},
        ),
    ]
    # acs and service -> first number, mode -> second number on tcid_tmpl
    for pf_idx in range(len(prov_from)):
        mode_idx = 1
        pf_txt, pf = prov_from[pf_idx][0], prov_from[pf_idx][1]
        for acs in acses:
            # Prov from Device View and ACS Un-avail: are invalid cases
            if pf_idx == 1 and acses.index(acs) == 1:
                break
            for mode in modes:
                tc = copy.deepcopy(tmpl)
                cfg = dict(
                    tcid=tcid_tmpl % (pf_idx+1, mode_idx),
                    prov_from_txt=pf_txt,
                    prov_from=pf,
                    acs=acs,
                    mode=mode,

                    model='%(model)s',
                    model_id='%(model_id)02d',
                )
                tc = fill_tc_tmpl_cfg(tc, cfg)
                tc_cfg = tc[2]
                tcfg = test_cfg[acses.index(acs)][modes.index(mode)]
                tc_cfg['precfg'], tc_cfg['cfg'] = tcfg[0], tcfg[1]
                tc_cfg['expected'] = copy.deepcopy(tcfg[2])
                if pf_idx == 1: # prov from FMDV, adding the config check in
                    tc_cfg['expected']['cfg_match'] = True

                tc_tmpls[cfg['tcid']] = (tc, ) # HACK HERE!

                mode_idx += 1
    return tc_tmpls


tc_templates = init_tc_templates()


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed
    return:
    - (testsuite name, testcase configs)
    '''

    tbcfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbcfg),kwa['is_interactive'])

    print 'Using FlexMaster as the linux server...'
    srv_ip = tbcfg['FM']['ip_addr']

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        for tcid in tc_id:
            for tc_tmpl in tc_templates[tcid]:
                tc = copy.deepcopy(tc_tmpl)
                cfg = dict(
                    model_id = int(model_map[model]),
                    model = model.upper(),
                    ap_ip = aps[model],
                )
                fill_tc_cfg(tc, cfg)
                test_cfgs[re.search('TCID:(.*?) -', tc[0]).group(1)] = tc
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View - Remote Management', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
