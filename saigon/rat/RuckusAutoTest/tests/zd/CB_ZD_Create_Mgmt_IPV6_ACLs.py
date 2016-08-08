# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
   Test parameters:
        - 'ap_mac_list': 'AP mac address list',
        - 'ip_cfg': 'AP IP configuration.'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set AP device IP setting as specified via CLI
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If set device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl

class CB_ZD_Create_Mgmt_IPV6_ACLs(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'mgmt_acl_list': 'management acl list'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Create management ipv6 acls via ZD GUI")
            err_dict = {}            
            for ipv6_acl in self.mgmt_ipv6_acl_list:
                err_acl = self._create_mgmt_acls(ipv6_acl)
                if err_acl:
                    err_dict[ipv6_acl['name']] = err_acl
            if err_dict:
                self.errmsg = "Create mgmt ipv6 acl failed: %s" % err_dict
                
            if not self.errmsg:
                logging.info("Get all management ipv6 acls via ZD GUI")
                self.gui_all_acls_list = mgmt_ip_acl.get_all_mgmt_ipv6_acl(self.zd)
                logging.info("Compare data between GUI set and get")
                self._compare_gui_set_get()
        except Exception, ex:
            self.errmsg = 'Create and compare mgmt ipv6 acl failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Create management ipv6 acls via ZD GUI and data are same between set and get successfully'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['gui_mgmt_ipv6_acl_list'] = self.gui_all_acls_list
        
    def _cfg_init_test_params(self, conf):
        '''
        Mgmt acl dict sample:
            {'name': 'mgmt ip acl name',
             'type': 'single|prefix,
             'addr': 'single addr|addr and prefix split with /',
             }
        '''
        self.conf = {'mgmt_acl_list': []}        
        self.conf.update(conf)
        
        self.mgmt_ipv6_acl_list = self.conf['mgmt_acl_list']
            
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        
    def _create_mgmt_acls(self, ipv6_acl):
        errmsg = ''
        try:
            mgmt_ip_acl.create_mgmt_ipv6_acl(self.zd, ipv6_acl)            
        except Exception,ex:
            errmsg = 'Create Mgmt IPV6 ACL Failed: %s' % ex.message
        return errmsg
            
    def _compare_gui_set_get(self):
        if self.mgmt_ipv6_acl_list and self.gui_all_acls_list:
            res = mgmt_ip_acl.compare_mgmt_ipv6_acl_gui_set_get(self.mgmt_ipv6_acl_list, self.gui_all_acls_list)
        else:
            if self.mgmt_ipv6_acl_list == self.gui_all_acls_list:
                res = "No mgmt acl in GUI set and get"
            elif not self.mgmt_ipv6_acl_list:
                res = "No mgmt acl in GUI set"
            elif not self.gui_all_acls_list:
                res = "No mgmt acl in GUI get"
        if res:
            self.errmsg = "Data between GUI set and get are different: %s" % res