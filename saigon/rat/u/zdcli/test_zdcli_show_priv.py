'''
Created on 2010-8-26
@author: cwang@ruckuswireless.com
tea.py test_zdcli_show_priv te_root=u.zdcli
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
    print "==================show ap all==========================="
    data = zdcli.do_show('ap all')
    pprint(demo.parse(data))
    print "================go to cfg, and show aaa================="
    data = zdcli.do_show('aaa', go_to_cfg = True)
    pprint(demo.parse(data))
    data = zdcli.do_show('show ap', go_to_cfg = True)
    pprint(demo.parse(data))
    print "==================show wlan all========================="
    data = zdcli.do_show('show sysinfo')
    pprint(demo.parse(data))
    print "==================show test============================="
    try:
        data = zdcli.do_show('test')
        return ("FAIL", "Should raise an exception")    
    except Exception, e:
        logging.info(e.message)
    print "==================show sysinfo========================="

    return ("PASS", "all of commands perform correctly")

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