'''
Description:
    Verify AP Ethernet information by ZD CLI.
    
Created on 2013-1-20
@author: kevin.tan@ruckuswireless.com
'''
import re

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli


class CB_ZD_CLI_Verify_AP_Ethernet_Info(Test):
    '''
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        ap_mac = self.active_ap.base_mac_addr
        
        info = cli.show_ap_info_by_mac(self.zdcli, ap_mac)
        
        if len(info) != 1:
            self.errmsg = 'Dict transition error when showinf AP info in ZDCLI by AP MAC'
            logging.info(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        
        for index in info['AP']['ID']:
            ap_info = info['AP']['ID'][index]['LAN Port']
            for key in ap_info:
                if type(ap_info[key]) is list:
                    #AP Ethernet port is disabled and all info can't be retrieved from AP any more
                    if key != '0':
                        self.errmsg += 'AP interface[%s] name[%s] is unexpected' % (key, inf_name)
                        break
                    for item in ap_info['0']:
                        if item['Interface'] != 'eth0':
                            self.errmsg += 'AP interface name [%s] is unexpected' % (item['Interface'])
                        if 'down' not in item['LogicalLink'].lower():
                            self.errmsg += 'AP interface logical link status[%s] is unexpected, should be up' % (ap_info['LogicalLink'])
                        if 'down' not in item['PhysicalLink'].lower():
                            self.errmsg += 'AP interface physical link status[%s] is unexpected, should be up' % (ap_info['PhysicalLink'])
                    break
                        
                inf_name = ap_info[key]['Interface']
                if inf_name != ('eth%s' % key):
                    self.errmsg += 'AP interface[%s] name[%s] is unexpected' % (key, inf_name)
                    
                logical = ap_info[key]['LogicalLink']
                physical = ap_info[key]['PhysicalLink']
                
                if key == '0' and self.conf['port_status'] == 'enable':
                    if 'up' not in logical.lower():
                        self.errmsg += 'AP interface[%s] logical link status[%s] is unexpected, should be up' % (key, logical)

                    if 'up' not in physical.lower():
                        self.errmsg += 'AP interface[%s] physical link status[%s] is unexpected, should be up' % (key, physical)
                else:
                    if 'up' in logical.lower():
                        self.errmsg += 'AP interface[%s] logical link status[%s] is unexpected, should be down' % (key, logical)

                    if 'up' in physical.lower():
                        self.errmsg += 'AP interface[%s] physical link status[%s] is unexpected, should be down' % (key, physical)

        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = {'port_status': 'enable'}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        
        self.passmsg = ""
        self.errmsg = ""
        