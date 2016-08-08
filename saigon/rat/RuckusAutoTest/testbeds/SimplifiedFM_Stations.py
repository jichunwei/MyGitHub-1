''' Flex Master testbed '''
import logging

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.common.utils import log_cfg
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components import create_com


class SimplifiedFM_Stations(TestbedBase):
    def __init__(self, testbedinfo, config):
        '''
        4 types of configs: FM, APs, ZDs (optional), Clients (optional)
        '''
        TestbedBase.__init__(self, testbedinfo, config)
        self.testbed_info = testbedinfo

        fmcfg = self.config['FM']
        apcfg = self.config['APs']
        zdcfg = self.config['ZDs'] if 'ZDs' in self.config else []
        clientcfg = self.config['Clients'] if 'Clients' in self.config else []

        self.selenium_mgr = SeleniumManager() # global instance
        self.components.update(dict(
            FM=  create_com(fmcfg['model'], fmcfg, self.selenium_mgr, https=False),
            APs=[create_com(com['model'], com, self.selenium_mgr) for com in apcfg],
            ZDs=[create_com(com['model'], com, self.selenium_mgr) for com in zdcfg],
            Clients=[create_com('client', dict(sta_ip_addr=ip)) for ip in clientcfg],
        ))

        self.components['FM'].start() # start FM WebUI right the way
        if 0: # for debugging
            log_cfg(self.config, 'Testbed Config')
            log_cfg(self.components, 'Testbed Components')

        ''' WARNING
        . since the verification of the ZD testbed is called after each build
          upgrade so putting the verification here to run once at starting time
          for FM testbed
        '''
        self.verify_testbed()



    def verify_testbed(self):
        ''' Loop through the testbed components
            and rely on components to verify themselves '''

        logging.info("Testbed %s: verifying component" % (self.testbed_info.name))
        self.components['FM'].verify_component()
        for ap in self.components['APs']:
            ap.verify_component()

        if 'ZDs' in self.components:
            for zd in self.components['ZDs']:
                zd.verify_component()

        if 'Clients' in self.components:
            for cl in self.components['Clients']:
                cl.verify_component()


    def getApByModel(self, model):
        """
        Returning a list of APs on testbed with the given model
        """
        return [ap for ap in self.components['APs'] \
                   if ap.config['model'].lower() == model.lower()]


    def get_ap_by_model(self, model):
        return self.getApByModel(model)


    def getApByIp(self, ip):
        """
        Returning an AP with given IP address
        In case, there are many APs with the same IP address,
        the first one will be returned.
        """
        for ap in self.components['APs']:
            if ap.ip_addr == ip:
                return ap
        return None


    def get_all_ap_ips(self):
        return [ap.ip_addr for ap in self.components['APs']]


    def get_all_zd_ips(self):
        return [ap.ip_addr for ap in self.components['ZDs']]


    def get_clientByIp(self, ip):
        for client in self.components['Clients']:
            if client.ip_addr == ip:
                return client
        return None


    def get_zd_by_ip(self, ip):
        for zd in self.components['ZDs']:
            if zd.ip_addr == ip:
                return zd
        return None


    def __del__(self):      
        if self.components['FM'].started:
            self.components['FM'].stop()