import sys
import os
from pprint import pformat

from libFM_TestSuite import start_fm, init_firmware_path, \
        get_local_firmwares, input_builds, make_test_suite, model_map
from RuckusAutoTest.common.lib_KwList import as_dict


'''
1.1.9.3. Firmware Upgrade Testsuite

1.1.9.3.1   Create fw upgrade task to ZF2925
1.1.9.3.2   Create fw upgrade task to ZF2942(select by group)
1.1.9.3.5   Create fw upgrade task to ZF7942(select by group)
1.1.9.3.13  Select by device to be fw upgrade
1.1.9.3.14  By schedule provisioning_fm firmware task to device and repeat test case 1.1.9.3.1-1.1.9.3.13

1.1.9.3.15  Cancel fw upgrade task
1.1.9.3.16  Firmware upgrade using HTTPS
1.1.9.3.17  FW Upgrade result

1.1.9.3.3   Create fw upgrade task to ZF2942_hotspot(select by group)
1.1.9.3.4   Create fw upgrade task to ZF2942_hotspot(select by group)
1.1.9.3.6   Create fw upgrade task to ZF2741(select by group)
1.1.9.3.7   Create fw upgrade task to VF7811
1.1.9.3.8   Create fw upgrade task to VF2811
1.1.9.3.9   Create fw upgrade task to VF2825(ruckus01)
1.1.9.3.10  Create fw upgrade task to VF2825(ruckus03)
1.1.9.3.11  Create fw upgrade task to VF2825(ruckus04)
1.1.9.3.12  Create fw upgrade task to ZD(select by group)

1.1.9.3.18  Partial successful provision result
1.1.9.3.19  Backup image test
1.1.9.3.20  Failed task could be restart
'''
# 2925_7.1.0.0.39_FCS.Bl7 ( 2925-7.1.0.0.39 )
# 2942_7.1.0.0.39_FCS.Bl7 ( 2942-7.1.0.0.39 )
# 7942_7.1.0.0.31_FCS.Bl7 ( 7942-7.1.0.0.31 )


def uploadFws(**kwa):
    '''
    Upload the firmwares to FM, if not exist
    kwa:
    . fmCfg
    . fmFws:     (optional) if given, then no need to get the list of firmwares
                 on Flex Master. By default, it is None
    . firmwares: a dict of model/firmware
    '''
    p = dict(fmFws=None)
    p.update(kwa)

    print('Uploading the selected firmware(s) to FM...')
    fm = None
    fmFws = p['fmFws']
    for fws in p['firmwares']:
        for m in fws.keys():
            if not fmFws: # get the list of Fws if not exists
                if not fm:    # start FM on request
                    sm, fm = start_fm(**p['fmCfg'])
                fmFws = [fw['firmwarename'] for fw in fw.get_all_firmwares(fm)]
            if not fws[m][1] in fmFws:
                if not fm:    # start FM on request
                    sm, fm = start_fm(**p['fmCfg'])
                fm.lib.fw.upload_firmware(fm, models=[m],
                                   filepath=os.path.join(init_firmware_path(), fws[m][1]))
    if fm:
        fm.stop()
        sm.shutdown()
        del fm, sm


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed: for uploading the firmwares
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = ['01.01.09.03.01',    '01.01.09.03.13', '01.01.09.03.14.01',
             '01.01.09.03.14.02', '01.01.09.03.15', '01.01.09.03.16',
             '01.01.09.03.17', ]

    tc_templates = [
      [ 'TCID:%s.%s - Create firmware upgrade task - %s',
        'FM_FwUpgrade',
        { 'model': '%s',
          'device_select_by': 'group',
          'firmware': '%s',
          'downgradeFw': '%s',
          'reboot':   True,
          'schedule': 0,
        },
      ],
      # 1.1.9.3.13. Select by device to be fw upgrade
      [ 'TCID:%s.%s - Select by device to be fw upgrade - %s',
        'FM_FwUpgrade',
        { 'model': '%s',
          'device_select_by': 'device',
          'firmware': '%s',
          'downgradeFw': '%s',
          'reboot':   True,
          'schedule': 0,
        },
      ],
      # 1.1.9.3.14 By schedule provisioning_fm firmware task to device
      #            and repeat test case 1.1.9.3.1-1.1.9.3.13
      [ 'TCID:%s.%s - By schedule provisioning_fm firmware task to device (by group) - %s',
        'FM_FwUpgrade',
        { 'model': '%s',
          'device_select_by': 'group',
          'firmware': '%s',
          'downgradeFw': '%s',
          'reboot':   True,
          'schedule': 3,
        },
      ],
      [ 'TCID:%s.%s - By schedule provisioning_fm firmware task to device (by device) - %s',
        'FM_FwUpgrade',
        { 'model': '%s',
          'device_select_by': 'device',
          'firmware': '%s',
          'downgradeFw': '%s',
          'reboot':   True,
          'schedule': 3,
        },
      ],
      # 1.1.9.3.15. Cancel fw upgrade task
      [ 'TCID:%s.%s - Cancel fw upgrade task - %s',
        'FM_FwUpgrade',
        { 'test_type': 'cancel', 'model': '%s', 'firmware': '%s', 'downgradeFw': '%s', },
      ],
      # 1.1.9.3.16. Firmware upgrade using HTTPS
      [ 'TCID:%s.%s - Firmware upgrade using HTTPS - %s',
        'FM_FwUpgrade',
        { 'test_type': 'https', 'model': '%s', 'firmware': '%s', 'downgradeFw': '%s', },
      ],
      # 1.1.9.3.17. FW Upgrade result
      [ 'TCID:%s.%s - FW Upgrade result - %s',
        'FM_FwUpgrade',
        { 'test_type': 'result', 'model': '%s', 'firmware': '%s', 'downgradeFw': '%s', },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    fmCfg = tbCfg['FM']
    print 'Getting the list of firmwares...'
    localFws = get_local_firmwares(isFmFwIncluded=True, fmCfg=fmCfg)
    test_fws = input_builds(models=kwa['models'], localFws=localFws, is_interactive=kwa['is_interactive'])

    print '\nPlease select the firmwares for downgrading after testing'
    downgrade_fws = input_builds(models=kwa['models'], localFws=localFws,is_interactive=kwa['is_interactive'])
    uploadFws(fmCfg=tbCfg['FM'], firmwares=[test_fws, downgrade_fws],
              fmFws=localFws['fm'])

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    print 'Selected firmwares for upgrading:\n%s\n' % pformat([(k, test_fws[k][1]) for k in test_fws.keys()])
    print 'Selected firmwares for downgrading after testing:\n%s\n' % \
          pformat([(k, downgrade_fws[k][1]) for k in downgrade_fws.keys()])
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                import copy
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                tc[2]['model'] = tc[2]['model'] % model
                tc[2]['firmware'] = tc[2]['firmware'] % test_fws[model][1][5:]
                tc[2]['downgradeFw'] = tc[2]['downgradeFw'] % downgrade_fws[model][1][5:]

                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Firmware Upgrade', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']


if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

