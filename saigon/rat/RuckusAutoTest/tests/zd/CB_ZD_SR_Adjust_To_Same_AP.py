import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_ruckus_ap_by_ip_addr
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Adjust_To_Same_AP(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
#        bugme.do_trace('debug')
        num=self._adjust_to_same(self.zd1,self.zd2)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)       
        
        msg = 'Two ZDs have same APs(%s)' % num
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
                
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
       

    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        all_ap_in_zd_dict = zd.get_all_ap_info()
        for ap in all_ap_in_zd_dict:
            if ap['status'].lower() == 'connected':
                zd_active_ap = create_ruckus_ap_by_ip_addr(**dict(ip_addr = ap['ip_addr'],username='admin',password='admin')) 
                zd_active_ap_list.append(zd_active_ap)
        
        return zd_active_ap_list
        
    def _adjust_to_same(self,zd1,zd2,timeout=600):
        time_start=time.time()
        while True:
            zd1_ap_list = self._get_active_ap_list(zd1)
            zd2_ap_list = self._get_active_ap_list(zd2)
            ap_list=zd1_ap_list+zd2_ap_list
            
            if time.time()-time_start>timeout:
                self._close_ap_telnet(ap_list)
                logging.error('time out when adjust zd have same ap')
                self.errmsg= 'time out when adjust zd have same ap'
                return 0
            
            if len(zd1_ap_list) == len(zd2_ap_list):
                self._close_ap_telnet(ap_list)
                return len(zd1_ap_list)
            
            elif len(zd1_ap_list) > len(zd2_ap_list):
                    number_ap_to_move = (len(zd1_ap_list) - len(zd2_ap_list)) / 2
                    cmd = 'set director ip  '+ zd2.ip_addr 
                    for i in range(0,number_ap_to_move):
                        zd1_ap_list[i].do_cmd(cmd)
                        zd1_ap_list[i].reboot()
                        del zd1_ap_list[i]  
                    
            elif len(zd1_ap_list) < len(zd2_ap_list):
                    number_ap_to_move = (len(zd2_ap_list) - len(zd1_ap_list)) / 2
                    cmd = 'set director ip  ' + zd1.ip_addr 
                    for i in range(0,number_ap_to_move):
                        zd2_ap_list[i].do_cmd(cmd)
                        zd2_ap_list[i].reboot()
                        del zd2_ap_list[i]
            self._close_ap_telnet(ap_list)
            
            
    def _close_ap_telnet(self,ap_list):
        for ap in ap_list:
            try:
                ap.close()
            except:
                pass
                            
