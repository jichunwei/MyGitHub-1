# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
Description:
set tacacs server ip/port/secret/service
verify valid value can be set and invalid value cannot be set
and also verify the alert when the value is invalid
"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Tacacs_Plus_Server_Configuration_Test(Test):

    def config(self, conf):
        self._init_parameter(conf)

    def test(self):
        self.errmsg = self._cfg_tacacs_plus_server_test()
        if self.errmsg: return ('FAIL', self.errmsg)
        self._update_carrierbag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_parameter(self, conf):
        str_longer_than_64='abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12dssss'
        self.conf = {'server': '',
                     'server_addr':{
                                    '255.255.255.255':'IP Address, 255.255.255.255, is not a valid IP address.',
                                    'abc.e.s.d':'IP Address, abc.e.s.d, is not a valid IP address.',
                                    '100':'IP Address, 100, is not a valid IP address.',
                                    },
                     'server_port':{
                                    '0':'Port is not a valid port number or port range.',
                                    '65536':'Port is not a valid port number or port range.', #@ZJ ZF-10206
                                    'x':'Port is not a valid port number or port range.',
                                    },
                    
                     'tacacs_auth_secret':{
                                           str_longer_than_64:'Can not set value "%s" to the element'%str_longer_than_64,
                                           "":'Shared Secret cannot be empty',
                                           " ":'Shared Secret cannot be empty',
                                           },
                     'tacacs_service':{' ':'TACACS+ Service cannot be empty',
                                       '':'TACACS+ Service cannot be empty',
                                       str_longer_than_64:'Can not set value "%s" to the element'%str_longer_than_64,
                                       },
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _cfg_tacacs_plus_server_test(self):
        res=''
        for config_item in self.conf:
            if  not config_item=='server':
                logging.info('begin %s configuration test'%config_item)
                d=self.conf[config_item]
                for value in d:
                    err_msg=d[value]
                    logging.info('set [%s] to [%s],alert or exception [%s] should be met'%(value,config_item,err_msg))
                    server_cfg={'server_name':self.conf['server'],
                                config_item:value,
                                'server_type':'tacacs_plus',
                                }
                    try:
                        msg=self._update_aaa_server(server_cfg)
                        if msg:
                            if not err_msg in msg:
                                res+= 'alert(%s) not the same as expected(%s),'%(msg,err_msg)
                                logging.error('alert(%s) not the same as expected(%s)'%(msg,err_msg))
                        elif err_msg:
                            res+= 'alert should exist(%s) when set [%s] to [%s],'%(err_msg,value,config_item)
                            logging.error('alert should exist(%s) when set [%s] to [%s]'%(err_msg,value,config_item))
                    except Exception, e:
                        if (not err_msg) or (not err_msg in e.message):
                            res+= 'unexpect exception met(%s),'%e.message
                            logging.error('unexpect exception met(%s)'%e.message)
                            
        return res
                        
    
    def _update_aaa_server(self,config):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        return lib.zd.aaa.edit_server(self.zd, self.conf['server'],config)


    def _update_carrierbag(self):
        pass
