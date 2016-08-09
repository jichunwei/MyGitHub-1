'''
Description:

This function is used to set mesh mode and uplink for AP


Created on 2012-12-18
@author: zoe.huang@ruckuswireless.com
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Configure_AP_Mesh(Test):
    required_components = ['Zone Director', 'Active AP']
    test_parameters = {'mesh_mode':'auto root, mesh, disable can be set',
                       'uplink_option':'smart and manual can be set to uplink mode',
                       'active_ap': 'the AP symbolic name'}

    def config(self, conf):
        self._init_test_parameters(conf)
        self._cfg_active_ap()

    def test(self):
        # Verify if Mesh is enabled on ZD, if not raise exception
        if not self.zd.get_mesh_cfg()['mesh_enable']:
            raise Exception('Mesh option is not enabled on Zone Director. The test will be broken')

        # Force AP Mesh mode base on the test parameters
        logging.info('set AP[%s] to mesh : %s' % (self.active_ap.base_mac_addr, str(self.mesh_cfg)))
        self._cfg_ap_mesh_mode()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        logging.info('Verify if mesh is set successfully.')
        self._test_ap_mesh_mode()
        if self.errmsg:
            return ('FAIL', 'Set mesh of AP[%s] to %s failed,error message %s' % (self.active_ap.base_mac_addr, str(self.mesh_cfg),self.errmsg))
        self.passmsg = 'Set mesh mode of AP[%s] to %s successfully' % (self.active_ap.base_mac_addr, str(self.mesh_cfg))
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    # Configuration
    def _init_test_parameters(self, conf):
    
        self.conf = {'mesh_cfg':{ 'mesh_mode':'auto',
                                  'uplink_option': {'uplink_mode': 'smart',
                                                    'uplink_aps': []}
                                },
                     'ap_tag':'',
                     'check_status_timeout': 180}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = None
        self.mesh_cfg = self.conf['mesh_cfg']

        self.errmsg = ''
        self.passmsg = ''

    def _cfg_active_ap(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']

    def _cfg_ap_mesh_mode(self):
        current_mesh_mode = lib.zd.ap.get_ap_mesh_config_by_mac(self.zd, self.active_ap.base_mac_addr)['mesh_mode']
        #current_mesh_mode = lib.zd.ap.get_cfg_info_by_mac_addr(self.zd, self.active_ap.base_mac_addr)['mesh_mode']
        if current_mesh_mode.lower() != self.mesh_cfg['mesh_mode'].lower():
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, self.mesh_cfg)

            self._verify_is_ap_reboot()
            if self.errmsg:
                logging.info(self.errmsg)
                return

            self._test_ap_connection_status()
            if self.errmsg:
                logging.info(self.errmsg)
                return
        else:
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, self.mesh_cfg)
            time.sleep(15)

    def _verify_is_ap_reboot(self, reboot_timeout = 60):
        start_time = time.time()
        time_out = time.time() - start_time
        rebooted = True

        while time_out < reboot_timeout:
            time_out = time.time() - start_time
            try:
                current_uptime = self.active_ap.get_up_time()
                if current_uptime['days'] is None and current_uptime['hrs'] is None :
                    run_time = 0
                    if current_uptime['mins']:
                        run_time = int(current_uptime['mins']) * 60
                    run_time = run_time + int(current_uptime['secs'])
                    if run_time < reboot_timeout + 15 :
                        rebooted = True
                        break
                else :
                    rebooted = False
                time.sleep( 3 )

            except Exception, e:
                rebooted = True
                # logging.info('exception info: %s' % e.message)
                if e.message.__contains__('haven\'t matched the uptime info'):
                    raise e
                logging.info('Active AP is rebooting')
                time.sleep(10)
                break

        if not rebooted:
            msg = 'AP [%s] does not reboot after %s seconds'
            self.errmsg = msg % (self.active_ap.base_mac_addr, repr(reboot_timeout))


    def _test_ap_connection_status(self, expected_status = 'Connected'):
        # Wait until AP reboot successfully
        start_time = time.time()
        time_out = time.time() - start_time
        flag = False

        while time_out < self.conf['check_status_timeout']:
            time_out = time.time() - start_time
            ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)
            if expected_status in ap_info['status']:
                if expected_status != 'Disconnected':
                    try:
                        self.active_ap.verify_component()
                    except:
                        time.sleep(30)
                        self.active_ap.verify_component()                        
                flag = True
                break
            time.sleep(30)

        if not flag:
            msg = 'AP [%s] is still %s instead of %s after %s'
            self.errmsg = msg % (self.active_ap.base_mac_addr, ap_info['status'], expected_status,
                                 self.conf['check_status_timeout'])

    def _test_ap_mesh_mode(self):
        mesh_info = lib.zd.ap.get_ap_mesh_config_by_mac(self.zd,self.active_ap.base_mac_addr)
        if mesh_info['mesh_mode'].lower() != self.mesh_cfg['mesh_mode'].lower():
            self.errmsg = 'The AP Mesh mode is "%s" instead of %s' % (mesh_info['mesh_mode'], self.mesh_cfg['mesh_mode'])
            return
        if self.mesh_cfg.has_key('uplink_option'):
            if mesh_info['mesh_param']['uplink_mode'].lower()!= self.mesh_cfg['uplink_option']['uplink_mode']:
                self.errmsg = 'The AP uplink mode is "%s" instead of %s' % (mesh_info['mesh_param']['uplink_mode'], self.mesh_cfg['uplink_option']['uplink_mode'])
                return
        ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)
        msg = '[Corrected Info] AP status is "%s" with Mesh mode is "%s"'
        logging.info(msg % (ap_info['status'], ap_info['mesh_mode']))
