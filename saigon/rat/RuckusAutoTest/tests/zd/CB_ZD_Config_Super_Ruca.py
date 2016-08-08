# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to set super ruca to specific attenuator value [db]
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import logging
import subprocess
from RuckusAutoTest.models import Test

class CB_ZD_Config_Super_Ruca(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
       
    def test(self):
        self._config_super_ruca()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Config Super Ruca %s to %s db' % (self.conf['ruca_id'], self.conf['db'])
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.conf = conf.copy()

    def _set_attenuator(self, id, db):
        if type(id) in (tuple, list):
            for idx in id:
                cmdline = 'rac -i%s -v%s' % (idx, db)
                logging.debug("set Attenuator cmd %s" % cmdline)
                output = subprocess.Popen(cmdline,  stdout=subprocess.PIPE).communicate()[0]
        else:
            cmdline = 'rac -i%s -v%s' % (id, db)
            logging.debug("set Attenuator cmd %s" % cmdline)
            output = subprocess.Popen(cmdline,  stdout=subprocess.PIPE).communicate()[0]
            
    def _config_super_ruca(self):
        self._set_attenuator(id=self.conf['ruca_id'], db=self.conf['db'])
