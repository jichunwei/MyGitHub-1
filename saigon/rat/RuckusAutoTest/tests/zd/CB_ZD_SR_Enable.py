'''
modified by west.li 
put active_zd/standby_zd/active_zd_cli/standby_zd_cli in carrierbag after SR enable
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd
from RuckusAutoTest.components.lib.zdcli import show_config
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sys_if

class CB_ZD_SR_Enable(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.make_sure_two_zd_have_same_ip_version()
        self.enable_smart_redundancy(timeout = self.conf['timeout'])
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.carrierbag['active_zd'] = self.active_zd
        self.carrierbag['standby_zd'] = self.standby_zd
        self.testbed.components['ZoneDirector']=self.active_zd
        if self.active_zd==self.zd1:
            self.carrierbag['active_zd_cli']=self.carrierbag['zdcli1']
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli2']
        else:
            self.carrierbag['active_zd_cli']=self.carrierbag['zdcli2']
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli1']
        self.testbed.components['ZoneDirectorCLI']=self.carrierbag['active_zd_cli']
        return self.returnResult('PASS', self.msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.conf  = dict(timeout = 150,)
        self.conf.update(conf)
        self.errmsg = ''
        if self.conf.has_key('zd1') and self.conf.has_key('zd2'):
            self.zd1 = self.carrierbag[self.conf['zd1']]
            self.zd2 = self.carrierbag[self.conf['zd2']]
        else:
            self.zd1 = self.carrierbag['zd1']
            self.zd2 = self.carrierbag['zd2']
        self.share_secret = self.carrierbag['share_secret'] 
        
        if self.conf.has_key('direction') and self.conf['direction']=='from':
            self.direction='from'
        else:
            self.direction='to'
        
    def enable_smart_redundancy(self, timeout = 150):
        logging.info('Verify the Smart Redundancy can be ENABLED via Web UI')
        logging.info('Make sure the ZD1 %s and ZD2 %s smart redundancy with the share secret %s', self.zd1.ip_addr,self.zd2.ip_addr,self.share_secret)
        active_zd=redundancy_zd.enable_pair_smart_redundancy(self.zd1, self.zd2, self.share_secret, timeout = timeout,direction=self.direction)
        if not(None==active_zd):
            self.msg = "The smart redundancy was enabled via WEB UI"
            self.active_zd=active_zd
            if active_zd==self.zd1:
                self.standby_zd=self.zd2
            else:
                self.standby_zd=self.zd1
            self.msg = "The smart redundancy was enabled via WEB UI,active zd is %s,standby zd is %s" % (self.active_zd.ip_addr,self.standby_zd.ip_addr)
            self.msg += "config sync: %s %s %s" % (self.zd1.ip_addr, self.direction, self.zd2.ip_addr) 
        else:
            self.errmsg = "The smart redundancy was NOT enabled via WEB UI"

    def make_sure_two_zd_have_same_ip_version(self, ip_version=const.DUAL_STACK):
        logging.info("Check two ZDs ip version")
        zd1_ip_version = show_config.get_ip_info_via_show_interface(self.carrierbag['zdcli1']).get('ip_version')
        zd2_ip_version = show_config.get_ip_info_via_show_interface(self.carrierbag['zdcli2']).get('ip_version')
        
        if zd1_ip_version == zd2_ip_version:
            logging.info("Two ZDs have the same ip version[%s]" % zd1_ip_version)
        else:
            logging.info("Two ZDs have different ip version, zd1[%s], zd2[%s]" % (zd1_ip_version, zd2_ip_version))
            if ip_version == const.DUAL_STACK:
                conf = {'ip_version': const.DUAL_STACK, 'ipv6':{'ipv6_mode':'auto'}}
                ip_type = const.IPV6
                if zd1_ip_version != ip_version:
                    sys_if.set_sys_if(self.carrierbag['zdcli1'], conf, ip_type)
                    self.zd1.login()
                elif zd2_ip_version != ip_version:
                    sys_if.set_sys_if(self.carrierbag['zdcli2'], conf, ip_type)
                    self.zd2.login()

            
            
            
            
