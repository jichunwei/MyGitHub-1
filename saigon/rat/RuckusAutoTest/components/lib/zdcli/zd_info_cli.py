'''
This module define the ZD system info

'''

import logging
import os

from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.utils import compare_dict_key_value
from RuckusAutoTest.common import utils

SHOW_ZD_ETH_INFO= 'show ethinfo'

def show_zd_eth_info(zdcli):
    cmd_block = SHOW_ZD_ETH_INFO
    logging.info("======show ZD Ethernet info==========")

    info = zdcli.do_show(cmd_block)
    
    logging.info('The result\n:%s',info)
    zd_ethinfo_on_cli = output.parse(info)
    
    return zd_ethinfo_on_cli


