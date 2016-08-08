import sys
import copy
import re

from libFM_TestSuite import make_test_suite, get_testsuitename
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.components.lib.dev_features import FM as fmft

# model_map is in libFM_TestSuite.py
tc_templates = {
    '07.01.01.01': (
      [ 'TCID:%(tcid)s.01 - SA create NA\GA\GO\OP (NA)',
        'FM_DA_AddUser',
        dict(
            test_user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - SA create NA\GA\GO\OP (GA)',
        'FM_DA_AddUser',
        dict(
            test_user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.03 - SA create NA\GA\GO\OP (GO)',
        'FM_DA_AddUser',
        dict(
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.04 - SA create NA\GA\GO\OP (OP)',
        'FM_DA_AddUser',
        dict(
            test_user=dict(
                username='do',   role=fmft.roles['device_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.01.01.02': (
      [ 'TCID:%(tcid)s.01 - GA create GO\OP (GO)',
        'FM_DA_AddUser',
        dict(
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - GA create GO\OP (GO)',
        'FM_DA_AddUser',
        dict(
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            test_user=dict(
                username='do',   role=fmft.roles['device_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.01.01.03': (
      [ 'TCID:%(tcid)s - Change user role and password should work properly',
        'FM_DA_EditUser',
        dict(
            create_user=dict(
                username='ga',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_admin'],
            ),
            user=dict(
                password='user1',
                confirm_password='user1',
                role=fmft.roles['group_op'],
            ),
        ),
      ],
    ),
    '07.01.02.01': (
      [ 'TCID:%(tcid)s.01 - SA delete NA\GA\GO\OP (NA)',
        'FM_DA_DeleteUser',
        dict(
            test_user=dict(
                username='na',
                password='user',
                confirm_password='user',
                role=fmft.roles['network_admin'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - SA delete NA\GA\GO\OP (GA)',
        'FM_DA_DeleteUser',
        dict(
            test_user=dict(
                username='ga',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_admin'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.03 - SA delete NA\GA\GO\OP (GO)',
        'FM_DA_DeleteUser',
        dict(
            test_user=dict(
                username='go',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_op'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.04 - SA delete NA\GA\GO\OP (OP)',
        'FM_DA_DeleteUser',
        dict(
            test_user=dict(
                username='do',
                password='user',
                confirm_password='user',
                role=fmft.roles['device_op'],
            ),
        ),
      ],
    ),

    '07.01.02.02': (
      [ 'TCID:%(tcid)s.01 - GA delete GO\OP (GO)',
        'FM_DA_DeleteUser',
        dict(
            user=dict(
                username='ga',
                password='user', confirm_password='user',
                role=fmft.roles['group_admin'],
            ),
            test_user=dict(
                username='go',
                password='user', confirm_password='user',
                role=fmft.roles['group_op'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - GA delete GO\OP (DO)',
        'FM_DA_DeleteUser',
        dict(
            user=dict(
                username='ga',
                password='user', confirm_password='user',
                role=fmft.roles['group_admin'],
            ),
            test_user=dict(
                username='do',
                password='user', confirm_password='user',
                role=fmft.roles['device_op'],
            ),
        ),
      ],
    ),
    '07.01.02.03': (
      [ 'TCID:%(tcid)s - GO can not delete OP',
        'FM_DA_DeleteUser',
        dict(
            user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
            test_user=dict(
                username='do',   role=fmft.roles['device_op'],
                password='user', confirm_password='user',
            ),
            is_delete=False,
            is_create_by_na=True, # need to create this account by na
        ),
      ],
    ),
    '07.01.02.04': (
      [ 'TCID:%(tcid)s - Any user can not delete self-account (GO)',
        'FM_DA_DeleteUser',
        dict(
            user=dict(
                username='go',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_op'],
            ),
            is_delete=False,
        ),
      ],
    ),
    '07.01.03.01': (
      [ 'TCID:%(tcid)s.01 - Only SA and NA can create device group(s) (SA)',
        'FM_DA_AddDeviceGroup',
        dict(
            dev_group=dict(groupname='sa_devgroup',),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - Only SA and NA can create device group(s) (NA)',
        'FM_DA_AddDeviceGroup',
        dict(
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='na_devgroup',),
        ),
      ],
      [ 'TCID:%(tcid)s.03 - Only SA and NA can create device group(s) (GA - negative test)',
        'FM_DA_AddDeviceGroup',
        # -- GA, GO, OP: NO creating
        dict(
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='ga_devgroup',),
            is_create=False,
        ),
      ],
    ),

    '07.01.04.01': (
      [ 'TCID:%(tcid)s.01 - SA\NA assign devices to device group(s) (SA)',
        'FM_DA_AddDeviceGroup',
        dict(
            dev_group=dict(groupname='sa_devgroup', matches=[dict(model='zf2942')],),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - SA\NA assign devices to device group(s) (NA)',
        'FM_DA_AddDeviceGroup',
        dict(
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
        ),
      ],
    ),

    '07.01.05.01': (
      [ 'TCID:%(tcid)s.01 - NA assign device group to GA\GO\OP (GA)',
        'FM_DA_AssignDeviceGroup',
        dict(
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
            test_user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - NA assign device group to GA\GO\OP (GO)',
        'FM_DA_AssignDeviceGroup',
        dict(
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.03 - NA assign device group to GA\GO\OP (OP)',
        'FM_DA_AssignDeviceGroup',
        dict(
            user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
            test_user=dict(
                username='do',   role=fmft.roles['device_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.01.05.02': (
      [ 'TCID:%(tcid)s.01 - GA assign device group to GO\OP (GO)',
        'FM_DA_AssignDeviceGroup',
        dict(
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='ga_devgroup', matches=[dict(model='zf7942')],),
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - GA assign device group to GO\OP (OP)',
        'FM_DA_AssignDeviceGroup',
        dict(
            user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            dev_group=dict(groupname='ga_devgroup', matches=[dict(model='zf7942')],),
            test_user=dict(
                username='do',   role=fmft.roles['device_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.02.01.01': (
      [ 'TCID:%(tcid)s - NA view all devices group in the network',
        'FM_DA_ViewDevices',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            #is_db_accessible=True,
        ),
      ],
    ),

    '07.03.01.01': (
      [ 'TCID:%(tcid)s - GA view his own devices group in the network',
        'FM_DA_ViewDevices',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.04.01.01': (
      [ 'TCID:%(tcid)s - GO view his own devices group in the network',
        'FM_DA_ViewDevices',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
        ),
      ],
    ),

    '07.02.02.01': (
      [ 'TCID:%(tcid)s - NA create auto-configuration rule from all device groups',
        'FM_DA_CreateAutoCfg',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='na',   role=fmft.roles['network_admin'],
                password='user', confirm_password='user',
            ),
            tmpl=dict(
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))),
            rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                      cfg_template_fm_name='t_2942'),
            #is_create=True,
        ),
      ],
    ),
    '07.03.02.01': (
      [ 'TCID:%(tcid)s - GA cannot create auto-configuration rule successfully',
        'FM_DA_CreateAutoCfg',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='ga',   role=fmft.roles['group_admin'],
                password='user', confirm_password='user',
            ),
            tmpl=dict(
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))),
            rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                      cfg_template_fm_name='t_2942'),
            is_create=False,
        ),
      ],
    ),
    '07.04.02.01': (
      [ 'TCID:%(tcid)s - GO can not create auto-configuration rule from his own device groups',
        'FM_DA_CreateAutoCfg',
        dict(
            dev_groups=[
                dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
                dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
            ],
            test_user=dict(
                username='go',   role=fmft.roles['group_op'],
                password='user', confirm_password='user',
            ),
            tmpl=dict(
                template_name='t_2942', template_model='zf2942',
                options=dict(device_general=dict(device_name='superdog'))),
            rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                      cfg_template_fm_name='t_2942'),
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
