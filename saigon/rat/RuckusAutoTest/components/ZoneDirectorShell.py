# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
enter ZD Shell and control zd or show zd information
support multi_user

"""

import logging
import re

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
import telnetlib
from RuckusAutoTest.common.sshclient import sshclient

SHELL_PROMPT='ruckus\$'
USER_PROMPT ='ruckus>'
PRIV_PROMPT ='ruckus#'
TELNET_PORT = '23'
SSH_PORT = 22

class ZoneDirectorShell:

    def __init__(self, config):
        self.conf = dict(
            shell_key = '!v54!',
            ip_addr='192.168.0.2',
            username='admin',
            password='admin',
            protocol='SSH'#SSH or Telnet
        )
        self.started = False
        self.conf.update(config)
        
        self.user_exec_prompt = USER_PROMPT
        self.priv_exec_prompt = PRIV_PROMPT
        self.shell_exec_prompt= SHELL_PROMPT
        self.ip_addr   = self.conf['ip_addr']
        self.ssh_port  = SSH_PORT
        self.telnet_port = TELNET_PORT
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.shell_key = self.conf['shell_key']
        self.protocol=  self.conf['protocol']
        
        
        res,msg=self.connect(self.protocol)
        if not res:
            raise msg
        
    def connect(self,protocol='SSH',timeout=20):
        if protocol.lower()=='ssh':
            res,msg=self._start_ssh_connection()
            if not res:
                return res,msg
            self.shell=self.ssh_shell
            
        elif protocol.lower()=='telnet':
            res,msg=self._start_telnet_connection()
            if not res:
                return res,msg
            self.shell=self.telnet_shell
            
        else:
            return False,'bad protocol %s'%protocol
        self.shell.write('%s\n'%self.shell_key)
        ix,mobj,rx = self.shell.expect([SHELL_PROMPT],timeout)
        if not ix:
            return True,'connect to zd shell(%s) successfully' % protocol
        else:
            return False,'connect to zd shell(%s) failed' % protocol
        

    def _start_ssh_connection(self, tries = 3):
        count = 0
        while not self.started:
            count += 1
            try:
                logging.info('Creating SSH session to Zone Director at %s' % self.ip_addr)
                self.ssh_shell = sshclient(self.ip_addr, self.ssh_port, self.username, self.password)
                self.started = True
                
            except Exception:
                self.close()
                if count >= tries:
                    return False,'not start ssh conection to zd successfully'

                logging.debug('Try to start SSH session to Zone Director %s time(s)' % count)
        
        return self._login()
    
    
    def _login(self):
        """
        Login to Ruckus Zone Director
        """
        logging.debug('Trying to login to the ZD...')
        try:
            ix, mobj, rx = self.ssh_shell.expect(['login'])
            if not ix:
                self.ssh_shell.write(self.username + '\n')

            else:
                raise Exception('Login prompt is not found')

            ix, mobj, rx = self.ssh_shell.expect(['Password'])
            if not ix:
                self.ssh_shell.write(self.password + '\n')

            else:
                raise Exception('Password prompt is not found')

            ix, mobj, rx = self.ssh_shell.expect([self.user_exec_prompt])
            if ix:
                raise Exception('Login failed')

            else:
                logging.info('Login to ZD [%s] successfully!' % self.ip_addr)
                return True,'Login to ZD [%s] successfully!' % self.ip_addr
        except Exception, e:
            return False,'Login error with msg: %s' % e.message
      

    
    def _start_telnet_connection(self,username='',password='',port=None,timeout=20):
        if not username:
            username=self.username
        if not password:
            password=self.password
        if not port:
            port = self.telnet_port
        self.telnet_shell = telnetlib.Telnet(self.ip_addr,port)
        ix,mobj,rx = self.telnet_shell.expect(["login"],timeout)
        if not ix:
            self.telnet_shell.write(username+"\n")
        else:
            logging.info('login prompt not found')
            return False,'login prompt not found'
        ix,mobj,rx = self.telnet_shell.expect(["Password"],timeout)
        if not ix:
            self.telnet_shell.write(password+"\n")
        else:
            logging.info('Password prompt not found')
            return False,'Password prompt not found'
        ix, mobj, rx = self.telnet_shell.expect([self.user_exec_prompt],timeout)
        if not ix:
            logging.info('login to telnet zdcli successfully')
            return True,'login to telnet zdcli successfully'
        else:
            logging.info('command prompt not found after login telnet zdcli')
            return False,'command prompt not found after login telnet zdcli'


    def do_cmd(self, cmd, timeout = 10, raw = False):
        self.shell.write(cmd + '\n')
        prompt_list = [self.shell_exec_prompt]
        ix, mobj, rx = self.shell.expect(prompt_list, timeout)
        if rx:
            self.current_prompt = rx.strip().split('\n')[-1]
        if ix == -1:
            raise Exception('Did not see the command prompt')
        elif raw:
            return rx
        else:
            rx = rx.replace(cmd, '')
            for prompt in prompt_list:
                m = re.search(prompt, rx, re.I)
                if m:
                    if m.start() == 0:
                        last_idx = 0
                    else:
                        last_idx = m.start() - 1
                    rx = rx[:last_idx]
                    rx = rx.strip()
                    break
                rx = rx.strip()
            return rx
        
        