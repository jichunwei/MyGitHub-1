'''
Description:
    1. Get ZeroIT prov file via Northbound Interface.
    
Create on 2012-8-10
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

class CB_WebPortal_Get_And_Install_Prov_File(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(url="http://192.168.0.2/admin/_portalintf.jsp",
                         data = None,
                         sta_tag = 'sta_1'
                         )
        self.conf.update(conf)
        
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            data = self.conf['data'].replace('"', '\"')
            arg = '{"url":"%s", "data":\'%s\'}' % (self.conf['url'], data)
            toolpath = self.target_station.do_cmd("download_zero_it_via_web_portal", arg)
            if not toolpath:                
                return self.returnResult('FAIL', "Download failure!")
            
            self.target_station.remove_all_wlan()
            
            arg  = '{"tool_path":"%s", "ssid":"", "auth_method":"", "use_radius":""}' % toolpath
            #execute_zero_it(tool_path, ssid, auth_method, use_radius, adapter_name = "")            
            res = self.target_station.do_cmd("execute_zero_it", arg)
            if not eval(res):
                return self.returnResult("PASS", "Download and install success")
            else:
                return self.returnResult("FAIL", "Download and install failure")
            
        except Exception, e:
            import traceback
            logging.warning(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
    
    def cleanup(self):
        self._update_carribag()

