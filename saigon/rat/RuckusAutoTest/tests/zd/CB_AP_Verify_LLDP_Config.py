'''
Created on Sep 30, 2014

@author: chen tao
'''

import logging

from RuckusAutoTest.models import Test

class CB_AP_Verify_LLDP_Config(Test):
   
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        try:
            self.ap_lldp_cfg = self.active_ap.get_lldp_cfg_dict()
            if self.ap_lldp_cfg:
                self.verify_ap_lldp_config(self.ap_lldp_cfg,self.conf['lldp_cfg'])
            else:
                self.errmsg = 'Getting lldp config from apcli failed.'
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg: 
            if self.negative:
                return self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            if self.negative:
                return self.returnResult('FAIL', self.passmsg)
            else:
                return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'ap_tag': '','lldp_cfg':{},'negative':False}
        self.conf.update(conf)
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
        self.negative = self.conf['negative']

    def verify_ap_lldp_config(self, ap_lldp_config, expect_lldp_cfg):
        #compare state
        if expect_lldp_cfg.has_key('state'):
            if expect_lldp_cfg['state'].lower() not in ap_lldp_config['state'].lower():
                msg = 'lldp state inconsistent, expect:%s,actual:%s.'\
                %(expect_lldp_cfg['state'].lower(),ap_lldp_config['state'].lower())
                logging.info(msg)
                self.errmsg += msg
        #compare interval
        if expect_lldp_cfg.has_key('interval'):
            if str(expect_lldp_cfg['interval']) != str(ap_lldp_config['interval']):
                msg = 'lldp interval inconsistent, expect:%s,actual:%s.'\
                %(str(expect_lldp_cfg['interval']), str(ap_lldp_config['interval']))
                logging.info(msg)
                self.errmsg += msg
        #compare holdtime
        if expect_lldp_cfg.has_key('holdtime'):
            if str(expect_lldp_cfg['holdtime']) != str(ap_lldp_config['holdtime']):
                msg = 'lldp holdtime inconsistent, expect:%s,actual:%s.'\
                %(str(expect_lldp_cfg['holdtime']), str(ap_lldp_config['holdtime']))
                logging.info(msg)
                self.errmsg += msg
        #compare mgmt
        if expect_lldp_cfg.has_key('mgmt'):
            if expect_lldp_cfg['mgmt'].lower() not in ap_lldp_config['mgmt'].lower():
                msg = 'lldp mgmt inconsistent, expect:%s,actual:%s.'\
                %(expect_lldp_cfg['mgmt'].lower(), ap_lldp_config['mgmt'].lower())
                logging.info(msg)
                self.errmsg += msg
        #compare enable interfaces
        if expect_lldp_cfg.has_key('enable_ports'):
            if expect_lldp_cfg['enable_ports']:
                for port in expect_lldp_cfg['enable_ports']:
                    if not port in ap_lldp_config['enable_ports']:
                        msg = 'lldp is expected to be enabled on eth%s,actually not.'%port
                        logging.info(msg)
                        self.errmsg += msg         
        #compare disable interfaces
        if expect_lldp_cfg.has_key('disable_ports'):
            if expect_lldp_cfg['disable_ports']:
                for port in expect_lldp_cfg['disable_ports']:
                    if not port in ap_lldp_config['disable_ports']:
                        msg = 'lldp is expected to be disabled on eth%s,actually not.'%port
                        logging.info(msg)
                        self.errmsg += msg
                        
        if not self.errmsg:
            self.passmsg = 'Verifying ap lldp config is successful.'        

