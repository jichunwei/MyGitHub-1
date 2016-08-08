'''
Description:Verify how many APs are managed at current ENV.
Created on 2012-1
@author: west.li@ruckuswireless.com 
'''
import time,logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import scaling_zd_lib
from RuckusAutoTest.common.sshclient import sshclient

class CB_Scaling_Verify_APs_Num(Test):
    '''
    Check from ZDCLI, just verify APs number.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):  
        try:
            self.zdcli.do_cmd('')
        except:
            logging.info('zdcli disconnected,let\'s log in again')
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
        
        res,num = scaling_zd_lib.check_aps_num_from_cmd(self.zdcli, self.conf['aps_num'], time_out = self.conf['timeout'])
        if not res:
            return self.returnResult('FAIL', 'Expected aps [%d] have not been managed correctly(only %d left)' % (self.conf['aps_num'],num))
        else:
            if self.carrierbag.get('port_disable_time'):
                sec_zd_switch_time = time.time() - self.carrierbag['port_disable_time']
                logging.info('it takes totally %s seconds for %s aps switch to secondary zd'%(sec_zd_switch_time,self.conf['aps_num']))
            if self.carrierbag.get('pri_zd_sw_enable_time'):
                pri_zd_switch_time = time.time() - self.carrierbag['pri_zd_sw_enable_time']
                logging.info('it takes totally %s seconds for %s aps switch back to pri zd'%(pri_zd_switch_time,self.conf['aps_num']))
            
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Expected aps [%d] have been managed correctly' % self.conf['aps_num'])
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('managed_ap_num'):
            self.conf['aps_num']=self.carrierbag['managed_ap_num']
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf= dict(timeout = 1800,                         
                        aps_num = 250,
                        chk_gui = False)
        self.conf.update(conf)        
        self.chk_gui = self.conf['chk_gui']
        self.timeout = self.conf['timeout']   
        if self.testbed.ap_mac_list:
            self.conf['aps_num'] = len(self.testbed.ap_mac_list)     
        if self.testbed.components.has_key('ZoneDirectorCLI'):                            
            self.zdcli = self.testbed.components['ZoneDirectorCLI'] 
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        self.passmsg = ""
        self.errmsg = ""   
    
