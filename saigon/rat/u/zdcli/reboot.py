"""
This tea program supports to do the reboot ZD in looping with expected gap time.

      tea.py reboot | [loop_times=the-expected-times-to-reboot][gap_time=the_time_between_each_reboot_actions]
                    | [ip_addr=192.168.0.2] [username=admin] [password=admin]
                    | [debug=True|False]

Example: tea.py u.zdcli.reboot ip_addr=192.168.0.2 loop_times=3 gap_time=10
"""

import time
import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import administrator_functions as zdcli_admin    

mycfg = {'debug': False}
zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin'}
rescfg = {'loop_times': 1,
          'gap_time': 30,
          'ping_timeout': 300,
          'bootup_timeout': 120
         }

result = {'config': {},
          'result': '',
          'message': ''}

def do_config(**kwargs):
    for k, v in kwargs.items():
        if zdcfg.has_key(k):
            zdcfg[k] = v
        if mycfg.has_key(k):
            mycfg[k] = v
        if rescfg.has_key(k):
            rescfg[k] = v
    
    result['config'].update(mycfg)
    result['config'].update(zdcfg)
    result['config'].update(rescfg)
    
    zdcli = create_zd_cli_by_ip_addr(**zdcfg)
    return zdcli

def do_test(zdcli):
    loop = rescfg['loop_times']
    count = 0
    start_time = time.time()
    while count < loop:
        count += 1
        try:
            msg = '----------------------->%s<------------------------'
            ctime = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            log_msg = 'Reboot ZD [%s] the %d time at %s' % (zdcfg['ip_addr'], count, ctime)
            logging.debug(msg % log_msg)
            zdcli_admin.reboot(zdcli, **rescfg)
            
            if count < loop:
                logging.debug('Waiting %s seconds before the next rebooting' % rescfg['gap_time'])
            time.sleep(rescfg['gap_time'])
            
        except Exception, e:
            result['result'] = 'FAIL'
            result['message'] = '[REBOOT THE %d TIME FAILED] %s' % (count, e.message)
            return result
    
    total_time = time.time() - start_time
    msg = 'Reboot ZD [%s] by %d times in %s seconds without issues' % (zdcfg['ip_addr'], count, total_time)
    logging.debug(msg)
    result['result'] = 'PASS'
    result['message'] = msg
    return result    

def do_clean_up(zdcli):
    try:
        del(zdcli)        
    except:
        pass

def main(**kwargs):
    try:
        zdcli = do_config(**kwargs)
        res = do_test(zdcli)         
        return res
    finally:
        do_clean_up(zdcli)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)