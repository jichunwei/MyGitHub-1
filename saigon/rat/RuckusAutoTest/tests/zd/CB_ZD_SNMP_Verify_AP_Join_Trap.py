'''
Created on July 01, 2011
@author: cherry.cheng@ruckuswireless.com

Description: 
   This script is used to snmp trap: AP Join Trap.
   Delete an ap from GUI, trap is received if trap is enabled; no any trap is received if trap is disabled. 

'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.lib.snmp.zd.snmp_agent_trap import verify_ap_join_trap

class CB_ZD_SNMP_Verify_AP_Join_Trap(Test):
    
    required_components = []
    parameter_description = {}
    
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_ap_join_trap()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        #Wait for ap join zd.
        if self.errmsg and self.ap_mac_addr and self.is_delete_ap:
            self._verify_ap_join_zd(self.ap_mac_addr)

    def _init_test_params(self, conf):
        self.conf = {'auto_approval': True,
                     'is_need_approval': False,
                     'timeout': 480}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.ap_mac_addr = None
        self.is_delete_ap = False
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _verify_ap_join_trap(self):
        logging.info('Verify SNMP Trap: AP Join Trap')
        try:
            trap_service_cfg = self.conf['snmp_trap_cfg']
            
            #Only get first trap server information.
            for i in range(1,5):
                if trap_service_cfg.has_key(str(i)):
                    trap_server_cfg = trap_service_cfg.pop(str(i))
                    trap_service_cfg.update(trap_server_cfg)
                    break    
            
            enabled = True
            if trap_service_cfg.has_key('enabled'):
                enabled = trap_service_cfg.pop('enabled')
                
            #Set default version as 2.
            if not trap_service_cfg.has_key('version'):
                trap_service_cfg['version'] = 2
                
            if int(trap_service_cfg['version']) == 2:
                #Always send trap with public for v2 trap.
                trap_service_cfg['community'] = 'public'
            
            trap_service_cfg['timeout'] = 120
            
            ap_mac_list = self.testbed.get_aps_sym_dict_as_mac_addr_list()
            ap_mac_addr = ap_mac_list[0]
            self.ap_mac_addr = ap_mac_addr
            
            logging.info('Delete AP[%s] from ZD via GUI' % (ap_mac_addr,))
            self.zd._delete_ap(ap_mac_addr)
            self.is_delete_ap = True
            
            logging.info('Start trap receiver and verify trap information')
            agent_ip_addr = self.zd.ip_addr
            
            is_found, msg = verify_ap_join_trap(trap_service_cfg, ap_mac_addr, agent_ip_addr)
            
            if is_found != enabled:
                self.errmsg = msg
            else:
                if is_found:
                    self.passmsg = msg 
                else:
                    self.passmsg = 'Not receive AP join trap when disable trap.'
                                    
        except Exception, ex:
            self.errmsg = ex.message 
            
    def _verify_ap_join_zd(self, ap_mac_addr):
        '''
        Get expected versions for ap.
        '''
        try:
            auto_approval = self.conf['auto_approval']
            is_need_approval = self.conf['is_need_approval']
            timeout = self.conf['timeout']
            
            aps_err_d = {}
            
            logging.info('Verify APs approved and connected: %s' % ap_mac_addr)
            if not auto_approval and is_need_approval:
                logging.info('Manual approval the aps [%s]' % ap_mac_addr)
     
                res_ap_approval = self._manual_approve_aps(ap_mac_addr)
                if res_ap_approval:
                    aps_err_d['APsApproval'] = res_ap_approval
                
            logging.info('Wait for APs are connected [%s]' % ap_mac_addr)
            res_ap_connected = self._wait_ap_connected(ap_mac_addr, timeout)
            if res_ap_connected:
                aps_err_d['APsConnected'] = res_ap_connected
                
            logging.info('Verify AP components')
            #Notes: is ap component used after upgrade and reboot ZD during testing.
            res_verify_ap = self._verify_ap_component(ap_mac_addr)
            if res_verify_ap:
                aps_err_d['VerifyAPs'] = res_verify_ap
                        
            if aps_err_d:
                self.errmsg = aps_err_d
                
            self.passmsg = 'All APs [%s] are connected and version are correct.' % ap_mac_addr
        except Exception, ex:
            self.errmsg = ex.message
            
    def _manual_approve_aps(self, ap_mac_addr, timeout = 120):
        '''
        Wait ap is approved if auto appproval; will approval manually is not auto approval.
        '''
        logging.info("Manual approval for AP %s to join the ZoneDirector" % ap_mac_addr)
        start_time = time.time()
        err_d = {}
        while True:
            ap_info = self.zd.get_all_ap_info(ap_mac_addr)
            if ap_info:
                if ap_info['status'].lower().startswith("approval"):
                    logging.info("The AP %s is in the \"Approval Pending\" status now")
                    logging.info("Approve for this AP to join the ZD")
                    self.zd.allow_ap_joining(ap_info['mac'])
                    break
            if time.time() - start_time > timeout:
                if ap_info:
                    logging.debug("AP info: %s" % str(ap_info))
                    err_msg = "FAIL", "The AP %s is in %s status instead of \"Pending Approval\" \
                            status after %d seconds" % (ap_mac_addr, ap_info['status'], timeout)
                    err_d[ap_mac_addr] = err_msg
                else:
                    err_msg = "FAIL", "The AP %s does not appear in the AP-Summary table after %d seconds" % \
                                (ap_mac_addr, timeout)
                    err_d[ap_mac_addr] = err_msg
                
        return err_d
    
    def _wait_ap_connected(self, ap_mac_addr, timeout):
        '''
        Wait ap provisioning, till status is connected.
        '''
        end_time = time.time() + timeout
        err_d = {}
        while True:
            ap_info = self.zd.get_all_ap_info(ap_mac_addr)
            if ap_info:
                if ap_info['status'].lower().startswith("connected"):
                    logging.info("The provision process for the AP %s is completed successfully" % ap_mac_addr)
                    break
            if time.time() > end_time:
                if ap_info:
                    err_msg = "FAIL", "The AP %s is in the %s status instead of \"Connected\" status after %d seconds" % \
                                 (ap_mac_addr, ap_info['status'], timeout)
                    err_d[ap_mac_addr] = err_msg
                else:
                    err_msg = "FAIL", "The AP %s still does not appear in the AP-Summary table after %d seconds" % \
                                     (ap_mac_addr, timeout)
                    err_d[ap_mac_addr] = err_msg
                    
        return err_d

    def _verify_ap_component(self, ap_mac_addr):
        '''
        Verify AP component.
        '''
        active_ap = tconfig.get_testbed_active_ap(self.testbed, ap_mac_addr)
        time.sleep(2)
        
        err = ''
       
        # Make sure that the AP is in RUN state at CLI mode
        active_ap.verify_component()
        if active_ap.get_director_info() != "RUN":
            err = "FAIL", "The AP %s is not in the RUN state" % ap_mac_addr
        else:
            logging.info("The AP %s is in RUN state now" % ap_mac_addr)
            
        return err        