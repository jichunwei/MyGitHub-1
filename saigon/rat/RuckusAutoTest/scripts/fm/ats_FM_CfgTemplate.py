import sys
import copy
from random import randint

from libFM_TestSuite  import model_map, make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map2


"""
Config Structure of a defineXXTsCfg() function:
    cfg = [
      ( Common name,
        Testsuite class,
        {
          configs,
        },
      ),
    ]
return (testsuite name, cfg)
"""

'''
1.1.9.1.1 Create new template for every model(ZF2925/ZF2942/ZF7942/ZF2741/VF7811/VF2825- Ruckus01/VF2825-Ruckus03/VF2825-Ruckus04)
1.1.9.1.2    Saved template edit(ZF2925/ZF2942/ZF7942/ZF2741/VF7811/VF2825- Ruckus01/VF2825-Ruckus03/VF2825-Ruckus04)
1.1.9.1.3    Template delete(ZF2925/ZF2942/ZF7942/ZF2741/VF7811/VF2825- Ruckus01/VF2825-Ruckus03/VF2825-Ruckus04)
1.1.9.1.4    Related to auto configuration template can not be deleted
1.1.9.1.5    some parameters are invaild check - 2925
1.1.9.1.6    Configuration Templates: Make sure exist template could be copy
1.1.9.1.7    Configuration Templates: Make sure exist template could be export to xls file
'''
'''
Detail AP configuration for templates returned from getAPCfgTemplate() function
    {
        'zf2925'[{config_1}, {config_2}, {config_3}, {config_4}],
        'zf2942'[{config_1}, {config_2}, {config_3}, {config_4}],
        'zf7942'[{config_1}, {config_2}, {config_3}, {config_4}],
    }
    Detail for config_1: Device General, WLAN Common, WLAN 1 to 4, Rate Limiting
    Detail for config_2: Device General, WLAN Common, WLAN 5 to 8, Rate Limiting
    Detail for config_3: Device General, WLAN Common, WLAN 1 to 8, No Rate Limiting
    Detail for config_4: WLAN 1 to 8, No Rate Limiting

'''

