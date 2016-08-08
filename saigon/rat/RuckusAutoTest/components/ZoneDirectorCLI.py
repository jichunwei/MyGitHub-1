# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
ZoneDirectorCLI interfaces with and controls any Ruckus ZoneDirector via SSH CLI.

Examples:

    >>> from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI
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

import logging
import re
import time

from RuckusAutoTest.components.ZoneDirectorCLI1 import ZoneDirectorCLI1

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
import telnetlib

class ZoneDirectorCLI(ZoneDirectorCLI1):
    UNKOWN_MODE = 0
    USER_MODE = 1#ruckus>
    PRIV_MODE = 2#ruckus#
    CONFIG_MODE = 3#ruckus(config)#
    OBJECT_MODE = 4#ruckus(config-*)#

    def __init__(self, config):
        self.conf = dict(
            base_prompt = r'ruckus',
            prompt = r'ruckus(\([^#]+\))?[#|%|>|\$]',
            logout_shell_key = r'login',
            shell_key = '!v54!',
            init = True,
            session_timeout = 600,
        )

        self.conf.update(config)
        self.base_prompt = self.conf['base_prompt']
        self.login_shell_key = self.conf['shell_key']
        self.logout_shell_key = self.conf['logout_shell_key']

        self.zdcli_prompts = []
        # user exec prompt, _getp() return 1
        self.zdcli_prompts.append(r'%s>' % self.base_prompt)
        # priv exec prompt, _getp() return 2
        self.zdcli_prompts.append(r'%s#' % self.base_prompt)
        # configure terminal mode entry, _getp() return 3
        self.zdcli_prompts.append(r'%s\(config\)#' % self.base_prompt)
        # configure an object prompt, _getp() return 4
        self.zdcli_prompts.append(r'%s\([^\)]+\)#' % self.base_prompt)
        # configure an system object prompt, _getp() return 5
        self.zdcli_prompts.append(r'%s\(config\-sys\)#' % self.base_prompt)

        self.zdcli_prompts.append(r'Are you sure you want to enable mesh\[Y/n\]')
        self.user_exec_prompt = "ruckus>"
        self.priv_exec_prompt = "ruckus#"

        ZoneDirectorCLI1.__init__(self, self.conf)

#        self.update_feature()

        self.set_session_timeout(self.conf['session_timeout'])
        
        #@author: anzuo, @since: 20140714, @change: modify /bin/sys-wrapper.sh to stop ntp discover process when zd start
