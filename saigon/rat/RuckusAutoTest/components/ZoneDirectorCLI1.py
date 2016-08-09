# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
ZoneDirectorCLI interfaces with and controls any Ruckus ZoneDirector via SSH CLI.

Examples:

    >>> from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI2
    >>> zdcli = ZoneDirectorCLI({})
    >>> data = zdcli.do_cmd('show ap')
    >>> print data
    IP Addr         MAC Addr          Mode State Radio     Chan VAP
    192.168.0.235   00:1d:2e:16:4f:60 L2   Oper  11b/g     1
    192.168.0.186   00:1f:41:23:00:01 L3   Oper  11g/n     Auto
    192.168.0.201   00:1d:2e:13:60:28 L2   Oper  11b/g     1
    192.168.0.182   00:1f:41:04:00:10 L2   Oper  11g/n     Auto
    192.168.0.214   00:22:7f:04:63:50 L2   Oper  11b/g     1
    192.168.0.193   00:1d:2e:13:92:1a L2   Oper  11b/g     1
    *** Total Active AP Entries: 6 ***
    >>> zdcli.zdcli.close()
    >>> zdcli.login()
    >>> data = zdcli.do_cmd('wlaninfo -A', timeout=30)
    >>> print data
    >>> print zdcli.do_shell_cmd('cat /var/log/messages', timeout=20)