def defineInvalidCfgs():
    '''
    TODO: Revise this function to avoid repeat code.
    This function is to get invalid configuration for validation invalid values.
    There are three invalid configurations for each items.

    Output:
    return a list: [invalid_cfg_1, invalid_cfg_2, invalid_cfg_3]
    '''
    # Define a group of values to do invalid check
    internet = [{
                    'gateway': 'a.b.c.d',
                    'conn_type': 'static',
                    'ip_addr': 'a.b.c.d', # 1.1.1, 256.1.1.1",
                    'mask': 'a.b.c.d',#"List of invalid IPs to check: 255.255.255.256, 255.255.0, ",
                },
                {
                    'gateway': '-1.1.1.1',
                    # If we use conn_type=static, you have to include its sub-items as mask, ip_addr
                    'conn_type': 'static',
                    'ip_addr': '-1.1.1.1', # 1.1.1, 256.1.1.1",
                    # NOTE: As Alex agreed, we only open a bug "8188" for the subnet mask problem with
                    # value "255.255.255.256" and  use another value like '-1.1.1.1' to do validate
                    # for subnet mask instead of "255.255.255.256"
                    'mask': '-1.1.1.1',#"List of invalid IPs to check: 255.255.255.256, 255.255.0, ",
                },
                {
                    'gateway': '256.1.1.1',
                    'conn_type': 'static',
                    'ip_addr': '256.1.1.1', # 1.1.1, 256.1.1.1",
                    'mask': '256.255.255.255',#"List of invalid IPs to check: 255.255.255.256, 255.255.0, ",
                },
               ]

    mgmt = [{
                'telnet_port': "a",
                'ssh_port': "a",
                'http_port': "a",
                'https_port': "a",
                'log_srv_ip': "a.a.a.a",
                'log_srv_port': "a",
            },
            {
                'telnet_port': "0",
                'ssh_port': "0",
                'http_port': "0",
                'https_port': "0",
                'log_srv_ip': "-1.1.1.1",
                'log_srv_port': "0",
            },
            {
                'telnet_port': "66666",
                'ssh_port': "66666",
                'http_port': "66666",
                'https_port': "66666",
                'log_srv_ip': "256.1.1.1",
                'log_srv_port': "66666",
            },
           ]

    vlan = [{
                'mgmt_id': "a",
                'tunnel_id': "a",
                'vlan_a_id': "a",
                'vlan_b_id': "a",
                'vlan_c_id': "a",
                'vlan_d_id': "a",
                'vlan_e_id': "a",
                'vlan_f_id': "a",
                'vlan_g_id': "a",
                'vlan_h_id': "a",
            },
            #The configuration has two the same id
            {
                'mgmt_id': "0",
                'tunnel_id': "0",
                'vlan_a_id': "0",
                'vlan_b_id': "0",
                'vlan_c_id': "0",
                'vlan_d_id': "0",
                'vlan_e_id': "0",
                'vlan_f_id': "0",
                'vlan_g_id': "0",
                'vlan_h_id': "0",
            },
            {
                'mgmt_id': "4095",
                'tunnel_id': "4096",
                'vlan_a_id': "4097",
                'vlan_b_id': "4098",
                'vlan_c_id': "4099",
                'vlan_d_id': "4050",
                'vlan_e_id': "4051",
                'vlan_f_id': "4052",
                'vlan_g_id': "4053",
                'vlan_h_id': "4054",
            },
           ]#vlan
    wlan = [ {
                'wlan_num': '%d',#"A number  to point out wlan 1 -> wlan 8",
                'dtim': '0',#'A number out of range (1, 255) to do the check',
                #'frag_threshold': '0',#'A number out of range (245, 2346) to do the check',
                'rtscts_threshold': '0',#'A number out of range (245, 2346) to do the check',
             },
             {
                'wlan_num': '%d',#"A number  to point out wlan 1 -> wlan 8",
                'dtim': '-1',#'A number out of range (1, 255) to do the check',
                #'frag_threshold': '-1',#'A number out of range (245, 2346) to do the check',
                'rtscts_threshold': '-1',#'A number out of range (245, 2346) to do the check',
             },
             {
                'wlan_num': '%d',#"A number  to point out wlan 1 -> wlan 8",
                'dtim': '256',#'A number out of range (1, 255) to do the check',
                #'frag_threshold': '2347',#'A number out of range (245, 2346) to do the check',
                'rtscts_threshold': '2347',#'A number out of range (245, 2346) to do the check',
             },
           ]

    cfgs = {
        'internet': internet,
        'mgmt': mgmt,
        'vlan': vlan,
    }
    # add invalid check for wlan 1 to wlan 8
    for i in range(1,9):
        tmp = copy.deepcopy(wlan)
        k = 'wlan_%d' % i
        tmp[0]['wlan_num'] = '%d' % i
        tmp[1]['wlan_num'] = '%d' % i
        tmp[2]['wlan_num'] = '%d' % i
        cfgs[k] = tmp

    combined_cfgs, key_name = [], 'Internet,Mgmt,Vlan,Wlan: 1->8'
    type_check = [
        'Non-numerical char. Pages: %s' % key_name,
        'Value < (valid range). Pages: %s' % key_name,
        'Value > (valid range). Pages: %s' % key_name,
    ]
    for i in range(0,3):
        tmp = {}
        for k, v in cfgs.iteritems():
            tmp[k] = v[i]

        combined_cfgs.append(dict(name=type_check[i], cfg=tmp))

    return combined_cfgs


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    @TODO: Will restructure this function by new way to define ts later
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = ['01.01.09.01.01', '01.01.09.01.02', '01.01.09.01.03',
             '01.01.09.01.04', '01.01.09.01.05', '01.01.09.01.06',
             '01.01.09.01.07',
             ]

    multiple_cfg_tcs = ['01.01.09.01.05', '01.01.09.01.01']
    # Get AP configuration for the test
    negative_cfgs = defineInvalidCfgs()
    simple_cfg = {
        'device_general': {
            'device_name': "rat"
        }
    }
    tc_templates = [
      #1.1.9.2.1    Create a new configuration task to Group - ZF295
      #1.1.9.2.2    Create a new configuration task to Group - ZF2942
      #1.1.9.2.4    Create a new configuration task to Group - ZF7942
      [ 'TCID:%s.%02d.%s - Create a config template. Config: %s - %s',
        'FM_CreateConfTemplate',
        {
            'template_name': 'Test Create tmpl %s',#'Name of template'
            'template_model': '%s',#'template for a model: zf2942, zf2925, zf7942'
            # Update list of options for the template here
        },
      ],
      # 1.1.9.2.10    Select by device to be provisioned configuration
      [ 'TCID:%s.%s - Edit template - %s',
        'FM_EditConfTemplate',
        {
            'template_name': 'Test Edit tmpl %s',#'Name of template'
            'template_model': '%s',#'template for a model: zf2942, zf2925, zf7942'
            'old_confs': {
                # Update list of options for the template here
            },
            'new_confs':{
                # Update list of options for the template here
            }
        },
      ],
      # 1.1.9.3.14. By schedule provisioning firmware task to device
      #             and repeat test case 1.1.9.3.1-1.1.9.3.13
      [ 'TCID:%s.%s - Delete template - %s',
        'FM_DeleteConfTemplate',
        {
            'template_name': 'Test Delete tmpl %s',#'Name of template'
            'template_model': '%s',#'template for a model: zf2942, zf2925, zf7942'
            # Update list of options to create a new config template to delete here
        },
      ],
      #1.1.9.1.4    Related to auto configuration template can not be deleted
      [ 'TCID:%s.%s - Delete config template being used by auto config rule - %s',
        'FM_DeleteAutoConfTemplate',
        {
            'template_model': '%s',#'template for a model: zf2942, zf2925, zf7942'
            'options': {}
        },
      ],
      # 1.1.9.1.5    some parameters are invaild check
      [ 'TCID:%s.%02d.%s - Negative check. Type: %s - %s',
        'FM_CheckValidationConfTemplate',
        {
            'template_name': 'Test invalid check tmpl %s',#'Name of template'
            'template_model': '%s',#'template for a model: zf2942, zf2925, zf7942'
            # Update list of options to do invalid check for the template here
        },
      ],
      # 1.1.9.1.6    Configuration Templates: Make sure exist template could be copy
      [ 'TCID:%s.%s- Copy template - %s',
        'FM_CfgTemplate',
        {
            'template_name': 'Test copy cfg template for model %s',# for back compatible, unused param with new testscript
            'template_model': 'AP model',
            'input_cfg': {},
            'test_type': 'copy',
        },
      ],
      # 1.1.9.1.7    Configuration Templates: Make sure exist template could be export to xls file
      [ 'TCID:%s.%s - Export config template to xls file - %s',
        'FM_CfgTemplate',
        {
            'template_name': 'Test copy cfg template for model %s', # for back compatible, unused param with new testscript
            'template_model': 'AP model',
            'input_cfg': {},
            'test_type': 'export',
        },
      ],
    ]

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    test_cfgs = {}
    for model in kwa['models']:
        # get config for this model
        ap_cfgs =[]
        ap_cfg_obj = model_cfg_map2[model.lower()]
        ap_cfgs.append(ap_cfg_obj.get_device_general_cfg(is_dv_cfg=False))
        ap_cfgs.append(ap_cfg_obj.get_wlan_common_cfg(is_dv_cfg=False))
        ap_cfgs.extend(ap_cfg_obj.get_wlan_cfgs(is_dv_cfg=False))
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                if not tc_id[i] in multiple_cfg_tcs:
                    tc = copy.deepcopy(tc_templates[i])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                    if tc_id[i] !='01.01.09.01.04':
                        tc[2]['template_name'] = tc[2]['template_name'] % model
                    tc[2]['template_model'] = model.upper()

                    # List options
                    cfg_map = {
                        '01.01.09.01.02': {
                            'old_confs': simple_cfg,
                            'new_confs': ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg'],
                        },
                        '01.01.09.01.03': ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg'],
                        '01.01.09.01.04': {
                            'options': simple_cfg,
                        },
                        '01.01.09.01.06': {
                            'input_cfg': ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg'],
                        },
                        '01.01.09.01.07': {
                            'input_cfg': ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg'],
                        },
                    }
                    tc[2].update(cfg_map[tc_id[i]])

                    test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc
                else:
                    #1. Invalid is a special test case, it requires three input configs for each model to do the check
                    # so we need to separate it.
                    #2. Create template tc also verify a few of input test config so put it here
                    cfgs = {
                        '01.01.09.01.01': ap_cfgs,
                        '01.01.09.01.05': negative_cfgs,
                    }[tc_id[i]]
                    for idx, cfg in enumerate(cfgs):
                        tc = copy.deepcopy(tc_templates[i])
                        # filling the template
                        tc[0] = tc[0] % (
                            tc_id[i], (idx+1), model_map[model],
                            cfg['name'], model.upper()
                        )
                        tc[2]['template_name'] = tc[2]['template_name'] % model
                        tc[2]['template_model'] = model.upper()
                        # List options
                        tc[2].update(cfgs[idx]['cfg'])

                        test_cfgs['%s.%02d.%s' % (tc_id[i], (idx+1), model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Configuration Template', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)


