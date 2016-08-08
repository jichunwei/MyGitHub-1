'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure AP in ZD WebUI: Configure -> Access Points -> Edit.

'''


import logging
import time
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import access_points_zd
import libZD_TestConfig as tconfig

AP_STATE_REGX = {
    'auto': "Connected",
    "root": "Connected \(Root AP\)",
    "mesh": "Connected \(Mesh AP, \d+ hops\)",
    "disabled": "Connected$",
}

class CB_ZD_Config_AP(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureAP()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'push_cfg_time': 60,
                     'check_mesh_timeout': 300}
        self.conf.update(conf)
        self.ap_cfg = dict(general_info = None,
                           radio_config = None,
                           ip_config = None,
                           mesh_config = None,
                           port_config = None,
                           )
        self.ap_cfg.update(self.conf['ap_cfg'])
        if self.conf.has_key('ap_tag') and self.conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.ap_mac = active_ap.base_mac_addr
        else:
            self.ap_mac = self.conf['ap_mac']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _configureAP(self):
        logging.info('Configure AP[%s] in ZD WebUI' % self.ap_mac)
        try:
            if self.ap_cfg['mesh_config']:
                logging.info("Get current mesh configuration on the ZD")
                mesh_conf = self.zd.get_mesh_cfg()
                if not mesh_conf['mesh_enable']:
                    self.errmsg = "Can't configure AP mesh mode, because ZD mesh is disabled"
                    return
            
            access_points_zd.set_ap_config_by_mac(self.zd, self.ap_mac,
                                                  self.ap_cfg['general_info'],
                                                  self.ap_cfg['radio_config'],
                                                  self.ap_cfg['ip_config'],
                                                  self.ap_cfg['mesh_config'])
            
            time.sleep(self.conf['push_cfg_time'])
            if self.ap_cfg['mesh_config']:
                mesh_mode = self.ap_cfg['mesh_config']['mesh_mode']
                start = time.time()
                while True:
                    time.sleep(30)
                    self.zd.refresh()
                    ap_info = lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.ap_mac)
                    if not re.search(AP_STATE_REGX[mesh_mode], ap_info["state"]):
                        if (time.time() - start) > self.conf['check_mesh_timeout']:
                            self.errmsg = "Fail to set the mesh mode of AP[%s] to '%s'" % (self.ap_mac, mesh_mode)
                            return
                    
                    else:
                        break
                        
            self.passmsg = 'Configure AP[%s] in ZD WebUI successfully' % self.ap_mac
            
        except Exception, ex:
            self.errmsg = ex.message
            
            