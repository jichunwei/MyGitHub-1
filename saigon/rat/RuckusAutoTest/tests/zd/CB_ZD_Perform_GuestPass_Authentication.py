'''
'''
import time
import logging

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig


class CB_ZD_Perform_GuestPass_Authentication(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

        self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()[1]


    def test(self):
        guest_pass = self.gp_cfg_list[1][1]
        self._perform_gp_auth(guest_pass)

        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)


    def cleanup(self):
        pass


    def _retrive_carrier_bag(self):
        self.gp_cfg_list = self.carrierbag['existed_guest_passes_record']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']


    def _update_carrier_bag(self):
        pass


    def _init_test_params(self, conf):
        self.conf = {'sta_tag': '',
                     'check_status_timeout': 100,
                     'use_tou': False,
                     'redirect_url': ''}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''


    def _perform_gp_auth(self, guest_pass = ''):
        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())
        time.sleep(5)

        arg = tconfig.get_guest_auth_params(self.zd, guest_pass, self.conf['use_tou'], self.conf['redirect_url'])
        self.target_station.perform_guest_auth(arg)

        logging.info("Verify information of the target station shown on the ZD")
        client_info_on_zd = None
        start_time = time.time()
        found = False

        while True:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    client_info_on_zd = client
                    if client['status'] == 'Authorized':
                        found = True
                        break

            if found:
                logging.debug("Active Client: %s" % str(client_info_on_zd))
                logging.info("The status of station is %s now" % client_info_on_zd['status'])
                break

            if time.time() - start_time > self.conf['check_status_timeout']:
                if client_info_on_zd:
                    logging.debug("Active Client: %s" % str(client_info_on_zd))
                    errmsg = "The station status shown on ZD is %s instead of 'Authorized' after doing Guest authentication. " % client_info_on_zd['status']
                    self.errmsg = self.errmsg + errmsg
                    logging.debug(errmsg)
                    return False

                if not client_info_on_zd:
                    logging.debug("Active Client list: %s" % str(active_client_list))
                    errmsg = "ZD didn't show any info about the target station (with MAC %s). " % self.sta_wifi_mac_addr
                    self.errmsg = self.errmsg + errmsg
                    logging.debug(errmsg)
                    return False

        return True
