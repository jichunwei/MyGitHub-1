'''
Restart ZoneDirector from UI
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import node_zd
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common.sshclient import sshclient

class CB_Scaling_Restart_ZD(Test):

    required_components = ["ZoneDirector"]
    parameter_description = {}
        
    def config(self, conf):
        self.conf = conf
        self.zd = self.testbed.components["ZoneDirector"]
        self.zdcli=self.testbed.components['ZoneDirectorCLI']
    
    def test(self):
        bugme.do_trace('restart.test')
        node_zd.restart_zd(self.zd, z_pause4ZDRestart = 5)
        
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
             
        return ("PASS","restart zd successfully")
    
    def cleanup(self):
        pass
    