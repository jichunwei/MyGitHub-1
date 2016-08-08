"""
This module supports to do the administrator functions via ZD CLI.
"""

import time
import logging

from RuckusAutoTest.common.Ratutils import *

reboot_cmd = 'reboot'

########################################################################################
# PUBLIC SECSSION
########################################################################################

def reboot(zdcli, **kwargs):
    """
    In privileged mode do the "reboot" command.
    Waiting until the ZD boot up
    Re login to the ZD CLI
    """ 
    cfg = {'ping_timeout': 300,
           'bootup_timeout': 360,
           'print_out': False}
    if kwargs: cfg.update(kwargs)
    
    _execute_reboot_command(zdcli, **cfg)
    
    for i in range(30):
        if "Timeout" in ping(zdcli.conf['ip_addr']):
            logging.info("ZD[%s] is rebooting now" % zdcli.conf['ip_addr'])
            break
        else:
            if i == range(30)[-1]:
                raise Exception("ZD cannot reboot in more than 60 s")
            time.sleep(2)
    
    _ping_to_zd(zdcli, **cfg)
    
    _reconnect_to_zd(zdcli, **cfg)

def execute_reboot_command(zdcli, **kwargs):
    cfg = {'print_out': False}
    if kwargs: cfg.update(kwargs)
    
    _execute_reboot_command(zdcli, **cfg)


########################################################################################
# PRIVATE SECSSION
########################################################################################

def _execute_reboot_command(zdcli, **kwargs):
    """
    Go to the privileged commands and form the "reboot" command
    """
    cfg = {'timeout': 3,
           'print_out': False}    
    if kwargs: cfg.update(kwargs)
    
    zdcli.position_at_priv_exec_mode(cfg['timeout'], cfg['print_out'])
    logging.debug("[ZD CMD INPUT] %s" % reboot_cmd)
    zdcli.zdcli.write(reboot_cmd + '\n')
    time.sleep(5)

def _ping_to_zd(zdcli, **kwargs):
    cfg = {'ping_timeout': 1000}
    if kwargs: cfg.update(kwargs)
    
    start_time = time.time()
    ping_retries = 0
    zd_ip = zdcli.conf['ip_addr']
    while True:
        ping_retries += 1
        logging.debug('Ping to ZD[%s] - Retry %d' % (zd_ip, ping_retries))
        res = ping(zd_ip)
        run_time = time.time() - start_time
        if not 'Timeout' in res:
            logging.debug('ping to ZD[%s] successfully after %s seconds' % (zd_ip, run_time))
            break
        else:
            if run_time > cfg['ping_timeout']:
                msg = 'Can not ping to ZD[%s] successfully after %s seconds' % (zd_ip, run_time)
                logging.debug(msg)
                raise Exception(msg)
        time.sleep(5)
    
def _reconnect_to_zd(zdcli, **kwargs):
    cfg = {'bootup_timeout': 360}
    if kwargs: cfg.update(kwargs)
    
    start_time = time.time()
    retry = 1
    while True:
        runtime = time.time() - start_time
        logging.debug('Try to connect to Zone Director - Retry %s' % retry)
        retry += 1
        try:
            zdcli.zdcli.close()
            zdcli.initialize()
            break
        except:
            logging.debug('Logging to Zone Director failed')

        if runtime > cfg['bootup_timeout']:
            raise Exception('Could not access to the Zone Director after %s seconds' % runtime)
    
    logging.debug('Re connect to ZD CLI successfully after %s seconds' % runtime)    