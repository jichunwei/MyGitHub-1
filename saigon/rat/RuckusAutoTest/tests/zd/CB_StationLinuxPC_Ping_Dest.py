"""
"""
import logging

from RuckusAutoTest.models import Test


class CB_StationLinuxPC_Ping_Dest(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        self._test_client_ping_dest()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        return self.returnResult("PASS", self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "",
            'sta_eth': "",
            'condition': "allowed", #["allowed", "disallowed"]
            'ping_timeout_ms': 10 * 1000,
            'target': "172.16.10.252",
        }
        self.conf.update(conf)
        self.sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.ping_params = ""
        if self.conf['sta_eth']:
            if_config = self.sta.get_if_config()
            if if_config.get(self.conf['sta_eth']):
                self.ping_params = "-I %s" % self.conf['sta_eth']

            else:
                logging.info("The given interface %s is not valid." % self.conf['sta_eth'])

        self.target_ip = self.conf['target']

        self.errmsg = ""
        self.passmsg = ""


    def _test_client_ping_dest(self):
        '''
        '''
        ping_result = self.sta.ping(
            self.target_ip, self.conf['ping_timeout_ms'], self.ping_params
        )

        if "allowed" == self.conf['condition']:
            if "Timeout exceeded" in ping_result:
                logging.info("Ping's Failed. INCORRECT behavior.")
                self.errmsg = "The sta %s could not send traffic to %s. INCORRECT behavior." % \
                              (self.conf['sta_tag'], self.target_ip)
                self.errmsg += " " + ping_result

            else:
                logging.info("Ping's Passed. CORRECT behavior.")
                self.passmsg = "Ping's Passed. CORRECT behavior."


        elif "disallowed" == self.conf['condition']:
            if "Timeout exceeded" in ping_result:
                logging.info("Ping's Failed. CORRECT behavior.")
                self.passmsg = "Ping's Failed. CORRECT behavior."

            else:
                logging.info("Ping's Passed. INCORRECT behavior.")
                self.errmsg = "The sta %s could send traffic to %s. INCORRECT behavior." % \
                              (self.conf['sta_tag'], self.target_ip)
                self.errmsg += " " + ping_result

