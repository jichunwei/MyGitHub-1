import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt_inf
class CB_ZD_Enable_Mgmt_Interface(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Enable MGMT IF via GUI')
        try:
            mgmt_inf.enable_mgmt_inf(self.zd, **self.conf)
        
        except Exception, e:
            self.errmsg = "Get FAIL message:[%s]" % e.message
            logging.warning(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
       
        self._update_carrierbag()
        msg = 'Enable the ZD [%s] MGMT IF via GUI' % self.zd.ip_addr
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         ip_addr = '192.168.1.2',
                         net_mask = '255.255.255.0',
                         vlan = 2,
                         zd_tag = '',
                         )
        
        self.conf.update(conf)
        
        zd_tag = self.conf.pop('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
    def _update_carrierbag(self):
        self.carrierbag['mgmt_ip'] = self.conf['ip_addr']
        pass