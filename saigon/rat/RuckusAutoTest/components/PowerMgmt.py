# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
PowerMgmt interfaces with and controls Power Management via Serial Console.
Edit by West@2013.5.24 add control through telnet
"""

import sys
import time
import re
import logging
import telnetlib

from RuckusAutoTest.common.uspp import *
from RuckusAutoTest.models import TestbedComponent,ComponentBase

class PowerMgmt(ComponentBase):
    def __init__(self, config):
        """
        Connect to the Power Management using serial console
        The specified parameters will be used
        """
        componentinfo = TestbedComponent.objects.get(name='PowerMgmt')
        ComponentBase.__init__(self, componentinfo, config)

        self.through_telnet = config.get('through_telnet')
        if config.has_key('timeout'):
            self.timeout = config['timeout']
        else: self.timeout = 10
        if not self.through_telnet:
            self.dev = config['dev']
            self.baudrate = int(config['baudrate'])
        self.prompt = '>'
        ip_addr=self.conf.get['ip_addr']
        if ip_addr:
            self.ip_addr = ip_addr
        else:
            self.ip_addr = '192.168.0.15'
        self.port = 23
        
        self.login()
        logging.info("Login to Power Mamagement via serial console successfully")

    def connect(self):
        if not self.through_telnet:
            try:
                self.tty = SerialPort(self.dev, self.timeout*1000, self.baudrate)
            except:
                print "################################"
                print "ERROR: Unable to connect to %s" % self.dev
                print "################################\n\n\n"
                raise Exception("Unable to connect to %s" % self.dev)
                sys.exit(1)
        else:
            self.tty = telnetlib.Telnet(self.ip_addr,self.port)


    def __del__(self):
        self.close()

    def close(self):
        """
        Close the serial port
        """
        try: del self.tty
        except: pass

    def expectPromt(self, prompt = "", timeout=0):
        if not prompt:
            prompt = self.prompt
        idx, data = self.expect([prompt], timeout)
        if idx:
            self.tty.write('\n')
            self.tty.write('\n')
            self.tty.write('\n')
            idx, data1 = self.expect([prompt], timeout)
            if idx:
                raise Exception("Prompt %s not found" % prompt)
        return data
    
    def expect_prompt_telnet(self, prompt = "", timeout = 0):
        """Expect a prompt and raise an exception if we don't get one. Returns only input."""
        if not prompt:
            target_prompts = [self.prompt]
        elif type(prompt) is list:
            target_prompts = prompt
        else:
            target_prompts = [prompt]

        ix, rx = self.expect_telnet(target_prompts, timeout = timeout)
        if ix:
            ix, rx = self.expect_telnet(target_prompts, timeout=30)
            if ix:
                raise Exception("Prompt %s not found" % prompt)
        return rx

    def expect_telnet(self, expect_list, timeout = 0):
        """
        A wrapper around the telnetlib expect().
        This uses the configured timeout value and logs the results to the log_file.
        Returns the same tuple as telnetlib expect()
        """
        if not timeout:
            timeout = self.timeout
        ix, mobj, rx = (-1, None, "")
        ix, mobj, rx = self.tty.expect(expect_list, timeout)
        return (ix, rx)

    def getData(self):
        return self.tty.read(self.tty.inWaiting())

    def expect(self, expect_list, timeout = 0):
        if not timeout:
            timeout = self.timeout

        start_time = time.time()
        data = ""
        found = -1
        while time.time() - start_time < timeout:
            if self.tty.inWaiting():
                data = data + self.getData()
            for idx in range(len(expect_list)):
                if data.find(expect_list[idx]) != -1:
                    found = idx
                    break
            if found != -1:
                break
        return (found, data)

    def login(self, timeout = 0):

        if not timeout: timeout = self.timeout

        self.close()
        self.connect()
        self.tty.write('\n')
        self.tty.write('\n')
        self.tty.write('\n')
        
        if not self.through_telnet:
            idx, buf = self.expect([self.prompt], timeout)
        else:
            idx, buf = self.expect_telnet([self.prompt], timeout)
        
        if idx == 0:
            return
        if idx == -1:
            self.tty.write('\n')
            self.tty.write('\n')
            self.tty.write('\n')
            ix, buf = self.expect([self.prompt], timeout)
            if ix == -1:
                raise Exception("Could not login to the device")
            else: self.login()

    def cmd(self, cmdTxt, prompt = "", timeout = 0):

        if not prompt: prompt = self.prompt
        if not timeout: timeout = self.timeout

        # Empty input buffer
        if not self.through_telnet:
            self.tty.flush()
        else:
            self.tty.read_very_eager()

        # Issue command
        self.tty.write(cmdTxt+'\n')
        time.sleep(2)
        if not self.through_telnet:
            buf = self.expectPromt(prompt, timeout)
        else:
            buf = self.expect_prompt_telnet(prompt, timeout)
            buf += self.tty.read_very_eager()
        
        # Split at newlines
        rl = buf.split('\n')
        rl = [x.strip(' ').strip('\r') for x in rl]
        rl = [x for x in rl if x and not x.startswith(prompt)]
        return rl[1:]

    def getPortStatus(self):
        """
        Get information of all ports
        """
        data = self.cmd('pshow')
        
        data = [x for x in data if not x.startswith('*') and not x.startswith('-')]

        header = [x.strip(' ').lower().split()[0] for x in data[0].split('|')]
        new_data = list()
        pat = "^[0-9]+[ ]+\|"
        for line in data[1:]:
            mobj = re.match(pat, line.strip(' '))
            if mobj:
                new_data.append(line)
        if not new_data: raise Exception("Can not get any information of ports")

        port_info = list()
        for line in new_data:
            tmp = {}
            line = [x.strip(' ').lower().split()[0] for x in line.split('|')]
            for i in range(len(line)):
                tmp[header[i]] = line[i]
            port_info.append(tmp)
            time.sleep(1)

        return port_info

    def turnOnPort(self, port_num):
        """ Turn on port"""
        tries = 2
        while tries:
            self.cmd('pset %s 1' % port_num)
            time.sleep(2)

            # Verify if port is already on
            On = True
            port_info = self.getPortStatus()
            for line in port_info:
                if int(line['port']) == port_num:
                    if line['status'] == 'on':
                        logging.info("Turn on port %d successfully" % port_num)
                        return
                    else:
                        On = False
                        break
            if not On:
                tries = tries - 1
                continue
        if not tries:
            raise Exception("Can not turn on port %s" % port_num)

    def turnOffPort(self, port_num):
        """ Turn off port"""
        tries = 2
        while tries:
            self.cmd('pset %s 0' % port_num)
            time.sleep(2)

            # Verify if port is already on
            Off = True
            port_info = self.getPortStatus()
            for line in port_info:
                if int(line['port']) == port_num:
                    if line['status'] == 'off':
                        logging.info("Turn off port %d successfully" % port_num)
                        return
                    else:
                        Off = False
                        break
            if not Off:
                tries = tries - 1
                continue
        if not tries:
            raise Exception("Can not turn on port %s" % port_num)

if __name__ == "__main__":
    config = {'dev':'COM1',
              'baudrate':9600
              }

    pwr_mgmt = PowerMgmt(config)
    pwr_mgmt.turnOnPort(1)
