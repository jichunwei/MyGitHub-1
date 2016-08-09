"""
This module is supported to do a restore action on ZD

   tea.py zd_restore restore_file_path=c:\restore.bak [restore_type=restore_everything]
                    | [ip_addr=192.168.0.2] [username=admin] [password=admin]
                    | [debug=True|False]

   Parameters:
       restore_file_path:       The file path of the backup file
       restore_type:            The restore type (restore_everything|restore_everything_except_ip|restore_basic_config)
       ip_addr :                IP address of the Zone Director
       username/password:       ZD's login username/password
       debug:                   True|False (turn on|off the debug mode)

   Examples:
       tea.py zd_restore restore_file_path="C:\\Documents and Settings\\Anthony-Nguyen\\Desktop\\ruckus_db_121509_12_11.bak"
       tea.py zd_restore restore_file_path="C:\\Documents and Settings\\Anthony-Nguyen\\Desktop\\ruckus_db_121509_12_11.bak" ip_addr=192.168.0.2
"""

import logging

from RuckusAutoTest.components.lib.zd import admin_backup_restore_zd as ADMIN
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import lib_Debug as bugme

def create_zd(conf):
    logging.info("Starting up ZoneDirector [%s]" % conf['ip_addr'])
    cfg = dict(
        ip_addr='192.168.0.2',
        username='admin',
        password='admin',
        model='zd',
        browser_type='firefox',
    )
    cfg.update(conf)

    sm = SeleniumManager()
    zd = ZoneDirector(sm)
    zd.start()

    return zd

def main(**kwargs):
    mycfg = {'debug': False}
    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin'}
    rescfg = {'restore_file_path': '',
              'restore_type': 'restore_everything',
              'timeout': 120,
              'reboot_timeout': 180}

    for k, v in kwargs.items():
        if zdcfg.has_key(k):
            zdcfg[k] = v
        if mycfg.has_key(k):
            mycfg[k] = v
        if rescfg.has_key(k):
            rescfg[k] = v

    if mycfg['debug']: bugme.pdb.set_trace()

    zd = create_zd(zdcfg)

    try:
        ADMIN.restore(zd, **rescfg)
    except Exception, e:
        return ('FAIL', '[RESTORE ERROR]: %s' % e.message)

    return ('PASS', 'The ZD configuration restore successfully from "%s"' % rescfg['restore_file_path'])
