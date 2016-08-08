'''
Created on 2010-12-29

@author: cherry.cheng@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as get_wlan

class CB_ZD_CLI_Remove_Wlans(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        if not self.wlan_name_list:
            self.wlan_name_list = get_wlan.get_all_wlan_name_list(self.zdcli)
            
        err_del_wlan = {}
        try:
            for wlan_name in self.wlan_name_list:
                logging.info("Delete the wlan %s via ZD CLI" % wlan_name)
                set_wlan.delete_wlan(self.zdcli, wlan_name)
                
                logging.info("Verify the wlan %s is deleted" % wlan_name)
                wlan_name_list_after_delete = get_wlan.get_all_wlan_name_list(self.zdcli)
                if wlan_name in wlan_name_list_after_delete:
                    errmsg = "Wlan %s is not deleted" % wlan_name
                    logging.error(errmsg)
                    err_del_wlan[wlan_name] = errmsg
                else:
                    logging.info('The wlan %s has been deleted successfully.' % wlan_name)
                    
            if err_del_wlan:
                self.errmsg = err_del_wlan
                
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'wlan_name_list': []}
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
        #@author: Jane.Guo @since: 2013-07-24 fix bug, first consider parameter, then get from carrier bag.
        self.wlan_name_list = []
        if self.conf.get('wlan_name_list'):
            self.wlan_name_list = self.conf['wlan_name_list']
        else:
            if self.carrierbag.has_key('wlan_name'):
                wlan_name = self.carrierbag['wlan_name']
                self.wlan_name_list = [wlan_name]
        
    def _update_carrier_bag(self):
        pass