# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
PushKeypadDevice interfaces with and controls the push keypad machine via console port.

Examples:

    from RuckusAutoTest.components import PushKeypadDevice as pkde
    push_dev = pkde.PushKeypadDevice(dict(dev='COM1',baudrate=9600))
    push_dev.turn_on_phone(key_pos=1)
    push_dev.turn_off_phone(key_pos=1)
    push_dev.push_send_key(key_pos=3)
    
"""
import sys
import time
import re
import logging

from RuckusAutoTest.common.uspp import *
from RuckusAutoTest.models import TestbedComponent,ComponentBase

class PushKeypadDevice(ComponentBase):
    PTT_KEY = [13, 14, 15, 16]
    SEND_KEY = [1, 3, 5, 7, 9, 11]
    PWR_KEY = [1, 4, 6, 8, 10, 12]
    def __init__(self, config):
        """
        Connect to the Push Keypad Device using serial console
        Initialized configuration should include the following values:
        - dev: serial port number is connected on controlled device.
        - baudrate: data transmission rate (bits/second) for push keypad device.
        """
        componentinfo = TestbedComponent.objects.get(name='PushKeypadDevice')
        ComponentBase.__init__(self, componentinfo, config)

        if config.has_key('timeout'):
            self.timeout = config['timeout']
        else: self.timeout = 10
        
        self.dev = config['dev']
        self.baudrate = int(config['baudrate'])
        self.prompt = ''
        self.login()
        logging.info("Login to PushKeypadSerial via serial console successfully")

    def connect(self):
        try:
            self.tty = SerialPort(self.dev, self.timeout*1000, self.baudrate)
        except:
            print "################################"
            print "ERROR: Unable to connect to %s" % self.dev
            print "################################\n\n\n"
            raise Exception("Unable to connect to %s" % self.dev)
            sys.exit(1)

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

        idx, buf = self.expect([self.prompt], timeout)
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
        self.tty.flush()

        # Issue command
        self.tty.write(cmdTxt+'\n')
        #time.sleep(2)
        buf = self.expectPromt(prompt, timeout)

        # Split at newlines
        rl = buf.split('\n')
        rl = [x.strip(' ').strip('\r') for x in rl]
        rl = [x for x in rl if x]
        return rl

    def turn_on_phone(self, key_pos):
        logging.info('Push pwr key [%s] to turn on phone' % str(key_pos))
        if int(key_pos) not in self.PWR_KEY:
            raise "input wrong key position [%s] to turn on the phone" % key_pos
        cmd_text = "%02do" % int(key_pos)
        self.cmd(cmd_text)
        time.sleep(0.5)
        cmd_text = "%02df" % int(key_pos)
        self.cmd(cmd_text)
                
    def turn_off_phone(self, key_pos):
        logging.info('Push pwr key [%s] to turn off phone' % str(key_pos))
        if int(key_pos) not in self.PWR_KEY:
            raise "input wrong key position [%s] to turn off the phone" % key_pos
        cmd_text = "%02do" % int(key_pos)
        self.cmd(cmd_text)
        time.sleep(3)
        cmd_text = "%02df" % int(key_pos)
        self.cmd(cmd_text)
                
    def push_send_key(self, key_pos):
        if int(key_pos) not in self.SEND_KEY:
            raise "input wrong key position [%s] to push SEND key" % key_pos 
        cmd_text = "%02do" % int(key_pos)
        self.cmd(cmd_text)
        time.sleep(0.5)
        cmd_text = "%02df" % int(key_pos)
        self.cmd(cmd_text)
        
    def push_end_key(self, key_pos):
        if int(key_pos) not in self.PWR_KEY:
            raise "input wrong key position [%s] to push END key" % key_pos 
        cmd_text = "%02do" % int(key_pos)
        self.cmd(cmd_text)
        time.sleep(0.5)
        cmd_text = "%02df" % int(key_pos)
        self.cmd(cmd_text)         
        
    def push_ptt_key(self, key_pos):
        if int(key_pos) not in self.PTT_KEY:
            raise "input wrong key position [%s] to push PTT key" % key_pos
        cmd_text = "%02do" % int(key_pos)
        self.cmd(cmd_text)
        
    def release_ptt_key(self, key_pos):
        if int(key_pos) not in self.PTT_KEY:
            raise "input wrong key position [%s] to release PTT key" % key_pos
        cmd_text = "%02df" % int(key_pos)
        self.cmd(cmd_text)

if __name__ == "__main__":
    config = {'dev':'COM1',
              'baudrate':9600
              }

    pkdev = PushKeypadDevice(config)
    for key in PWR_KEY:
        pkdev.turn_on_phone(key)
        time.sleep(5)