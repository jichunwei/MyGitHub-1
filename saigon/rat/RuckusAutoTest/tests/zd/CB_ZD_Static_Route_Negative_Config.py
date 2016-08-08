# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Test invalid static route in ZD static route table:

"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Static_Route_Negative_Config(Test):
    def config(self, conf):
        self.conf={}
        self.conf.update(conf)
        self.zd=self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''

    def test(self):
        logging.info('Configure ZD Static Route table with invalid parameters')

        zd_subnet = utils.get_network_address(self.zd.get_ip_cfg()['ip_addr'], '255.255.255.0')
        name = '@1A2b5$'
        subnet = '192.168.22.0/24'
        gateway = zd_subnet[:-1]+'249' 
        param = {'name':name, 'subnet':subnet, 'gateway':gateway, }

        #no item exists
        logging.info('No static route item exists, create it')
        self._negative_test(name, subnet, gateway, op='create')

        #an item exists, edit it with invalid value
        logging.info('No static route item exists, edit it')
        lib.zd.sys.create_static_route(self.zd, param)
        self._negative_test(name, subnet, gateway, op='edit')

        #an item exists, clone it with invalid value
        logging.info('No static route item exists, clone it and edit new item')
        self._negative_test(name, subnet, gateway, op='clone')
        #create/edit/clone an new item, but route parameter exists
        self._item_exist_test(name, subnet, gateway)

        return ("PASS", "ZD Static Route table negative configuration testing successfully")

    def cleanup(self):
        pass

    def _negative_test(self, name, subnet, gateway, op):
        invalid_subnet_list = ['192.168.0.256/32', '192.168.256.222/32', '192.168.0.222/33', 
                               '192.168.0/24', '192.168.0.2a/32', '192.168.0.222 /32']
        invalid_gatevay = ['192.168.0.256', '192.168.256.249', '192.168.0', '192.168.0.a', '192.168.111.249'] #not the same subnet as ZD
        
        for item in invalid_subnet_list:
            param = {'name':(name+'2'), 'subnet':item, 'gateway':gateway, }
            
            try:
                if op == 'create':
                    lib.zd.sys.create_static_route(self.zd, param)
                elif op == 'edit':
                    lib.zd.sys.edit_static_route(self.zd, name, param)
                elif op == 'clone':
                    lib.zd.sys.clone_static_route(self.zd, name, param)
                else:
                    pass

                self.errmsg = "Zone Director accepts an invalid subnet value '%s'" % item
                return
            except:
                pass
                    
        for item in invalid_gatevay:
            param = {'name':(name+'3'), 'subnet':subnet, 'gateway':item, }
            
            try:
                if op == 'create':
                    lib.zd.sys.create_static_route(self.zd, param)
                elif op == 'edit':
                    lib.zd.sys.edit_static_route(self.zd, name, param)
                elif op == 'clone':
                    lib.zd.sys.clone_static_route(self.zd, name, param)

                self.errmsg = "Zone Director accepts an invalid gateway value '%s'" % item
                return
            except:
                pass

    def _item_exist_test(self, name, subnet, gateway):
        #The same name exists, create
        try:
            param = {'name': name, 'subnet':'192.168.23.0/24', 'gateway':gateway}
            lib.zd.sys.create_static_route(self.zd, param)
            
            self.errmsg = "Zone Director accepts existed name when create item"
            return
        except:
            pass
        
        #The same subnet exists, create
        try:
            param = {'name': (name+'-10'), 'subnet':subnet, 'gateway':gateway}
            lib.zd.sys.create_static_route(self.zd, param)
            self.errmsg = "Zone Director accepts existed subnet when create item"
            return
        except:
            pass

        #The same name exists, clone
        try:
            param = {'name': name, 'subnet':'192.168.23.0/24', 'gateway':gateway}
            lib.zd.sys.clone_static_route(self.zd, name, param)
            self.errmsg = "Zone Director accepts existed name when clone item"
            return
        except:
            pass

        #The same subnet exists, clone
        try:
            param = {'name': (name+'-10'), 'subnet':subnet, 'gateway':gateway}
            lib.zd.sys.clone_static_route(self.zd, name, param)

            self.errmsg = "Zone Director accepts existed subnet when clone item"
            return
        except:
            pass

        param = {'name': 'test2', 'subnet':'192.168.53.0/24', 'gateway':gateway}
        lib.zd.sys.create_static_route(self.zd, param)
        #The same name exists, edit
        try:
            param = {'name': name, 'subnet':'192.168.23.0/24', 'gateway':gateway}
            lib.zd.sys.edit_static_route(self.zd, name, param)
            self.errmsg = "Zone Director accepts existed name when edit item"
            return
        except:
            pass

        #The same subnet exists, edit
        try:
            param = {'name': (name+'-10'), 'subnet':subnet, 'gateway':gateway}
            lib.zd.sys.edit_static_route(self.zd, name, param)

            self.errmsg = "Zone Director accepts existed subnet when edit item"
            return
        except:
            pass
