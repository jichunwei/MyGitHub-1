'''
1.1.9.8    Manage ZoneDirector Configuration

1.1.9.8.1    Add ZD configuration to FM
1.1.9.8.2    Editable Configuration file list

'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, input_with_default, \
        select_zd_by_model, get_zd_by_models
from RuckusAutoTest.common.lib_KwList import as_dict


def define_zd_cfg(tb_cfg):
    '''
    '''
    fm_ip = tb_cfg['FM']['ip_addr']
    map_path = ''

    if tb_cfg['is_interactive']:
        while not map_path:
            map_path = input_with_default('[Required]: Enter path to map image', '')
            if not map_path:
                print 'Warning: Please input the map path. Enter to continue...'
                raw_input()
    else:
        if 'map_path' not in tb_cfg or not tb_cfg['map_path']:
            print 'There is no map_path. This testsuite requires path of map.'
            exit(1)
        else:
            map_path = tb_cfg['map_path']

    print 'NOTE: BELOW VALUES ARE JUST FOR WEB UI TEST. '\
          'NO NEED TO INPUT "EXACT VALUES" FOR THEM NOW!!!'
    auth_server_ip = fm_ip
    trap_server_ip = fm_ip
    auth_server_port = fm_ip
    mail_server_ip = fm_ip
    admin_email = 'admin@ruckus.com'

    if tb_cfg['is_interactive']:
        auth_server_ip = input_with_default('[Required]: Authentication server ip', fm_ip)
        trap_server_ip = input_with_default('[Required]: Trap server ip', fm_ip)
        auth_server_port = input_with_default('[Required]: Authentication server port', '1812')
        mail_server_ip = input_with_default('[Required]: Mail server ip', fm_ip)
        admin_email = input_with_default('[Required]: Input admin email for alarm setting', 'admin@ruckus.com')

    cfg = dict(
        # define cfg for System link
        system = dict(
            # Keys for identity
            system_name = 'CloningTest',

            # Keys for FlexMaster mgmt
            enable_fm_mgmt = True, #|False,
            fm_url = fm_ip, # without "http" and "intune/server"
            fm_interval = '2',

            # SNMP Agent
            enable_snmp_agent = True, #|False,
            snmp_system_contact = 'admin@ruckus.com',
            snmp_system_location = 'Sunnyvale',
            snmp_ro_community = 'public',
            snmp_rw_community = 'private',

            # SNMP Trap
            enable_snmp_trap = True, # |False,
            trap_server_ip = trap_server_ip,
        ),
        # define cfg for CONFIGURE WLANS link
        wlan = dict(
            # keys for wlan
            wlan_ssid = 'RuckusZD_CloningTest',
            wlan_description = 'TestRuckusZD',
            wlan_type = 'standard',
            auth = 'open',
            encrypt_method = None,

            # keys for wlan group
            group_name = 'Test_Wlan_Group_1',
            group_desc = 'Test Wlan Group',
            enable_vlan_override = True,
            wlan_members = [
                {'wlan_name': 'RuckusZD_CloningTest', 'vlan_attr': 'no_change'},
            ]
        ),
        access_point = {
            # Must use the value different from defaul value to test.
            '11n_2.4g': 'N-only', #'Auto' (Default), 'N-only'
            '11n_5g': 'Auto', # 'Auto', 'N-only' (Default),
        },
        access_control = dict(
            # keys for L3 ACL
            l3_acl_name = 'L3 ACL Rule 1',
            l3_acl_description = 'Test L3 ACL Rule',
            l3_acl_mode = 'allow-all', #'allow-all'|'deny-all',
            # No need this config now
            # l3_acl_rule =[
            #    dict(
            #        l3_rule_order = '',
            #        l3_rule_description = '',
            #        l3_rule_action = '',
            #        l3_rule_dst_addr = '',
            #        l3_rule_application = '',
            #        l3_rule_protocol = '',
            #        l3_rule_dst_port = '',
            #    ),
            # ], # a list of dictionary to config for rule
        ),
        map = dict(
            map_name = 'Test Map',
            map_description = "Test map in zd cloning",
            map_path = map_path, #"D:\\working\\FM_Automation\\FM_Odessa\\fm_qingdao\\rat\\rat\\components\\test.jpg"
        ),
        role = dict(
            role_name = 'Test role',
            role_description = 'Test role in zd cloning',
            group_attr = 'Test role',
            specify_wlan = 'all', # | 'wlan name',
                            #+ all: To allow access all wlans
                            #+ 'wlan name': specify only wlan name for this role.
                            # @TODO: Will enhance to allow select more than one wlan.
            guest_pass = True, #| False,
            zd_admin = 'limited', # None | False | 'full' | 'limited',
        ),
        user = dict(
            username = 'cloning_user',
            password = '1345678',
            fullname = 'Cloning User',
            role = 'Default', #'Default' | 'Role name'
        ),
        guest_access = dict(
            rsa_order = 1, #'an interger for its order',
            rsa_description = 'test restricted subnet access',
            rsa_action = 'Deny', #'Deny'|'Allow',
            rsa_dst_addr = 'Any', # 'Any' | 'pattern'
            rsa_application = 'Any',# 'Any'|'HTTP'|'HTTPS'|'FTP'|'SSH'|'TELNET'|'SMTP'|'DNS'|'DHCP'|'SNMP',
            rsa_protocol = 'Any',
            rsa_dst_port = 'Any',# 'Any'|'port interger',
        ),
        hotspot_service = dict(
            hotspot_name = 'Test Hotspot Service',
            login_page = 'http://hotspot_service_url',
            start_page = 'another_url', #'user_url'|'another_url',
            start_page_url = 'http://start_page_url',# 'specify url for this page if start_page="another_url"',
            enable_session_timeout = True, # True | False,
            session_timeout_interval = 440,# 'specify the interval here if enable_session_timeout=True',
            enable_idle_timeout = True, #True|False,
            idle_timeout_interval = 50,# 'specify the interval here if enable_idle_timeout=True',
        ),
        mesh = dict(
            mesh_name = 'cloning_mesh',
            mesh_psk = 'cloning_mesh_123',
            generate_psk = False, #True|False,
        ),
        aaa_server = dict(
            auth_name = 'cloning_ad_auth',
            auth_type = 'ad', #'ad'|'ldap'|'radius', 'radius_acc',
            # Additional attribute for each authentication server
            # Common attribute for each auth server
            server_ip = auth_server_ip,
            server_port = auth_server_port,
            # Specific attribute for Active Directory
            windows_domain_name = 'ruckus.com',
            # Specific attribute for LDAP
            # ldap_base_dn = 'Distinguish Name for LDAP',
            # Specific attribute for Radius and Radius Accounting.
            # radius_secret = 'shared secret key for Radius/Radius Accounting',
            # radius_confirm_secret = 'Confirm secret key for Radius/Radius Accounting',
        ),
        alarm_setting= dict(
            enable_email_notification = True, # True|False,
            email_addr = admin_email, # 'email address to notify',
            mail_server_ip = mail_server_ip,
        ),
        service = dict(
            # For Self Healing
            enable_adjust_ap_radio_power = True, #True|False,
            enable_adjust_ap_channel = True, #True|False,
            # For Intruction Prevention
            enable_protect_wireless_network = True, #True|False,
            enable_block_wireless_client = True, #True|False,
            block_time = 20, # specify time in minute if enable_block_wireless_client = True
            # Background Scanning
            enable_run_background_scan = True, #True|False,
            interval_scan = 10, # specify time in minute if enable_run_background_scan=True
            enable_report_rogue_device = True, #True|False, # specify True|False in minute if enable_run_background_scan=True
            # For Rogue DHCP Server Detection
            enable_rouge_dhcp_detection = True, #True|False,
        ),
    )

    return cfg

def get_test_settings(cloning_mode):
    '''
    This function is to get settings for the test. It will return keys which we
    expect they should be different and the same between the source ZD and the
    target ZD.
    - cloning_mode: 'full_restore'|'failover_restore'|'policy_restore'
    Return:
    - Return keys to set, expected_inconsistent_keys and expected_consistent_keys

    Eplaination for used variables:
    1. expected_inconsistent_keys:
       - This variable is a list to define what items
       and its sub-items of ZD Configure page are expected different between
       source and target ZD.
       - If each elment of the list is a dictionaty, keys of the dict is
       parent page and its values is a list of sub-items of this page which we
       expect different between source and target ZD.
         Otherwise, if it is a string, it means we expect all sub-items of this
        page are different between source and target ZD
       E.g:
        expected_inconsistent_keys = [
            {'system': [
                'system_name'
            ]}, # list keys which we expect that they are different between two zds for this page
            'guest_access',
        ]
        => Explaination:
            - For 'system' element: We expect the key "system_name of "system" page
              is different between source and target ZD
            - For 'guest_access' element: We expect all sub-items of "guest_access" page
              are completely different between source and target ZD.

    2. expected_consistent_keys:
       - The idea is the same for "expected_inconsistent_keys"
    '''
    keys_for_set = [
        'system', 'wlan', 'access_point', 'access_control', 'map', 'role', 'user',
        'guest_access', 'hotspot_service', 'mesh', 'aaa_server', 'alarm_setting',
        'service',
    ]
    keys_for_get = [
        {'system': []}, # list keys to get their values
        'wlan', 'access_point', 'access_control', 'map', 'role', 'user',
        'guest_access', 'hotspot_service', 'mesh', 'aaa_server', 'alarm_setting',
        'service',
    ]
    # By default, the restore mode is "full_restore" so there is no difference.
    expected_inconsistent_keys = [
        # list keys which we expect that they are different on two zds for this page
    ]
    expected_consistent_keys = [
        'system', 'wlan', 'access_point', 'access_control', 'map', 'role', 'user',
        'guest_access', 'hotspot_service', 'mesh', 'aaa_server', 'alarm_setting',
        'service',
    ]

    if 'policy_restore' == cloning_mode:
        expected_inconsistent_keys = [
            {'system': [
                'system_name'
            ]}, # list keys which we expect that they are different on two zds for this page
            #'guest_access',
        ]
        expected_consistent_keys = [
            {'system': [
                'enable_snmp_agent', 'snmp_system_contact', 'enable_snmp_trap',
                'fm_interval', 'fm_url', 'trap_server_ip', 'snmp_system_location',
                'snmp_rw_community', 'enable_fm_mgmt', 'snmp_ro_community'
            ]},
            'wlan', 'access_point', 'access_control', 'map', 'role', 'user',
            'hotspot_service', 'mesh', 'aaa_server', 'alarm_setting',
            'service','guest_access',
        ]
    elif 'failover_restore' == cloning_mode:
        expected_inconsistent_keys = [
            {'system': [
                'system_name'
            ]}, # list keys of  this page which we expect that they are different on two zds
        ]

        expected_consistent_keys = [
            {'system': [
                'enable_snmp_agent', 'snmp_system_contact', 'enable_snmp_trap',
                'fm_interval', 'fm_url', 'trap_server_ip', 'snmp_system_location',
                'snmp_rw_community', 'enable_fm_mgmt', 'snmp_ro_community'
            ]},
            'wlan', 'access_point', 'access_control', 'map', 'role', 'user',
            'guest_access', 'hotspot_service', 'mesh', 'aaa_server', 'alarm_setting',
            'service',
        ]

    return (keys_for_set, expected_inconsistent_keys, expected_consistent_keys)

def get_src_dest_zd(zd_model, tb_cfg):
    '''
    . Get source and target zd of zd_model
    . Input:
    .         - zd_model: kind of model
    .         - tb_cfg: testbed config
    . Output:
    .         - dictionary of src zd and target zd
    .            {'source_zd_ip':<src_zd>, 'target_zd_ip':<target_zd>}
    '''

    source_zd_ip, target_zd_ip = None, None
    if tb_cfg['is_interactive']:
        while source_zd_ip == target_zd_ip:
            print "Select a source ZD to get config for model %s:" % zd_model
            source_zd_ip = select_zd_by_model(get_zd_by_models([zd_model], tb_cfg))[zd_model]

            print "Select a target ZD to do config cloning for model %s:" % zd_model
            target_zd_ip = select_zd_by_model(get_zd_by_models([zd_model], tb_cfg))[zd_model]
            if source_zd_ip and target_zd_ip and source_zd_ip == target_zd_ip:
                print 'Error: Source and target ZD must be different. Enter to retry...'
                raw_input()
                continue
    else:
        zds = get_zd_by_models([zd_model], tb_cfg)
        if len(zds[zd_model]) > 1:
            source_zd_ip = zds[zd_model][0]
            target_zd_ip = zds[zd_model][1]
        else:
            raise Exception('Error: At least 2 zds for each model...')

    return {'source_zd_ip':source_zd_ip, 'target_zd_ip':target_zd_ip}

def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zd1k', 'zd3k']

    NOTE: Currently support zd1k only
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    # Currently support 1k only
    tc_id = [
            '01.01.09.07.01', '01.01.09.07.02', '01.01.09.07.03',
             '01.01.09.07.05.01', '01.01.09.07.05.02', '01.01.09.07.05.03',
             '01.01.09.07.06', '01.01.09.07.07'
             ]

    tc_templates = [
      [ 'TCID:%s.%s - Create a "Full Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {   'test_type': 'create',
            'schedule': 0,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Create a "Full Restore" ZD cloning task',
            'cloning_mode': 'full_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Create a "Failover Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {
            'test_type': 'create',
            'schedule': 0,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Create a "Failover Restore" ZD cloning task',
            'cloning_mode': 'failover_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Create a "Policy Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {
            'test_type': 'create',
            'schedule': 0,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Create a "Policy Restore" ZD cloning task',
            'cloning_mode': 'policy_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Schedule a "Full Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {
            'test_type': 'create',
            'schedule': 10,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Schedule a "Full Restore" ZD cloning task',
            'cloning_mode': 'full_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Schedule a "Failover Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {
            'test_type': 'create',
            'schedule': 10,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Schedule a "Failover Restore" ZD cloning task',
            'cloning_mode': 'failover_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Schedule a "Policy Restore" ZD cloning task - %s',
        'FM_ZdCloning',
        {
            'test_type': 'create',
            'schedule': 10,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'target_zd_ip': 'specify the target zd',
            'zd_set_cfg': 'specify the set cfg',
            'test_name': 'Create a "Policy Restore" ZD cloning task',
            'cloning_mode': 'policy_restore', # dhcp, static
            'keys_for_set': [],
            'expected_inconsistent_keys':[],
            'expected_consistent_keys': [],
        },
      ],
      [ 'TCID:%s.%s - Cancel ZoneDirector clone task - %s',
        'FM_ZdCloning',
        {   'test_type': 'cancel',
            'schedule': 10,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'test_name': 'Cancel ZD clone task',
            'cloning_mode': 'full_restore', # dhcp, static
        },
      ],
      # NOTE: This test case need to do two things:
      # 1. Verify updating result for "success" case: a clone task executed successfully.
      # 2. Verify updating result for "failed/expired" cases: Currently cannot not
      # verify this case due to no L3 switch in testbed to disable zds/aps ports on the
      # switch.
      [ 'TCID:%s.%s - Make sure FM update result for ZD clone task - %s',
        'FM_ZdCloning',
        {   'test_type': 'update',
            'schedule': 0,
            'zd_model': '',
            'source_zd_ip': 'specify the source zd',
            'test_name': 'Make sure FM update result for ZD clone task',
            'cloning_mode': 'full_restore', # dhcp, static
        },
      ],
    ]
    print "="*15 + "ENTER NECCESSARY INFO FOR ZD CLONING TEST" + "="*15
    tb_cfg = eval(kwa['testbed'].config)
    tb_cfg['is_interactive'] = kwa['is_interactive']

    if kwa.has_key('map_path'):
        tb_cfg['map_path'] = kwa['map_path']

    test_dev_cfg = {}
    for zd_model in kwa['models']:
            test_dev_cfg.update({
                zd_model: get_src_dest_zd(zd_model, tb_cfg)
            })

    # Get ZD test cfg
    zd_set_cfg = define_zd_cfg(tb_cfg)

    print 'Generate testcases for model(s)/ZD(s): %s' \
          % (', '.join(['%s (%s)' % (m, test_dev_cfg[m]) for m in kwa['models']]))
    test_cfgs = {}

    for zd_model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                #for j in range(len(tc_templates)):
                tc = copy.deepcopy(tc_templates[i])
                # Get test setting for this test
                keys_for_set, expected_inconsistent_keys, expected_consistent_keys = \
                                                get_test_settings(tc[2]['cloning_mode'])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[zd_model], zd_model.upper())
                tc[2]['zd_model'] = zd_model
                tc[2]['source_zd_ip'] = test_dev_cfg[zd_model]['source_zd_ip']
                if tc[2]['test_type'] == 'create':
                    tc[2]['target_zd_ip'] = test_dev_cfg[zd_model]['target_zd_ip']
                    tc[2]['zd_set_cfg'] = zd_set_cfg
                    tc[2]['keys_for_set'] = keys_for_set
                    tc[2]['expected_inconsistent_keys'] = expected_inconsistent_keys
                    tc[2]['expected_consistent_keys']   = expected_consistent_keys

                test_cfgs['%s.%s' % (tc_id[i], model_map[zd_model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Configure -  ZoneDirector Clone', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_zd_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