"""
import re
import time
import logging

from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib import FeatureUpdater as ftup


class ZoneDirectorCLI2:
    '''
    '''
    feature_update = {}


    def __init__(self, config):
        """
        Connect to the Ruckus ZD at the specified IP address via ssh.
        The specified login credentials will be used.
        All subsequent CLI operations will be subject to the specified default timeout.
        If log file is specified then out CLI output will be logged to the specified file.
        """
        self.conf = dict(
            ip_addr = '192.168.0.2',
            port = 22,
            username = 'admin',
            password = 'admin',
            timeout = 10,
            log_file = None,
            prompt = r'ruckus(%|#)',
            shell_prompt = r'ruckus(#|%)',
            init = True,
            debug = 0,
            shell_key = '!v54!',
        )
        self.conf.update(config)

        self.accumulate_attrs()

        if self.conf['init']:
            self.initialize()

        # register itself to Feature Updater
        ftup.FeatureUpdater.register(self)


    def __del__(self):
        self.zdcli.close()


    def log(self, txt):
        """
        Log specified text if a log file is configured
        """
        if self.log_file:
            stime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            self.log_file.write("\r%s\r%s" % (stime, txt))


    def initialize(self, set_session_timeout=True):
        self.ip_addr = self.conf['ip_addr']
        self.port = self.conf['port']
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.timeout = int(self.conf['timeout'])
        self.prompt = self.conf['prompt']
        self.shell_prompt = self.conf['shell_prompt']
        self.log_file = self.conf['log_file']
        self.next_gen_cli = False
        self.current_prompt = ''

        self.started = False
        self.start_ssh_client()
        #@author: Jane.Guo @since: 2013-09 fix bug
        self.login(set_session_timeout=set_session_timeout)

        self.sysinfo = self.get_system_info()


    def start_ssh_client(self, tries = 3):
        '''
        '''
        count = 0
        while not self.started:
            count += 1
            try:
                logging.info('Creating SSH session to Zone Director at %s' % self.ip_addr)
                self.zdcli = sshclient(self.ip_addr, self.port, self.username, self.password)
                self.started = True

            except Exception:
                self.close()
                if count >= tries:
                    raise

                logging.debug('Try to start SSH session to Zone Director %s time(s)' % count)


    def login(self,set_session_timeout=True):
        """
        Login to Ruckus Zone Director
        """
        logging.debug('Trying to login to the ZD [%s]...' % self.ip_addr)
        try:
            ix, mobj, rx = self.zdcli.expect(['login'])
            logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
            if not ix:
                self.zdcli.write(self.username + '\n')
                logging.debug("[ZD %s CMD INPUT] %s" % (self.ip_addr,self.username))
            else:
                raise Exception('Login prompt is not found')

            ix, mobj, rx = self.zdcli.expect(['Password'])
            logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
            if not ix:
                self.zdcli.write(self.password + '\n')
                logging.debug("[ZD %s CMD INPUT] %s" % (self.ip_addr,self.password))
            else:
                raise Exception('Password prompt is not found')

            ix, mobj, rx = self.zdcli.expect([self.prompt])
            logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
            if ix:
                raise Exception('Login failed')
            else:
                logging.info('Login to ZD [%s] successfully!' % self.ip_addr)
        except Exception, e:
            raise Exception('Login error with msg: %s' % e.message)
        if set_session_timeout:
            self.set_session_timeout(self.conf['session_timeout'])


    def re_login(self,set_session_timeout=True):
        '''
        '''
        try:
#            logging.debug("Trying to exit from the CLI shell mode by the 'login' command...")
            self.exit_shell()
#            logging.debug("The 'login' command was executed successfully.")
#            logging.debug("Please proceed to the login procedure.")

        except Exception, e:
            logging.debug(e.message)

        time.sleep(5)

        #@author: Jane.Guo @since: 2013-09 fix bug
        self.initialize(set_session_timeout=set_session_timeout)
#        self.set_session_timeout(self.conf['session_timeout'])


    def exit_shell(self):
        '''
        '''
#        self.zdcli.write("login\n")
        self.zdcli.write('quit\n')
#        logging.debug("The 'quit' command was executed successfully.")
        self.zdcli.write('exit\n')
#        logging.debug("The 'exit' command was executed successfully.")


    def re_initialize(self):
        self.close()
        self.initialize()
        self.set_session_timeout(self.conf['session_timeout'])


    def close(self):
        """
        Closes the connection and deletes the object.
        """
        try:
#            logging.debug("Trying to close the CLI connection by the 'quit' command...")
            self.zdcli.write('quit\n')
#            logging.debug("The 'quit' command was executed successfully.")
#            logging.debug("Trying to close the CLI connection again by the 'exit' command...")
            self.zdcli.write('exit\n')
#            logging.debug("The 'exit' command was executed successfully.")

            self.started = False
            try:
                logging.debug("Trying to delete self.zdcli object...")
                del self.zdcli
                logging.debug("The self.zdcli object was deleted.")

            except:
                logging.debug("The self.zdcli object could not be deleted.")
                pass

        except Exception, e:
            logging.debug('[CLI][EXIT ERROR] %s' % e.message)


    def logout(self,telnet=False):
        """
        Closes the connection.
        """
        if not telnet:
            cli = self.zdcli
        else:
            cli = self.tn_cli
        try:
            logging.debug("Trying to close the CLI connection by the 'quit' command...")
            logging.debug("[ZD %s CMD INPUT] %s" % (self.ip_addr,"quit"))
            cli.write('quit\n')
            ix, mobj, rx = cli.expect("Exit Ruckus CLI.")
            logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
            logging.debug("The 'exit' command was executed successfully.")
            logging.debug("Trying to close the CLI connection again by the 'exit' command...")
            cli.write('exit\n')
            logging.debug("The 'exit' command was executed successfully.")

        except Exception, e:
            logging.debug('[CLI][EXIT ERROR] %s' % e.message)



    def do_cmd(self, cmd, prompt = '', timeout = 120, raw = False):#Chico, 2014-11-27, change timeout from 10 to 120
        """
        Return the output of the command executing on the ZD CLI.
        Input:
            cmd: command string
            timeout: timeout for the command executing
        """
        if not prompt:
            prompt = self.prompt
            
        logging.debug("[ZD %s CMD INPUT] %s" % (self.ip_addr,cmd))
        self.zdcli.write(cmd + '\n')

        if type(prompt) is str:
            prompt_list = [prompt]

        else:
            prompt_list = prompt

        ix, mobj, rx = self.zdcli.expect(prompt_list, timeout)
        logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
        
        if "Your session has timed out" in rx:
            self.zdcli.write(cmd + '\n')
            ix, mobj, rx = self.zdcli.expect(prompt_list, timeout)
            #An Nguyen, an.nguyen@ruckuswireless.com - Nov 2010
            #Update current prompt as the last line received from socket.

        if rx:
            self.current_prompt = rx.strip().split('\n')[-1]

        if ix == -1:
            raise Exception('Did not see the command prompt: %s, cmd is %s, rx is %s' % (prompt_list, cmd, rx))

        elif raw:
            return rx

        else:
            rx = rx.replace(cmd, '')
            # prompt is by default regexp encoded; use re to extract it
            for prompt in prompt_list:
                m = re.search(prompt, rx, re.I)
                if m:
                    #cwang@2020-10-6, fix when match from zero index.
                    if m.start() == 0:
                        last_idx = 0

                    else:
                        last_idx = m.start() - 1

                    rx = rx[:last_idx]
                    rx = rx.strip()

                    break

                rx = rx.strip()

            return rx


    def do_shell_cmd(self, cmd, timeout = 10):
        """
        Return the result after excute the command on the ZD linux shell.
        Input:
            cmd: commad string
            timeout: timout for the command excuting
        """
        self.do_cmd(self.conf['shell_key'], self.shell_prompt)
        result = self.do_cmd(cmd, prompt = self.shell_prompt, timeout = timeout)
        self.do_cmd(self.conf['shell_key'], self.prompt)

        return result

    def get_pmk_cache(self, timeout = 0):
        """
        Return the output of command 'wlaninfo -J' executing
        """
        info = self.do_cmd('wlaninfo -J', timeout)

        return info


    def get_pmk_info(self, timeout = 0):
        """
        Return the list dictionary of PKM information.
        """
        total_pmk = 0
        pmks_info = []
        info = self.do_cmd('wlaninfo -J', timeout)
        if self.sysinfo['Version'][0] in ['8']:
            pmks_count = re.findall('Total ([0-9]+) in VAP ([0-9a-fA-F:]{17})', info)
            if pmks_count:
                total_pmk = 0
                for pmk_entry in pmks_count:
                    pmk_info = {}
                    count, bssid = pmk_entry
                    pmk_info['station'] = ''
                    pmk_info['auth_user'] = ''
                    pmk_info['pmk_timer'] = ''
                    pmk_info['pmk_count'] = count
                    pmk_info['bssid'] = bssid
                    pmk_entry_info = ('', '', '')
                    if count and bssid and count != '0':
                        if total_pmk < count:
                            total_pmk = count

                        entry_info = self.get_pmk_info_by_bssid(bssid)
                        for info in entry_info:
                            sta, user, timer = info
                            pmk_info['station'] = sta.strip()
                            pmk_info['auth_user'] = user.strip()
                            pmk_info['pmk_timer'] = timer.strip()
                            pmks_info.append(pmk_info)

                    elif count and bssid and count == '0':
                        pmks_info.append(pmk_info)

        else:
            pmks_count = re.findall('Total pmk count = ([0-9]+)', info)
            total_pmk = max(pmks_count)
            if pmks_count and  total_pmk != '0':
                stas_info = info.split('station')
                for sta in stas_info:
                    if sta.strip():
                        sta_mac = re.findall('[0-9a-fA-F:]{17}', sta)
                        pmk_entry = re.findall('user(.*)expiration: ([0-9]+)', sta)
                        pmk_count = re.findall('Total pmk count = ([0-9]+)', sta)
                        if sta_mac and pmk_entry and pmk_count:
                            pmk_info = {}
                            user, timer = pmk_entry[0]
                            pmk_info['station'] = sta_mac[0]
                            pmk_info['auth_user'] = user.strip()
                            pmk_info['pmk_timer'] = timer.strip()
                            pmk_info['pmk_count'] = pmk_count[0]
                            pmks_info.append(pmk_info)

        return (total_pmk, pmks_info)


    def get_pmk_info_by_bssid(self, bssid):
        """
        """
        info = self.do_cmd('wlaninfo -v %s -l8' % bssid)
        return re.findall('([0-9a-fA-F:]{17}) :(.+) expire in ([0-9]+) s', info)


    def get_system_info(self):
        """
        Return the Zone Director information as a dictionary.
        Ex:
            {'IP Addr': '192.168.0.2/255.255.255.0',
            'MAC Addr': '00:1d:2e:16:b4:80',
            'System Name': 'ruckus',
            'Version': '7.1.0.0 build 37',
            'Model': 'zd1006'}
        """

        info = self.do_cmd('show system').split('\r\n')
        sys_info = {}
        for line in info:
            if ': ' in line:
                line_info = line.split(': ')
                sys_info[line_info[0].strip()] = line_info[1].strip()

        return sys_info


    def get_ip_lease(self):
        """
        """
        dhcpd_lease_path = '/etc/airespider-images/dhcpd.lease'
        re_ip = '(\d{1,3}\.){3}\d{1,3}'
        re_mac = '[0-9a-fA-F:]{17}'
        re_leasetime = '[0-9]+'
        ip_lease_info = []
        info = self.do_shell_cmd('cat %s' % dhcpd_lease_path).split('\r\n')
        for line in info:
            ip = re.search(re_ip, line)
            mac = re.search(re_mac, line)
            leasetime = re.search(re_leasetime, line)

            if ip and mac and leasetime:
                ip_lease = {}
                ip_lease['ip'] = ip.group()
                ip_lease['mac'] = mac.group()
                ip_lease['leasetime'] = leasetime.group()
                ip_lease_info.append(ip_lease)

        return ip_lease_info


    def get_wlan_id(self, ssid):
        info = self.do_cmd("wlaninfo -w '%s'" % ssid)
        info = info.replace("\r", "").replace("\n", "")
        m = re.search("WLAN ID = ([0-9]+),", info)
        if m:
            return m.group(1)

        raise Exception("Unable to find WLAN ID of the SSID [%s] in the buffer [%s]" % (ssid, info))


    def get_hotspot_policy(self, wlan_id, access_policy = False, redir_policy = False):
        proc_file = ""
        acl_list = []

        if access_policy:
            proc_file = "%s-*" % wlan_id

        elif redir_policy:
            proc_file = "%s-*" % str((int(wlan_id) + 33))

        if not proc_file:
            return acl_list

        data = self.do_shell_cmd("cat /proc/afmod/policy/%s" % proc_file)
        acl_re = re.compile("([\d\./]+)\s+([\d\./]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([a-zA-Z]+)")
        for line in data.split("\r\n"):
            m = acl_re.search(line)
            if m:
                acl_list.append(
                    {'src-addr': m.group(1), 'dst-addr': m.group(2),
                     'proto': m.group(3), 'sport': m.group(4),
                     'dport': m.group(5), 'action': m.group(6)
                     }
                )

        return acl_list


    def get_l3_acl_cfg(self, timeout = 0):
        """
        """
        l3acl_list = []
        #@author: yuyanan @since: 2014-10-22 @bug: zf-10173
        try:
            info = self.do_shell_cmd('wlaninfo -P', timeout) # execute command in shell mode from 9.0
        except:
            raise Exception("Error occurred while executing 'wlaninfo -P' in zd shell mode.")

        acl_name_re = '\'(.*)\''
        id_re = 'id\s*=\s*([0-9]+)'
        defaulf_action_re = 'action\s*=\s*(\w+)'
        mac_re = '[0-9a-fA-F:]{17}'
        ip_re = '[0-9.]+/[0-9]+'
        l2_re = '(%s)\s+(%s)\s+(\w+)\s+(\w+)' % (mac_re, mac_re)
        l3_re = '(%s)\s+(%s)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)' % (ip_re, ip_re)
        for acl in info.split('Access Policy'):
            name = re.findall(acl_name_re, acl)
            #if not name or len(name) > 1:
            if not name:
                continue

            name = name[0]
            id = re.findall(id_re, acl)[0]
            default_mode = re.findall(defaulf_action_re, acl)[0]

            l2_rules = []
            for entry in re.findall(l2_re, acl):
                rule = {}
                rule['src_mac'], rule['dst_mac'], rule['eth_type'], rule['action'] = entry
                l2_rules.append(rule)

            l3_rules = []
            idx = 1
            for entry in re.findall(l3_re, acl):
                rule = {}
                rule['order'] = idx
                rule['src_addr'], rule['dst_addr'], rule['protocol'], rule['src_port'], rule['dst_port'], rule['action'] = entry
                l3_rules.append(rule)
                idx += 1

            acl_conf = {}
            acl_conf['name'] = name
            acl_conf['id'] = id
            acl_conf['default_mode'] = default_mode
            acl_conf['l2_rules'] = l2_rules
            acl_conf['rules'] = l3_rules
            l3acl_list.append(acl_conf)

        return l3acl_list


    def set_serial_number(self, sn):
        self.do_cmd(self.conf['shell_key'], self.shell_prompt)

        cmds = []
        cmds.append({'cmd':'rbd change\n', 'exp_txt': 'name'})
        cmds.append({'cmd':'\n', 'exp_txt': 'Serial Number'})
        cmds.append({'cmd':'%s\n' % sn, 'exp_txt': 'Customer ID'})
        cmds.append({'cmd':'\004', 'exp_txt': 'Save Board Data to flash'})
        cmds.append({'cmd':'y\n', 'exp_txt': self.shell_prompt})

        for cmd in cmds:
            self.zdcli.write(cmd['cmd'])
            ix, mobj, rx = self.zdcli.expect(cmd['exp_txt'])
            if ix:
                # Try to terminate the command execution
                self.do_cmd('\003', self.shell_prompt)
                # And quit the shell
                self.do_cmd(self.conf['shell_key'], self.prompt)

                raise Exception("Did not see the text '%s'" % cmd['exp_txt'])

        self.do_cmd(self.conf['shell_key'], self.prompt)


    def get_serial_number(self):
        return [l for l in self.do_shell_cmd('rbd dump').split('\r\n')
                if l.startswith("Serial#")][0].split(':')[1].strip()

    def get_dfs_channel_by_country_code(self, country_code):
        cmd = 'cat /etc/airespider-default/country-list.xml | grep %s' % country_code.upper()
        raw_info = self.do_shell_cmd(cmd)
        dfs_channel_info = re.findall('dfs-channels-11a\s*=\s*"([\d,]*)"\s', raw_info)
        all_channel_info = re.findall('channels-11a\s*=\s*"([\d,]*)"\s', raw_info)

        if dfs_channel_info:
            dfs_channel_info = dfs_channel_info[0].split(',')

        else:
            raise Exception('There is no info about "dfs-channels-11a"')

        dfs_enabled = re.findall('allow-dfs-channels\s*=\s*"(true|false)"\s', raw_info)
        if dfs_enabled:
            dfs_enabled = True if dfs_enabled[0] == 'true' else False

        else:
            raise Exception('There is no info about "allow-dfs-channels"')

        if all_channel_info:
            all_channel_info = all_channel_info[0].split(',')
        else:
            raise Exception('There is no info about "channels-11a"')

        non_dfs_list = []
        for channel in all_channel_info:
            if channel not in dfs_channel_info:
                non_dfs_list.append(channel)

        return {'allow_dfs': dfs_enabled,
                'dfs_channels': dfs_channel_info,
                'non-dfs-channels': non_dfs_list}

    def get_raps_supported_opion(self):
        #Check radio avoidance pr-esanning supported or not
        cmd = 'cat /writable/etc/airespider/system.xml | grep dfs'
        
        #<adv-radio country="GB" environment="0x3" use-dfs-channels="1" only-centrino-channels="0" beacon-interval="100" dtim-period="1" indoor-channel-allow="0">
        raw_info = self.do_shell_cmd(cmd)
        tmp1 = re.findall('use-dfs-channels\s*=\s*"(\d*)"\s', raw_info)
        tmp2 = re.findall('only-centrino-channels\s*=\s*"(\d*)"\s', raw_info)

        rap_supported = False
        if (tmp1 and tmp1[0] == '1') or (tmp2 and tmp2[0] == '1'):
            rap_supported = True

        return rap_supported

    def get_ap_ipmode_by_mac_addr(self, mac):
        cmd = 'cat /etc/airespider/ap-list.xml | grep %s' % mac.lower()
        raw_info = self.do_shell_cmd(cmd)

        ipmode = '*' 
        info = re.findall(r'ipmode="(\*|\d)"', raw_info)
        if info:
            ipmode = info[0]

        return ipmode

    def get_apgrp_ipmode_by_name(self, name='System Default'):
        cmd = 'cat /etc/airespider/apgroup-list.xml'
        raw_info = self.do_shell_cmd(cmd)
        apgrp_list = raw_info.split(r'</apgroup>')
        
        ipmode = '3'
        for info in apgrp_list:
            if name in info:
                ipmode = re.findall(r'<network ipmode="(\*|\d)" />', info)[0]
                break
                
        return ipmode

    ###
    ###

    def fw_upgrade(self, **kwargs):
        self.do_cmd(self.conf['shell_key'], self.shell_prompt)
        self._fw_upgrade(**kwargs)


    def _fw_upgrade(self, **kwargs):
        """
        Force to upgrade firmware for Zone Director via CLI, support TFTP and FTP
        Using the synopsis:
            fw_upgrade <protocol>://<server ip|server name>/<path/image name> [-f]
        """
        fw_upgrade_confirm_txt = 'Are you sure you want to upgrade the entire wireless network?'
        restore_option_selection_txt = 'Please select one from above'
        upgrade_failed_txt = 'Upgrade failed, please try again'
        option = {'protocol': '',
                  'server_ip': '',
                  'user': '',
                  'password': '',
                  'image_name': '',
                  'production_mode': '',
                  'restore_factory': True,
                  'download_timeout': 120,
                  'time_out': 2,
                  'reboot_timeout': 300
                  }

        option.update(**kwargs)
        self._verify_fw_upgrade_option(option)
        # generate upgrade command base on the input parameters
        cmd = self._generate_fw_upgrade_command(option)

        logging.debug('Upgrade the Zone Director:\n\t\t\t\t\t%s' % cmd)
        self.zdcli.write(cmd + '\n')
        ix, mobj, rx = self.zdcli.expect([upgrade_failed_txt, fw_upgrade_confirm_txt, restore_option_selection_txt],
                                         option['download_timeout'])
        if ix == -1:
            raise Exception('[ERROR] %s' % rx)

        if ix == 0:
            raise Exception('[UPGRADE FAILED] %s' % rx)

        if ix == 1:
            logging.debug('Confirm to upgrade the firmware')
            self.zdcli.write('y\n')

        if ix == 2:
            if option['restore_factory']:
                logging.debug('Confirm to downgrade the firmware with restore factory')
                self.zdcli.write('1\n')

            else:
                logging.debug('Confirm to upgrade the firmware with restore the last configuration')
                self.zdcli.write('2\n')

            ix1, mobj1, rx1 = self.zdcli.expect([upgrade_failed_txt, fw_upgrade_confirm_txt],
                                                option['time_out'])
            if ix1 == -1:
                errmsg = '[ERROR] %s' % rx1
                logging.debug(errmsg)
                raise Exception(errmsg)

            if ix1 == 0:
                errmsg = '[UPGRADE FAILED] %s' % rx1
                logging.debug(errmsg)
                raise Exception(errmsg)

            if ix1 == 1:
                logging.debug('Confirm to upgrade the firmware')
                self.zdcli.write('y\n')

        self._wait_to_zonedirector_up(option['reboot_timeout'])


    def _generate_fw_upgrade_command(self, option):
        """
        Generate a command base on the synopsis:
            fw_upgrade <protocol>://<server ip|server name>/<path/image name> [-f]
        """
        cmd = 'fw_upgrade %s://%s/%s %s'
        protocol = option['protocol'].lower()
        if option['user'] and option['password']:
            server_info = '%s:%s@%s' % (option['user'], option['password'], option['server_ip'])

        else:
            server_info = option['server_ip']

        image_name = option['image_name']
        production_mode = '' if not option['production_mode'] else '-f %s' % option['production_mode'].lower()

        return cmd % (protocol, server_info, image_name, production_mode)


    def _verify_fw_upgrade_option(self, option):
        for info in ['protocol', 'server_ip', 'image_name']:
            if not option[info]:
                errmsg = '[INPUT ERROR] The %s information is missed' % info
                raise Exception(errmsg)

        if option['protocol'].lower() not in ['ftp', 'tftp']:
            errmsg = '[INPUT ERROR] This function is not support upgrade Zone Director firmware via %s'
            errmsg = errmsg % option['protocol']
            raise Exception(errmsg)


    def _wait_to_zonedirector_up(self, time_out):
        start_time = time.time()
        retry = 1
        while True:
            logging.info('Waiting for the Zone Director booting up')
            time.sleep(30)
            logging.info('Try to connect to Zone Director - Retry %s' % retry)
            retry += 1
            try:
                self.zdcli.close()
                self.initialize()
                break

            except:
                logging.debug('Logging to Zone Director failed')

            runtime = time.time() - start_time
            if runtime > time_out:
                raise Exception('Could not access to the Zone Director after %s seconds' % runtime)

        print "Re-access to ZD successfully"


    def say_hello(self):
        '''
        This is to test the FeatureUpdater
        '''
        print "ZoneDirectorCLI2: Hello!"


    def _get_version(self):
        """
        Get current version of ZD
        """
        try:
            cur_ver = self.get_system_info()['Version']
            cur_ver = cur_ver.split()

            self.version = {
                'release': cur_ver[0],
                'build': cur_ver[2],
                'version': '.'.join([cur_ver[0], cur_ver[2]]),
            }

            return self.version

        except Exception, e:
            logging.debug(e.message)
            logging.info("Unable to get the ZoneDirector version via its CLI")
            return None


    def get_version(self):
        '''
        '''
        ver = self._get_version()
        if ver:
            return ver['release']

        else:
            return ver


    def update_feature(self):
        '''
        . this generic function should only be ran on subclasses
        . just some classes have the update ability, for those don't have this
          feature, just let get_version() return None
        '''
        ver = self.get_version()
        if ver:
            ftup.FeatureUpdater.notify(self, ver)


    def features_adding(self):
        '''
        Define a dict of original/updated attributes
        '''
        return {
            '9.1.0.0': {
                'say_hello': self.say_hello,
            },
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



class ZoneDirectorCLI1(ZoneDirectorCLI2):
    '''
    '''

func_map = {
    'doCmd': 'do_cmd',
    'doShellCmd': 'do_shell_cmd',
    'getPMKCache': 'get_pmk_cache',
    'getPMKInfo': 'get_pmk_info',
    'getPMKInfoByBSSID': 'get_pmk_info_by_bssid',
    'getSystemInfo': 'get_system_info',
    'getIPLease': 'get_ip_lease',
    'getWlanID': 'get_wlan_id',
    'getHotspotPolicy': 'get_hotspot_policy',
    'getL3ACLConfiguration': 'get_l3_acl_cfg',
    'setSerialNumber': 'set_serial_number',
    'getSerialNumber': 'get_serial_number',

}

for attr, attr2 in func_map.items():
    # dynamically attaches the new methods to ZoneDirector from ZoneDirectorCLI2
    # if they do not exist
    try:
        getattr(ZoneDirectorCLI1, attr)

    except:
        setattr(ZoneDirectorCLI1, attr, getattr(ZoneDirectorCLI1, attr2))

