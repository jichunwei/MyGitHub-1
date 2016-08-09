# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
set ad country code in web
config:
    unfix country in all ap connected to zd
test 
    config the country code in zd and wait ap connect
"""

import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_ZD_Set_Country_Code(Test):
    def config(self, conf):
        self.conf={'country_code':'United Kingdom',
                   'optimize':None,
                   'allow_indoor_channel':None,
                   'unfix_ap':True
                   }
        self.conf.update(conf)
        if self.carrierbag.has_key('channel_selection_test_para'):
            self.conf['country_code']= self.carrierbag['channel_selection_test_para']['ctry']
        self.zd=self.testbed.components['ZoneDirector']
        self.ap_mac_list=self.testbed.get_aps_mac_list() 

        #unfix ap country code if need
        if self.conf['unfix_ap'] == True:
            for mac in self.ap_mac_list:
                ap_info=self.zd.get_all_ap_info(mac)
                if ap_info['status'].lower().startswith('connected'):
                    ap = self.testbed.mac_to_ap[mac.lower()]
#                    ap = RuckusAP(dict(ip_addr = ap_info['ip_addr'],username='admin',password='admin'))
                    logging.info("set ap \"fixed ctry code\" status of the AP %s to \"no\"" % mac)
                    ap.set_fixed_country_code(False)
                    ap.reboot()
                else:
                    logging.error("ap %s status is not connected"% mac)
        ###zj 2014-0218 fix ZF-7233    
        if (not self.conf['optimize']) and ((self.conf['country_code']=='United States') or (self.conf['country_code']=='United states')):
            self.conf['optimize']=self.carrierbag.get('channel_optimization')

        if (not self.conf['allow_indoor_channel']):
            self.conf['allow_indoor_channel']=self.carrierbag.get('allow_indoor_channel')

    def test(self):
        logging.info('set country code %s'%self.conf['country_code'])
        self.zd.set_country_code(self.conf['country_code'],self.conf['optimize'],self.conf['allow_indoor_channel'])
        time.sleep(1)
        cc=self.zd.get_country_code()
        if cc['label'].lower()!=self.conf['country_code'].lower():
            return('FAIL','country code set failure get %s,expected %s'%(cc['label'],self.conf['country_code']))
        
        #wait all ap connect after country code change
        wait_time=2400
        t0=time.time()
        for mac in self.ap_mac_list:
            while True:
                if time.time()-t0>wait_time:
                    return('FAIL','not all ap connect to zd after change country code %d seconds'%wait_time)
                try:
                    ap_info=self.zd.get_all_ap_info(mac)
                    if ap_info['status'].lower().startswith('connected'):
                        break
                except:
                    pass
                    
        return ["PASS", "set country %s successfully"%self.conf['country_code']]

    def cleanup(self):
        pass


