"""
Description: This script is used to create a new wlan group in zd.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Create_New_WlanGroup(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._createNewWlanGroup()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        if conf.has_key('add_wlan'):
            self.add_wlan=conf['add_wlan']
        else:
            self.add_wlan=True
            
        if conf.has_key('wlan_list'):
            self.wlan_list=conf['wlan_list']
        else:
            self.wlan_list=[]
        
        self.wgs_cfg = conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _createNewWlanGroup(self):
        logging.info('Create a new WLAN group in ZD via GUI with configuration:\n%s.' % pformat(self.wgs_cfg))
        
        try:
            wgs.create_new_wlan_group(self.zd, self.wgs_cfg,add_wlan=self.add_wlan,add_wlan_list=self.wlan_list)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        logging.info('Create the new WLAN group [%s] successfully!')    
        self.passmsg = 'Create the new WLAN group [%s] in ZD via GUI successfully' % self.wgs_cfg
