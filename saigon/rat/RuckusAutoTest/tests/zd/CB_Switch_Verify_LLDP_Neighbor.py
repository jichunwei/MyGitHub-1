'''
Created on Oct 13, 2014

@author: lab
'''
import time
import logging

from RuckusAutoTest.models import Test

class CB_Switch_Verify_LLDP_Neighbor(Test):
   
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        try:
            self.verify_lldp_neighbors()
        except Exception, ex:
            self.errmsg = ex.message
        if self.errmsg in ['Expected lldp neighbor is not found in Switch',
                           'No lldp neighbor found in Switch']:
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
                     'lldp_neighbor':{'system_name':'RuckusAP',
                                      'port_description':'',
                                      'system_capabilities':'bridge wlanaccesspoint router',
                                      'system_description':''
                                      },
                     'verify_mgmt': True,
                     'negative': False
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
        sw_lldp_neighbors = self.switch.get_lldp_neighbors()
        
        if sw_lldp_neighbors:
            self.verify_lldp_neighbor_items(self.conf['lldp_neighbor'],sw_lldp_neighbors)
        else:
            self.errmsg = 'No lldp neighbor found in Switch'        
            
    def verify_lldp_neighbor_items(self,expect_neighbor, sw_lldp_neighbors):
        """
        {1: {'chassis_id': '2ce6-cc23-1f50',
             'management_address': '192.168.0.148',
             'port_description': 'eth0',
             'port_id': '2ce6-cc23-1f53',
             'system_capabilities': 'bridge wlanaccesspoint router',
             'system_description': 'Ruckus 7982 Multimedia Hotzone Wireless AP/SW Version: 9.9.0.0.150',
             'system_name': 'RuckusAP',
             'time_to_live': ''}}
        """
        target_neighbor = None
        ap_ip = self.active_ap.ip_addr
        ap_mac_addr = ''.join(self.active_ap.base_mac_addr.split(':'))

        for neighbor in sw_lldp_neighbors.values():
            chassis_id = ''.join(neighbor['chassis_id'].split('-'))
            if ap_mac_addr.lower() == chassis_id.lower():
                target_neighbor = neighbor
                break
        if target_neighbor:
            #verify mgmt ip
            if self.conf['verify_mgmt']:
                if not neighbor.has_key('management_address'):
                    self.errmsg += 'Mgmt info is not found.'
                elif neighbor['management_address'] != ap_ip:
                    self.errmsg += 'Management address inconsistent, expect %s, actual %s.'%(ap_ip,neighbor['management_address'])
            else:
                if neighbor.get('management_address'):
                    self.errmsg += 'Mgmt info exists, should not.'
            #verif system_name
            if neighbor['system_name'] != expect_neighbor['system_name']:
                self.errmsg += 'System name inconsistent, expect %s, actual %s.'%(expect_neighbor['system_name'],neighbor['system_name'])

            #verif port description
            active_port_id = self.active_ap.get_ap_eth_port_num_dict()['up'][0]
            active_port = 'eth%s'%active_port_id
            if neighbor['port_description'] != active_port:
                self.errmsg += 'Port description inconsistent, expect %s, actual %s.'%(active_port, neighbor['port_description'])
            #verify port_id
            active_port_mac = self.active_ap.get_eth_port_mac(active_port)
            port_id = active_port_mac
            if not port_id:
                self.errmsg += 'Can not get port id from switch.'
            elif ''.join(port_id.split(':')).lower() != ''.join(neighbor['port_id'].split('-')).lower():
                self.errmsg += 'Port id inconsistent, expect %s, actual %s.'%(''.join(port_id.split(':')).lower(), ''.join(neighbor['port_id'].split('-')).lower())
            #verify system capabilities
            if neighbor['system_capabilities'].lower() != expect_neighbor['system_capabilities'].lower():
                self.errmsg += 'System capabilities inconsistent, expect %s, actual %s'%(expect_neighbor['system_capabilities'].lower(),neighbor['system_capabilities'].lower())
            #verify system description
            ap_model = self.active_ap.get_device_type().lower()
            ap_model = ap_model.split('zf')[-1]
            ap_version = self.active_ap.get_version()
            #description_info = "Ruckus %s Multimedia Hotzone Wireless AP/SW Version: %s"%(ap_model)
            if not ap_model in neighbor['system_description'].lower():
                self.errmsg += 'AP model does not exist in system description'
            if not ap_version in neighbor['system_description']:
                self.errmsg += 'AP version does not exist in system description'

        else: self.errmsg = 'Expected lldp neighbor is not found in Switch'
