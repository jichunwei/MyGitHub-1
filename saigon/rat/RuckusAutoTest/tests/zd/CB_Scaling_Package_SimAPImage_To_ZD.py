'''
Description:
Created on 2010-8-2
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:

upgrade by west.li
1.get zd and zdcli in SR
2.get sim ap version in conf
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.simap import image_installer as installer

class CB_Scaling_Package_SimAPImage_To_ZD(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        if self.conf.has_key('sim_version'):
            self.sim_version=self.conf['sim_version']
        self._retrive_carrier_bag()
        
        self.package_simap_cfg = dict(tftpserver=self.conf['tftpserver'],
                                      model=self.conf['sim_models'],
                                      version=self.sim_version,
                                      img=self.conf['sim_img'])
        
    def test(self):
        passmsg = []
        if self.carrierbag.get('skip_packet_sim_ap'):
            return self.returnResult("PASS", 'not need use sim ap')
        
        logging.info('package_sim-cfg [%s]' % self.package_simap_cfg)
        
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
            
        installer.install(self.zdcli, **self.package_simap_cfg)
           
        try:        
            self.zd.do_login()
        except:
            pass
        
        self.passmsg = 'SIMAP firmware configure successfully' 
        logging.info(self.passmsg)       
        self._update_carrier_bag()
        passmsg.append(self.passmsg)
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.conf.has_key('build') and self.conf['build']=='base':
            self.sim_version=self.carrierbag['base_simap_version']
            self.conf['sim_img'] = self.carrierbag['base_simap_file']
        else:
            self.sim_version=self.carrierbag['target_simap_version']
            self.conf['sim_img'] = self.carrierbag['target_simap_file']

        self.conf['tftpserver']=self.carrierbag['tftp_server']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(simap_models = 'ss2942 ss7942 ss7962',
                         tftpserver = '192.168.0.10',)
        self.conf.update(conf)
        
        if self.testbed.components.has_key('ZoneDirector') and self.testbed.components.has_key('ZoneDirectorCLI'):
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli = self.testbed.components['ZoneDirectorCLI']   
        if self.testbed.components.has_key('zd1')and self.testbed.components.has_key('ZDCLI1'):
            self.zd = self.testbed.components['zd1']                
            self.zdcli = self.testbed.components['ZDCLI1'] 
        if self.conf.has_key('zd'):
            if self.conf['zd']== 'standby':
                self.zd = self.carrierbag['standby_zd']
                self.zdcli = self.carrierbag['standby_zd_cli']
            elif self.conf['zd']== 'active':
                self.zd = self.carrierbag['active_zd']
                self.zdcli = self.carrierbag['active_zd_cli']
            elif self.conf['zd']== 'zd1':
                self.zd = self.carrierbag['zd1']
                self.zdcli = self.carrierbag['zdcli1']
            elif self.conf['zd']== 'zd2':
                self.zd = self.carrierbag['zd2']
                self.zdcli = self.carrierbag['zdcli2']
                
                            
        self.errmsg = ''
        self.passmsg = ''
