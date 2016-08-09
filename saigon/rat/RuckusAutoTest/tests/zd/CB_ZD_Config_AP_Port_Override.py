'''
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Config_AP_Port_Override(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        self._test_config_ap_port_override()

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'ap_tag': "",
            'port_settings': {},
            'cfg_type': "config", #["init", "config", "teardown"]
            'is_negative': False,
            'msg_port_vlan': "VLAN ID must be a value between 1 and 4094",
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.ap_tag = self.conf['ap_tag']

        try:
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        except:
            self.active_ap = self.carrierbag['AP'][self.ap_tag]['ap_ins']

        self.ap_mac_addr = self.active_ap.base_mac_addr
        self.is_negative = self.conf['is_negative']

        self.errmsg = ""
        self.passmsg = ""


    def _config_ap_port_unoverride(self, mac_addr):
        '''
        To apply AP Group config.
        Port Setting    Override Group Config    will be unchecked
        '''
        port_config = {
            'override_parent': False,
        }
        lib.zd.ap.set_ap_port_config_by_mac(self.zd, mac_addr, port_config)


    def _config_ap_port_all_trunk_vid1(self, mac_addr):
        '''
        To override AP Group config.
        Port Setting    Override Group Config    will be checked

        All LAN ports will be set to Trunk Port Type with Untag VLAN ID 1
        Notes:
          - The first 2 (two) ports will be set, leaving the remaining ones unchanged
        '''
        port_config = {
            'override_parent': True,
            'lan1': {
                'enabled': True,
                'type': "trunk",              #[trunk, access, general]
                'untagged_vlan': "1",         #[1-4094, none] (expected String type)
                'vlan_members': "",           #[1-4094] (expected String type)
                'dot1x': "disabled",          #[disabled, supp, auth-port, auth-mac]
            },
            'lan2': {
                'enabled': True,
                'type': "trunk",
                'untagged_vlan': "1",
                'vlan_members': "",
                'dot1x': "disabled",
            },
        }
        lib.zd.ap.set_ap_port_config_by_mac(self.zd, mac_addr, port_config)


    def _config_ap_port_settings(self, mac_addr, **kwargs):
        '''
        The kwargs list forms the keys of settings dict.
        The format is 'lanx_config' where:
         .x is the port number
         .config is the one of the settings of that port

        settings = {
            'lan1_enabled': True,
            'lan1_type': "trunk",
            'lan1_untagged_vlan': "1",
            'lan1_vlan_members': "",
            'lan1_dot1x': "disabled",
        }
        '''
        settings = {}
        settings.update(kwargs)

        port_config = {
            'override_parent': True,
        }

        for k, v in settings.iteritems():
            port = k[:4]
            if not port_config.get(port):
                port_config[port] = {}

            pk = k[5:]
            port_config[port].update({pk: v})

        # now the port_config has been updated
        lib.zd.ap.set_ap_port_config_by_mac(self.zd, mac_addr, port_config)


    def _test_config_ap_port_override(self):
        '''
        '''
        if "init" == self.conf['cfg_type']:
            self._config_ap_port_all_trunk_vid1(self.ap_mac_addr)
            self.passmsg = "All AP LAN ports were set to Trunk, Untag VLAN 1."

        if "config" == self.conf['cfg_type']:
            try:
                self._config_ap_port_settings(
                    self.ap_mac_addr, **self.conf['port_settings']
                )

            except Exception:
                if not self.is_negative and self.zd.s.is_alert_present(6):
                    self.errmsg = "INCORRECT. Invalid port settings were not caught."
                    return

                msg = self.zd.s.get_alert()
                if not msg or self.conf['msg_port_vlan'] in msg:
                    self.passmsg = "CORRECT. Invalid port settings were caught."

                else:
                    self.errmsg = "Unexpected alert message was caught."

                return

            info = lib.zd.ap.get_ap_port_config_by_mac(self.zd, self.ap_mac_addr)
            self.passmsg = "Config active AP [%s %s] LAN ports successfully. %s" % \
                      (self.ap_tag, self.ap_mac_addr, info)

        if "teardown" == self.conf['cfg_type']:
            self._config_ap_port_unoverride(self.ap_mac_addr)
            self.passmsg = "AP LAN ports were un-overridden successfully."

