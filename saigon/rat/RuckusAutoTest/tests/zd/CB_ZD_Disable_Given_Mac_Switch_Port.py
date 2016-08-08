# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
disable switch port connected to given mac
by West.li
"""

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import mesh
from RuckusAutoTest.components.lib.zdcli.sys_basic_info import get_zd_mac
import libZD_TestConfig as tconfig

class CB_ZD_Disable_Given_Mac_Switch_Port(Test):

    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
    def test(self):
        if self.not_test:
            return 'PASS','Mesh not enable,not disable ap mac'
        try:
            logging.info("Disable MAC: %s" % self.disable_mac_list)
            time.sleep(2)
            self._get_port_by_mac(self.disable_mac_list)
            time.sleep(2)
            disabled_int_list = self.sw.get_disabled_interface()
            self._port_list = list(set(self._port_list)-set(disabled_int_list))
            self._disable_sw_port(self._port_list)
            self._update_carrier_bag()
        except Exception, e:
            self.errmsg=e.message
        if self.errmsg:
            return 'FAIL',self.errmsg
        return 'PASS','disable port succ'
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('sw'):
            self.sw=self.carrierbag['sw']
        else:
            self.sw=self.testbed.components['L3Switch']
        if self.carrierbag.has_key('lower_mac_zd_mac'):
            self.lower_mac_zd_mac  = self.carrierbag['lower_mac_zd_mac']
        if self.carrierbag.has_key('higher_mac_zd_mac'):
            self.higher_mac_zd_mac = self.carrierbag['higher_mac_zd_mac']
    
        if self.carrierbag.has_key('lower_mac_zd') and self.carrierbag.has_key('active_zd'):
            if self.carrierbag['active_zd']==self.carrierbag['lower_mac_zd']:
                self.active_zd_mac=self.lower_mac_zd_mac
                self.standby_zd_mac=self.higher_mac_zd_mac
            else:
                self.active_zd_mac=self.higher_mac_zd_mac
                self.standby_zd_mac=self.lower_mac_zd_mac
            
    def _update_carrier_bag(self):
        if self.disableDevice == 'ap':
            if not self.carrierbag.has_key('disabled_ap_sw_port_list'):
                self.carrierbag['disabled_ap_sw_port_list']=[]
            self.carrierbag['disabled_ap_sw_port_list']+=self._port_list
        elif self.disableDevice == 'zd':
            if not self.carrierbag.has_key('disabled_zd_sw_port_list'):
                self.carrierbag['disabled_zd_sw_port_list']=[]
            self.carrierbag['disabled_zd_sw_port_list']+=self._port_list
            
        
    
    def _init_test_params(self, conf):
        self.errmsg=''
        self.conf=conf
        self.disable_mac_list = []
        if conf.has_key('disable_mac_list'):
            self.disable_mac_list=conf['disable_mac_list']
        self.disableDevice=conf['device']
        
        if conf.has_key('ap_tag'):
            if conf['ap_tag'] == 'all':
                self.disable_mac_list = self.testbed.get_aps_mac_list()
            elif type(conf['ap_tag']) != list:
                conf['ap_tag'] = [conf['ap_tag']]
                for ap_tag in conf['ap_tag']:
                    ap = tconfig.get_testbed_active_ap(self.testbed, ap_tag)
                    self.disable_mac_list.append(ap.base_mac_addr)
        
        if conf.has_key('zd'):
            self.disable_mac_list=[self.carrierbag[conf['zd']]]
            
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
            if self.conf['device']=='zd':
                self.disable_mac_list = [get_zd_mac(self.zdcli)]
        self.not_test = False
        if conf.get('for_mesh'):
            mesh_status = mesh.get_mesh_status(self.zdcli)
            if mesh_status=='Disabled':
                self.not_test = True
        
        
    def _get_port_by_mac(self,mac_list):
        self._port_list=[]
        mac_num=len(mac_list)
        macIdx=0
        while macIdx<mac_num:
            self._port_list+=[self.sw.mac_to_interface(mac_list[macIdx])]
            macIdx+=1
        logging.info('the port(s) below will be disabled:')
        for port in self._port_list:
            logging.info("%s," % port)
            

    def _disable_sw_port(self,port_list):
        if port_list.count(''):
            port_list.remove('')
        port_num=len(port_list)
        if port_num == 0:
            return
        portIdx=0
        while portIdx<port_num:
            self.sw.disable_interface(port_list[portIdx])
            self.carrierbag['port_disable_time']=time.time()
            logging.info('port %s is disabled' % port_list[portIdx])
            portIdx+=1
            logging.info("wait 20 seconds")
            time.sleep(20)
            
            
            
        
        
            
            
