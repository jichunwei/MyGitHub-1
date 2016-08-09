'''
Description:Check AP's device name via ZD CLI's shell mode to call AP's device name,
and make sure all of AP device name are mapping.
Created on 2010-9-19
@author: cwang@ruckuswireless.com
'''
import logging
import re
import time

from RuckusAutoTest.models import Test

class CB_Scaling_Verify_AP_Side_Device_Name_From_ZDCLI(Test):
    '''
    Go to ZD CLI's shell mode, call remote_ap_cli -A "get device_name" for all of AP device name.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
#        import pdb
#        pdb.set_trace()
        data = self._get_device_name()
        if not  self._chk_command_succ_invoke(data):
            return self.returnResult("FAIL", self.errmsg)
        
        if not self._chk_device_name(data):
            return self.returnResult("FAIL", self.errmsg)
                
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "All device name of APs have deployed successfully")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key("existing_aps_list"):
            self.aps = self.carrierbag['existing_aps_list']
        else:
            self.aps = self.testbed.get_aps_sym_dict()
        
        if self.carrierbag.has_key('existed_aps_cfg_list'):
            self.aps_cfg_list = self.carrierbag['existed_aps_cfg_list']
        
        self.aps_num = len(self.aps)    
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
        
    def _get_device_name(self):        
        timeout = self.aps_num * 2 
    	cnt = 3
    	while cnt:		
                try:      
                    data = self.zdcli.do_shell_cmd('remote_ap_cli -A "get device-name"', timeout)
                    break
                except Exception, e:
                    logging.debug(e.message)
                    self.zdcli.login()
                    cnt = cnt - 1
    		if not cnt:
    		    raise e
    	        time.sleep(5)
                            
        return data
        
    def _chk_command_succ_invoke(self, data):
        expr = 'success: (\d+)'
        margin = 10        
        res = re.search(expr, data, re.I | re.M)
        if res:
            s_nums = int(res.group(1))
            if s_nums + margin < self.aps_num:
                self.errmsg = 'When invoke command "get device-name", expected success: [%d], actual success: [%d]' % (self.aps_num, s_nums)
                logging.error(self.errmsg)
                return False
        return True
    
        
    def _chk_device_name(self, data):
        expr = "([a-fA-F0-9:]{17})\s*device name\s*:\s*\'(.*)\'"
        res =  re.findall(expr, data, re.IGNORECASE | re.MULTILINE)
        if res:
            for s in res:
                if not self._chk_cfg(s, self.aps_cfg_list):
                    return False
            
            return True
        else:
            self.errmsg = 'AP configuration from ZDCLI, please check'
            logging.warning(self.errmsg)
            return False
                            
                            
    def _chk_cfg(self, s, target):
        for t in target:
            if s[0] == t['mac']:
                if s[1] == t['device_name']:
                    return True
                else:
                    self.errmsg = 'AP [%s] device name has not deploy correctly,\
                     expected result [%s], actual result [%s]' % (s[0], t['device_name'], s[1])
                    logging.warning(self.errmsg)
                    return False
                
#        self.errmsg = 'AP [%s] has not found from previous configuration list' % s[0]
#        logging.warning(self.errmsg)
                
        return True

    
