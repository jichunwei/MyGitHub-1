"""
Copyright (C) 2010 Ruckus Wireless, Inc.
@author: An Nguyen - an.nguyen@ruckuswireless.com
@since: Oct 2010

This tea program supports to do the reboot multi ZD in looping with expected gap time.

      tea.py multi_zd_reboot_cycle_testing | [loop_times=the-expected-times-to-reboot][gap_time=the_time_between_each_reboot_actions]
                                           | [debug=True|False]

Example: tea.py u.zdcli.reboot_cycle_testing cycle_number=3 interval=10

"""

import time
import logging

from pprint import pformat

from RuckusAutoTest.common.Ratutils import ping
from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import administrator_functions as zd_cli_admin    

mycfg = {'debug': False}
testcfg = {'duration': 86400,
           'cycle_number': 1000,
           'interval': 1,
           'ping_timeout': 200,
           'access_retry': 5,
           }

zdcfg = {
         '172.18.36.11': {'username': 'admin',
                         'password': 'admin',
                         'shell_key': '!v54! SCppTEY7krZPPD1XSNb4GeV8Bh44P9cZ',
                         'obj': None,
                         },         
         '172.18.36.12': {'username': 'admin',
                          'password': 'admin',
                          'shell_key': '!v54! R@VFeYBdt7wq51uJ3MR3Sbo2bNeeNsoT',
                          'obj': None,
                         },
         '172.18.36.13': {'username': 'admin',
                         'password': 'admin',
                         'shell_key': '!v54! mtSR4relIQbTEdiGrBKiTuQNiH4wU03C',
                         'obj': None,
                        },
         '172.18.36.14': {'username': 'admin',
                          'password': 'admin',
                          'shell_key': '!v54! ZjwyiRh6o2DDyNztdqHYEzYdo@Exx5Ud',
                          'obj': None,
                         },
         '172.18.36.15': {'username': 'admin',
                         'password': 'admin',
                         'shell_key': '!v54! ADl2vIltApuQl3c7jKN.l2W0tXU0p5oR',
                         'obj': None,
                        },
        }

reboot_log_msg = '[CYCLE %s] Reboot device %s %s at %s'
ping_log_msg = '[CYCLE %s] Ping to device %s %s after %s seconds'
access_log_msg = '[CYCLE %s] Access to device %s %s after %s retri(es)'
verify_log_msg = '[CYCLE %s] Verify device [%s] info %s'
interval_waiting_msg = '[SOFT REBOOT TEST] ----------- Waiting for %s seconds for next reboot ------------'

def _ping_to_zd(zd_ip):
    res = ping(zd_ip)
    return ('Timeout' not in res)

def _verify_zd(zd_cli, expected_info):
    current_info = _get_zd_expected_sys_info(zd_cli)
    return (current_info == expected_info)
    
def _get_zd_expected_sys_info(zd_cli):
    un_verified_info = ['Memory Utilization']
    for key in un_verified_info:
        if zd_cli.sysinfo.has_key(key):
            logging.debug('%s: %s' % (key, zd_cli.sysinfo.pop(key)))
    
    return zd_cli.sysinfo

def _access_zd(cfg, zd_ip):
    zd_cli = None
    retry = 0
    while retry < cfg['testcfg']['access_retry']:
        retry +=1
        logging.debug('Access to device %s - Retry %s' % (zd_ip, retry))
        try:
            zd_cli = create_zd_cli_by_ip_addr(ip_addr = zd_ip, 
                                              username = cfg['zdcfg'][zd_ip]['username'],
                                              password = cfg['zdcfg'][zd_ip]['password'],
                                              shell_key = cfg['zdcfg'][zd_ip]['shell_key'])
            if zd_cli:
                break
        except:
            pass
    
    return zd_cli, retry 
    
