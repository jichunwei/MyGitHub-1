import sys
import copy
from pprint import pformat

from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models, input_with_default, \
        init_firmware_path, input_builds, get_local_firmwares
from RuckusAutoTest.common.lib_KwList import as_dict


'''
4.4    Management Page in ZF2925 8.0
4.4.1.1    Upgrade image via AP WebUI
4.4.1.2    Upgrade image via AP CLI mode
Idea of this add testsuite
'''
# 2925_7.1.0.0.39_FCS.Bl7 ( 2925-7.1.0.0.39 )
# 2942_7.1.0.0.39_FCS.Bl7 ( 2942-7.1.0.0.39 )
# 7942_7.1.0.0.31_FCS.Bl7 ( 7942-7.1.0.0.31 )

def _selectUpgradeProtocol(**pro_cfg):
    '''
    This function is to let users select what protocols they want to do upgrade
    Output:
    - Return a list of type of tests for ugpradihg. Each its element is a
    dictionary for ftp/tftp config
    '''
    protocols = ['tftp', 'ftp']
    print 'Select protocol to do upgrade:\n%s' % \
          '\n'.join(['  %s - %s' % (i, v) for i, v in enumerate(protocols)])
    sel_opt = input_with_default('Select protocol or all', 'all') \
              if pro_cfg['is_interactive'] else 'all'

    test_protocols = {
        '0': [protocols[0]],
        '1': [protocols[1]],
        'all': protocols,
        '': protocols,
    }[sel_opt.replace('\r', '')] # remove CR in the raw input string

    list_srv_cfg = []
    for k in test_protocols:
        list_srv_cfg.append(_inputSrvCfg(k,**pro_cfg))

    return list_srv_cfg

def _inputSrvCfg(protocol,**pro_cfg):
    '''
    '''
    print '-'*50
    print 'Enter config for %s server' % protocol
    srv_cfg = dict(
        protocol = '', # ftp, tftp
        ip_addr = '',
        port = '', # port of tftp, ftp
        rootpath = '',
        #username = '', # use for ftp only
        #password = '', # use for ftp only
    )

    srv_cfg['ip_addr'] = input_with_default('[Require]: Enter ip server', '192.168.30.252') \
                         if pro_cfg['is_interactive'] else '192.168.30.252'
    default_port = {
        'tftp': '69',
        'ftp': '21',
    }[protocol.lower()]
    srv_cfg['protocol'] = protocol
    srv_cfg['port'] = input_with_default('[Require]: Enter port for %s' % protocol, default_port) \
                      if pro_cfg['is_interactive'] else default_port
    srv_cfg['rootpath'] = input_with_default('[Require]: Enter root path for %s' % protocol
                          , pro_cfg['fw_path_dir']) \
                          if pro_cfg['is_interactive'] else pro_cfg['fw_path_dir']

    if 'ftp' == protocol:
        srv_cfg['username'] = input_with_default('[Require]: Enter username for %s' % protocol, 'root') \
                              if pro_cfg['is_interactive'] else 'root' if not pro_cfg.has_key('ftp') else pro_cfg['ftp']['username']
        srv_cfg['password'] = input_with_default('[Require]: Enter password for %s' % protocol, 'lab4man1') \
                              if pro_cfg['is_interactive'] else 'lab4man1' if not pro_cfg.has_key('ftp') else pro_cfg['ftp']['passwd']

    return srv_cfg

