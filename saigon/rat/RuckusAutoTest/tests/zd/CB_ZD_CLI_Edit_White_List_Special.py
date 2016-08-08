"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: July 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - 'white_list_name': white list name
       - 'rule_no': rule no index
       - 'rule_type': MAC or MACandIP
       - 'value_type': switch, server, station, zd
       - 'ip_tag':ip or sta_tag, if value_type is switch or server, ip_tag should be ip, 
                                if value_type is station,ip_tag should be station tag
       - expect_failed: negative or not
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Edit white list, edit rule       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: if not negative, configure success, if negative, configure fail.
                FAIL: if not negative, configure fail, if negative, configure success. And if any other item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import white_list


class CB_ZD_CLI_Edit_White_List_Special(Test):
    required_components = ['ZoneDirectorCLI','L3Switch','LinuxServer','Station']
    parameters_description = {'white_list_name':'', 
                              'rule_no':'1',
                              'rule_type':'MAC',#MAC, MACandIP
                              'value_type':'server', #switch, server, station,zd
                              'ip_tag':'192.168.0.252', #ip or sta_tag
                              'expect_failed':False,
                              }
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.info("Edit white list.")
        self._update_ip_mac()
        self._set_rule_conf()
        
        res=white_list.add_rule(self.zdcli, self.white_list_name, self.rule_conf, self.expect_failed)

        if self.expect_failed:
            self.passmsg = 'Edit white list %s, rule %s failed as expected, correct behavior'%(self.white_list_name,self.rule_conf)
            self.errmsg = 'Edit white list %s,rule %s successfully while expect fail, wrong behavior'%(self.white_list_name,self.rule_conf)
        else:
            self.passmsg = 'Edit white list %s,rule %s successfully as expected, correct behavior'%(self.white_list_name,self.rule_conf)
            self.errmsg = 'Edit white list %s,rule %s failed, wrong behavior'%(self.white_list_name,self.rule_conf)
                    
        if not res: 
            return self.returnResult('FAIL', self.errmsg) 
        
        res = self._verify_white_list_exist_or_not()
        if not res: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Wait the modification deploy to AP,after edit white list.")
        time.sleep(25)
        pass

    def _initTestParameters(self, conf):
        self.conf={'white_list_name':'',
                   'rule_no':'1',
                   'rule_type':'MAC',
                   'value_type':'server',
                   'ip_tag':'192.168.0.252',
                   'expect_failed':False,
                   }
        self.conf.update(conf)
        
        self.white_list_name = self.conf['white_list_name']
        self.rule_no= self.conf['rule_no']
        self.rule_type = self.conf['rule_type']
        self.value_type = self.conf['value_type']
        self.ip_tag = self.conf['ip_tag']
        self.expect_failed= self.conf['expect_failed']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

    def _update_ip_mac(self):
        if self.value_type == 'switch' :
            self.ip = self.ip_tag
            self.switch = self.testbed.components['L3Switch']
            self.mac = self.switch.get_mac_by_interface()
        elif self.value_type == 'server' :
            self.ip = self.ip_tag
            self.server = self.testbed.components['LinuxServer']
            if_info = self.server.get_interface_info_by_ip(self.ip)
            self.mac = if_info['mac']
        elif self.value_type == 'station' :
            self.ip = self.carrierbag[self.conf['ip_tag']]['wifi_ip_addr']
            self.mac = self.carrierbag[self.conf['ip_tag']]['wifi_mac_addr']
        elif self.value_type == 'zd' :
            sys_info = self.zdcli.get_system_info()
            self.ip = sys_info.get('IP Address')
            self.mac = sys_info.get('MAC Address')
            if not self.mac:
                logging.info('Get system info: %s'%sys_info)
        
        if not self.mac:
            self.errmsg = "Get mac fail"
            return self.returnResult('FAIL', self.errmsg)
    
    def _set_rule_conf(self):
        rule_conf = {}
        if self.rule_type == "MAC":
            rule_conf[self.rule_no] = {'mac':self.mac}
            self.rule_conf = rule_conf
        elif self.rule_type == "MACandIP":
            rule_conf[self.rule_no] = {'mac':self.mac, 
                                       'ip':self.ip, }
            self.rule_conf = rule_conf
        else:
            self.errmsg = 'The rule type is wrong'
            return self.returnResult('FAIL', self.errmsg)
         
    def _verify_white_list_exist_or_not(self):
        res = white_list.verify_white_list(self.zdcli, self.white_list_name, self.rule_conf)
        if self.expect_failed:
            if res:
                logging.info("Verify success, wrong behavior.")  
                return False
            else:
                logging.info("Verify fail, correct behavior.")
                return True              
        else:
            if res:
                logging.info("Verify success, correct behavior.")
                return True
            else:
                logging.info("Verify fail, wrong behavior.")
                return False