from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

import logging

class CB_ZD_Config_AP_Policy(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        self.passmsg = ''
        
        if self.active_ap:
            apmac = self.active_ap.base_mac_addr
            
            logging.info("Get AP group that active belongs to from AP general info table. Waiting...")
            grp_info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, apmac)
            self.ap_group = grp_info['ap_group']
            logging.info("AP group name of active AP[%s] is %s" % (apmac, self.ap_group))
            
            logging.info("Get AP model from Monitor--Active Access Points page. Waiting...")
            model_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, apmac)
            self.ap_model = model_info['model']
            logging.info("AP model of active AP[%s] is %s" % (apmac, self.ap_model))

        if 'init' == self.conf['cfg_type']:
            self.carrierbag['ap_policy'] = self.zd.get_ap_policy_approval(
                                                                          self.ap_group,
                                                                          self.ap_model
                                                                          )

        if 'config' == self.conf['cfg_type']:
            self.zd.set_ap_policy_approval(
                self.conf['auto_approval'],
                self.conf['max_clients'],
                self.ap_group,
                self.ap_model
            )

        if 'teardown' == self.conf['cfg_type']:
            '''
            '''
            if self.carrierbag['ap_policy']:
                self.zd.set_ap_policy_approval(
                    self.carrierbag['ap_policy']['approval'],
                    self.carrierbag['ap_policy']['max_clients'],
                    self.ap_group,
                    self.ap_model
                )

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'auto_approval': True,
                     'max_clients': 0, #Chico, 2014-11-19, change default value to 0 to avoid unnecessary script operation costs 
                     'cfg_type': 'config', #['init', 'config', 'teardown']
                     }
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        ap_tag = self.conf.get('ap_tag')
        if ap_tag:
            self.active_ap = self.carrierbag[ap_tag]['ap_ins']
        else:
            self.active_ap = None

        self.ap_group = 'System Default'
        self.ap_model = 'zf7982' #yuyanan 2014-7-17 bug:ZF-8776
         
        self.errmsg = ''
        self.passmsg = ''

