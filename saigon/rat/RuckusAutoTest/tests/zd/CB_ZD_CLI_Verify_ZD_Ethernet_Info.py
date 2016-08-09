'''
Description:
    Verify ZD Ethernet information by ZD CLI.
    
Created on 2013-1-20
@author: kevin.tan@ruckuswireless.com
'''
import re
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import zd_info_cli as cli


class CB_ZD_CLI_Verify_ZD_Ethernet_Info(Test):
    '''
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        info = cli.show_zd_eth_info(self.zdcli)
        zd_mac = self.zd.mac_addr
        
        #Verify active port 0
        ethinfo = info['System Ethernet Overview']['Port  0']

        val = ethinfo['Interface']
        if val.lower() != 'eth0':
            self.errmsg = 'Interface name of Ethernet port 0 is %s, should be eth0!' % val
            
        val = ethinfo['Physical Link']
        if val.lower() != 'up':
            self.errmsg = 'Physical Link of Ethernet port 0 is %s, should be up!' % val

        val = ethinfo['Speed']
        if val.lower() != '1000mbps':
            self.errmsg = 'Speed of Ethernet port 0 is %s, should be 1000Mbps!' % val

        val = ethinfo['MAC Address']
        if val.lower() != zd_mac.lower():
            self.errmsg = 'MAC Address of Ethernet port 0 is %s, should be %s!' % (val, zd_mac)

        #Verify active port 1
        ethinfo = info['System Ethernet Overview']['Port  1']

        val = ethinfo['Interface']
        if val.lower() != 'eth1':
            self.errmsg = 'Interface name of Ethernet port 1 is %s, should be eth1!' % val
            
        val = ethinfo['Physical Link']
        if val.lower() != 'down':
            self.errmsg = 'Physical Link of Ethernet port 1 is %s, should be down!' % val

        val = ethinfo['Speed']
        if val.lower() != '1000mbps':
            self.errmsg = 'Speed of Ethernet port 1 is %s, should be 1000Mbps!' % val

        
        if self.errmsg:
            logging.info('self.errmsg')
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.passmsg = ""
        self.errmsg = ""
        