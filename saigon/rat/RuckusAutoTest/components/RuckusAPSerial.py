# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
RuckusAP interfaces with and controls any Ruckus Access Point via Serial Console.
"""

import os
import sys
import time
import re
import logging
from pprint import pformat

from RuckusAutoTest.common.uspp import *
from RuckusAutoTest.components.PowerMgmt import PowerMgmt
from DUT import DUT
from RuckusAutoTest.models import TestbedComponent, ComponentBase
from RuckusAutoTest.common.utils import log_trace, try_times

class RuckusAPSerial(DUT):
    def __init__(self, config):
        """
        Connect to the Ruckus AP using serial console
        The specified login credentials will be used
        """
        component_info = TestbedComponent.objects.get(name='RuckusAPSerial')
        DUT.__init__(self, component_info, config)

        if config.has_key('timeout'):
            self.timeout = config['timeout']
        else: self.timeout = 15

        if config.has_key('log_file'):
            self.log_file = config['log_file']
        else: self.log_file = 0

        if config.has_key('ip_addr'):
            self.ip_addr   = config['ip_addr']
        else:
            self.ip_addr   = "192.168.0.1"

        if config.has_key('username'):
            self.username = config['username']
        else:
            self.username = "super"

        if config.has_key('password'):
            self.password = config['password']
        else:
            self.password = "sp-admin"

        self.dev = config['dev']
        self.baudrate = int(config['baudrate'])
        self.prompt = 'rkscli'
        self.login()
        logging.info("Login to RuckusAP via serial console successfully")

    def log(self, txt):
        """Log specified text if a log_file is configured"""
        if self.log_file:
            stime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            self.log_file.write("\r%s\r%s" %(stime,txt))

    def connect(self):
        try:
            self.tty = SerialPort(self.dev, self.timeout*1000, self.baudrate)
        except:
            print "################################"
            print "ERROR: Unable to connect to %s" % self.dev
            print "################################\n\n\n"
            raise Exception("Unable to connect to %s" % self.dev)
            sys.exit(1)

    def close(self):
        """
        Close the serial port
        """
        try: del self.tty
        except: pass

#    def __del__(self):
#        self.close()

    def expect_prompt(self, prompt = "", timeout=0):
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

    def get_data(self):
        return self.tty.read(self.tty.inWaiting())

    def expect(self, expect_list, timeout = 0):
        if not timeout:
            timeout = self.timeout

        start_time = time.time()
        data = ""
        found = -1
        while time.time() - start_time < timeout:
            if self.tty.inWaiting():
                data = data + self.get_data()
            for idx in range(len(expect_list)):
                if re.search(expect_list[idx], data):
                    found = idx
                    break
            if found != -1:
                break
        self.log(data)
        return (found, data)

    def login(self, timeout = 0):

        if not timeout: timeout = self.timeout
        self.close()
        self.connect()
        self.tty.flush()
        self.tty.write('\n')
        self.tty.write('\n')
        self.tty.write('\n')

        expect_list = ["Please login", "#", "rkscli", "RedBoot", "u-boot"]
        idx, buf = self.expect(expect_list, timeout)
        if idx == 0:
            self.tty.write(self.username+'\n')
            ix, buf = self.expect(['password'])
            if ix:
                raise Exception("Login Error")
            self.tty.write(self.password+'\n')
            self.expect_prompt('rkscli')
        if idx == 1:
            tries = 5
            while tries:
                self.tty.write('exit\n')
                try:
                    data = self.expect_prompt('Please login')
                    break
                except:
                    tries = tries - 1
            self.login()
        if idx == 2:
            return
        if idx == 3 or idx == 4:
            self.tty.write('reset\n')
            self.login(timeout=180)
        if idx == -1:
            self.tty.write('\n')
            self.tty.write('\n')
            self.tty.write('\n')
            ix, buf = self.expect(expect_list, timeout)
            if ix == -1:
                raise Exception("Could not login to the device")
            else: self.login()
        time.sleep(2)

    def cmd(self, cmd_text, prompt = "", timeout = 0):
        """
        Issue the specified cmd_text and return the complete response
        as a list of lines stripped of the following:
           Echo'd cmd_text
           CR and LR from each line
           Final prompt line
        A timeout value of 0 means use the default configured timeout.
        """
        if not prompt: prompt = self.prompt
        if not timeout: timeout = self.timeout

        tries = 3
        while tries:
            # Empty input buffer
            self.tty.flush()
            self.tty.write(cmd_text+'\n')
            time.sleep(2)
            try:
                buf = self.expect_prompt(prompt, timeout)
                break
            except Exception, e:
                time.sleep(4)
                self.login()
                tries = tries - 1
                continue

        if tries:
            # Split at newlines
            rl = buf.split('\n')
            rl = [x.strip(' ').strip('\r') for x in rl]
            rl = [x for x in rl if x and not x.startswith(prompt)]
            return rl[1:]
        else: raise

    def reboot(self, timeout = 180):
        """
        Rebooting AP
        """
        if not timeout: timeout = self.timeout
        self.tty.flush()
        self.tty.write('reboot\n')
        time.sleep(1)

        idx, data = self.expect(['Please login'], timeout)
        if idx:
            raise Exception("Can not login to the device after rebooting")
        interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
        logging.info("[%s]: AP has been rebooted successfully" % interval)

        # Login again
        time.sleep(4)
        self.tty.write('\n')
        self.tty.write('\n')
        self.login()
        return data

    def goto_red_boot(self, timeout = 180):
        if not timeout: timeout = self.timeout

        cmd = "\x03"
        expect_txt = ["Hit Ctrl-c to stop autoboot:", "enter \^C to abort"]
        prompt = ["u-boot\>", "RedBoot\>"]

        self.tty.flush()
        self.tty.write('reboot\n')
        idx, data = self.expect(expect_txt, timeout)
        if idx != -1:
            self.tty.write(cmd)
            try:
                self.expect_prompt(prompt[0])
            except: self.expect_prompt(prompt[1])
        else:
            raise Exception("Can not go to RedBoot mode")

    def goto_shell(self):
        self.cmd('set rpmkey cli_esc2shell_ok t')
        self.cmd('!v54!', '#')

    def exit_from_shell(self):
        self.cmd('exit', 'Please login:')
        self.login()

    def get_board_data_item(self, line_info, return_line = 0):
        data = self.cmd('get boarddata')
        time.sleep(2)
        index = 0
        while index < len(data):
            if data[index].find(line_info) != -1:
                if not return_line:
                    return data[index].split(' ')[-1]
                else:
                    return data[index]
            index += 1
        return

    def get_model(self):
        return self.get_board_data_item("Model:")

    def get_fw_upgrade_setting(self):
        """
        Get the firmware upgrade setting of the Ruckus AP.
        Output:
        Return a dictionary, which keys:
        - control    : Frameware control control file name
        - host       : Control file server
        - port       : Server port number
        - proto      : Upgrade protocol
        - user       : User name
        - password   : User password
        """
        try:
            setting = self.cmd('fw show')
            time.sleep(5)
            setting_info = {'auto_upgrade':'','control':'', 'host':'', 'port':'', 'user':'', 'password':'', 'proto':''}
            for line in setting:
                if re.search('Auto', line):setting_info['auto_upgrade'] = line.split('=')[1].strip()
                if re.search('FW (.)* Control File', line): setting_info['control'] = line.split('=')[1].strip()
                if re.search('(.)* Server', line): setting_info['host'] = line.split('=')[1].strip()
                if re.search('Port', line): setting_info['port'] = line.split('=')[1].strip()
                if re.search('Protocol', line): setting_info['proto'] = line.split('=')[1].strip()
                if re.search('^User', line): setting_info['user'] = line.split('=')[1].strip().split('\"')[1].strip()
                if re.search('^Password', line): setting_info['password'] = line.split('=')[1].strip().split('\"')[1]
                if re.search('^Running on image', line): setting_info['running_image'] = line.split('=')[-1].strip()
                if re.search('FW Decryption', line): setting_info['psk'] = line.split('=')[1].strip().split('\'')[1].strip()
                if re.search('First', line): setting_info['firstcheck'] = line.split('=')[1].split(" ")[1].strip()
                if re.search('Periodic', line): setting_info['interval'] = line.split('=')[1].split(" ")[1].strip()
        except:
            raise Exception('Can not get firmware upgrade setting')
        return setting_info


    def get_bridge_if_cfg(self):
        """
        This function gets ip configuration information of br interfaces at Linux shell by using command ifconfig
        Return a dictionary contains configuration information of each br interface.
        """
        self.goto_shell()
        self.tty.write('ifconfig\n')

        idx, txt = self.expect(['#'], 15)
        if idx:
            raise Exception("Error during get config on Bridge interfaces")

        buf = [line.rstrip('\r').strip() for line in txt.split('\n')]

        if_info = {}
        ppp_inf = False
        for line in buf:
            if line.startswith("br"):
                inf = line.split()[0]
                mac = line.split()[-1]
            if line.startswith('eth'):
                continue
            if line.startswith('ppp'):
                inf = line.split()[0]
                ppp_inf = True
            if line.startswith('inet addr') and not '127.0.0.1' in line:
                temp = {}
                inet_addr = line.split()[1:]
                if not ppp_inf: temp['mac'] = mac
                temp['ip_addr'] = inet_addr[0].split(':')[1]
                temp['mask'] = inet_addr[2].split(':')[1]
                if_info['%s' % inf] = temp

        self.exit_from_shell()
        return if_info

    def get_mgmt_ip_addr(self):
        """
        This function gets ip address on mgmt port (applied for AP has profile ruckus05)
        """
        res = {}
        res['mgmt'] = {}

        ip_addr = self.cmd("get ip_addr mgmt")[0].split(':')[-1].strip().split()[0]
        res['mgmt']['ip_addr'] = ip_addr
        return res

    def get_profile(self):
        return self.get_board_data_item("Customer ID:")

    def get_main_image_id(self):
        """ Check Main image ID at RedBoot mode"""
        bootid = -1
        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])
        if ix == 0:
            bootid = int(self.cmd('bootid', 'u-boot>')[0].split(' ')[-1])
        else:
            bootid = int(self.cmd('boot', 'RedBoot>')[0].split(' ')[-1])

        return bootid

    def set_main_image_id(self, bootid):
        """ Change Boot ID from RedBoot mode """

        self.tty.write('himem reset\n')
        time.sleep(2)

        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])
        if ix == 0:
            self.cmd('bootid %s' % bootid, 'u-boot>')
        elif ix == 1:
            self.cmd('boot %s' % bootid, 'RedBoot>')
        time.sleep(2)

    def load_image(self, main, bootid):

        # Change Boot ID
        self.set_main_image_id(bootid)

        self.tty.flush()
        self.tty.write('\n')
        self.tty.write('\n')
        prompt_list = ['u-boot', 'RedBoot']
        idx, txt = self.expect(prompt_list)
        if idx == 0:
            if main: cmd = 'bootlcl rcks_wlan.main'
            else: cmd = 'bootlcl rcks_wlan.bkup'
        elif idx == 1:
            if main: cmd = 'fis run rcks_wlan.main'
            else: cmd = 'fis run rcks_wlan.bkup'
        else: raise Exception("AP is not in RedBoot/U-Boot mode")

        self.cmd(cmd, "Please login", 180)
        time.sleep(5)
        self.login()

        # Reboot again to finish loading image from Redboot
        self.reboot()

    def exit_red_boot(self):
        self.cmd('reset', 'Please login:', 180)
        time.sleep(3)

        # Login to AP after reseting
        self.login()

    def wlan_if_to_name(self, wlan_if):
        """return the internal AP wlan name (e.g. 'svcp') given a wlan_if (wlanXX)  name
        """
        for x in self.get_wlan_list():
            #  verify each line in 'get wlanlist' has column wlanID
            if len(x) >= 4:
                if x[3] == wlan_if:
                    return x[0]
        raise Exception("Convert wlan interface %s to name failed. Wlan interface not found in 'get wlanlist' "
                        % wlan_if)

    def get_encryption(self, wlan_if):
        """
        Get encryption configuration of AP
        @return a dictionary of encryption configuration
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("get encryption %s" % wlan_if_name)
        if buf[-1].lower() != 'ok':
            buf = self.cmd("get encryption %s" % wlan_if)

        buf = self.cmd("get encryption %s" %(wlan_if_name))[:-1]
        info = {}
        security = ""
        auth = ""
        encryption = ""
        key_string = ""
        for line in buf:
            temp = [x.strip() for x in line.split(':')]
            time.sleep(2)
            if 'ssid' in temp[0].lower(): info['ssid'] = temp[1]
            if 'security' in temp[0].lower(): security = temp[1]
            if 'authentication' in temp[0].lower(): auth = temp[1].split('-')[0]
            if 'cipher' in temp[0].lower(): encryption = temp[1].split('-')[0]
            if 'passphrase' in temp[0].lower(): key_string = temp[1]
            if 'protocol' in temp[0].lower(): info['wpa_ver'] = temp[1].split('-')[0]
            if 'Key' in temp[0]:
                info['key_index'] = temp[0].split()[1]
                key_string = temp[1].split()[-1].strip('"')
            if 'encryption' in temp[0].lower(): encryption = temp[1]

        if security == "WPA" and auth == "Open":
            info['auth'] = "PSK"
        elif security == "WEP":
            if auth == "Auto": info['auth'] = auth
            else: info['auth'] = auth.lower()
        else: info['auth'] = "open"

        if encryption.startswith("disabled"):
            info['encryption'] = 'none'
        elif encryption.startswith('WEP'):
            if len(key_string) == 10 or len(key_string) == 5:
                info['encryption'] = "WEP-64"
            else: info['encryption'] = "WEP-128"
        else: info['encryption'] = encryption

        if key_string: info['key_string'] = key_string

        return info

    def cfg_wlan(self, wlan_cfg):
        """
        Configure the specified wlan interface with the specified auth parameters:
        """
        zf_ap = False
        model = self.get_model()
        if model.lower().startswith('zf'):
            zf_ap = True

        self.log(self.tty.flush())
        if wlan_cfg.has_key('ssid'):
            self.set_ssid(wlan_cfg['wlan_if'], wlan_cfg['ssid'])

        self.tty.write('set encryption %s\n' % self.wlan_if_to_name(wlan_cfg['wlan_if']))
        ix, rx = self.expect(['Wireless Encryption Type:'])
        if ix == -1:
            raise Exception('Can not set encryption on %s interface' % wlan_cfg['wlan_if'])

        if wlan_cfg['auth'] == 'open' and wlan_cfg['encryption'] == 'none':
            self.tty.write('1\n')
            ix, rx = self.expect(['OPEN no error'])
            if ix == -1: raise Exception('Can not disable encryption method')

        elif wlan_cfg['auth'] in ('open', 'shared', 'Auto') and wlan_cfg['encryption'] in ('WEP-64', 'WEP-128'):
            self.tty.write('2\n')
            ix, rx = self.expect(['WEP Authentication Type:'])
            if ix == -1: raise Exception('Can not set the WEP encryption method')

            self.tty.write('%d\n' % {'open':1, 'shared':2, 'Auto':3}[wlan_cfg['auth']])
            ix, rx = self.expect(['Cipher is set to: WEP'])
            if ix == -1: raise Exception('Can not set the WEP authentication type')

            self.tty.write('%s\n' % wlan_cfg['key_index'])
            ix, rx = self.expect(['OK: key is good'])
            if ix == -1:
                self.tty.write('%s\n' % {'64':'2', '128':'4'}[wlan_cfg['encryption'].split('-')[1]])
            else:
                self.tty.write('%s\n' % {'64':'3', '128':'5'}[wlan_cfg['encryption'].split('-')[1]])
            ix, rx = self.expect(['Enter'])
            if ix == -1: raise Exception('Can not set the WEP encryption strength')

            self.tty.write('%s\n' % wlan_cfg['key_string'])
            ix, rx = self.expect(['OK: key is good'])
            if ix == -1: raise Exception('Can not set the WEB key string')

            self.tty.write('1\n')
            ix, rx = self.expect(['WEP no error'])
            if ix == -1: raise Exception('Setting WEP encryption method on the Ruckus Ap is not successful')

        elif wlan_cfg['auth'] in ('PSK', 'Auto') and wlan_cfg['wpa_ver'] in ('WPA', 'WPA2', 'WPA-Auto'):
            self.tty.write('3\n')
            ix, rx = self.expect(['WPA Protocol Version'])
            if ix == -1: raise Exception('Can not set WPA encryption')

            self.tty.write('%d\n' % {'WPA':1,'WPA2':2,'WPA-Auto':3}[wlan_cfg['wpa_ver']])
            if zf_ap:
                ix, rx = self.expect(['WPA Authentication Type'])
                if ix == -1: raise Exception('Can not set WPA Authentication')
                self.tty.write('%d\n' % {'PSK':1, 'Auto':3}[wlan_cfg['auth']])

            ix, rx = self.expect(['WPA Cipher Type'])
            if ix == -1: raise Exception('Can not set WPA %s' % wlan_cfg['auth'])

            self.tty.write('%d\n' %{'TKIP':1,'AES':2,'Auto':3}[wlan_cfg['encryption']])
            ix, rx = self.expect(['Enter A New PassPhrase', 'Enter A PassPhrase'])
            if ix == -1: raise Exception('Can not set WPA %s %s' % (wlan_cfg['auth'], wlan_cfg['encryption']))

            self.tty.write('%s\n' % wlan_cfg['key_string'])
            ix, rx = self.expect(['WPA no error'])
            if ix == -1: raise Exception('Setting WAP encryption options is not successful')
        else:
            raise Exception('Authentication is not available')

        if self.expect_prompt(timeout=10)==-1:
            raise Exception('Setting encryption options on Ruckus AP not successful')

    def set_ssid(self, wlan_if, ssid):
        # Need to convert the wlan interface ID to name since older Ruckus
        # AP implementation doesn't support interface ID.
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set ssid %s %s" % (wlan_if_name, ssid))[-1]
        if res.lower() != "ok":
            self.cmd("set ssid %s %s" % (wlan_if, ssid))


    def get_wlan_list(self):
        """return list version of 'get wlanlist' cli command"""
        # only interested in the lines with MAC Address in it.
        return [x.split() for x in self.cmd("get wlanlist")if re.search('([0-9a-fA-F:]{17})',x)]

    def set_state(self, wlan_if, state):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set state %s %s" % (wlan_if_name, state))[-1]
        if res.lower() != 'ok':
            res = self.cmd("set state %s %s" % (wlan_if, state))

    def get_state(self, wlan_if):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("get state %s" % wlan_if_name)
        if res[-1].lower() != 'ok':
            res = self.cmd("get state %s" % wlan_if)
        return res[0].split(':')[-1].strip()

