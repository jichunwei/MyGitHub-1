import sys
import copy
import re

from libFM_TestSuite import make_test_suite, get_testsuitename
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.components.lib.dev_features import FM as fmft

# model_map is in libFM_TestSuite.py
tc_templates = {
    '07.02.04.01': (
      [ 'TCID:%(tcid)s - NA create Configuration Upgrade task for all device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='cfg_upgrade',
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            ],
            tmpl=dict( # for cfg_upgrade only
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))
            ),
            task=dict(
                task_name='2942',
                #template_name='', # update later
                template_model='zf2942'.upper(),
                provision_to=dict(device='192.168.20.180'), # get this by model
            ),
        ),
      ],
    ),
    '07.02.04.02': (
      [ 'TCID:%(tcid)s - NA create Factory Reset task for all device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='factory_reset',
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now', reboot='True',
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),
    '07.02.04.04': (
      [ 'TCID:%(tcid)s - NA upgrade firmware for all device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='fw_upgrade',
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now',
                zf2942_fw='.*8.1.0.0.124.*', # get this by model
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),

    '07.02.04.05': (
      [ 'TCID:%(tcid)s - NA create Reboot task for all device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='ap_reboot',
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now',
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),
    '07.03.04.01': (
      [ 'TCID:%(tcid)s - GA create Configuration Upgrade task for his own device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='cfg_upgrade',
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            ],
            tmpl=dict( # for cfg_upgrade only
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))
            ),
            task=dict(
                task_name='2942',
                #template_name='', # update later
                template_model='zf2942'.upper(),
                provision_to=dict(device='192.168.20.180'), # get this by model
            ),
        ),
      ],
    ),
    '07.03.04.02': (
      [ 'TCID:%(tcid)s - GA create Factory Reset task for his own device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='factory_reset',
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now', reboot='True',
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),
    '07.03.04.03': (
      [ 'TCID:%(tcid)s - GA upgrade firmware for his own device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='fw_upgrade',
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now',
                zf2942_fw='.*8.2.0.0.18.*', # get this by model
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),

    '07.03.04.04': (
      [ 'TCID:%(tcid)s - GA create Reboot task for his own device groups',
        'FM_DA_Provisioning',
        dict(
            testcase='ap_reboot',
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now',
                device=['192.168.20.180'], # get this by model
            ),
        ),
      ],
    ),

    '07.04.04.01': (
      [ 'TCID:%(tcid)s - GO can not create template',
        'FM_DA_Provisioning',
        dict(
            testcase='cfg_upgrade',
            user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            ],
            tmpl=dict( # for cfg_upgrade only
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))
            ),
            task=dict(
                task_name='2942',
                #template_name='', # update later
                template_model='zf2942'.upper(),
                provision_to=dict(device='192.168.20.180'), # get this by model
            ),
            is_create=False,
        ),
      ],
    ),
    '07.04.04.02': (
      [ 'TCID:%(tcid)s - GO can not create Configuration Upgrade task',
        'FM_DA_Provisioning',
        dict(
            testcase='cfg_upgrade',
            user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            ],
            tmpl=dict( # for cfg_upgrade only
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))
            ),
            task=dict(
                task_name='2942',
                #template_name='', # update later
                template_model='zf2942'.upper(),
                provision_to=dict(device='192.168.20.180'), # get this by model
            ),
            is_create=False,
            is_tmpl_create=False,
        ),
      ],
    ),
    '07.04.04.03': (
      [ 'TCID:%(tcid)s - GO can not create Firmware Upgrade task',
        'FM_DA_Provisioning',
        dict(
            testcase='fw_upgrade',
            user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
            dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
            task=dict(
                task_name='2942', schedule='now',
                zf2942_fw='.*8.2.0.0.18.*', # get this by model
                device=['192.168.20.180'], # get this by model
            ),
            is_create=False,
        ),
      ],
    ),
}


def fill_tc_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    #log(tc[0])
    return tc


def define_ts_cfg(**kwa):
    '''
    kwa:    models, testbed
    return: (testsuite name, testcase configs)
    '''
    test_cfgs = {}
    for tcid in tc_templates:
        for tc_tmpl in tc_templates[tcid]:
            tc = copy.deepcopy(tc_tmpl)
            fill_tc_cfg(tc, dict(tcid = tcid,))
            test_cfgs[re.search('TCID:(.*?) -', tc[0]).group(1)] = tc
    keys = test_cfgs.keys()
    keys.sort()
    return get_testsuitename('fm_delegated_admin'), [test_cfgs[k] for k in keys]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