def _do_reboot_test(cfg, verify_zd_ip_list, idx=1):
    """
    """
    start_time = time.time()
    ping_retry = 0
    for zd_ip in verify_zd_ip_list:

        if cfg['zdcfg'][zd_ip]['obj']:
            logging.debug(reboot_log_msg % (idx, zd_ip,'started', time.strftime("%Y%m%d%H%M")))
            zd_cli_admin.execute_reboot_command(cfg['zdcfg'][zd_ip]['obj'])
            del(cfg['zdcfg'][zd_ip]['obj'])
        else:
            verify_zd_ip_list.remove(zd_ip)
            
    while verify_zd_ip_list:        
        ping_retry += 1 
        for zd_ip in verify_zd_ip_list:
            logging.debug('Ping to device %s - Retry %s' % (zd_ip, ping_retry))
            if _ping_to_zd(zd_ip):
                running_time = time.time() - start_time
                if idx not in cfg['res']['log'][zd_ip]['ping_passed_at']:
                    cfg['res']['log'][zd_ip]['ping_passed_at'].append(idx)
                logging.debug(ping_log_msg % (idx, zd_ip, 'PASSED', running_time))
                time.sleep(5)
                
                cfg['zdcfg'][zd_ip]['obj'], retry = _access_zd(cfg, zd_ip)
                if not cfg['zdcfg'][zd_ip]['obj']:
                    verify_zd_ip_list.remove(zd_ip)
                    cfg['res']['log'][zd_ip]['access_failed_at'].append(idx)    
                    logging.debug(access_log_msg % (idx, zd_ip, 'FAILED', retry))               
                    continue               
                                
                cfg['res']['log'][zd_ip]['access_passed_at'].append(idx)
                logging.debug(access_log_msg % (idx, zd_ip, 'PASSED', retry)) 
                
                logging.debug('Verify system info of device %s' % zd_ip)
                if _verify_zd(cfg['zdcfg'][zd_ip]['obj'], cfg['res']['log'][zd_ip]['default_info']):
                    cfg['res']['log'][zd_ip]['verify_passed_at'].append(idx)
                    logging.debug(verify_log_msg % (idx, zd_ip, 'PASSED'))
                else:
                    cfg['res']['log'][zd_ip]['verify_failed_at'].append(idx)
                    logging.debug(verify_log_msg % (idx, zd_ip, 'FAILED'))
                    logging.debug('Current system info: \n %s' % pformat(cfg['zdcfg'][zd_ip]['obj'].info))
                    logging.debug('Expected system info: \n %s' % pformat(cfg['res']['log'][zd_ip]['default_info']))

                verify_zd_ip_list.remove(zd_ip)               
            else:
                running_time = time.time() - start_time
                if running_time  > cfg['testcfg']['ping_timeout']:
                    verify_zd_ip_list.remove(zd_ip)
                    cfg['zdcfg'][zd_ip]['obj'] =  None
                    cfg['res']['log'][zd_ip]['ping_failed_at'].append(idx)
                    logging.debug(ping_log_msg % (idx, zd_ip, 'FAILED', running_time))
    
    cfg['res']['completed_cycle'] +=1

def _get_defaut_zds_sys_info(cfg):
    for zd_ip in cfg['res']['log'].keys():
        zd_cli, retry = _access_zd(cfg, zd_ip)
        if not zd_cli:
            cfg['zdcfg'][zd_ip]['obj'] = None
            continue
        
        cfg['zdcfg'][zd_ip]['obj'] = zd_cli
        cfg['res']['log'][zd_ip]['default_info'] = _get_zd_expected_sys_info(zd_cli)
    
#
# Test functions
#

