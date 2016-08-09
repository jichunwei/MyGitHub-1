import sys
import copy

from libFM_TestSuite import (
        model_map, make_test_suite, select_ap_by_model, get_aps_by_models,
        get_testsuitename, filter_tcs, sort_tcfg, get_tcid,
        get_testsuite
)
from RuckusAutoTest.common.lib_KwList import as_dict


tc_templates = {
    '03.02.02.05': (
      [ 'TCID:%(tcid)s.01.%(model_id)02d - Remote Management set to AUTO mode - %(model)s',
        'FMDV_Mgmt_RemoteModes',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(remote_mode='fm',),
            cfg=dict(remote_mode='auto',),
            device_cfg=dict(device_name='__superdog__'),
            expected=dict(cfg_match=True, is_prov=True, prov_match=True,),
        ),
      ],
      [ 'TCID:%(tcid)s.02.%(model_id)02d - Remote Management set to Flexmaster Only mode - %(model)s',
        'FMDV_Mgmt_RemoteModes',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(remote_mode='auto',),
            cfg=dict(remote_mode='fm',),
            device_cfg=dict(device_name='__superdog__'),
            expected=dict(cfg_match=True, is_prov=True, prov_match=True,),
        ),
      ],
      [ 'TCID:%(tcid)s.03.%(model_id)02d - Remote Management set to SNMP Only - %(model)s',
        'FMDV_Mgmt_RemoteModes',
        dict(
            ap_ip='%(ap_ip)s',
            precfg=dict(remote_mode='auto',),
            cfg=dict(remote_mode='snmp',),
            device_cfg=dict(device_name='__superdog__'),
            expected=dict(cfg_match=True, is_prov=False, prov_match='na',),
        ),
      ],
    ),
}


tcs = tc_templates.keys()
filtered_tcs = {} # dict(zf2942=['03.02.02.05',])


def fill_tc_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    #log(tc[0])
    tc_cfg = tc[2]
    tc_cfg['ap_ip'] = tc_cfg['ap_ip'] % cfg
    return tc


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
