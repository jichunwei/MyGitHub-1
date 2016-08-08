
import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib
import time

class CB_ZD_Create_Active_AP(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        self._create_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag[self.ap_tag]['ap_ins'] = self.active_ap
        self.carrierbag[self.ap_tag]['ap_mac'] = self.active_ap.get_base_mac().lower()
        passmsg = 'Create active AP [%s %s] successfully' % (self.active_ap.get_ap_model(), self.active_ap.get_base_mac())
        return self.returnResult('PASS', passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap_symbolic_name = self.conf['active_ap']
        self.ap_tag = self.conf['ap_tag']
        self.carrierbag[self.ap_tag] = dict()

    def _create_ap(self):
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.active_ap_symbolic_name)
        if not self.active_ap:
            self.errmsg = "Active AP [%s] not found in testbed." % self.active_ap_symbolic_name
            return

        #'ap_info':{'apgroup_name': name, 'apgroup_ipmode': grp_mode, 'ap_ipmode': ap_mode}
        if self.conf.has_key('ap_info'):
            apmac = self.active_ap.base_mac_addr
            info = self.conf['ap_info']
            
            if info.has_key('apgroup_name'):
                try:
                    ap_group.set_ap_group_ip_mode_by_name(self.zd, info['apgroup_name'], info['apgroup_ipmode'])
                except:
                    ap_group.create_ap_group(self.zd, info['apgroup_name'])
                    ap_group.set_ap_group_ip_mode_by_name(self.zd, info['apgroup_name'], info['apgroup_ipmode'])
            
                lib.zd.ap.set_ap_general_by_mac_addr(self.zd, apmac, ap_group=info['apgroup_name'])

            if info.has_key('ap_ipmode'):
                lib.zd.ap.set_ap_network_setting_by_mac(self.zd, apmac, info['ap_ipmode'])

            time0 = time.time()
            wait_time = 300
            while(True):
                current_time = time.time()
                if  (current_time-time0) >wait_time:
                    self.errmsg = "Active AP [%s] not connected in %s second after change IP mode and move AP group." % (self.active_ap_symbolic_name, wait_time)
                    return
                try:
                    ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, apmac)
                    if ap_info['state'].lower().startswith('connected'):
                        break
                except:
                    pass
    
                time.sleep(3)
