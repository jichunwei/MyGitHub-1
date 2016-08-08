# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Jul 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Zone Director'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Configure dhcp server on ZD WebUI
        - Verify if the service is running
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import re

import logging

from RuckusAutoTest.models import Test


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Verify_Assigned_IP_Display(Test):

    def config(self, conf):
        """
        """
        self._init_test_parameters(conf)

    def test(self):
        """
        """
        self._verify_zd_assigned_ip_display()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', '')

    def cleanup(self):
        """
        """
        pass

#
#
#
    def _init_test_parameters(self, conf):
        """
        """
        self.conf = {'zd_tag': '',
                     'key': '',
                     'leasetime_gap': 300,
                     'sta_tag': '',} # mac/ip
        self.conf.update(conf)
        
        if self.conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else: 
            self.zd = self.testbed.components['ZoneDirector']
        
        self._get_expected_station_ip_info()
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _get_expected_station_ip_info(self):
        if not self.conf['sta_tag']:
            self.expected_info = None
            return
        self.conf['key'] = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.expected_info = {'mac': self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'],
                              'ip': self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']}
    
    def _verify_zd_assigned_ip_display(self):
        """
        """
        logging.info('Verify the assigned ip display')
        zd_dhcp_config = self.zd.get_dhcp_server_info()
        if self.conf['key']:
            logging.info('Searching for the assigned ip with key "%s"' % self.conf['key'])
            zd_assigned_ip = self.zd.get_assigned_ip_info(self.conf['key'])
        else:    
            zd_assigned_ip = self.zd.get_assigned_ip_info()
            
        logging.info('ZD DHCP Server configuration: \n%s' % zd_dhcp_config)
        logging.info('Assigned IP Info: \n%s' %zd_assigned_ip)
        
        if not zd_assigned_ip:
            self.errmsg = 'There is not info for the assigned ip as expected'
            return
        
        unmatch_leasetime = []
        expected_leasetime = {'Six hours':21600, 'Twelve hours':43200, 'One day':86400, 
                              'Two days':172800, 'One week':604800, 'Two weeks':1209600}[zd_dhcp_config['leasetime']]
        for entry in zd_assigned_ip:
            display_leasetime = self._read_leasetime(entry['leasetime'])
            if expected_leasetime - display_leasetime > self.conf['leasetime_gap']:
                unmatch_leasetime.append(entry)
                msg = 'The entry %s which leasetime is %s not in range "%s" as expected'
                msg = msg % (entry, entry['leasetime'], zd_dhcp_config['leasetime'])
                logging.info(msg)
        
        if unmatch_leasetime:
            errmsg = 'The following entries are displayed unexpected lease time %s'
            self.errmsg = errmsg % unmatch_leasetime
            logging.info(self.errmsg)
            return
        
        self.passmsg = 'All assigned ip info are displayed as expected'
        if not self.expected_info:
            logging.info(self.passmsg)
            return
        
        test_entry = {}
        if self.expected_info:
            for entry in zd_assigned_ip:
                if entry['mac'].lower() == self.expected_info['mac'].lower():
                    test_entry = entry
        if not test_entry:
            self.errmsg = 'Can not find the entry for device %s to verify' % self.expected_info['mac']
            logging.info(self.errmsg)
            return
        
        if test_entry['ip'] != self.expected_info['ip']:
            errmsg = 'The IP of device[%s] is %s instead of %s as expected'
            self.errmsg = errmsg % (test_entry['mac'], test_entry['ip'], self.expected_info['ip'])
            logging.info(self.errmsg)
            return

    def _read_leasetime(self, leasetime):
        lease_in_secs = 0
        time_re = {'week': '(\d+)w', 'day': '(\d+)d', 'hour': '(\d+)h', 'min': '(\d+)m',  'sec': '(\d+)s'}
        time_mu = {'week': 604800, 'day': 86400, 'hour': 3600, 'min': 60,  'sec': 1}
        
        for key in time_re.keys():
            res = re.findall(time_re[key], leasetime)
            if res:
                lease_in_secs += int(res[0]) * time_mu[key]
        return lease_in_secs