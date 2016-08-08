# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
RuckusAP interfaces with and controls any Ruckus Access Point via telnet CLI.
For wlan interface specific commands such as 'set ssid wlan_if', wlan interface ID
(wlan0, wlan1, etc) is used as argument.

Usage Example:

    from ratenv import *
    dd = dict(ip_addr='192.168.0.200', username='admin', password='admin', init=False)
    apx = RuckusAP.RuckusAP(dd)
    apx.initlialize()
    print "AP Mgmt_VLan: %s" % ap.get_mgmt_vlan()

"""

import os
import logging
import time
import re
import copy
import socket
import telnetlib
import tarfile
import ftplib
import shutil
import paramiko
import urllib
import urllib2

from RuckusAutoTest.models import TestbedComponent
from RuckusAutoTest.components.DUT import DUT
from RuckusAutoTest.components.FTPServer import FTPServer
from RuckusAutoTest.common.Ratutils import get_indexed_item, ping, rlstrip_list, \
        remove_blanks_from_list, get_uptime
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common.utils import try_interval, try_times
from RuckusAutoTest.components.lib import FeatureUpdater as ftup
from RuckusAutoTest.common import lib_FeatureList as ftlist
from RuckusAutoTest.common.utils import *


URL_SESAME = "http://sesame.video54.local/fq.asp" #@author: yuyanan @since: 2014-8-25 bug:zf-8381

INTERNAL_WLAN = {
    'name': ['meshd', 'meshu', 'recovery-ssid', 'wlan50', 'wlan51', ],
    'type': ['MON', '???'], # has wlan50 and wlan51
}


class RuckusAP2(DUT):
    '''
    '''
        
    BRCTL_SHOW_HEADER =  ['bridge', 'HostOnly', 'Bridge id', 'STP', 'PIF', 'Serv', 
            'ABF Serv', 'Mode', 'Port', 'Learning', 'PFF', 'Untagged vlan', 'Enabled vlans']
    BRCTL_SHOW_HEADER_FOREPART =  ['bridge', 'HostOnly', 'Bridge id', 'STP', 'PIF']
    BRCTL_SHOW_HEADER_BACKPART = ['Serv', 'ABF Serv', 'Mode', 'Port', 'Learning', 'PFF', 'Untagged vlan', 'Enabled vlans']
    
    
    feature_update = {}


    def __init__(self, config):
        """
        Connect to the Ruckus AP at the specified IP address via telnet.
        The specified login credentials will be used.
        All subsequent CLI operations will be subject to the specified default timeout.
        If log_file is specified then out CLI output will be logged to the specified file.
        This will enable telnet if telnet is not already enabled.
        """
        component_info = TestbedComponent.objects.get(name='RuckusAP')
        DUT.__init__(self, component_info, config)

        self.conf = dict(
            ip_addr = '192.168.0.1', username = 'super', password = 'sp-admin',
            timeout = 10, ftpsvr = '', log_file = '', init = True,
            debug = False, telnet = True, port = 23, force_telnet = False,
            ssh_port = 22,
        )

        self.conf.update(config)

        self.accumulate_attrs()

        if self.conf['init']:
            self.initialize()

        # register itself to Feature Updater
        ftup.FeatureUpdater.register(self)

        self.update_feature()


    def __del__(self):
        self.close()


    def initialize(self):
        if self.conf['debug']: bugme.pdb.set_trace()
        self.ip_addr = self.conf['ip_addr']
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.timeout = self.conf['timeout']  # default timeout
        self.ftpsvr = FTPServer(self.conf['ftpsvr']) if self.conf['ftpsvr'] else ''
        self.log_file = self.conf['log_file']
        self.telnet  = self.conf['telnet']
        self.port = self.conf['port']
        self.prompt = "rkscli:"
        self.base_mac_addr = '00:00:00:00:00:00'

        # global pause seconds to overwrite default pause/sleep times
        self.pausedict = dict(after_reboot=5)
        if self.conf.has_key('pausedict'):
            self.pausedict.update(self.conf['pausedict'])

        if self.telnet:
            self.login(self.port)
        else:
            self.login_via_ssh(self.conf['ssh_port'])
        self.mac_addr = self.get_eth0_mac()

        #self.login_via_ssh(self.port)
        self.CPU_USAGE_INFO = 0
        self.MEMORY_INFO = 1

        # for display we would not talk to AP; use the first one
        self.base_mac_addr = self.get_base_mac().lower()
        logging.info("Creating RuckusAP [%s %s] " % (self.base_mac_addr, self.ip_addr))
        self.mgmt_vlan = self.get_ip_cfg("wan")['vlan']
        if self.mgmt_vlan:
            logging.info("AP Mgmt_Vlan: %s" % (self.mgmt_vlan))
        self.zd_ip_list = self.get_director_cfg()
        logging.info("Directory IP: %s" % (self.zd_ip_list)) 
        
        #@author:yuyanan @since: 2014-8-25 zf-8381
        #Get sesame key for AP.
        self.sesame_key = self.get_sesame_key()

        
        

    def log(self, txt):
        """Log specified text if a log_file is configured"""
        if self.log_file:
            stime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            self.log_file.write("\r%s\r%s" % (stime, txt))

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_ip_addr(self):
        return self.ip_addr


    def expect(self, expect_list, timeout = 0):
        """
        A wrapper around the telnetlib expect().
        This uses the configured timeout value and logs the results to the log_file.
        Returns the same tuple as telnetlib expect()
        """
        if not timeout:
            timeout = self.timeout
        ix, mobj, rx = (-1, None, "")
        ix, mobj, rx = self.tn.expect(expect_list, timeout)
        self.log(rx)
        return (ix, mobj, rx)

    def expect_prompt(self, timeout = 0, prompt = ""):
        """Expect a prompt and raise an exception if we don't get one. Returns only input."""
        if not prompt:
            target_prompts = [self.prompt]
        elif type(prompt) is list:
            target_prompts = prompt
        else:
            target_prompts = [prompt]

        ix, mobj, rx = self.expect(target_prompts, timeout = timeout)
        if ix:
            # mesh AP seems to response slower; give it another try anyway
            ix, mobj, rx = self.expect(target_prompts, timeout=30)
            if ix:
                raise Exception("Prompt %s not found" % prompt)
        return rx

    def login(self, port=23, interval = 2):
        '''
        . Login to AP. If a telnet session is already active this will close
          that session and create a new one.
          allo to change default interval sleep before try another login to 120 if set_factory is called
        '''
        for z in try_times(3, interval):
            try:                                
                logging.info("Login to RuckusAP [%s %s] " \
                             % (self.base_mac_addr, self.ip_addr))
                if not self.conf.get('force_telnet', False):
                    self.enable_telnet_via_ssh()
                self.tn = telnetlib.Telnet(self.ip_addr, port)
                break
                        
            except:
                # if force_telnet = True, it means only using telnet to connect.
                # No enable telnet via ssh                
                if not self.conf.get('force_telnet', False):
                    self.enable_telnet_via_ssh()
                if z == 3:
                    #log_trace()
                    logging.info('Unable to login to AP  [%s %s] ' \
                                    % (self.base_mac_addr, self.ip_addr))
                    raise
                
        ix,mobj,rx = self.expect(["login"])
        if ix == -1:
            try:
                # special condition for sim-ap which started up in shell mode
                self.tn.write("rkscli\n")
            except:
                pass
        else:
		    #@auther:yin.wenling AP OTA
            try:
                self.tn.write(self.username+"\n")
                ix2,mobj,rx = self.expect(["password"])
                if ix or ix2:
                    raise Exception("Login Error")
                self.tn.write(self.password+"\n")
                self.expect_prompt(30)
            except:
                self.tn.write('super'+"\n")
                ix2,mobj,rx = self.expect(["password"])
                if ix or ix2:
                    raise Exception("Login Error")
                self.tn.write('sp-admin'+"\n")
                self.expect_prompt(30)
        
        self.set_timeout() # set default timeout for AP


    def _wait_for(self, chan, text, recv_bufsize=1024, retry=200, pause=0.02):
        '''
        quick and dirty excpect substitute for paramiko channel;
        Raise exception if text not found.
        ssh=dict(pause=0.02, retry=200, recv_bufsize=1024, port=22),
        '''
        for x in range(retry):
            if chan.recv_ready():
                data = chan.recv(recv_bufsize)
                print data
                if text in data:
                    return # success
            time.sleep(pause) # 100*.02 = approx 2 seconds total
        raise Exception("SSH expect")


    def _ssh(self, port, is_enabling=True, retries=3):
        if is_enabling:
            logging.info("SSH to RuckusAP [%s %s] to enable telnet" \
                         % (self.base_mac_addr, self.ip_addr))
        for i in try_times(retries, 5):
            try:
                t = paramiko.Transport((self.ip_addr, port))
                t.connect(username = "", password = "", hostkey = None)
                # t.connect(username = "super", password = "sp-admin", hostkey = None)
                chan = t.open_session()
                chan.get_pty()
                chan.invoke_shell()
                self._wait_for(chan, 'login')
                chan.send(self.username + "\n")
                self._wait_for(chan, 'password')
                chan.send(self.password + "\n")
                self._wait_for(chan, 'rkscli:')

                if is_enabling:
                    chan.send("set rpmkey telnetd-port-number %s\n" % self.conf['port'])
                    self._wait_for(chan, 'OK')
                    chan.send("set telnet disable\n")
                    self._wait_for(chan, 'OK')
                    time.sleep(2)
                    chan.send("set telnet enable\n")
                    self._wait_for(chan, 'OK')
                    print 'Enable telnet success'

                chan.close()
                t.close()
                del chan, t
                return
            except:
			    #@auther:yin.wenling AP OTA
                try:
                    t = paramiko.Transport((self.ip_addr, port))
                    t.connect(username = "", password = "", hostkey = None)
                    # t.connect(username = "super", password = "sp-admin", hostkey = None)
                    chan = t.open_session()
                    chan.get_pty()
                    chan.invoke_shell()
                    self._wait_for(chan, 'login')
                    chan.send('super' + "\n")
                    self._wait_for(chan, 'password')
                    chan.send('sp-admin' + "\n")
                    self._wait_for(chan, 'rkscli:')
    
                    if is_enabling:
                        chan.send("set rpmkey telnetd-port-number %s\n" % self.conf['port'])
                        self._wait_for(chan, 'OK')
                        chan.send("set telnet disable\n")
                        self._wait_for(chan, 'OK')
                        time.sleep(2)
                        chan.send("set telnet enable\n")
                        self._wait_for(chan, 'OK')
                        print 'Enable telnet success'
    
                    chan.close()
                    t.close()
                    del chan, t
                    return
                except:
                    pass
            #finally:
                if i == retries:
                    logging.info(("Unable to login ssh via [%s:%s]" % (self.ip_addr, port)))
                    raise #Exception("Unable to login ssh via [%s:%s]" % (self.ip_addr, port))


    def enable_telnet_via_ssh(self):
        return self._ssh(self.conf['ssh_port'], is_enabling=True)

    def login_via_ssh(self, port=22):
        return self._ssh(port, is_enabling=False)


    def close(self):
        """Terminate the telnet session"""
        try:
            self.tn.close()
            time.sleep(0.5)#Make sure current session can be closed immediately.
        except:
            pass

    #@auther:yin.wenling AP OTA
    def do_cmd(self, cmd_text, timeout = 0, prompt = "",force_ssh=False):
        if force_ssh:
            return self.cmd(cmd_text, timeout = timeout, prompt = prompt, return_list = False,force_ssh=True)
        else:
            return self.cmd(cmd_text, timeout = timeout, prompt = prompt, return_list = False)

    def cmd(self, cmd_text, timeout = 0, prompt = "", return_list = True,force_ssh = False):
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

        try:
            # empty input buffer and log if necessary
            self.log(self.tn.read_very_eager())
            # issue command
            #@author: chen.tao 2013-12-19, to fix bug ZF-6354
            if type(cmd_text) == type(u'This_is_a_unicode_string'):
                cmd_text = cmd_text.encode('ascii') 
            #@author: chen.tao 2013-12-19, to fix bug ZF-6354
            logging.debug('[AP CMD INPUT] %s' % cmd_text)
            self.tn.write(cmd_text + "\n")
            # get result
            r = self.expect_prompt(prompt = prompt)  # logs as side-effect
            logging.debug('[AP CMD OUTPUT] %s' % r)
        except (EOFError, Exception, socket.error):
            if force_ssh:
                logging.info("Telnet session had been disconnected. Try to relogin to the AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
                r = self._ssh_ap_cli_send(cmd_text,prompt=prompt)
                r = r[:-1]
            else:
                logging.info("Telnet session had been disconnected. Try to relogin to the AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
                try:
                    self.login()
                except:
                    self.enable_telnet_via_ssh()
                    self.login()
                self.tn.write(cmd_text + "\n")
                r = self.expect_prompt(prompt = prompt)

        if return_list:
            # split at newlines
            rl = r.split("\n")
            # remove any trailing \r
            rl = [x.rstrip('\r') for x in rl]
            # filter empty lines and prompt
            rl = [x for x in rl if x and not x.endswith(prompt)]
            return rl[1:] # remove cmd_text from output
        else:
            return r
        
    def _ssh_ap_cli_send(self,text,prompt = '',username='super',password='sp-admin',port=22,ip_addr='169.254.1.1'):
        """
        """
        t = paramiko.Transport((self.ip_addr,port))  
        t.connect(username="",password="")
        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()
        self._wait_for(chan, 'login')
        chan.send(username + "\n")
        self._wait_for(chan, 'password')
        chan.send(password + "\n")
        self._wait_for(chan, 'rkscli:')
        
        if prompt=='#':
            chan.send("!v54!" + "\n")
            time.sleep(.5) 
            chan.send("\n")
            self._wait_for(chan, '#')
        chan.send(text + "\n")
        time.sleep(1)
        for x in range(3):
            if chan.recv_ready():
                return_value = chan.recv(2048)
                chan.close()
                t.close()
                del chan,t
                return return_value
            time.sleep(0.02)
        raise Exception("SSH Send Failed")
    
    def verify_component(self):
        """ Perform sanity check on the component: the AP is there
            Device should already be logged in.
        """
        logging.info("Sanity check: Verify Test engine execute command on AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
        self.get_version()

    def get_base_mac(self):
        """
        Return the device Mac address of the AP
        """
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search('base ([0-9,a-f,A-F]+:*)*', x)][0]
    
    def get_config_wlan_psk(self,ap_mac):
        ap_mac = ap_mac.replace(":","").replace("-","")
        island_name = "island-%s" % ap_mac[6:]
        self.login()
        self.goto_shell()
        cmd = "wrad_cli psk %s" % island_name
        buff = self.cmd(cmd,prompt='#')
        if buff:
            return buff[2].split(':')[1].replace(' ','')
        else:
            raise "Failed to get psk"
        
    def get_bssid(self,wlan_if='wlan0'):
        """
        Return the device Mac address of the AP
        """
        return [x.split('yes')[-1] for x in self.cmd('get boarddata') if re.search('%s:    yes ([0-9,a-f,A-F]+:*)*'%wlan_if, x)][0].strip()

    def get_version(self):
        """Return the AP Software version string reported by 'get version'"""
        ss = self.cmd("get version", return_list=False)
        mm = re.search(r'version:\s*([\d.]+)', ss, re.I)
        if mm:
            return mm.group(1)

        return '0.0.0.0.0'
    
    def get_primary_secondary_img_version(self):
        '''
        return primary version,secondary version
        '''
        """
            after type fw show all in apcli the following info will be shown on the screen:
             
            rkscli: fw show all
            <Control Info>
            ipaddr: 0.0.0.0
            file: zf2942/9.3.0.0.87/rcks_fw.bl7.main
            size: 6684672
            MD5 : 1129983D49B974BF96F375DF76730AAD
            type: 0
            local_file
            -------------------------------------
            current primary boot image is Image1
            ---------------<Image1 FW header>
            Magic:        RCKS
            next_image:   d0000
            invalid:      0
            hdr_len:      160
            compression:  l7
            load_address: 0x80041000
            entry_point:  0x802C6000
            timestamp:    Thu Jan 12 03:04:26 2012
            binl7_len:    6684512
            hdr_version:  3
            hdr_cksum:    0x0A32
            version:      9.3.0.0.87        ( 9.3.0.0.87 )
            MD5:          1129983D49B974BF96F375DF76730AAD
            product:      zf2925    (0)
            architecture: 1
            chipset:      0
            board_type:   5
            board_class:  2
            customer:
            ---------------<Image2 FW header>
            Magic:        RCKS
            next_image:   d0000
            invalid:      0
            hdr_len:      160
            compression:  l7
            load_address: 0x80041000
            entry_point:  0x802CB000
            timestamp:    Wed Feb 22 00:09:05 2012
            binl7_len:    6606688
            hdr_version:  3
            hdr_cksum:    0x4012
            version:      9.4.0.0.27        ( 9.4.0.0.27 )
            MD5:          9FDFE7F387B50096FDD100DE29FB8C8C
            product:      zf2925    (0)
            architecture: 1
            chipset:      0
            board_type:   5
            board_class:  2
            customer:
            OK
        """
        l = self.cmd("fw show all")
        version={'img1':'',
                 'img2':''
                 }
        img = 'img1'
        for s in l:
            if 'version' in s and 'hdr_version' not in s:
                version[img]=s.split()[1]
                if img == 'img2':
                    break
                img='img2'
                
        if 'current primary boot image is Image1' in l:
            return version['img1'],version['img2']
        else:
            return version['img2'],version['img1']
    
    def verify_primary_secondary_img_version_after_upgrade(self,basebuild,targetbuild):
        only_upgrade_one=False
        if basebuild<targetbuild and basebuild>'9.2' or basebuild>targetbuild:
            only_upgrade_one=True
        logging.info('base build is %s,target is %s'% (basebuild,targetbuild))
        primary,secondary=self.get_primary_secondary_img_version()
        logging.info('primary version is %s,secondary version is %s'% (primary,secondary))
        
        if only_upgrade_one:
            if not (primary,secondary)==(targetbuild,basebuild):
                msg='build number do not match,primary:%s,secondary:%s,basebuild:%s,targetbuild:%s' %(primary,secondary,basebuild,targetbuild)
                logging.info(msg)
                return False,msg 
        elif not (primary,secondary)==(targetbuild,targetbuild):
            msg='build number do not match,primary:%s,secondary:%s,basebuild:%s,targetbuild:%s' %(primary,secondary,basebuild,targetbuild)
            logging.info(msg)
            return False,msg
        return True,'build number match,primary:%s,secondary:%s,basebuild:%s,targetbuild:%s' %(primary,secondary,basebuild,targetbuild)
        
            
    
    def get_wlan_list(self):
        """
        DO NOT use this method. Use get_wlan_info_dict instead.
        return list version of 'get wlanlist' cli command
        """
        # only interested in the lines with MAC Address in it.
        return [x.split() for x in self.cmd("get wlanlist")if re.search('([0-9a-fA-F:]{17})', x)]

    def get_local_date_time(self):
        '''
        Get current local time of AP from cmd 'get ntp'
        '''
        local_date_time = self.cmd("get ntp")[0].split(": ")[-1]
        return dict(CurrentLocalTime = local_date_time)

    def get_wlan_info_dict(self,force_ssh=False):
        '''
        Get all info from cmd 'get wlanlist'
        '''
        result = {}

        res = self.cmd("get wlanlist",force_ssh=force_ssh)
        coloum_name = res[0].split()
        items = res[2:-1]
        
        for item in items:
            temp = dict.fromkeys(coloum_name, "")
            item = item.split()
            
            if len(item) > len(coloum_name):
                item[-2] = item[-2]+" "+item[-1]
                item.remove(item[-1])
                
            for y in range(len(item)):
                temp[coloum_name[y]] = item[y]
            
            result[item[3]] = temp
            
        return result
    
    
    def get_info_for_external_wlans(self):
        '''
        Get all info of the wlans created by users from cmd 'get wlanlist'.
        '''
        result = {}
        list_info = []
        for x in self.cmd("get wlanlist"):
            if re.search('bssid',x):
                list_info = x.split()

            if re.search('([0-9a-fA-F:]{17})',x):
                # result of list_value : ['svcp', 'up', 'AP', 'wlan0', '00:1F:41:24:6E:B8']
                list_value = x.split()
                if list_value[0] in INTERNAL_WLAN['name'] or list_value[2] in INTERNAL_WLAN['type']:           
                    continue
                temp = {}
                for i in range(len(list_info)):
                    temp[list_info[i]] = list_value[i]
                #get ssid according to wlanID
                ssid = self.get_ssid(list_value[3])
                temp['ssid'] = ssid
                result[list_value[3]] = temp

        return result


    def wlan_if_to_name(self, wlan_if,force_ssh=False):
        """return the internal AP wlan name (e.g. 'svcp') given a wlan_if (wlanXX)  name
        """
		#@auther:yin.wenling ap ota
        wlan_if_to_name_dict = self.get_wlan_info_dict(force_ssh=force_ssh)
        for (wlan_id, wlan) in wlan_if_to_name_dict.iteritems():
            # verify each line in 'get wlanlist' has column wlanID
            if wlan['wlanID'] and wlan['wlanID'] == wlan_if:
                return wlan['name']

        raise Exception("Convert wlan interface %s to name failed. Wlan interface not found in 'get wlanlist' "
                        % wlan_if)
        
    def wlan_name_to_if(self, wlan_name):
        """return the internal AP wlan if (e.g. 'wlan0') given a wlan name (e.g. 'home')
        """
        for (wlan_id, wlan) in self.get_wlan_info_dict().iteritems():
            # verify each line in 'get wlanlist' has column wlanID
            if wlan['name'] and wlan['name'] == wlan_name:
                return wlan['wlanID']

        raise Exception("Convert wlan name %s to interface failed. Wlan name not found in 'get wlanlist' "
                        % wlan_name)
        
    def bssid_to_wlan_if(self, bssid):
        for (wlan_id, wlan) in self.get_wlan_info_dict().iteritems():
            if wlan.get("bssid") and wlan.get("bssid") == bssid:
                return wlan_id
        raise Exception("Convert bssid %s to wlan interface failed. Wlan interface not found in 'get wlanlist' "
                        % bssid)

    def remove_wlan(self, wlan_cfg):
        """
        Turn off wlan interface on AP.
        Note: for AP build 5.0 or above, wlan_if value in wlan_cfg could be wlan0 to wlan9.
        for 4.x standalone build, it will convert wlan0->svcp,wlan1->home, wlan2->rcks,wlan3->mdfx..
        """
        return self.set_state(self.wlan_if_to_name(wlan_cfg['wlan_if']), "down")


    def remove_all_wlan(self):
        # use Wlan interface from wlanlist instead of wlan name to call set_state
        for (wlan_id, wlan) in self.get_wlan_info_dict().iteritems():
            if wlan['name'] in ['meshd', 'meshu']:
                continue

            self.set_state(wlan['wlanID'], "down")


    def enable_all_wlan(self):
        """
        Enable all wlan that we have on the device
        """
        for (wlan_id, wlan) in self.get_wlan_info_dict().iteritems():
            self.set_state(wlan['wlanID'], "up")


    def cfg_wlan(self, wlan_cfg):
        """
        Configure the specified wlan interface with the specified auth parameters:
        """
        zf_ap = False
        model = self.get_device_type()
        if model.lower().startswith('zf'):
            zf_ap = True

        self.log(self.tn.read_very_eager())
        #Cherry-2011-07-20: Convert wlan interface to wlan name.
        #When call set encryption, need to use wlan name instead of wlan interface.
        wlan_name = self.wlan_if_to_name(wlan_cfg['wlan_if'])
        
        if wlan_cfg.has_key('ssid'):
            self.set_ssid(wlan_cfg['wlan_if'], wlan_cfg['ssid'])

        self.tn.write('set encryption %s\n' % wlan_name)
        
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

        elif wlan_cfg['auth'] in ('PSK', 'EAP', 'Auto') and wlan_cfg['wpa_ver'] in ('WPA', 'WPA2', 'WPA-Auto'):
            self.tn.write('3\n')
            ix, mobj, rx = self.expect(['WPA Protocol Version'])
            if ix == -1: raise Exception('Can not set WPA encryption')
            self.tn.write('%d\n' % {'WPA':1, 'WPA2':2, 'WPA-Auto':3}[wlan_cfg['wpa_ver']])
            ix, mobj, rx = self.expect(
                ['WPA Authentication Type', 'WPA Cipher Type']
            )
            # Default authen type is PSK in "the build 8.5, 5.3". Cannot set it
            if ix == -1: raise Exception('Can not set WPA %s %s' % (wlan_cfg['auth'], wlan_cfg['wpa_ver']))
            elif ix == 0:
                self.tn.write('%d\n' % {'PSK':1, 'EAP':2, 'Auto':3}[wlan_cfg['auth']])
                ix, mobj, rx = self.expect(['WPA Cipher Type'])
                if ix == -1: raise Exception('Can not set WPA %s' % wlan_cfg['auth'])
            self.tn.write('%d\n' % {'TKIP':1, 'AES':2, 'Auto':3}[wlan_cfg['encryption']])

            if wlan_cfg['auth'] in ('PSK', 'Auto'):
                ix, mobj, rx = self.expect(['Enter A New PassPhrase', 'Enter A PassPhrase'])
                if ix == -1: raise Exception('Can not set WPA %s %s' % (wlan_cfg['auth'], wlan_cfg['encryption']))
                self.tn.write('%s\n' % wlan_cfg['key_string'])

            if wlan_cfg['auth'] in ('EAP', 'Auto'):
                ix, mobj, rx = self.expect(['Enter A New NAS-ID', 'Enter A NAS-ID'])
                if ix == -1: raise Exception('Can not set WPA %s %s' % (wlan_cfg['auth'], {'Auto': wlan_cfg['key_string']
                                                                    , 'EAP': wlan_cfg['encryption']}[wlan_cfg['auth']]))
                self.tn.write('%s\n' % wlan_cfg['ras_addr'])
                ix, mobj, rx = self.expect(['Select server to change', 'Select server to set'])
                if ix == -1: raise Exception('Can not set NAS-ID: %s' % wlan_cfg['ras_addr'])
                self.tn.write('1\n') # Set information for primary server
                ix, mobj, rx = self.expect(['Enter A New IP', 'Enter A IP'])
                if ix == -1: raise Exception('Can not setting/changing on primary server')
                self.tn.write('%s\n' % wlan_cfg['ras_addr'])
                ix, mobj, rx = self.expect(['Enter A New Port', 'Enter A Port'])
                if ix == -1: raise Exception('Can not set Ras IP address: %s' % wlan_cfg['ras_addr'])
                self.tn.write('%s\n' % wlan_cfg['ras_port'])
                ix, mobj, rx = self.expect(['Enter A New Secret', 'Enter A Secret'])
                if ix == -1: raise Exception('Can not set Ras port: %s' % wlan_cfg['ras_port'])
                self.tn.write('%s\n' % wlan_cfg['ras_secret'])
                ix, mobj, rx = self.expect(['Select server to change'])
                if ix == -1: raise Exception('Can not set Ras secret: %s' % wlan_cfg['ras_secret'])
                
                if wlan_cfg.has_key('rac_addr'):
                    #Setting radius accounting server information. It is optional.
                    self.tn.write('2\n')
                    ix, mobj, rx = self.expect(['Select server to change', 'Select server to set'])
                    if ix == -1: raise Exception('Can not set NAS-ID: %s' % wlan_cfg['rac_addr'])
                    self.tn.write('1\n') # Set information for primary server
                    ix, mobj, rx = self.expect(['Enter A New IP', 'Enter A IP'])
                    if ix == -1: raise Exception('Can not setting/changing on primary server')
                    self.tn.write('%s\n' % wlan_cfg['rac_addr'])
                    ix, mobj, rx = self.expect(['Enter A New Port', 'Enter A Port'])
                    if ix == -1: raise Exception('Can not set Rac IP address: %s' % wlan_cfg['rac_addr'])
                    self.tn.write('%s\n' % wlan_cfg['rac_port'])
                    ix, mobj, rx = self.expect(['Enter A New Secret', 'Enter A Secret'])
                    if ix == -1: raise Exception('Can not set Rac port: %s' % wlan_cfg['rac_port'])
                    self.tn.write('%s\n' % wlan_cfg['rac_secret'])
                    ix, mobj, rx = self.expect(['Select server to change'])
                    if ix == -1: raise Exception('Can not set Rac secret: %s' % wlan_cfg['rac_secret'])
                else:
                    self.tn.write('4\n')
                
                self.tn.write('4\n')

            ix, mobj, rx = self.expect(['WPA no error'])
            if ix == -1: raise Exception('Setting WAP encryption options is not successful')

        else:
            raise Exception('Authentication is not available')

        if self.expect_prompt(10) == -1:
            raise Exception('Setting encryption options on Ruckus AP not successful')

        # set wireless interface up
        logging.info("Enable wlan %s" % wlan_cfg['wlan_if'])
        logging.info(self.set_state(wlan_cfg['wlan_if'], 'up'))
        time.sleep(5) # waiting for wlan up
        self.get_encryption(wlan_cfg['wlan_if'])


    def change_fw_setting(self, conf):
        if conf.has_key('auto'):
            if conf['auto']: res = self.cmd('fw auto enable')[-1]
            else: res = self.cmd('fw auto disable')[-1]
        if conf.has_key('control'):
            res = self.cmd('fw set control %s' % conf['control'])
        if conf.has_key('host'):
            res = self.cmd('fw set host %s' % conf['host'])
        if conf.has_key('proto'):
            res = self.cmd('fw set proto %s' % conf['proto'])
            if conf['proto'].lower() == 'ftp':
                self.cmd('fw set user %s' % conf['user'])
                self.cmd('fw set password %s' % conf['password'])
        port = conf['port'] if conf.has_key('port') else 'auto'
        res = self.cmd('fw set port %s' % port)
        if conf.has_key('firstcheck'):
            res = self.cmd('fw set firstcheck %s' % conf['firstcheck'])
        if conf.has_key('interval'):
            res = self.cmd('fw set interval %s' % conf['interval'])
        if conf.has_key('psk'):
            res = self.cmd('fw set psk %s' % conf['psk'])

    # this function is used for FM and ZD. We will merge with upgrade_sw_ap later
    def upgrade_sw_fm(self, img_file_path="", timeout=180, is_img_file_extracted=False):
        """ upgrade AP firmware with the image specified by the img_file_path.
        - is_img_file_extracted: this param is to support a case the file alread extracted
        On AP, it will use upgrade method specified in testbed config
        1. Extract file and move to tftp/ftp folder
        2. Create control file for the image
        3. Save current firmware control setting of AP
        4. Update firmware control setting that provided by testbed config
        5. Perform upgrade firmware
        6. Restore original firmware control setting of AP
        7. Reboot AP

        Note: to avoid infinity loop, it will raise timeout exception.
        """
        ap_fw_setting = self.get_fw_upgrade_setting()

        # upload image file and control file to server
        build_files = img_file_path
        # if the image file already extracted, no need to do it again
        if not is_img_file_extracted:
            img_file_path = self.extract_image(img_file_path)

        ctr_file_path = self.create_ctrl_file_fm(img_file_path)
        # copy file from temp folder to root folder of FTP/TFPT
        shutil.copyfile(img_file_path,"%s%s%s" % (self.ftpsvr.get_root_path(), os.sep, os.path.basename(img_file_path)))
        shutil.copyfile(ctr_file_path,"%s%s%s" % (self.ftpsvr.get_root_path(), os.sep, os.path.basename(ctr_file_path)))
        # TODO  Hieu Phan: Using shutil.copyfile to copy image, ctrl files to ftp
        # root wil encounter problem if the ftp/tftp server is a remote server not
        # a test machine. We will consider this change later, still use original
        # way to copy image, ctrl files to ftp/tftp root dir.
        # Will change to use upload_file_to_ftp_server function to upload
        # image and control file to FTP server. The upload_file_to_ftp_server function
        # use ftplib  instead of copy command in command line to connecto to ftp/tftp
        # server to upload the files. With this way, we don't need to care about the rootpath
        # self.upload_file_to_ftp_server(img_file_path, server_path=self.ftpsvr.get_root_path(),
        #                            server_ip=self.ftpsvr.get_ip_addr(), user=self.ftpsvr.get_username(),
        #                            password=self.ftpsvr.get_password())
        # self.upload_file_to_ftp_server(ctr_file_path, server_path=self.ftpsvr.get_root_path(),
        #                            server_ip=self.ftpsvr.get_ip_addr(), user=self.ftpsvr.get_username(),
        #                            password=self.ftpsvr.get_password())

        # don't clean up if the file is not extracted by this function
        if not is_img_file_extracted:
            # clean-up build files under rat folder
            os.remove(build_files)
            os.remove(img_file_path)

        os.remove(ctr_file_path)

        # Get information about upgrade method and settings from testbed level
        self.change_fw_setting(os.path.basename(ctr_file_path), host=self.ftpsvr.get_ip_addr(),
                             proto=self.ftpsvr.get_protocol(), user=self.ftpsvr.get_username(),
                             password=self.ftpsvr.get_password())

        logging.info("Upgrading...")
        self.tn.write("fw update main\n")
        ix, mobj, rx = (-1, None, "")

        for z in try_interval(timeout, 0.1):
            if ix >= 0:
                # Upgrade done: restore firmware setting and reboot
                logging.info("Upgraded DONE.")
                self.change_fw_setting(**ap_fw_setting)
                self.reboot()
                return

            ix,mobj,rx = self.expect(["Completed","OK", "No update"])
            logging.info(rx)
            # Hieu Phan: add to manage "**fw(4054) : No update" case
            # TODO: Whether we treat a situation "No update" as failed case or not? Currently, No
            # We may see this problem if the upgrade fw is the same with current fw on AP
            if (("Completed" not in rx) or ('no update' not in rx.lower())) and ("OK" in rx):
                raise Exception(rx)
        raise Exception("Upgrade failed after %s seconds" % timeout)

    # this function is used for AP. We will merge with upgrade_sw_fm later
    def upgrade_sw_ap(self, build, timeout = 300):

        logging.info("Upgrading...")
        self.tn.write('\n')
        self.tn.read_very_eager()
        time.sleep(5)
        self.tn.write("fw update\n")

        # loop until AP write firmware success or timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print "Upgrade failed after %s seconds" % timeout
                raise Exception("Upgrade failed after %s seconds" % timeout)

            ix, mobj, rx = self.tn.expect(['\*\*fw\([0-9]+\) : [A-Za-z]+.*'], 5)
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
                time.sleep(5)
                logging.info("Upgrade DONE. Rebooting AP....")
                self.reboot()
                logging.info("Reboot AP DONE.")
            elif 'no update' in fw_txt.lower():
                logging.info("No Upgrade. AP is running an expected image")
                return
            else:
                logging.info('[ERROR telnet buffer]\n%s' % rx)
                raise Exception(fw_txt.split(':')[-1])

    # new version of upgrade_sw_ap() so we can see few lines of beginning and end
    # of the output message from the fw update command.
    def update_ap_fw(self, timeout=360,pause=10,prompt=''):
        if not prompt:
            prompt = self.prompt
        if not timeout:
            timeout = 180
        # empty input buffer
        self.tn.read_very_eager()
        self.tn.write("fw update\n")
        time.sleep(pause)
        odata = self.tn.read_very_eager()
        logging.debug('AP FW UPDATE output_begin:\n%s' % odata)
        print odata,
        timeout_at = time.time() + timeout
        cnt = 0
        while (not re.search(prompt, odata, re.I) and time.time() < timeout_at):
            data1 = self.tn.read_very_eager()
            #print data1,
            odata += data1
            cnt += 1
            if (cnt % 4000) == 0:
                if os.path.exists('_BUG_RUCKUSAP'):
                    import pdb
                    pdb.set_trace()
                print '>',
                time.sleep(pause)
        logging.debug('\nAP FW UPDATE output_end:\n%s' % odata[-80:])
        mobj = re.search(r'\*\*fw\((\d+)\)\s*:\s*(completed|no update)', odata[-80:], re.I)
        if mobj:
            res = mobj.group(2).lower()
            if 'completed' in res:
                time.sleep(5)
                logging.info("Upgrade DONE. Rebooting AP....")
                self.reboot()
                logging.info("Reboot AP DONE.")
            elif 'no update' in res:
                logging.info("No Upgrade. AP is running an expected image")
            else:
                logging.info(odata)
                raise Exception('AP fw update return unpexected result')
        else:
            logging.info(odata)
            raise Exception("AP fw update failed after %s seconds" % timeout)
        return odata

    def reboot(self, timeout=360, login=True, telnet=True, exit_on_pingable=False):
        """ Reboot the AP and wait until it boots up """
        logging.info("reboot AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
        self.do_cmd("reboot")

        self._wait_for_ap_reboot()

        if not login:
            return

        self._wait_for_ap_boot_up(timeout,exit_on_pingable)

    def _wait_for_ap_reboot(self, re_try=10):
        logging.info("verify AP [%s %s] rebooting(cannot pingable)" % (self.base_mac_addr, self.ip_addr))
        for i in range(re_try):
            if "Timeout" in ping(self.ip_addr):
                logging.info("AP is rebooting now")
                break
            else:
                if i == range(10)[-1]:
                    raise Exception("AP cannot reboot in more than 20 s")
                time.sleep(2)    

    def _wait_for_ap_boot_up(self, timeout=180, exit_on_pingable=False):
        logging.info("Wait until the AP [%s %s] boots up" % (self.base_mac_addr, self.ip_addr))
        time.sleep(5)
        is_ping_able = False
        for z in try_interval(timeout, 2):
            if not is_ping_able:
                if "Timeout" not in ping(self.ip_addr):
                    logging.info("Device is pingable. Wait until the SSH/telnet services are up and running.")
                    is_ping_able = True
                    if exit_on_pingable:
                        logging.info("AP is pingable, exiting reboot procedure.")
                        return
            else:
                try:
                    self.login(interval=timeout%5+5)
                    logging.info("Login to the AP [%s %s] successfully" \
                                 % (self.base_mac_addr, self.ip_addr))
                    return
                except:
                    pass
        if is_ping_able:
            raise Exception("Unable to connect to the ping-able AP [%s %s]" % \
                            (self.base_mac_addr, self.ip_addr))
        msg = "Unable to ping the AP [%s %s] after rebooting %s seconds" % \
            (self.base_mac_addr, self.ip_addr, timeout)
        raise Exception(msg)


    def set_ssid(self, wlan_if, ssid = 'RAT'):
        # Need to convert the wlan interface ID to name since older Ruckus
        # AP implementation doesn't support interface ID.
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set ssid %s %s" % (wlan_if_name, ssid))[-1]
        if res.lower() != "ok":
            self.cmd("set ssid %s %s" % (wlan_if, ssid))

    def get_ssid(self, wlan_if,force_ssh=False):
        res = self.cmd("get ssid %s" % wlan_if,force_ssh=force_ssh)
        if res[-1].lower() != "ok":
            wlan_if_name = self.wlan_if_to_name(wlan_if,force_ssh=force_ssh)
            res = self.cmd("get ssid %s" % wlan_if_name,force_ssh=force_ssh)

        #return res[0].split(' ')[-1]
        #Updated by cwang@20140327, because some ssid contain whitespace by itself, 
        #which will return an incomplete ssid name if split as ' '.
        return res[0].split('SSID: ')[-1]


    def get_wlan_list_by_ssid(self, ssid):
        wlan_info_list = self.get_wlan_info_dict()
        wlan_if_list = []
        for wlan_if in wlan_info_list.keys():
            if wlan_info_list[wlan_if].get('status') == 'up' and \
                self.get_ssid(wlan_if) == ssid:
                wlan_if_list.append(wlan_if)
                
        return wlan_if_list
                
    def get_dhcp_option82_by_wlan_if(self, wlan_if):
        res_dict = {'option82':None,
                    'subopt1':None,
                    'subopt2':None,
                    'subopt150':None,
                    'subopt151':None}
        dhcp_option82_info = self.cmd("get dhcp option82-insertion %s" % wlan_if)
        for item in dhcp_option82_info:
            if 'Option 82 insertion:' in item:
                res_dict['option82'] = item.split(':')[-1].strip()
            elif 'Subopt1:' in item:
                res_dict['subopt1'] = item.split(':')[-1].strip()
            elif 'Subopt2:' in item:
                res_dict['subopt2'] = item.split(':')[-1].strip()
            elif 'Subopt150:' in item:
                res_dict['subopt150'] = item.split(':')[-1].strip()
            elif 'Subopt151:' in item:
                res_dict['subopt151'] = item.split(':')[-1].strip()
        
        return res_dict

    def set_state(self, wlan_if, state):
        """
        Note: for AP build 5.0 or above, wlan_if value in wlan_if could be wlan0 to wlan9.
        for 4.x standalone build, it will convert wlan0->svcp,wlan1->home, wlan2->rcks,wlan3->mdfx..
        """
        if self.mgmt_vlan:
            mgmt_vlan = self.get_ip_cfg("wan")['vlan']
            logging.info("AP Mgmt_Vlan before set_state(%s,%s): %s" % (wlan_if, state, mgmt_vlan))

        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set state %s %s" % (wlan_if_name, state))[-1]
        if res.lower() != 'ok':
            res = self.cmd("set state %s %s" % (wlan_if, state))

        return res


    def get_state(self, wlan_if):
        res = self.cmd("get state %s" % wlan_if)
        if res[-1].lower() != 'ok':
            wlan_if_name = self.wlan_if_to_name(wlan_if)
            res = self.cmd("get state %s" % wlan_if_name)
        return res[0].split(':')[-1].strip()

    def set_channel(self, wlan_if, channel):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set channel %s %s" % (wlan_if_name, channel))[-1]
        if res.lower() != 'ok':
            self.cmd("set channel %s %s" % (wlan_if, channel))

    def get_channel(self, wlan_if, use_wlan_id = True):
        if use_wlan_id:
            # Convert wlan ID to wlan name
            wlan_if_name = self.wlan_if_to_name(wlan_if)
        else:
            # No need to convert
            wlan_if_name = wlan_if
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

    def set_country_code(self, country_code):
        return self.cmd("set countrycode %s" % country_code)

    def get_country_code(self):
        return self.cmd("get countrycode")[0].split(' ')[-1]

    def get_board_data_item(self, line_info, return_line = 0):
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

    def get_eth0_mac(self):
        data = self.get_board_data_item("eth0")
        data = data.lower()
        return "".join(data.split(':'))

    def get_wireless_mac(self):
        data = self.get_board_data_item("wlan0")
        data = data.lower()
        return "".join(data.split(':'))

    def get_device_hw_type(self):
        return self.get_board_data_item("V54 Board Type:")

    def get_profile(self):
        return self.get_board_data_item("Customer ID:")

    def get_antenna_info(self):
        data = self.get_board_data_item("Antenna Info:", 1)
        if data.find("yes") != -1:
            return data.split(' ')[-1]
        else:
            return "0x00000000"

    #@author: yuyanan @since: 2014-8-26 ZF-8381 Optimize: Prompt # not found
    def goto_shell(self,force_ssh=False):
        """ Enter into the shell
        """
        try: 
            if self.sesame_key:
                self.tn.write(self.sesame_key+'\n')
            else:
                self.tn.write("!v54!\n")
                time.sleep(.5) 
                self.tn.write("\n")
            time.sleep(3)
            self.expect_prompt(prompt = '#',timeout=10)
        except (EOFError, Exception, socket.error):
            logging.info("Telnet session had been disconnected. Try to relogin to the AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
            if force_ssh:
                logging.info("Telnet session had been disconnected. Try to relogin to the AP [%s %s]" % (self.base_mac_addr, self.ip_addr))
                t = paramiko.Transport((self.ip_addr,22))  
                t.connect(username="",password="")
                chan = t.open_session()
                chan.get_pty()
                chan.invoke_shell()
                self._wait_for(chan, 'login')
                chan.send('super' + "\n")
                self._wait_for(chan, 'password')
                chan.send('sp-admin' + "\n")
                self._wait_for(chan, 'rkscli:')
                chan.send("!v54!" + "\n")
                time.sleep(.5) 
                chan.send("\n")
                self._wait_for(chan, '#')
            else:
                try:
                    self.login()
                except:
                    self.enable_telnet_via_ssh()
                    self.login()
                self.tn.write( "!v54!" + "\n")
                time.sleep(.5) 
                self.tn.write("\n")
                self.expect_prompt(prompt = '#',timeout=10)
            
            
    #@author: yuyanan @since: 2014-8-25 zf-8381 optimize: add new fun for ap shell
    def get_sesame_key(self):
        sn = self.get_board_data_item(line_info = "Serial")
        in_data = dict(f = "shell_key",
                       serial = sn,
                       vendor = "ruckus",
                       )
        url = URL_SESAME
        
        if in_data:
            data = urllib.urlencode(in_data)
            url = url+ '?' + data
            
            req = urllib2.Request(url)
        try:
            response=urllib2.urlopen(req)
            result = response.read()
        except urllib2.URLError, e:                       
            logging.info('get json data to url[%s] failed, due to error[%s]' % (url, e))
            return
            
        return result
    
    def exit_shell(self,force_ssh=False):
        """ Exit the shell and log back into CLI
        """
        try:
            self.cmd('exit', 0, 'Please login',force_ssh=force_ssh)
            self.tn.write('\n')
        except Exception:
            pass
        if not force_ssh:
            self.login()

    def get_tx_power(self, wlan_if, use_wlan_id = True):
        """ Get the txpower of the given wlan interface in rkscli mode """
        if use_wlan_id:
            # Convert wlan ID to wlan name
            wlan_if_name = self.wlan_if_to_name(wlan_if)
        else:
            # No need to convert
            wlan_if_name = wlan_if

        txpower_info = self.cmd("get txpower %s" % wlan_if_name)[0]
        r = re.search("(-\d+) dB from max power", txpower_info)
        if r:
            txpower = r.group(1) + "dB"

        else:
            txpower = txpower_info.split()[-1]

        return txpower

    def sh_get_wlan_tx_power(self, wlan = -1):
        if wlan == -1:
            power = list()
            wlanNum = 0
        else:
            power = -1
            wlanNum = wlan
        self.goto_shell()
        buf = self.cmd("iwconfig", prompt = "#")
        self.exit_shell()
        for lineNum in range(len(buf)):
            if buf[lineNum].find("wlan%d" % wlanNum) != -1:
                lineNum = lineNum + 2
                if len(buf) > lineNum:
                    index = buf[lineNum].find("Tx-Power:")
                    endIndex = buf[lineNum].find("dBm")
                    if index != -1 and endIndex != -1:
                        if wlan == -1:
                            tmp = buf[lineNum][(index + 9):(endIndex - 1)]
                            if tmp.isdigit():
                                power.append(int(tmp))
                                wlanNum += 1
                        else:
                            power = int(buf[lineNum][(index + 9):(endIndex - 1)])
                            break
        return power


    def set_timeout(self, timeout = 3600):
        self.cmd("set timeout %d" % timeout)
        time.sleep(1)

    def get_timeout(self):
        res = self.cmd('get timeout')
        pat = '([0-9]+)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def get_ap_model(self):
        """
        Detect model of standalone AP
        """
        ap_name = self.cmd("get boarddata")[0].split(' ')[-1]

        try:
            self.ap_type = re.search('[0-9]+', ap_name).group()
        except:
            raise Exception("Can not get AP [%s %s] type number" % (self.base_mac_addr, self.ip_addr))
        return self.ap_type

    def get_station_count(self, wlan_if='wlan0'):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        rcode = self.cmd("get station %s list" % wlan_if_name)
        if rcode[-1].lower() != 'ok':
            rcode = self.cmd("get station %s list" % wlan_if)
        count = 0
        line = 1
        while line < len(rcode):
            lineStr = rcode[line]
            aid = get_indexed_item(lineStr, 1)
            if aid.isdigit() and int(aid) >= 1:
                count = count + 1
            line = line + 1
        return count

    def get_current_status(self):
        if self.get_station_count() == 1:
            return "connected"
        return "disconnected"

    def get_encryption(self, wlan_if, use_id = True):
        """
        Get encryption configuration of AP
        @return a dictionary of encryption configuration
        """
        if use_id:
            wlan_if_name = self.wlan_if_to_name(wlan_if)
        else:
            wlan_if_name = wlan_if

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
            if temp[0].lower().startswith('ssid'):
                info['ssid'] = temp[1]
            if 'security' in temp[0].lower():
                security = temp[1]
                info['BeaconType'] = temp[1]
            
            if 'authentication' in temp[0].lower():
                if temp[1].find('-')>-1:
                    auth = temp[1].split('-')[0]
                else:
                    auth = temp[1]
            
            if 'cipher' in temp[0].lower():
                encryption = temp[1].split('-')[0]
                info['WPAEncryptionModes'] = temp[1].split('-')[0] + "Encryption"
            if 'passphrase' in temp[0].lower(): key_string = temp[1]
            if 'protocol' in temp[0].lower(): info['wpa_ver'] = temp[1].split('-')[0]
            if 'Key' in temp[0]:
                info['key_index'] = temp[0].split()[1]
                key_string = temp[1].split()[-1].strip('"')
            if 'encryption' in temp[0].lower(): encryption = temp[1]
            
            #[Cherry,20110724]: Add parsing radius auth and accounting information.
            if temp[0].startswith('Auth(P) IP'):
                info['ras_addr'] = temp[1]
            if temp[0].startswith('Auth(P) Port'):
                info['ras_port'] = temp[1]
            if temp[0].startswith('Auth(P) Secret'):
                info['ras_secret'] = temp[1]
            if temp[0].startswith('Acct(P) IP'):
                info['rac_addr'] = temp[1]
            if temp[0].startswith('Acct(P) Port'):
                info['rac_port'] = temp[1]
            if temp[0].startswith('Acct(P) Secret'):
                info['rac_secret'] = temp[1]
                
        if auth.lower().find('eap')> -1: 
            info['auth'] = 'EAP'
        elif security == "WPA" and auth == "Open":
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

        if key_string:
            # Many places invoke get_encryption to get security cfg then use
            # that result as param to invoke RuckusAP.cfg_wlan() to set
            # wlan set. But in cfg_wlan uses "key_string" not "WPA PassPhrase"
            # to set the security so add a new key "key_string"
            info['WPA PassPhrase'] = key_string
            info['key_string'] = key_string

        return info


    def get_shaper(self, ssid, debug = False):
        """ Return the ratelimiting information of a give wlan_if
        @param ssie: ssid of the WLAN
        @param debug: True:
                       False:

        @return: a dictionary of ratelimitng information"""
        if debug:
            import pdb
            pdb.set_trace()
        wlan_if = ""
        try:
            if not wlan_if:
                wlan_if = self.ssid_to_wlan_if(ssid)
        except Exception, e:
            msg = "Exception on ssid_to_wlan_if(%s): %s" % (ssid, e.message)
            logging.info(msg)
            raise Exception(msg)
        shaper = {'down':None , 'up':None}
        #downstream ratelimiting
        #EGRESS    to WLAN: (   100 kbps shared per station)
        dn_ptn = r"EGRESS\s+to\s+WLAN:\s+\(\s+(\d+)\s+(.bps)\s+shared\s+per\s+station\)"
        #upstream ratelimiting
        #INGRESS from WLAN: (   100 kbps shared per station)
        up_ptn = r"INGRESS\s+from\s+WLAN:\s+\(\s+(\d+)\s+(.bps)\s+shared\s+per\s+station\)"
        for line in self.cmd("get shaper %s" % wlan_if):
            m1 = re.match(dn_ptn, line, re.I)
            m2 = re.match(up_ptn, line, re.I)
            if m1:
                shaper['down'] = m1.group(1) + m1.group(2)
            if m2:
                shaper['up'] = m2.group(1) + m2.group(2)

        return shaper


    def set_shaper(self, wlan_if, preset_name="", uplink_preset_name = "", disable=False):
        """
        Default preset:
             Preset Name : Preset Summary Description
             ----------- - --------------------------
                 100kbps : 100 kbps link per station
                 250kbps : 250 kbps link per station
                 500kbps : 500 kbps link per station
                   1mbps :   1 mbps link per station
                   2mbps :   2 mbps link per station
                   5mbps :   5 mbps link per station
                  10mbps :  10 mbps link per station
                  20mbps :  20 mbps link per station
                  50mbps :  50 mbps link per station
        """
        if disable:
            res = self.cmd("set shaper %s disable" % wlan_if)
            if res[-1].lower() == 'ok': return True
            else: return False
        else:
            res = self.cmd("set shaper %s %s %s" % (wlan_if, preset_name, uplink_preset_name))
            if res[-1].lower() == 'ok': return True
            else: return False


    def get_encryption_ex(self, timeout = 30, debug = False):
        """
        Return a list of dictionary of encryption information of all non-mesh WLANs configured on the AP, including:
            'wlan_name'     : the name of wlan on AP
            'ssid'          : the SSID
            'bssid'         : the BSSID
            'channel'       : the channel
            'auth'          : the authentication type
            'encrypt'       : the encryption type
            'key'           : the key string/passpharse code, may be NULL
            'security_mode' : the security mode, may be NULL

        Ex: The wlan infomation on the AP:
                  wlan0:    Anthony-Shared-WEP-128    00:1F:41:96:3F:1A
                  Channel 6
                  Auth:     Open
                  Encrypt:  WEP
                  Key= 16CB-6D05-DAA0-21CD-3D3F-D071-90   Security mode:restricted

            Return result:
             [{'security_mode': 'restricted', 'name': 'wlan6', 'bssid': '00:1F:41:96:3F:1A', 'encryption': 'WEP',
             'auth': 'Open', 'key': '16CB-6D05-DAA0-21CD-3D3F-D071-90', 'channel': '6', 'ssid': 'Anthony-Shared-WEP-128'}]
        """
        if debug: bugme.pdb.set_trace()
        self.goto_shell()
        self.tn.write('apmgrinfo -w\n')
        ix, mobj, rx = self.expect(['#'], timeout)
        encrypt_info = rx.replace('apmgrinfo -w', '')
        encrypt_info = encrypt_info.split('\r\n\r\n')
        encrypt_info_list = []
        # For each group of wlan information getting from AP, get the appropriate value of encryption type,
        # authentication type, key string, security mode and channel
        for wlan_00 in encrypt_info:
            wlan_name = ''
            ssid = ''
            bssid = ''
            channel = ''
            auth = ''
            encrypt = ''
            key = ''
            security_mode = ''
            wlan = wlan_00.split('\r\n')
            for info in wlan:
                if not wlan_name:
                    mgmt_vlan = re.search('(wlan[0-9]+):', info)
                    if not mgmt_vlan:
                        continue
                    wlan_name = mgmt_vlan.group(1)
                    if re.search('wlan[0-9]+:', info):
                        #JLIN@20090810 modified for AP CLI changed in reading
                        #restr = '(wlan[0-9]+): +([a-z0-9A-Z _-]+) +([a-f0-9A-F:]{17})'
                        restr = r'(wlan[0-9]+):\s+([\w_-]+)\s+([a-f0-9A-F:]+|Not-Associated)'
                        name_info = re.match(restr, info.strip())
                        if not name_info:
                            logging.debug ('[WLAN BAD.FORMAT] %s' % wlan_00)
                            continue
                        wlan_name = name_info.group(1)
                        ssid = name_info.group(2).strip()
                        bssid = name_info.group(3)
                    continue
                elif 'Channel' in info:
                    channel = info.split('Channel')[1].strip()
                elif 'Auth' in info:
                    auth = info.split('Auth: ')[1].strip()
                elif 'Encrypt' in info:
                    #JLIN@20090810 modified for AP CLI changed in reading
                    #encrypt = info.split('Encrypt: ')[1].strip()
                    m = re.search(r"encrypt\s*(|[^:]+):\s+(\w+)", info, re.I)
                    if m:
                        encrypt = m.group(2)
                elif 'Key' in info:
                    key = info.split('Key= ')[1].strip()

                if 'Encrypt' in auth:
                    encrypt = auth.split('Encrypt: ')[1].strip()
                    auth = auth.split('Encrypt: ')[0].strip()

                if 'Security mode' in key:
                    security_mode = key.split('Security mode:')[1].strip()
                    key = key.split('Security mode:')[0].strip()

            if wlan_name:
                info_dict = {'name': wlan_name, 'ssid':ssid, 'bssid':bssid,
                             'channel':channel, 'auth':auth,
                             'encryption':encrypt, 'key':key,
                             'security_mode':security_mode}
                encrypt_info_list.append(info_dict)
                if not (wlan_name and ssid and bssid and channel and auth and encrypt):
                    logging.warning('[WLAN BAD.FORMAT] DATA: %s\nDICT: %s' % (wlan_00, str(info_dict)))

        self.exit_shell()
        return encrypt_info_list

    def get_director_info(self):
        """
        Get the status of the AP when it communicates with the ZD.
        The status can be "DISCOVERY", "RUN", "JOIN"
        """
        # return self.cmd("get director-info")[1].split(' ')[-1]
        data = self.cmd("get director-info", return_list = False)
        
        m = re.search(r'Currently AP is in state: (\w+)', data, re.M)
        if m:
            return m.group(1)

        m = re.search(r'AP is in (.+) mode', data, re.I)
        if m:
            return m.group(1)
        else:
            return ''

    def get_director_cfg(self):
        """
        Return current configuration of director in a dictionary that includes the keys:
        - pri_zd_ip: primary Zone Director IP address
        - sec_zd_ip: secondary Zone Director IP address
        - zdcode: zdcode in DHCP43
        """
        data = self.cmd("get director-info", return_list = False)
        pri_zd_ip = sec_zd_ip = zdcode = ""
        m = re.search(r'Primary zone director ip : ([0-9.]+)', data, re.M)
        if m:
            pri_zd_ip = m.group(1)
        m = re.search(r'Secondary zone director ip : ([0-9.]+)', data, re.M)
        if m:
            sec_zd_ip = m.group(1)
        m = re.search(r'zdcode in dhcp43 : ([0-9]+)', data, re.M)
        if m:
            pri_zd_ip = m.group(1)
        return {"pri_zd_ip":pri_zd_ip, "sec_zd_ip":sec_zd_ip, "zdcode":zdcode}
    
    #@author: Liang Aihua,@since: 2015-3-10,@change: Add function to get management director info
    #********************* 
    def get_mgmt_director_ip(self):
        
        data = self.cmd("get director-info", return_list = False)
        
        m = re.search(r'AP is under management of ZoneDirector: (\S+)', data, re.M)
        if m:
            return m.group(1)
        else:
            return ''
    #****************************

    def extract_image(self, img_file_path):
        """ Extract correct image file download from K2

        i.e: image file pattern: 2942_4.2.0.0.171_Main.Bl7.
        The function will put file into the same directory with zip file.
        """
        img_file_pattern = "%s[0-9\._a-zA-Z]+.Bl7" % self.get_ap_model()

        path_name_list = os.path.split(img_file_path)
        try:
            tar_file = tarfile.TarFile.open(img_file_path, 'r:gz')
            file_list = tar_file.getnames()

            for i in range(len(file_list)):
                if re.search(img_file_pattern, file_list[i]):
                    break

            tar_file.extract(file_list[i], path_name_list[0])
            img_file_path = os.path.join(path_name_list[0], file_list[i])

        except:
            raise Exception("Can not open the tar file")

        return img_file_path

    def create_ctrl_file(self, main_file_path, backup_file_path = '', server_ip_addr = '0.0.0.0'):
        """
        Create the control file (.rcks) at the same directory of the main image file.
        In put:
        - main_file_path: the full path of the main image file.
        - backup_file_path: the full path of the backup image file which could be missing.
        - server_ip_addr: the FTP/TFTP server IP address, default if the server is also the local
                         the IP address could be 0.0.0.0
        """

        try:
            f = open(main_file_path + '.rcks', 'w')
            f.write('[rcks_fw.main]\n')
            f.write(server_ip_addr + '\n')
            f.write(os.path.basename(main_file_path) + '\n')
            f.write(str(os.path.getsize(main_file_path)) + '\n\n')
            if backup_file_path:
                f.write('[rcks_fw.bkup]\n')
                f.write(server_ip_addr + '\n')
                f.write(os.path.basename(backup_file_path) + '\n')
                f.write(str(os.path.getsize(backup_file_path)) + '\n\n')
            f.close()
        except:
            try:
                f.close()
                os.remove(f.name)
            finally:
                raise Exception('Can not create the control file for %s ...' % os.path.basename(main_file_path))
        return "%s.rcks" % main_file_path


    def create_ctrl_file_ap(self, rootpath, buildname, serv_ip = '0.0.0.0'):

        buildname = '%s/%s' % (rootpath, buildname)
        if not os.path.isfile(buildname):
            raise Exception("Build %s is not found in FTP server" % buildname)

        model = self.get_device_type().lower()
        cntrl_file = '%s/%s' % (rootpath, model)
        try:
            f = open(cntrl_file, 'w')
            f.write('[rcks_fw.main]\n')
            f.write(serv_ip + '\n')
            f.write(buildname + '\n')
            f.write(str(os.path.getsize('%s' % buildname)) + '\n\n')

            f.write('[rcks_fw.bkup]\n')
            f.write(serv_ip + '\n')
            f.write(buildname + '\n')
            f.write(str(os.path.getsize('%s' % buildname)) + '\n\n')
            f.close()
        except:
            try:
                f.close()
            finally:
                raise Exception('Can not create the control file for %s ...' % buildname)

        return cntrl_file


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
            setting_info = {'auto_upgrade':'','control':'', 'host':'', 'port':'', 'user':'', 'password':'', 'proto':''}
            if self.get_version().startswith("4.1"):
                for line in setting:
                    if re.search('Auto', line):setting_info['auto_upgrade'] = line.split(',')[0].split(" ")[-1].strip()
                    if re.search('FW (.)*[Cc]+ontrol [Ff]+ile', line): setting_info['control'] = line.split('=')[1].strip()
                    if re.search('(.)* Server', line): setting_info['host'] = line.split('=')[1].strip()
                    if re.search('Protocol (.)*User', line):
                        setting_info['proto'] = re.search('Protocol (.)*User', line).group().split('=')[1].strip()
                        setting_info['proto'] = setting_info['proto'].split()[0]
                    if re.search('User (.)*Passwd', line):
                        setting_info['user'] = re.search('User (.)*Passwd', line).group().split('=')[1].split()[0]
                        setting_info['user'] = setting_info['user'].replace("\"","")
                    if re.search('Passwd (.)*\"', line):
                        setting_info['password'] = re.search('Passwd (.)*\"', line).group().split('=')[-1].strip().split('\"')[1]
            else:
                for line in setting:
                    if re.search('Auto', line):setting_info['auto_upgrade'] = line.split('=')[1].strip()
                    if re.search('FW (.)* Control File', line): setting_info['control'] = line.split('=')[1].strip()
                    if re.search('(.)* Server', line): setting_info['host'] = line.split('=')[1].strip()
                    if re.search('Port', line): setting_info['port'] = line.split('=')[1].strip()
                    if re.search('Protocol', line): setting_info['proto'] = line.split('=')[1].strip()
                    if re.search('^User', line): setting_info['user'] = line.split('=')[1].strip().split('\"')[1]
                    if re.search('^Password', line): setting_info['password'] = line.split('=')[1].strip().split('\"')[1]
                    if re.search('^Running on image', line): setting_info['running_image'] = line.split('=')[-1]
                    if re.search('FW Decryption', line): setting_info['psk'] = line.split('=')[1].split('\'')[1]
                    
                    if re.search('FW First Check', line): setting_info['firstcheck'] = line.split('=')[1]
                    if re.search('FW Periodic Check', line): setting_info['interval'] = line.split('=')[1]
                    if re.search('FW Badfile Retry', line): setting_info['badfile_retry'] = line.split('=')[1]
                    if re.search("FW auto-update's max wait time for reboot", line): setting_info['reboot_maxwait'] = line.split('=')[1]
                    if re.search("FW auto-update's scheduled reboot time", line): setting_info['reboot'] = line.split('=')
        except:
            raise Exception('Can not get firmware upgrade setting')
        return setting_info


    def upload_file_to_ftp_server(self, local_path, server_path = "", server_ip = "localhost", user = "anonymous", password = "blank"):
        """
        use to upload AP image and control file to (TFTP/FTP) server using FTP protocol with default port
        - local_path     : path + file name are uploaded
        - server_path    : path on FTP server where file is uploaded. By Default, it uses root folder
        - server_ip      : FTP server IP address
        - user          : user name to access FTP server
        - password      : password to access FTP server
        """

        try:
            ftpsrv = ftplib.FTP(server_ip, user, password)
            # open local file to analyze file type, size
            fp = open(local_path, "rb")
            sfsize = os.path.getsize(local_path)
            temp = fp.read(2048)
            fp.seek(0, 0)

            # check file type
            remote_file = '%s%s' % (server_path, os.path.basename(local_path))
            if temp.find('\0') != -1:
                ftpsrv.storbinary("STOR %s" % remote_file, fp)
            else:
                ftpsrv.storlines("STOR %s" % remote_file, fp)

            fp.close()
            ftpsrv.quit()
        except:
            raise Exception("Connect to server %s with user name = %s, password = %s upload file %s" % \
                            (server_ip, user, password, local_path))

    def verify_wlan(self, wlan_if=None):
        """
        Verify_wlan is used to verify that Wlan configuration set by Zone Director
        @param wlan_if, check interface other than all, i.e. wlan_if = 'wlan0'
        Updated by cwang@20120618.
        """
        wlan_info = self.get_wlan_info_dict()

        # check SIMAP WLANs, SIMAP sometime doesn't contain any WLANs inculding meshu, meshd
        if not wlan_info:
            return False

        count = 0
        count_up = 0        
        for (wlan_id, wlan) in wlan_info.iteritems():
            # don't check internal wlans
            if wlan['name'] in INTERNAL_WLAN['name'] or \
            wlan['type'] in INTERNAL_WLAN['type']:
                count += 1
                continue

            # verify wlan status up and bssid is not 00:00:00:00:00:00
#            status = self.get_state(wlan['wlanID']).lower()
            status = wlan['status'].lower()
            if wlan_if:
                if wlan_if == wlan['wlanID']:
                    if status.startswith("up"):
                        return True
                    else:
                        return False
                else:
                    count += 1
                                    
            else:#Check all interface.            
                if status.startswith("down") or \
                    wlan['bssid'] == "00:00:00:00:00:00":
                    return False
                else:
                    #@author: Jane.Guo @since: 2013-09 add one counter to check the external wlan
                    count_up += 1
            

        if count == len(wlan_info):
            logging.debug('No WLAN except internal WLANs are found: %s' % wlan_info)
            return False
        
        if count + count_up == len(wlan_info):
            return True
        else:
            logging.debug('Wlan check fail: %s' % wlan_info)
            return False            
        

    def verify_all_wlans_are_up(self):
        '''
        '''
        return self.verify_wlan()


    def get_station_list(self, wlan_if):
        """ get all station associated to AP via wlan_if """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        return [x.split() for x in self.cmd("get station %s list" % wlan_if_name) if re.search('([0-9a-fA-F:]{17})', x)]


    def ssid_to_wlan_if(self, ssid):
        for (wlan_id, wlan) in self.get_wlan_info_dict().iteritems():
            if wlan['name'] in INTERNAL_WLAN['name'] or \
            wlan['type'] in INTERNAL_WLAN['type']:
                continue
            
            #Behavior change start from 9.5
            if wlan['bssid'] == '00:00:00:00:00:00':
                continue

            _ssid = self.get_ssid(wlan_id)

            logging.debug("ssid of %s is %s" % (wlan_id, _ssid))
            if _ssid == ssid:
                return wlan['wlanID']


    def get_fixed_country_code(self):
        """
        Return the status of Fixed Country code on the AP
        """
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search('Fixed Ctry Code:', x)][0]

    def change_board_data(self, key, parameter):
        """
        To change the board data info on the AP
        """
        try:
            self.goto_shell()
            self.tn.write('rbd change\n')
            ixx, mobj, rx = self.tn.expect([key], 0.4)
            while ixx != 0:
                self.tn.write('\n')
                ixx, mobj, rx = self.tn.expect([key], 0.4)
            self.tn.write('%s\n' % parameter)
            ixx, mobj, rx = self.tn.expect(['Save Board Data'], 0.4)
            while ixx != 0:
                self.tn.write('\n')
                ixx, mobj, rx = self.tn.expect(['Save Board Data'], 0.4)
            self.tn.write('y\n')
            self.exit_shell()
        except:
            raise Exception('Error during changing %s on Board Data' % key)

    def set_fixed_country_code(self, is_fixed = True):
        """
        Enable or disable the option 'Set country code' on the AP
        Input:
        - is_fixed: If it is True, disable option 'Set country code' on the AP.
        Otherwise, enable that option.
        """
        if is_fixed:
            parameter = "y"
        else:
            parameter = "n"
        self.change_board_data('Fixed Ctry Code', parameter)


    def get_serial(self):
        """
        This function is to get serial number
        """
        return self.get_board_data_item('Serial')

    def set_serial(self, serial):
        """
        This function is to change serial number.
        """
        self.change_board_data('Serial Number', serial)

    def set_bssid(self,wlan_if,bssid):
        """
        This function is to change serial number.
        """
        get_id_arr=self.get_bssid(wlan_if).split(':')
        set_id_arr=bssid.split(':')
        if get_id_arr[0]!=set_id_arr[0] or get_id_arr[1]!=set_id_arr[1] or get_id_arr[2]!=set_id_arr[2]:
            logging.info('can not set bssid like %s'%bssid)
            return False
        unique_portion=set_id_arr[3]+':'+set_id_arr[4]+':'+set_id_arr[5]
        self.change_board_data('%s mac unique portion'%wlan_if, unique_portion)
        self.reboot()
        return True

    def get_ntp_info(self):
        """
        """
        return self.cmd('get ntp')

    def get_time(self):
        """
        """
        time = self.get_ntp_info()[0].split(' : ')[1]
        return time

    def update_ntp_server(self):
        """
        """
        return self.cmd('set ntp update')

    def set_ntp_server(self, server_ip_addr):
        """
        """
        return self.cmd('set ntp server %s' % server_ip_addr)

    def cfg_syslog(self, parameter, value = ''):
        """
        """
        if parameter == 'enable' or parameter == 'disable':
            self.tn.write('set syslog %s\n' % parameter)
            self.tn.write('\n')
            self.tn.expect([self.prompt])
        else:
            self.cmd('set syslog %s %s' % (parameter, value))
        self.cmd('')

    def get_syslog(self, parameter):
        """
        """
        return self.cmd('get syslog %s' % parameter)

    def set_ip_cfg(self, ip_cfg):
        """
        Input: ip_cfg is a dictionary containing interface (lan/wan),
        gw (gateway), IP address, mask, and ip_addr.
        If the gw or mask are not given, they are generated assuming a
        class C network.
        """
        if not ip_cfg['gw']:
            # assuming class C address
            gw = ip_cfg['ip_addr'].split('.')
            gw[3] = '254'
            ip_cfg['gw'] = str.join('.', gw)
        if not ip_cfg['mask']:
            ip_cfg['mask'] = "255.255.255.0"
        return self.cmd("set ipaddr %s %s %s %s" %
                       (ip_cfg['interface'], ip_cfg['ip_addr'],
                        ip_cfg['mask'], ip_cfg['gw']))


    def get_ip_cfg(self, interface):
        """
        return ip_addr, subnet mask, gateway of interface
        """
        ipcfg = {'ip_addr': '', 'net_mask': '', 'gw':'', 'vlan':''}
        rx = self.cmd("get ipaddr %s" % interface)
        ipcfg['ip_addr'] = re.search("IP: [0-9. ]+Netmask", rx[0]).group().split()[1]
        ipcfg['net_mask'] = re.search("Netmask [0-9. ]+",rx[0]).group().split()[1]
        ipcfg['gw'] = rx[0].split()[-1]
        ipcfg['vlan'] = re.search("vlan [0-9]+", rx[0]).group().split()[-1]
        return ipcfg


    def get_ip_info(self, interface):
        """
        Returns a dictionary containing connection type, ip_addr, mask, and gateway.
        IP Address Configuration Type: static, IP: 192.168.0.200  Netmask 255.255.255.0  Gateway 192.168.0.252
        """
        ip_re = '([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        type_re = '(\w+)'
        info_re = 'Type: %s, IP: %s  Netmask %s  Gateway %s' % (type_re, ip_re, ip_re, ip_re)
        ip_info = {}
        buf = self.cmd("get ipaddr %s" % interface)

        if re.match(info_re, buf[0]):
            info = re.findall(info_re, buf[0])
            ip_info['type'], ip_info['ip_addr'], ip_info['net_mask'], ip_info['gateway'] = info[0]
        else:
            type_re = '\((.*)\)'
            info_re = r'^.*IP Address: %s, IP: %s  Netmask %s  Gateway %s' % (type_re, ip_re, ip_re, ip_re)
            info = re.findall(info_re, buf[0])
            ip_info['type'], ip_info['ip_addr'], ip_info['net_mask'], ip_info['gateway'] = info[0]
        
        return ip_info

    def get_ip_mode(self, interface):
        """
        return ip_mode of interface
        """
        rx = self.cmd("get ipmode %s" % interface)
        ipmode = re.search("IP Mode: (\w+)",rx[0]).group(1)

        return ipmode

    def get_media_queue_stats(self, wlan_if):
        stats = dict()
        mqstats = self.cmd("get mqstats %s all" % self.wlan_if_to_name(wlan_if))
        line = 0
        #logging.debug("GetMediaQueueStats: mqstats=%s" % mqstats)
        while (line < len(mqstats) and mqstats[line].find("STA:") == -1):
            line += 1
        if line >= len(mqstats):
            return stats
        if mqstats[-1] == "OK":
            mqstats.pop()
        try:
            # get the statistic labels
            labels = rlstrip_list(mqstats[line + 2].split(' '))
            remove_blanks_from_list(labels)
            while line < len(mqstats):
                # get the station MAC
                mac = rlstrip_list(mqstats[line].split(' '))
                remove_blanks_from_list(mac)
                mac = mac[1]
                line += 3
                # get the rx statistics
                while line < len(mqstats) and mqstats[line].find("----------------") == -1:
                    # get the queue label
                    queue = mqstats[line].split(':')[0]
                    queue = queue.lstrip()
                    # get the queue stats
                    lineList = rlstrip_list(mqstats[line].split(':')[1].split(' '))
                    remove_blanks_from_list(lineList)
#                    stats[mac+"_"+queue] = dict()
                    for col in range(len(lineList)):
                        # Fixes a bug caused by a bug in the AP where there were
                        # more data entries than labels
                        if col < len(labels):
                            queue = queue.split("(")[0]
                            stats[mac + "_" + queue + '_' + labels[col]] = lineList[col]
                    line += 1
                line += 1
        except:
            #self.log.LogInfo("get_media_queue_stats: Problem with parsing the data", "ERROR")
            #self.log.LogInfo(traceback.format_exc(), "ERROR")
            #self.log.LogInfo("mqstats=%s, line=%s" % (mqstats, line))
            stats = dict()
        return stats


    def set_known_multicast(self, wlan_if, enable = True):
        """
        Enable/Disable well-known multicast on wlan interface
        """
        return self.cmd("set qos %s known_multicast %s" % (self.wlan_if_to_name(wlan_if),
                                                           {True:"enable", False:"disabled"}[enable]))

    def set_directed_threshold(self, wlan_if, value):
        res = self.cmd('set DirectedThreshold %s %s' % (wlan_if, value))[-1]
        if res.lower() == 'ok':
            return True
        else:
            res = self.cmd('set directed-thr %s %s' % (wlan_if, value))[-1]
            if res.lower() == 'ok': return True
            else: return False


    def get_gblqos(self):
        """
        Get the content of the file /cat/media/gblQOS file
        @return content of /cat/media/gblQOS file
        """

        self.goto_shell()
        buf = self.cmd('cat /proc/media/gblQOS', 0, '#')
        self.exit_shell()
        return buf


    def get_igmp_table(self):
        """
        return all entry in igmp table
        """
        igmp_table = []
        is_igmp_entry = False
        res = self.get_gblqos()
        for index, line in enumerate(res):
            if "IGMP Group" in line:
                is_igmp_entry = True
            if "MLD Group" in line:
                is_igmp_entry = False
                break
            if is_igmp_entry and len(line.strip()) > 0:
                igmp_table.append(line)

        # remove igmp table header and empty line at the bottom
        igmp_table = igmp_table[2:]
        return igmp_table


    def get_mesh_info(self):
        """
        DO NOT use this method. Use get_mesh_info_dict instead.
        Get mesh-related information by executing command "get mesh"
        The function assume the data is shown in the layout below:

        BSSID             S LastSeen Ch P-Adver P-Sampl RSSI Flt IF D Management-MAC    SSID
        00:1d:2e:05:43:20 R        0  1   54.00    0.00   0   l   - 1 00:1d:2e:05:43:20 Mesh-430701005215
        @return: a list in which each item is a list holds information of a mesh link
        """
        return [x.split() for x in self.cmd("get mesh") if re.match("([0-9a-fA-F:]{17})", x)]

    def get_mesh_info_dict(self):
        """
        Get mesh-related information by executing command "get mesh"
        The function assume the data is shown in the layout below:

        rkscli: get mesh    [7.4.0.0.39 added column UR; we will return a dictionary dictionary]
        BSSID             S LastSeen Ch P-Metric L-Sampl RSSI/UL/NF  Flt IF UR D Management-MAC    SSID   IP
        00:22:7f:24:a9:00 M     3443 11   35.00    0.00    0/00/0    l    -  A 2 00:22:7f:24:a9:00 oSUlMHGknbAdHfFcrulKgNnGhUdGabFu 192.168.32.196
        00:1d:2e:56:3a:c8 N     3443 11   35.00   35.00   35/34/-95  a    -  A 1 00:1d:2e:16:3a:c0 oSUlMHGknbAdHfFcrulKgNnGhUdGabFu 192.168.32.192
        00:1d:2e:55:ff:c8 N     3376  6   35.00   35.00   45/41/-95  s    -  8 1 00:1d:2e:15:ff:c0 oSUlMHGknbAdHfFcrulKgNnGhUdGabFu 192.168.32.191
        00:22:7f:64:a9:88 U     3443 11   35.00   35.00   41/41/-95  c    -  * 1 00:22:7f:24:a9:80 oSUlMHGknbAdHfFcrulKgNnGhUdGabFu 192.168.32.197

        @return: a dictionary in which each key/ap_mac_address is a dictionary of a mesh link
        NOTE: IP column does not exist prior/equal to 7.4.0.0.24
        """
        result = self.do_cmd("get mesh")
        return_result = dict()
        rr_key = 'Management-MAC'
        m = re.search("""BSSID.*LastSeen.*Management-MAC\s*SSID.*IP""", result, re.I | re.M)
        if m:
            l_title = result[m.start():m.end()].split()
            l_result = result[m.end() + 1:].split('\n')
            for minfo in l_result:
                if re.match(r"^[0-9a-f:]+\s+", minfo, re.I):
                    aDict = dict()
                    l_info = minfo.split()
                    for idx in range(0, len(l_title)):
                        try:
                            aDict[l_title[idx]] = l_info[idx]

                        except:
                            aDict[l_title[idx]] = None

                    return_result[aDict[rr_key].lower()] = aDict

        return return_result


    def set_factory(self, login=True,force_ssh=False):
        """
        Set factory default for AP
        """
        res = self.cmd("set factory")
        if res[-1] == "OK":
            self.reboot(login=login,exit_on_pingable=force_ssh) #(factory = True)
        else:
            raise Exception("Can not set default factory for AP")


    def clear_persistent_cfg(self):
        '''
        This function will removed post_factory_persistence_data file on linux shell
        '''
        self.goto_shell()
        self.cmd('rm -f /writable/data/tr069/post_factory_persistence_data',
                 prompt="#")
        self.exit_shell()

    def set_cfg_info(self, **kwa):
        '''
        This function is to set some information like username, password... etc of the instance
        '''
        _kwa = {}
        _kwa.update(kwa)

        if _kwa.has_key('username'):
            self.username = _kwa['username']

        if _kwa.has_key('password'):
            self.password = _kwa['password']

    def get_kernel_info(self, **kwa):
        '''
        This function is to get system information such as average of CPU usage, memory
        in the period "interval" several times.
        Note: This function is verified on kernel
        Linux version 2.6.15 (root@lhotse.video54.local) (gcc version 4.2.4) #2 Tue Mar 10 19:33:54 PDT 2009
        kwa:
        - interval: A period to get average of cpu usage, memory(KB) in second
        - get_info: 0 for CPU_USAGE_INFO, 1 for MEMORY_INFO
        - times_to_check: how many times to get kernel information. Each time will be done
                in a period interval.
        output:
        - cpu usage/memory consumed by running processes
        '''
        _kwa = {
            'interval': 2, # it should not be less than 1.5
            'times_to_check': 3,
            'get_info': self.CPU_USAGE_INFO,
        }
        _kwa.update(kwa)
        interval, get_info = _kwa['interval'], _kwa['get_info']

        tmp = ''
        count = 1
        frame_pattern, frame_keyword = 'Mem:', 'Load average'
        while count <= _kwa['times_to_check']:
            self.tn.write('top\n')
            time.sleep(interval)
            self.tn.write('^C\n')
            ix, mobj, data = self.tn.expect(["#"],1)
            if data =='':
                interval +=1
                continue

            # get index of the first occurence
            search_pos = 0
            start_frame_idx, next_frame_idx = -1, -1
            end_frame_idx = -1
            start_frame_idx = data.find(frame_pattern, search_pos)
            if start_frame_idx == -1:
                interval +=1 # sleep longer
                continue

            # get index of next occurence
            search_pos = start_frame_idx + len(frame_pattern)
            next_frame_idx = data.find(frame_pattern, search_pos)
            end_frame_idx = next_frame_idx-1 if next_frame_idx != -1 \
                            else len(data)-1 # the data has only one frame

            tmp += data[start_frame_idx:end_frame_idx]
            # sleep a moment to continue get a new one
            count +=1
            #time.sleep(1)

        buf = tmp.split('\r\n')
        # get number of frames from top command in 'interval' time
        total_frame = len(filter(lambda x: re.match('.*Load average', x, re.I), buf))
        #logging.info('Current process list:\n %s\n. Total frame: %d' % (buf, total_frame))

        # cannot get cpu usage
        if total_frame == 0: raise Exception('Cannot get kernel info')

        # remove unsued line contains words such as "Men", "Load average", "PID USER", and empty element
        # and also remove "telnetd", "top" processes
        # after this step the list will look like
        # '  464 root     S N     4004     1  0.0 13.4 tr069d',
        # '  526 root     S N     4004   525  0.0 13.4 tr069d',
        # '  525 root     S N     4004   464  0.0 13.4 tr069d',
        filter_pattern = '.*shrd|.*buff|.*Mem|.*Load average|.*telnetd|.*top|\\x1b'
        running_process = filter(lambda x: not (x =='' or \
                        re.match(filter_pattern, x, re.I) ), buf) #|^ top

        cpu_col_idx, mem_col_idx = -3, -2
        col_idx = {
            self.CPU_USAGE_INFO: cpu_col_idx, # column to get cpu usage (the third col from the right side
            self.MEMORY_INFO: mem_col_idx, # column to get cpu usage (the second col from the right side
        }[get_info]
        total_resource_consumed = 0.0

        for i in range(len(running_process)):
            # break each string '  464 root     S N     4004     1  0.0 13.4 tr069d'
            # and remove empty element. After this filter, each element in running process looks like
            # ['81', 'root', 'S', 'N', '724', '20', '1.1', '2.4', 'timer']
            # ['464', 'root', 'S', 'N', '4004', '1', '0.0', '13.4', 'tr069d']
            # ['526', 'root', 'S', 'N', '4004', '525', '0.0', '13.4', 'tr069d']
            try:
                running_process[i] = filter(lambda x: x !='', running_process[i].split(' '))
                # sum all cpu usage for each process
                total_resource_consumed += float(running_process[i][col_idx])
            except Exception:
                # ignore error if found a line having one element only
                pass

        #logging.info('Kernel information: %0.4f' % (total_resource_consumed/total_frame))
        return (total_resource_consumed/total_frame)


    def set_syslog_network_level(self, level=3):
        return self.cmd(r'set syslog level network %s' % level)


    def get_processes(self):
        self.goto_shell()
        r = self.cmd(r'ps -ef', prompt='#', return_list=False)
        self.exit_shell()
        return r


    def get_ap_mgr_info(self):
        """
        Return the connection mode of the AP by issuing the command "apmgrinfo -a" in the Linux shell
        """
        self.goto_shell()
        self.tn.write("apmgrinfo -a\n")
        ix, mobj, rx = self.tn.expect(["# "])
        self.exit_shell()
        if not mobj:
            raise Exception("Not found the Linux shell")
        apmgrinfo = {}
        rx = rx.split("\n")
        rx = [l.strip("\r") for l in rx]
        for l in rx:
            x = l.split(":")
            if len(x) == 2:
                apmgrinfo[x[0].strip()] = x[1].strip()
        return apmgrinfo

    def set_director_info(self, ip1 = "", ip2 = "", zdcode = ""):
        if ip1 or ip2:
            self.cmd('set director ip %s %s' % (ip1, ip2))
        elif zdcode:
            self.cmd('set director zdcode %s' % zdcode)
        else:
            self.cmd('set director ip del')
            self.cmd('set director zdcode del')

    # Examples:
    #
    #   from ratenv import *
    #   dd = dict(ip_addr='192.168.2.200', username='admin', password='admin')
    #   ap200 = RuckusAP.RuckusAP(dd)
    #   mgmt_vlan = ap.get_mgmt_vlan()
    #   print mgmt_vlan
    #   {'ip': '192.168.2.200', 'net_mask': '255.255.255.0', 'brname': 'br5', 'type': 'dynamic', 'gateway': '192.168.2.253'}
    #   mbr0 = ap200.get_mgmt_vlan('br0')
    #   print mbr0
    #   {'ip': '169.254.68.26', 'net_mask': '255.255.0.0', 'brname': 'br0', 'type': 'static', 'gateway': '192.168.2.253'}
    #   mbr5 = ap200.get_mgmt_vlan('br5')
    #   print mbr5
    #   {'ip': '192.168.2.200', 'net_mask': '255.255.255.0', 'brname': 'br5', 'type': 'dynamic', 'gateway': '192.168.2.253'}
    #   mbr1 = ap200.get_mgmt_vlan('br1')
    #
#    def get_mgmt_vlan(self, mgmt_bridge = ''):
#        data = self.cmd("get mgmt_vlan", return_list = False)
#        if mgmt_bridge:
#            return self._bridge_ip_address(data, mgmt_bridge)
#        m = re.search(r'Management\s+Bridge\s+(br\d+)\s+', data, re.M | re.I)
#        if m:
#            mvcfg = self._bridge_ip_address(data, m.group(1))
#            if type(mvcfg) is dict and mvcfg.has_key('brname'):
#                obrn = 'br0' if mvcfg['brname'] == 'br5' else 'br5'
#                other = self._bridge_ip_address(data, obrn)
#                mvcfg['other'] = other
#            return mvcfg
#        return ''

    def _bridge_ip_address(self, data, br_name):
        ipPtn = r"[0-9.]+"
        pattern = r"%s\s+IP\s+Address\s+IP\s+Address\s+Configuration\s+Type:\s+(dynamic|static),\s+IP:\s+(%s)\s+Netmask\s+(%s)\s+Gateway\s+(%s)" % (br_name, ipPtn, ipPtn, ipPtn)
        m2 = re.search(pattern, data, re.I)
        if m2:
            return dict(brname = br_name, type = m2.group(1), ip = m2.group(2), net_mask = m2.group(3), gateway = m2.group(4))
        return ''

    # return list of list( (<cmd>, <response>) )
    def do_shell(self, cmd_block):
        rblock = []
        self.goto_shell()
        try:
            for cmd_line in cmd_block.split("\n"):
                print 'shcmd: %s' % cmd_line
                result = self.do_cmd(cmd_line, prompt = "#")
                rblock.append([cmd_line, result])
                pass
        except:
            pass
        self.exit_shell()
        return rblock

    def get_hotspot_policy(self, wlan_id, access_policy = False, redir_policy = False):       
        proc_file = ""
        acl_list = []

        if access_policy:
            proc_file = "%s-*" % wlan_id
            self.goto_shell()
            self.tn.write("cat /proc/afmod/policy/%s\n" % proc_file)
            ix, mobj, rx = self.tn.expect(["# "])
            self.exit_shell()
            if not mobj:
                raise Exception("Not found the Linux shell")
            
        elif redir_policy:
            proc_file = "%s-*" % str((int(wlan_id) + 2049))
            self.goto_shell()
            self.tn.write("cat /proc/afmod/policy/%s\n" % proc_file)
            ix, mobj, rx = self.tn.expect(["# "])
            if 'No such file or directory' in rx:
                proc_file = "%s-*" % str((int(wlan_id) + 33))                
                self.tn.write("cat /proc/afmod/policy/%s\n" % proc_file)
                ix, mobj, rx = self.tn.expect(["# "])
            self.exit_shell()
            if not mobj:
                raise Exception("Not found the Linux shell")
            
        if not proc_file:
            return acl_list

        
        #Updated by Jacky Luh @since: 2013-12-05
        #9.8 build enhance the walled garden policy file to surpport the domain name
        #in zd cli shell mode: cat /proc/afmod/policy/1025-3
        acl_re = re.compile("([\da-zA-Z\./]+)\s+([\da-zA-Z\./]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([a-zA-Z]+)")
        for line in rx.split("\r\n"):
            m = acl_re.search(line)
            if m:
                acl_list.append({'src-addr':m.group(1), 'dst-addr':m.group(2), 'proto':m.group(3),
                                 'sport':m.group(4), 'dport':m.group(5), 'action':m.group(6)})
        return acl_list

    def verify_status(self):
        """
        """
        logging.info('Sanity check: Verify telnet connection closed on AP [%s]' % self.ip_addr)
        self.tn.read_very_lazy()

    def get_top_info(self):
        self.goto_shell()
        self.tn.write('top\n')
        time.sleep(2)
        self.tn.write('^C')
        self.tn.write('\n')

        print self.tn.read_all()

    def get_l3_acl_cfg(self, acl_id):
        """
        """
        id_re = 'id\s*=\s*([0-9]+)'
        defaulf_action_re = 'default\s*=\s*(\w+)'
        mac_re = '[0-9a-fA-F:]{17}'
        ip_re = '[0-9.]+/[0-9]+'
        l2_re = '(%s)\s+(%s)\s+(\w+)\s+(\w+)' % (mac_re, mac_re)
        l3_re = '(%s)\s+(%s)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)' % (ip_re, ip_re)

        self.goto_shell()
        self.tn.write('cat /proc/afmod/policy/%s\n' % acl_id)
        ixx, mobj, rx = self.tn.expect(['#'])
        info = rx
        self.exit_shell()

        if 'No such file or directory' in info:
            raise Exception('There is no information about the policy "%s" on device' % acl_id)

        id = re.findall(id_re, info)[0]
        default_mode = re.findall(defaulf_action_re, info)[0]

        l2_rules = []
        for entry in re.findall(l2_re, info):
            rule = {}
            rule['src_mac'], rule['dst_mac'], rule['eth_type'], rule['action'] = entry
            l2_rules.append(rule)

        l3_rules = []
        idx = 1
        for entry in re.findall(l3_re, info):
            rule = {}
            rule['order'] = idx
            rule['src_addr'], rule['dst_addr'], rule['protocol'], rule['src_port'], rule['dst_port'], rule['action'] = entry
            l3_rules.append(rule)
            idx += 1

        acl_conf = {}
        acl_conf['id'] = id
        acl_conf['default_mode'] = default_mode
        acl_conf['l2_rules'] = l2_rules
        acl_conf['rules'] = l3_rules

        return acl_conf

    def get_device_type(self):
        """
        Return the model of the AP
        """
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
            if line.startswith('inet addr'):
                temp = {}
                inet_addr = line.split()[1:]
                if len(inet_addr) > 2:
                    if not ppp_inf: temp['mac'] = mac
                    temp['ip_addr'] = inet_addr[0].split(':')[1]
                    temp['mask'] = inet_addr[2].split(':')[1]
                    if_info['%s' % inf] = temp

        self.exit_shell()
        return if_info

    def get_tos_values(self, get_tos_classify = True):
        """
        This function gets ToS values of media types.
        Input:
            - get_tos_classify: used to decide if this function will get ToS classification values or not.
        Output:
            - Return a dictionary of ToS values of media types
        """
        list_qos_info = self.cmd('get qos')
        found = False
        tos_dict = {}
        for element in list_qos_info:
            if get_tos_classify:
                pat = "^(TOS.*Classification:).*"
                mobj = re.search(pat, element)
                if mobj:
                    found = True
                    break
            else:
                pat = "^(TOS.*marking:).*"
                mobj = re.search(pat, element)
                if mobj:
                    found = True
                    break
        if not found:
            if get_tos_classify:
                raise Exception('The ToS Classification values do not appear when getting QoS information')
            else:
                raise Exception('The ToS marking values do not appear when getting QoS information')
        if get_tos_classify:
            tos_classify_value = [x.rstrip(',') for x in element.split(' ') if x][2:]
            for value in tos_classify_value:
                value = value.split('=')
                tos_dict['%s' % value[0].lower()] = value[1]
        else:
            tos_marking_value = [x.rstrip(',') for x in element.split(' ') if x][2:]
            for value in tos_marking_value:
                value = value.split('=')
                if value[0].lower() == 'voip':
                    media = 'voice'
                else:
                    media  = value[0].lower()
                tos_dict['%s' % media] = value[1]

        time.sleep(5)
        return tos_dict

    def set_tos_values(self, media_type, tos_value, set_tos_classify = True):
        """
        This function sets ToS values for classification or marking.
        Input:
            - media_type: type of media, such as voice, video, data, background
            - tos_value: ToS value
            - set_tos_classify: used to determine if ToS value is set for classification or marking
        Output: none
        """
        if set_tos_classify:
            cmd = "set qos tos classify %s %s" % (media_type, tos_value)
        else:
            cmd = "set qos tos mark %s %s" % (media_type, tos_value)

        res = self.cmd(cmd)
        if res[-1] != "OK":
            raise Exception("Can not set ToS value for media queue")

    def _get_eth_inf_status(self, if_port = "0"):
        """
        Get status of ethernet interface to check if it is up or not
        @return a dictionary of interface name and its status
        """

        self.goto_shell()
        cmd = "cat /proc/net/eth/%s" % if_port
        res = self.cmd(cmd, 0, "#")[0].split()
        self.exit_shell()
        return dict(if_name = res[1], status = int(res[-1]))

    def _get_all_eth_inf_status(self):
        self.goto_shell()
        cmd = "cat /proc/net/eth/ports"
        res = self.cmd(cmd, 0, "#")
        self.exit_shell()
        return res

    def get_eth_dev_id(self, eth_inf):
        self.goto_shell()
        res = self.cmd('cat /proc/net/eth/devices', 0, '#')
        dev_id = ''
        for line in res:
            if eth_inf in line:
                dev_id = line.split()[0]
        self.exit_shell()
        return dev_id

    def get_eth_inferface_name(self):
        """
        Get name of Ethernet inferface that appropriating with svcp interface
        """
        profile = self.get_board_data_item("Customer ID")
        interface = ""
        if profile == "ruckus" or profile == 'router01': interface = "eth0"
        elif profile == "ruckus01" or profile == "ruckus03": interface = "eth1"
        elif profile == "ruckus05": interface = "eth3"
        elif profile == 'ruckus04': interface = 'eth2'
        elif profile == '4bss' or profile == 'ruckus06':
            try:
                for i in range(5):
                    res_tmp = self._get_eth_inf_status(i)
                    if res_tmp['status']:
                        interface = res_tmp['if_name']
                        break
                    time.sleep(1)
            except:
                res_tmp = self._get_all_eth_inf_status()
                for eth in res_tmp:
                    if int(eth.split()[-1]):
                        interface = "eth" + eth.split()[0].strip()
                        break

        return interface

    def get_all_eth_interface(self):
        """
        Get all Ethernet interfaces (name and status) on AP (using for 8.0 and over)
        Note:
         output 9.0 and previous version for get eth is different
         9.0: 1     eth1        Up            Up 100Mbps full
         Old: eth1            Up
         So need to change the way to extract eth status: Status is the word
         right after interface name.
        """
        buf = self.cmd('get eth\n')
        buf = [x.strip() for x in buf]

        if_pat, status_pat = '(eth[0-9]+)', '(?<=eth\d)\s+\w+'
        interface_list = []
        for line in buf:
            temp_dict = {}
            mobj = re.search(if_pat, line)
            if mobj:
                temp_dict['interface'] = mobj.group(1)
                temp_dict['status'] = \
                    re.search(status_pat, line, re.I).group(0).strip().lower()
                interface_list.append(temp_dict)

        return interface_list

    def set_tos_classification(self, interface, enabled = True):
        """
        Set status for ToS Classification on Ethernet interface that appropriating with svcp interface
        """
        if enabled: status = "enable"
        else: status = "disable"

        cmd = "set qos %s tos classify %s" % (interface, status)
        res = self.cmd(cmd)[-1]
        if res != "OK":
            raise Exception("Can not %s ToS classification" % status)

    def get_tos_classification(self, interface):
        """
        Get status for ToS Classification on Ethernet interface that appropriating with svcp interface
        If ToS classification is enabled, return True. Otherwise, return False
        """
        cmd = "get qos %s" % interface

        res = [x for x in self.cmd(cmd) if x.startswith("TOS Classification")][0].split()[-1]
        if res == "Enabled": return True
        return False

    def set_tos_marking(self, interface, enabled = True):
        """
        Set status for ToS marking on the Ethernet interface that appropriating with svcp interface
        """
        if enabled: status = "enable"
        else: status = "disable"

        cmd = "set qos %s tos marking %s" % (interface, status)
        res = self.cmd(cmd)[-1]
        if res != "OK":
            raise Exception("Can not %s ToS marking" % status)

    def get_tos_marking(self, interface):
        """
        Get status for ToS marking on Ethernet interface that appropriating with svcp interface
        If ToS marking is enabled, return True. Otherwise, return False
        """
        cmd = "get qos %s" % interface

        res = [x for x in self.cmd(cmd) if x.startswith("TOS Marking")][0].split()[-1]
        if res == "Enabled": return True
        return False

    def set_heuristics_status(self, status, interface):
        """
        Set status for Heuristics
        """
        res = self.cmd("set qos heuristics %s" % status)[-1]
        if res != "OK":
            try:
                res = self.cmd("set qos %s heuristics udp %s" % (interface, status))[-1]
            except:
                raise Exception("Can not %s heuristics" % status)

    def get_heuristics_cfg(self):
        """
        Get Heuristics configuration information.
        Return a dictionary of packet gap and packet length that configured for voice/video
        """
        res = self.cmd('get qos')

        heuristics_config = {}
        packet_len = {}
        packet_gap = {}
        classify = {}
        noclassify = {}
        for line in res:
            if "packet length" in line.lower():
                temp_packet_len = line.split(':')[1].strip().split()
                temp_packet_len = [x.split('/') for x in temp_packet_len]
                packet_len['voice'] = temp_packet_len[0]
                packet_len['video'] = temp_packet_len[1]

            if "packet gap" in line.lower():
                temp_packet_gap = line.split(':')[1].strip().split()
                temp_packet_gap = [x.split('/') for x in temp_packet_gap]
                packet_gap['voice'] = temp_packet_gap[0]
                packet_gap['video'] = temp_packet_gap[1]

            if 'during classify' in line.lower():
                temp_classify = line.split(':')[1].strip().split()
                classify['voice'] = temp_classify[0]
                classify['video'] = temp_classify[1]

            if 'between classify' in line.lower():
                temp_noclassify = line.split(':')[1].strip().split()
                noclassify['voice'] = temp_noclassify[0]
                noclassify['video'] = temp_noclassify[1]


        heuristics_config['packet_len'] = packet_len
        heuristics_config['packet_gap'] = packet_gap
        heuristics_config['classify'] = classify
        heuristics_config['noclassify'] = noclassify

        return heuristics_config

    def set_heuristics_cfg(self, media_type, cfg_classify = False, cfg_noclassify = False, cfg_pktgap = False, cfg_pktlen = False,
                            octet_count = '', min_value = '', max_value = ''):

        if cfg_classify:
            cmd = 'set qos heuristics %s classify %s' % (media_type, octet_count)
        if cfg_noclassify:
            cmd = 'set qos heuristics %s noclassify %s' % (media_type, octet_count)
        if cfg_pktgap:
            cmd = 'set qos heuristics %s ipg %s %s' % (media_type, min_value, max_value)
        if cfg_pktlen:
            cmd = 'set qos heuristics %s pktlen %s %s' % (media_type, min_value, max_value)

        res = self.cmd(cmd)[-1]
        if not 'ok' in res.lower(): return False
        return True

    def get_mqstats(self, wlan_if):
        """
        This function gets media queues statistic on the AP.
        - Output: return a dictionany, in there key of this dictionary is the mac address of the station,
        value of these key is another dictionary that includes value of media queues
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd('get mqstats %s all' % wlan_if_name)
        if res[-1].lower() != 'ok':
            res = self.cmd('get mqstats %s all' % wlan_if)
            if res[-1].lower() != 'ok':
                res = self.cmd('get mqstats %s assoc' % wlan_if)

        res = [x.lstrip(' ').rstrip(' ') for x in res if not x.startswith('-')][:-1]
        col_name = res[1].split()
        for item in res:
            if item.startswith('Qued'):
                res.remove(item)

        all_stations = {}
        each_station = {}
        for i in range(len(res)):
            if res[i].startswith('STA'):
                if res[i].split()[1] != "None":
                    mac_addr = res[i].split()[1]
                continue
            if 'deflt' in res[i]:
                continue

            if res[i].startswith('VAP'):
                mac_addr = res[i].split()[1]
                continue

            # Get value on each column for each media type and save it to a dictionary
            #list_tmp = [x.lstrip(' ').rstrip(' ') for x in res[i].split(' ') if x][1:]
            list_str_tmp = [x.strip() for x in res[i].split(' ') if x][1:]
            list_tmp = []
            for s in list_str_tmp:
                try:
                    s = int(s)
                    list_tmp.append(s)
                except: pass
            l = 0
            queue = {}
            for name in col_name:
                queue[name] = list_tmp[l]
                l = l + 1
            queue_temp = queue.copy()
            
            #@author: Jane.Guo @since: 2013-09 use common function to compare version
            newv_list = ['9.5.0.5.71','9.7.0.0.84','0.0.0.99.738']
            version = self.get_version()
            c_result = compare_version_list(version, newv_list)
        
            if c_result >= 0:
                if 'data VO' in res[i]: each_station['data VO'] = queue_temp
                if 'data VI' in res[i]: each_station['data VI'] = queue_temp
                if 'data BE' in res[i]: each_station['data BE'] = queue_temp
                if 'data BK' in res[i]: each_station['data BK'] = queue_temp                
            else:
                if 'voice' in res[i]: each_station['voice'] = queue_temp
                if 'video' in res[i]: each_station['video'] = queue_temp
                if 'data' in res[i]: each_station['data'] = queue_temp
                if 'bkgnd' in res[i]: each_station['bkgnd'] = queue_temp

            # Save all information of each station to a dictionary
            if len(each_station) == 4:
                all_stations['%s' % mac_addr] = each_station
                each_station = {}
        logging.info('[mqstats is] %s'%all_stations)
        return all_stations

    def clear_mqstats(self, wlan_if, option = "all"):
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        res = self.cmd("set mqstats %s clear %s" % (wlan_if, option))
        if res[-1] != "OK":
            res = self.cmd("set mqstats %s clear %s" % (wlan_if_name, option))
            if res[-1] != 'OK':
                res = self.cmd('set mqstats %s clear assoc' % wlan_if)
        time.sleep(2)

    def set_port_match_status(self, status, interface):
        """
        This function sets port match status for AP enable or disable.
        """
        res = self.get_port_match_status(interface)
        if res:
            cmd = "set qos %s port %s" % (interface, status)
            res = self.cmd(cmd)[-1]
            if res != "OK":
                raise Exception("Can not %s Port Match Filter on the AP" % status)

    def get_port_match_status(self, interface):
        """
        If AP allow to set Port Match status, this function will get status of port match
        """
        cmd = "get qos %s" % interface

        port_match_txt = ""
        for x in self.cmd(cmd):
            if x.startswith("Port Match"):
                port_match_txt = x
                break
        if port_match_txt:
            res = port_match_txt.split()[-1]
            if res == "Enabled":
                return 'enable'
            else:
                return 'disable'
        else:
            return

    def add_port_matching_rule(self, interface, proto, action, filter_value = "", dest_port = True, media = "", layer = "4", cast = "ucast"):
        """
        Add a port matching filter rule to the specific interface
        Input:
        - proto: protocol udp or tcp
        - action: drop, tos, or priority
        - port: port number
        - dest_port: If it's true, added port is destination's. Otherwise, added port is source's
        - media: voice/video/data/background
        """
        #@author: Jane.Guo @since: 2013-09 use common function to compare version
        newv_list = ['9.8.0.0.10', '9.9.0.0.29']
        version = self.get_version()
        c_result = compare_version_list(version, newv_list)
        
        #Modified by Serena Tan. 2010.11.1
        #To fix bug 16093.
        if c_result >= 0 or version[0:7] == "9.0.0.3":
            if layer == "3":
                cmd = 'set qos %s ip add %s' % (interface,cast)
                if dest_port: cmd = "%s dest %s/255.255.255.255" % (cmd, filter_value)
                else: cmd = "%s src %s/255.255.255.255" % (cmd, filter_value)
            
            elif layer == "4":
                cmd = 'set qos %s port add %s %s' % (interface, cast, proto)  
                if dest_port: cmd = "%s dest %s" % (cmd, filter_value)
                else: cmd = "%s src %s" % (cmd, filter_value) 
                          
            else:
                cmd = 'set qos %s mac add %s' % (interface,cast)               
                if dest_port: cmd = "%s dest %s" % (cmd, filter_value)
                else: cmd = "%s src %s" % (cmd, filter_value) 
    
            if action == "drop": cmd = "%s %s" % (cmd, action)
            else:
                if not media: media = "voice"
                cmd = "%s %s %s" % (cmd, action, media)
############zj_edit 2013-11-21 above is to adaptor the behavior change for AP cli command zf-6155 9.8.0.0.66
        else:
            if layer == "4":
                cmd = 'set qos %s port add %s' % (interface, proto)
            elif layer == "3":
                cmd = 'set qos %s ip add' % interface
            else:
                cmd = 'set qos %s mac add' % interface

            if dest_port: cmd = "%s dest %s" % (cmd, filter_value)
            else: cmd = "%s src %s" % (cmd, filter_value)

            if action == "drop": cmd = "%s %s" % (cmd, action)
            else: cmd = "%s %s %s" % (cmd, action, media)

        res = self.cmd(cmd)[-1]
        if (res != "OK") :
            logging.info(res)
            raise Exception("Can not add a port matching rule on the AP")


    def get_port_matching_rule(self, interface):
        """
        Get all port matching filter rules configured on the specific interface
        Return a list of dictionaries, in there each dictionary contains configuration parameters for each rule
        """

        #Modified by Serena Tan. 2010.11.23
        #To fix bug 16093.
        version = self.get_version()
        ver = version.split('.')[0:2]
        ver = '.'.join(ver)
        if float(ver) >= 9.1 or version[0:7] == "9.0.0.3":
            return self.get_port_matching_rule_from_new_build(interface)

        res = self.cmd('get qos %s' % interface)
        list_tmp = []
        for i in range(len(res)):
            if "filters" in res[i].lower():
                list_tmp = res[i:len(res) - 1]
                break

        number_tcp_filters_pat = ".* ([0-9]+) TCP/IP .*$"
        number_udp_filters_pat = ".* ([0-9]+) UDP/IP .*$"
        num_general_filters_pat = ".* ([0-9]+) General Filter.*$"

        tcp_rule_list = []
        udp_rule_list = []
        rule_list = []

        for i in range(len(list_tmp)):
            tcp_obj = re.search(number_tcp_filters_pat, list_tmp[i])
            udp_obj = re.search(number_udp_filters_pat, list_tmp[i])
            if tcp_obj:
                number_tcp_filters = int(tcp_obj.group(1))
                tcp_rule_list = list_tmp[(i + 2):(i + number_tcp_filters + 2)]
            if udp_obj:
                number_udp_filters = int(udp_obj.group(1))
                udp_rule_list = list_tmp[(i + 2):(i + number_udp_filters + 2)]

        # Get information of udp filters
        port_filter_info = []

        if not udp_rule_list and not tcp_rule_list:
            for i in range(len(list_tmp)):
                mobj = re.search(num_general_filters_pat, list_tmp[i])
                if mobj:
                    number_filters = int(mobj.group(1))
                    rule_list = list_tmp[(i + 2):(i + number_filters + 2)]
        else:
            rule_list = (udp_rule_list + tcp_rule_list)

        for rule in rule_list:
            rule_dict = {}
            temp = rule.split()[0].split('-')[0].lower()
            if temp == "udp" or temp == "tcp":
                rule_dict['proto'] = temp
                rule_dict['location'] = rule.split()[0].split('-')[1].lower()
            else:
                rule_dict['location'] = temp
                rule_dict['proto'] = rule.split()[0].split('-')[1].lower()
            rule_dict['filter_value'] = rule.split()[1]
            if rule.split()[2].lower().startswith('drop'):
                rule_dict['action'] = rule.split()[2].lower()
            else:
                rule_dict['action'] = rule.split()[3].lower()
                rule_dict['media'] = rule.split()[5]

            port_filter_info.append(rule_dict)

        return port_filter_info

    #Added by Serena Tan. 2010.11.23
    #To fix bug 16093.
    def get_port_matching_rule_from_new_build(self, interface):
        """
        This method is for build no lower than 9.1.
        Get all port matching filter rules configured on the specific interface.
        Return a list of dictionaries, in there each dictionary contains configuration parameters for each rule
        """
        res = self.cmd('get qos %s' % interface)
        list_tmp = []
        for i in range(len(res)):
            if "Interface" in res[i]:
                list_tmp = res[i:len(res) - 1]
                break

        number_ucast_filters_pat = "Interface .* ([0-9]+) Unicast .* Filters.*$"
        number_bcast_filters_pat = "Interface .* ([0-9]+) Broadcast/Multicast .* Filters.*$"

        ucast_rule_list = []
        bcast_rule_list = []
        for i in range(len(list_tmp)):
            ucast_obj = re.search(number_ucast_filters_pat, list_tmp[i])
            bcast_obj = re.search(number_bcast_filters_pat, list_tmp[i])
            if ucast_obj:
                number_ucast_filters = int(ucast_obj.group(1))
                ucast_rule_list = list_tmp[(i + 2):(i + number_ucast_filters + 2)]
            if bcast_obj:
                number_bcast_filters = int(bcast_obj.group(1))
                bcast_rule_list = list_tmp[(i + 2):(i + number_bcast_filters + 2)]

        port_filter_info = []

        for rule in ucast_rule_list:
            rule_dict = {}
            rule_dict['cast'] = 'ucast'
            temp = rule.split()[0].split('-')[0].lower()
            if temp == "udp" or temp == "tcp":
                rule_dict['proto'] = temp
                rule_dict['location'] = rule.split()[0].split('-')[1].lower()
            else:
                rule_dict['location'] = temp
                rule_dict['proto'] = rule.split()[0].split('-')[1].lower()
            rule_dict['filter_value'] = rule.split()[1]
            if rule.split()[2].lower().startswith('drop'):
                rule_dict['action'] = rule.split()[2].lower()
            else:
                rule_dict['action'] = rule.split()[3].lower()
                rule_dict['media'] = rule.split()[5]
            port_filter_info.append(rule_dict)

        for rule in bcast_rule_list:
            rule_dict = {}
            rule_dict['cast'] = 'bcast'
            temp = rule.split()[0].split('-')[0].lower()
            if temp == "udp" or temp == "tcp":
                rule_dict['proto'] = temp
                rule_dict['location'] = rule.split()[0].split('-')[1].lower()
            else:
                rule_dict['location'] = temp
                rule_dict['proto'] = rule.split()[0].split('-')[1].lower()
            rule_dict['filter_value'] = rule.split()[1]
            if rule.split()[2].lower().startswith('drop'):
                rule_dict['action'] = rule.split()[2].lower()
            else:
                rule_dict['action'] = rule.split()[3].lower()
                rule_dict['media'] = rule.split()[5]
            port_filter_info.append(rule_dict)

        return port_filter_info

    def remove_port_matching_rule(self, interface):
        """
        Remove all port matching rules configured on the Ethernet interface that appropriating with svcp interface
        """
        port_filter_rules = self.get_port_matching_rule(interface)

        #Modified by Serena Tan. 2010.11.23
        #To fix bug 16093.
        version = self.get_version()
        ver = version.split('.')[0:2]
        ver = '.'.join(ver)
        if float(ver) >= 9.1 or version[0:7] == "9.0.0.3":
            for each_rule in port_filter_rules:
                cast = each_rule['cast']
                proto = each_rule['proto']
                filter_value = each_rule['filter_value']
                location = each_rule['location']
                cmd = 'set qos %s port delete %s %s %s %s' % (interface, cast, proto, location, filter_value)
                print cmd
                res = self.cmd(cmd)[-1]
                if res != "OK":
                    raise Exception("Can not remove a port matching rule on the AP")
                time.sleep(2)

        else:
            for each_rule in port_filter_rules:
                proto = each_rule['proto']
                filter_value = each_rule['filter_value']
                location = each_rule['location']
                cmd = 'set qos %s port delete %s %s %s' % (interface, proto, location, filter_value)
                print cmd
                res = self.cmd(cmd)[-1]
                if res != "OK":
                    raise Exception("Can not remove a port matching rule on the AP")
                time.sleep(2)

    def get_device_name(self):
        """
        Get display device name of AP
        """
        res = self.cmd("get device-name")
        return res[0].split("device name : ")[-1].split("'")[1]

    def get_device_location(self):
        """
        Get display device location of AP
        """
        res = self.cmd("get device-location")
        location = res[0].split("Device location : ")[-1]
        location = location.replace("\'", "")
        return location

    def get_device_gps(self):
        """
        Get AP GPS coordinates
        """
        res = self.cmd("get device-gps")
        device_gps = res[0].split("GPS coordinates : ")[-1]
        device_gps_info = { 'latitude': '', 'longitude':''}
        if "," in device_gps:
            device_gps_info['latitude'] = device_gps.split(',')[0]
            device_gps_info['longitude'] = device_gps.split(',')[-1]
        return device_gps_info

    def verify_dead_station(self, station):
        """
        This function is used to verify that the station is alive or not
        """
        self.goto_shell()
        self.tn.write('ls /proc/v54\n')
        idx, mobj, txt = self.tn.expect(['#'], 10)
        self.exit_shell()

        buf = [line.rstrip('\r').strip('\n') for line in txt.split()][2:-1]
        sta_pat = "^([\w]+)_[\w]+$"
        mac_txt = ""
        for i in buf:
            mobj = re.search(sta_pat, i)
            if mobj:
                mac_txt = mobj.group(1)
                break

        sta_dead = True
        if mac_txt.lower() == station.lower():
            sta_dead = False

        if sta_dead: return True
        return False

    def get_ath_stats(self, model):
        """
        Get athstats to verify transmited packets out of the wireless interface on the AP
        @return number of transmited packet
        """
        self.goto_shell()
        buf = self.cmd('athstats', 0, '#')
        self.exit_shell()

        buf = [x.strip() for x in buf]
        tx_packet = 0
        if model == 'vf7811':
            pattern = "([0-9]+) total tx data packets.*"
        else:
            pattern = "([0-9]+) tx frames with short preamble"

        for line in buf:
            mobj = re.search(pattern, line)
            if mobj:
                tx_packet = int(mobj.group(1))
                break
        return tx_packet

    def ping_from_ap(self, target_ip, timeout_ms = 1000):
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
                mobj = re.search(pat, line)
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
        Get sta-mgmt information on the specific interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd('get sta-mgmt %s' % wlan_if_name)
        if buf[-1].lower() != 'ok':
            buf = self.cmd('get sta-mgmt %s' % wlan_if)

        buf = buf[0].split(':')[1]
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
        Set status of sta-mgmt on the specific interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        if enabled:
            status = 'enable'
        else:
            status = 'disable'

        buf = self.cmd('set sta-mgmt %s %s' % (wlan_if_name, status))[-1]
        time.sleep(2)
        if not "OK" in buf:
            self.cmd('set sta-mgmt %s %s' % (wlan_if, status))

    def get_station_info(self, wlan_if):
        """
        Get all station information of the specific wlan on the AP
        @return a dictionary of station information
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd('get station %s info all' % wlan_if_name)
        if buf[-1].lower() != 'ok':
            buf = self.cmd('get station %s info all' % wlan_if)

        buf = buf[:-1]
        if len(buf) == 1:
            return {}

        buf = [x for x in buf if not x.startswith('-')]

        col = [x.lower() for x in buf[0].split()[2:]]
        sta_info = {}
        for sta in buf[1:]:
            temp = {}
            mac = sta.split()[0]
            for i in range(len(col)):
                temp[col[i]] = sta.split()[i+1]
            sta_info[mac] = temp

        sta_info['total_station'] = len(buf[1:])
        return sta_info

    def get_rpm_key(self,key):
        """
        return rpmkey current setting of key.
        if key doesn't exist, this function return error message on AP
        """
        return self.cmd("get rpmkey %s" % key)

    def set_tx_power(self, wlan_if, value):
        self.cmd('set txpower %s %s' % (wlan_if, value))


    def get_login(self):
        """ return current login ID"""
        return self.cmd("get login")[0].split(":")[1]

    def get_managemt_service_status(self, service_name):
        """
        return status of managemnent service
        """
        return self.cmd("get %s" % service_name)[0].split()[-1]

    def enable_qos_directed_multicast(self, if_name, enable=True):
        """
        Enable/Disable QoS Directed Multicast on interface (if_name)
        """
        if not if_name.startswith("eth") and if_name not in['svcp','home']:
            if_name = self.wlan_if_to_name(if_name)

        return self.cmd("set qos %s directed multicast %s" %
                        (if_name, {True:'enable', False:'disable'}[enable]))

    def get_qos_cfg_option(self, if_name = None):
        """
        Get all QoS Option on interface
        Use if_name = "" to get QoS option of eth interface appropriate with wlan svcp
        return all QOS configuration options
        """
        if if_name is None:
            if_name = self.get_eth_inferface_name()
        if not if_name.startswith("eth") and if_name not in['svcp','home']:
            if_name = self.wlan_if_to_name(if_name)
        qos_cfg = {}
        for option in self.cmd("get qos %s" % if_name):
            if ":" in option:
                qos_cfg[option.split(":")[0].replace(" ","_").lower()] = option.split(":")[-1].strip()

        return qos_cfg



    def get_mgmt_ip_addr(self):
        """
        This function gets ip address on mgmt port (applied for AP has profile ruckus05)
        """
        res = {}
        res['mgmt'] = {}

        ip_addr = self.cmd("get ip_addr mgmt")[0].split(':')[-1].strip().split()[0]
        res['mgmt']['ip_addr'] = ip_addr
        return res


    def set_qos_cfg_option(self, interface, option = '', enabled = True):
        """
        Change QoS configuration option on Ethernet inferface that appropriating with svcp interface
        """
        if enabled: status = "enable"
        else: status = "disable"

        buf = self.cmd('set qos %s %s %s' % (interface, option, status))[-1]
        time.sleep(2)
        if not "OK" in buf:
            raise Exception("Can not %s %s on the %s interface" % (status,option, interface))

    def get_igmp_snooping(self, wlan_if):
        """
        Get status of IGMP snooping on svcp interface
        """
        status = ""
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("get qos %s" % wlan_if_name)
        if buf[-1].lower() != 'ok':
            buf = self.cmd("get qos %s" % wlan_if)

        for line in buf:
            if line.lower().startswith('igmp snooping'):
                status = line.split(':')[-1].strip().lower()
                break
        if status.startswith('enabled'): return True
        else: return False

    def set_igmp_snooping(self, wlan_if, enabled = True):
        """
        Change status of IGMP snooping on svcp interface
        """
        if enabled: status = "enable"
        else: status = "disable"

        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("set qos %s igmp %s" % (wlan_if_name, status))
        if buf[-1].lower() != 'ok':
            buf = self.cmd("set qos %s igmp %s" % (wlan_if, status))
        time.sleep(2)

    def set_directed_bcast_status(self, wlan_if, status = 'enable'):
        """
        Change status of directed broadcast on svcp interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("set qos %s directed broadcast %s" % (wlan_if_name, status))
        if buf[-1].lower() != 'ok':
            buf = self.cmd("set qos %s directed broadcast %s" % (wlan_if, status))
        time.sleep(2)

    def get_directed_bcast_status(self, wlan_if):
        """
        Get status of directed broadcast on svcp interface
        """
        wlan_if_name = self.wlan_if_to_name(wlan_if)
        buf = self.cmd("get qos %s" % wlan_if_name)
        if buf[-1].lower() != 'ok':
            buf = self.cmd("get qos %s" % wlan_if)
        time.sleep(2)

        status = ""
        for line in buf:
            if line.lower().startswith('directed broadcast'):
                status = line.split(':')[-1].strip().lower()
                break
        if status.startswith('enabled'): return 'enable'
        else: return 'disable'

    def get_dead_station_count(self):
        """
        Return current Dead Station Count value in 'get qos' information.
        """
        qos_info = self.cmd('get qos')

        for line in qos_info:
            if "Dead Station Count" in line:
                return int(line.split(":")[-1].split()[0])

    def set_http_status(self, enable = True):
        if enable: status = "enable"
        else: status = "disable"
        self.cmd("set http %s" % status)

    def set_https_status(self, enable = True):
        if enable: status = "enable"
        else: status = "disable"
        self.cmd("set http %s" % status)

    def get_dhcpc_info(self):
        pat = "([0-9]+)"
        dhcpc_info = {}

        tryagain = self.cmd('get dhcpc tryagain')[0]
        mobj = re.search(pat, tryagain)
        if not mobj:
            raise Exception('DHCPC tryagain is not configured')
        dhcpc_info['tryagain'] = mobj.group(1)

        expbkofftime = self.cmd('get dhcpc expbkofftime')[0]
        mobj = re.search(pat, expbkofftime)
        if not mobj:
            raise Exception('DHCPC expbkofftime is not configured')
        dhcpc_info['expbkofftime'] = mobj.group(1)

        maxexptime = self.cmd('get dhcpc maxexptime')[0]
        mobj = re.search(pat, maxexptime)
        if not mobj:
            raise Exception('DHCPC maxexptime is not configured')
        dhcpc_info['maxexptime'] = mobj.group(1)

        return dhcpc_info

    def get_vlan_info(self):
        res = self.cmd('get vlan')
        res = [line.strip('\t').strip() for line in res if not line.startswith('-') and not 'not used' in line][:-1]

        vlan_info = []
        pat = ".*: \\((.*)\\) VID ([0-9]+)"
        position_vlan = []
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                position_vlan.append(res.index(line))

        for pos in range(len(position_vlan)):
            each_vlan = {}
            position_untagged = 0
            position_tagged = 0
            wlan_untagged_list = []
            wlan_tagged_list = []
            if pos == len(position_vlan) - 1:
                each_vlan_list = res[int(position_vlan[pos]) : len(res)]
            else:
                each_vlan_list = res[int(position_vlan[pos]):int(position_vlan[pos+1])]

            for line in each_vlan_list:
                mobj = re.search(pat, line)
                if mobj:
                    each_vlan['vlan_name'] = mobj.group(1)
                    each_vlan['vlan_id'] = mobj.group(2)

                if line.lower().startswith('eth port'):
                    if 'tagged' in line:
                        list_tmp = line.split(':')[-1].split(',')[:-1]
                        str_tmp = " ".join(i for i in list_tmp).lstrip()
                        each_vlan['eth_tagged_port'] = str_tmp
                    else:
                        list_tmp = line.split(':')[-1].split(',')[:-1]
                        str_tmp = " ".join(i for i in list_tmp).lstrip()
                        each_vlan['eth_native_port'] = str_tmp

                if line.lower().startswith('wireless') and 'tagged' in line:
                    position_tagged = each_vlan_list.index(line)
                if line.lower().startswith('wireless') and not 'tagged' in line:
                    position_untagged = each_vlan_list.index(line)

            if position_tagged and position_untagged:
                wlan_untagged_list = each_vlan_list[position_untagged + 1 : position_tagged]
                wlan_tagged_list = each_vlan_list[position_tagged + 1:]
            elif position_tagged and not position_untagged:
                wlan_tagged_list = each_vlan_list[position_tagged + 1:]
            elif position_untagged and not position_tagged:
                wlan_untagged_list = each_vlan_list[position_untagged + 1:]

            wlan_pat = 'wlan([0-9]+)'
            list_tmp = []
            for wlan in wlan_untagged_list:
                mobj = re.search(wlan_pat, wlan)
                if mobj:
                    list_tmp.append(mobj.group(1))
            if list_tmp:
                str_tmp = " ".join(i for i in list_tmp)
                each_vlan['native_wlan'] = str_tmp

            list_tmp = []
            for wlan in wlan_tagged_list:
                mobj = re.search(wlan_pat, wlan)
                if mobj:
                    list_tmp.append(mobj.group(1))
            if list_tmp:
                str_tmp = " ".join(i for i in list_tmp)
                each_vlan['tagged_wlan'] = str_tmp

            vlan_info.append(each_vlan)

        return vlan_info

    def remove_all_vlan(self):
        vlan_info = self.get_vlan_info()

        for info in vlan_info:
            if info['vlan_id'] != '1':
                self.cmd('set vlan %s clear' % info['vlan_id'])
                if info.has_key('native_wlan'):
                    self.cmd('set vlan 1 native wlan %s add' % info['native_wlan'])
                if info.has_key('eth_native_port'):
                    self.cmd('set vlan 1 native port %s add' % info['eth_native_port'])
                self.cmd('set vlan apply')
                time.sleep(2)

    def create_vlan(self, vlan_cfg):

        if vlan_cfg.has_key('vlan_name'):
            self.cmd('set vlan %s name %s' % (vlan_cfg['vlan_id'], vlan_cfg['vlan_name']))
        if vlan_cfg.has_key('eth_native_port'):
            self.cmd('set vlan 1 native port %s del' % vlan_cfg['eth_native_port'])
            self.cmd('set vlan %s native port %s add' % (vlan_cfg['vlan_id'], vlan_cfg['eth_native_port']))
        if vlan_cfg.has_key('eth_tagged_port'):
            self.cmd('set vlan %s tagged port %s add' % (vlan_cfg['vlan_id'], vlan_cfg['eth_tagged_port']))
        if vlan_cfg.has_key('native_wlan'):
            self.cmd('set vlan 1 native wlan %s del' % vlan_cfg['native_wlan'])
            self.cmd('set vlan %s native wlan %s add' % (vlan_cfg['vlan_id'], vlan_cfg['native_wlan']))
        if vlan_cfg.has_key('tagged_wlan'):
            self.cmd('set vlan %s tagged wlan %s add' % (vlan_cfg['vlan_id'], vlan_cfg['tagged_wlan']))
        self.cmd('set vlan apply')
        time.sleep(2)

    def set_vlan(self, vlan_id, port, option, tag = None):
        if tag:
            self.cmd('set vlan %s tagged %s %s' % (vlan_id, port, option))
        else:
            self.cmd('set vlan %s native %s %s' % (vlan_id, port, option))
        self.cmd('set vlan apply')

    def clone_vlan(self, vlan_id_clone, vlan_id):
        self.cmd('set vlan %s clone %s' % (vlan_id_clone, vlan_id))
        self.cmd('set vlan apply')

    def swap_vlan(self, vlan_swap, vlan_id):
        self.cmd('set vlan %s swap %s' % (vlan_swap, vlan_id))
        self.cmd('set vlan apply')

    def change_vlan(self, vlan_id, vlan_id_change):
        self.cmd('set vlan %s to %s' % (vlan_id, vlan_id_change))
        self.cmd('set vlan apply')

    def clear_vlan(self, vlan_id):
        self.cmd('set vlan %s clear' % vlan_id)
        self.cmd('set vlan apply')
        time.sleep(2)



    def set_qos_threshold(self, option, value):
        res = self.cmd('set qos %s %s' % (option, value))[-1]
        if res.lower() == 'ok':
            return True
        else: return False

    def get_qos_threshold(self, option):
        res = self.cmd('get qos')
        if option == 'txFailThreshold':
            thr = res[0].split('\t')[0].split()[-1].strip()
        else:
            thr = res[1].split()[-1].strip()
        time.sleep(5)
        return thr

    def set_beacon_interval(self, wlan_if, interval):
        res = self.cmd('set beacon-intval %s %s' % (wlan_if, interval))[-1]
        time.sleep(2)
        if res.lower() == 'ok': return True
        return False

    def get_beacon_interval(self, wlan_if):
        res = self.cmd('get beacon-intval %s' % wlan_if)

        pat = '([0-9]+)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return int(mobj.group(1))
        return None


    def verify_beacon_intval(self, wlan_if):
        self.goto_shell()

        # Get interface number
        pat_interface = "([0-9]+$)"
        num = -1
        wifi_int = ""
        inf_obj = re.search(pat_interface, wlan_if)
        if inf_obj: num = int(inf_obj.group(1))
        else: raise Exception("Wrong wireless interface name")

        # Identify wifi number
        if num >= 0 and num <= 7: wifi_int = "wifi0"
        else: wifi_int = "wifi1"

        aths_cmd = 'athstats -i %s | grep beacon' % wifi_int
        buf = self.cmd(aths_cmd, 0, '#')

        # Get number of beacons
        pat = "^([0-9]+) beacons transmitted"
        for line in buf:
            obj = re.search(pat, line)
            if obj: return int(obj.group(1))

        return None

    def get_channel_list(self, wlan_if):
        """
        Get all channels that AP supports
        """
        buf = self.cmd('set channel %s\n' % wlan_if)
        buf = [x.strip() for x in buf]

        channel_list = []
        channel_pat = "\*[ ]+([0-9]+) \("
        for line in buf:
            mobj = re.search(channel_pat, line)
            if mobj: channel_list.append(mobj.group(1))

        if channel_list: return channel_list
        else: return None

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

    def get_phy_mode(self, wlan_if):
        res = self.cmd('get mode %s' % wlan_if)[0]
        if 'auto' in res:
            return 'auto'
        else:
            return res.split()[-1]

    def add_ip_to_brd_intf(self, br_interface, ip_addr):
        """
        Add an ip address to sub bridge interface (ex: br0.200) at shell
        """
        self.goto_shell()
        cmd = 'ifconfig %s %s' % (br_interface, ip_addr)

        self.tn.read_very_eager()
        self.tn.write(cmd+'\n')
        idx, mo, txt = self.tn.expect(['#'])
        buf = txt.split('\n')
        buf = [line.strip('\r').strip() for line in buf][1:len(buf) - 1]
        self.exit_shell()

        if not buf:
            return True, ''
        for line in buf:
            if 'no such device' in line:
                return False, line

    def remove_vlan(self, vlanid):
        """
        Remove a VLAN out of VLAN table
        """
        vlan_info = self.get_vlan_info()

        for info in vlan_info:
            if info['vlan_id'] == vlanid:
                self.cmd('set vlan %s clear' % info['vlan_id'])
                if info.has_key('native_wlan'):
                    self.cmd('set vlan 1 native wlan %s add' % info['native_wlan'])
                if info.has_key('eth_native_port'):
                    self.cmd('set vlan 1 native port %s add' % info['eth_native_port'])
                self.cmd('set vlan apply')
                time.sleep(2)
                break

    def get_tx_power_at_shell(self, wlan_if):
        """
        Get txpower of a specific wireless interface by using iwconfig command
        """
        self.goto_shell()
        buf = self.cmd('iwconfig %s' % wlan_if, 0, '#')
        pat = 'Tx-Power:([0-9]+) dBm'
        self.exit_shell()

        power = ''
        for line in buf:
            mobj = re.search(pat, line)
            if mobj:
                power = mobj.group(1)
                break
        if not power: raise Exception("Not found txpower")
        return power

    def sh_get_radio_tx_power(self,radio):
        if radio not in [5, 2.4, '5', '2.4']:
            raise('wrong parameter radio:%s'%radio)
        self.goto_shell()
        buf = self.cmd("iwconfig", prompt = "#")
        self.exit_shell()
        radio_str='Frequency:%s'%radio
        for lineNum in range(len(buf)):
            if radio_str in buf[lineNum]:
                power=int(buf[lineNum].split()[4].split(':')[1])
                logging.info('power is %s'%power)
                break
        logging.info('radio %s power is %s'%(radio,power))
        return power

    def set_phy_mode(self, wlan_if, mode):
        res = self.cmd('set mode %s %s' % (wlan_if, mode))[-1]
        if res.lower() == 'ok': return True
        return False

    def set_dfs(self, wlan_if, status, val = ''):
        res = self.cmd('set dfs %s %s %s' % (wlan_if, status, val))[-1]
        time.sleep(1)
        if res.lower() == 'ok': return True
        return False

    def set_query_interval(self, value):
        res = self.cmd('set qos QueryInterval %s' % value)[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_query_interval(self):
        pat = ".* Query Interval:[ ]+([0-9]+).*"
        res = self.cmd('get qos')
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)

        return None

    def set_qos_aging(self, status):
        res = self.cmd('set qos aging %s' % status)[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_qos_aging(self):
        pat = ".* [A|a]ging [M|m]echanism:[ ]+([A-Za-z]+)"
        res = self.cmd('get qos')
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def set_igmp_query(self, version, status, igmp=True):
        if igmp: opt = 'igmp_query'
        else: opt = 'mld_query'

        res = self.cmd('set qos %s %s %s' % (opt, version, status))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_igmp_query(self, igmp=True):
        if igmp: opt = "IGMP"
        else: opt = "MLD"

        query_res = {}
        ver = ''

        pat = "^%s[ ]+General Query (V[0-9]{1}/V[0-9]{1}):[ ]+([A-Za-z]+/[A-Za-z]+)" % opt
        res = self.cmd('get qos')
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                ver = mobj.group(1).split('/')
                for i in range(len(ver)):
                    query_res[ver[i]] = mobj.group(2).split('/')[i]
        return query_res

    def set_system(self, value, wlan_if = ""):
        res = self.cmd('set system %s %s' % (wlan_if, value))
        ok = True
        if res[-1].lower() != 'ok':
            res = self.cmd('set system %s' % value)[-1]
            if res.lower() !=  'ok': ok = False
        time.sleep(1)

        if not ok: return False
        return True

    def get_system(self, wlan_if = ""):
        res = self.cmd('get system %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get system')
        return res[0]

    def set_ap_bridge(self, wlan_if, status):
        res = self.cmd('set ap-bridge %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_ap_bridge(self, wlan_if):
        res = self.cmd('get ap-bridge %s' % wlan_if)
        pat = "[\w]+: ([A-Za-z]+)"
        status = ""
        time.sleep(1)
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                status = mobj.group(1).lower()
                break
        return status

    def set_auto_prov(self, status):
        res = self.cmd('set autoprov %s' % status)[-1]
        time.sleep(1)
        if res.lower() == 'ok': return True
        return False

    def get_auto_prov(self):
        res = self.cmd('get autoprov')
        pat = '([A-Za-z]+able[d]?)'

        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def get_counter_measure(self, wlan_if = ""):
        res = self.cmd('get countermeasure %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get countermeasure')

        if 'not active' in res[0]: return 'disable'
        return 'enable'

    def set_counter_measure(self, status, wlan_if = ""):
        res = self.cmd('set countermeasure %s %s' % (wlan_if, status))
        ok = True
        if res[-1].lower() != 'ok':
            res = self.cmd('set countermeasure %s' % status)[-1]
            if res.lower() != 'ok': ok = False
        if not ok: return False
        else: return True

    def set_country_ie(self, wlan_if, status):
        res = self.cmd('set countryie %s %s' % (wlan_if, status))[-1]
        time.sleep(2)
        if res.lower() != 'ok':
            res = self.cmd('set countryie %s' % status)[-1]
            if res.lower() != 'ok':
                return False
        return True

    def get_country_ie(self, wlan_if):
        res = self.cmd('get countryie %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get countryie')
        res = res[0].split()[-1].lower()

        time.sleep(5)
        if res == 'on':
            return 'enable'
        else:
            return 'disable'

    def get_cwmin_adapt(self, wlan_if = ""):
        res = self.cmd('get cwmin-adapt %s' % wlan_if)
        pat = '([A-Za-z]+able[d]?)'

        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_cwmin_adapt(self, status, wlan_if = ""):
        res = self.cmd('set cwmin-adapt %s %s' % (wlan_if, status))
        if res[-1].lower() != 'ok':
            return False
        return True

    def set_cw_mode(self, wlan_if, mode):
        res = self.cmd('set cwmode %s %s' % (wlan_if, mode))[-1]

        if res.lower() != 'ok':
            res = self.cmd('set cwmode %s' % mode)[-1]
            if res.lower() != 'ok':
                return False
        return True

    def get_cw_mode(self, wlan_if):
        res = self.cmd('get cwmode %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get cwmode')

        pat = ".* \(([0-9]+)\)$"
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def set_dtim_period(self, wlan_if, value):
        res = self.cmd('set dtim-period %s %s' % (wlan_if, value))[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_dtim_period(self, wlan_if):
        res = self.cmd('get dtim-period %s' % wlan_if)

        pat = '([0-9]+)$'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def set_invisible(self, wlan_if, status):
        res = self.cmd('set invisible %s %s' % (wlan_if, status))

        if 'ok' in res[-1].lower():
            return True
        return False

    def get_invisible(self, wlan_if):

        res = self.cmd('get invisible %s' % wlan_if)
        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_rx_chain_mask(self, wlan_if, value):
        res = self.cmd('set rxchainmask %s %s' % (wlan_if, value))
        time.sleep(5)
        if not 'ok' in res[-1].lower():
            res = self.cmd('set rxchainmask %s' % value)
            if not 'ok' in res[-1].lower():
                return False
        return True

    def get_rx_chain_mask(self, wlan_if):
        res = self.cmd('get rxchainmask %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get rxchainmask')
        time.sleep(5)
        pat = ".* ([0-9]+).*"
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                return mobj.group(1)
        return None

    def set_tx_chain_mask(self, wlan_if, value):
        res = self.cmd('set txchainmask %s %s' % (wlan_if, value))
        if not 'ok' in res[-1].lower():
            res = self.cmd('set txchainmask %s' % value)
            if not 'ok' in res[-1].lower():
                return False
        return True

    def get_tx_chain_mask(self, wlan_if):
        res = self.cmd('get txchainmask %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get txchainmask')

        time.sleep(5)
        pat = ".* ([0-9]+).*"
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                return mobj.group(1)
        return None

    def set_legacy_tx_chain_mask(self, wlan_if, value):
        res = self.cmd('set legacytxchainmask %s %s' % (wlan_if, value))
        time.sleep(5)
        if not 'ok' in res[-1].lower():
            res = self.cmd('set legacytxchainmask %s' % value)
            if not 'ok' in res[-1].lower():
                return False
        return True

    def get_legacy_tx_chain_mask(self, wlan_if):
        res = self.cmd('get legacytxchainmask %s' % wlan_if)
        if res[-1].lower() != 'ok':
            res = self.cmd('get legacytxchainmask')

        time.sleep(5)
        pat = ".* ([0-9]+).*"
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                return mobj.group(1)
        return None

    def get_event(self, wlan_if):
        res = self.cmd('get event %s' % wlan_if)
        res = [line.strip() for line in res]
        event = {}

        for line in res:
            if line.lower().startswith('association'):
                event['assoc'] = line.split()[1:]
            elif line.lower().startswith('auth'):
                event['auth'] = line.split()[-1]
            elif line.lower().startswith('other bss'):
                event['obss'] = line.split()[-2:]
            elif line.lower().startswith('video'):
                event['video_drop'] = line.split()[-2:]
            elif line.lower().startswith('voice'):
                event['voice_drop'] = line.split()[-2:]
            elif line.lower().startswith('rssi'):
                event['rssi'] = line.split()[1:]
            elif line.lower().startswith('crc'):
                event['crc'] = line.split()[1:]
            elif line.lower().startswith('channel'):
                event['clcs'] = line.split()[-1]

        time.sleep(2)
        return event

    def set_event(self, wlan_if, option, period, threshold = ""):
        res = self.cmd('set event %s %s %s %s' % (wlan_if, option, threshold, period))[-1]
        if res.lower() != 'ok': return False
        return True

    def set_ssid_supress(self, wlan_if, status):
        res = self.cmd('set ssid-suppress %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_ssid_suppress(self, wlan_if):
        res = self.cmd('get ssid-suppress %s' % wlan_if)

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_rts_thr(self, wlan_if, value):
        res = self.cmd('set rts-thr %s %s' % (wlan_if, value))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_rts_thr(self, wlan_if):
        res = self.cmd('get rts-thr %s' % wlan_if)

        pat = ".*: ([\w ]+)$"
        expect = ""
        for line in res:
            mobj = re.search(pat, line)
            if mobj: expect = mobj.group(1)

        if 'disable' in expect: return 'disable'
        new_pat = '([0-9]+)'
        mobj = re.search(new_pat, expect)
        if mobj: return mobj.group(1)
        return None

    def set_rescan_ap(self, wlan_if, rescan_cfg):
        if rescan_cfg.has_key('exp'):
            self.cmd('set rescan %s exp %s' % (wlan_if, rescan_cfg['exp']))
        if rescan_cfg.has_key('min'):
            self.cmd('set rescan %s min %s' % (wlan_if, rescan_cfg['min']))
        if rescan_cfg.has_key('max'):
            self.cmd('set rescan %s max %s' % (wlan_if, rescan_cfg['max']))
        time.sleep(2)

    def get_rescan_ap(self, wlan_if):
        res = self.cmd('get rescan %s' % wlan_if)

        if res[-1].lower() != 'ok':
            return -1
        res = [x.strip('\t') for x in res]
        rescan_cfg = {}
        for line in res:
            if line.lower().startswith('minimum'):
                rescan_cfg['min'] = line.split(':')[-1].strip()
            if line.lower().startswith('maximum'):
                rescan_cfg['max'] = line.split(':')[-1].strip()
            if line.lower().startswith('exponential'):
                rescan_cfg['exp'] = line.split(':')[-1].strip()

        return rescan_cfg

    def set_vo_detect(self, wlan_if, status):
        res = self.cmd('set vodetect %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_vo_detect(self, wlan_if):
        res = self.cmd('get vodetect %s' % wlan_if)

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_wds_mode(self, wlan_if, status):
        res = self.cmd('set wds-mode %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_wds_mode(self, wlan_if):
        res = self.cmd('get wds-mode %s' % wlan_if)
        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_dvlan(self, wlan_if, status):
        res = self.cmd('set dvlan %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_dvlan(self, wlan_if):
        res = self.cmd('get dvlan %s' % wlan_if)

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def get_wlan_text(self, wlan_if):
        res = self.cmd('get wlantext %s' % wlan_if)
        pat = "\'([\w]+)\'"
        time.sleep(2)
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                return mobj.group(1)
        return

    def set_wlan_text(self, wlan_if, text):
        res = self.cmd('set wlantext %s %s' % (wlan_if, text))[-1]
        if res.lower() == 'ok': return True
        return False

    def set_wmm(self, wlan_if, status):
        self.cmd('set wmm %s %s' % (wlan_if, status))

    def get_wmm(self, wlan_if):
        res = self.cmd('get wmm %s' % wlan_if)[0].split(':')[-1].strip().lower()
        if res == "enabled": return 'enable'
        else: return 'disable'

    def set_class2_mq_prio(self, wlan_if, voice, video, data, bk):
        cmd = 'set class2mqprio %s %s %s %s %s' % (wlan_if, bk, data, video, voice)
        res = self.cmd(cmd)[-1]
        if res.lower() != "ok":
            cmd = 'set class2mqprio %s %s %s %s %s' % (wlan_if, voice, video, data, bk)
            self.cmd(cmd)
        time.sleep(5)

    def get_class_2_mq_prio(self, wlan_if):
        res = self.cmd('get class2mqprio %s' % wlan_if)
        res = [line.strip() for line in res]
        pat = "[C|c]lass ([A-Za-z]+).*:"
        class1mqprio_info = {}
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                if mobj.group(1).lower().startswith('vo'):
                    class1mqprio_info['voice'] = line.split(':')[-1].strip()
                elif mobj.group(1).lower().startswith('vi'):
                    class1mqprio_info['video'] = line.split(':')[-1].strip()
                elif mobj.group(1).lower().startswith('be') or mobj.group(1).lower().startswith('da'):
                    class1mqprio_info['data'] = line.split(':')[-1].strip()
                elif mobj.group(1).lower().startswith('bk') or mobj.group(1).lower().startswith('ba'):
                    class1mqprio_info['bk'] = line.split(':')[-1].strip()
        time.sleep(5)
        return class1mqprio_info

    def get_frag_thr(self, wlan_if):
        res = self.cmd('get frag-thr %s' % wlan_if)

        pat = ".*: ([\w ]+)$"
        expect = ""
        for line in res:
            mobj = re.search(pat, line)
            if mobj: expect = mobj.group(1)

        if 'disable' in expect: return 'disable'
        new_pat = '([0-9]+)'
        mobj = re.search(new_pat, expect)
        if mobj: return mobj.group(1)
        return None

    def set_frag_thr(self, wlan_if, value):
        res = self.cmd('set frag-thr %s %s' % (wlan_if, value))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_fixed_rate(self, wlan_if):
        res = self.cmd('get fixed-rate %s' % wlan_if)[0].split(',')

        info = {}
        info['mode'] = res[0].split()[-2]
        if len(res) > 1:
            pat = ".* ([\w]+Mb).*"
            for line in res:
                mobj = re.search(pat, line)
                if mobj:
                    info['rate'] = mobj.group(1)
                    break
        return info

    def set_fixed_rate(self, wlan_if, rate):
        self.cmd('set fixed-rate %s %s legacy' % (wlan_if, rate))
        time.sleep(1)

    def set_11h_status(self, wlan_if, status):
        res = self.cmd('set 802.11-h %s %s' % (wlan_if, status))
        time.sleep(5)
        if 'ok' in res[-1].lower():
            return True
        return False

    def get_11h_status(self, wlan_if):
        res = self.cmd('get 802.11-h %s' % wlan_if)[0].split()[-1].lower()
        time.sleep(5)
        if res == 'on': return 'enable'
        else: return 'disable'

    def set_max_aid(self, wlan_if, value):
        res = self.cmd('set max-aid %s %s' % (wlan_if, value))
        time.sleep(5)
        if 'ok' in res[-1].lower():
            return True
        return False

    def get_max_aid(self, wlan_if):
        res = self.cmd('get max-aid %s' % wlan_if)
        time.sleep(5)
        pat = ".* ([0-9]+).*"
        for line in res:
            mobj = re.search(pat, line)
            if mobj:
                return mobj.group(1)
        return None

    def set_min_rate(self, wlan_if, value):
        res = self.cmd('set minrate %s %s' % (wlan_if, value))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_min_rate(self, wlan_if):
        res = self.cmd('get minrate %s' % wlan_if)

        pat = "([0-9]+)"
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return

    def get_prot_mode(self, wlan_if):
        res = self.cmd('get prot-mode %s' % wlan_if)

        pat = ".*: ([\w-]+)"
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def set_prot_mode(self, wlan_if, mode):
        res = self.cmd('set prot-mode %s %s' % (wlan_if, mode))[-1]
        if res.lower() == 'ok': return True
        return False

    def set_band_steering_thr(self, wlan_if, rssi):
        res = self.cmd('set band-steering %s %s' % (wlan_if, rssi))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_band_steering_thr(self, wlan_if):
        res = self.cmd('get band-steering %s' % wlan_if)

        pat = "RSSI [A-Za-z]+: ([0-9]+)"
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def get_mqstats_def(self, wlan_if):
        """
        This function gets media queues statistic on the AP.
        - Output: return a dictionany, in there key of this dictionary is the mac address of the station,
        value of these key is another dictionary that includes value of media queues
        """
        res = self.cmd('get mqstats %s def' % wlan_if)
        res = [x.lstrip(' ').rstrip(' ') for x in res if not x.startswith('-')][:-1]

        col_name = res[1].split()
        for item in res:
            if item.startswith('Qued'):
                res.remove(item)

        queue_deflt_info = {}
        for i in range(len(res)):
            if res[i].startswith('STA'):
                continue
            if not 'deflt' in res[i]:
                continue

            # Get value on each column for each media type and save it to a dictionary
            list_tmp = [x.lstrip(' ').rstrip(' ') for x in res[i].split('  ') if x][1:]
            l = 0
            queue = {}
            for name in col_name:
                queue[name] = list_tmp[l]
                l = l+1
            queue_deflt_info = queue.copy()

            time.sleep(2)
            return queue_deflt_info

    def set_mq(self, wlan_if, **args):

        if args.has_key('credit'):
            res = self.cmd('set mq %s credit %s %s' % (wlan_if,
                                                       args['credit']['gclient'],
                                                       args['credit']['bclient']))[-1]
        elif args.has_key('pscredit'):
            res = self.cmd('set mq %s pscredit %s' % (wlan_if, args['pscredit']))[-1]
        elif args.has_key('qtime'):
            res = self.cmd('set mq %s qtime %s %s %s %s' % (wlan_if,
                                                            args['qtime']['voice'],
                                                            args['qtime']['video'],
                                                            args['qtime']['data'],
                                                            args['qtime']['background']))[-1]
        elif args.has_key('maxpkts'):
            res = self.cmd('set mq %s maxpkts %s %s %s %s' % (wlan_if,
                                                              args['maxpkts']['voice'],
                                                              args['maxpkts']['video'],
                                                              args['maxpkts']['data'],
                                                              args['maxpkts']['background']))[-1]

        if res.lower() == 'ok': return True
        return False

    def get_mq(self, wlan_if):
        res = self.cmd('get mq %s' % wlan_if)

        ps = 'Power-Save .*: ([0-9]+)'
        bsta = 'B-Station[ ]+: ([0-9]+)'
        gsta = 'G-Station[ ]+: ([0-9]+)'
        qtime = ".* [Q|q]ueue [T|t]ime"
        maxpkts = "Max Pkts .*"

        mq_info = {}
        mq_info['credit'] = {}
        mq_info['qtime'] = {}
        mq_info['maxpkts'] = {}

        for line in res:
            mo = re.search(ps, line)
            if mo: mq_info['pscredit'] = mo.group(1)

            mo = re.search(bsta, line)
            if mo: mq_info['credit']['bclient'] = mo.group(1)

            mo = re.search(gsta, line)
            if mo: mq_info['credit']['gclient'] = mo.group(1)

            mo = re.search(maxpkts, line)
            if mo:
                idx = res.index(line)
                media = ['voice', 'video', 'data', 'background']
                print idx
                #print media.index(i)
                for i in media:
                    mq_info['maxpkts'][i] = res[idx+media.index(i)+1].split(':')[-1].strip()

            mo = re.search(qtime, line)
            if mo:
                idx = res.index(line)
                media = ['voice', 'video', 'data', 'background']
                for i in media:
                    mq_info['qtime'][i] = res[idx+media.index(i)+1].split(':')[-1].strip()

        return mq_info

    def set_auto_cfg(self, wlan_if, **args):

        # Enable autoconfig
        self.cmd('set autoconfig %s enable' % wlan_if)

        if args.has_key('nasid_sel'):
            self.cmd('set autoconfig %s nasid-sel %s' % (wlan_if, args['nasid_sel']))
        if args.has_key('ssid_sel'):
            self.cmd('set autoconfig %s ssid-sel %s' % (wlan_if, args['ssid_sel']))
        if args.has_key('ssid_prefix'):
            self.cmd('set autoconfig %s ssid-prefix %s' % (wlan_if, args['ssid_prefix']))
        if args.has_key('weplen'):
            self.cmd('set autoconfig %s weplen %s' % (wlan_if, args['weplen']))
        if args.has_key('wpalen'):
            self.cmd('set autoconfig %s wpalen %s' % (wlan_if, args['wpalen']))

        time.sleep(1)

    def get_auto_cfg(self, wlan_if):
        res = self.cmd('get autoconfig %s' % wlan_if)
        wlanifname = self.wlan_if_to_name(wlan_if)

        atcf_wlan = ""
        for line in res:
            if wlanifname in line:
                atcf_wlan = line
                break
        if not atcf_wlan:
            raise Exception("Can not find %s in autoconfig info" % wlan_if)

        if 'disable' in atcf_wlan:
            return {}
        tmp = atcf_wlan.split(':')[-1].split()
        atcf = {}
        atcf['nasid_sel'] = tmp[1]
        atcf['ssid_sel'] = tmp[2]
        atcf['ssid_prefix'] = tmp[3]
        atcf['weplen'] = tmp[4]
        atcf['wpalen'] = tmp[5]

        return atcf

    def set_distance(self, wlan_if, value):
        res = self.cmd('set distance %s %s' % (wlan_if, value))
        if res[-1].lower() == 'ok': return True
        return False

    def get_distance(self, wlan_if):
        res = self.cmd('get distance %s' % wlan_if)

        pat = "([0-9]+)"
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def set_zaxis(self, wlan_if, status):
        res = self.cmd('set zaxis %s %s' % (wlan_if, status))[-1]
        if res.lower() == 'ok': return True
        return False

    def get_zaxis(self, wlan_if):
        res = self.cmd('get zaxis %s' % wlan_if)[0].split()[-1].lower()
        if res == 'on': return 'enable'
        return 'disable'

    def get_bonjour(self):
        res = self.cmd('get bonjour')

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1).lower()
        return None

    def set_bonjour(self, status):
        res = self.cmd("set bonjour %s" % (status))[-1]
        if res.lower() == 'ok': return True
        return False

    def set_dev_location(self, value):
        res = self.cmd('set device-location %s' % value)[-1].lower()
        if res == 'ok': return True
        else: return False

    def get_dev_location(self):
        res = self.cmd('get device-location')

        pat = ".*:[ ]+\'(.*)\'"
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def set_device_name(self, value):
        res = self.cmd('set device-name %s' % value)[-1].lower()
        if res == 'ok': return True
        else: return False

    def set_dhcpc(self, id):
        res = self.cmd('set dhcpc option60 %s' % id)
        time.sleep(3)
        if res[-1].lower() == 'ok': return True
        return False

    def get_dhcpc(self):
        res = self.cmd('get dhcpc')[0].split()[-1]
        return res

    def get_dns(self):
        res = self.cmd('get dns')[:-1]
        dns = {'ip_addr1':'', 'ip_addr2':''}

        none_pat = "<None>"
        for line in res:
            mobj = re.search(none_pat, line)
            if mobj: return dns
        dns_pat = '[a-zA-Z]+ [0-9]+ : ([0-9.]+)$'

        dns_list = []
        for line in res:
            mobj = re.search(dns_pat, line)
            if mobj: dns_list.append(mobj.group(1))

        if not dns_list: return dns
        if len(dns_list) == 2:
            dns = {'ip_addr1':dns_list[0], 'ip_addr2':dns_list[1]}
        else: dns = {'ip_addr1':dns_list[0], 'ip_addr2':''}

        time.sleep(1)
        return dns

    def set_dns(self, ip_addr1, ip_addr2=""):
        res = self.cmd('set dns %s %s' % (ip_addr1, ip_addr2))
        time.sleep(2)

        return True if res[-1].lower() == 'ok' else False

    def get_eth_mon(self):
        res = self.cmd('get eth-mon')
        pat = ".* ([0-9]+).*"
        for line in res:
            mobj = re.match(pat, line)
            if mobj:
                return mobj.group(1)
        return None

    def set_eth_mon(self, value):
        res = self.cmd('set eth-mon %s' % value)[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_http(self):
        res = self.cmd('get http')
        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    def set_http(self, status):
        res = self.cmd('set http %s' % status)[-1]
        if res.lower() == 'ok': return True
        return False

    def get_https(self):
        res = self.cmd('get https')[0]
        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    def set_https(self, status):
        res = self.cmd('set https %s' % status)[-1]
        if res.lower() == 'ok': return True
        return False

    def set_internal_heater(self, status):
        res = self.cmd('set internal_heater %s' % status)[-1]
        if res.lower() == 'ok': return True
        return False

    def get_internal_heater(self):
        res = self.cmd('get internal_heater')

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    def get_snmp(self):
        res = self.cmd("get snmp")
        snmp_cfg = {}
        for line in res:
            if 'manager' in line:
                snmp_cfg['manager'] = line.split(':')[-1].strip()
            if 'ro community' in line:
                snmp_cfg['ro_community'] = line.split(':')[-1].strip()
            if 'rw community' in line:
                snmp_cfg['rw_community'] = line.split(':')[-1].strip()

        time.sleep(1)
        return snmp_cfg

    def set_snmp(self, snmp_cfg):
        if snmp_cfg.has_key('manager'):
             self.cmd('set snmp manager %s' % snmp_cfg['manager'])
        if snmp_cfg.has_key('ro_community'):
            self.cmd('set snmp community ro %s' % snmp_cfg['ro_community'])
        if snmp_cfg.has_key('rw_community'):
            self.cmd('set snmp community rw %s' % snmp_cfg['rw_community'])
        time.sleep(1)

    def get_snmp_acl(self):
        res = self.cmd('get snmp-acl')
        snmp_acl_info = {}
        if 'disabled' in res[0]:
            snmp_acl_info['status'] = 'disable'
            return snmp_acl_info

        res = [x.strip() for x in res]
        acl_pat = '[0-9]+: ([0-9.]+)$'
        acl_entry = []
        for line in res:
            mobj = re.search(acl_pat, line)
            if mobj: acl_entry.append(mobj.group(1))
        snmp_acl_info['acl_entry'] = acl_entry
        snmp_acl_info['status'] = 'enable'

        return snmp_acl_info

    def set_snmp_acl(self, snmp_acl_cfg):
        if snmp_acl_cfg.has_key('status'):
            self.cmd('set snmp-acl %s' % snmp_acl_cfg['status'])[-1].lower()

        if snmp_acl_cfg.has_key('add_entry'):
            if snmp_acl_cfg['add_entry']:
                for entry in snmp_acl_cfg['acl_entry']:
                    self.cmd('set snmp-acl add %s' % entry)
            else:
                for entry in snmp_acl_cfg['acl_entry']:
                    self.cmd('set snmp-acl del %s' % entry)

    def get_syslog_info(self):
        res = self.cmd('get syslog info')
        syslog_info = {}
        tmp = res[0].split()[-1]
        if tmp == 'enabled': syslog_info['status'] = 'enable'
        else: syslog_info['status'] = 'disable'

        for line in res:
            if 'ip' in line.lower():
                syslog_info['server_ip'] = line.split(':')[-1].strip()
            if 'port' in line.lower():
                syslog_info['server_port'] = line.split(':')[-1].strip()
            if 'network' in line.lower():
                syslog_info['level_network'] = line.split(':')[-1].strip()
            if 'local' in line.lower():
                syslog_info['level_local'] = line.split(':')[-1].strip()

        time.sleep(1)
        return syslog_info

    def set_syslog_info(self, syslog_cfg):
        if syslog_cfg.has_key('status'):
            self.cmd('set syslog %s' % syslog_cfg['status'])
        if syslog_cfg.has_key('server_ip'):
            self.cmd('set syslog ipv4 %s' % syslog_cfg['server_ip'])
        if syslog_cfg.has_key('server_port'):
            self.cmd('set syslog port %s' % syslog_cfg['server_port'])
        if syslog_cfg.has_key('level_local'):
            self.cmd('set syslog level local %s' % syslog_cfg['level_local'])
        if syslog_cfg.has_key('level_network'):
            self.cmd('set syslog level network %s' % syslog_cfg['level_network'])

        time.sleep(2)

    def set_thermo(self, value):
        res = self.cmd('set thermo %s' % value)[-1]
        if res.lower() == 'ok': return True
        return False

    def get_thermo(self):
        res = self.cmd('get thermo')

        pat = '([0-9]+)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def set_tr069(self, tr069_cfg):
        ok = True
        if tr069_cfg.has_key('url'):
            res = self.cmd('set tr069 url %s' % tr069_cfg['url'])
        elif tr069_cfg.has_key('interval'):
            res = self.cmd('set tr069 interval %s' % tr069_cfg['interval'])
        elif tr069_cfg.has_key('acs_user'):
            res = self.cmd('set tr069 user %s' % tr069_cfg['acs_user'])
        elif tr069_cfg.has_key('acs_pass'):
            res = self.cmd('set tr069 password %s' % tr069_cfg['acs_pass'])
        elif tr069_cfg.has_key('cpe_user'):
            res = self.cmd('set tr069 digest-user %s' % tr069_cfg['cpe_user'])
        elif tr069_cfg.has_key('cpe_pass'):
            res = self.cmd('set tr069 digest-password %s' % tr069_cfg['cpe_pass'])

        if res[-1].lower() == 'ok': return True
        return False

    def get_tr069(self):
        res = self.cmd('get tr069')

        tr069 = {}
        url = ".* URL[ ]+: (.*)$"
        intval = ".* interval[ ]+: ([0-9]+)"
        acs_user = "^CPE.* username [ ]+: (.*)"
        acs_pass = "^CPE.* password [ ]+: (.*)"
        cpe_user = "^ACS.* username [ ]+: (.*)"
        cpe_pass = "^ACS.* password [ ]+: (.*)"

        for line in res:
            mo = re.search(url, line)
            if mo: tr069['url'] = mo.group(1)

            mo = re.search(intval, line)
            if mo: tr069['interval'] = mo.group(1)

            mo = re.search(acs_user, line)
            if mo: tr069['acs_user'] = mo.group(1)

            mo = re.search(acs_pass, line)
            if mo: tr069['acs_pass'] = mo.group(1)

            mo = re.search(cpe_user, line)
            if mo: tr069['cpe_user'] = mo.group(1)

            mo = re.search(cpe_pass, line)
            if mo: tr069['cpe_pass'] = mo.group(1)
            time.sleep(1)

        return tr069

    def set_model_display(self, string):
        res = self.cmd('set model-display %s' % string)[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_model_display(self):
        res = self.cmd('get model-display')

        pat = '.* : (.*)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def set_orientation(self, value):
        res = self.cmd('set orientation %s' % value)[-1]
        if res.lower() == 'ok': return True
        return False

    def get_orientation(self):
        res = self.cmd('get orientation')

        pat = '([0-9]+)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1)
        return None

    def get_ntp(self):
        res = self.cmd("get ntp")
        ntp_info = {'gmt_time': '', 'active_server': '', 'backup_server': ''}
        ntp_info['gmt_time'] = res[0].split("time   :")[-1].strip()
        ntp_info['active_server'] = res[1].split(":")[-1].strip()
        ntp_info['backup_server'] = res[2].split(":")[-1].strip()

        time.sleep(2)
        return ntp_info

    def set_ntp(self, option, server):
        if option != "update":
            self.cmd("set ntp server %s" % server)
        else: self.cmd("set ntp update")
        time.sleep(1)

    def get_ssh(self):
        res = self.cmd("get ssh")
        time.sleep(1)

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    def set_ssh(self, status):
        self.cmd("set ssh %s" % status)
        time.sleep(1)

    def set_poe_out(self, status):
        res = self.cmd('set poe_out %s' % status)[-1]
        if res.lower() == 'ok': return True
        return False

    def get_poe_out(self):
        res = self.cmd('get poe_out')

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    def set_remote_mgmt(self, option):
        self.cmd('set remote-mgmt %s' % option)
        time.sleep(1)

    def get_remote_mgmt(self, ):
        res = self.cmd('get remote-mgmt')[:-1]
        res = [line.strip() for line in res]
        info = {}
        info['remote_mgmt'] = res[0].split(':')[-1].lower().strip()
        res = res[1:]
        for line in res:
            info['%s' % line.split(':')[0].lower()] = line.split(':')[-1].strip()

        time.sleep(1)
        return info

    def set_aerosct(self, status):
        res = self.cmd('set aerosct %s' % status)[-1]
        if res.lower() == 'ok': return True
        else: return False

    def get_aerosct(self):
        res = self.cmd('get aerosct')

        pat = '([A-Za-z]+able[d]?)'
        for line in res:
            mo = re.search(pat, line)
            if mo: return mo.group(1).lower()
        return None

    #### ACL Group
    def get_acl(self, wlan_if):
        res = self.cmd("get acl %s" % wlan_if)[:-1]
        acl_entry = []
        acl_info = {}
        acl_pat = "[0-9]+: ([a-fA-F0-9:]+)$"
        for line in res:
            if 'white list' in line: acl_info['action'] = 'allow'
            if 'black list' in line: acl_info['action'] = 'deny'

            mobj = re.search(acl_pat, line)
            if mobj:
                acl_entry.append(mobj.group(1))

        acl_info['acl_entry'] = acl_entry
        return acl_info

    def set_acl(self, wlan_if, action = "", entry = []):
        """
        - action: "disable", "allow", "deny"
        """
        if action:
            self.cmd("set acl %s mac %s" % (wlan_if, action))
        if entry:
            for e in entry:
                self.cmd('set acl %s mac add %s' % (wlan_if, e))
                time.sleep(1)

    def get_noise_level(self, wlan_if):
        """
        Get noise level of a specific wireless interface by using iwconfig command
        """
        self.goto_shell()
        buf = self.cmd('iwconfig %s' % wlan_if, 0, '#')

        pat = 'Noise level=(-?[0-9]+) dBm'

        noise_level = ''
        for line in buf:
            mobj = re.search(pat, line)
            if mobj:
                noise_level = mobj.group(1)
                break
        self.exit_shell()
        return noise_level

    def get_netstats_info(self):
        """
        Get info after run command 'get netstats'
        Below is an example of result:
        {'receive': {'br0': {'FIFO': '0',
                     'Frame': '0',
                     'Interface': 'br0',
                     'Mcast': '0',
                     'ZIP': '0',
                     'bytes': '2612231',
                     'drop': '0',
                     'errors': '0',
                     'packets': '79883'},
             'wlan0': {'FIFO': '0',
                       'Frame': '0',
                       'Interface': 'wlan0',
                       'Mcast': '0',
                       'ZIP': '0',
                       'bytes': '3699034',
                       'drop': '0',
                       'errors': '0',
                       'packets': '79427'}},
         'transmit': {'br0': {'Carrier': '0',
                      'Collide': '0',
                      'FIFO': '0',
                      'Interface': 'br0',
                      'ZIP': '0',
                      'bytes': '530074',
                      'drop': '0',
                      'errors': '0',
                      'packets': '2407'},
              'wlan0': {'Carrier': '0',
                        'Collide': '0',
                        'FIFO': '0',
                        'Interface': 'wlan0',
                        'ZIP': '0',
                        'bytes': '109836',
                        'drop': '0',
                        'errors': '0',
                        'packets': '1437'}}}
        """
        result = {}
        receive_result = {}
        transmit_result = {}

        flag_transmit = False
        netstats_result = self.cmd("get netstats")

        len_of_list = 1
        list_result = []
        for element in netstats_result:
            list_info = element.split()
            if re.search('Transmit', element):
                flag_transmit = True

            if not re.search('<--', element) and len(list_info) >= len_of_list :
                if re.search('Interface', element):
                    list_result = list_info
                    len_of_list = len(list_info)
                else:
                    if flag_transmit == False:
                        dict_receive = {}
                        for i in range(len(list_result)):
                            dict_receive[list_result[i]] = list_info[i]
                        receive_result[dict_receive['Interface']] = dict_receive
                    else:
                        dict_transmit = {}
                        for i in range(len(list_result)):
                            dict_transmit[list_result[i]] = list_info[i]
                        transmit_result[dict_transmit['Interface']] = dict_transmit

        result['receive'] = receive_result
        result['transmit'] = transmit_result
        return result


    def get_data_collection(self):
        try:
            list_res = self.cmd("get dc")
            stats_interval = list_res[1].split(", ")[0].split(" ")[-1]
            stats_interval_bin = list_res[1].split(", ")[1].split(" ")[1]
        except:
            raise Exception('can not get data collection')
        res = dict(X_001392_STATS_INTERVAL = stats_interval, X_001392_STATS_INTERVAL_BINS = stats_interval_bin)
        return res

    def get_up_time(self):
        res = self.cmd("get uptime")
        uptime_str = res[0].split(": ")[-1]
        # change to second
        uptime = get_uptime(uptime_str) ### phannt: in Ratutils under AP Standardlone
        return uptime

    def get_station_stats_info(self, wlan_id):
        dict_regex = dict(
            mac_address = '[0-9a-fA-F:]{17}',
            line_1 = '\trx_data_frm (?P<trx_data_frm>\d+) rx_mgt_frm (?P<rx_mgt_frm>\d+) rx_bytes (?P<rx_bytes>\d+) rx_dup (?P<rx_dup>\d+)',
            line_2 = '\ttx_data_frm (?P<ttx_data_frm>\d+) tx_mgmt_frm (?P<tx_mgmt_frm>\d+) tx_bytes (?P<tx_bytes>\d+)',
            line_3 = '\tgood_tx_frms (?P<tgood_tx_frms>\d+) good_rx_frms (?P<good_rx_frms>\d+) tx_retries (?P<tx_retries>\d+)',
            line_4 = '\ttx_rate (?P<ttx_rate>\d+) tx_kbps (?P<tx_kbps>\d+) rx_crc_errs (?P<rx_crc_errs>\d+)',
            line_5 = '\ttx_per (?P<ttx_per>\d+) tx_rssi (?P<tx_rssi>\d+)'
        )

        dict_info = dict(
            line_1 = ['trx_data_frm', 'rx_mgt_frm', 'rx_bytes', 'rx_dup'],
            line_2 = ['ttx_data_frm', 'tx_mgmt_frm', 'tx_bytes'],
            line_3 = ['tgood_tx_frms', 'good_rx_frms', 'tx_retries'],
            line_4 = ['ttx_rate', 'tx_kbps', 'rx_crc_errs'],
            line_5 = ['ttx_per', 'tx_rssi'],
        )

        list_info = self.cmd('get station %s stats all' % wlan_id)
        str_info = ' '.join(str(i) for i in list_info)
        list_mac_addr = []
        result = {}
        for info in dict_regex.keys():
            list_tuple_result = re.findall(dict_regex[info], str_info)
            if info == 'mac_address':
                list_mac_addr = list_tuple_result

            index_for_mac = 0
            for tuple_result in list_tuple_result:
                if info == 'mac_address':
                    result[tuple_result] = {}
                else:
                    index = 0
                    temp = {}
                    for ele in tuple_result:
                        temp[dict_info[info][index]] = ele
                        index += 1
                    result[list_mac_addr[index_for_mac]].update(temp)
                    index_for_mac += 1
        return result

    def fw_update_custom(self):
        """
        """
        update_proces = self.cmd('fw update custom', 10, 'rkscli')
        for step in update_proces:
            if 'Completed' in step:
                logging.info('Custom file loading completed')
                return
            if 'No update' in step:
                logging.info('No update for the custom')
                return
        raise '[Upgrade error] %s' % update_proces

    def get_custom_file_list(self):
        """
        """
        self.goto_shell()
        return self.cmd('ls /writable/custom/ -1', 0, '#')
        self.exit_shell()

    def remove_all_custom_file(self):
        """
        """
        self.goto_shell()
        self.cmd('rm /writable/custom/*.*', 0, '#')
        self.exit_shell()


    def get_perclient_rate_limit(self):
        """
        """

        self.goto_shell()
        self.cmd("rm /tmp/shaper_dbg.txt", 0, "#")
        self.cmd('eve_cli shaper dump', 0, '#')
        res = self.cmd("cat /tmp/shaper_dbg.txt", 0, "#")
        self.exit_shell()
        return res

    def get_radar_threshold(self):
        # result is ['Radar Trigger Threshold: 2', 'OK']
        res = self.cmd("get radarthreshold")
        return res[0].split(':')[-1].strip()

    def set_radar_threshold(self, value):
        self.cmd("set radarthreshold %s" % value)

    def get_rfmd_option(self):
        # result is ['RFMD mode is enable', 'OK']
        res = self.cmd("get rfmd")
        ser = re.search('enable', res[0])
        if ser and 'enable' == ser.group(0).lower():
            return True
        else:
            return False

    def set_rfmd_option(self, option=True):
        if option == True:
            self.cmd("set rfmd enable")
        else:
            self.cmd("set rfmd disable")

    def show_radar_event_table(self):
        #$show radar event table maintained at a AP; age of each entry is 10seconds
        self.goto_shell()
        res = self.cmd("rfmd -d", 0, "#")
        self.exit_shell()
        return res

    def get_scand_option(self):
        # result is ['SCAND mode is enable', 'OK']
        res = self.cmd("get scand")
        ser = re.search('enable', res[0])
        if ser and 'enable' == ser.group(0).lower():
            return True
        else:
            return False

    def set_scand_option(self, option=True):
        if option == True:
            self.cmd("set scand enable")
        else:
            self.cmd("set scand disable")

    def grep_ap_process(self, process):
        """
        """
        self.goto_shell()
        res = self.cmd('ps -ef|grep %s' % process, 0, '#')
        self.exit_shell()
        
        #[' 4592     1 root      3312 S    /usr/sbin/scand -S ', '10798 10666 root      1092 S    grep scand']
        if len(res) == 1:
            return False
        else:
            return True

    def get_channel_availability(self, wlan_if='wifi1'):
        res_list = self.cmd("get channelavailability %s" % wlan_if)
        avail_channel_list = []
        block_channel_list = []
        dfs_block_channel_list = []

        for info in res_list:
            avl = re.search(r'\s*(\d*):.*\s*AVBLE', info, re.I)
            if avl:
                avail_channel_list.append(avl.groups()[0])
            else:
                dfs = re.search(r'\s*(\d*):.*\s*Block Radar', info, re.I)
                if dfs:
                    dfs_block_channel_list.append(dfs.groups()[0])
                else:
                    blk = re.search(r'\s*(\d*):.*\s*BLOCK', info, re.I)
                    if blk:
                        block_channel_list.append(blk.groups()[0])
        
        return {'avail_channel': avail_channel_list,
                'block_channel': block_channel_list,
                'dfs_block_channel': dfs_block_channel_list}

    #AP initial provision tag
    def get_ipt_option(self):
        # result is ['current provisioning tag: xxxx.', 'OK']
        res = self.cmd("get provisioning-tag")
        ser = re.search(':( *)(\w+\s*\w*)(.*)', res[0])
        if ser:
            return ser.groups()[1]
        else:
            return ''

    def set_ipt_option(self, ipt_name):
        self.cmd("set provisioning-tag %s" % ipt_name)

    def get_dc_info(self):
        """
        """
        dc_info = {}
        expected_info_re = {'status': 'feature is (\S*)',
                            'duration': 'duration\s*(\d+)',
                            'total_periods': 'total\s*(\d+)\s*periods',
                            'current_period': 'current period is\s*(\d+)'}
        result = self.cmd('get dc')
        for line in result:
            for key in expected_info_re.keys():
                info = re.findall(expected_info_re[key], line)
                if info:
                    dc_info[key] = info[0]
                    continue
        return dc_info

    def get_mq_holding_time(self):
        dict_regex = {
            'voice' : 'voice\s+holding time = (\d+)',
            'video' : 'video\s+holding time = (\d+)',
            'data' : 'data\s+holding time = (\d+)',
            'bk' : 'bk\s+holding time = (\d+)'
        }
        result = {
            'voice' : 0,
            'video' : 0,
            'data' : 0,
            'bk' : 0
        }

        list_holding_time = self.cmd('get mq holdingtime')
        str_info = ' '.join(str(i) for i in list_holding_time)
        for info in result.keys():
            result[info] = re.findall(dict_regex[info], str_info)[0]

        return result

    def set_mq_holding_time(self, dict_input):
        result = {
            'voice' : 0,
            'video' : 0,
            'data' : 0,
            'bk' : 0
        }

        result.update(dict_input)

        self.cmd('set mq holdingtime %s %s %s %s' % (result['voice'], result['video'], result['data'], result['bk']))

    def get_directed_thr(self, wlan_if):
        pat = r"([0-9]+)$"
        res = self.cmd('get directed-thr %s' % wlan_if)
        for line in res:
            mobj = re.search(pat, line)
            if mobj: return mobj.group(1)
        return None

    def get_directed_threshold(self, wlan_if):
        return self.get_directed_thr(wlan_if)

    def get_bssid_by_ssid(self, ssid):
        wlan_if = self.ssid_to_wlan_if(ssid)
        for x in self.get_wlan_list():
            if x[0] == wlan_if:
                #return x[-1]
                #@author: lipingping;@bug: ZF-8778;@since: 2014.6.19 behavior change for ap cli cmd "get wlanlist"
                return x[-2]
        return ''

    def get_channel_by_ssid(self, ssid):
        wlan_if = self.ssid_to_wlan_if(ssid)
        channel, mode = self.get_channel(wlan_if)
        return channel
    
     
    def get_bridge_setting(self, mode='', bridge = 'all', mgmt_vlan_id = ''):
        res = self.do_shell('brctl show')
        brctl_u_dict = {}
        columns = []
        sub_columns = []        
        br_info = []
        br_info_result = []
        sub_res = res[0][1]
        res_list = sub_res.split("\r\n")        
        res_list = res_list[1:]
        
        header = self.BRCTL_SHOW_HEADER
        header_len = len(header)
        
        header_forepart = self.BRCTL_SHOW_HEADER_FOREPART
        header_forepart_len = len(header_forepart)
        
        header_backpart = self.BRCTL_SHOW_HEADER_BACKPART
        header_backpart_len = len(header_backpart)

        for row in res_list[1:]:
            if row == '' or row == '#':
                continue           
            columns = re.findall("([\t\w\.*\!*\,*\-*]+)[\s\\t]*", row)
            
            if 'br' in columns[0]:
                if len(columns) == (header_len - 1):
                    columns_forepart = columns[:header_forepart_len]
                    columns_backpart = columns[header_forepart_len:]
                    sub_columns = copy.copy(columns_forepart)
                    
                    columns_backpart_temp_part1 = columns_backpart[:2]
                    columns_backpart_temp_part2 = columns_backpart[2:]
                    columns_backpart_temp_part1.extend([''])
                    columns_backpart_temp_part1.extend(columns_backpart_temp_part2)
                    columns = copy.copy(columns_forepart)
                    columns.extend(columns_backpart_temp_part1)
                    
                elif len(columns) == (header_len - 2):
                    columns_forepart = columns[:header_forepart_len]
                    columns_backpart = columns[header_forepart_len:]
                    sub_columns = copy.copy(columns_forepart)
                    
                    columns_backpart_temp_part1 = columns_backpart[:1]
                    columns_backpart_temp_part2 = columns_backpart[1:]
                    columns_backpart_temp_part1.extend(['', ''])
                    columns_backpart_temp_part1.extend(columns_backpart_temp_part2)
                    columns = copy.copy(columns_forepart)
                    columns.extend(columns_backpart_temp_part1)
                
                elif len(columns) == (header_len - 3):    
                    columns_forepart = columns[:header_forepart_len]
                    columns_backpart = columns[header_forepart_len:]
                    sub_columns = copy.copy(columns_forepart)
                    
                    columns = copy.copy(columns_forepart)
                    columns.extend(['', '', ''])
                    columns.extend(columns_backpart)
                    
                else:
                    tag = 0
                    while (tag < header_backpart_len):
                        columns.append('')
                        tag += 1
            else:
                if len(columns) == header_backpart_len:
                    i_sub_columns = copy.copy(sub_columns)
                    sub_columns.extend(columns)
                    columns = copy.copy(sub_columns)
                    sub_columns = copy.copy(i_sub_columns)
                    
                elif len(columns) == header_backpart_len - 1:
                    i_sub_columns = copy.copy(sub_columns)
                    columns_temp_part1 = columns[:2]
                    columns_temp_part2 = columns[2:]
                    columns_temp_part1.extend([''])
                    columns_temp_part1.extend(columns_temp_part2)
                    sub_columns.extend(columns_temp_part1)
                    columns = copy.copy(sub_columns)
                    sub_columns = copy.copy(i_sub_columns)
                    
                elif len(columns) == header_backpart_len - 2:
                    i_sub_columns = copy.copy(sub_columns)
                    columns_temp_part1 = columns[:1]
                    columns_temp_part2 = columns[1:]
                    columns_temp_part1.extend(['', ''])
                    columns_temp_part1.extend(columns_temp_part2)
                    sub_columns.extend(columns_temp_part1)
                    columns = copy.copy(sub_columns)
                    sub_columns = copy.copy(i_sub_columns)
                    
                else:
                    i_sub_columns = copy.copy(sub_columns)
                    sub_columns.extend(['', '', ''])
                    sub_columns.extend(columns)
                    columns = copy.copy(sub_columns)
                    sub_columns = copy.copy(i_sub_columns)
                    
            for index, col in enumerate(columns):
                brctl_u_dict[header[index]] = col
                
            back_brctl_u_dict = copy.deepcopy(brctl_u_dict)    
            br_info.extend([back_brctl_u_dict])
 
        if mode and (bridge != 'all'):
            for br_u in br_info:
                if mgmt_vlan_id and ((bridge + '.' + mgmt_vlan_id) in br_u['bridge']) and (mode == br_u['Mode']):
                    br_info_result.extend([br_u])
                elif (not mgmt_vlan_id) and (bridge in br_u['bridge']) and (mode == br_u['Mode']):
                    br_info_result.extend([br_u])
        elif (not mode) and (bridge != 'all'):
            for br_u in br_info:
                if mgmt_vlan_id and ((bridge + '.' + mgmt_vlan_id) in br_u['bridge']):
                    br_info_result.extend([br_u]) 
                elif (not mgmt_vlan_id) and (bridge in br_u['bridge']):
                    br_info_result.extend([br_u])
        elif mode and (bridge == 'all'):
            for br_u in br_info:
                if mode == br_u['Mode']:
                    br_info_result.extend([br_u])
        elif (not mode) and (bridge == 'all'):
            br_info_result = br_info
    
        return br_info_result
    
    def get_sta_ip_mac_info(self, bridge = 'br0', iptype = 'all'):
        sta_ip_mac_info_dic = {}
        sta_ip_mac_info_dic_ipv4 = {}
        sta_ip_mac_info_dic_ipv6 = {}
        sta_ip_mac_info_ipv4 = {'ipv4': []}
        sta_ip_mac_info_ipv6 = {'ipv6': []}
        cmd = 'brctl showips %s %s' %(bridge, iptype)
        
        res = self.do_shell(cmd)
        sub_res = res[0][1]
        res_list = sub_res.split("\r\n")        
        res_list = res_list[1:]
        
        for row in res_list:
            columns = []
            if row == '' or row == '#':
                continue           
            tem_columns = row.split("\t")
            for item in tem_columns:
                if item:
                    item_strip = item.strip()
                    columns.append(item_strip)   
            if columns[0] == 'ip':
                columns[0] = 'ipv4'
                header_ipv4 = copy.copy(columns)
            elif columns[0] == 'ipv6':
                header_ipv6 = copy.copy(columns)
            elif len(columns[0]) <= 15:
                for index, col in enumerate(columns):
                    sta_ip_mac_info_dic_ipv4[header_ipv4[index]] = col
                sta_ip_mac_info_dic_ipv4_temp = copy.deepcopy(sta_ip_mac_info_dic_ipv4)
                sta_ip_mac_info_ipv4['ipv4'].extend([sta_ip_mac_info_dic_ipv4_temp])
            else:
                for index, col in enumerate(columns):
                    sta_ip_mac_info_dic_ipv6[header_ipv6[index]] = col
                sta_ip_mac_info_dic_ipv6_temp = copy.deepcopy(sta_ip_mac_info_dic_ipv6)
                sta_ip_mac_info_ipv6['ipv6'].extend([sta_ip_mac_info_dic_ipv4_temp])
        
        if iptype == '4':
            return sta_ip_mac_info_ipv4
        elif iptype == '6':
            return sta_ip_mac_info_ipv6
        else:
            sta_ip_mac_info_dic.update(sta_ip_mac_info_ipv4)
            sta_ip_mac_info_dic.update(sta_ip_mac_info_ipv6)
            return sta_ip_mac_info_dic

    def del_sta_ip_mac_info(self, bridge = 'br0', wlan_port = 'wlan0', sta_wifi_mac = '00:00:00:00:00:00', iptype = '4'):
        cmd = 'brctl delipdbmac %s %s %s %s' %(bridge, wlan_port, sta_wifi_mac, iptype)
        self.do_shell(cmd)
        
    def set_sta_ip_mac_age_time(self, bridge = 'br0', age_time = '8'):
        '''
        The units of 'age_time' is 'minute'
        '''
        cmd = 'brctl setipageing %s %s' %(bridge, age_time)
        self.do_shell(cmd)
        
    def set_eth_mtu(self, eth_interface = 'eth0', mtu = 1500):
        cmd_text = 'set mtu %s %d' %(eth_interface, mtu)
        res = self.cmd(cmd_text = cmd_text, return_list = True)
        if res[-1].lower() == 'ok':
            return True
        else:
            return False
    
    def verify_eth_mtu(self, eth_interface = 'eth0', mtu = 1500):
        cmd_text = 'get mtu %s' % eth_interface
        res = self.cmd(cmd_text = cmd_text, return_list = True)
        if res[-1].lower() != 'ok':
            return False
        elif (res[0].split(': '))[1] != str(mtu):
            return False
        else:
            return True
			
#@author:chen.tao 2014-10, to get lldp config from ap cli
    def get_lldp_cfg_dict(self):
        """
        Result example:
        {
         'state': 'Enabled',
         'mgmt': 'Enabled',
         'holdtime': '120',
         'interval': '30',
         'enable_ports':[0,1,2],
         'disable_ports':[3,4]
         }
        """
        lldp_info_dict = {}
        lldp_info_dict['enable_ports']=[]
        lldp_info_dict['disable_ports']=[]
        cmd_text = "get lldp"
        res = self.cmd(cmd_text = cmd_text, return_list = True)
        pattern_lldp_status = "LLDP\s*state\s*:\s*(Enabled|Disabled)"
        pattern_lldp_interval = "LLDP\s*interval\s*:\s*(\d+)"
        pattern_lldp_holdtime = "LLDP\s*holdtime\s*:\s*(\d+)" 
        pattern_lldp_mgmt = "LLDP\s*mgmt\s*:\s*(Enabled|Disabled)"
        pattern_lldp_eth = "LLDP\s*on\s*eth(\d+)\s*:\s*(Enabled|Disabled)"
        for line in res:
            if re.search(pattern_lldp_status,line):
                lldp_info_dict['state'] = re.search(pattern_lldp_status,line).group(1)
            if re.search(pattern_lldp_interval,line):
                lldp_info_dict['interval'] = re.search(pattern_lldp_interval,line).group(1)
            if re.search(pattern_lldp_holdtime,line):
                lldp_info_dict['holdtime'] = re.search(pattern_lldp_holdtime,line).group(1)
            if re.search(pattern_lldp_mgmt,line):
                lldp_info_dict['mgmt'] = re.search(pattern_lldp_mgmt,line).group(1)
            if re.search(pattern_lldp_eth,line):
                port_name = re.search(pattern_lldp_eth,line).group(1)
                status = re.search(pattern_lldp_eth,line).group(2)
                if status == 'Enabled':
                    lldp_info_dict['enable_ports'].append(port_name)
                if status == 'Disabled':
                    lldp_info_dict['disable_ports'].append(port_name) 

        return lldp_info_dict

    def _get_lldp_neighbors(self):

        """
        '-------------------------------------------------------------------------------',
        'LLDP neighbors:',
        '-------------------------------------------------------------------------------',
        'Interface:    eth0, via: LLDP, RID: 1, Time: 0 day, 00:00:03',
        '  Chassis:     ',
        '    ChassisID:    mac 10:47:80:21:cc:cb',
        '    SysName:      Quidway',
        '    SysDescr:     S3700-28TP-SI-AC ',
        'Huawei Versatile Routing Platform Software ',
        ' VRP (R) software,Version 5.70 (S3700 V100R005C01SPC100) ',
        ' Copyright (C) 2000-2006 Huawei Technologies Co., Ltd.',
        '    MgmtIP:       20.0.2.252',
        '    Capability:   Bridge, on',
        '  Port:        ',
        '    PortID:       ifname Ethernet0/0/7',
        '    PortDescr:    Not received',
        '  LLDP-MED:    ',
        '    Device Type:  Network Connectivity Device',
        '    Capability:   Capabilities',
        '    Capability:   Policy',
        '    Capability:   MDI/PSE',
        '    Capability:   MDI/PD',
        '    Capability:   Inventory',
        '    LLDP-MED Network Policy for: Voice, Defined: yes',
        '      VLAN:         priority',
        '      Priority:     Voice',
        '      DSCP Value:   46',
        '    Extended Power-over-Ethernet:',
        '      Power Type:   unknown',
        '      Power Source: unknown',
        '      Power priority: unknown',
        '      Power Value:  200',
        '      Inventory:   ',
        '        Hardware Revision: VER B',
        '        Software Revision: Version 5.70 V100R005C01SPC100',
        '        Firmware Revision: ',
        '        Serial Number: ',
        '        Manufacturer: HUAWEI TECH CO., LTD',
        '        Model:        ',
        '        Asset ID:     ',
        '-------------------------------------------------------------------------------',
        """    
        
        cmd_text = "get lldp neighbors"
        res = self.cmd(cmd_text = cmd_text, return_list = True)
        return res

#@author:chen.tao 2014-10, to get lldp neighbor from ap cli
    def get_lldp_neighbors(self):
        """
        Result example:
        {1: {'chassis_id': '10:47:80:21:cc',
             'management_address': '20.0.2.252',
             'port_description': 'Not received',
             'port_id': 'ifname Ethernet0/0/7',
             'system_capabilities': 'Bridge, on',
             'system_description': 'S3700-28TP-SI-AC',
             'system_name': 'Quidway',
             'time_to_live': ''}}
        """

        lldp_info_dict = {
                      'chassis_id':'',
                      'port_id':'',
                      'time_to_live':'',
                      'port_description':'',
                      'system_name':'',
                      'system_description':'',
                      'system_capabilities':'',
                      'management_address':''
        }
        neighbors = self._get_lldp_neighbors()
        pattern_chassis_id = "ChassisID\s*:\s*mac\s*([0-9a-fA-F:]{17})"
        pattern_port_id = "PortID\s*:\s*(.+)"
        pattern_port_desc = "PortDescr\s*:\s*(.+)"
        pattern_sys_name = "SysName\s*:\s*(.+)"
        pattern_sys_desc = "SysDescr\s*:\s*(.+)"
        pattern_sys_capability =  "Capability\s*:\s*(.+)"
        pattern_mgmt_ip = "MgmtIP\s*:\s*(.+)"
        neighbors_dict = {}
        neighbor_idx = 0

        for line in neighbors:
            line = line.strip()
            if re.search(pattern_chassis_id,line):
                neighbor_idx+=1
                neighbors_dict[neighbor_idx] = copy.deepcopy(lldp_info_dict)
                neighbors_dict[neighbor_idx]['chassis_id'] = re.search(pattern_chassis_id,line).group(1)
                capability_flag = True#indicating if this the first line starting with "Capability"
                
            if not neighbor_idx: continue

            if re.search(pattern_port_id,line):
                neighbors_dict[neighbor_idx]['port_id'] = re.search(pattern_port_id,line).group(1)
            if re.search(pattern_port_desc,line):
                neighbors_dict[neighbor_idx]['port_description'] = re.search(pattern_port_desc,line).group(1)
            if re.search(pattern_sys_name,line):
                neighbors_dict[neighbor_idx]['system_name'] = re.search(pattern_sys_name,line).group(1)
            if re.search(pattern_sys_desc,line):
                neighbors_dict[neighbor_idx]['system_description'] = re.search(pattern_sys_desc,line).group(1)
            if re.search(pattern_sys_capability,line) and capability_flag:
                neighbors_dict[neighbor_idx]['system_capabilities'] = re.search(pattern_sys_capability,line).group(1) 
                capability_flag = False           
            if re.search(pattern_mgmt_ip,line):
                neighbors_dict[neighbor_idx]['management_address'] = re.search(pattern_mgmt_ip,line).group(1)                 
                
        return neighbors_dict

#@author:chen.tao 2014-10, to get all ap's Ethernet ports
    def get_ap_eth_port_num_dict(self):
        ap_port_dict = {'all':[],
                        'up':[],
                        'down':[]
                        }
        buf = self.cmd('get eth\n')
        buf = [x.strip() for x in buf]
        pattern_down_port = "eth(\d).+Down"
        pattern_up_port = "eth(\d).+Up"
        for line in buf:
            m = re.search(pattern_up_port, line)
            if m: 
                port_num = str(m.group(1))
                ap_port_dict['up'].append(port_num)
                ap_port_dict['all'].append(port_num)
            else:
                mm = re.search(pattern_down_port, line)
                if mm:
                    port_num = str(mm.group(1))
                    ap_port_dict['down'].append(port_num)
                    ap_port_dict['all'].append(port_num)

        return ap_port_dict

#@author:chen.tao 2014-10, to get the mac address of a specified Ethernet port
    def get_eth_port_mac(self, eth_port):
        expect_info = '%s([0-9,a-f,A-F]+:*)*'%eth_port
        return [x.split()[-1] for x in self.cmd('get boarddata') if re.search(expect_info, x)][0]

    def say_hello(self):
        '''
        This is to test the FeatureUpdater
        '''
        print "RuckusAP2: Hello!"


    def _parse_version(self, version):
        '''
        rkscli: get version -> Version: 9.1.0.3.78
        but we need 9.1.0.3 for comparision
        '''
        l = version.split('.')
        return '.'.join(l[:4])


    def update_feature(self):
        '''
        . this generic function should only be ran on subclasses
        . just some classes have the update ability, for those don't have this
          feature, just let get_version() return None
        '''
        ver = self._parse_version(self.get_version())
        if ver:
            ftup.FeatureUpdater.notify(self, ver)


    def features_adding(self):
        '''
        Define a dict of original/updated attributes
        '''
        return {
        }


    def accumulate_attrs(self):
        '''
        Add additional attributes
        '''
        for ver, attrs in self.features_adding().iteritems():
            if self.feature_update.has_key(ver):
                self.feature_update[ver].update(attrs)

            else:
                self.feature_update[ver] = attrs



class RuckusAP(RuckusAP2):
    '''
    '''

