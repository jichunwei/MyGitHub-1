"""
author#cwang@ruckuswireless.com
2010-10-20
Description:
	This file is used for get aaa server information by server_name.
Usage:
	tea.py get_aaa_server_by_name te_root=u.zdcli.aaaservers server_name='radius_server'.
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
    server_name = 'radius_server'
    if kwargs.has_key('server_name'):
        server_name = kwargs['server_name']
    
    logging.info('Try to search aaa server [%s]' % server_name)    
    svr_dict = svr_helper.get_aaa_server_by_name(zdcli, server_name)
    if _chk_aaa_info(svr_dict, server_name):
        return ('PASS', 'Get server [%s] information DONE!' % server_name)
    else:
	return ('FAIL', 'Get server [%s] information FAIL' % server_name)


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
