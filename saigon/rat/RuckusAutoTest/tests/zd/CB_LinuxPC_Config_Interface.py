'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
       
Create on Nov 28, 2011
@author: jluh@ruckuswireless.com
'''
import logging
from RuckusAutoTest.models import Test

class CB_LinuxPC_Config_Interface(Test):

    def config(self, conf):
        '''
        '''
        self._init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        '''
        '''
        if self.is_cleanup:
            self._cleanup_if()

        elif self.vlan_id:
            self._add_vlan_if()

        elif self.sub_if_id:
            self._add_sub_if()

        else:
            self._set_ip_addr()

        self._update_carrier_bag()

        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        pass


    def _retrive_carrier_bag(self):
        '''
        '''
        self.linuxpc = self.conf.get('lpc_ins')
        if not self.linuxpc and self.linuxpc_tag:
            linuxpc_dict = self.carrierbag['LinuxPC'][self.linuxpc_tag]
            self.linuxpc = linuxpc_dict.get('lpc_ins')

        if not self.linuxpc:
            raise Exception("No linuxpc provided.")

        self.vlan_if_list = self.carrierbag['LinuxPC'].get(self.linuxpc_tag).get('vlan_if_list', [])
        self.sub_if_list = self.carrierbag['LinuxPC'].get(self.linuxpc_tag).get('sub_if_list', [])


    def _init_test_params(self, conf):
        '''
        '''       
        self.conf = {
            'lpc_tag': "",
            'interface': "",
            'ip_addr': "",
            'vlan_if_ip_addr': "",
            'vlan_id': "",
            'sub_if_id': "",
            'sub_if_ip_addr': "",
            'is_cleanup': False,
        }
        self.conf.update(conf)

        self.linuxpc_tag = self.conf['lpc_tag']
        self.interface = self.conf['interface']
        self.ip_addr = self.conf['ip_addr']
        self.vlan_id = self.conf['vlan_id']
        self.vlan_if_ip_addr = self.conf['vlan_if_ip_addr']
        self.sub_if_id = self.conf['sub_if_id']
        self.sub_if_ip_addr = self.conf['sub_if_ip_addr']

        self.is_cleanup = self.conf['is_cleanup']

        self.errmsg = ""
        self.passmsg = ""


    def _set_ip_addr(self):
        '''
        '''
        self.linuxpc.set_ip_addr(self.interface, self.ip_addr)

        interface = self.interface
        self._verify_if(interface, self.ip_addr)


    def _add_sub_if(self):
        '''
        '''
        self.linuxpc.add_sub_intf(self.interface, self.sub_if_ip_addr, self.sub_if_id)

        interface = "%s:%s" % (self.interface, self.sub_if_id)
        self._verify_if(interface, self.sub_if_ip_addr)

        if self.passmsg:
            self.sub_if_list.append(interface)


    def _add_vlan_if(self):
        '''
        '''
        self.linuxpc.add_vlan(self.interface, self.vlan_id, self.vlan_if_ip_addr)

        interface = "%s.%s" % (self.interface, self.vlan_id)
        self._verify_if(interface, self.vlan_if_ip_addr)

        if self.passmsg:
            self.vlan_if_list.append(interface)


    def _verify_if(self, interface, ip_addr):
        '''
        '''
        if_config = self.linuxpc.get_if_config()
        logging.debug(if_config)

        if if_config.get(interface) and ip_addr == if_config[interface]['ip_addr']:
            self.passmsg = "Interface %s was configured successfully. %s" % \
                           (interface, if_config)
        else:
            self.errmsg = "Unable to configure interface %s" % interface


    def _cleanup_if(self):
        '''
        '''
        for tmp_if in self.vlan_if_list:
            try:
                self.linuxpc.rem_vlan(tmp_if)
                self.vlan_if_list.remove(tmp_if)

            except:
                logging.debug("Interface %s could not be removed." % tmp_if)
                pass

        for tmp_if in self.sub_if_list:
            try:
                self.linuxpc.rem_sub_intf(tmp_if)
                self.sub_if_list.remove(tmp_if)

            except:
                logging.debug("Interface %s could not be removed." % tmp_if)
                pass


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag['LinuxPC'][self.linuxpc_tag]['vlan_if_list'] = self.vlan_if_list
        self.carrierbag['LinuxPC'][self.linuxpc_tag]['sub_if_list'] = self.sub_if_list

