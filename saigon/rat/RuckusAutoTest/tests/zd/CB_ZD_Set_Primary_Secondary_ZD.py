# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Chris Wang
   @contact: cwang@ruckuswireless.com
   @since: Aug-09, 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       - enabled: default is True, enable/disable limited zd discovery.
       - primary_zd_ip: default is '192.168.0.2', primary zd ip or domain name.
       - secondary_zd_ip: default is '192.168.0.3', secondary zd ip or domain name.
       - keep_ap_setting: default is False, keep ap setting.
       - prefer_prim_zd: default is False, prefer primary zd.
       - zd_tag: zd tag. Will get zd components via zd tag in self.testbed.components.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Configure limited ZD discovery with valid values.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: The value are updated successfully.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging, time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd as lib  

class CB_ZD_Set_Primary_Secondary_ZD(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'enabled': "default is True, enable/disable limited zd discovery",
                              'primary_zd_ip': "default is '192.168.0.2', primary zd ip or domain name",
                              'secondary_zd_ip': "default is '192.168.0.3', secondary zd ip or domain name",
                              'keep_ap_setting': "default is False, keep ap setting",
                              'prefer_prim_zd': "default is False, prefer primary zd",
                              'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
                              }
    
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Configure limited ZD discovery settings via ZD")
            err_msg = lib.cfg_limited_zd_discovery(self.zd, self.conf)
            if err_msg:
                self.errmsg = "Fail to configure limited ZD discovery: %s" % err_msg
                logging.debug(self.errmsg)
            else:
                get_cfg = lib.get_limited_zd_discovery_cfg(self.zd)
                logging.debug("Current limited ZD discovery cfg: %s" % get_cfg)
            if self.conf['set_mgmt_id']:
                logging.info('set ap mgmt vlan to %s'%self.mgmt_vlan_id )
                lib.set_ap_mgmt_vlan_in_ap_policy(self.zd,self.mgmt_vlan_id)
                
                logging.info("wait 10 seconds")
                time.sleep(10)
                
                logging.info("wait all APs connected to ZD")
                self.zd.wait_aps_join_in_zd()
                
                logging.info("update all AP instances IP")
                all_aps_info = self.zd.get_all_ap_info()
                all_aps_ins = self.testbed.components['AP']
                for ap_ins in all_aps_ins:
                    for ap_info in all_aps_info:
                        if ap_ins.base_mac_addr.upper() == ap_info.get('mac').upper() and ap_info.get('ip_addr') != '':
                            ap_ins.ip_addr = ap_info.get('ip_addr')
        except Exception, e:
            self.errmsg = "Fail to configure limited ZD discovery: %s" % e.message
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Configure limited ZD discovery correctly: %s" % (self.conf)
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(enabled = True,
                         primary_zd_ip = '192.168.0.2',
                         secondary_zd_ip = '192.168.0.3',
                         keep_ap_setting = False,
                         keep_zd_ip=False,
                         prefer_prim_zd = False,
                         zd_tag = '',
                         set_mgmt_id = False,
                         mgmt_vlan_id = 'keep'
                         )
        self.conf.update(conf)
        
        zd_tag = self.conf.pop('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        self.mgmt_vlan_id = self.conf['mgmt_vlan_id']
        
        self.errmsg = ''
        self.passmsg = ''