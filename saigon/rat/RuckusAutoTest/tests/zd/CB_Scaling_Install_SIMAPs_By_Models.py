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

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import scaling_zd_lib as lib
from RuckusAutoTest.components.lib.simap import image_installer as installer

class CB_Scaling_Install_SIMAPs_By_Models(Test):
    
    required_components = ["ZoneDirector"]
    parameter_description = {}

    def config(self, conf):
        self.conf = dict(vm_ip_addr = '192.168.0.150',
                         tftpserver = '192.168.0.20',
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.agent = self.carrierbag['existed_sim_agent']
        self.sim_version = self.carrierbag['sim_version']        
        self.simaps_models = self.carrierbag['existed_simaps_models']
                
        model_expr = self._retrieve_models(self.simaps_models)        
        self.package_simap_cfg = dict(tftpserver=self.conf['tftpserver'],
                                      model=model_expr,
                                      version=self.sim_version,)
    
    def test(self):
        logging.info('package_sim-cfg [%s]' % self.package_simap_cfg)
        installer.install(self.zdcli, **self.package_simap_cfg)
        logging.info('SIMAP firmware configure successfully')
        
        self._bootup_simaps(self.agent, self.simaps_models)
        if not self._verify_simaps_from_vm(self.agent, len(self.simaps_models)):
            raise Exception('Some of SIMAPs haven\'t boot up correctly, please check.')
                
        logging.info('[Initial]begin verify RuckusAPs and SimAPs, make sure all of them are connected.')
        
        try:        
            self.zd.do_login()
        except:
            pass
        
        lib.verify_aps_by_models(self.zd, self.simaps_models)
        logging.info('[Initial]all of RuckusAPs and SimAPs are connected.')     
        return self.returnResult("PASS", "SIMAP models[%s]" % self.simaps_models)
            
    
    def cleanup(self):
        pass
    
    def _bootup_simaps(self, agent, models):
        simcfg = {   
                'ap_start_mac' : '00:13:92:03:02:00',
                'ap_cnt' : 1,
                'ap_mode':'zf9999',
               }   
        for index in range(len(models)):
            simcfg['ap_mode'] = models[index]
            macID = '00'
            macID = self._convert_hex(index + 1)
            simcfg['ap_start_mac'] = '00:13:92:03:%s:00' % macID
            simcfg['ap_cnt'] = 1
            simcfg['rogue'] = 0            
            simcfg['tap_id'] = index + 1            
            logging.info(simcfg)
            agent.touch_tcfg(simcfg)
            agent.startup_single_simap()
            
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
    
            
    def _verify_simaps_from_vm(self, agent, expect_cnt, timeout=90):
        startT = time.time()
        while True:
            if time.time() - startT < timeout :
                cnt = agent.get_sim_ap_nums()
                if cnt != expect_cnt:
                    logging.info('[%d] SimAPs have started, waiting for another[%d]' % (cnt, expect_cnt - cnt))
                    time.sleep(5)
                    
                else:
                    
                    return True
        return False 
    