'''
Description:
  Checking WLANs deployed from APs, 8 WLANs per radio if we disabled the mesh function, 
and also support 6 WLANs per radio if we enabled mesh.

Created on 2010-9-19
@author: cwang@ruckuswireless.com
'''
import logging
import re
from RuckusAutoTest.models import Test

class CB_Scaling_Verify_AP_Side_WLANs_From_ZDCLI(Test):
    '''
        Go to ZDCLI shell mode, and use command "remote_ap_cli -A "get wlanlist"" for all of APs information.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        data = self._get_wlans_from_zdcli()
        res = self._check_command_succ_invoke(data)
        if not res:
            logging.warning(data)
            return self.returnResult("FAIL", self.errmsg)
        
        res = self._check_wlans(data)
        if res:
            self.passmsg = 'All of APs deployed WLANs successfully'
        else:
            self.errmsg = "WLANs deployed are failure, please validate."
            return self.returnResult("FAIL", self.errmsg)
        
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key("existing_aps_list"):
            self.aps = self.carrierbag['existing_aps_list']
        else:
            self.aps = self.testbed.get_aps_sym_dict()
        self.aps_num = len(self.aps)  
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.ap_list = self.testbed.get_aps_sym_dict()
        mesh_cfg = self.zd.get_mesh_cfg()  
        self.mesh_enable = mesh_cfg['mesh_enable'] 
        self.errmsg = ''
        self.passmsg = ''
    
    def _get_wlans_from_zdcli(self):
        timeout = 3 * self.aps_num
        try:
            data = self.zdcli.do_shell_cmd('remote_ap_cli -A "get wlanlist"', timeout)
        except Exception, e:
            logging.debug(e.message)
            self.zdcli.login()
            data = self.zdcli.do_shell_cmd('remote_ap_cli -A "get wlanlist"', timeout)
            
        return data
    
    def _check_command_succ_invoke(self, data):
        expr = 'success: (\d+)'        
        res = re.search(expr, data, re.I | re.M)
        if res:
            s_nums = int(res.group(1))
            if s_nums != self.aps_num:
                self.errmsg = 'When invoke command "get wlanlist", expected success: [%d], actual success: [%d]' % (self.aps_num, s_nums)
                logging.error(self.errmsg)
                return False
        return True
    
    def _check_wlans(self, data):
        single_ap_number = 0
        dual_ap_number = 0
        for ap in self.ap_list:
            if int(self.ap_list[ap]['model'][4]) == 6:
                dual_ap_number += 1
            else:
                single_ap_number += 1
                
        expr = 'wlan\d+\s*up\s*AP\s*wlan\d+\s*\d+\s*[a-f-A-F0-9:]{17}'
        res = re.findall(expr, data, re.I | re.M)
        if res:            
            total_wlans = len(res)
            if self.mesh_enable:
                if total_wlans == 6 * single_ap_number + 12 * dual_ap_number:
                    return True
            else:
                if total_wlans == 8 * single_ap_number + 16 * dual_ap_number:
                    return True
        else:
            return False
        
        return False
            