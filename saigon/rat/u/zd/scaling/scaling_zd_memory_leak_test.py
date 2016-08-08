'''
Created on 2010-6-18

@author: cwang@ruckuswireless.com
'''
import time
import logging

from RuckusAutoTest.components.lib.zd import node_zd
from u.zd.scaling.lib import scaling_utils
from u.zd.scaling.lib import scaling_zd_lib 

def do_config(**kwargs):
    args = dict()
    args.update(kwargs)
    zd = scaling_utils.create_zd(**args)
    return zd 

def do_test(zd, **kwargs):
    cfg = dict(total_time=3600*24, interval_time=60*30, timeout=1800)
    cfg.update(kwargs)    
    ap_list = scaling_zd_lib.resolve_verify_all_aps(zd)
    cnt = 0
    start_time = time.time()
    while time.time()-start_time < cfg['total_time']:
        node_zd.restart_zd(zd, z_pause4Confirmation=5, z_pause4ZDRestart = 10)
        cnt += 1
        internal_start_time = time.time()
        zd_cli = scaling_utils.create_zd_cli(**cfg)
        res = scaling_zd_lib.check_all_aps_status_from_cmd(zd_cli, ap_list, time_out=cfg['timeout'], chk_mac=True)
        if not res:
            raise Exception("some of ap haven't reconnected after wait for %d" % cfg['timeout'])
        
        internal_end_time = time.time()
        if internal_end_time-internal_start_time < cfg['interval_time']:
            span =  cfg['interval_time']-(internal_end_time-internal_start_time)
            logging.info('waiting for %ds' % span)            
            time.sleep(span)
        
    return ["PASS", "system reboot cnt[%d], running time[%d] per [%d]" %(cnt, cfg['total_time'], cfg['interval_time'])]
    
def do_clean_up(zd):
    zd.s.shut_down_selenium_server()

def usage():
    '''    
        Description:
            Loop-repeat restart ZoneDirector in scaling ENV etc.
        Prerequisites:
          1) TFTP server is runing at your ENV, "install_apimg.sh" script and "rcks_fw.bl7" 
          image exist at TFTP server root folder
          2) All of SimAPs are running at your ENV and all of them are connected. 
        usage:
            tea.py <scaling_zd_repeat_restart key/value pair> ...
            
            where <scaling_zd_repeat_restart key/value pair> are:
              ip_addr        :     'ipaddr of ZoneDirector'
              username       :     'uername of ZoneDirector'
              password       :     'password of ZoneDirector'
                            
            notes:
        Examples:
            tea.py scaling_zd_memory_leak_test te_root=u.zd.scaling 
            tea.py scaling_zd_memory_leak_test te_root=u.zd.scaling 
            tea.py scaling_zd_memory_leak_test te_root=u.zd.scaling ip_addr='192.168.0.2' username='admin' password='admin'   
    '''

def main(**kwargs):
    mycfg = dict(total_time=60*24, 
                 interval_time=100, 
                 timeout=1800,
                 debug=False, 
                 ip_addr='192.168.0.2',
                 username='admin',
                 password='admin',)
    mycfg.update(kwargs)
    zd = do_config(**mycfg)
    try:
                
        res = do_test(zd, **mycfg)
        
        return res        
    
    finally:
        do_clean_up(zd)


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)