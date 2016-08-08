'''
after zd upgrade or downgrade,check the version of ap primary and backup img is correct or not
by west.li 2012.03.05
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP


class CB_ZD_Check_Ap_Version_After_Upgrade(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.ap_list=self._get_active_ap_list(self.zd)
        for ap in self.ap_list:
            result,msg=ap.verify_primary_secondary_img_version_after_upgrade(self.basebuild,self.targetbuild)
            if not result:
                self.errmsg = msg+'(%s)'% ap.ip_addr
                break

        if self.errmsg:
            return ('FAIL', self.errmsg)       
        
        msg = 'all ap version is correct'
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        for mac in self.ap_mac_list:
            ap_info=zd.get_all_ap_info(mac)
######zj 20140324 fix ZF-7703
            '''
            (Pdb)  ap_info['status']  :  u'Connected (Root AP)'
            '''
            if ap_info['status'].lower().startswith('connected') :
######zj 20140324 fix ZF-7703
#            if ap_info['status'].lower() == 'connected':
                if self.testbed.mac_to_ap.has_key(mac):
                    zd_active_ap = self.testbed.mac_to_ap[mac]
                else:
                    zd_active_ap = RuckusAP(dict(ip_addr = ap_info['ip_addr'],username='admin',password='admin')) 
                zd_active_ap_list.append(zd_active_ap)
        logging.info('there are %s aps need to check'%len(zd_active_ap_list))
        return zd_active_ap_list    
    
    def _cfgInitTestParams(self,conf): 
        self.errmsg=''
        self.zd = self.testbed.components['ZoneDirector']
        ap_mac_list = conf.get('ap_mac_list')
        if ap_mac_list:
            self.ap_mac_list = ap_mac_list
        else:
            self.ap_mac_list=self.testbed.ap_mac_list
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        if conf['action']=='upgrade':
            self.basebuild=self.carrierbag['base_build_version']
            self.targetbuild=self.carrierbag['target_build_version']
        else:
            self.targetbuild=self.carrierbag['base_build_version']
            self.basebuild=self.carrierbag['target_build_version']
            
        
    