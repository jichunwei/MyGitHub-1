'''
4.4    Management Page
4.4.2    TR069 in AUTO mode after factory default
4.4.4    Digest-authentication Username and Password should be shown
4.4.5    Device Periodically inform
4.4.6    "Auto" mode and option 43
4.4.7    "FlexMaster only" mode and DNS resolve.
4.4.8    "FlexMaster only" mode with HTTPS
'''

import sys
import copy
import re

from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models, input_with_default
from RuckusAutoTest.common.lib_KwList import as_dict


tc_id = ['04.04.02', '04.04.04', '04.04.05', '04.04.06', '04.04.07', '04.04.08', ]

tc_templates = {
    '04.04.02': (
      [ 'TCID:%(tcid)s.%(model_id)02d - TR069 in AUTO mode after factory default - %(model)s',
        'AP_Tr069ModeAfterFactory',
        dict(
            ap_ip = '%(ap_ip)s',
            model = '%(model)s',
            test_name = 'Tr069 mode is in "auto" mode after factory default',
            exp_mgmt_cfg = dict(remote_mode='auto'),
        ),
      ],
    ),
    '04.04.04': (
      [ 'TCID:%(tcid)s.%(model_id)02d -  Digest-authentication Username and Password should be shown - %(model)s',
        'AP_CheckDigestAuthInfo',
        dict(
            ap_ip = '%(ap_ip)s',
        ),
      ],
    ),
    '04.04.05': (
      [ 'TCID:%(tcid)s.01.%(model_id)02d - Device Periodically inform - %(model)s',
        'AP_CheckCallHomeInform',
        dict(
            ap_ip='%(ap_ip)s',
            inform_interval  = '1m',
            default_interval = '15ms',
            times_to_check   = 5,
        ),
      ],
      [ 'TCID:%(tcid)s.02.%(model_id)02d - Device Periodically inform - %(model)s',
        'AP_CheckCallHomeInform',
        dict(
            ap_ip='%(ap_ip)s',
            inform_interval  = '5ms',
            default_interval = '15ms',
            times_to_check   = 3,
        ),
      ],
        [ 'TCID:%(tcid)s.03.%(model_id)02d - Device Periodically inform - %(model)s',
          'AP_CheckCallHomeInform',
           dict(
                ap_ip='%(ap_ip)s',
                inform_interval  = '15ms',
                default_interval = '15ms',
                times_to_check   = 2, # it will take long time if we check many periodics
        ),
      ],
    ),
    '04.04.06': (
      [ 'TCID:%(tcid)s.%(model_id)02d - Auto mode and option 43 - %(model)s',
        'FM_APRegMgmt',
        "{\
            'ap_ip': '%(ap_ip)s',\
            'input_mgmt_cfg': {\
                'remote_mode'     : 'auto',\
                'fm_url'          : '',\
                'inform_interval' : '5ms'\
            },\
            'srv_cfg': %(srv_cfg)s,\
        }",
      ],
    ),
    '04.04.07': (
      [ 'TCID:%(tcid)s.%(model_id)02d - "FlexMaster only" mode and DNS resolve - %(model)s',
        'FM_APRegMgmt',
        "{\
            'ap_ip': '%(ap_ip)s',\
            'input_mgmt_cfg': {\
                'remote_mode'     : 'fm',\
                'fm_url'          : 'http://%(fm_domain_name)s/intune/server',\
                'inform_interval' : '5ms'\
            },\
            'srv_cfg': %(srv_cfg)s,\
        }",
      ],
    ),
    '04.04.08': (
      [ 'TCID:%(tcid)s.%(model_id)02d - "FlexMaster only" mode with HTTPS - %(model)s',
        'FM_APRegMgmt',
        "{\
            'ap_ip': '%(ap_ip)s',\
            'input_mgmt_cfg': {\
                'remote_mode'     : 'fm',\
                'fm_url'          : 'https://%(fm_ip)s/intune/server',\
                'inform_interval' : '5ms',\
            },\
            'srv_cfg': %(srv_cfg)s,\
        }",
      ],
    ),
}

def input_linux_srv_cfg(is_interactive=True):
    srv_cfg = dict(
        ip_addr      = '192.168.30.252',
        user        = 'lab',
        password      = 'lab4man1',
        root_password = 'lab4man1',
    )
    if is_interactive:
        srv_cfg['ip_addr'] = input_with_default('Please input Linux DHCP server address', srv_cfg['ip_addr'])
        srv_cfg['user'] = input_with_default('Please input an user to access the server', srv_cfg['user'])
        srv_cfg['password'] = input_with_default('Please input password of %s' % srv_cfg['user'], srv_cfg['password'])
        srv_cfg['root_password'] = input_with_default('Please input the root password', srv_cfg['root_password'])

    return srv_cfg

def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed
    return:
    - (testsuite name, testcase configs)
    '''
    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    srv_cfg = input_linux_srv_cfg(kwa['is_interactive'])
    fm_domain_name =input_with_default('Please input FM name in domain format to verify DNS resolve',
                                     'itms.ruckus.com') \
                    if kwa['is_interactive'] else 'itms.ruckus.com'

    fm_ip = tbCfg['FM']['ip_addr']

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        for tcid in tc_id:
            for tc_tmpl in tc_templates[tcid]:
                tc = copy.deepcopy(tc_tmpl)
                cfg = dict(
                    tcid = tcid,
                    model_id = int(model_map[model]),
                    model = model.upper(),
                    ap_ip = aps[model],
                    srv_cfg = srv_cfg,
                    fm_ip = fm_ip,
                    fm_domain_name = fm_domain_name,
                )
                tc = eval(str(tc) % cfg)
                test_cfgs[re.search('TCID:(.*?) -', tc[0]).group(1)] = tc
    keys = test_cfgs.keys()
    keys.sort()
    return 'AP - Management Page', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
