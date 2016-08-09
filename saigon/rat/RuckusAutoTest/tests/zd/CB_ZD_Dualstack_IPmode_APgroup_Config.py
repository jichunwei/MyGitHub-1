'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-10-10
@author: kevin.tan@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Constant as CONST

default_apgrp_name = 'System Default'

IPMODE_PARENT = '*'
IPMODE_IPV4 = '1'
IPMODE_IPV6 = '2'
IPMODE_DUAL = '3'

nn = {IPMODE_IPV4: 'ipv4',
      IPMODE_IPV6: 'ipv6',
      IPMODE_DUAL: 'dual',
     }

class CB_ZD_Dualstack_IPmode_APgroup_Config(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
        self.passmsg = ''
        self.errmsg = ''

    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Verify dual stack IP address after setting factory default')
        self._verify_dualstack_after_setting_factory()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        logging.info('Verify ZD UI can configure AP mode to ipv4 only in default AP group')
        self._verify_ipv4_only_in_default_apgrp()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        #verify ZD UI can configure AP mode to dual stack in non-default AP group
        try:
            logging.info('Verify IP mode when AP in new AP group, default group is dual stack, new group is using parent')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_PARENT)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Verify IP mode when AP in new AP group, default group is dual stack, new group is dual stack overriding parent')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_DUAL)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Verify IP mode when AP in new AP group, default group is dual stack, new group is ipv4 only overriding parent')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_IPV4)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Verify IP mode when AP in new AP group, default group is ipv4 only, new group is using parent')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_IPV4, mode_new_grp=IPMODE_PARENT)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Verify IP mode when AP in new AP group, default group is ipv4 only, new group is ipv4 only')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_IPV4, mode_new_grp=IPMODE_IPV4)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
        except:
            pass
        
        #check configuration overwrite hierarchy : AP->APGROUOP->System default group
        try:
            logging.info('Default group is dual stack, new group is using parent, AP override AP group configuration with dual stack')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_PARENT, mode_ap=IPMODE_DUAL)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Default group is dual stack, new group is using parent, AP override AP group configuration with ipv4 only')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_PARENT, mode_ap=IPMODE_IPV4, event_trigger=True)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Default group is dual stack, new group is ipv4 only, AP override AP group configuration with dual stack')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_DUAL, mode_new_grp=IPMODE_IPV4, mode_ap=IPMODE_DUAL, event_trigger=True)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Default group is ipv4 only, new group is using parent, AP override AP group configuration with dual stack')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_IPV4, mode_new_grp=IPMODE_PARENT, mode_ap=IPMODE_DUAL, event_trigger=True)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Default group is ipv4 only, new group is using parent, AP override AP group configuration with ipv4 only')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_IPV4, mode_new_grp=IPMODE_PARENT, mode_ap=IPMODE_IPV4)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            logging.info('Default group is ipv4 only, new group is dual stack, AP override AP group configuration with ipv4 only')
            self._verify_ipmode_while_ap_in_new_apgrp(mode_default_grp=IPMODE_IPV4, mode_new_grp=IPMODE_DUAL, mode_ap=IPMODE_IPV4, event_trigger=True)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)

        except:
            pass
        
        return self.returnResult('PASS', 'IP mode test of AP group passed')

    def _verify_dualstack_after_setting_factory(self):
        info = ap_group.get_ap_group_ip_mode_by_name(self.zd, default_apgrp_name)
        if info['ip_mode'] != IPMODE_DUAL:
            self.errmsg += 'default IP mode in System Default AP group is %s, not %s, ' % (info['ip_mode'], IPMODE_DUAL)
            
        #verify IP mode is dual stack with override disabled in active AP configuration
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != default_apgrp_name:
            self.errmsg += 'default AP group of active AP is %s, not %s, ' % (info['ap_group'], default_apgrp_name)

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != IPMODE_PARENT:
            self.errmsg += 'default AP IP mode of active AP is %s, not %s, ' % (info['ip_mode'], IPMODE_PARENT)
        if info['ip_version'] != IPMODE_DUAL:
            self.errmsg += 'default AP IP version of active AP is %s, not %s, ' % (info['ip_version'], IPMODE_DUAL)

    def _verify_ipv4_only_in_default_apgrp(self):
        ap_group.set_ap_group_ip_mode_by_name(self.zd, default_apgrp_name, IPMODE_IPV4)
            
        #verify IP mode is dual stack with override disabled in active AP configuration
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != default_apgrp_name:
            self.errmsg += 'default AP group of active AP is %s, not %s, ' % (info['ap_group'], default_apgrp_name)

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != IPMODE_PARENT:
            self.errmsg += 'default AP IP mode of active AP is %s, not %s, ' % (info['ip_mode'], IPMODE_PARENT)
        if info['ip_version'] != IPMODE_IPV4:
            self.errmsg += 'default AP IP version of active AP is %s, not %s, ' % (info['ip_version'], IPMODE_IPV4)

        #Restore configuration
        ap_group.set_ap_group_ip_mode_by_name(self.zd, default_apgrp_name, IPMODE_DUAL)

    def _verify_ipmode_while_ap_in_new_apgrp(self, mode_default_grp, mode_new_grp, mode_ap=IPMODE_PARENT, event_trigger=False):
        new_apgrp = 'new-apgrp-created'
        ap_group.create_ap_group(self.zd, new_apgrp)
        
        ap_group.set_ap_group_ip_mode_by_name(self.zd, default_apgrp_name, mode_default_grp)
        ap_group.set_ap_group_ip_mode_by_name(self.zd, new_apgrp, mode_new_grp)
        ap_group.move_ap_to_member_list(self.zd, new_apgrp, self.apmac)

        #verify IP mode of active AP on ZD webUI
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != new_apgrp:
            self.errmsg += 'active AP is in AP group %s, not in new group %s, ' % (info['ap_group'], new_apgrp)

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != IPMODE_PARENT:
            self.errmsg += 'active AP IP mode of  is %s, not %s, ' % (info['ip_mode'], IPMODE_PARENT)
        if mode_new_grp == IPMODE_PARENT:
            if info['ip_version'] != mode_default_grp:
                self.errmsg += 'active AP IP version is %s, not %s, ' % (info['ip_version'], mode_default_grp)
        else:
            if info['ip_version'] != mode_new_grp:
                self.errmsg += 'active AP IP version is %s, not %s, ' % (info['ip_version'], mode_new_grp)

        #Check AP mode via AP CLI and ap-list.xml in ZD shell
        if mode_ap != IPMODE_PARENT:
            info = lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, mode_ap)

            # check event: AP[xx:xx:xx:xx:xx:xx] reset due to IP address change
            if event_trigger == True:
                self._veirfy_ip_change_event()
            
        #Restore configuration
        ap_group.delete_all_ap_group(self.zd)
        ap_group.set_ap_group_ip_mode_by_name(self.zd, default_apgrp_name, IPMODE_DUAL)
        lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, IPMODE_PARENT)
        self.zd.clear_all_events()

    def _veirfy_ip_change_event(self):
        logging.info('Verify IP address change event on ZD WebUI')
        all_events = self.zd.getEvents()

        #MSG_AP_ip_change={ap} reset due to IP address change
        expected_event = self.zd.messages['MSG_AP_ip_change']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )

        expected_event = expected_event % (self.apmac)

        for event in all_events:
            if expected_event in event:
                self.passmsg = '[Correct behavior] %s' % event
                return

        self.errmsg = '[Incorrect behavior] There is no event about IP address change on AP[%s], ' % (self.apmac)

    def cleanup(self):
        self._update_carribag()
