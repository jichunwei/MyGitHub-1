import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt_inf
class CB_ZD_Disable_Mgmt_Interface(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Disable MGMT IF via GUI')
        try:
            mgmt_inf.disable_mgmt_inf(self.zd)
        except Exception, e:
            self.errmsg = "Disable MGMT IF fail: [%s]" % e.message
            logging.warning(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
       
        self._update_carrierbag()
        msg = 'Disable the ZD [%s] MGMT IF via GUI' % self.zd.ip_addr
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(zd_tag='')
        
        self.conf.update(conf)
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
    def _update_carrierbag(self):
#        self.carrierbag['interface'] = self.interface
        pass