#        cmds = ["mount / -o rw,remount",
#               "chmod +w /bin/sys_wrapper.sh",
#               'sed -i "s/startNtpd \$\*/echo \"FAIL\"/g" /bin/sys_wrapper.sh',]
#        for cmd in cmds:
#            self.do_shell_cmd(cmd)

    def login(self,set_session_timeout=True,timeout = 10):
        """
        Login to Ruckus Zone Director
        """
        logging.debug('Trying to login to the ZD...')
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

            ix, mobj, rx = self.zdcli.expect([self.prompt],timeout = timeout)
            logging.debug("[ZD %s CMD OUTPUT] %s" % (self.ip_addr,rx))
            if ix:
                raise Exception('Login failed')

            else:
                logging.info('Login to ZD [%s] successfully!' % self.ip_addr)
                if mobj.group(0) == '%s>' % self.base_prompt:
                    self.next_gen_cli = True
                    logging.info('ZoneDirectorCLI is next generation CLI')

                else:
                    logging.info("ZoneDirectorCLI is the old CLI")

        except Exception, e:
            self.zdcli.write('\n')
            ix, mobj, rx = self.zdcli.expect([self.prompt],timeout = timeout)
            if ix:
                raise Exception('Login error with msg: %s' % e.message)
        if set_session_timeout:
            self.set_session_timeout(self.conf['session_timeout'])


    def do_shell_cmd(self, cmd, timeout = 10, re_login = True, set_session_timeout = True, print_message = True):
        """
        Go to shell mode and perform command, which is low-compatible.
        """
        if self.next_gen_cli:
            return self._do_shell_cmd(cmd, timeout, re_login = re_login, set_session_timeout = set_session_timeout, print_message = print_message)

        else:
            return ZoneDirectorCLI1.do_shell_cmd(self, cmd, timeout)


    #Obsolete API, CWANG@2010/08/26
    def enable_config(self, timeout = 10):
        self.position_at_priv_exec_mode()


    def set_session_timeout(self, timeout = 600):
        """
        Set timeout to ZoneDirectorCLI, make sure ZDCLI won't timeout before i.e. 600s
        """
        if self.next_gen_cli:
            self.position_at_priv_exec_mode()

        logging.info("set session-timeout to %d minutes" % timeout)
        result_str=self.do_cmd("session-timeout %d" % timeout)
        if timeout>0 and timeout<1441:
            if 'The command was executed successfully.' in result_str:
                return True,'timeout %s is set successfully by zdcli'%timeout
        elif 'The session timeout interval must be a number between 1 and 1440 minutes.' in result_str:
            return True,'correct behavior,timeout %s can not set'%timeout
        else:
            return False,'wrong behavior,timeout:%s,result:%s'%(timeout,result_str)
                


    def get_session_timeout(self):
        """
        get session value
        """
        if self.next_gen_cli:
            self.position_at_priv_exec_mode()

        str=self.do_cmd("show session-timeout")
        logging.info(str)
        timeout=str.split()[5]
        logging.info("session-timeout is %s minutes" % timeout)
        return int(timeout)

    
    def check_auto_logout_status(self,expected_status=True,telnet_zdcli=False):
        if telnet_zdcli:
            zdcli=self.tn_cli
        else:
            zdcli=self.zdcli
        ix, mobj, rx = zdcli.expect(['Your session is timeout. Please login again'])
        if not ix:
            status=True
            msg='message (%s) get,zdcli session is auto logout'%rx
            logging.info(msg)
        else:
            status=False
            logging.info('time out message not found,zd not auto logout')
        if status==expected_status:
            return True
        else:
            return False
        
    
    def start_telnet_cli(self,username='',password='',port=23,timeout=20):
        if not username:
            username=self.username
        if not password:
            password=self.password
        self.tn_cli = telnetlib.Telnet(self.ip_addr,port)
        ix,mobj,rx = self.tn_cli.expect(["login"],timeout)
        if not ix:
            self.tn_cli.write(username+"\n")
        else:
            logging.info('login prompt not found')
            return False,'login prompt not found'
        ix,mobj,rx = self.tn_cli.expect(["Password"],timeout)
        if not ix:
            self.tn_cli.write(password+"\n")
        else:
            logging.info('Password prompt not found')
            return False,'Password prompt not found'
        ix, mobj, rx = self.tn_cli.expect(['ruckus'],timeout)
        if not ix:
            logging.info('login to telnet zdcli successfully')
            return True,'login to telnet zdcli successfully'
        else:
            logging.info('command prompt not found after login telnet zdcli')
            return False,'command prompt not found after login telnet zdcli'
    def get_wlan_id(self, ssid):
        if self.next_gen_cli:
            return self._get_wlan_id(ssid)

        else:
            return ZoneDirectorCLI1.get_wlan_id(self, ssid)

    def get_wlaninfo_dfs(self, ap_mac, command = 'wlaninfo --dfs %s'):
        """
        Supporting for the command:
            wlaninfo --dfs ap_mac: to show the non-occupancy channel on the AP
        """
        result = {'nol': '', 'total_nol': ''}
        expected_info = {'nol':'channel\s+(\d+)\s+.*timeout in\s+(\d+)',
                         'total_nol':'Total.*:\s*(\d+)\s*'}
        
        data = self.do_shell_cmd(command % ap_mac, timeout = 30)
        logging.info('wlaninfo --dfs %s: %s' % (ap_mac, data))
        
        for key in expected_info.keys():
            tmp_result = re.findall(expected_info[key], data)
            if not tmp_result:
                break;
            result[key] = tmp_result

        return result

    def get_system_info(self):
        if self.next_gen_cli:
            return self._get_system_info()

        else:
            return ZoneDirectorCLI1.get_system_info(self)

    def get_wlan_info_system(self):
        info = self.do_shell_cmd("wlaninfo --system", timeout = 20)
        info = info.replace("\r", "").replace("\n", "")
        
        return info

    def fw_upgrade(self, **kwargs):
        if self.next_gen_cli:
            self.enable_config()
            self._fw_upgrade(**kwargs)

        else:
            ZoneDirectorCLI1.fw_upgrade(self, **kwargs)


    def get_hotspot_policy(self, wlan_id, access_policy = False, redir_policy = False):
        if self.next_gen_cli:
            proc_file = ""
            acl_list = []            
            if access_policy:
                proc_file = "%s-*" % wlan_id
                data = self.do_shell_cmd("cat /proc/afmod/policy/%s" % proc_file, timeout = 30)

            elif redir_policy:
                proc_file = "%s-*" % str((int(wlan_id) + 1024 + 1))
                data = self.do_shell_cmd("cat /proc/afmod/policy/%s" % proc_file, timeout = 10)
                if 'No such file or directory' in data:
                    proc_file = "%s-*" % str((int(wlan_id) + 1024 * 2 + 1))
                    data = self.do_shell_cmd("cat /proc/afmod/policy/%s" % proc_file, timeout = 10)
                    if 'No such file or directory' in data:
                        proc_file = "%s-*" % str((int(wlan_id) + 32 + 1))
                        data = self.do_shell_cmd("cat /proc/afmod/policy/%s" % proc_file, timeout = 10)
            
            if not proc_file:
                return acl_list
            
            #Updated by Jacky Luh @since: 2013-12-05
            #9.8 build enhance the walled garden policy file to surpport the domain name
            #in zd cli shell mode: cat /proc/afmod/policy/1025-3
            acl_re = re.compile("([\da-zA-Z\./]+)\s+([\da-zA-Z\./]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([a-zA-Z]+)")
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

        else:
            return ZoneDirectorCLI1.get_hotspot_policy(self, wlan_id, access_policy, redir_policy)


    def do_cfg(self, cmd_block, exit_to_cfg = True, print_out = True,
               back_cmd = 'end', timeout = 10, raw = False):
        """
        Do configuration action for zd, system will save automatically.
        For example:
           TMPL_AUTOTEST_STD_AAA_CONF = '''
            aaa $name
               type $type
               ip-addr $ip_addr port $port
           exit
           '''
           cmd_blocks = Template(TMPL_AUTOTEST_STD_AAA_CONF).substitute(dict(name = 'test2',
                                                                             type = 'ad',
                                                                             ip_addr = '192.168.0.252',
                                                                             port = '389'))
           zdcli.do_cfg(cmd_blocks)
        """
        try:
            return self._do_cfg(
                cmd_block, exit_to_cfg = exit_to_cfg,
                back_cmd = back_cmd, print_out = print_out,
                timeout = timeout, raw = raw
            )

        except Exception, e:
            logging.debug('[CLI ERROR] %s' % e.message)
            logging.info('Re connect to device and try the command 1 more time.')
            self.re_initialize()

            return self._do_cfg(
                cmd_block, exit_to_cfg = exit_to_cfg, back_cmd = back_cmd,
                print_out = print_out, timeout = timeout, raw = raw
            )


    def do_cfg_show(self, cmd_block, print_out = False, timeout = 10, raw = False):
        """
        Do configuration show action for zd.
        For example:
               cmd_block = '''
               system
                   interface
               '''
               data = zdcli.do_cfg_show(cmd_block)
        """
        cmd = ""
        if cmd_block.rstrip().endswith('show'):
            cmd = cmd_block.strip()

        else:
            cmd = cmd_block.strip() + "\nshow"

        data = self.do_cfg(cmd, print_out = print_out, back_cmd = 'quit', timeout = timeout, raw = raw)

        return data['show'][0]


    def do_show(self, cmd, go_to_cfg = False, print_out = False, timeout = 10, raw = False):
        """
        Show privilege configuration context, system won't save automatically.
        For example:
            Place at PRIV_MODE
            zdcli.do_show('wlan all')
            Return result:'WLAN Service:\r\r\n \r\r\nruckus#'

            Place at CONFIG_MODE
            zdcli.do_show('aaa', go_to_cfg = True)
        """
        cmd = cmd.strip()
        if not cmd.startswith('show'):
            cmd = "show %s" % cmd

        if go_to_cfg:
            return self.do_cfg(cmd, print_out = print_out, timeout = timeout, raw = raw)[cmd]

        res = self._do_show(cmd, print_out = print_out, timeout = timeout, raw = raw)
        if type(res) is list:
            res = res[0]
        
        return res 
    
    


    def position_at_priv_exec_mode(self, timeout = 3, print_out = False):
        """
        Force to configuration mode
        """
        self._pos_mode(mode_type = self.PRIV_MODE, print_out = print_out)


    #stan@20101222
    def back_to_priv_exec_mode(self, back_cmd = 'end', timeout = 3, print_out = False):
        self._back_to_priv_exec_mode(back_cmd, timeout, print_out)


