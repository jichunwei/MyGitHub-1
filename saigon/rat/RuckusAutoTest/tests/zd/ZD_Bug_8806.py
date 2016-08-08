# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods_Bugs as bust

class ZD_Bug_8806(Test):
    required_components = ['ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.cfg = dict(username = self.zd.username, password = self.zd.password, password2 = 'ruckus', timeout = 60, debug = 0)
        # radius AuthServ should not be exist; all data are for provision only
        self.cfg.update(dict(ras_addr = '192.168.0.252', ras_port = '1812', ras_secret = '1234567890'))
        self.cfg.update(dict(ras_username = 'ras.not.exist', ras_password = 'ras.not.exist', auth_serv = 'radius.admin'))
        self.cfg.update(dict(doFactoryDefault = False))
        self.cfg.update(conf)
        self.errmsg = ''

    def test(self):
        self._factory_defaultZoneDirector()
        self._changeAdminLocalPassword()
        self._create_auth_server()
        self._enableAdminExternalAuthServer()
        # If I can not ssh ZD; bug 8806 exists
        self._canSshZoneDirector()
        self._restoreZoneDirector()

        if self.errmsg:
            return (False, self.errmsg)
        else:
            return (True, "ZoneDirector [version %s] has not bugid 8806 issue." % self.version)

    def cleanup(self):
        pass

    def _factory_defaultZoneDirector(self):
        if not self.cfg['doFactoryDefault']:
            logging.info('[Bug8806 #01] Requested not to set ZoneDirector to factory default.')
            return
        logging.info('[Bug8806 #01] set ZoneDirector to factory default.')
        self.zd.do_login()
        self.zd.setup_wizard_cfg()

    def _changeAdminLocalPassword(self):
        logging.info('[Bug8806 #02] set ZoneDirector administrator withUser[%s %s]'
                    % (self.cfg['username'], self.cfg['password2']))
        bust.set_auth_info_local(self.zd, username = self.cfg['username'], password = self.cfg['password2'])
        self.zd.do_login()
        self.version = self.zd._get_version()['version']
        self.zd.logout()
        logging.info('[Bug8806 INFO] ZoneDirector software version is %s.'
                    % self.version)
        logging.info('[Bug8806 INFO] TestEngine should be able to ssh ZoneDirector withUser[%s %s]'
                    % (self.cfg['username'], self.cfg['password2']))
        zdssh = bust.login_zd(self.zd.ip_addr, self.cfg['username'], self.cfg['password2'], self.cfg['timeout'])
        if not zdssh:
            raise Exception('[Bug8806 #02] Cannot ssh to ZD[%s] withUser[%s %s]'
                           % (self.zd.ip_addr, self.cfg['username'], self.cfg['password2']))
        zdssh.close()

    def _create_auth_server(self):
        logging.info('[Bug8806 #03] Create an AAA server entry named %s.' % (self.cfg['auth_serv']))
        self.zd.create_radius_server(self.cfg['ras_addr'], self.cfg['ras_port'], self.cfg['ras_secret'], self.cfg['auth_serv'])

    def _enableAdminExternalAuthServer(self):
        logging.info("[Bug8806 #04] Set Administrator to user AuthServ[%s]; but don't change password."
                    % (self.cfg['auth_serv']))
        bust.set_auth_info_external(self.zd, self.cfg['auth_serv'], username = None, password = None)

    def _canSshZoneDirector(self):
        logging.info('[Bug8806 INFO] TestEngine should be able to ssh ZoneDirector withUser[%s %s]'
                    % (self.cfg['username'], self.cfg['password2']))
        self.errmsg = ''
        zdssh = bust.login_zd(self.zd.ip_addr, self.cfg['username'], self.cfg['password2'], self.cfg['timeout'])
        if not zdssh:
            self.errmsg = '[Bug8806 BUSTERED] ZoneDirector [version %s] has bugid 8806 -- [Step #4] Cannot ssh to ZD[%s] withUser[%s %s]' \
                        % (self.version, self.zd.ip_addr, self.cfg['username'], self.cfg['password2'])
            # restart ZD to recover it
            logging.info(self.errmsg)
            self.ap0, self.ap1 = bust.restart_zd(self.zd, True)
        else:
            zdssh.close()

    def _restoreZoneDirector(self):
        logging.info('[Bug8806 INFO] restore ZoneDirector to withUser[%s %s]'
                    % (self.cfg['username'], self.cfg['password']))
        bust.set_auth_info_local(self.zd, username = self.cfg['username'], password = self.cfg['password'])
        self.zd.delete_auth_server(self.cfg['auth_serv'])

