# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
RuckusAP interfaces with and controls any Ruckus Access Point via telnet CLI.
For wlan interface specific commands such as 'set ssid wlan_if', wlan interface ID
(wlan0, wlan1, etc) is used as argument.
"""

import telnetlib
import os,time,datetime
import re
import logging
import random
import ftplib
import shutil
import socket
import ConfigParser
from tarfile import *
try:
    from SeleniumControl import Selenium
except:
    pass

class RuckusAD:

    def __init__(self, config):
        """
        Connect to the Ruckus AD at the specified IP address via telnet.
        The specified login credentials will be used.
        All subsequent CLI operations will be subject to the specified default timeout.
        If log_file is specified then out CLI output will be logged to the specified file.
        This will enable telnet if telnet is not already enabled.
        """

        if config.has_key('ip_addr'):
            self.ip_addr   = config['ip_addr']
        else:
            self.ip_addr   = "192.168.0.254"

        if config.has_key('username'):
            self.username = config['username']
        else:
            self.username = "super"

        if config.has_key('password'):
            self.password = config['password']
        else:
            self.password = "sp-admin"

        if config.has_key('ssh_port'):
            self.ssh_port = config['ssh_port']
        else: self.ssh_port = "22"

        if config.has_key('timeout'):
            self.timeout  = config['timeout']  # default timeout
        else:
            self.timeout = 10

        # Login to Adapter by WebUI
        self.url = ""
        if config.has_key('url'):
            self.url = config['url']
            self.browser_type = config['browser_type']

            self.ad_info_file = r"RuckusAD.inf"
            self.info = self._load_information_file(self.ad_info_file)

            # Load Selenium
            self.selenium = Selenium(self.browser_type, self.url)
            self.selenium.loadSelenium()
            self.s = self.selenium.getClient()
            self.s.set_speed(200)

        else:
            # Otherwise, login to adapter by CLI
            self.prompt = "rkscli:"
            try:
                self.login()
            except:
                self.enable_telnet_via_ssh()
                time.sleep(5)
                self.login()

    def __del__(self):
        """
        This method is a destructor
        It will be called when an instance of this class has been killed
        """
        if self.url:
            try:
                self.selenium.closeAllBrowsers()
                time.sleep(3)
                self.selenium.killServer()
            except:
                pass
        else:
            self.close()

    def expect(self, expect_list, timeout=0):
        """
        A wrapper around the telnetlib expect().
        This uses the configured timeout value and logs the results to the log_file.
        Returns the same tuple as telnetlib expect()
        """
        if not timeout:
            timeout=self.timeout
        ix, mobj, rx = (-1, None, "")
        try:
            ix, mobj, rx = self.tn.expect(expect_list, timeout)
        except EOFError:
            logging.info("Telnet session timeout. Try to re-login")
            self.enable_telnet_via_ssh()
            time.sleep(5)
            self.login()
        except socket.error, (code, msg):
            if code == 10054:
                logging.info("%s ****** Try to re-login" % msg)
                self.enable_telnet_via_ssh()
                time.sleep(5)
                self.login()
        except socket.error, (code, msg):
            if str(msg).find("Connection refused") != -1:
                logging.info("%s ****** Try to re-login" % msg)
                self.enable_telnet_via_ssh()
                time.sleep(5)
                self.login()

        return (ix,mobj,rx)

    def expect_prompt(self, timeout=0, prompt=""):
        """Expect a prompt and raise an exception if we don't get one. Returns only input."""
        if not prompt:
            prompt = self.prompt
        ix,mobj,rx = self.expect([prompt], timeout=timeout)
        if ix:
            raise Exception("Prompt %s not found" % prompt)
        return rx

    def login(self):
        """Login to Adapter. If a telnet session is already active this will close that session and create a new one."""
        tries = 2
        while tries:
            try:
                self.close()
                self.tn = telnetlib.Telnet(self.ip_addr)
                break
            except socket.error, (code, msg):
                if str(msg).find("Connection refused") != -1:
                    tries = tries - 1
                    continue

        ix,mobj,rx = self.expect(["login"])
        self.tn.write(self.username+"\n")
        ix2,mobj,rx = self.expect(["password"])
        if ix or ix2:
            raise Exception("Login Error")
        self.tn.write(self.password+"\n")
        self.expect_prompt()
        # set default timeout for AD
        self.set_timeout()

    def enable_telnet_via_ssh(self):
        """Use paramiko ssh library to login to Ruckus AP and enable telnet"""
        import paramiko
        from time import sleep
        def wait_for(chan, text):
            """quick and dirty excpect substitute for paramiko channel; Raise exception if text not found."""
            for x in range(100):
                if chan.recv_ready():
                    if text in chan.recv(1024):
                        return # success
                sleep(.020) # 100*.02 = approx 2 seconds total
            raise Exception("SSH expect")

        t = paramiko.Transport((self.ip_addr, int(self.ssh_port)))
        t.connect(username="", password="", hostkey=None)
        chan = t.open_session()
        try:
            chan.get_pty()
            chan.invoke_shell()
            wait_for(chan, 'login')
            chan.send(self.username+"\n")
            wait_for(chan, 'password')
            chan.send(self.password+"\n")
            wait_for(chan, 'rkscli:')
            chan.send("set telnet enable\n")
            wait_for(chan, 'OK')
        finally:
            chan.close()
            t.close()
        time.sleep(3)

    def close(self):
        """Terminate the telnet session"""
        try:
            self.tn.close()
        except:
            pass

    def cmd(self, cmd_text, timeout=0, prompt=""):
        """
        Issue the specified cmd_text and return the complete response
        as a list of lines stripped of the following:
           Echo'd cmd_text
           CR and LR from each line
           Final prompt line
        A timeout value of 0 means use the default configured timeout.
        Logs all telnet output to the log file as side-effect.
        """
        if not prompt:
            prompt = self.prompt
        tries = 3
        while tries:
            try:
                # empty input buffer and log if necessary
                self.tn.read_very_eager()

                # issue command
                self.tn.write(cmd_text+"\n")
            except EOFError:
                logging.info("Telnet session timeout. Try to re-login")
                time.sleep(5)
                self.login()
                self.tn.write(cmd_text+"\n")
            except socket.error, (code, msg):
                if code == 10054:
                    logging.info("%s. Try to re-login" % msg)
                    time.sleep(5)
                    self.login()
                    self.tn.write(cmd_text+"\n")
            try:
                r = self.expect_prompt(prompt=prompt)  # logs as side-effect
                break
            except Exception, e:
                self.login()
                tries = tries - 1
                continue

        if tries:
            # split at newlines
            rl = r.split("\n")
            # remove any trailing \r
            rl = [x.rstrip('\r') for x in rl]
            # filter empty lines and prompt
            rl = [x for x in rl if x and not x.endswith(prompt)]
            return rl[1:] # remove cmd_text from output
        else:
            raise

    def verify_component(self):
        """ Perform sanity check on the component: the AP is there
            Device should already be logged in.
        """
        logging.info("Sanity check: Verify Test engine execute command on AD %s" % self.ip_addr)
        # Can log in to AP
        try:
            self.get_version()
        except:
            pass

    def get_wlan_list(self):
        """return list version of 'get wlanlist' cli command"""
        # only interested in the lines with MAC Address in it.
        return [x.split() for x in self.cmd("get wlanlist")if re.search('([0-9a-fA-F:]{17})',x)]

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

    def cfg_wlan(self, wlan_cfg):
        """
        Configure the specified wlan interface with the specified auth parameters:
        """
        self.tn.read_very_eager()
        if wlan_cfg.has_key('ssid'):
            self.set_ssid(wlan_cfg['wlan_if'], wlan_cfg['ssid'])

        self.tn.write('set encryption %s\n' % self.wlan_if_to_name(wlan_cfg['wlan_if']))
        ix, mobj, rx = self.expect(['Wireless Encryption Type:'])
        if ix == -1:
            raise Exception('Can not set encryption on %s interface' % wlan_cfg['wlan_if'])

        if wlan_cfg['auth'] == 'open' and wlan_cfg['encryption'] == 'none':
            self.tn.write('1\n')
            ix, mobj, rx = self.expect(['OPEN no error'])
            if ix == -1: raise Exception('Can not disable encryption method')

        elif wlan_cfg['auth'] in ('open', 'shared', 'Auto') and wlan_cfg['encryption'] in ('WEP-64', 'WEP-128'):
            self.tn.write('2\n')
            ix, mobj, rx = self.expect(['WEP Authentication Type:'])
            if ix == -1: raise Exception('Can not set the WEP encryption method')

            self.tn.write('%d\n' % {'open':1, 'shared':2, 'Auto':3}[wlan_cfg['auth']])
            ix, mobj, rx = self.expect(['Cipher is set to: WEP'])
            if ix == -1: raise Exception('Can not set the WEP authentication type')

            self.tn.write('%s\n' % wlan_cfg['key_index'])
            ix, mobj, rx = self.expect(['OK: key is good'])
            if ix == -1:
                self.tn.write('%s\n' % {'64':'2', '128':'4'}[wlan_cfg['encryption'].split('-')[1]])
            else:
                self.tn.write('%s\n' % {'64':'3', '128':'5'}[wlan_cfg['encryption'].split('-')[1]])
            ix, mobj, rx = self.expect(['Enter'])
            if ix == -1: raise Exception('Can not set the WEP encryption strength')

            self.tn.write('%s\n' % wlan_cfg['key_string'])
            ix, mobj, rx = self.expect(['OK: key is good'])
            if ix == -1: raise Exception('Can not set the WEB key string')

            self.tn.write('1\n')
            ix, mobj, rx = self.expect(['WEP no error'])
            if ix == -1: raise Exception('Setting WEP encryption method on the Ruckus Ap is not successful')

        elif wlan_cfg['auth'] in ('PSK', 'Auto') and wlan_cfg['wpa_ver'] in ('WPA', 'WPA2', 'WPA-Auto'):
            self.tn.write('3\n')
            ix, mobj, rx = self.expect(['WPA Protocol Version'])
            if ix == -1: raise Exception('Can not set WPA encryption')

            self.tn.write('%d\n' % {'WPA':1,'WPA2':2,'WPA-Auto':3}[wlan_cfg['wpa_ver']])
            ix, mobj, rx = self.expect(['WPA Cipher Type'])
            if ix == -1: raise Exception('Can not set WPA %s' % wlan_cfg['auth'])

            self.tn.write('%d\n' %{'TKIP':1,'AES':2,'Auto':3}[wlan_cfg['encryption']])
            ix, mobj, rx = self.expect(['Enter A New PassPhrase', 'Enter A PassPhrase'])
            if ix == -1: raise Exception('Can not set WPA %s %s' % (wlan_cfg['auth'], wlan_cfg['encryption']))

            self.tn.write('%s\n' % wlan_cfg['key_string'])
            ix, mobj, rx = self.expect(['WPA no error'])
            if ix == -1: raise Exception('Setting WAP encryption options is not successful')
        else:
            raise Exception('Authentication is not available')

        if self.expect_prompt(10)==-1:
            raise Exception('Setting encryption options on Ruckus AP not successful')

    def reboot(self, timeout=180):
        self.tn.write("reboot\n")
        ix,mobj,rx = self.expect(["please wait"])
        time.sleep(10)
        print "Starting the 180 second timeout delay"
        timecount = 0

        # Wait for AP to come up and re-login
        while 1:
            if timecount > timeout:
                raise Exception("Device is not running after reboot after %s seconds" % timeout)
            else:
                timecount = timecount + 0.1
            time.sleep(0.1)

            if len(ping(self.ip_addr)) < 8 or ping(self.ip_addr) == "ok":
                print "Device is pingable.  Sleep for 30 to wait for telnet service on AP"
                time.sleep(30)  # wait for telnet service on AP up
                self.login()
                return

    def set_ssid(self, wlan_if, ssid):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        self.cmd("set ssid %s %s" % (wlan_if_name, ssid))

    def get_ssid(self, wlan_if):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        return self.cmd("get ssid %s" % wlan_if_name)[0].split(' ')[-1]

    def set_state(self, wlan_if, state):
        """
        Note: for AP build 5.0 or above, wlan_if value in wlan_if could be wlan0 to wlan9.
        for 4.x standalone build, it will convert wlan0->svcp,wlan1->home, wlan2->rcks,wlan3->mdfx..
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        return self.cmd("set state %s %s" % (wlan_if_name, state))

    def get_state(self, wlan_if):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        return self.cmd("get state %s" % (wlan_if_name))[0].split(' ')[-1]

    def get_board_data_item(self, line_info, return_line=0):
        data = self.cmd("get boarddata", 4)
        index = 0
        while index < len(data):
            if data[index].find(line_info) != -1:
                if not return_line:
                    return data[index].split(' ')[-1]
                else:
                    return data[index]
            index += 1
        return "unknown"

    def set_timeout(self, timeout = 3600):
        return self.cmd("set timeout %d" % timeout)

    def get_encryption(self, wlan_if):
        """
        Get encryption method of the adapter
        @return a dictionary of encryption information on the specific interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("get encryption %s" %(wlan_if_name))[:-1]

        info = {}
        security = ""
        auth = ""
        encryption = ""
        key_string = ""
        for line in buf:
            temp = [x.strip() for x in line.split(':')]
            if 'ssid' in temp[0].lower():
                info['ssid'] = temp[1]
            if 'security' in temp[0].lower():
                security = temp[1]
            if 'authentication' in temp[0].lower():
                auth = temp[1].split('-')[0]
            if 'cipher' in temp[0].lower():
                encryption = temp[1].split('-')[0]
            if 'passphrase' in temp[0].lower():
                key_string = temp[1]
            if 'protocol' in temp[0].lower():
                info['wpa_ver'] = temp[1].split('-')[0]
            if 'Key' in temp[0]:
                info['key_index'] = temp[0].split()[1]
                key_string = temp[1].split()[-1].strip('"')
            if 'encryption' in temp[0].lower():
                encryption = temp[1]

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

    def change_board_data(self, key, parameter):
        """
        To change the board data info on the AP
        """
        try:
            self.goto_shell()
            self.tn.write('rbd change\n')
            ixx,mobj,rx = self.tn.expect([key], 0.4)
            while ixx !=0:
                self.tn.write('\n')
                ixx,mobj,rx = self.tn.expect([key], 0.4)
            self.tn.write('%s\n' %parameter)
            ixx,mobj,rx = self.tn.expect(['Save Board Data'], 0.4)
            while ixx !=0:
                self.tn.write('\n')
                ixx,mobj,rx = self.tn.expect(['Save Board Data'], 0.4)
            self.tn.write('y\n')
            self.exit_shell()
        except:
            raise Exception('Error during changing %s on Board Data' % key)

    def get_wireless_mac(self):
        data = self.get_board_data_item('wlan0')
        return data.lower()

    def ping(self, target_ip, timeout_ms = 1000):
        """
        ping performs a basic connectivity test to the specified target
        Input:
            - target_ip: an ip address to ping
            - timeout_ms: maximum time for a ping to be done
        Output:
            - A message if ping fails or passes
        """
        self.goto_shell()
        cmd = "ping -c 1 %s" % target_ip

        timeout_s = timeout_ms/1000.0
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < timeout_s:
            self.tn.read_very_eager()
            self.tn.write(cmd+'\n')
            idx, mo, txt = self.tn.expect(['#'])
            buf = txt.split('\n')
            buf = [line.strip('\r').strip() for line in buf][1:len(buf) - 1]

            # Find percentage of packet loss
            pat = ".*, ([0-9]+)% packet loss"
            pkt_loss_percentage = -1
            for line in buf:
                mobj = re.match(pat, line)
                if mobj:
                    pkt_loss_percentage = int(mobj.group(1))
                    break

            current_time = time.time()
            if pkt_loss_percentage == -1:
                self.exit_shell()
                raise Exception("Pattern to find percentage of packet loss does not match")
            elif pkt_loss_percentage < 100:
                self.exit_shell()
                return "Ping OK ~~ %.1f seconds" % (current_time - start_time)
            time.sleep(0.03)

        self.exit_shell()
        return "Timeout exceeded (%.1f seconds)" % timeout_s

    def get_sta_mgmt(self, wlan_if):
        """
        Get status of sta-mgmt of the adapter on the specific interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd('get sta-mgmt %s' % wlan_if_name)[0].split(':')[1]
        buf = [x.strip() for x in buf.split('/')]

        sta_mgmt = {}
        if buf[0].lower().startswith('enabled'):
            sta_mgmt['enable'] = True
            if buf[1].lower() == "active":
                sta_mgmt['active'] = True
            else:
                sta_mgmt['active'] = False
        else:
            sta_mgmt['enable'] = False

        return sta_mgmt

    def set_sta_mgmt(self, wlan_if, enabled = True):
        """
        Set status for sta-mgmt of the adapter on the specific interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        if enabled:
            status = 'enable'
        else:
            status = 'disable'

        buf = self.cmd('set sta-mgmt %s %s' % (wlan_if_name, status))[-1]
        if buf != "OK":
            raise Exception("Can not %s sta-mgmt on the %s interface" % (status, wlan_if_name))

    def goto_shell(self):
        """ Enter into the shell
        """
        self.cmd("set rpmkey cli_esc2shell_ok t")
        self.cmd("!v54!", prompt="#")

    def exit_shell(self):
        """ Exit the shell and log back into CLI
        """
        self.cmd("rkscli")
        self.login()

    def get_device_type(self):
        return self.get_board_data_item("Model:")

    def get_bridge_if_cfg(self):
        """
        This function gets ip configuration information of br interfaces at Linux shell by using command ifconfig
        Return a dictionary contains configuration information of each br interface.
        """
        self.goto_shell()
        self.tn.write('ifconfig\n')
        idx, mobj, txt = self.tn.expect(['#'])
        if idx:
            raise Exception("Error during get config on Bridge interfaces")
        buf = [line.rstrip('\r').strip() for line in txt.split('\n')]

        if_info = {}
        for line in buf:
            if line.startswith("br"):
                inf = line.split()[0]
                mac = line.split()[-1]
            if line.startswith('eth'):
                break
            if line.startswith('inet addr'):
                temp = {}
                inet_addr = line.split()[1:]
                temp['mac'] = mac
                temp['ip_addr'] = inet_addr[0].split(':')[1]
                temp['mask'] = inet_addr[2].split(':')[1]
                if_info['%s' % inf] = temp

        self.exit_shell()
        return if_info

    def _load_information_file(self, ad_info_file):
        """
        Load adapter information file.
        Input:
        - info_file: name of information file.
        Output:
        - info: a dictionary of infomation from the information file
        """
        info = dict()
        cp   = ConfigParser.ConfigParser()
        cp.read(ad_info_file)
        for s in cp.sections():
            for i in cp.items(s):
                info[i[0]] = i[1]

        return info

    def _check_element_present(self, locator, timeout=10):
        """
        Check whether a selenium element locator is present or not
        If that locator can be found before timeout, return True. Otherwise, return False

        Input:
        - locator: element locator to be checked
        - timeout: the maximum time to find the locator
        Output: True/False
        """
        start_time = time.time()
        while True:
            element = self.s.is_element_present(locator)
            if element:
                return True
            if (time.time() - start_time) > timeout:
                return False
            time.sleep(0.5)

    def _safe_type(self, locator, value, timeout=10):
        """
        Make sure that value is set to the locator
        Input:
        - locator:
        - value: the text string set to locator
        - timeout: the maximum time to set the value to the locator
        """
        start_time = time.time()
        while True:
            self.s.type(locator, value)
            if self.s.get_value(locator) == value:
                return True
            if (time.time() - start_time) > timeout:
                return False

    def _type_text(self,locator,value):
        """
        This function is a wrapper of 'type' function in selenium module
        """
        if not self._check_element_present(locator):
            raise Exception("Element %s not found" % locator)
        if not self._safe_type(locator, value):
            raise Exception("Can not set value %s to the element %s" % (value,locator))

    def _click(self, button):
        """
        This function is a wrapper of 'click' function in selenium module
        """
        if not self._check_element_present(button):
            raise Exception("Element %s not found" % button)
        try:
            self.s.click(button)
        except:
            time.sleep(2)
            self.s.click(button)

    def _select_option(self, element, option):
        """
        This function is a wrapper of 'select' function in selenium module
        """
        if not self._check_element_present(element):
            raise Exception("Element %s not found" % element)
        try:
            time.sleep(2)
            tries = 2
            while tries > 0:
                self.s.select(element, "label=regexp:^" + option + "$")
                time.sleep(4)
                if self.s.get_selected_label(element) == option:
                    break
                time.sleep(1)
                tries = tries - 1
        except:
            raise Exception("Option %s not found" % option)

    def _get_text(self,locator):
        """
        This function is a wrapper of 'get_text' function in selenium module
        """
        if not self._check_element_present(locator):
            raise Exception("Element %s not found" % locator)
        try:
            return self.s.get_text(locator)
        except:
            time.sleep(2)
            return self.s.get_text(locator)

    def _login_web_ui(self):
        """
        Login to adapter WebUI
        """
        tries = 3
        while tries:
            if self._check_element_present(self.info['loc_login_username_textbox']):
                try:
                    self._type_text(self.info['loc_login_username_textbox'], self.username)
                    self._type_text(self.info['loc_login_password_textbox'], self.password)
                    time.sleep(2)
                    self._click(self.info['loc_login_image'])
                    self.s.wait_for_page_to_load(20000)
                    if self._check_element_present(self.info['loc_logout_image']):
                        break
                    else:
                        raise
                except:
                    self.selenium.closeAllBrowsers()
                    self.selenium.killServer()
                    time.sleep(10)
                    self.selenium = Selenium(self.browser_type, self.url)
                    self.selenium.loadSelenium()
                    self.s = self.selenium.getClient()
                    time.sleep(5)
            else:
                self._logout_web_ui()
                continue
            time.sleep(3)
            tries = tries - 1

    def _logout_web_ui(self):
        """
        Logout from WebUI
        """
        self._click(self.info['loc_logout_image'])
        self.s.wait_for_page_to_load(20000)
        if not self._check_element_present(self.info['loc_login_username_textbox']):
            self.selenium.closeAllBrowsers()
            self.selenium.killServer()
            time.sleep(10)
            self.selenium = Selenium(self.browser_type, self.url)
            self.selenium.loadSelenium()
            self.s = self.selenium.getClient()
            time.sleep(5)

    def set_ssid_web_ui(self, ssid, is_vf7111 = False):
        """
        Set SSID for adapter from WebUI
        """
        self._login_web_ui()
        if is_vf7111:
            href = self.info['loc_conf_wireless_anchor_vf7111']
            href = href.replace('$_$', self.url)
            self._click(href)
            href_video = self.info['loc_conf_wireless_video_anchor_vf7111']
            href_video = href_video.replace('$_$', self.url)
            self._click(href_video)
        else:
            self._click(self.info['loc_conf_wireless_anchor'])
            self.s.choose_ok_on_next_confirmation()
            self._select_option(self.info['loc_conf_wireless_countrycode_option'], self.info['const_countrycode'])
            if self.s.is_confirmation_present():
                self.s.get_confirmation()

        time.sleep(2)
        try:
            if is_vf7111:
                self._type_text(self.info['loc_conf_wireless_ssid_textbox_vf7111'], ssid)
            else:
                self._type_text(self.info['loc_conf_wireless_ssid_textbox'], ssid)

            self._click(self.info['loc_conf_wireless_update_button'])
            if self.s.is_alert_present():
                msg_alert = self.s.get_alert()
                self._logout_web_ui()
                raise Exception(msg_alert)
            self._logout_web_ui()
        except Exception, error:
            if str(error).find("Timed out") != -1:
                self.selenium.closeAllBrowsers()
                self.selenium.killServer()
            else:
                raise Exception(error.message)

    def set_encryption_web_ui(self, encryption_cfg, is_vf7111 = False):
        """
        Set wlan configuration for adapter
        @param auth: authentication method (open, shared, PSK, Auto)
        @param encryption: WEP-64, WEP-128, TKIP, AES, Auto
        @param key_index: WEP key index
        @param key_string: a string of passphrase or wep key
        @param wpa_ver: WPA, WPA2, WPA-Auto
        """
        self._login_web_ui()
        if is_vf7111:
            href = self.info['loc_conf_wireless_anchor_vf7111']
            href = href.replace('$_$', self.url)
            self._click(href)
            href_video = self.info['loc_conf_wireless_video_anchor_vf7111']
            href_video = href_video.replace('$_$', self.url)
            self._click(href_video)
        else:
            self._click(self.info['loc_conf_wireless_anchor'])
            self.s.choose_ok_on_next_confirmation()
            self._select_option(self.info['loc_conf_wireless_countrycode_option'], self.info['const_countrycode'])
            if self.s.is_confirmation_present():
                self.s.get_confirmation()

        time.sleep(2)

        wep_auth_list = [self.info['const_auth_method_open'], self.info['const_auth_method_shared'],
                         self.info['const_auth_method_auto']]
        wep_encryption_list = [self.info['const_encryption_method_wep64'], self.info['const_encryption_method_wep128']]
        wpa_auth_list = [self.info['const_auth_method_psk'], self.info['const_auth_method_auto']]
        wpa_ver_list = [self.info['const_encryption_method_wpa'], self.info['const_encryption_method_wpa2'],
                        self.info['const_encryption_method_wpa_auto']]
        element = self.info['loc_conf_wireless_encryption_option']
        element_vf7111 = self.info['loc_conf_wireless_encryption_option_vf7111']

        if encryption_cfg['auth'] == self.info['const_auth_method_open']:
            if encryption_cfg['encryption'] == self.info['const_encryption_method_none']:
                if is_vf7111:
                    self._select_option(element_vf7111, "Disabled")
                else:
                    self._select_option(element, "Disabled")

        elif encryption_cfg['auth'] in wep_auth_list and encryption_cfg['encryption'] in wep_encryption_list:
            self._select_option(element, "WEP")
            time.sleep(1)

            # Choose authentication method
            if encryption_cfg['auth'] == wep_auth_list[0]:
                button = self.info['loc_conf_wireless_wep_auth_open_button']
            elif encryption_cfg['auth'] == wep_auth_list[1]:
                button = self.info['loc_conf_wireless_wep_auth_shared_button']
            elif encryption_cfg['auth'] == wep_auth_list[2]:
                button = self.info['loc_conf_wireless_wep_auth_auto_button']
            self._click(button)
            time.sleep(1)

            # Choose encryption method
            wep_method = self.info['loc_conf_wireless_wep_encryption_option']
            temp = self.s.get_select_options(wep_method)
            if encryption_cfg['encryption'] == wep_encryption_list[0]:
                self._select_option(wep_method, temp[0])
                time.sleep(2)
                if len(encryption_cfg['key_string']) == 10:
                    self._click(self.info['loc_conf_wireless_wep_key_entry_hex_button'])
                elif len(encryption_cfg['key_string']) == 5:
                    self._click(self.info['loc_conf_wireless_wep_key_entry_ascii_button'])

            elif encryption_cfg['encryption'] == wep_encrytion_list[1]:
                self._select_option(wep_method, temp[1])
                time.sleep(2)
                if len(encryption_cfg['key_string']) == 26:
                    self._click(self.info['loc_conf_wireless_wep_key_entry_hex_button'])
                elif len(encryption_cfg['key_string']) == 13:
                    self._click(self.info['loc_conf_wireless_wep_key_entry_ascii_button'])

            # Enter key string
            self._type_text(self.info['loc_conf_wireless_wep_key_textbox'], encryption_cfg['key_string'])

            # Select wep key index
            index = self.info['loc_conf_wireless_wep_key_index_option']
            self._select_option(index, encryption_cfg['key_index'])

        elif encryption_cfg['auth'] in wpa_auth_list and encryption_cfg['wpa_ver'] in wpa_ver_list:
            if is_vf7111:
                self._select_option(element_vf7111, "WPA")
            else:
                self._select_option(element, "WPA-PSK")
            time.sleep(1)

            if not is_vf7111:
                if encryption_cfg['wpa_ver'] == wpa_ver_list[0]:
                    self._click(self.info['loc_conf_wireless_wpa_version_button'])
                elif encryption_cfg['wpa_ver'] == wpa_ver_list[1]:
                    self._click(self.info['loc_conf_wireless_wpa2_version_button'])
                elif encryption_cfg['wpa_ver'] == wpa_ver_list[2]:
                    self._click(self.info['loc_conf_wireless_wpaauto_version_button'])

                if encryption_cfg['encryption'] == self.info['const_algorithm_tkip']:
                    self._click(self.info['loc_conf_wireless_wpa_tkip_button'])
                elif encryption_cfg['encryption'] == self.info['const_algorithm_aes']:
                    self._click(self.info['loc_conf_wireless_wpa_aes_button'])
                elif encryption_cfg['encryption'] == self.info['const_algorithm_auto']:
                    self._click(self.info['loc_conf_wireless_wpa_auto_button'])

                self._type_text(self.info['loc_conf_wireless_wpa_passphrase_textbox'], encryption_cfg['key_string'])

            else:
                if encryption_cfg['wpa_ver'] == wpa_ver_list[0]:
                    self._click(self.info['loc_conf_wireless_wpa_version_button_vf7111'])
                elif encryption_cfg['wpa_ver'] == wpa_ver_list[1]:
                    self._click(self.info['loc_conf_wireless_wpa2_version_button_vf7111'])
                elif encryption_cfg['wpa_ver'] == wpa_ver_list[2]:
                    self._click(self.info['loc_conf_wireless_wpaauto_version_button_vf7111'])

                if encryption_cfg['encryption'] == self.info['const_algorithm_aes']:
                    self._click(self.info['loc_conf_wireless_wpa_aes_button_vf7111'])

                self._type_text(self.info['loc_conf_wireless_wpa_passphrase_textbox_vf7111'], encryption_cfg['key_string'])
        try:
            self._click(self.info['loc_conf_wireless_update_button'])
            if self.s.is_alert_present():
                msg_alert = self.s.get_alert()
                self._logout_web_ui()
                raise Exception(msg_alert)
            self._logout_web_ui()
        except Exception, error:
            if str(error).find("Timed out") != -1:
                self.selenium.closeAllBrowsers()
                self.selenium.killServer()
            else:
                raise Exception(error.message)

    def get_device_status_web_ui(self):
        """
        Get status of adapter from WebUI
        @return a dictionary of device information
        """
        self._login_web_ui()
        self._click(self.info['loc_status_device_anchor'])
        time.sleep(1)

        i = 1
        status_list = []
        while True:
            cell = self.info['loc_status_device_cell']
            cell = cell.replace('$_$', str(i))
            if self._check_element_present(cell):
                text = self._get_text(cell)
                status_list.append(text)
            else:
                break
            i += 1
            time.sleep(1)
        self._logout_web_ui()

        res = {}
        for item in status_list:
            if item.lower().startswith('device name'):
                res['device_name'] = item.split(':')[1].strip()
            elif item.lower().startswith('mac address'):
                temp = item.split()[-1].split(':')[1:]
                res['mac'] = ':'.join(temp)
            elif item.lower().startswith('serial'):
                res['serial_num'] = item.split(':')[-1].strip()
            elif item.lower().startswith('software'):
                res['version'] = item.split(':')[-1].strip()
            elif item.lower().startswith('uptime'):
                res['uptime'] = item.split(':')[-1]
            elif item.lower().startswith('home'):
                if item.split(':')[-1].strip().lower().startswith("disabled"):
                    res['home_protection'] = False
                else:
                    res['home_protection'] = True

        return res

    def set_system_name_web_ui(self, system_name):
        """
        Set system name for adapter from WebUI
        """
        self._click(self.info['loc_conf_device_anchor'])
        self._type_text(self.info['loc_conf_device_name_textbox'], system_name)
        time.sleep(2)

        self._click(self.info['loc_conf_wireless_update_button'])
        if self.s.is_alert_present():
            msg_alert = self.s.get_alert()
            raise Exception(msg_alert)

    def set_home_protection(self, enable = True):
        """
        Enable/disable home proctection for adapter from WebUI
        """
        self._login_web_ui()
        self._click(self.info['loc_conf_device_anchor'])
        time.sleep(2)
        if enable:
            self._click(self.info['loc_conf_device_home_protection_enable_button'])
        else:
            self._click(self.info['loc_conf_device_home_protection_disable_button'])
        self._click(self.info['loc_conf_wireless_update_button'])
        self._logout_web_ui()

    def get_serial_num(self):
        return self.get_board_data_item("Serial#:")

    def get_version(self):
        res = self.cmd("get version")
        version = ""
        for line in res:
            if line.lower().startswith('version'):
                version = line.split()[-1]
                break
        if not version:
            raise Exception('Can not get software version')
        return version

    def get_home_login_info(self):
        """
        Get information of home user
        """
        self._login_web_ui()
        self._click(self.info['loc_conf_device_anchor'])
        time.sleep(2)

        info = {}
        if self._check_element_present(self.info['loc_conf_device_home_username_textbox']):
            info['username'] = self.s.get_value(self.info['loc_conf_device_home_username_textbox'])
        if self._check_element_present(self.info['loc_conf_device_home_password_textbox']):
            info['password'] = self.s.get_value(self.info['loc_conf_device_home_password_textbox'])

        self._logout_web_ui()
        return info

    def get_base_mac(self):
        """
        Return the device Mac address of the adapter
        """
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search('base ([0-9,a-f,A-F]+:*)*', x)][0]

    def get_channel(self, wlan_if):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("get channel %s" % wlan_if_name)
        if res[-1].lower() != 'ok':
            res = self.cmd("get channel "+ wlan_if)

        channel_data = res[0]
        channel = channel_data.split(' ')[2]
        if not channel.isdigit():
            channel = 0
        else:
            channel = int(channel)
        if channel_data.find("Auto") != -1:
            mode = "Auto"
        else:
            mode = "Manual"
        return (channel, mode)

    def set_channel(self, wlan_if, channel):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set channel %s %s" % (wlan_if_name, channel))[-1]
        if res.lower() != 'ok':
            self.cmd("set channel %s %s" % (wlan_if, channel))

if __name__ == "__main__":
    url = "http://192.168.50.191:25401"
    config = {'browser_type':'firefox', 'url':url, 'username':'super', 'password':'sp-admin'}
    en = {'encryption': 'AES', 'wpa_ver': 'WPA2', 'auth': 'PSK', 'key_string':'1234567890'}

    ad = RuckusAD(config)
    print ad.get_device_status_web_ui()
