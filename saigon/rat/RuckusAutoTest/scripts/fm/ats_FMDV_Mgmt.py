import sys
import copy

from libFM_TestSuite import (
        model_map, make_test_suite, select_ap_by_model, get_aps_by_models,
        get_testsuitename, filter_tcs, sort_tcfg, get_tcid,get_testsuite,
        update_test_case, get_models
)
from RuckusAutoTest.common.lib_KwList import as_dict


tc_templates = {
    '03.02.02.01': (
      [ 'TCID:%(tcid)s.01.%(model_id)02d - SSH: enabled, default port (22) - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(ssh_enabled='disabled', ssh_port=9996,
                        telnet_enabled='disabled', https_enabled='enabled',),
            cfg=dict(ssh_enabled='enabled', ssh_port=22,),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=23, telnet=False,ssh_port=22),
            expected=dict(web=True, cli=True, cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.02.%(model_id)02d - SSH: enabled, custom port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(ssh_enabled='disabled', ssh_port=22,
                        telnet_enabled='disabled', https_enabled='enabled',),
            cfg=dict(ssh_enabled='enabled', ssh_port=9996,),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=23, telnet=False,ssh_port=9996),
            expected=dict(web=True, cli=True, cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.03.%(model_id)02d - SSH: disabled - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(ssh_enabled='enabled', ssh_port=22,
                        https_enabled='enabled',),
            cfg=dict(ssh_enabled='disabled',),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=23, telnet=False,ssh_port=22),
            expected=dict(web=True, cli=False, cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.04.%(model_id)02d - Telnet: enabled, default port (23) - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(telnet_enabled='disabled', telnet_port=9997,
                        ssh_enabled='disabled', https_enabled='enabled',),
            cfg=dict(telnet_enabled='enabled', telnet_port=23,),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=23, telnet=True, force_telnet=True),
            expected=dict(web=True, cli=True, cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.05.%(model_id)02d - Telnet: enabled, custom port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(telnet_enabled='disabled', telnet_port=23,
                        ssh_enabled='disabled', https_enabled='enabled',),
            cfg=dict(telnet_enabled='enabled', telnet_port=9997,),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=9997, telnet=True, force_telnet=True),
            expected=dict(web=True, cli=True, cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.06.%(model_id)02d - Telnet: disabled - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(telnet_enabled='enabled', telnet_port=23,
                        https_enabled='enabled',),
            cfg=dict(telnet_enabled='disabled',),
            ap_cfg=dict(ip_addr='%(ap_ip)s', https=True,),
            apcli_cfg=dict(ip_addr='%(ap_ip)s', port=23, telnet=True, force_telnet=True),
            expected=dict(web=True, cli=False, cfg_match=True),
        ),
      ],
    ),

    '03.02.02.02': (
      [ 'TCID:%(tcid)s.01.%(model_id)02d - HTTP: enabled, default port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(http_enabled='disabled', https_enabled='enabled',),
            cfg=dict(http_enabled='enabled', http_port=80,
                     https_enabled='disabled'),
            ap_cfg=dict(ip_addr='%s:%s' % ('%(ap_ip)s', 80), https=False,),
            expected=dict(web=True, cli='na', cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.02.%(model_id)02d - HTTP: enabled, custom port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(http_enabled='disabled', https_enabled='enabled',),
            cfg=dict(http_enabled='enabled', http_port=9999,
                     https_enabled='disabled',),
            ap_cfg=dict(ip_addr='%s:%s' % ('%(ap_ip)s', 9999), https=False,),
            expected=dict(web=True, cli='na', cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.03.%(model_id)02d - HTTPS: enabled, default port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(https_enabled='disabled', http_enabled='enabled',),
            cfg=dict(https_enabled='enabled', https_port=443,
                     http_enabled='disabled',),
            ap_cfg=dict(ip_addr='%s:%s' % ('%(ap_ip)s', 443), https=True,),
            expected=dict(web=True, cli='na', cfg_match=True),
        ),
      ],
      [ 'TCID:%(tcid)s.04.%(model_id)02d - HTTPS: enabled, custom port - %(model)s',
        'FMDV_Mgmt_WebCLI',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(https_enabled='disabled', http_enabled='enabled',),
            cfg=dict(https_enabled='enabled', https_port=9998,
                     http_enabled='disabled',),
            ap_cfg=dict(ip_addr='%s:%s' % ('%(ap_ip)s', 9998), https=True,),
            expected=dict(web=True, cli='na', cfg_match=True),
        ),
      ],
    ),

    '03.02.02.03': (
      [ 'TCID:%(tcid)s.01.%(model_id)02d - Log Access & Syslog Server:' +
        ' log enabled, syslog set to linux server - %(model)s',
        'FMDV_Mgmt_Log',
        dict(
            ap_ip='%(ap_ip)s',
            log_cfg=dict(log_enabled='enabled', log_ip='%(srv_ip)s', log_port=514,),
            log_precfg=dict(log_enabled='disabled',),
            srv_cfg=dict(ip_addr='%(srv_ip)s',),
            # No compare match between log of syslog server and AP
            expected=dict(cfg_match=True, local=True, server=True, log_match='na',)
        ),
      ],
      [ 'TCID:%(tcid)s.03.%(model_id)02d - Log Access & Syslog Server:' +
        ' log disabled, syslog set to linux server - %(model)s',
        'FMDV_Mgmt_Log',
        dict(
            ap_ip='%(ap_ip)s',
            log_cfg=dict(log_enabled='disabled',),
            log_precfg=dict(log_enabled='enabled', log_ip='%(srv_ip)s', log_port=514,),
            srv_cfg=dict(ip_addr='%(srv_ip)s',),
            expected=dict(cfg_match=True, local=False, server=False, log_match='na',),
        ),
      ],
    ),

    '03.02.02.04': (
      [ 'TCID:%(tcid)s.%(model_id)02d - Disable all management services - %(model)s',
        'FMDV_Mgmt_DisableAll',
        dict(ap_ip='%(ap_ip)s',),
      ],
    ),
}


