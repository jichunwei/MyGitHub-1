import sys

from libFM_TestSuite import make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    return 'Additional Testcases', [
        ['TCID:01.04.06  Firmware Status > Model type & firmware version display'+\
         ', Consistency btw displayed devices & actual devices',
         'FM_InvZDDetails',
         {},
        ],
        ['TCID:01.02.01.02  ZoneDirector details display',
         'FM_CfgFwStatus',
         {},
        ],
    ]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