#-------------------------------------------#
#  Under/after SAIGON production            #
#  Handle configuration mode command        #
#===========================================#

    def _step_into_priv_exec_mode(self):
        """
        Enable configuration mode.
        """
        try:
            self.do_cmd("enable force", prompt = self.priv_exec_prompt, raw = True)
        except:
            logging.info('can not login zdcli,reboot it and retry')
            self.do_shell_cmd('reboot',re_login=False)
            self._wait_to_zonedirector_up(1200)

    def _pos_mode(self, timeout = 3, print_out = False, mode_type = PRIV_MODE):
        cnt = 5
        while cnt > 0:
            data = self.do_cmd('', prompt = self.zdcli_prompts, timeout = timeout, raw = True)
            if print_out: print data

            climode = self._getp(data)
            if climode == mode_type:
                return

            if climode == self.UNKOWN_MODE:
                raise Exception('UNKOWN mode, raw data [%s]' % data)

            if climode == self.USER_MODE and mode_type > self.USER_MODE:
                self._step_into_priv_exec_mode()

            elif climode > self.PRIV_MODE:
                #@ZJ 20150624
                if 'config-email-server' in data:
                    self._back_to_priv_exec_mode(back_cmd = 'quit')
                else:
                    self._back_to_priv_exec_mode()

            cnt -= 1


    def _getp(self, data):
        for idx, prompt in enumerate(self.zdcli_prompts):
            ptn = re.compile(prompt, re.M | re.I)
            m = ptn.search(data)
            if m:
                return (idx + 1)

        return 0


    def _do_show(self, cmd, back_cmd = 'quit', print_out = True, timeout = 10, raw = False):
        try:
            logging.debug('[CURENT PROMPT] %s' % self.current_prompt)
            self.position_at_priv_exec_mode()
            lresp = self.do_cmd(cmd, self.zdcli_prompts, timeout = timeout, raw = raw)
            if print_out: print lresp
            logging.debug('[CURENT PROMPT] %s' % self.current_prompt)
            return lresp

        except Exception, e:
            logging.debug('[CLI ERROR] %s' % e.message)
            logging.info('Re connect to device and try the command 1 more time.')
            self.re_initialize()
            logging.debug('[CURENT PROMPT] %s' % self.current_prompt)
            self.position_at_priv_exec_mode()
            lresp = self.do_cmd(cmd, self.zdcli_prompts, timeout = timeout, raw = raw)
            if print_out: print lresp
            logging.debug('[CURENT PROMPT] %s' % self.current_prompt)
            return lresp


    def _do_cfg(self, cmd_block, exit_to_cfg = True, back_cmd = 'end', print_out = False, timeout = 10, raw = False):
        logging.debug('[CURENT PROMPT] %s' % self.current_prompt)
        self.position_at_priv_exec_mode()

        lresp = self.do_cmd('config', self.zdcli_prompts, timeout = timeout, raw = raw)
        if print_out: print lresp

        data = {}
        for cmd_line in cmd_block.split('\n'):
            lresp = self.do_cmd(cmd_line.strip(), self.zdcli_prompts, timeout = timeout, raw = raw)
            if data.has_key(cmd_line):
                data[cmd_line].append(lresp)

            else:
                data[cmd_line] = [lresp]

            if print_out: print lresp

        if exit_to_cfg:
            ppos = self._getp(lresp)
            if ppos == 1:
                self._step_into_priv_exec_mode()
            elif ppos == 2:#@author: yuyanan @since: 2015-2-3 @change:current prompt is #,do nothing.
                pass
            else:
                self._back_to_priv_exec_mode(back_cmd, timeout = timeout)

        logging.debug('[CURENT PROMPT] %s' % self.current_prompt)

        return data


    def _back_to_priv_exec_mode(self, back_cmd = 'end', timeout = 3, print_out = False):
        cnt = 5
        while cnt > 0:
            cnt -= 1
            data = self.do_cmd(back_cmd, prompt = self.zdcli_prompts, timeout = timeout, raw = True)
            if print_out: print data
            if "Are you sure you want to enable mesh[Y/n]" in data:
                data = self.do_cmd("y", prompt = self.zdcli_prompts, timeout = timeout, raw = True)
                
            climode = self._getp(data)
            if climode > 2:
                continue

            elif climode == 2:
                return