#    def wlan_if_to_name(self, wlan_if):
#        """return the internal AP wlan name (e.g. 'svcp') given a wlan_if (wlanXX)  name
#        """
#        for x in self.get_wlan_list():
#            #  verify each line in 'get wlanlist' has column wlanID
#            if len(x) >= 4:
#                if x[3] == wlan_if:
#                    return x[0]
#        raise Exception("Convert wlan interface %s to name failed. Wlan interface not found in 'get wlanlist' "
#                        % wlan_if)

    def power_cycle(self, pwr_mgmt_conf = None, timeout = 180):
        """
        Reboot AP by power cycling
        @pwr_mgmt_conf: a dictionary of parameters to login to Power MGMT, including:
        - port: port that AP power connects to
        - baudrate: baudrate of Power MGMT
        - dev: COM port
        ex: pwr_mgmt_conf = {'port':0, 'baudrate':9600, 'dev':'COM1'}
        """
        pwr_mgmt = PowerMgmt(pwr_mgmt_conf)

        # Power Cycle the AP
        # Turn off port
        try:
            pwr_mgmt.turnOffPort(int(pwr_mgmt_conf['port']))
        except Exception, e:
            raise e
        time.sleep(5)

        # Then turn on port
        self.tty.flush()
        try:
            pwr_mgmt.turnOnPort(int(pwr_mgmt_conf['port']))
        except Exception, e:
            raise e

        idx, data = self.expect(["Please login:"], timeout)
        if idx:
            raise Exception("Can not login to AP after power cycling")

        interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
        logging.info("[%s]: Power Cycle the AP successfully" % interval)

    def reboot_boot_rom(self):
        self.goto_red_boot()
        time.sleep(3)
        self.exit_red_boot()
        interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
        logging.info("[%s]: Reboot AP from bootrom successfully" % interval)

    def set_boot_script(self, condition):
        """
        Pre-condition: AP is in RedBoot/u-boot mode
        """
        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])

        msg = "Create a Boot Script to test %s command"
        if ix == 0:
            cmd = "himem"
            if condition:
                logging.info(msg % cmd)
                self.cmd('setenv bootcmd %s' % cmd, 'u-boot>')
            else: self.cmd('setenv bootcmd', 'u-boot>')
            self.cmd('saveenv', 'u-boot>')
            data = self.cmd('printenv', 'u-boot>')

            set_ok = False
            reset_ok = True
            finish = True
            if condition:
                for line in data:
                    if re.search("bootcmd=%s" % cmd, line):
                        set_ok = True
                        break
                if not set_ok: finish = False
            else:
                for line in data:
                    if re.search("bootcmd=%s" % cmd, line):
                        reset_ok = False
                        break
                if not reset_ok: finish = False
            if not finish:
                self.exit_red_boot()
                raise Exception("Can not set bootcmd for AP at U-Boot mode. Create Boot Script failed")

        elif ix == 1:
            if condition: 
                cmd = "fis list"
                logging.info(msg % cmd)

            failed_msg = "Can not complete modifying the boot script. Create a Boot Script failed"
            self.tty.write('fconfig\n')
            idx, txt = self.expect(["Run script at boot:"])
            if idx == -1:
                self.tty.write("\x03")
                self.exit_red_boot()
                raise Exception(failed_msg)
            if condition:
                self.tty.write("\b\b\b\b\b\b\b\b\btrue\n")
                time.sleep(1)
                ix, txt = self.expect([">>"])
                if ix == -1:
                    self.tty.write("\x03")
                    self.exit_red_boot()
                    raise Exception(failed_msg)

                self.tty.write('%s\n' % cmd)
                self.tty.write("\n")
                ix, txt = self.expect(["Boot script timeout"])
                if ix == -1 :
                    self.tty.write("\x03")
                    self.exit_red_boot()
                    raise Exception(failed_msg)
                self.tty.write("\b\b\b\b\b\b10\n")
            else:
                self.tty.write("\b\b\b\b\b\b\bfalse\n")

            timeout = time.time() + 60
            while time.time() < timeout: # loop to find out expected line
                ix, txt = self.expect(["Update (.*) - continue \(y/n\)\?"], 3)
                if ix == -1:
                    self.tty.write('\n')
                    continue
                elif ix == 0:
                    self.tty.write('y\n')
                    time.sleep(1)
                    break

            if time.time() >= timeout:
                self.exit_red_boot()
                raise Exception(failed_msg)
        else:
            raise Exception('Cannot create Boot script command')

        time.sleep(3)

    def run_boot_script(self):
        """
        Pre-condition:
            - The boot script is already created on the AP
            - AP is in RedBoot mode
        This function is used to run the boot script, verify that if the script runs correctly or not
        """
        self.tty.write('reset\n')
        timeout = 30
        start_time = time.time()
        found = False
        data = ''
        while time.time() - start_time < timeout:
            data = data + self.get_data()
            if re.search("Found Boot Script", data):
                found = True
                break
            time.sleep(0.2)
        if not found:
            return [False, "AP can not execute the Boot Script"]
        logging.info("Boot Script Found!")

        # Get all data after running boot script
        time.sleep(15)
        data = data + self.get_data()

        # Compare
        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])
        self.tty.flush()
        new_data = ''
        if ix == 0:
            new_data = self.cmd('himem', 'u-boot>')
        elif ix == 1:
            new_data = self.cmd('fis list', 'RedBoot>')

        for line in new_data:
            if not line in data:
                return [False, "Information after running boot script is not correct"]

        logging.info("Information after running boot script is correct")
        return [True, "AP executes the Boot Script successfully"]

    def set_boot_net_info(self, ap_ip_addr, serv_ip):
        """
        Go to Redboot and configure network information so that AP can boot via network
        """

        self.goto_red_boot()

        logging.info("Set information for AP booting via network")
        # Define Bootrom mode
        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])
        self.tty.flush()
        ok = True
        if ix == 0:
            # Configure network infor
            self.cmd('setenv ip_addr %s' % ap_ip_addr, 'u-boot>')
            self.cmd('setenv server_ip %s' % serv_ip, 'u-boot>')

            # Verify network info after setting
            self.tty.flush()
            self.tty.write('printenv\n')
            ix1, txt1 = self.expect(['u-boot>'], 20)
            if not re.search("ip_addr=%s" % ap_ip_addr, txt1): ok = False
            if not re.search("server_ip=%s" % serv_ip, txt1): ok = False

        elif ix == 1:
            self.tty.flush()
            self.tty.write('ip_address -l %s -h %s\n' % (ap_ip_addr, serv_ip))
            ix1, txt1 = self.expect(["RedBoot>"])
            ap_ip_pat = "IP: %s/" % ap_ip_addr
            serv_pat = "Default server: %s" % serv_ip
            if not re.search(ap_ip_pat, txt1): ok = False
            if not re.search(serv_ip, txt1): ok = False

        if not ok:
            return [False, "Can not configure network information for AP from bootrom"]

        return [True, "Configure ip address information for AP booting via network successfully"]

    def boot_from_network(self, timeout = 180):
        """
        Pre-condition: AP must be in Redboot mode
        """
        logging.info("Verify that AP can load image when booting from network")

        # Define Bootrom mode
        self.tty.write('\n')
        ix, txt = self.expect(["u-boot>", "RedBoot>"])
        self.tty.flush()

        time.sleep(1)
        if ix == 0: self.tty.write('bootnet vmlinux\n')
        elif ix == 1: self.tty.write('run vmlinux\n')

        start_time = time.time()
        ok = False
        while time.time() - start_time < timeout:
            idx, data = self.expect(["Please login", "[c|C]an\'t load \'vmlinux\':", "[R|r]etry count exceeded\;"])
            if idx == 0:
                ok = True
                break
            elif idx == -1:
                continue
            else: break
            time.sleep(0.5)
        if not ok:
            if ix == 0: self.tty.write("\x03")
            time.sleep(0.5)
            self.exit_red_boot()
            return [False, "Failed to load vmlinux. Maybe network error"]

        self.login()
        return [True, "Load image when booting from network successfully"]

    def get_base_mac(self):
        """
        Return the device Mac address of the AP
        """
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search('base ([0-9,a-f,A-F]+:*)*', x)][0]

    def get_fixed_country_code(self):
        """
        Return the status of Fixed Country code on the AP
        """
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search('Fixed Ctry Code:', x)][0]

    def get_version(self):
        """Return the AP Software version string reported by 'get version'"""
        res = self.cmd("get version")[:-1]
        version = ""
        for line in res:
            if line.lower().startswith("version"):
                version = line.split(':')[-1].strip()
                break
        if not version:
            raise Exception("Can not get software version")
        return version

    def change_fw_setting(self, conf):
        if conf.has_key('control'):
            self.cmd('fw set control %s' % conf['control'])

        if conf.has_key('host'):
            self.cmd('fw set host %s' % conf['host'])

        if conf.has_key('proto'):
            self.cmd('fw set proto %s' % conf['proto'])
            if conf['proto'].lower() == 'ftp':
                self.cmd('fw set user %s' % conf['user'])
                self.cmd('fw set password %s' % conf['password'])

        if conf.has_key('auto'):
            if conf['auto']:
                self.cmd('fw auto enable')
            else:
                self.cmd('fw auto disable')

        if conf.has_key('firstcheck'):
            self.cmd('fw set firstcheck %s' % conf['firstcheck'])

        if conf.has_key('interval'):
            self.cmd('fw set interval %s' % conf['interval'])
        if conf.has_key('psk'):
            self.cmd('fw set psk %s' % conf['psk'])

    def upgrade_sw(self, timeout = 300, custom=False, reboot=True):

        if custom: txt = "custom file"
        else: txt = "build"

        logging.info("Upgrading %s..." % txt)
        self.tty.write('\n')
        self.tty.flush()
        time.sleep(5)
        if custom: self.tty.write('fw update custom\n')
        else: self.tty.write("fw update\n")

        # loop until AP write firmware success or timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception("Upgrade %s failed after %s seconds" % (txt, timeout))

            ix, rx = self.expect(['\*\*fw\([0-9]+\) : [A-Za-z]+.*'], 5)
            time.sleep(0.5)
            if ix != -1:
                break
            time.sleep(1)

        rl = rx.split('\n')
        rl = [x.rstrip('\r') for x in rl]

        fw_txt = ''
        for res in rl:
            if res.lower().startswith("**fw"):
                fw_txt = res
                break
        if fw_txt:
            if 'completed' in fw_txt.lower():
                if reboot:
                    time.sleep(5)
                    logging.info("Upgrade %s DONE. Rebooting AP...." % txt)
                    self.reboot()
