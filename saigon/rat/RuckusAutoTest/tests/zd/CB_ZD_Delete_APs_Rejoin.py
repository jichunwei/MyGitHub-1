'''
Description:

This function is used to delete AP from ZD webUI and wait for them rejoin.

Created on 2013-1-5
@author: zoe.huang@ruckuswireless.com
'''

import time
import logging
import types

from RuckusAutoTest.models import Test

class CB_ZD_Delete_APs_Rejoin(Test):
    required_components = ['Zone Director']
    test_parameters = {'ap_tags':'list of AP tags',
                       'ap_macaddr_list':'mac addr of ap to be deleted'
                      }

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._delete_aps()
        if self.errmsg: return ('FAIL', self.errmsg)
        self._wait_aps_rejoin()
        if self.errmsg: return ('FAIL', self.errmsg)
        time.sleep(60)#wait for ap configuration
        self.passmsg = 'APs %s are deleted and rejoin successfully.' % str(self.ap_to_delete)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    # Configuration
    def _init_test_parameters(self, conf):
    
        self.conf = {'ap_tags': [],
                     'ap_macaddr_list':[],
                     'wait_time': 300
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag_list = self.conf.get('ap_tags',[])
        self.ap_macaddr_list = self.conf.get('ap_macaddr_list',[])
        self.ap_to_delete = []
        if len(self.ap_macaddr_list) == 0:
            for ap_tag in self.ap_tag_list:                
                active_ap = self.carrierbag[ap_tag]['ap_ins']
                self.ap_to_delete.append(active_ap.base_mac_addr)
        else:
            self.ap_to_delete = self.ap_macaddr_list
        
        self.wait_time = self.conf['wait_time']   
        self.errmsg = ''
        self.passmsg = ''


    def _delete_aps(self):
        msg = 'Remove the approval APs %s' % str(self.ap_to_delete)
        logging.info(msg)
        try:
            for ap_mac in self.ap_to_delete:                
                self.zd.remove_approval_ap(ap_mac)
            msg = 'Remove approval APs %s successfully' % str(self.ap_to_delete)
            logging.info(msg)
        except:
            self.errmsg += 'Failed to remove approval APs %s' % str(self.ap_to_delete)
            
    def _wait_aps_rejoin(self,expected_status = 'Connected'):
        # Wait until AP rejoin successfully
        start_time = time.time()
        time_out = time.time() - start_time

        while time_out < self.wait_time:
            time_out = time.time() - start_time
            flag = True
            for ap_mac in self.ap_to_delete:
                ap_info = self.zd.get_all_ap_info(ap_mac)
                if type(ap_info) is types.DictionaryType:
                    if expected_status not in ap_info['status']:                        
                        flag = False
                        break
                else:
                    flag = False
                    break
            if flag == False:
                time.sleep(20)
            else:
                break

        if time_out > self.wait_time:
            msg = 'APs %s not all rejoin successfully after time: %s'
            self.errmsg += msg % (self.ap_to_delete, self.wait_time)