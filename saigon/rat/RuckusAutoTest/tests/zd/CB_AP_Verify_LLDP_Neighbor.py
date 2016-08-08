'''
Created on Oct 13, 2014

@author: lab
'''
import time
import logging

from RuckusAutoTest.models import Test

class CB_AP_Verify_LLDP_Neighbor(Test):
   
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        try:
            self.verify_lldp_neighbors()

        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg in ['Expected lldp neighbor is not found in AP',
                           'No lldp neighbor found in AP']:
            if self.conf['negative']:
                return self.returnResult('PASS', self.errmsg)
        elif self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            if self.negative:
                return self.returnResult('FAIL', 'Verify lldp neighbor successfully')
            else: 
                return self.returnResult('PASS', 'Verify lldp neighbor successfully')

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'ap_tag': '',
                     'timeout':120,
                     'lldp_neighbor':{'system_name':'Quidway',
                                      'port_description':'Not received',
                                      'system_capabilities':'Bridge, on',
                                      'system_description':'S3700-28TP-SI-AC',
                                      'management_address': '192.168.0.253',
                                      },
                     'negative':False
                    }
        if conf.get('lldp_neighbor'):
            self.conf['lldp_neighbor'].update(conf['lldp_neighbor'])
            conf.pop('lldp_neighbor')
        self.conf.update(conf)
        self.switch = self.testbed.components["L3Switch"]
        self.negative = self.conf['negative']
        
    def verify_lldp_neighbors(self):
        timeout = self.conf['timeout']
        logging.info('Wait for %s seconds until the lldp status is stable.'%timeout)
        time.sleep(timeout)
        ap_lldp_neighbors = self.active_ap.get_lldp_neighbors()
        
        if ap_lldp_neighbors:
            self.verify_lldp_neighbor_items(self.conf['lldp_neighbor'],ap_lldp_neighbors)
        else:
            self.errmsg = 'No lldp neighbor found in AP'
            
    def verify_lldp_neighbor_items(self,expect_neighbor, ap_lldp_neighbors):
        """
        {1: {'chassis_id': '10:47:80:21:cc',
             'management_address': '192.168.0.253',
             'port_description': 'Not received',
             'port_id': 'ifname Ethernet0/0/7',
             'system_capabilities': 'Bridge, on',
             'system_description': 'S3700-28TP-SI-AC',
             'system_name': 'Quidway',
             'time_to_live': ''}}
        """
        target_neighbor = None
        sw_ip = self.switch.ip_addr
        for neighbor in ap_lldp_neighbors.values():
            if neighbor['management_address'] == sw_ip:
                target_neighbor = neighbor
                break
        if target_neighbor:
            #verify chassis id
            sw_mac_addr = ''.join(self.switch.mac_addr.split('-'))
            chassis_id = ''.join(neighbor['chassis_id'].split(':'))
            if sw_mac_addr.lower() != chassis_id.lower():
                self.errmsg += 'Chassis id inconsistent, expect %s, actual %s.'\
                %(sw_mac_addr.lower(),chassis_id.lower())
            #verif system_name
            if neighbor['system_name'] != expect_neighbor['system_name']:
                self.errmsg += 'System name inconsistent, expect %s, actual %s.'\
                %(expect_neighbor['system_name'],neighbor['system_name'])
            
            #verif port description
            if neighbor['port_description'] != expect_neighbor['port_description']:
                self.errmsg += 'Port description inconsistent, expect %s, actual %s.'\
                %(expect_neighbor['port_description'],neighbor['port_description'])
            #In mesh environment, ap mac is shown on multiple ports on switch
            #verify port_id
            port_id_list = self.switch.mac_to_multi_interface(self.active_ap.base_mac_addr)
            if not port_id_list:
                self.errmsg += 'Can not get port id from switch.'
            else:
                port_id_matched = False
                for port_id in port_id_list:
                    if port_id in neighbor['port_id']:
                        port_id_matched = True
                        break
                if not port_id_matched:
                    self.errmsg += 'Port id inconsistent, expect %s, actual %s.'\
                    %(port_id_list,neighbor['port_id'].split(' ')[-1])
            #verify system capabilities
            if neighbor['system_capabilities'] != expect_neighbor['system_capabilities']:
                self.errmsg += 'System capabilities inconsistent, expect %s, actual %s'\
                %(expect_neighbor['system_capabilities'],neighbor['system_capabilities'])
            #verify system description
            if neighbor['system_description'] != expect_neighbor['system_description']:
                self.errmsg += 'System description inconsistent, expect %s, actual %s'\
                %(expect_neighbor['system_description'],neighbor['system_description'])

        else: self.errmsg = 'Expected lldp neighbor is not found in AP'
