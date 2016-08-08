'''
1.1.10.2. Administration - Users Testsuite

  1.1.10.2.4 Create many user(over 100 user accounts)
'''

import sys

from libFM_TestSuite import make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    return:
    - (testsuite name, testcase configs)
    '''
    return 'Administration - Users Testsuite', [[
        'TCID:01.01.10.02.04  Create many user(over 100 user accounts)',
        'FM_ManageUsers',
        dict(totalUsers=120, roles = ['Network Administrator', 'Group Administrator',
             'Group Operator', 'Device Operator'],),]]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