#====================================#
#  Be used for SAIGON or after SAIGON
#====================================#
    def _do_shell_cmd(self, cmd, timeout = 20,re_login=True,set_session_timeout=True,print_message=True):
        try:
            self.do_cmd(self.conf['shell_key'])
            result = self.do_cmd(cmd, timeout = timeout)
            if print_message:
                logging.debug(result)

        except Exception, e:
            if 'Did not see the command prompt' in e.message:
                self.re_login(set_session_timeout=set_session_timeout)
                self.do_cmd(self.conf['shell_key'])
                result = self.do_cmd(cmd, timeout = timeout)
                if print_message:
                    logging.debug(result)
            #@author: li.pingping @bug: ZF-8422 @since:2014-5-21 
            elif "ZoneDirectorCLI instance has no attribute 'zdcli'" in e.message:
                time.sleep(5)
                cnt = 3
                while cnt:
                    try:
                        self.start_ssh_client()
                        time.sleep(1)
                        self.login(set_session_timeout=set_session_timeout)
                        self.do_cmd(self.conf['shell_key'])
                        result = self.do_cmd(cmd, timeout = timeout)
                        if print_message:
                            logging.debug(result)
                        break
                    except:
                        self.close()              
                        cnt = cnt - 1
                        time.sleep(5)
            
            else:
                raise e
        finally:
            if re_login:
                self.re_login(set_session_timeout=set_session_timeout)

        return result


    def _get_wlan_id(self, ssid):
        info = self.do_shell_cmd("wlaninfo -w %s" % ssid, timeout = 20)
        info = info.replace("\r", "").replace("\n", "")
        m = re.search("WLAN ID = ([0-9]+),", info)
        if m:
            return m.group(1)

        raise Exception("Unable to find WLAN ID of the SSID [%s] in the buffer [%s]" % (ssid, info))


    def _get_system_info(self):
        """
        Return the Zone Director information as a dictionary.
        Ex:
            {'IP Addr': '192.168.0.2/255.255.255.0',
            'MAC Addr': '00:1d:2e:16:b4:80',
            'System Name': 'ruckus',
            'Version': '7.1.0.0 build 37',
            'Model': 'zd1006'}
        """
        #@author: Jane.Guo @since: 2013-7-31 show system is deleted, so update to show sysinfo
        self.position_at_priv_exec_mode()
        info = self.do_cmd('show sysinfo')
        info = info.split('\r\n')
        sys_info = {}
        for line in info:
            if '= ' in line:
                line_info = line.split('= ')
                sys_info[line_info[0].strip()] = line_info[1].strip()

        return sys_info


    def _get_version(self):
        """
        Get current version of ZD
        """
        try:
            data = self.do_show("sysinfo")
            cur_ver = output.parse(data)['System Overview']['Version']
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


    def say_hello_v2(self):
        '''
        This is to test the FeatureUpdater
        '''
        print "ZoneDirectorCLI: Hello!"


    def features_adding(self):
        '''
        Define a dict of original/updated attributes
        '''
        return {
        }

if __name__ == "__main__":
    zdcli = ZoneDirectorCLI(dict())

    print zdcli.get_wlan_id("WISPr-WLAN-UNDER-TEST-811888")
    print zdcli.get_wlan_id("WISPr-WLAN-UNDER-TEST-811888")
    print ""