tcs = tc_templates.keys()
filtered_tcs = {}


def fill_tc_cfg(tc, cfg):
    tc[0] %= cfg
    #log(tc[0])
    tc_cfg = tc[2]
    tc_cfg['ap_ip'] %= cfg
    if 'ap_cfg' in tc_cfg:
        tc_cfg['ap_cfg']['ip_addr'] %= cfg
    if 'apcli_cfg' in tc_cfg:
        tc_cfg['apcli_cfg']['ip_addr'] %= cfg

    if 'log_cfg' in tc_cfg:
        tc_cfg['srv_cfg']['ip_addr'] %= cfg
        log_cfg, log_precfg = tc_cfg['log_cfg'], tc_cfg['log_precfg']
        if 'log_ip' in log_cfg:
            log_cfg['log_ip'] %= cfg
        if 'log_ip' in log_precfg:
            log_precfg['log_ip'] %= cfg
    return tc


def get_ap_cls(model):
    from RuckusAutoTest.components import get_cls
    from RuckusAutoTest.components import APWebUIs
    return get_cls(APWebUIs, model)


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
    for model, tcid in filter_tcs(kwa['models'], tcs, filtered_tcs):
        for tc_tmpl in tc_templates[tcid]:
            tc = copy.deepcopy(tc_tmpl)
            fill_tc_cfg(
                tc,
                dict(
                    tcid = tcid,
                    model_id = int(model_map[model]),
                    model = model.upper(),
                    ap_ip = aps[model],
                    srv_ip = srv_ip,
                )
            )
            test_cfgs[get_tcid(tc[0])] = tc
    return get_testsuitename('dv_mgmt'), sort_tcfg(test_cfgs)


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
