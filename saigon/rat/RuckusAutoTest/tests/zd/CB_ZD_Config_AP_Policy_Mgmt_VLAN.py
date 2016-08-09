'''
'''
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
import logging

class CB_ZD_Config_AP_Policy_Mgmt_VLAN(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        if "init" == self.conf['cfg_type']:
            self.carrierbag['ap_mgmt_vlan'] = lib.zd.ap_policy.get_ap_mgmt_vlan(self.zd)
            self.carrierbag['ap_vlan_id'] = self.ap.get_ip_cfg("wan")['vlan']
            #jluh updated @ 2013-05-29
            #force the init ap vlan id to 1(default)
            lib.zd.ap_policy.set_ap_mgmt_vlan(self.zd, **{'mode': 'enable', 'vlan_id': '1'})

            self._update_ap_ins_ip()

            self.passmsg = "Backed up AP Mgmt VLAN settings successfully. %s" % \
                           self.carrierbag['ap_mgmt_vlan']

        if "config" == self.conf['cfg_type']:
            lib.zd.ap_policy.set_ap_mgmt_vlan(self.zd, **self.mgmt_vlan)
            info = lib.zd.ap_policy.get_ap_mgmt_vlan(self.zd)
            
            self._update_ap_ins_ip()
            
            self.passmsg = "Config AP Mgmt VLAN successfully. %s" % info

        if "teardown" == self.conf['cfg_type']:
            lib.zd.ap_policy.set_ap_mgmt_vlan(self.zd, **{'mode': 'enable', 'vlan_id': self.carrierbag['ap_vlan_id']})
            lib.zd.ap_policy.set_ap_mgmt_vlan(
                self.zd, **self.carrierbag['ap_mgmt_vlan']
            )
            
            self._update_ap_ins_ip()
            
            self.passmsg = "AP Mgmt VLAN settings were restored successfully."

        return self.returnResult("PASS", self.passmsg)


    def cleanup(self):
        '''
        '''
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'mgmt_vlan': {
                'mode': "keep",
                'vlan_id': "",
            },
            'cfg_type': "config", #["init", "config", "teardown"]
            'zd_tag': '',
            'ap_tag':'',
        }
        self.conf.update(conf)
        self.mgmt_vlan = self.conf['mgmt_vlan']
        
        zd_tag = self.conf['zd_tag']
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf['ap_tag']:
            self.ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        else:
            APs = self.testbed.components.get('AP')
            if len(APs) >= 1:
                self.ap = APs[0]

        self.errmsg = ""
        self.passmsg = ""

    def _update_ap_ins_ip(self):
        logging.info("wait 10 seconds")
        time.sleep(10)
                
        logging.info("wait all APs connected to ZD")
        self.zd.wait_aps_join_in_zd()
                
        logging.info("update all AP instances IP")
        all_aps_info = self.zd.get_all_ap_info()
        all_aps_ins = self.testbed.components['AP']
        for ap_ins in all_aps_ins:
            for ap_info in all_aps_info:
                if ap_ins.base_mac_addr.upper() == ap_info.get('mac').upper() and ap_info.get('ip_addr') != '':
                    ap_ins.ip_addr = ap_info.get('ip_addr')
