'''
@author: An Nguyen; an.nguyen@ruckuswireless.com
@since: July 2012

This module includes the functions to execute the 'wlaninfo' command under ZDCLI shell mode.
For the old module that support 'wlaninfo' command please refer components/lib/zd/cli_zd for more information

'''

import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.utils import compare_dict_key_value
from RuckusAutoTest.common import utils

WLANINFO_CMD = 'wlaninfo'

#
# Public functions
#

def wlaninfo_a(zdcli, **kwargs):
    cfg = {'ap_mac': ''}
    cfg.update(kwargs)
    
    if cfg['ap_mac']:
        cmd = '%s -a %s' % (WLANINFO_CMD, cfg['ap_mac'])
    else:
        cmd = '%s -A' % (WLANINFO_CMD)
    
    info = zdcli.do_shell_cmd(cmd)
    return info



#
# Private functions
#