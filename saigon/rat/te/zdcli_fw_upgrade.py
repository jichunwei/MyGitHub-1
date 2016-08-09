"""
This module is supported to do a backup action on ZD

   tea.py zdcli_fw_upgrade [ip_addr=192.168.0.2] [username=admin] [password=admin]
                   | [server_ip=192.168.0.20] [server_user=server_user_name] [server_password_name=server_password_name]
                   | [image_name=image_path_in_server] [production_mode=production_mode] [protocol:tftp|ftp]
                   | [debug=True|False]

   Parameters:
       ip_addr :                     IP address of the Zone Director
       username/password:            ZD's login username/password
       server_ip:                    IP of TFTP/FTP server
       server_user/server_password:  Server authentication user/password
       image_name:                   Image name/path in the server in format ".img"
       production_mode:              Production mode
       protocol:                     Upgrade protocol (TFTP|FTP)
       debug:                        True|False (turn on|off the debug mode)

   Examples:
       tea.py zdcli_fw_upgrade ip_addr=192.168.0.2 server_ip=192.168.0.2 
                               protocol=tftp image_name=zdbuild.img debug=False
                               shell_ky="!v54! L4Gv0dxO24mKElOTwXgbJXdG8Gd0wfUo"

"""
from pprint import pprint, pformat

import logging
import time

from RuckusAutoTest.components import ZoneDirectorCLI
from RuckusAutoTest.components import Helpers as lib

import RuckusAutoTest.common.lib_Debug as bugme

def create_zd(zdconf):
    logging.info("Starting up ZoneDirector [%s]" % zdconf['ip_addr'])
    zdcli = ZoneDirectorCLI.ZoneDirectorCLI(zdconf)
    return zdcli

def main(**kwargs):
    mycfg = {'debug': False}
    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin',
             'shell_key': '',
             }
    fw_upgrade_cfg = {
             'protocol': '',
             'server_ip': '',
             'server_user': '',
             'server_password': '',
             'image_name': '',
             'production_mode': '',
             'reboot_timeout': 1000,
             }

    for k, v in kwargs.items():
        if zdcfg.has_key(k):
            zdcfg[k] = v
        if mycfg.has_key(k):
            mycfg[k] = v
        if fw_upgrade_cfg.has_key(k):
            fw_upgrade_cfg[k] = v

    if mycfg['debug']: bugme.pdb.set_trace()

    zdcli = create_zd(zdcfg)

    start_time = time.time()
    logging.info(zdcli.sysinfo)

    try:
        logging.debug('[CURRENT ZD INFO] %s' % zdcli.sysinfo)
        logging.info('Upgrade Zone Director firmware using image: %s' % fw_upgrade_cfg['image_name'])
        lib.zdcli.debug.fw_upgrade(zdcli, **fw_upgrade_cfg)
        logging.debug('[CURRENT ZD INFO] %s' % zdcli.sysinfo)
    except Exception, e:
        return ('FAIL', '[FWUPGRADE ERROR]: %s' % e.message)
    upgrade_time = time.time() - start_time

    return ('PASS', 'Zone Director is upgraded successfully after % seconds' % upgrade_time)