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
import time
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import scaling_zd_lib as lib
from RuckusAutoTest.components.lib.simap import image_installer as installer

class CB_Scaling_Upgrade_SIMAP(Test):
    
    required_components = ["ZoneDirector"]
    parameter_description = {}

    def config(self, conf):
        self.conf = dict(simap_cfg = dict(tftpserver = '192.168.0.20',
                                          version = '9.0.0.0.21',
                                          model = 'ss2942'))
        
        self.conf.update(conf)
        self.simap_models = self.carrierbag['existed_simap_models']
        self.package_simap_cfg = self.conf['simap_cfg']
        self.package_simap_cfg['simap_models'] = self._retrieve_models(self.simap_models)
                 
        self.agent = self.carrierbag['existed_sim_agent']
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def test(self):        
        logging.info('package_sim-cfg [%s]' % self.package_simap_cfg)
        installer.install(self.zdcli, **self.package_simap_cfg)
        logging.info('SIMAP firmware configure successfully')        
        self._bootup_simaps(self.agent, self.simap_models)
        if not self._verify_simaps_from_vm(self.agent, len(self.simap_models)):
            raise Exception('Some of SIMAPs haven\'t boot up correctly, please check.')
                
        logging.info('[Initial]begin verify RuckusAPs and SimAPs, make sure all of them are connected.')        
        try:        
            self.zd.do_login()
        except:
            pass
        
        lib.verify_aps_by_models(self.zd, self.simap_models)
        logging.info('All of RuckusAPs and SimAPs are connected.')
        return self.returnResult("PASS", "All of RuckusAPs and SimAPs[%s] are connected." % self.simap_models)        

                
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
            simcfg['ap_start_mac'] = '00:13:92:03:02:%s' % macID
            simcfg['ap_cnt'] = 1
            simcfg['rogue'] = 0
            simcfg['tap_id'] = index + 1
            agent.touch_tcfg(simcfg)
            agent.startup_single_simap()
            
                
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