'''
@author: An Nguyen
@since: Mar, 2013

Description: This script is used to configure syslog in ZD CLI. Support from 9.6 builds.

'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class CB_ZD_CLI_Configure_Syslog(Test):
    def config(self, conf):
        self._init_test_parameters(conf)
        if self.conf['backup']:
            self._backup_syslog_cfg()
        self._retrieve_carribag()

    def test(self):
        self._configure_syslog()
        
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        self._update_carribag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'syslog_cfg': {},
                     'restore': False,
                     'backup': False}
        self.conf.update(conf)
        
        self.syslog_cfg = self.conf['syslog_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        if self.conf['restore']:
            self.syslog_cfg = self.carrierbag.get('bak_syslog_info')
    
    def _update_carribag(self):
        self.carrierbag['syslog_cfg'] = self.syslog_cfg
        
    def _backup_syslog_cfg(self):
        self.carrierbag['bak_syslog_info'] = lib.zdcli.syslog.get_syslog_config(self.zdcli)
        
    def _configure_syslog(self):
        if not self.syslog_cfg:
            self.errmsg = 'There is no syslog_cfg [%s] defined. Please check!' % str(self.syslog_cfg)
        try:
            lib.zdcli.syslog.config_syslog(self.zdcli, **self.syslog_cfg)
            self.passmsg = '[Configure Syslog][PASSED]'            
        except Exception, e:
            self.errmsg = '[Configure Syslog][FAILED] %s' % e.message
            

