import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
class CB_ZD_Add_Mgmt_Acl(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('add MGMT ACL via GUI')
        self._add_mgmtipacl(**self.conf['mgmtipacl_cfg'])
       
        self._update_carrierbag()
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        return self.returnResult('PASS', "add mgmt acl success")
    
    def cleanup(self):
        pass
    
    def _add_mgmtipacl(self,**cfg):
        try:
            mgmt_ip_acl.create_mgmtipacl(self.zd,cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message :
                self.errmsg += '[mgmtipacl creat failed] %s,' % e.message
                logging.error(e.message)   
                return
        logging.info('mgmtip ACL creat succ')

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.mgmtipacl_cfg = {'name':'mgmt-ip-acl-test',
                'type':'range',
                'addr':'192.168.0.3-192.168.0.253',}
        self.conf = dict(mgmtipacl_cfg=self.mgmtipacl_cfg
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
    def _update_carrierbag(self):
        pass