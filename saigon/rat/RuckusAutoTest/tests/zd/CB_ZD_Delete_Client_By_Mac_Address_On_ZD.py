import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Delete_Client_By_Mac_Address_On_ZD(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._get_active_client_by_mac_addr()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._delete_client_by_mac_addr()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        passmsg = "Delete client[%s] on ZD successfully" % self.client_mac              
        return self.returnResult("PASS", passmsg)
        
    def cleanup(self):
        pass
        #self._removeActiveWlansFromWlanGroup()
        #self.carrierbag['active_phone']={}
        
    def _cfgInitTestParams(self, conf):
        self.conf = dict(client_mac='')
        self.errmsg = ''
        self.passmsg = ''
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.client_mac = self.conf['client_mac']
        
    def _get_active_client_by_mac_addr(self, retry=3):
        try:
            active_client = lib.zd.cac.get_active_client_status_by_mac(self.zd, self.client_mac)
        except Exception, e:
            self.errmsg = e.message

    def _delete_client_by_mac_addr(self):        
        logging.info("Delete client[%s] on ZD" % self.client_mac)
        try:
            self.zd.delete_clients(self.client_mac)
        except Exception, e:
            self.errmsg = e.message