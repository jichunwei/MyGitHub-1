# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: July 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector'
   Test parameters:
       - 'mac_addr': 'ap mac address',
       - 'mac_addr_list': 'ap mac address list',
       - 'auto_approval': 'is ap auto approval',
       - 'is_need_approval': 'need to do manual approval',
       - 'timeout': 'timeout for ap join',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - If need do manual approval, approval the ap in mac address list.
        - Verify ap joins and verify ap component via cli.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: AP joins successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Join(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'mac_addr': 'ap mac address',
                              'mac_addr_list': 'ap mac address list',
                              'auto_approval': 'is ap auto approval',
                              'is_need_approval': 'need to do manual approval',
                              'timeout': 'timeout for ap join',
                              }

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._verify_aps_join()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        if self.conf.get('ap_tag') and self.conf.get('ap_group'):
            if self.conf.get('event_log'):
                self._verify_ap_initial_provision_tag()
            elif self.conf.get('event_band_switch'):
                self._verify_ap_band_switch()
            
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        self._update_carrier_bag()
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'mac_addr': None,
                     'mac_addr_list': [],
                     'auto_approval': True,
                     'is_need_approval': False,
                     'timeout': 480,
                     'is_allow': True,
                     'verify_ap_component': True,
                     'ap_tag':'',}
        
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        self.mac_addr_list = self.conf['mac_addr_list']
        # An Nguyen @ Sep 2012 - modify to get more variable from tester
        if self.conf.get('mac_addr'):
            self.mac_addr_list.append(self.conf['mac_addr'])
        if self.conf.get('ap_tag'):
            if type(self.conf['ap_tag']) != list:
                ap_tags = [self.conf['ap_tag']]
            else:
                ap_tags = self.conf['ap_tag']
                
            for ap_tag in ap_tags:
                self.mac_addr_list.append(self.carrierbag[ap_tag]['ap_ins'].base_mac_addr)
        
        if self.conf.get('all_ap'):
            self.mac_addr_list.extend(self.testbed.get_aps_mac_list())
                              
        self.is_allow = self.conf['is_allow']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _verify_aps_join(self):
        '''
        Get expected versions for ap.
        '''
        try:
            auto_approval = self.conf['auto_approval']
            is_need_approval = self.conf['is_need_approval']
            timeout = self.conf['timeout']
            
            result = True
            aps_err_d = {}
            
            logging.info('Verify APs approved and connected: %s' % self.mac_addr_list)
            if not auto_approval and is_need_approval:
                logging.info('Manual approval the aps [%s]' % self.mac_addr_list)
                
                res_aps_approval = []
                for mac_addr in self.mac_addr_list:
                    res_ap_approval = self._manual_approve_aps(mac_addr)
                    if res_ap_approval:
                        res_aps_approval.append(res_ap_approval)
                        
                if res_aps_approval:
                    result = False
                    aps_err_d['APsApproval'] = res_aps_approval
            
            if result:
                #(self.is_allow == True and result == True) or (self.is_allow == False and result == True):
                logging.info('Wait for APs are connected [%s]' % self.mac_addr_list)
                res_aps_connected = []
                for mac_addr in self.mac_addr_list:
                    res_ap_connected = self._wait_ap_connected(mac_addr, timeout)
                    if res_ap_connected:
                        res_aps_connected.append(res_ap_connected)
                
                if res_aps_connected:
                    result = False
                    aps_err_d['APsConnected'] = res_aps_connected
                
                #When is allow, verify ap components.
                if self.conf['verify_ap_component'] and self.is_allow and result:
                    logging.info('Verify AP components')
                    res_verify_aps = []
                    for mac_addr in self.mac_addr_list:
                        #Notes: is ap component used after upgrade and reboot ZD during testing.
                        res_verify_ap = self._verify_ap_component(mac_addr)
                        if res_verify_ap:
                            res_verify_aps.append(res_verify_ap)
                                
                        if res_verify_aps:
                            result = False
                            aps_err_d['VerifyAPs'] = res_verify_aps
            
            if self.is_allow:             
                #If ap allow to connect to ZD.
                if result == False:
                    self.errmsg = aps_err_d
                self.passmsg = 'All APs [%s] are connected and version are correct.' % self.mac_addr_list
            else:
                #If ap is not allowed to connect to ZD.
                if result == True:
                    self.errmsg = 'APs [%s] are connected to ZD.' % self.mac_addr_list
                    
                self.passmsg = 'All APs [%s] are not connected to ZD.' % self.mac_addr_list
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
                status = ap_info['status'].lower() 
                if status.startswith("approval"):
                    logging.info("The AP %s is in the \"Approval Pending\" status now" % ap_mac_addr)
                    logging.info("Approve for this AP to join the ZD")
                    self.zd.allow_ap_joining(ap_info['mac'])
                    break
                else:
                    #IF ap status is disconnected or connected, don't need approval.
                    if status.startswith('disconnected') or status.startswith('connected'):
                        logging.info("The AP %s has been approved and status is %s" % (ap_mac_addr, status))
                        break

                    
            if time.time() - start_time > timeout:
                if ap_info:
                    err_msg = "FAIL", "The AP %s is in %s status instead of \"Pending Approval\" \
                            status after %d seconds" % (ap_mac_addr, ap_info['status'], timeout)
                    err_d[ap_mac_addr] = err_msg
                else:
                    err_msg = "FAIL", "The AP %s does not appear in the AP-Summary table after %d seconds" % \
                                (ap_mac_addr, timeout)
                    err_d[ap_mac_addr] = err_msg
                    
                break
                
        return err_d
    
    def _wait_ap_connected(self, ap_mac_addr, timeout):
        '''
        Wait ap provisioning, till status is connected.
        '''
        logging.info('Waiting %s for ap %s connected' % (timeout, ap_mac_addr))
        end_time = time.time() + timeout
        err_d = {}
        while True:
            ap_info = self.zd.get_all_ap_info(ap_mac_addr)
            if ap_info:
                if ap_info['status'].lower().startswith("connected") and self.is_allow:
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
                    
                break
                    
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
        for i in range(10):
            if active_ap.get_director_info() != "RUN":
                err = "FAIL", "The AP %s is not in the RUN state" % ap_mac_addr
            else:
                logging.info("The AP %s is in RUN state now" % ap_mac_addr)
                err = ''
                break
            time.sleep(5)
            
        return err
    def _verify_ap_initial_provision_tag(self):
        apmac = self.carrierbag[self.conf['ap_tag']]['ap_ins'].base_mac_addr
        apgrp = self.conf['ap_group']
        time.sleep(30)
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, apmac)
        if info['ap_group'] != apgrp:
            self.errmsg += 'active AP is in AP group %s, not %s for initial provision tag' % (info['ap_group'], apgrp)
            return
        
        if self.conf.get('event_log') and self.conf.get('original_ap_group'):
            logging.info('Test Initial Provision Tag event when AP rejoin ZD at the first time')
            all_events = self.zd.getEvents()

            #MSG_AP_joined_apgroup_found={ap} is assigned to {apgroup}
            expected_event_1 = self.zd.messages['MSG_AP_joined_apgroup_found']
            expected_event_1 = expected_event_1.replace("{ap}", r"AP[%s]" )
            expected_event_1 = expected_event_1.replace("{apgroup}", r"[%s]")
            expected_event_1 = expected_event_1 % (apmac.lower(), self.conf['original_ap_group'])

            #MSG_AP_joined_apgroup_fail={ap} initial provisioning {apgroup} is undefined; AP assigned to system default group
            expected_event_2 = self.zd.messages['MSG_AP_joined_apgroup_fail']
            expected_event_2 = expected_event_2.replace("{ap}", r"AP[%s]" )
            expected_event_2 = expected_event_2.replace("{apgroup}", r"[%s]")
            expected_event_2 = expected_event_2 % (apmac.lower(), self.conf['original_ap_group'])

            if self.conf['event_log'] == 'none':
                for event in all_events:
                    if expected_event_1 in event or expected_event_2 in event:
                        errmsg = '[Incorrect behavior] Event about AP group [%s] assignment when AP[%s] with IPT joins ZD is shown on GUI'
                        self.errmsg = errmsg % (self.conf['original_ap_group'], apmac)
                        return
            else:
                if self.conf['event_log'] == 'positive':
                    expected_event = expected_event_1
                else: #negative
                    expected_event = expected_event_2
    
                for event in all_events:
                    if expected_event in event:
                        self.passmsg = '[Correct behavior] %s' % event
                        return
    
                errmsg = '[Incorrect behavior] There is not any event about AP group [%s] assignment when AP[%s] with IPT joins ZD at the first time, '
                self.errmsg = errmsg % (self.conf['original_ap_group'], apmac)

    def _verify_ap_band_switch(self):
        apmac = self.carrierbag[self.conf['ap_tag']]['ap_ins'].base_mac_addr
        apgrp = self.conf['ap_group']
        time.sleep(30)
        ap_config_info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, apmac)
        
        if ap_config_info['ap_group'] != apgrp:
            self.errmsg += 'active AP is in AP group %s, not %s for initial provision tag' % (ap_config_info['ap_group'], apgrp)
            return
        
        current_ap_info = self.zd.get_all_ap_info(apmac)
        if not current_ap_info:
            logging.info('Get active AP[%s] info on "Currently Managed APs" page failed, wait for a few second and get it again' % (apmac))
            time.sleep(30)
            self.zd.get_all_ap_info(apmac)
            if not current_ap_info:
                self.errmsg += 'Get active AP[%s] info on "Currently Managed APs" page failed!' % (apmac)
                return

        ori_band = ''
        new_band = self.conf['band_switch_new']
        ap_channel = current_ap_info['channel']
        if  new_band== '2.4 GHz':
            ori_band = '5 GHz'
            if not (r'g/n' in ap_channel):#chen.tao 2014-2-24, to fix ZF-7563
                self.errmsg += 'Active AP[%s] channel[%s] on "Currently Managed APs" page unexpected, should be 11g/n!' % (apmac, ap_channel)
                return
        elif new_band == '5 GHz':
            ori_band = '2.4 GHz'
            if not (r'a/n' in ap_channel):#chen.tao 2014-2-24, to fix ZF-7563
                self.errmsg += 'Active AP[%s] channel[%s] on "Currently Managed APs" page unexpected, should be 11a/n!' % (apmac, ap_channel)
                return

        all_events = self.zd.getEvents()

        #MSG_AP_band_switch={ap} radio band change from {ori_band} to {new_band}
        expected_event_1 = self.zd.messages['MSG_AP_band_switch']
        expected_event_1 = expected_event_1.replace("{ap}", r"AP[%s]" )
        expected_event_1 = expected_event_1.replace("{ori_band}", r"[%s]")
        expected_event_1 = expected_event_1.replace("{new_band}", r"[%s]")
        expected_event_1 = expected_event_1 % (apmac.lower(), ori_band, new_band)

        #MSG_AP_band_switch_reset={ap} reset due to radio band change from {ori_band} to {new_band}
        expected_event_2 = self.zd.messages['MSG_AP_band_switch_reset']
        expected_event_2 = expected_event_2.replace("{ap}", r"AP[%s]" )
        expected_event_2 = expected_event_2.replace("{ori_band}", r"[%s]")
        expected_event_2 = expected_event_2.replace("{new_band}", r"[%s]")
        expected_event_2 = expected_event_2 % (apmac.lower(), ori_band, new_band)

        #MSG_AP_band_diff={ap} joins with radio band {ap-band}, set to {zd-band}
        expected_event_3 = self.zd.messages['MSG_AP_band_diff']
        expected_event_3 = expected_event_3.replace("{ap}", r"AP[%s]" )
        expected_event_3 = expected_event_3.replace("{ap-band}", r"[%s]")
        expected_event_3 = expected_event_3.replace("{zd-band}", r"[%s]")
        expected_event_3 = expected_event_3 % (apmac.lower(), ori_band, new_band)
        
        flag1 = False
        flag2 = False
        if self.conf['event_band_switch'] == 'configure':
            logging.info('Verify event when configuring AP radio to another band-switch')
            for event in all_events:
                if flag1 == True and flag2 == True:
                    break

                if flag1 == False:
                    if expected_event_1 in event:
                        flag1 = True
                    
                if flag2 == False:
                    if expected_event_2 in event:
                        flag2 = True

            if flag1 == False or flag2 == False :
                errmsg = '[Incorrect behavior] Event [%s] and [%s] not both shown on ZF GUI for AP[%s]'
                self.errmsg = errmsg % (expected_event_1, expected_event_2, apmac)
        elif self.conf['event_band_switch'] == 'rejoin':
            logging.info('Verify event when AP rejoins ZD for the first time after AP is deleted')
            for event in all_events:
                if flag1 == True and flag2 == True:
                    break

                if flag1 == False:
                    if expected_event_2 in event:
                        flag1 = True
                    
                if flag2 == False:
                    if expected_event_3 in event:
                        flag2 = True

            if flag1 == False or flag2 == False :
                errmsg = '[Incorrect behavior] Event [%s] and [%s] not both shown on ZF GUI for AP[%s]'
                self.errmsg = errmsg % (expected_event_2, expected_event_3, apmac)
        elif self.conf['event_band_switch'] == 'negative':
            logging.info('Verify that there should be no event shown on ZD GUI')
            for event in all_events:
                if (expected_event_1 in event) or (expected_event_2 in event) or (expected_event_3 in event):
                    errmsg = '[Incorrect behavior] There should not any event about AP[%s] band switch'
                    self.errmsg = errmsg % (self.conf['original_ap_group'], apmac)
                    return
        else:
            errmsg = '[Incorrect behavior] event_band_switch value [%s] invalid'
            self.errmsg = errmsg % (self.conf['event_band_switch'])

