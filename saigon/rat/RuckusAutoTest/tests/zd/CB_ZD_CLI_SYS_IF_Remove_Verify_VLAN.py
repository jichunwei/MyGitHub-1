'''
Created on 2011-2-23
@author: louis.lou@ruckuswireless.com
description:

'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sys_if
from RuckusAutoTest.components.lib.zd import system_zd
from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_CLI_SYS_IF_Remove_Verify_VLAN(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        logging.info('Get Switch port that connected to ZD')
        zd_mac = self.zd.mac_addr
        port = self.sw.mac_to_interface(zd_mac)
        
        try:
            sys_if._remove_vlan(self.zdcli)
        except Exception,e :
            pass
        
        logging.info("ZD is restarting, please wait...")
        self.sw.remove_interface_from_vlan(port,self.sys_if_conf['vlan_id'])
        self.sw.add_interface_to_vlan(port,self.sys_if_conf['vlan_id'])
        
        time.sleep(200)
        self.zd.login()
        
        cli_get = sys_if.get_sys_if_info(self.zdcli)
        gui_get = system_zd.get_device_ip_settings(self.zd)
        
        if cli_get['Management VLAN']['VLAN ID']:
            self.errmsg += '[ZDCLI Get]ZD Management VLAN [%s] expect [None]' %(cli_get['Management VLAN']['VLAN ID'])
        
        if gui_get['vlan']:
            self.errmsg += '[GUI Get] ZD Management VLAN [%s] expect[None] '%(gui_get['vlan'])
        
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         sys_if_conf={}
                         )
        
        self.conf.update(conf)
        self.sys_if_conf = self.conf['sys_if_conf']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.sw = self.testbed.components['L3Switch']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         