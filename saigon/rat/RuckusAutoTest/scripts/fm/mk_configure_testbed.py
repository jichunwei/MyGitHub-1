'''
Steps
1. make the testbed with given info
2. call all the addtestsuite scripts sequentially

'''
import sys
import lib_mk_testbed as ltb
from RuckusAutoTest.common import lib_KwList as kwlist


testbed_info = dict(
    name='configure',
    imported_testsuites = [
        dict(ts='ats_FM_ApReboot', ignoreModel=False),
        dict(ts='ats_FM_FactoryReset', ignoreModel=False),
        dict(ts='ats_FM_CfgTemplate', ignoreModel=False),
        dict(ts='ats_FM_CfgUpgrade_2', ignoreModel=False),
        dict(ts='ats_FM_CfgUpgrade', ignoreModel=False),
        dict(ts='ats_FM_ManageFirmwares', ignoreModel=False),
        dict(ts='ats_FM_FwUpgrade', ignoreModel=False),
        dict(ts='ats_AP_FwUpgrade', ignoreModel=False),
        dict(ts='ats_FM_Admin', ignoreModel=True),
        dict(ts='ats_FM_AdminUser', ignoreModel=True)
    ],
    device='APs',
    ignoreModel=False,
    ftp=dict(username='root',passwd='lab4man1'),
    is_interactive=False,
    usage=
'''
[HELP] This program help you to create tesbed and its testsuites
It has 2 modes: automatic and interactive

For ex:
 - Run in automatic mode, add all testscript into configure testbed,
   ftp argument include username and password for ftp protocol
     python mk_configure-testbed.py is_interactive=False fpt=[]
- Run in automatic mode, add all testscript into configure testbed,
   ftp protocol will get default value
     python mk_configure-testbed.py is_interactive=False
- Run in interactive mode
     python mk_configure-testbed.py is_interactive=True
''',
)


if __name__ == '__main__':
    testbed_info['input'] = kwlist.as_dict(sys.argv[1:])
    ltb.define_logical_testbed(**testbed_info)

