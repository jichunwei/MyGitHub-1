"""
make all aps connected to one ZD
need ,take parameter 'from_zd' and 'to_zd' in conf
by west.li
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Let_Mesh_AP_Connect_To_Standby_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
#        bugme.do_trace('debug')
        cmd = 'set director ip  '+ self.zd_ip 
        for ap in self.ap_list:
            ap.do_cmd(cmd)
            time.sleep(5)
            ap.do_cmd('reboot')
        if self.errmsg:
            return ('FAIL', self.errmsg)       
        
        msg = 'ap moved to zd[%s]' % self.zd_ip
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         )
        self.conf.update(conf)
        self.zd_ip=self.carrierbag['standby_zd'].ip_addr
        self.ap_ip_list=self.carrierbag['mesh_ap_ip_list']
        self.ap_list=[]
        for ip in self.ap_ip_list:
            ap=RuckusAP(dict(ip_addr = ip,username='admin',password='admin')) 
            self.ap_list.append(ap)

                
    def _close_ap_telnet(self,ap_list):
        for ap in ap_list:
            try:
                ap.close()
            except:
                pass
        
             
                    