def do_config(**kwargs):
    cfg = {'mycfg': {},
           'testcfg': {},
          }
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        if testcfg.has_key(k):
            testcfg[k] = v
    
    cfg['mycfg'].update(mycfg)
    cfg['testcfg'].update(testcfg)
    cfg['zdcfg'] = zdcfg.copy()
    cfg['res'] = {'result': '',
                  'message': '',
                  'completed_cycle': 0,
                  'log': {}}
    
    for zd_ip in cfg['zdcfg'].keys():
        cfg['res']['log'][zd_ip] = {'verify_passed_at': [],
                                    'verify_failed_at': [],
                                    'ping_passed_at': [],
                                    'ping_failed_at': [],
                                    'access_passed_at': [],
                                    'access_failed_at': []}
    
    return cfg

def print_out_result(result):
    logging.info('\n\n\nPOWER CYCLE TESTING ........................................................................')    
    logging.info('RESULT .....................................................................................')
    logging.info(result['result'])
    logging.info(result['message'])
    for zd_ip in result['log'].keys():
        ping_msg = 'Ping %s times successfully, %s failed.' % (len(result['log'][zd_ip]['ping_passed_at']), 
                                                               len(result['log'][zd_ip]['ping_failed_at']))
        access_msg = 'Access %s times successfully, %s failed.' % (len(result['log'][zd_ip]['access_passed_at']), 
                                                                   len(result['log'][zd_ip]['access_failed_at']))
        verify_msg = 'Verify system info %s times successfully, %s failed.' % (len(result['log'][zd_ip]['verify_passed_at']), 
                                                                               len(result['log'][zd_ip]['verify_failed_at']))
        logging.debug('............................................................................................')
        logging.info(pformat(result['log'][zd_ip]['default_info'], 4, 20))
        logging.info(ping_msg)
        logging.info(access_msg)
        logging.info(verify_msg)
        logging.debug('............................................................................................\n\n\n')
   
def do_test(cfg):
    # Access to all device to get the before test info
    logging.info('The testing parameters: \n %s' % pformat(cfg['testcfg']))
    logging.info('Following devices will be verify: \n %s' % pformat(zdcfg, 4, 120))
    _get_defaut_zds_sys_info(cfg)
    
    start_cycle_time = time.time()
    
    logging.info('[SOFT REBOOT TESTING] Starts at %s' % time.strftime("%Y%m%d%H%M"))
    cycle_idx = 0
    running_test_time = time.time() - start_cycle_time
    while cycle_idx < cfg['testcfg']['cycle_number'] and running_test_time <= cfg['testcfg']['duration']:
        cycle_idx += 1
        
        verify_zd_ip_list = [zd_ip for zd_ip in cfg['zdcfg'].keys() if cfg['zdcfg'][zd_ip]['obj']]
        if not verify_zd_ip_list:
            msg = 'Cycle %s - All devices are in trouble' % cycle_idx
            logging.debug(msg)
            cfg['res']['result'] = 'FAIL'
            cfg['res']['message'] = '[SOFT REBOOT TESTING] Stops after %s seconds at %s ' % (running_test_time, msg)
            return
        logging.info('[SOFT REBOOT TESTING] Starts cycle %s at %s' % (cycle_idx, time.strftime("%Y%m%d%H%M")))
        _do_reboot_test(cfg, verify_zd_ip_list, cycle_idx)
        
        running_test_time = time.time() - start_cycle_time
        
        logging.info(interval_waiting_msg % cfg['testcfg']['interval'])
        time.sleep(cfg['testcfg']['interval'])
        
    msg = 'Finishes at %s with %s reboot times in %s seconds'
    msg = msg % (time.strftime("%Y%m%d%H%M"), cycle_idx, running_test_time)
    
    cfg['res']['result'] = 'PASS'
    cfg['res']['message'] = '[SOFT REBOOT TESTING] %s' % msg
    print_out_result(cfg['res'])
    return cfg['res']

def do_clean_up(cfg):
    for zd_ip in cfg['zdcfg'].keys():
        try:
            del(cfg['zdcfg'][zd_ip]['obj'])
        except:
            pass

def main(**kwargs):
    try:
        conf = do_config(**kwargs)
        res = do_test(conf)         
        return res
    finally:
        do_clean_up(conf)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)
