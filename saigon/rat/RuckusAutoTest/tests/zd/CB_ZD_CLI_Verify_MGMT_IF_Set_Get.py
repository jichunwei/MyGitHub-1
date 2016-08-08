'''
Created on 2011-2-16
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as mgmt
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt_if


class CB_ZD_CLI_Verify_MGMT_IF_Set_Get(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        mgmt_if_cli_get = mgmt.show_mgmt_if_info(self.zdcli)

        cli_get = mgmt_if_cli_get[mgmt.info['mgmt_if_v4']]

        mgmt_if_gui_get = mgmt_if.get_mgmt_inf(self.zd)

        logging.info("Verify CLI Set and CLI Get")
        self.errmsg = self.verify_cli_set_get(self.mgmt_if_conf, cli_get)

        logging.info("Verify CLI Set and GUI Get")
        self.errmsg = self.verify_cli_set_get(self.mgmt_if_conf, mgmt_if_gui_get)

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass

    def verify_cli_set_get(self,cli_set,get):
        temp = {}
        map = self.key_map()
        for key,value in map.items():
            if key in cli_set.keys():
                temp[value] = cli_set[key]

        for key in temp:
            if temp[key] != get[key]:
                return("FAIL, CLI Set[%s]:[%s] is different Get[%s]" %(key,temp[key],get[key]))



    def key_map(self):
        map = {'ip_addr':'IP Address',
               'net_mask':'Netmask',
               'vlan_id':'VLAN'
               }
        return map

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         mgmt_if_conf = {}
                         )

        self.conf.update(conf)
        self.mgmt_if_conf = conf['mgmt_if_conf']

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

    def  _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass