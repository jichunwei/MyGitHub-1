import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
class CB_ZD_Remove_Mgmt_Acl(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('del MGMT ACL via GUI')
        self._del_mgmtipacl(self.conf['name'])
       
        self._update_carrierbag()
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        return self.returnResult('PASS', "remove mgmt acl %s success"%self.conf['name'])
    
    def cleanup(self):
        pass
    
    def _del_mgmtipacl(self,name):
        try:
            mgmt_ip_acl.delete_mgmtipacl(self.zd,name)
        except Exception, e:
            self.errmsg = '[mgmtipacl del failed] %s,' % e.message
            logging.error(e.message)   
            return
        logging.info('mgmtip ACL Del succ')

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = {
                     'name':'mgmt-ip-acl-test'
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
    def _update_carrierbag(self):
        pass