'''
Steps
1. make the testbed with given info
2. call all the addtestsuite scripts sequentially

'''
import sys
import lib_mk_testbed as ltb
from RuckusAutoTest.common import lib_KwList as kwlist

testbed_info = dict(
    name='dualband',
    imported_testsuites = [
        dict(ts='ats_FMDV_Dalmatian', ignoreModel=False),
        dict(ts='ats_FM_Dalmatian', ignoreModel=False),
        dict(ts='ats_FM_AutoCfgTest_2', ignoreModel=False),
        ],
    device='APs',
    is_interactive=False,
    usage=
'''
[HELP] This program help you to create tesbed and its testsuites
It has 2 modes: automatic and interactive

For ex:
 - Run in automatic mode, add all testscript into dualband testbed,
     python mk_dualband-testbed.py is_interactive=False
 - Run in interactive mode
     python mk_dualband-testbed.py is_interactive=True
''',
)

if __name__ == '__main__':
    testbed_info['input'] = kwlist.as_dict(sys.argv[1:])
    ltb.define_logical_testbed(**testbed_info)
    exit()

