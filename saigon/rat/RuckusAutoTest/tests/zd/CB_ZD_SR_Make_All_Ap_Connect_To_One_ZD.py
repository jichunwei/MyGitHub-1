"""
make all aps connected to one ZD
need ,take parameter 'from_zd' and 'to_zd' in conf
by west.li
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
#        bugme.do_trace('debug')
        self._adjust_ap_to_one_zd(self.to_zd,self.from_zd)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)       
        
        msg = 'all ap moved to zd[%s]' % self.to_zd.ip_addr
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
        if self.conf.has_key('from_zd') and self.conf.has_key('to_zd'):
            self.from_zd=self.carrierbag[self.conf['from_zd']]
            self.to_zd  =self.carrierbag[self.conf['to_zd']]
        else:        
            self.from_zd = self.carrierbag['zd1']
            self.to_zd  = self.carrierbag['zd2']
       

    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        all_ap_in_zd_dict = zd.get_all_ap_info()
        for ap in all_ap_in_zd_dict:
            if ap['status'].lower() == 'connected':
                zd_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin')) 
                zd_active_ap_list.append(zd_active_ap)
        logging.info("ZD %s have %s APs %s" % (zd.ip_addr, len(zd_active_ap_list), zd_active_ap_list))
        return zd_active_ap_list
    
    # adjust all ap in zd2 to zd1    
    def _adjust_ap_to_one_zd(self,zd1,zd2,timeout=600):
        time_start=time.time()
        while True:
            zd2_ap_list = self._get_active_ap_list(zd2)
            zd1_ap_list = self._get_active_ap_list(zd1)
            ap_list=zd1_ap_list+zd2_ap_list
            
            for ap in ap_list:
                while True:
                    res = ap.do_cmd('get director')
                    if time.time()-time_start>timeout/2:
                        break
                    elif 'Currently AP is in state: RUN' in res:
                        break
            zd2_ap_list = self._get_active_ap_list(zd2)
            
            if time.time()-time_start>timeout:
                self._close_ap_telnet(ap_list)
                logging.error('time out when adjust ap to one zd')
                self.errmsg= 'time out when adjust ap to one zd'
                return
            
            if len(zd1_ap_list)==len(ap_list):
                self._close_ap_telnet(ap_list)
                logging.info("ZD %s has %d APs,ZD %s has %d APs" %(zd1.ip_addr,len(zd1_ap_list),zd2.ip_addr,len(zd2_ap_list)))
                return
            
            number_ap_to_move = len(zd2_ap_list)
            cmd = 'set director ip  '+ zd1.ip_addr 
            for i in range(0,number_ap_to_move):                             
                zd2_ap_list[0].do_cmd(cmd)
                zd2_ap_list[0].reboot()
                del zd2_ap_list[0]
#            time.sleep(240)
            
            self._close_ap_telnet(ap_list)
                
    def _close_ap_telnet(self,ap_list):
        for ap in ap_list:
            try:
                ap.close()
            except:
                pass
        
             
                    