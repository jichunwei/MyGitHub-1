"""
Description: This script is used to remove all wlans from the target station.
Author: Jacky Luh
Email: jluh@ruckuswireless.com
"""

import types
import logging

from RuckusAutoTest.models import Test

class CB_LinuxPC_Close_Socket_Connect(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._close_socket_connect_from_linuxpc()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = "All of linuxpc's sockect is closed."
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.lpc_tag = self.conf['lpc_tag']

        self.errmsg = ''
        self.passmsg = ''

    def _close_socket_connect_from_linuxpc(self):
        if type(self.lpc_tag) is types.ListType:
            for u_tag in self.lpc_tag:
                self.lpc_tag_obj = self.carrierbag['LinuxPC'][u_tag]['lpc_ins']
                try:
                    self.lpc_tag_obj.__del__()
                    logging.info("Close the linux pc[%s]'s socket successfully" % u_tag)
                except Exception, e:
                    self.errmsg = "[Close the linux pc[%s]'s socket failed] %s" % (u_tag, e.message)
        else:
            self.lpc_tag_obj = self.carrierbag['LinuxPC'][self.lpc_tag]['lpc_ins']
            try:
                self.lpc_tag_obj.__del__()
                logging.info("Close the linux pc[%s]'s socket successfully" % self.lpc_tag)
            except Exception, e:
                self.errmsg = "[Close the linux pc[%s]'s socket failed] %s" % (self.lpc_tag, e.message)