def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed: for uploading the firmwares
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = [
            '04.04.01.01', '04.04.01.02',
            ]

    tc_templates = [
      [ 'TCID:%s.%s.%02d - Upgrade image via AP WebUI by using protocol %s- %s',
        'AP_FwUpgrade',
        {
            'model': '',
            'ap_ip': '',
            'fw_upgrade_fm_path': '%s', #fw which is used to test, it is a full path likes "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'fw_restore_path': '%s', # fw which is used to restore when finish the test, it is a full path like "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'test_type': 'webui',
            'test_name': 'Verify firmware upgrade via Web UI by using protocol %s',
            'reboot':   True,
            'ftp_cfg': dict(
                protocol = '', # ftp, tftp
                ip_addr = '', # tftp, ftp
                port = '', # tftp, ftp
                rootpath = '', # tftp, ftp
                #username = '%s', # use for ftp only
                #password = '%s', # use for ftp only
            ),
        },
      ],
      # 1.1.9.3.13. Select by device to be fw upgrade
      [ 'TCID:%s.%s.%02d - Upgrade image via AP CLI mode by using protocol %s - %s',
        'AP_FwUpgrade',
        {
            'model': '%s',
            'ap_ip': '',
            'fw_upgrade_fm_path': '%s', #fw which is used to test, it is a full path likes "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'fw_restore_path': '%s', # fw which is used to restore when finish the test, it is a full path like "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'test_type': 'cli',
            'reboot':   True,
            'test_name': 'Verify firmware upgrade via CLI by using protocol %s',
            'ftp_cfg': dict(
                protocol = '%s', # ftp, tftp
                ip_addr = '%s', # tftp, ftp
                port = '%s', # tftp, ftp
                rootpath = '%s', # tftp, ftp
                #username = '%s', # use for ftp only
                #password = '%s', # use for ftp only
            ),
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'],tbCfg), kwa['is_interactive'])

    fmCfg = tbCfg['FM']
    fw_path_dir = init_firmware_path()
    print 'fw_path_dir: %s' % fw_path_dir

    dict_proto = {}
    dict_proto['fw_path_dir'] = fw_path_dir
    dict_proto['is_interactive'] = kwa['is_interactive']
    if kwa.has_key('ftp'):
       dict_proto['ftp'] = kwa['ftp']

    test_protocols = _selectUpgradeProtocol(**dict_proto)
    #print 'Getting the list of firmwares...'
    print 'Getting a list of fws were already downloaded to local...'
    local_fws = get_local_firmwares(isFmFwIncluded=False, fmCfg=fmCfg)
    print '\nPlease select a firmware to do test upgrading...'
    test_fws = input_builds(models=kwa['models'], localFws=local_fws, isFmFwIncluded=False, is_interactive=kwa['is_interactive'])

    print '\nPlease select a firmware to restore after testing...'
    restore_fws = input_builds(models=kwa['models'], localFws=local_fws, is_interactive=kwa['is_interactive'])

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    print 'The firmware to do test upgrading:\n\t%s\n' % pformat([(k, test_fws[k][1]) for k in test_fws.keys()])
    print 'The firmware to restore after testing:\n\t%s\n' % \
          pformat([(k, restore_fws[k][1]) for k in restore_fws.keys()])

    test_cfgs = {}
    FW_NAME_POS = 1
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                '''
                'model': '%s',
                'fw_upgrade_fm_path': '%s', #fw which is used to test, it is a full path likes "D:/temp/fw/2942_8.1.0.0.72.Bl7"
                'fw_restore_path': '%s', # fw which is used to restore when finish the test, it is a full path like "D:/temp/fw/2942_8.1.0.0.72.Bl7"
                'reboot':   True,
                'test_name': 'Verify firmware upgrade via CLI with protocol %s',
                'ftp_cfg': dict(
                    protocol = '%s', # ftp, tftp
                    ip_addr = '%s', # tftp, ftp
                    port = '%s', # tftp, ftp
                    rootpath = '%s', # tftp, ftp
                    #username = '%s', # use for ftp only
                    #password = '%s', # use for ftp only
                ),
                '''
                for j, ftp_cfg in enumerate(test_protocols):
                    tc = copy.deepcopy(tc_templates[i])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], j+1,
                                     ftp_cfg['protocol'], model.upper())
                    tc[2]['model'] = model
                    tc[2]['ap_ip'] = aps[model]
                    tc[2]['fw_upgrade_fm_path'] = fw_path_dir + '\\' + test_fws[model][FW_NAME_POS]
                    tc[2]['fw_restore_path'] = fw_path_dir + '\\' + restore_fws[model][FW_NAME_POS]
                    tc[2]['test_name'] = tc[2]['test_name'] % ftp_cfg['protocol']
                    tc[2]['ftp_cfg'].update(ftp_cfg)

                    test_cfgs['%s.%s.%02d' % (tc_id[i], model_map[model], j+1)] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'AP Management - Firmware Upgrade', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

