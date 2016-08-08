'''
Description:
    Get xml file from ZD via HTTP request, and convert into dict.
          return PASS, if grab and convert successfully.
          return FAIL, if parse or convert unsuccessfully.
Notes:
    Be used for second change to grab xml data from ZD, in order to compare twice result.
Create on 2013-8-7
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import statistic_report as LIB

class CB_Statistic_Pull_XML_Next(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_xml_data_cfg_next'] = self._cfg
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        ip_addr = self.zd.ip_addr
        username = self.zd.username
        password = self.zd.password
        try:
            _data = LIB.get_xml_data(ip_addr, username, password)
            self._cfg = LIB.convert2dict(_data)
            self._update_carribag()
            return self.returnResult('PASS', 'Grab xml data and Convert2Dict Successful')
        except Exception, e:
            import traceback
            logging.info(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        pass