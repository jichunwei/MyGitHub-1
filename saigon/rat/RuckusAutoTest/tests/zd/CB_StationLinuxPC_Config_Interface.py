"""
"""
import logging
from RuckusAutoTest.models import Test

class CB_StationLinuxPC_Config_Interface(Test):

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
        self.sta = self.conf.get('sta_ins')

        if not self.sta and self.sta_tag:
            try:
                sta_dict = self.carrierbag.get(self.sta_tag)
                self.sta = sta_dict.get('sta_ins')
            except:
                if not self.carrierbag.has_key(self.sta_tag):
                    self.carrierbag[self.sta_tag] = dict()
                self.sta = self.carrierbag[self.sta_tag]['sta_ins'] = self.testbed.components[self.sta_tag]        

        if not self.sta:
            raise Exception("No station provided.")

        self.vlan_if_list = self.carrierbag.get(self.sta_tag).get('vlan_if_list', [])
        self.sub_if_list = self.carrierbag.get(self.sta_tag).get('sub_if_list', [])


    def _init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "LinuxPC1",
            'interface': "eth0",
            'ip_addr': "192.17.111.1",
            'vlan_id': "",
            'sub_if_id': "",
            'is_cleanup': False,
        }
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']
        self.interface = self.conf['interface']
        self.ip_addr = self.conf['ip_addr']
        self.vlan_id = self.conf['vlan_id']
        self.sub_if_id = self.conf['sub_if_id']

        self.is_cleanup = self.conf['is_cleanup']

        self.errmsg = ""
        self.passmsg = ""


    def _set_ip_addr(self):
        '''
        '''
        self.sta.set_ip_addr(self.interface, self.ip_addr)

        interface = self.interface
        self._verify_if(interface)
        
        if self.errmsg:
            self.errmsg = ''
            self.sta.rem_sub_intf(interface)
            import time
            time.sleep(10)
            self.sta.set_ip_addr(self.interface, self.ip_addr)
    
            interface = self.interface
            self._verify_if(interface)


    def _add_sub_if(self):
        '''
        '''
        self.sta.add_sub_intf(self.interface, self.ip_addr, self.sub_if_id)

        interface = "%s:%s" % (self.interface, self.sub_if_id)
        self._verify_if(interface)

        if self.passmsg:
            self.sub_if_list.append(interface)


    def _add_vlan_if(self):
        '''
        '''
        self.sta.add_vlan(self.interface, self.vlan_id, self.ip_addr)

        interface = "%s.%s" % (self.interface, self.vlan_id)
        self._verify_if(interface)

        if self.passmsg:
            self.vlan_if_list.append(interface)


    def _verify_if(self, interface):
        '''
        '''
        if_config = self.sta.get_if_config()
        logging.debug(if_config)

        if if_config.get(interface) and \
        self.ip_addr == if_config[interface]['ip_addr']:
            self.passmsg = "Interface %s was configured successfully. %s" % \
                           (interface, if_config)

        else:
            self.errmsg = "Unable to configure interface %s, if_config[interface]=%s, self.ip_addr=%s" \
            % (interface,if_config[interface],self.ip_addr)


    def _cleanup_if(self):
        '''
        '''
        for tmp_if in self.vlan_if_list:
            try:
                self.sta.rem_vlan(tmp_if)
                self.vlan_if_list.remove(tmp_if)

            except:
                logging.debug("Interface %s could not be removed." % tmp_if)
                pass

        for tmp_if in self.sub_if_list:
            try:
                self.sta.rem_sub_intf(tmp_if)
                self.sub_if_list.remove(tmp_if)

            except:
                logging.debug("Interface %s could not be removed." % tmp_if)
                pass
        #jluh updated @ 2013-05-29
        #set linux pc ethernet to a init ip, which is not conflicted with the test ip.
        self._set_ip_addr()


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag.get(self.sta_tag)['vlan_if_list'] = self.vlan_if_list
        self.carrierbag.get(self.sta_tag)['sub_if_list'] = self.sub_if_list

