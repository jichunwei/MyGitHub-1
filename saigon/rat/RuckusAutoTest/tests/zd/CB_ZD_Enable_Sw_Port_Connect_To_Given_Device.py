# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
enable given number of switch port connected to given deivce
by West.li
"""
import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_Enable_Sw_Port_Connect_To_Given_Device(Test):

    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
    def test(self):
        self._enable_sw_port( self.enableNum,self._port_list)
        self._update_carrier_bag()
        if self.errmsg:
            return 'FAIL',self.errmsg
        return 'PASS','enable port succ'
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('sw'):
            self.sw=self.carrierbag['sw']
        else:
            self.sw=self.testbed.components['L3Switch']
    
    def _update_carrier_bag(self):
        if self.enableDevice == 'ap':
            port_list_carrier_bag='disabled_ap_sw_port_list'
        elif self.enableDevice == 'zd':
            port_list_carrier_bag='disabled_zd_sw_port_list'
        else:
            return
        
        delNum=0
        while delNum<len(self._enabled_list):
            del_port=self.carrierbag[port_list_carrier_bag].pop(0)
            logging.info('port %s is removed from carribag' % del_port)
            delNum+=1
        
    def _init_test_params(self, conf):
        self.errmsg=''
        self.enableDevice=conf.get('device')
        
        self._port_list=[]
        if self.enableDevice == 'ap':
            if self.carrierbag.has_key('disabled_ap_sw_port_list'):
                self._port_list=self.carrierbag['disabled_ap_sw_port_list']
        elif self.enableDevice == 'zd':
            if self.carrierbag.has_key('disabled_zd_sw_port_list'):
                self._port_list=self.carrierbag['disabled_zd_sw_port_list']
        else:
            self._port_list = self.sw.get_disabled_interface()
                
        if conf.has_key('number'):
            self.enableNum=conf['number']
        else:
            self.enableNum=len(self._port_list)
            
        logging.info('there are %d port(s) are disabled,and there are %d port(s) to enable' 
                     % (len(self._port_list),self.enableNum))
        
        self.conf=conf
        
        
    def _enable_sw_port(self,num,port_list):
        port_num=num
        self._enabled_list=[]
        if len(port_list)==0:
            logging.info('no port disabled,return directly')
            return
        if port_num>len(port_list):
            logging.info('port number %d more then the port in disabled list:%d,set it to %d ' % (port_num,len(port_list),len(port_list)))
            port_num=len(port_list)
            
        portIdx=0
        while portIdx<port_num:
            self.sw.enable_interface(port_list[portIdx])
            logging.info('port %s is enabled' % port_list[portIdx])
            self._enabled_list+=[port_list[portIdx]]
            self.carrierbag['pri_zd_sw_enable_time'] = time.time()
            portIdx+=1
            logging.info('wait 20 seconds')
            time.sleep(20)
            
            if self.conf.has_key('zdcli'):
                zdcli=self.carrierbag[self.conf['zdcli']]
            else:
                zdcli=self.testbed.components['ZoneDirectorCLI']
            retry_time=10
            for i in range(0,retry_time):
                try:
                    zdcli.zdcli = sshclient(zdcli.ip_addr, zdcli.port,'admin','admin')
                    zdcli.login()
                    break
                except Exception,e:
                    logging.debug('exception met:%s,try again'%e.message)
                    time.sleep(5)
                    
    
        
