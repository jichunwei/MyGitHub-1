''' Model independent testcases '''

import sys
import copy
import re

from libFM_TestSuite import make_test_suite, get_testsuitename
from RuckusAutoTest.common.lib_KwList import as_dict

from RuckusAutoTest.components.lib.dev_features import FM as fmft


# model_map is in libFM_TestSuite.py
tc_templates = {
    '01.05.04.01': (
      [ 'TCID:%(tcid)s.01 - Super-user and operator adding (Network Administrator)',
        'FM_AdminAddUser',
        dict(
            user=dict(
                username='na',
                password='user',
                confirm_password='user',
                role=fmft.roles['network_admin'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.02 - Super-user and operator adding (Group Administrator)',
        'FM_AdminAddUser',
        dict(
            user=dict(
                username='ga',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_admin'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.03 - Super-user and operator adding (Group Operator)',
        'FM_AdminAddUser',
        dict(
            user=dict(
                username='go',
                password='user',
                confirm_password='user',
                role=fmft.roles['group_op'],
            ),
        ),
      ],
      [ 'TCID:%(tcid)s.04 - Super-user and operator adding (Device Operator)',
        'FM_AdminAddUser',
        dict(
            user=dict(
                username='do',
                password='user',
                confirm_password='user',
                role=fmft.roles['device_op'],
            ),
        ),
      ],
    ),
    '01.05.04.02': (
      [ 'TCID:%(tcid)s - Default super-user account',
        'FM_AdminCheckSuperUser',
        dict(
            acc=dict(
                password='user',
                confirm_password='user',
                # unchange-able:
                #username='',
                #role=fmft.roles['network_admin'],
            ),
        ),
      ],
    ),
    '01.05.04.03': (
      [ 'TCID:%(tcid)s.01 - Specific character check',
        'FM_AdminUserSpecialChars',
        dict(
            user=dict(
                username=r'user_<>~!#$%^*/\()?,:;\'`"',
                password='user',
                confirm_password='user',
                role=fmft.roles['network_admin'],
            ),
            is_create=False,
        ),
      ],
      [ 'TCID:%(tcid)s.02 - Specific character check',
        'FM_AdminUserSpecialChars',
        dict(
            user=dict(
                username=r'[{-@=&|+_+|&=@-}]',
                password='user',
                confirm_password='user',
                role=fmft.roles['network_admin'],
            ),
            is_create=True,
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
    return get_testsuitename('fm_admin_user'), [test_cfgs[k] for k in keys]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
