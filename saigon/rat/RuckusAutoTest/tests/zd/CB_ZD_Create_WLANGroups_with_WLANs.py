'''
Create/Update WLANGourps tag with WLANs in peer.
    WG1--WLAN1, WLAN2, WLAN3....
    WG2--WLAN4, WLAN5, WLAN6...
    WG3--None
    
Created on 2011-7-15
@author: cwang@ruckuswireless.com
'''
import logging
import sys

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD

class CB_ZD_Create_WLANGroups_with_WLANs(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'wlangroups_map':'provide for \
                                wlangroups and wlans mapping dictionary'}
        
    def _init_params(self, conf):
        self.conf = {'wlangroups_map':{'wlangroup_1':['wlan1', 'wlan2'],
                                       'wlangroup_2':['wlan3', 'wlan4']}} 
        self.conf.update(conf)
        self.wlangroups_map = self.conf['wlangroups_map']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
    
    def config(self, conf):
        self._init_params(conf)
        
        if conf.has_key('zd_tag') and conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else:
            self.zd = self.testbed.components['ZoneDirector']
    
    def test(self):
        try:
            wlan_name_list = None                        
            for wlan_group_name, wlan_name in self.wlangroups_map.items():
                if Helper_ZD.wgs.find_wlan_group(self.zd, wlan_group_name):
                    if not wlan_name_list:                    
                        wlan_name_list = Helper_ZD.wlan.get_wlan_list(self.zd)
                    
                    Helper_ZD.wgs.remove_wlan_members_from_wlan_group(self.zd, wlan_group_name, wlan_name_list)
                    Helper_ZD.wgs.cfg_wlan_member(self.zd, wlan_group_name, wlan_name, check=True)
                    logging.info('WLAN Group %s with WLANs %s update successfully' % (wlan_group_name, wlan_name))
                else:
                    Helper_ZD.wgs.create_wlan_group(self.zd, wlan_group_name, wlan_name)
                    logging.info('WLAN Group %s with WLANs %s created successfully' % (wlan_group_name, wlan_name))            
        except:
            error_info = 'Exception type=%s, value=%s, traceinfo=%s when Configure WLANGroup' % sys.exc_info()
            error_info = error_info + " %s " % self.wlangroups_map
            return self.returnResult('ERROR', error_info)
        
        return self.returnResult('PASS', 'WLANGroups %s configure successfully' % self.wlangroups_map)
    
    def cleanup(self):
        pass


        