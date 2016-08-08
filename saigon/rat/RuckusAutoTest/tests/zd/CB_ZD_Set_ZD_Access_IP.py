# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

'''
set zd web or cli access ip addr
'''
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient


class CB_ZD_Set_ZD_Access_IP(Test):
    
    
    def config(self, conf):
        self.conf={
                   'zd_ip':'192.168.0.2',
                   'login_name':'admin',
                   'login_pass':'admin',
                   'web':True,
                   'cli':True
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli=self.testbed.components['ZoneDirectorCLI']
        
        if self.carrierbag.has_key('zd_ip'):
            self.zd_ip = self.carrierbag['zd_ip']
        else:
            self.zd_ip=self.zd.ip_addr
            
        if self.carrierbag.has_key('zdcli_ip'):
            self.zdcli_ip = self.carrierbag['zdcli_ip']
        else:
            self.zdcli_ip=self.zdcli.ip_addr 
        
        if self.conf['cli']:
            self.zdcli.ip_addr=self.zdcli_ip
            self.zdcli.username = self.conf['login_name']
            self.zdcli.password = self.conf['login_pass']
            self.passmsg='access zd cli by ip(%s) successfully'%self.zdcli_ip
            
        if self.conf['web']:
            self.zd.ip_addr=self.zd_ip
            self.zd.username = self.conf['login_name']
            self.zd.password = self.conf['login_pass']
            self.zd.conf['url.login'] = "https://%s/admin/login.jsp"%self.zd_ip
            self.passmsg='access zd web by ip(%s) successfully'%self.zd_ip
        
        if self.conf['web'] and self.conf['cli']:
            self.passmsg='access zd web and cli by ip(%s) successfully'%self.zd_ip
            
        self.errmsg = ""        
            
    def test(self):   
        try:  
            if self.conf['cli']:        
                self.zdcli.logout()        
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,self.conf['login_name'],self.conf['login_pass'])
                self.zdcli.login()
            
            if self.conf['web']:
                self.zd.do_login()
        except Exception,e:
            self.errmsg = e.message
        
        if self.errmsg:
            return ("FAIL",self.errmsg)
        return ("PASS",self.passmsg) 
                    
    def cleanup(self):
        pass
    

    def _update_carrier_bag(self): 
        pass
        
                
