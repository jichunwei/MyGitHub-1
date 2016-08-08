'''
Description:
Reboot all APs from GUI, which reboot will toggle reboot button from ZD's Access Points.
Created on 2010-9-7
'''
import logging
import re

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.lib.zd import scaling_zd_lib as SCALING 
#from RuckusAutoTest.components import RuckusAP
#from RuckusAutoTest.common import lib_Debug as bugme
#from RuckusAutoTest.components import Helpers as lib
class CB_ZD_Scaling_APs_Reboot(Test):
    '''
    Reboot all APs from GUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        #if not self.aps:
        #    self.aps = self.testbed.get_aps_sym_dict()        
    
    def test(self):
        #Because reboot from AP's CLI is too slow when reboot 500APs, so change it reboot from ZD's GUI directly.
        try:
            data = self._reboot_aps_from_zdcli()
            if not self._check_command_succ_invoke(data):
                return self.returnResult("FAIL", "Some of APs haven't reboot successfully, detail [%s]" % data)
#            self.zd.restart_aps()
        except Exception, e:
            return self.returnResult("FAIL", "When try to reboot APs, failure reason [%s]" % e.message)

#        for ap in self.aps.values():        
#            mac_addr = ap['mac']
#            try:
#                bugme.do_trace('test_r')
#                ip_addr = SCALING.get_ap_ip_addr_by_ap_mac(self.zdcli, mac_addr)
#            except Exception, e:
#                logging.warning(e.message)
#                return self.returnResult("FAIL", "AP[%s] haven't been managed by ZD" % mac_addr)
            
#            try:    
#                active_ap = RuckusAP.RuckusAP(dict(ip_addr = ip_addr, username = self.ap_username, password = self.ap_password, ))
#                logging.info("reboot AP [%s %s]" % (mac_addr, ip_addr))
#                active_ap.tn.write("reboot\n")
#            except Exception, e:
#                logging.warning(e.message)
#                return self.returnResult("FAIL", "AP[%s, %s] can't reboot correctly, please see failure reason:[%s]" % (mac_addr, ip_addr, e.message))
        
        return self.returnResult("PASS","All of APs reboot successfully")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key("existing_aps_list"):
            self.aps = self.carrierbag['existing_aps_list']
        else:
            self.aps = self.testbed.get_aps_sym_dict()
        self.aps_num = len(self.aps)          
        #if self.carrierbag.has_key("existing_aps_list"):
        #    self.aps = self.carrierbag['existing_aps_list']        
                    
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
#        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        #self.ap_username = self.zd.username
        #self.ap_password = self.zd.password        
        #self.aps = None
        self.errmsg = ''
        self.passmsg = ''
    
    
    def _reboot_aps_from_zdcli(self):
        #zj_20131217 fix zf-6650  timeout from '3' to '5'
        timeout = 5 * self.aps_num
        try:
            data = self.zdcli.do_shell_cmd('remote_ap_cli -A "reboot"', timeout)
        except Exception, e:
            logging.debug(e.message)
            self.zdcli.login()
            data = self.zdcli.do_shell_cmd('remote_ap_cli -A "reboot"', timeout)
            
        return data
    
    def _check_command_succ_invoke(self, data):
        margin = 10 
        expr = 'success: (\d+)'        
        res = re.search(expr, data, re.I | re.M)
        if res:
            s_nums = int(res.group(1))
            if s_nums + margin < self.aps_num:
                self.errmsg = 'When invoke command "reboot", expected success: [%d], actual success: [%d]' % (self.aps_num, s_nums)
                logging.error(self.errmsg)
                return False
        return True
        
