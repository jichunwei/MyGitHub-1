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

class CB_ZD_CLI_Set_Verify_SYS_IF_Vlan(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        
        logging.info('Get Switch port that connected to ZD')
        zd_mac = self.zd.mac_addr
        port = self.sw.mac_to_interface(zd_mac)
        
        logging.info("Set system interface manage VLAN %s" % (self.sys_if_conf['vlan_id']))
        try:
            sys_if._set_vlan(self.zdcli, self.sys_if_conf)
        except Exception,e:
            pass
        
        self.sw.add_interface_to_vlan(port,self.sys_if_conf['vlan_id'],tagging = True)
        
        logging.info("ZD is restarting, pleas wait ...")
        time.sleep(200)
        self.zd.login()
        
        cli_get = sys_if.get_sys_if_info(self.zdcli)
        gui_get = system_zd.get_device_ip_settings(self.zd)
        if str(cli_get['Management VLAN']['VLAN ID']) != str(self.sys_if_conf['vlan_id']):
            self.errmsg += '[ZDCLI Get]ZD Management VLAN [%s] expect [%s]' %(cli_get['Management VLAN']['VLAN ID'],self.sys_if_conf['vlan_id'])
        
        if str(gui_get['vlan']) != str(self.sys_if_conf['vlan_id']):
            self.errmsg += '[GUI Get] ZD Management VLAN [%s] expect[%s] '%(gui_get['vlan'],self.sys_if_conf['vlan_id'])
        
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
                         sys_if_conf = {}
                         )
        
        self.conf.update(conf)
        self.sys_if_conf = conf['sys_if_conf']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.sw = self.testbed.components['L3Switch']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         