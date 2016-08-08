'''
Steps
1. make the testbed with given info
2. call all the addtestsuite scripts sequentially

'''
import sys
import lib_mk_testbed as ltb
from RuckusAutoTest.common import lib_KwList as kwlist


testbed_info = dict(
    name='fm_zd',
    imported_testsuites = [
        dict(ts='ats_FM_ZdCloning', ignoreModel=False),
        dict(ts='ats_FM_ManageZdCfg', ignoreModel=False),
        ],
    device='ZDs',
    map_path='D:\map1.png',
    is_interactive=False,
    usage=
'''
[HELP] This program help you to create tesbed and its testsuites
It has 2 modes: automatic and interactive

For ex:
- Run in automatic mode, add 'ats_FM_ZdCloning', 'ats_FM_ManageZdCfg' into zds testbed,
   map_path is used for FM_ZdCloning
     python mk_zds-testbed.py is_interactive=False map_path='D:\map1.png'
- Run in automatic mode, add 'ats_FM_ManageZdCfg' into zds testbed
     python mk_zds-testbed.py is_interactive=False
- Run in interactive mode
     python mk_zds-testbed.py is_interactive=True
''',
)

if __name__ == '__main__':
    testbed_info['input'] = kwlist.as_dict(sys.argv[1:])
    ltb.define_logical_testbed(**testbed_info)
    exit()


