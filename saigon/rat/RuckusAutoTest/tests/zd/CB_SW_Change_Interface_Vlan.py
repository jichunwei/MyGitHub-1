'''
'''
import logging

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig

class CB_SW_Change_Interface_Vlan(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        macs = []
        if self.conf.get('mac'):
            macs.append(self.conf.get('mac'))
        elif self.conf.get('component') == 'AP':
            APs = self.testbed.components[self.conf.get('component')]
            for ap in APs:
                macs.append(ap.base_mac_addr)
        elif self.conf.get('ap_tag'):
            active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
            ap_mac = active_ap.get_base_mac()
            macs.append(ap_mac)
#           macs.append(self.testbed.config.get('ap_sym_dict').get(self.conf.get('ap_tag')).get('mac'))
        if self.conf["is_check"]:
            logging.info("restart APs on Web to make sure their status are disconnected")
            self.zd.restart_aps()

        for mac in macs:
            logging.info('Get Switch port that connected to MAC[%s]' % mac)
            port = self.sw.mac_to_interface(mac)
            
            logging.info("Change SW port[%s] from vlan %s to vlan %s" % (port, self.conf.get("from_vlan_id"), self.conf.get("to_vlan_id")))
            self.sw.remove_interface_from_vlan(port,self.conf.get("from_vlan_id"))
            self.sw.add_interface_to_vlan(port,self.conf.get("to_vlan_id"))   

            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
        
        logging.info("wait all APs connected to ZD")
        if self.conf["is_check"]:
            self.zd.wait_aps_join_in_zd()
        
        logging.info("update all AP instances IP")
        all_aps_info = self.zd.get_all_ap_info()
        all_aps_ins = self.testbed.components['AP']
        for ap_ins in all_aps_ins:
            for ap_info in all_aps_info:
                if ap_ins.base_mac_addr.upper() == ap_info.get('mac').upper() and ap_info.get('ip_addr') != '':
                    ap_ins.ip_addr = ap_info.get('ip_addr')
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
     
    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(from_vlan_id='',
                         to_vlan_id='',
                         mac='',
                         ap_tag='',
                         is_check=True)
        
        self.conf.update(conf)
        self.sw = self.testbed.components['L3Switch']
        self.zd = self.testbed.components['ZoneDirector']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         