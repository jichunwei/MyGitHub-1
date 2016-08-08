"""
This class provide the helping function to reset_factory ZD,
then recover its original mesh configuration and mgmt_vlan.

Calling Procedure:

    from ratenv import *
    from RuckusAutoTest.components.lib import ZD_Reset_factory
    ZD = ZoneDirector.ZoneDirector(dict(ip_addr='192.168.0.2'))
    zdReset = ZD_Reset_factory.ZD_Reset_factory(zD, {}, debug=True)
    (mgmt_vlan, meshcfg) = zdReset.factory_default()
    zdReset = None
    from pprint import pprint
    pprint(mgmt_vlan)
    pprint(meshcfg)

"""
import logging
import time
from pprint import pformat

from RuckusAutoTest.components.lib.zd import te_mgmt_vlan_hlp as TE
from RuckusAutoTest.components import NetgearSwitchRouter as NSR

class ZD_ResetFactory():
    def __init__(self, zdInstance, resetConf, onTestbed = None, **kwargs):
        # 'system_name': 'Ruckus',
        # 'wireless1_name': 'Ruckus-Wireless-1', 'wireless1_enabled': True,
        # 'authentication_open': True,
        # 'guest_wlan_enabled': False, 'guest_wlan_name': 'Ruckus-Guest',
        # 'create_user_account_is_checked': False,
        self.resetConf = {'language': 'English',
                          'mesh_enabled': False,
                          'country_code': 'United States',
                          'dhcp': False,
                          'admin_name': 'admin',
                          'admin_password': ''}
        self.resetConf.update(resetConf)
        self.cfg = dict(debug = False, init = True)
        self.cfg.update(kwargs)
        self.zd = zdInstance
        self.mytestbed = onTestbed
        if self.cfg['init']:
            self.initialize()

    def __del__(self):
        if hasattr(self, 'nsr') and self.nsr:
            self.nsr.close()

    def initialize(self):
        _halt(self.cfg['debug'])
        # default mesh_name
        # self.resetConf['mesh_name'] = "Mesh-"+ self.zd.get_serial_number()
        self.mgmtVlan0 = TE.MVLAN.get_node_mgmt_vlan_info(self.zd) if self.zd.has_mgmt_vlan else {}
        if self.cfg.has_key('new_mesh_conf') and type(self.cfg['new_mesh_conf']) is dict:
            self.meshConf = self.cfg['new_mesh_conf']
        else:
            self.meshConf = self.zd.get_mesh_cfg()
        self._store_mgmt_vlan_info()

    def factory_default(self, **kwargs):
        rcfg = dict(debug = False)
        rcfg.update(kwargs)
        _halt(rcfg['debug'])
        #self.zd.do_login()
        self._reset_factory_and_untag_zd_switch_port()
        self.zd._setup_wizard_cfg(self.resetConf, {}) 
        self._restore_mgmt_vlan_info()
        logging.info("Setup wizard configuration successfully") 
        return self._get_current_cfg()

    def _store_mgmt_vlan_info(self):
        if self.mgmtVlan0:
            if self.mgmtVlan0['zd']['enabled']:
                # ZD mgmt_vlan enabled; in our testbed, it required L3 Switch presented in testbed
                self.l3sw = self.mytestbed.components['L3Switch']
                # Can python's class initialized from its parent instance?
                nsr_conf = dict(ip_addr = self.l3sw.ip_addr,
                                username = self.l3sw.username,
                                password = self.l3sw.password,
                                enable_password = self.l3sw.enable_password)
                self.nsr = NSR.NetgearSwitchRouter(nsr_conf)
                self.mgmtVlan0['swp'] = TE.get_zd_switch_port(self.zd, self.nsr) 
            else:
                self.nsr = None
            logging.info("[ZoneDirector Reset_factory] mgmt_vlan:\n%s" % pformat(self.mgmtVlan0, indent = 4))
 
    def _reset_factory_and_untag_zd_switch_port(self):
        self.wait_for_alive = False if self.mgmtVlan0 and self.mgmtVlan0['zd']['enabled'] else True
        # ZoneDirector._reset_factory() changed to not wait for ZD come alive
        # if ZD MgmtVlan is enabled.
        self.zd._reset_factory(self.wait_for_alive)
        if not self.wait_for_alive:
            # ZD port is tagged; after reset_factory; the port need to be untagged
            TE.NSRHLP.untag_switch_vlan_interface(self.nsr,
                                               self.mgmtVlan0['swp']['vlan_id'],
                                               self.mgmtVlan0['swp']['interface'],)
            # ATTN: step to reset_factoryWaitForAlive() immeidately
            try:
                # ZD is being reset and restarted
                self.zd._reset_factory_wait_for_alive_s1()
            except:
                # ZD is restarted
                self.zd._reset_factory_wait_for_alive_s2()

    def _restore_mgmt_vlan_info(self):
        if self.meshConf['mesh_enable']:
            self.zd.enable_mesh(self.meshConf['mesh_name'], self.meshConf['mesh_psk'])
        if self.mgmtVlan0:
            if self.mgmtVlan0['zd']['enabled']:
                self.mgmtVlan2 = TE.tag_zd_mgmt_vlan(self.zd,
                                                  self.nsr,
                                                  self.mgmtVlan0['swp']['interface'],
                                                  self.mgmtVlan0['swp']['vlan_id'],)
                time.sleep(2)
            ap_mgmt_vlan = self.mgmtVlan0['ap']['mgmt_vlan']
            if ap_mgmt_vlan['enabled'] and ap_mgmt_vlan['vlan_id']:
                if self.mgmtVlan0['ap']['zd_discovery']['enabled']:
                    prim_ip = self.mgmtVlan0['ap']['zd_discovery']['prim_ip']
                    sec_ip = self.mgmtVlan0['ap']['zd_discovery']['sec_ip']
                else:
                    prim_ip = sec_ip = u''
                self.appolicy2 = TE.tag_ap_mgmt_vlan(self.zd,
                                                  ap_mgmt_vlan['vlan_id'],
                                                  prim_ip, sec_ip)
    
    def _get_current_cfg(self):
        self.mgmtVlan2 = TE.MVLAN.get_node_mgmt_vlan_info(self.zd) if self.zd.has_mgmt_vlan else {}
        self.meshConf2 = self.zd.get_mesh_cfg()
        return (self.mgmtVlan2, self.meshConf2)

def _halt(_debug):
    if _debug:
        import pdb
        pdb.set_trace()

