'''
Description:

Get AP list from ZD and delete one of them
        
Create on 2012-8-15
@author: zoe.huang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test


class CB_ZD_Delete_AP(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.deleted_ap = ''
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        self.carrierbag['deleted_ap_mac_addr'] = self.deleted_ap
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            ap_mac_list = self.testbed.get_aps_sym_dict_as_mac_addr_list()
            ap_mac_addr = ap_mac_list[0]
            logging.info('Delete AP[%s] from ZD' % ap_mac_addr)
            self.zd.remove_approval_ap(ap_mac_addr)
            self.deleted_ap = ap_mac_addr          
        except Exception, ex:
            self.errmsg = ex.message
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:  
            return self.returnResult('PASS', 'Delete AP[%s] successfully.' % ap_mac_addr)  
    
    def cleanup(self):
        self._update_carribag()