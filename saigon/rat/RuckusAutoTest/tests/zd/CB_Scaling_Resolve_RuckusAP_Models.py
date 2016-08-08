# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
import logging
import time

from u.zd.scaling.lib import scaling_zd_lib as lib
from u.zd.simap import simap_vm_controller as controller

from RuckusAutoTest.models import Test

class CB_Scaling_Resolve_RuckusAP_Models(Test):
    
    required_components = ['ZoneDirector']
    parameter_description = {'vm_ip_addr':'172.18.35.150',
                             'tftpserver':'192.168.0.20',}
    
    def config(self, conf):
        self.conf = dict(chk_time_out = 200)        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.chk_time_out = self.conf['chk_time_out']        
    
        
    def test(self):
        self._stop_simap_server()   
                                                
        self.zd.remove_approval_ap()        
        if not self._verify_ruckus_aps():
            return self.returnResult("FAIL", "Some of APs haven't managed after [%s] seconds" % self.chk_time_out)   
                
        rks_ap_models = lib.retrieve_aps_models(self.zd)
        self.simaps_models = self._convert_models(rks_ap_models)
        self.models_expr = self._retrieve_models(self.simaps_models)
        self._update_carribag()
        return self.returnResult("PASS", "models[%s]" % self.models_expr)
        
        
    def cleanup(self):
        pass
    
    
    def _update_carribag(self):
        self.carrierbag['existed_simaps_models'] = self.simaps_models
        self.carrierbag['ruckus_aps'] = self.ruckus_aps
    
    def _stop_simap_server(self):
        #Stop SIMAP server.
        vmcfg = dict(ipaddr=self.conf['vm_ip_addr'])
        agent = controller.SimAPsAgent()
        agent.touch_tcfg(vmcfg)
        agent.connect_te()
        agent.shutdown_simaps()
        
        
    def _verify_ruckus_aps(self):
        logging.info('Try to remove all of APs, make sure just RuckusAPs are managed')
        start_time = time.time()
        all_connected = False
        while time.time() - start_time < self.chk_time_out:            
            self.ruckus_aps = self.zd.get_all_ap_info()
            if not self._verify_aps_from_testbed(self.ruckus_aps):
                logging.info('Some of APs have not been managed')
                time.sleep(10)
            else:
                all_connected = True
                break
                        
        return all_connected

    def _convert_models(self, models=['zf2942']):
        expect_models = []
        for model in models:
            if model.index('zf') == 0:
                expect_models.append(model.replace('zf', 'ss'))
                        
        return expect_models

            
    def _convert_hex(self, index):
        if index < 15 :
            return hex(index).replace('0x', '0').upper()
        
        elif index < 256 :
            return hex(index).replace('0x', '').upper()
        
        raise Exception('out of range [0,255]')                    
    

    def _retrieve_models(self, models=['ss2942']):
        modelsStr = ""
        for model in models:
            if modelsStr == "":
                modelsStr = model
                
            else:
                modelsStr = modelsStr + " " + model
                
        return str(modelsStr)   
            
    def _verify_aps_from_testbed(self, aplist):        
        ap_list = self.testbed.get_aps_sym_dict_as_mac_addr_list()
        for ap in aplist :
            if not ap['mac'] in ap_list:
                return False
        
        return True
                