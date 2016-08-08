'''
Description:
Trap servers start to listen and receive trap messages
Created on 2012-08-10
@author: zoe.huang@ruckuswireless.com

'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_server_by_ip_addr

class CB_ZD_Start_Linux_SNMPTrap_Server(Test):
    
    required_components = ['ZoneDirector', 'LinuxServer']
    parameter_description = {'snmp_trap_cfg': 'SNMP trap info',
                             'time_out': 'time for trap server to listen'}
      
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        

    def test(self):        
        self._start_linux_snmp_trap_server()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Start all trap servers successflly.')

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)       
        self.zd = self.testbed.components['ZoneDirector']
        self.linuxserver = self.testbed.components['LinuxServer']
        self.time_out = self.conf['time_out']       
        self.filename = {}      
        self.errmsg = ''
        self.serverlist = {}
                
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['files_save_snmp_trap'] = self.filename
        self.carrierbag['linux_server_instance'] = self.serverlist

    def _start_linux_snmp_trap_server(self):
        try:
            trap_service_cfg = self.conf['snmp_trap_cfg']
                            
            #Set default version as 2.
            version = 2
            if trap_service_cfg.has_key('version'):
                version = trap_service_cfg['version']
               
            for i in range(1,5):
                if trap_service_cfg.has_key(str(i)):
                    if trap_service_cfg[str(i)].has_key('server_ip'):
                        server_ip = trap_service_cfg[str(i)]['server_ip']
                        filename = 'trapInfoV%s%s' % (version,server_ip)
                        params = 'filename="%s" version=%s server_ip="%s" timeout=%s' % (filename, version, server_ip, self.time_out) 
                        
                        linux_server = self._create_linux_server()
                        linux_server.start_snmptrap(filename, params)
                        #linux_server.close()
                        logging.info('Start linux SNMP trap server[%s], params: %s' % (server_ip, params))
                        self.filename[str(i)] = filename
                        self.serverlist[str(i)] = linux_server
                        time.sleep(2)
                    else:
                        self.errmsg = self.errmsg + ('snmp_trap_cfg[%s] does not have server_ip.' % str(i))              
        except Exception, ex:
            self.errmsg = self.errmsg + ex.message
            
    def _create_linux_server(self): 
        linux_server = create_server_by_ip_addr(self.linuxserver.conf['ip_addr'],self.linuxserver.conf['user'],self.linuxserver.conf['password'],self.linuxserver.conf['root_password'])
        return linux_server
        
                      