# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.
"""
The SpectralinkSVP class provides functions to configure Spectralink SVP.
"""
from telnetlib import *
import re, time
import logging
import RuckusAutoTest.common.Ratutils as RU

ExpState = {'EXPECT': 'expect', 'MATCH': 'match', 'TIMEOUT': 'timeout', 'DATA': 'data', 'EMPTY': 'empty'}

class SpectralinkSVP:
    def __init__(self, config):
        """
        Connect to the linux machine at the specified IP address via telnet.
        All user will be change to root use after login.
        All subsequent CLI operations will be subject to the specified default timeout.
        If logfile is specified then out CLI output will be logged to the specified file.
        """
        self.conf = dict( timeout=60
                        , logfile=''
                        , ip_addr='192.168.0.230'
                        , username='admin'
                        , password='admin'
                        , prompt="Cursor"
                        , init=False
                        , debug=0
                        , recv_pause=0.25
                        , waitfor=300
                        , pause=2
                        , stdout=1
                        , ping_timeout=10
                        )
        self.conf.update(config)
        (self.exp_state, self.exp_output, self.exp_recv_cnt) = ('', '', 0)
        if self.conf['init']: self.initialize()

    def initialize(self, dologin=True):
        self.timeout = self.conf['timeout']
        self.logfile = self.conf['logfile']
        self.ipaddr = self.conf['ip_addr']
        self.user = self.conf['username']
        self.passwd = self.conf['password']
        self.prompt = self.conf['prompt']
        self.re_prompt = re.compile(self.prompt)
        if not dologin: return
        try:
            self.login()
        except:
            raise Exception('Can not login to the Spectralink SVP')

    def log(self, txt):
        """
        Save the log to file
        """
        if self.logfile:
            self.logfile.write(txt)

    def login(self, asRoot=True):
        """
        Login the linux machine via telnet and change the user to root.
        """
        self.pc = Telnet(self.ipaddr)
        self.pc.expect(['login'])
        self.pc.write(self.user+'\n')
        self.pc.expect(['Password'])
        self.pc.write(self.passwd+'\n')
        ix, ox, tx = self.pc.expect(self.prompt, self.timeout)
        if ix == -1:
            raise Exception('Can not telnet to \'%s\'' %self.ipaddr)

    def close(self):
        """
        Close the telnet session
        """
        try:
            self.pc.close()
        except:
            pass

    def verify_component(self):
        logging.info("Sanity check: Verify Test engine can ping Spectralink SVP[%s]" % (self.conf['ip_addr']))
        rmsg = RU.ping_win32( self.conf['ip_addr'], timeout_ms=self.conf['ping_timeout']*1000, echo_timeout=1000)
        if rmsg.find('Timeout') != -1:
            raise Exception("Spectralink SVP is no response")

    def __del__(self):
        '''
        Destructor
        '''
        pass
