"""
This module is supported to do a backup action on ZD

   tea.py zd_backup [ip_addr=192.168.0.2] [username=admin] [password=admin]
                   | [debug=True|False]

   Parameters:
       ip_addr :               IP address of the Zone Director
       username/password:      ZD's login username/password
       debug:                  True|False (turn on|off the debug mode)

   Examples:
       tea.py zd_backup
       tea.py zd_backup ip_addr=192.168.0.2 debug=False

"""

from pprint import pprint, pformat
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
    zd = ZoneDirector()
    zd.start()

    return zd

def main(**kwargs):
    mycfg = {'debug': False}
    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin'}

    for k, v in kwargs.items():
        if zdcfg.has_key(k):
            zdcfg[k] = v
        if mycfg.has_key(k):
            mycfg[k] = v

    if mycfg['debug']: bugme.pdb.set_trace()

    zd = create_zd(zdcfg)

    try:
        bak_file = ADMIN.backup(zd)
    except Exception, e:
        return ('FAIL', '[BACKUP ERROR]: %s' % e.message)

    return ('PASS', 'The ZD configuration backup successfully at "%s"' % bak_file)