#                    time.sleep(5)
#                    self.login() # Login after reboot
                else: logging.info("Upgrade %s DONE" % txt)
            elif 'no update' in fw_txt.lower():
                logging.info("No Upgrade. AP is running an expected %s" % txt)
                return
            else:
                raise Exception(fw_txt.split(':')[-1])

    def check_log_auto_up(self, timeout = 300, log_factory = False):

        logging.info("[Auto Upgrade]: Check if AP will automatically reboot after upgrading...")

        # loop until AP write firmware success or timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception("Upgrade failed after %s seconds" % timeout)
            ix, rx = self.expect(['\*\*\*(.*)\*\*\*'], 3)
            if ix != -1:
                break
            time.sleep(0.1)

        rl = rx.split('\n')
        rl = [x.rstrip('\r') for x in rl]

        fw_txt = ''
        for res in rl:
            if res.lower().find("reboot") != -1:
                fw_txt = res
                break
        if fw_txt:
            logging.info("Auto Upgrade DONE. Waiting the AP to reboot...")
            if not log_factory:
                msg = "[%s]: AP has been rebooted successfully"
            if log_factory:
                start_time = time.time()
                while True:
                    if time.time() - start_time > timeout:
                        raise Exception("AP does not set factory after upgrade custom file with command 'set factory'")
                    ix, rx = self.expect(['Reset to factory defaults'], 10)
                    if ix != -1:
                        break
                    time.sleep(1)
                msg = "[%s]: AP did reboot and set factory successfully"

            idx, data = self.expect(['Please login'], timeout)
            if idx:
                raise Exception("Can not login to the device after rebooting")
            interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
            logging.info(msg % interval)

            # Login again
            time.sleep(4)
            self.tty.write('\n')
            self.tty.write('\n')
            self.login()
        else:
            raise Exception(fw_txt.split(':')[-1])

    def is_auto_upgrade(self, interval):

        res_dict = {}

        # loop until AP write firmware success or timeout
        start_time = time.time()
        while time.time() - start_time < interval:
            ix, rx = self.expect(['.* custom file written .*',
                                  '_erase_flash: offset=0x[\w]+ count=[0-9]+'])
            if ix == 0: res_dict['upgrade_custom'] = True
            elif ix == 1: res_dict['upgrade_custom'] = False

            if res_dict: break
            time.sleep(0.2)

        return res_dict

    def create_ctrl_file(self, rootpath, filename, serv_ip = '0.0.0.0', custom=False):

        filename = '%s/%s' % (rootpath, filename)
        if custom: txt = "Source file"
        else: txt = "Build"
        if not os.path.isfile(filename):
            raise Exception("%s %s is not found in FTP server" % (txt, filename))

        model = self.get_model().lower()
        cntrl_file = '%s/%s' % (rootpath, model)
        try:
            f = open(cntrl_file, 'a')
            if custom:
                f.write('[custom]\n')
                f.write(serv_ip + '\n')
                f.write(filename + '\n')
                f.write(str(os.path.getsize('%s' % filename)) + '\n\n')
            else:
                f.write('[rcks_fw.main]\n')
                f.write(serv_ip + '\n')
                f.write(filename + '\n')
                f.write(str(os.path.getsize('%s' % filename)) + '\n\n')

                f.write('[rcks_fw.bkup]\n')
                f.write(serv_ip + '\n')
                f.write(filename + '\n')
                f.write(str(os.path.getsize('%s' % filename)) + '\n\n')
            f.close()
        except:
            try:
                f.close()
            finally:
                raise Exception('Can not create the control file for %s ...' % filename)

        return cntrl_file

    def corrupt_image(self, timeout = 180):
        cmd = "\x03"
        expect_txt = ["\.\.\.\.\.\.\.\.\.\.\.\."]
        self.tty.flush()
        self.tty.write("fw up \n")
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print "Upgrade failed after %s seconds" % timeout
                raise Exception("Upgrade failed after %s seconds" % timeout)

            idx, data = self.expect(expect_txt, timeout)
            if idx != -1:
                self.tty.write(cmd)
                try:
                    self.expect_prompt(self.prompt)
                    break
                except:
                    raise Exception("Can not corrupted the download")

    def check_reboot_times(self, timeout = 180):
        self.tty.flush()
        self.tty.write('\n')
        self.tty.write('\n')
        self.tty.write('\n')

        expect_list = ["Please login", "RedBoot", "u-boot"]
        idx, buf = self.expect(expect_list, timeout)
        if idx == -1:
            self.tty.write('reboot \n')
        elif idx == 0:
            self.tty.write(self.username+'\n')
            ix, buf = self.expect(['password'])
            if ix:
                raise Exception("Login Error")
            self.tty.write(self.password+'\n')
            self.expect_prompt('rkscli')
            self.tty.write('reboot \n')
        else:
            self.tty.write('reset \n')
        expect_list = ["Please login", "Hit Ctrl-c to stop autoboot:", "enter \^C to abort"]
        count = 0
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print "Couldn't count the retry times"
                raise Exception("Couldn't count the retry times")
            idx, data = self.expect(expect_list, 2)
            if idx == 0: break
            elif idx != -1:
                count = count + 1
        return count

    def get_antenna_info(self):
        return self.get_board_data_item("Antenna Info:")

    def get_board_type(self):
        return self.get_board_data_item("Board Type:")

    def set_factory(self):
        """
        Set factory default for AP
        """
        res = self.cmd("set factory")
        if "OK" in res: self.reboot()
        else: raise Exception("Can not set default factory for AP")

    def get_dfs_info(self, wlan_if):
        buf = self.cmd('get dfs %s' % wlan_if)

        dfs_info = {}
        status = buf[0].split()[-1]

        if status.lower() == "on": dfs_info['enable'] = True
        else: dfs_info['enable'] = False

        cactime_pat = "DFS [C|c]hannel [A|a]vailability [C|c]heck [a-zA-Z ]+ ([0-9]+)"
        notime = "DFS Non-Occupancy [a-zA-Z ]+ ([0-9]+)"
        blkchan = "DFS [C|c]hannel [B|b]lock"
        for line in buf:
            mobj = re.search(cactime_pat, line)
            if mobj: dfs_info['cactime'] = mobj.group(1)
            else: dfs_info['cactime'] = ''

            mo = re.search(notime, line)
            if mo: dfs_info['notime'] = mo.group(1)
            else: dfs_info['notime'] = ''

            mo = re.search(blkchan, line)
            if mo:
                blk = line.split()[-1]
                if blk.lower() == 'on': dfs_info['blkchans'] = 'enable'
                else: dfs_info['blkchans'] = 'disable'
            else: dfs_info['blkchans'] = ''

        return dfs_info

    def get_eth_rx_packets(self, ethif):
        self.goto_shell()
        self.tty.flush()
        self.tty.write('ifconfig\n')
        idx, data = self.expect(['Please login'], timeout)
        if idx:
            raise Exception("Error during get config on interface %s" % ethif)

        buf = [line.rstrip('\r').strip() for line in data.split('\n')]
        rxpat = "RX packets:([0-9]+)"
        for line in buf:
            mo = re.search(rxpat, line)
            if mo: return int(mo.group(1))

        return

    def get_all_eth_interface(self):
        """
        Get all Ethernet interfaces (name and status) on AP (using for 8.0 and over)
        """
        buf = self.cmd('get eth\n')
        buf = [x.strip() for x in buf]

        pat = '(eth[0-9]+)'
        interface_list = []
        for line in buf:
            temp_dict = {}
            mobj = re.search(pat, line)
            if mobj:
                temp_dict['interface'] = mobj.group(1)
                temp_dict['status'] = line.split()[1].lower()
                interface_list.append(temp_dict)

        return interface_list

    def get_station_list(self, wlan_if):
        """ get all station associated to AP via wlan_if """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        return [x.split() for x in self.cmd("get station %s list" % wlan_if_name)if re.search('([0-9a-fA-F:]{17})',x)]

    def remove_all_custom_file(self):
        self.goto_shell()

        res = self.cmd('ls writable/custom', '#')
        existed=False
        for line in res:
            if 'defaults' in line:
                self.cmd('rm -f writable/custom/*.*', '#')
                self.exit_from_shell()
                time.sleep(1)
                self.set_factory()
                existed=True
                break

        if not existed:
            self.exit_from_shell()

    def verify_custom_file_shell(self):

        # Get custom file name
        profile = self.get_profile()
        custom = "%s.defaults" % profile

        self.goto_shell()
        data = self.cmd('ls writable/custom', '#')

        found = False
        if custom in data: found = True
        self.exit_from_shell()

        return found

if __name__ == "__main__":
    config = {'dev':'COM5',
              'baudrate':115200,
              'username':'super',
              'password':'sp-admin'
              }
    power_mgmt = {'dev':'COM1',
              'baudrate':9600,
              'port':3
              }

    pdb.set_trace()

    ap = serialAPCLI(config)
    ap.goto_red_boot()
    ap.set_boot_script(True)
    print ap.run_boot_script()
    ap.set_boot_script(False)
