'''
Device View

3.1.11  Display of the Associated Wireless Devices in Device View
        when AP's Associated-Clients Monitoring Mode is "Disable"
3.1.12  Display of the Associated Wireless Devices in Device View
        when AP's Associated-Clients Monitoring Mode is "Passive"
3.1.13  Display of the Associated Wireless Devices in Device View
        when AP's Associated-Clients Monitoring Mode is "Active"
'''

import sys
import copy

from libFM_TestSuite import (
        model_map, make_test_suite, select_ap_by_model, get_tcid, sort_tcfg,
        get_aps_by_models, select_client, get_testsuite,
        update_test_case, get_models
)
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):

    tc_id = ['03.01.11', ]

    tc_templates = [
      [ 'TCID:%s.%02d.%s - Display of the Associated Wireless Devices in Device View (WITH client association) - %s',
        'FMDV_ClientAssocs',
        {
            'ap_ip':     '192.168.20.171',
            'client_ip': '192.168.1.11',
            'is_client_associated': True,
        },
      ],
      [ 'TCID:%s.%02d.%s - Display of the Associated Wireless Devices in Device View (WITHOUT client association) - %s',
        'FMDV_ClientAssocs',
        {
            'ap_ip':     '192.168.20.171',
            'client_ip': '192.168.1.11',
            'is_client_associated': False,
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])
    client_ip = select_client(tbCfg, kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]:
                for j in range(len(tc_templates)):
                    tc = copy.deepcopy(tc_templates[j])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], j+1, model_map[model], model.upper())
                    tc[2]['ap_ip'] = aps[model]
                    tc[2]['client_ip'] = client_ip

                    test_cfgs[get_tcid(tc[0])] = tc
    return 'Device View - Summary Page - Associated Client List', sort_tcfg(test_cfgs)


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
