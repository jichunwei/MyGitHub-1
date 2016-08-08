'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update ap via SNMP.
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aps_info
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_SNMP_Verify_Update_AP(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_update_ap_cfg()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'set_ap_cfg': {},
                     'wg_name': '',
                     'auto_approval': True,
                     'is_need_approval': False,
                     'timeout': 480}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        #@ZJ 20150324 ZF-12462
        self.ap = self.testbed.components['AP'] 
         
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _verify_update_ap_cfg(self):
        logging.info('Verify update AP config via ZD SNMP')
        try:
            if self.conf.has_key('edit_ap_cfg_list'):
                update_cfg_list = self.conf['edit_ap_cfg_list']
            else:
                wg_name = 'Default'
                if self.conf.has_key('wg_name') and self.conf['wg_name']:
                    wg_name = self.conf['wg_name']
                    
                if self.conf['set_ap_cfg']:
                    update_cfg_list = [self.conf['set_ap_cfg']]
                else:
                    update_cfg_list = aps_info.gen_zd_ap_update_cfg(wg_name)
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zd.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            ap_id_mac_mapping = aps_info.get_zd_ap_index_value_mapping(snmp)
            
            if not ap_id_mac_mapping:
                self.errmsg = 'No AP joins this ZD.'
            else:
                if self.conf.has_key('mac_addr'):
                    edit_mac_addr = helper.format_mac_address(self.conf['mac_addr'])                    
                    edit_ap_id = helper.get_dict_key_by_value(ap_id_mac_mapping, edit_mac_addr)                    
                else:
                    edit_ap_id = ap_id_mac_mapping.keys()[0]
                    edit_mac_addr = ap_id_mac_mapping.values()[0]
                
                if edit_ap_id == '0':
                    self.errmsg = "No ap exist with mac addr %s" % edit_mac_addr
                else:
                    res_d, need_restart_ap = aps_info.verify_update_zd_ap(snmp, edit_ap_id, update_cfg_list)
                    
                    if need_restart_ap:
                        logging.info("Set AP's director ip first")
                        #@ZJ 20150324 ZF-12462
                        ap = self.ap[0]
#                        ap = self.testbed.mac_to_ap[self.conf['mac_addr'].lower()]  
                        ip_mode = ap.get_ip_mode('wan')
                        if ip_mode in ['ipv6','dual']: 
                            if self.zd.ip_addr != ap.get_mgmt_director_ip():
                                logging.info("Set AP's director IP to '%s'" %self.zd.ip_addr)
                                ap.set_director_info(self.zd.ip_addr)
                                ap.reboot()
                                time.sleep(40) #wait 40s for ap setting to take effect.
                            else:
                                logging.info("No need to set AP's director")
                        logging.info("Wating AP restarted based on IP changes")
                        self._verify_ap_join_zd(edit_mac_addr)
                    
                    if res_d:
                        self.errmsg = res_d
                    else:
                        self.passmsg = 'Update AP config successfully: %s' % edit_mac_addr
                                    
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
            