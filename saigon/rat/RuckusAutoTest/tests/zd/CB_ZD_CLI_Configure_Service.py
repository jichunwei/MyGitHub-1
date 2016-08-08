'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure service in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import service


class CB_ZD_CLI_Configure_Service(Test):
    def config(self, conf):
        self._initTestParameters(conf)
        self._retrieve_carribag()

    def test(self):
        self._configureService()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'service_cfg': '',
                     'restore': False}
        self.conf.update(conf)
        
        self.service_cfg = self.conf['service_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        if self.conf['restore']:
            self.service_cfg = self.carrierbag['bak_service_info']
        
    def _configureService(self):
        try:
            res, msg = service.configure_service(self.zdcli, self.service_cfg)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
            