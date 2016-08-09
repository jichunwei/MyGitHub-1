'''
Description:
   This scripts verifies AP join trap can be set to all trap servers.
   
Created on 2012-08-10
@author: zoe.huang@ruckuswireless.com

'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd.snmp_agent_trap import expected_trap_info
from RuckusAutoTest.components.lib.snmp.zd.snmp_agent_trap import verify_trap_sent_to_server

class CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver(Test):
    
    required_components = ['ZoneDirector', 'LinuxServer']
    parameter_description = {'snmp_trap_cfg': 'SNMP trap info',
                             'zd_ipv6_addr': 'ipv6 addr of ZD',
                             'wait_time_for_trap': 'wait time for trap raised'}
      
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        

    def test(self):        
        self._verify_ap_join_multi_trap_receivers()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        if self.serverlist:
            for i in range(1,5):
                if self.serverlist.has_key(str(i)):
                    linux_server = self.serverlist[str(i)]
                    linux_server.close()                

    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)       
        self.zd = self.testbed.components['ZoneDirector']
        self.linuxserver = self.testbed.components['LinuxServer']
        self.zd_ipv4_addr = self.zd.ip_addr
        self.zd_ipv6_addr = self.conf['zd_ipv6_addr']
        self.wait_time = self.conf['wait_time_for_trap']       
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        self.filelist = self.carrierbag['files_save_snmp_trap']
        self.deleted_ap = self.carrierbag['deleted_ap_mac_addr']
        self.serverlist = self.carrierbag['linux_server_instance'] 
    
    def _update_carrier_bag(self):
        pass

    def _verify_ap_join_multi_trap_receivers(self):
        logging.info('Verify SNMP Trap when multiple trap servers are configured: AP Join Trap')
        try:
            trap_service_cfg = self.conf['snmp_trap_cfg']
            enabled = True
            if trap_service_cfg.has_key('enabled'):
                enabled = trap_service_cfg.pop('enabled') 
            logging.info('wait for trap to be raised for %s s' % self.wait_time)
            time.sleep(self.wait_time)   
            for i in range(1,5):
                if trap_service_cfg.has_key(str(i)):
                    logging.info('Begin to check trap server[%s]' % str(i))
                    trap_message_list = self.linuxserver.read_snmptrap(self.filelist[str(i)])
                    if len(trap_message_list)==0:
                        if enabled:
                            self.errmsg += ('Trap server[%s] does not receiver any trap message.' % str(i) )
                        else:
                            self.passmsg += 'Trap server[%s] does not receiver any trap message when trap is disabled.' % str(i)
                            logging.info('Trap server[%s] does not receiver any trap message when trap is disabled.' % str(i))
                        continue
                    if i<4:
                        agent_ip_addr = self.zd_ipv4_addr
                    else:
                        agent_ip_addr = self.zd_ipv6_addr
                    expected_ap_join_trap =  expected_trap_info('ruckusZDEventAPJoinTrap', agent_ip_addr, 'ruckusZDEventAPMacAddr', self.deleted_ap)            
                    is_found, msg = verify_trap_sent_to_server(expected_ap_join_trap, trap_message_list)
                    msg = 'Trap server[%s] %s' % (str(i),msg)
                    if is_found != enabled:
                        self.errmsg += msg
                    else:
                        if is_found:
                            self.passmsg += msg 
                        else:
                            self.passmsg += 'Trap server[%s] does not receive AP join trap when disable trap.' % str(i)
        
        except Exception, ex:
            self.errmsg += ex.message
                