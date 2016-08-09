'''
Created on 2010-8-26
@author: cwang@ruckuswireless.com

tea.py test_zdcli_show_cfg te_root=u.zdcli
'''
import logging
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.lib.zdcli import output_as_dict as demo
from pprint import pprint

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    args = dict()
    args.update(kwargs)
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    return zdcli

def do_test(zdcli, **kwargs):
    
    print "==================create aaa test2========================"
    cmd_block = '''
    aaa test2
    type ad
    ip-addr 192.168.0.252 port 389
    exit
    '''
    zdcli.do_cfg(cmd_block)
    print "==================aaa show================================="
    _test_aaa_show(zdcli)
    print "==================interface show==========================="
    _test_sys_if_show(zdcli)
    _test_sys_if(zdcli)

    return ("PASS", "all of commands perform correctly")

def _test_aaa_show(zdcli):
    data = zdcli.do_cfg_show('aaa test2')
    pprint(demo.parse(data))    

def _test_sys_if_show(zdcli):
    cmd_block = '''
    system
        interface
        show
    '''
    data = zdcli.do_cfg_show(cmd_block)
    sys_if_data = demo.parse(data)
    pprint(sys_if_data)

def _test_sys_if(zdcli):
    cmd_block = '''
    system
        interface
    '''
    data = zdcli.do_cfg_show(cmd_block)
    sys_if_data = demo.parse(data)
    print(sys_if_data)    
   
def do_clean_up(zdcli):
    try:
        del(zdcli)        
    except:
        pass

def main(**kwargs):
    try:
        zdcli = do_config(**kwargs)
        res = do_test(zdcli, **kwargs)         
        return res
    finally:
        do_clean_up(zdcli)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)