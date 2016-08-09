'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import logging
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr
class CB_ZD_CLI_Verify_SR_Status(Test):

    def config(self,conf):
        self._init_test_params(conf)

    def test(self):
        try:
            self.verify_sr_status()
        except Exception, ex: 
            self.errmsg = ex.message

        self.passmsg = 'Verifying sr status succeeded.'
        if self.conf['negative']:
            if self.errmsg:
                return self.returnResult('PASS', self.errmsg)
            return self.returnResult('FAIL', self.passmsg)
        else:
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'zdcli_tag':'',
                     'expect_info':{'status':'',
                                    'local_status':'',
                                    'peer_address':'',
                                    'peer_status':'',
                                    'share_secret':''},
                     'negative':False
                     }
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]

    def verify_sr_status(self):
        info = sr.show_sr_info(self.zdcli)
        sr_info = info.get('Smart Redundancy')
        if not sr_info:
            raise Exception('SR info is not found.')
        new_sr_info = self.translate_sr_info(sr_info)
        exp_sr_info = self.conf['expect_info']
        for key in exp_sr_info:
            if not new_sr_info.has_key(key):
                self.errmsg += 'Key %s does not exist in sr info.'%key
            else:
                if new_sr_info[key] != exp_sr_info[key]:
                    self.errmsg += 'Value of [%s] inconsistent, expected %s, actual %s.'\
                    %(key,new_sr_info[key],exp_sr_info[key])
        
    def translate_sr_info(self,info):
        new_info = {}
        if info.has_key('Status'):
            new_info['status'] = info['Status']
        if info.has_key('Local Connect Status'):
            new_info['local_status'] = info['Local Connect Status']
        if info.has_key('Peer IP/IPv6 Address'):
            new_info['peer_address'] = info['Peer IP/IPv6 Address']
        if info.has_key('Peer Connect Status'):
            new_info['peer_status'] = info['Peer Connect Status']
        if info.has_key('Shared Secret'):
            new_info['share_secret'] = info['Shared Secret']
        
        return new_info