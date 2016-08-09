"""
author#cwang@ruckuswireless.com
2010-10-20
Description:
	This file is used for get all aaa servers.
Usage:
	tea.py get_all_aaa_servers te_root=u.zdcli.aaaservers.
"""

import logging
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zdcli import aaa_servers as svr_helper

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    return zdcli

def do_test(zdcli, **kwargs):
    svr_dict = svr_helper.get_all_aaa_servers(zdcli)
    if svr_dict.has_key('AAA'):	    
       return ('PASS', 'AAA servers [%s]' % svr_dict['AAA'])
    else:
       return ('PASS', 'AAA server is empty')


def do_clean_up():
    clean_up_rat_env()
    

def main(**kwargs):
    try:
        zdcli = do_config(**kwargs)        
        res = do_test(zdcli, **kwargs)         
        return res
    finally:
        do_clean_up()


def _chk_aaa_info(aaa_info, expect_svr_name):
    if not aaa_info.has_key('AAA'):
        return False
    else:
	aaa_dict = aaa_info['AAA']
	print pformat(aaa_dict)
	return True
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)
