# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
LinuxPC interfaces with and controls the linux machine via telnet.

Examples:

    from RuckusAutoTest.components import LinuxPC
    # method 1
    pc = LinuxPC.LinuxPC(dict(init=False))
    pc.initialzie()
    data = pc.do_cmd('ls -la')
    print data
    # method 2
    pc = LinuxPC.LinuxPC(dict())
    data = pc.do_cmd('ls -la')
    print data
"""
import time
import re
import logging
from telnetlib import *
from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.common import lib_Constant as CONST

ExpState = {'EXPECT': 'expect', 'MATCH': 'match', 'TIMEOUT': 'timeout', 'DATA': 'data', 'EMPTY': 'empty'}

class LinuxPC:
    # define constants for set_dhcp_option_43, enable_dhcp_option_43, disable_dhcp_option_43
    PRODUCT_INFO_FM = 0
    PRODUCT_INFO_ZD = 1
    COMMENT_SIGN  = '#'

    def __init__(self, config):
        """
        Connect to the linux machine at the specified IP address via telnet.
        All user will be change to root use after login.
        All subsequent CLI operations will be subject to the specified default timeout.
        If log_file is specified then out CLI output will be logged to the specified file.
        """
        self.conf = dict(
            timeout = 60,
            log_file = '',
            ip_addr = '192.168.0.252',
            user = 'lab',
            password = 'lab4man1',
            root_password = 'lab4man1',
            prompt = "\[(lab|root)@(localhost|[^\s]+) [~\w\.\-]+\]#",
            init = True,
            debug = 0,
            recv_pause = 0.25,
            wait_for = 300,
            pause = 2,
            stdout = 1
        )
        self.conf.update(config)

        (self.exp_state, self.exp_output, self.exp_recv_cnt) = ('', '', 0)

        if self.conf['init']:
            self.initialize()


    def __del__(self):
        '''
        Destructor
        '''
        pass


    def initialize(self, dologin = True):
        self.timeout = self.conf['timeout']
        self.log_file = self.conf['log_file']
        self.ip_addr = self.conf['ip_addr']
        self.user = self.conf['user']
        self.password = self.conf['password']
        self.root_password = self.conf['root_password']
        self.prompt = self.conf['prompt']
        self.re_prompt = re.compile(self.prompt)
        if not dologin:
            return

        try:
            self.login()

        except:
            log_trace()
            raise Exception('Can not login to the linux PC')


    def re_init(self, conf = None):
        '''
        This method is used to re_init the LinuxPC component to:
        - prevent the issue 'Telnet session is closed'
        - change the prompt or any other conf
        '''
        ### update conf ###
        # this is to preserve the param 'dologin' in self.initialize() method
        _conf = {'dologin': True}

        if conf is not None:
            _conf.update(conf)

        self.conf.update(_conf)

        # close current (telnet) session
        self.close()

        # init the component again
        self.initialize(self.conf.pop('dologin'))


    def log(self, txt):
        """
        Save the log to file
        """
        if self.log_file:
            self.log_file.write(txt)

    def login(self, asRoot = True):
        """
        Login the linux machine via telnet and change the user to root.
        """
        self.pc = Telnet(self.ip_addr)
        self.pc.expect(['login'])
        self.pc.write(self.user + '\n')
        self.pc.expect(['Password'])
        self.pc.write(self.password + '\n')
        ix, ox, tx = self.pc.expect([self.prompt, '\]\$'], self.timeout)
        if ix == 1 and asRoot:
            self.login_as_root()
        if ix == -1:
            raise Exception('Can not telnet to \'%s\'' % self.ip_addr)

    def login_as_root(self):
        self.pc.write('su root\n')
        self.pc.expect(['Password'])
        self.pc.write(self.root_password + '\n')
        ix, ox, tx = self.pc.expect([self.prompt], self.timeout)
        if ix == -1:
            raise Exception('Can not change \'%s\' to be root user' % self.user)

    def close(self):
        """
        Close the telnet session
        """
        try:
            self.pc.close()
        except:
            pass

    def do_cmd(self, cmd_text, timeout = 10):
        
        return self.cmd(cmd_text, timeout = timeout, return_as_list = False)

    def cmd(self, cmd_text, timeout = 10, return_as_list = True):
        """
        Excute an command
        """
        # empty input buffer and log if necessary
        self.log(self.pc.read_very_eager())
        # issue command
        logging.debug('[LINUX CMD INPUT] %s' % cmd_text)
        self.pc.write(cmd_text + "\r\n")
        ix, ox, cx = self.pc.expect([self.prompt])  # logs as side-effect
        logging.debug('[LINUX CMD OUTPUT] %s' % cx)

        if return_as_list:
            # split at newlines
            rl = cx.split("\n")
            # remove any trailing \r
            rl = [x.rstrip('\r') for x in rl]
            # filter empty lines and prompt
            rl = [x for x in rl if x and not x.endswith(']#') and not re.search(cmd_text, x)]
            return rl[0:] # remove cmd_text from output
        else:
            return cx

    def get_system_time(self, format = '%a %b %d %H:%M:%S %Y'):
        """
        Return the systime on the machine follow the format '%a %b %d %H:%M:%S %Y' by default
        """
        self.cmd('')
        #chen.tao 2014-2-24, to fix ZF-7565
        result = self.cmd('date +\"%s\"' % format)
        if len(result) >= 2:
            if 'date' in result[0]:
                return result[1]
            else:
                return result[0]
        else:
            return self.cmd('date +\"%s\"' % format)[0]

    def get_gmt_time(self, format = '%a %b %d %H:%M:%S %Y'):
        """
        Return the gmttime on the machine follow the format '%a %b %d %H:%M:%S %Y' by default
        """
        self.cmd('')
        #chen.tao 2014-2-24, to fix ZF-7565
        result = self.cmd('date -u +\"%s\"' % format)
        if len(result) >= 2:
            if 'date' in result[0]:
                return result[1]
            else:
                return result[0]
        else:
            return self.cmd('date -u +\"%s\"' % format)[0]

    def set_date_time(self, time_value):
        """
        Setting the datetime to the machine with time_value have format 'mmddHHMMYY'
        """
        self.cmd('')
        return self.cmd('date %s' % repr(time_value))

    def restart_syslog(self):
        '''
        restarting the syslog service
        '''
        self.cmd(r'/sbin/service syslog-ng restart')
        syslog_session = self.cmd("netstat -an | grep '0.0.0.0:514'")

        if not syslog_session:
            raise Exception(
                'Cannot restart syslog server. syslog-ng status: %s'%
                self.cmd('/sbin/service syslog-ng status')
            )

    def clear_syslog_messages(self, file_path = '/var/log/messages'):
        """
        Clear all syslog messages on the machine
        """
        return self.cmd(r'> %s' % file_path)

    def get_syslog_messages(self, file_path = '/var/log/messages'):
        """
        Get all syslog messages on the machine
        """
        return self.cmd(r'cat %s' % file_path)

    def get_syslog_messages_from(self, key, file_path = '/var/log/messages'):
        """
        Get all syslog messages on the machine have included the key
        """
        return [i for i in self.get_syslog_messages(file_path) if key in i]


    def delete_all_mails(self, dir = '/home/lab/Mail_Server/Inbox'):
        """
        Delete all mail on the default dirpath = 'Mail_Server/Inbox'
        """
        self.pc.write('rm %s/*.*\n' % dir)
        ix, ox, rx = self.pc.expect([self.prompt], 0.2)
        while ix == -1:
            self.pc.write('y\n')
            ix, ox, rx = self.pc.expect([self.prompt], 0.2)
        self.cmd('')

    def get_mails_list(self, dir = '/home/lab/Maildir/new/'):
        """
        Return a list of mail on the default dirpath = '/home/lab/Maildir/new/'
        """
        mail_list = self.cmd('ls -1 %s' % dir)
        mail_content = [self.cmd('cat %s/%s' % (dir, i), return_as_list = False) for i in mail_list]

        return mail_content

    def read_mails(self, dir = '/home/lab/Mail_Server/Inbox/'):
        """
        Return a list of mail on the default dirpath = 'Mail_Server/Inbox' follow format [mail_from, mail_to, title, message]
        """
        mail_list = self.cmd('ls -1 %s' % dir)
        mail_content = [self.cmd('cat %s/%s' % (dir, i)) for i in mail_list]

        mail_summary = []
        for i in mail_content:
            mail_from = ''
            mail_to = ''
            subject = ''
            message = ''

            for j in i:
                if 'From:' in j:
                    mail_from = j.split('From:')[1].strip()

                if 'Sender:' in j:
                    mail_from = j.split('Sender:')[1].strip()

                if 'To:' in j:
                    mail_to = j.split('To:')[1].strip()

                if 'Subject:' in j:
                    subject = j.split('\'')[1]

                if 'Full message:' in j:
                    message = j.split('message:')[1].strip()

            if mail_from and mail_to and subject and message:
                mail_summary.append([mail_from, mail_to, subject, message])

        return mail_summary

    def read_postfix_mails(self, dir = '/home/lab/Maildir/new'):
        """
        Also return a list of mails which follow format [mail_from, mail_to, title, message]
        """
        mail_name_list = self.cmd('ls -1 %s' % dir)
        mail_content_list = [self.cmd('cat %s/%s' % (dir, mail_name), return_as_list = False) for mail_name in mail_name_list]

        mail_summary_list = []
        for mail in mail_content_list:
            mail_from = ''
            mail_to = ''
            title = ''
            message = ''
            if 'Subject:' in mail:
                subject = mail.split('Subject:')[1].split('\r\n')[0]
                mail_from = subject.split('[')[1].split(']')[0].split(' ')[0]
                title = subject.split('\'')[1]

            if 'To:' in mail:
                mail_to = mail.split('To:')[1].split('\r\n')[0].strip()

            if 'Details:' in mail:
                message = mail.split('Details:')[1].split('\r\n')[1]

            if mail_from and mail_to and title and message:
                mail_summary_list.append([mail_from, mail_to, title, message])

        return mail_summary_list

    def kill_zing(self):
        session = self.cmd('pkill zing')

    def start_zing_server(self, tos = '', udp = '', port = '', tcp = ''):
        cmd_txt = './zing --server'
        if tos:
            cmd_txt = '%s -q%s' % (cmd_txt, tos)

        if port and tcp:
            cmd_txt = '%s -p%s' % (cmd_txt, port)
        #@zj 20140903 ZF-9927
        if udp or (port and udp):
            cmd_txt = '%s -u%s' % (cmd_txt, port)
        
#        if ((bool(port)^bool(tcp))^bool(tcp)) or udp:
#            cmd_txt = '%s -u%s' % (cmd_txt, port)
        logging.info('The command text is :%s' % cmd_txt)
        #@zj 20140903 ZF-9927
        
        self.cmd("%s &" % cmd_txt)

    def send_zing(self, host, udp = True, port = '', sending_time = 30):
        log_file = '/home/lab/zing.cvs'
        self.cmd('rm -f %s' % log_file)
        time.sleep(3)
        self.cmd('cd /home/lab')
        cmd = "./zing --client %s" % host
        if udp or port: cmd += ' -u%s' % port
        cmd += ' -S%s -f%s' % (sending_time, log_file)
        self.cmd(cmd)
        time.sleep(3)
        return self.collect_data('zing', log_file)

    def collect_data(self, toolname, result_file):
        """
        collect_data is a function called after the traffic is run.
        This function reads the traffic result file and collects the statistics
        of the run.
        @param toolname: name of the traffic generator; only "zap" is supported
        @param result_file: name of the CVS file
        @return: a dictionary of the traffic performance results
        """
        # pull the results out of the test log file
        rf = self.cmd('cat %s' % result_file, return_as_list = False)
        data = rf.split('\n')
        ##zj 2014-01-20
        #@author: chen.tao 2014-01-08 to fix ZF-6795
        if 'cat /home/lab/zing.cvs' in data[0]:
            del data[0]
        #@author: chen.tao 2014-01-08 to fix ZF-6795
        kdata = data[0].strip().split(',')
        keys = []
        for key in kdata:
            keys.append(key.strip('%'))

        vdata = data[1].strip().split(',')
        ##zj 2014-01-20
        values = []
        for value in vdata:
            values.append(value.strip())

        return dict(zip(keys, values))


    def get_dhcp_leases(self):
        cmd = "cat /var/lib/dhcpd/dhcpd.leases"
        return self.cmd(cmd)

    def get_ip_addr_in_dhcp_leases_by_mac_addr(self, mac_addr, debug=False):
        """
        dhcpd.leases as below:
        lease 20.0.2.200 {
        starts 4 2009/08/27 21:18:47;
        ends 5 2009/08/28 06:12:07;
        binding state active;
        next binding state free;
        hardware ethernet 00:90:7a:06:e1:f6;
        client-hostname "slnk-06e1f6";
        }
        .
        .

        """
        if debug:
            import pdb
            pdb.set_trace()
        cmd = "cat /var/lib/dhcpd/dhcpd.leases"
        rdata = self.do_cmd(cmd)
        sPattern = """lease\s*([0-9.]+)\s*\{"""
        sPattern += """\s*starts\s*\d+\s*(\d+/\d+/\d+\s*[\d:]+);"""
        sPattern += """\s*ends\s*\d+\s*(\d+/\d+/\d+\s*[\d:]+);"""
        sPattern += """\s*binding\s*\w+\s+\w+;"""
        sPattern += """\s*next\s*\w+\s*\w+\s*\w+;"""
        sPattern += """\s*hardware\s*\w+\s*([0-9a-f:]{17});"""
        sPattern += """\s*client-hostname\s*".*\";"""
        sPattern += """\s*\}"""
        curtime = time.strftime("%Y/%m/%d %H:%M:%S",time.gmtime())
        i = 0
        while True:
            m = re.search(sPattern, rdata[i:])
            if m:
                i = m.end() + i
                ip = m.group(1)
                starttime = m.group(2)
                endtime = m.group(3)
                mac = m.group(4)
                if (curtime > starttime) and (curtime < endtime) and (mac.lower() == mac_addr.lower()):
                    return ip
            else:
                return None


    def set_dhcp_option_43(self, enable_option, zd_ip_list = [], zdcode = "3"):
        """ Configure DHCP option 43 on the Linux server
        @param enable_option: boolean value to enable or disable
        @param zd_ip_list: list of IP address of ZDs
        @param zdcode: subcode of option 43 for ZD IP list
        """
        if enable_option and not zd_ip_list:
            logging.info("ZD IP address list was empty. No need to configure")
            return

        # Obtain the current DHCP server configuration
        # An Nguyen, Jun 2013. Check to make sure the first line return contain the command before remove it.
        tcmd = "cat /etc/dhcpd.conf"
        text = self.cmd(cmd_text = tcmd, return_as_list = False)
        text = text.split("\r\n")
        if tcmd in text:
            text = text[1:-1]

        # Search for option 43 definition
        rks_ext_name = None
        rks_ext_name_def_idx = None
        zd_ip_name = None
        zd_ip_name_def_idx = None
        rks_ext_declare_idx = None
        zd_ip_declare_idx = None
        idx = 0
        for line in text:
            # Look for the name of the vendor extension option
            if line.startswith("option space"):
                rks_ext_name = line.split()[2].strip(";")
                rks_ext_name_def_idx = idx
            # Look for the name of the ZD IP address list subcode
            elif rks_ext_name and not zd_ip_name and line.startswith("option %s" % rks_ext_name):
                x = line.split()
                if x[2].strip() == "code" and x[3].strip() == "3":
                    y = x[1].strip().split(".")
                    if rks_ext_name and y[0] == rks_ext_name:
                        zd_ip_name = y[1]
                        zd_ip_name_def_idx = idx
            elif rks_ext_name and line == "vendor-option-space %s;" % rks_ext_name:
                rks_ext_declare_idx = idx
            elif rks_ext_name and zd_ip_name and rks_ext_declare_idx and \
                 line.startswith("option %s.%s" % (rks_ext_name, zd_ip_name)):
                zd_ip_declare_idx = idx
            if rks_ext_name_def_idx and zd_ip_name_def_idx and \
               rks_ext_declare_idx and zd_ip_declare_idx: break
            idx += 1

        cfg_changed = False
        if enable_option:
            def_rks_ext_name = "ruckus_info"
            def_zd_ip_name = "zd_ip_list"

            if not rks_ext_name_def_idx:
                # Vendor extension information has not been defined
                # i.e. the line "option space ruckus_info;" was not found
                # Insert the definition to the beginning of DHCP configuration file
                rks_ext_name = def_rks_ext_name
                conf = "option space %s;" % rks_ext_name
                text.insert(0, conf)
                rks_ext_name_def_idx = 0
                cfg_changed = True
            if not zd_ip_name_def_idx:
                # Vendor extension information has not been defined
                # But zd_ip_list subcode has not been defined
                # i.e. the line "option ruckus_info.zd_ip_list code 3 = text" was not found
                # Insert the definition of zd_ip_list subcode to the configuration file, after the definition of the vendor extension
                zd_ip_name = def_zd_ip_name
                option_space_name = "%s.%s" % (rks_ext_name, zd_ip_name)
                conf = "option %s code 3 = text;" % option_space_name
                text.insert(rks_ext_name_def_idx + 1, line)
                zd_ip_name_def_idx = rks_ext_name_def_idx + 1
                cfg_changed = True
            if not rks_ext_declare_idx:
                # Vendor extension information has been defined, so has zd_ip_list subcode
                # But the vendor extension has not been declared
                # i.e. the line "vendor-option-space ruckus_info" was not found
                # Insert the declaration to the configuration file, after the definition of the zdsubcode
                conf = "vendor-option-space %s;" % rks_ext_name
                text.insert(zd_ip_name_def_idx + 1, conf)
                rks_ext_declare_idx = zd_ip_name_def_idx + 1
                cfg_changed = True
            if not zd_ip_declare_idx:
                # All the definition has been defined
                # Except the declaration of zd IP address list
                # i.e. the line "option ruckus_info.zd_ip_list '192.168.0.2'" was not found
                # Insert the line after the declaration of the vendor extension
                conf = "option %s.%s \"%s\";" % (rks_ext_name, zd_ip_name, ",".join(zd_ip_list))
                text.insert(rks_ext_declare_idx + 1, conf)
                cfg_changed = True
            else:
                # It has been declared
                # Need to check if the ZD IP address list is correct or not
                conf = "option %s.%s \"%s\";" % (rks_ext_name, zd_ip_name, ",".join(zd_ip_list))
                if text[zd_ip_declare_idx] != conf:
                    text[zd_ip_declare_idx] = conf
                    cfg_changed = True
        else:
            if rks_ext_declare_idx:
                del text[rks_ext_declare_idx]
                if zd_ip_declare_idx and zd_ip_declare_idx > rks_ext_declare_idx:
                    zd_ip_declare_idx -= 1
                cfg_changed = True
            if zd_ip_declare_idx:
                del text[zd_ip_declare_idx]
                cfg_changed = True

        if cfg_changed:
            # Convert TAB character to spaces
            for idx in range(len(text)):
                text[idx] = text[idx].expandtabs(8)

            # Backup current DHCP configuration file
            self.cmd("echo 'y' | cp /etc/dhcpd.conf /etc/dhcpd.conf.bak")

            # Rewrite the file with updated content
            text = "\r\n".join(text)
            self.cmd("echo '%s' > /etc/dhcpd.conf" % text)

            # Reset dhcpd for the new change to take effect
            res = self.cmd("/sbin/service dhcpd restart")
            if not re.match("Starting dhcpd:.*OK", res[1]):
                raise Exception("Unable to restart dhcpd after changing its configuration file. Please check /var/log/message")

    def set_dhcp_option_15(self, enable_option, domain_name = "example.net", domain_name_server = ""):
        if enable_option and not domain_name:
            logging.info("Domain name was empty. No need to configure")
            return

        if not domain_name_server:
            server_ip = self.ip_addr
        else:
            server_ip = domain_name_server

        # Obtain the current DHCP server configuration
        # An Nguyen, Jun 2013. Check to make sure the first line return contain the command before remove it.
        tcmd = "cat /etc/dhcpd.conf"
        text = self.cmd(cmd_text = tcmd, return_as_list = False)
        text = text.split("\r\n")
        if tcmd in text:
            text = text[1:-1]

        # Look for option 15 definition or the first subnet definition
        option15_declare_idx = None
        server_ip_declare_idx = None
        first_subnet_idx = None
        idx = 0
        for line in text:
            if line.startswith("option domain-name-servers"):
                server_ip_declare_idx = idx
            elif line.startswith("option domain-name"):
                option15_declare_idx = idx
            elif line.startswith("subnet") and not first_subnet_idx:
                first_subnet_idx = idx
            idx += 1

        cfg_changed = False
        if enable_option:
            conf = "option domain-name \"%s\";" % domain_name
            if option15_declare_idx:
                # The definition has already declared
                # Make sure that the domain name is correct
                if text[option15_declare_idx] != conf:
                    text[option15_declare_idx] = conf
                    cfg_changed = True
            else:
                # It has not been declared
                # Insert the declaration before the first subnet definition
                if first_subnet_idx == None:
                    raise Exception("There was no definition of subnets in DHCP server")
                confs = [conf, ""]
                for line in confs:
                    text.insert(first_subnet_idx, line)
                    first_subnet_idx += 1
                option15_declare_idx = first_subnet_idx - 2
                cfg_changed = True

            conf = "option domain-name-servers %s;" % server_ip
            if server_ip_declare_idx:
                # The server IP address definition has already declared
                # Make sure that it is correct
                if text[server_ip_declare_idx] != conf:
                    text[server_ip_declare_idx] = conf
                    cfg_changed = True
            else:
                # It has not been declared
                # Insert the declaration after the domain name definition
                text.insert(option15_declare_idx + 1, conf)
                cfg_changed = True
        else:
            if option15_declare_idx:
                # It has been declared, remove it
                del text[option15_declare_idx]
                if server_ip_declare_idx and server_ip_declare_idx > option15_declare_idx:
                    server_ip_declare_idx -= 1
                # Remove the next empty line if it exists
                if not text[option15_declare_idx]:
                    del text[option15_declare_idx]
                    if server_ip_declare_idx and server_ip_declare_idx > option15_declare_idx:
                        server_ip_declare_idx -= 1
                cfg_changed = True
            if server_ip_declare_idx:
                # It has been declared, remove it
                del text[server_ip_declare_idx]
                # Remove the next empty line if it exists
                if not text[server_ip_declare_idx]:
                    del text[server_ip_declare_idx]
                cfg_changed = True

        if cfg_changed:
            # Convert TAB character to spaces
            for idx in range(len(text)):
                text[idx] = text[idx].expandtabs(8)

            # Backup current DHCP configuration file
            self.cmd("echo 'y' | cp /etc/dhcpd.conf /etc/dhcpd.conf.bak")

            # Rewrite the file with updated content
            text = "\r\n".join(text)
            self.cmd("echo '%s' > /etc/dhcpd.conf" % text)

            # Reset dhcpd for the new change to take effect
            res = self.cmd("/sbin/service dhcpd restart")
            if not re.match("Starting dhcpd:.*OK", res[1]):
                raise Exception("Unable to restart dhcpd after changing its configuration file. Please check /var/log/message")

    def set_dhcp_lease_time(self, cfg_type, lease_time=""):
        """
            @author: Jane.Guo
            @since: 2013-5-9 Add for Force DHCP feature to modify dhcp lease time
            @param cfg_type: get -get the max lease time
                             set -set the max lease time
            @param lease_time: max lease time
            @return: the old max lease time
        """
        # Obtain the current DHCP server configuration
        text = self.cmd(cmd_text = "cat /etc/dhcpd.conf", return_as_list = False)
        #@author: Jane.Guo @since: 2013-06-18 fix bug sometimes the split method is wrong, it'll remove the first line
        text = text.split("\r\n")[0:-1]
        text.pop(0)
        # Look for max lease time
        max_lease_time_idx = None
        idx = 0
        for line in text:
            if line.startswith("max-lease-time "):
                max_lease_time_idx = idx
            idx += 1
        
        if not max_lease_time_idx:
            return ''

        cfg_changed = False
        old_conf = ""
        conf = "max-lease-time %s;" % lease_time
        if max_lease_time_idx:
            old_conf = re.match("max-lease-time\s*(\d.*)\s*;",text[max_lease_time_idx])
            if text[max_lease_time_idx] != conf:
                text[max_lease_time_idx] = conf
                if cfg_type == 'get':
                    cfg_changed = False
                elif cfg_type == 'set':
                    cfg_changed = True
        if cfg_changed:
            # Convert TAB character to spaces
            for idx in range(len(text)):
                text[idx] = text[idx].expandtabs(8)

            # Backup current DHCP configuration file
            self.cmd("echo 'y' | cp /etc/dhcpd.conf /etc/dhcpd.conf.bak")

            # Rewrite the file with updated content
            text = "\r\n".join(text)
            self.cmd("echo '%s' > /etc/dhcpd.conf" % text)

            # Reset dhcpd for the new change to take effect
            res = self.cmd("/sbin/service dhcpd restart")
            if not re.match("Starting dhcpd:.*OK", res[1]):
                raise Exception("Unable to restart dhcpd after changing its configuration file. Please check /var/log/message")
        return old_conf.group(1)

    def start_dhcp_server(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service dhcpd start'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep dhcpd')
        if not session:
            raise Exception('There no dhcpd session is started')

    def stop_dhcp_server(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service dhcpd stop'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep dhcpd')
        if session:
            raise Exception('The dhcpd session [%s] is not stopped' % repr(session))
        
    def delete_dhcp_leases(self):
        self.cmd('')
        cmd = '> /var/lib/dhcpd/dhcpd.leases'
        self.cmd(cmd)
        dhcp_lease = self.get_dhcp_leases()
        if dhcp_lease:
            raise Exception('The DHCP Lease is not deleted')


    def start_radius_server(self, service = "radiusd"):
        self.cmd('')
        cmd = '/sbin/service %s start' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if not session:
            raise Exception("There's no %s session started" % service)


    def stop_radius_server(self, service = "radiusd"):
        self.cmd('')
        cmd = '/sbin/service %s stop' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if session:
            raise Exception('The %s session [%s] was not stopped' %
                            (service, repr(session)))

    def restart_radius_server(self, service = "radiusd"):
        self.cmd('')
        cmd = '/sbin/service %s restart' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if not session:
            raise Exception("There's no %s session re-started" % service)


    def start_radius_server_output_to_file(self, file="nohup.out", service = "radiusd"):
        self.cmd('')
        cmd = '/sbin/service %s stop' % service
        self.cmd(cmd)
        time.sleep(3)
        
        self.cmd("cd  /home/lab/")
        self.cmd("touch %s" % file) 
        self.cmd("echo > %s" % file)
        
        cmd = 'nohup /usr/sbin/%s -x &' % service
        self.cmd(cmd)

#        session = self.cmd('pgrep %s' % service)
#        if not session:
#            raise Exception("There's no %s session started" % service)

    def verify_radius_server_auth_method(self, file="nohup.out", auth_str_list=''):
        cmd = "cat /home/lab/%s" % file
        data = self.cmd(cmd_text=cmd, return_as_list=False)
        
        self.cmd("echo > /home/lab/%s" % file)

        for str in auth_str_list:
            if str not in data:
                return False

        return True

    def get_radius_server_log_detail(self, file="nohup.out", clear_log=True):
        cmd = "cat /home/lab/%s" % file
        data = self.cmd(cmd_text=cmd, return_as_list=False)
        
        if clear_log == True:
            self.cmd("echo > /home/lab/%s" % file)

        return data

    DUMP_FILE = '/tmp/tcpdump_capture.pcap'
    TSHARK_FILE = '/tmp/tshark_capture.pcap'


    def get_interface(self):
        interface = self.cmd('/sbin/ifconfig')[0].split()[0]
        return interface


    def get_interface_name_by_ip(self, ip_addr, ip_type = CONST.IPV4):
        '''
        '''
        interface_info = self.get_if_cfg_Info(ip_type)
        if_name = ''
        for name in interface_info.keys():
            if interface_info[name]['ip_addr'] == ip_addr:
                if_name = name
                break

        if not if_name:
            raise Exception('There is not any interface whose IP address is %s' % ip_addr)

        else:
            return if_name
        
    def get_interface_info_by_ip(self, ip_addr, ip_type = CONST.IPV4):
        """
            Get interface infomation by ip 
            @author: Jane.Guo
            @since: 2013-7-22
        """
        interface_info = self.get_if_cfg_Info(ip_type)
        if_info = {}
        for name in interface_info.keys():
            if interface_info[name]['ip_addr'] == ip_addr:
                if_info = interface_info[name]
                break

        if not if_info:
            raise Exception('There is not any interface whose IP address is %s' % ip_addr)

        else:
            return if_info

    def create_virtual_interface(self, if_name, ip_addr, netmask):
        '''
        Creates a virtual interface
        @param if_name: interface name
        @param ip_addr: ip address
        @param netmask: netmask
        @return: {
            if_name: virtual interface name,
            ip_addr: interface ip address,
            if_is_up: True/False if the interface is up/down,
        }
        '''
        virtual_if_cfg = {
            'if_name': '',
            'ip_addr': '',
            'if_is_up': '',
        }

        i = 1
        if_ip_addr = "1"
        while True:
            virtual_if_name = if_name + ":" + str(i)
            if_ip_addr = self._get_ip_address(virtual_if_name)

            if if_ip_addr == "":
                command = "/sbin/ifconfig " + virtual_if_name + " " + ip_addr + " netmask " + netmask
                self.cmd(command)
                if_ip_addr = self._get_ip_address(virtual_if_name)

            if if_ip_addr == ip_addr:
                virtual_if_cfg.update({
                    'if_name': virtual_if_name,
                    'ip_addr': self._get_ip_address(virtual_if_name),
                    'if_is_up': True,
                })
                return virtual_if_cfg

            i = i + 1

        return virtual_if_cfg


    def del_interface(self, if_name):
        '''
        Deletes this interface
        @param if_name: interface name
        '''
        self.cmd("/sbin/ifconfig " + if_name + " down")


    def _get_ip_address(self, if_name):
        '''
        Gets IP Address of an interface
        @param if_name: interface name
        @return: ip address
        '''
        command =  "/sbin/ifconfig " + if_name + " | grep inet | awk '{print $2}' | sed -e s/.*://"
        ip_addr_list = self.cmd(command)
        ip_addr = "".join(ip_addr_list)
        ip_addr = ip_addr.strip()

        return ip_addr


    def get_if_cfg_Info(self, ip_type = CONST.IPV4):
        """
        Return a dictionary of all active network interface (except the local interface) that we have.
        Ex: /sbin/ifconfig
            eth1      Link encap:Ethernet  HWaddr 00:0C:29:FE:13:87
                      inet addr:192.168.0.252  Bcast:192.168.0.255  Mask:255.255.255.0
                      inet6 addr: fe80::20c:29ff:fefe:1387/64 Scope:Link
                      ...........

            lo        Link encap:Local Loopback
                      inet addr:127.0.0.1  Mask:255.0.0.0
                      ...........

            [root@localhost lab]#
            The return: {'eth1':{'ip_addr': '192.168.0.252', 'mac': '00:0C:29:FE:13:87',
                                 'mask': '255.255.255.0', 'link': 'Ethernet'}}
        """
        hardware_re = '([\w.:]+) +Link encap:([\w]+) +HWaddr ([0-9a-fA-F:]+)'
        info = self.cmd('/sbin/ifconfig', return_as_list = False)
        info = info.replace('/sbin/ifconfig', '')
        info = info.split('\r\n\r\n')
        interface_info = {}
        
        if ip_type == CONST.IPV4:
            address_re = 'inet addr:(\d+.\d+.\d+.\d+) +Bcast:(\d+.\d+.\d+.\d+) +Mask:(\d+.\d+.\d+.\d+)'
            for interface in info:
                interface = interface.strip()
                if interface and not interface.endswith(']#') and not interface.startswith('lo'):
                    hardware_info = re.findall(hardware_re, interface)
                    address_info = re.findall(address_re, interface)
                    if hardware_info and address_info:
                        name, link, mac = hardware_info[0]
                        ip_addr, bcast, mask = address_info[0]
                        interface_info[name] = {}
                        interface_info[name]['ip_addr'] = ip_addr
                        interface_info[name]['mask'] = mask
                        interface_info[name]['link'] = link
                        interface_info[name]['mac'] = mac
                        interface_info[name]['bcast'] = bcast
        elif ip_type == CONST.IPV6:
            address_re = 'inet6 addr: ([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{0,4}:){0,6}[0-9A-Fa-f]{1,4})/\d+ Scope:Global'
            
            for interface in info:
                interface = interface.strip()
                if interface and not interface.endswith(']#') and not interface.startswith('lo'):
                    hardware_info = re.findall(hardware_re, interface)
                    address_info = re.findall(address_re, interface)
                    if hardware_info and address_info:
                        name, link, mac = hardware_info[0]
                        ipv6_addr, colon = address_info[0]
                        interface_info[name] = {}
                        interface_info[name]['ip_addr'] = ipv6_addr

        return interface_info


    def start_tshark(self, params):
        self.stop_tshark()
        self.cmd('rm -f %s' % self.TSHARK_FILE)
        time.sleep(4)
        cmd = "/usr/sbin/tshark %s -c 1500 -V -w %s &" % (params, self.TSHARK_FILE)
        return self.cmd(cmd)
    
    def read_tshark(self, params = "", return_as_list = True):
        return self.cmd('/usr/sbin/tshark -r %s -V %s' % (self.TSHARK_FILE, params), return_as_list = return_as_list)
    
    def stop_tshark(self):
        self.cmd("pkill tshark")
    
    def start_sniffer(self, params):
        # always kill unexpect sniffer running before start new sniffer
        self.stop_sniffer()
        self.cmd('rm -f %s' % self.DUMP_FILE)
        time.sleep(4)
        cmd = "/usr/sbin/tcpdump -s 1500 %s -Uw %s &" % (params, self.DUMP_FILE)
        return self.cmd(cmd)

    def read_sniffer(self, params = "", return_as_list = True):
        return self.cmd('/usr/sbin/tcpdump -r %s -nnvtttt %s' % (self.DUMP_FILE, params), return_as_list = return_as_list)

    def stop_sniffer(self):
        self.cmd("pkill tcpdump")

    def set_route(self, option = "", ip_addr = "", net_mask = "", if_name = ""):
        """
        Add/delete multicast route which used to send multicast traffic with iperf
        - option: 'add' or 'del'
        """
        cmd = "/sbin/route %s -net %s netmask %s %s" % (option, ip_addr, net_mask, if_name)
        self.cmd(cmd)

    def add_route(self, ip_addr = "", net_mask = "", if_name = ""):
        self.set_route("add", ip_addr, net_mask, if_name)

    def delete_route(self, ip_addr = "", net_mask = "", if_name = ""):
        self.set_route("del", ip_addr, net_mask, if_name)

    def start_iperf(self, serv_addr = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = "", multicast_srv = False, port = 0):
        """
        Execute iperf to send traffic with the given configuration
        - serv_addr: ip_address of iperf server
        - test_udp: This is the bool value. If it's True, sent traffic is udp. Otherwise, sent traffic is tcp
        - packet_len: number of bytes of each packet
        - bw: bandwidth
        - timeout: maximum time to send traffic
        - tos: send traffic with ToS value
        - multicast_srv: option to bind multicast address to igmp table in the AP
        """
        cmd = "./iperf -C"
        if multicast_srv:
            cmd = "%s -s -B %s" % (cmd, serv_addr)
        else:
            if serv_addr: cmd = "%s -c %s" % (cmd, serv_addr)
            else: cmd = "%s -s" % cmd
        if test_udp: cmd = "%s -u" % cmd
        if packet_len: cmd = "%s -l %s" % (cmd, packet_len)
        if bw: cmd = "%s -b %s" % (cmd, bw)
        if timeout: cmd = "%s -t %s" % (cmd, timeout)
        if tos: cmd = "%s -S %s" % (cmd, tos)
        if port: cmd = "%s -p %s" % (cmd, port)
        cmd = "%s &" % cmd
        # Execute the command
        self.cmd(cmd)

    def start_iperf_server(self, serv_addr = "", test_udp = True):
        if serv_addr:
            self.start_iperf(serv_addr = serv_addr, test_udp = test_udp, multicast_srv = True)
        else:
            self.start_iperf(serv_addr = "", test_udp = test_udp, multicast_srv = False)

    def start_iperf_client(self, stream_srv = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = ""):
        self.start_iperf(serv_addr = stream_srv, test_udp = test_udp, packet_len = packet_len, bw = bw, timeout = timeout, tos = tos)


    def stop_iperf(self):
        self.cmd("pkill iperf")

    def start_tcp_replay(self, if_name = "", file_name = ""):
        self.cmd("tcpreplay -i %s %s" % (if_name, file_name))
        time.sleep(10)

###
# For scalability tests which should use the perform() to show the progress
# of tests.
###
    def send(self, _cmd):
        if self.conf['debug'] > 0 or self.conf['stdout']: print _cmd
        self.pc.write(_cmd + "\n")

    def recv(self, _timeout = None, _prompt = None):
        re = None
        if not _prompt:
            _p_list = [ self.re_prompt ]
        elif type(_prompt) is list:
            _p_list = _prompt[:]
        else:
            _p_list = [ _prompt ]
        indices = range(len(_p_list))
        for i in indices:
            if not hasattr(_p_list[i], "search"):
                _p_list[i] = re.compile(_p_list[i])
        if _timeout is not None:
            _time_start = time.time()
        (self.exp_state, self.exp_output, self.exp_recv_cnt) = (ExpState['EXPECT'], '', 0)

        while 1:
            if self.pc.eof: break
            self.exp_recv_cnt += 1

            _buf = self.pc.read_very_eager()
            if self.conf['debug'] > 1 :
                print "<<< " + str(self.exp_recv_cnt) + " >>> " + _buf

            if _buf and len(_buf) > 0 :
                self.exp_state = ExpState['DATA']
                if self.conf['stdout']:
                    print _buf,
                if self.log_file:
                    self.log_file.write(_buf)
                    self.log_file.flush()
                self.exp_output += _buf
                for i in indices:
                    m = _p_list[i].search(self.exp_output)
                    if m:
                        e = m.end()
                        self.exp_state = ExpState['MATCH']
                        return (i, m, self.exp_output)
            else:
                if self.exp_state == ExpState['EMPTY']:
                    if _timeout is not None:
                        _elapsed = time.time() - _time_start
                        if _elapsed >= _timeout:
                            self.exp_state = ExpState['TIMEOUT']
                            break
                else:
                    _time_start = time.time()

                self.exp_state = ExpState['EMPTY']
                time.sleep(self.conf['recv_pause'])

        _text = self.pc.read_very_lazy()
        if not _text and self.pc.eof:
            raise EOFError
        return (-1, None, _text)

    def perform(self, _cmd, _timeout = 10):
        self.send(_cmd)
        try:
            self.last_perform = self.recv(_timeout)
        except:
            self.last_perform = (-1, None, '')
        return self.last_perform

    def last(self):
        if not self.last_perform: return None
        (a, b, c) = self.last_perform
        if not b: return None
        return c

    def last_response(self, no_1st_line = 1):
        if not self.last_perform: return None
        (a, b, c) = self.last_perform
        if not b: return None

        if not no_1st_line: return c[0:b.start(0)]
        _m = re.search("\n", c)
        if not _m : return c[0:b.start(0)]
        return c[_m.end(0):b.start(0)]

    def last_prompt(self):
        if not self.last_perform: return None
        (a, b, c) = self.last_perform
        if not b: return None
        return c[b.start(0):b.end(0)]


    def is_vendor_option_43_set(self, vendor='ruckus_info'):
        '''
        This function is to check whether an option 43 is set for a vendor.
        Return True/False
        '''
        # Obtain the current DHCP server configuration
        data = self.cmd(cmd_text="cat /etc/dhcpd.conf", return_as_list=False)
        vendor_pat = 'option.*space.*' + vendor + '(|;)'
        return True if re.search(vendor_pat, data, re.I) else False

    def is_product_option_43_set(self, product=PRODUCT_INFO_FM, vendor='ruckus_info'):
        '''
        '''
        data = self.cmd(cmd_text="cat /etc/dhcpd.conf", return_as_list=False)
        product_header_pat = {
            self.PRODUCT_INFO_FM: 'option.*%s\.tr069_acs_url' % vendor,
            self.PRODUCT_INFO_ZD: 'option.*%s\.zdiplist' % vendor,
        }[product]
        return True if re.search(product_header_pat, data, re.I) else False

    # Tu Bui: this is used for FM --> will merge with ZD later
    def set_dhcp_option_43_fm(self, addr, product=PRODUCT_INFO_FM, vendor='ruckus_info', subnet=''):
        '''
        This function is to configure dhcp option 43 for fm or zd. It is to
        simplify the old function setDhcpOption43.
        - Do back up dhcpd.conf first
        - search vendor info of Ruckus
        - search dhcp option 43 for fm/zd
        - if vendor info is not set, set it.
        - if vendor info is not set, set it.
        Input:
        - product: 0 for FM
                   1 for ZD
        - subnet: default 192.168.30
        - addr: the ipaddr or url like http://itms.ruckus.com/intune/server
        NOTE: This function can support set dhcp 43 for global or subnet only
        IMPORTANT: HAVE NOT tested this function on real RedHat yet. It will
                   be done later
        '''
        # Obtain the current DHCP server configuration
        data = self.cmd(cmd_text="cat /etc/dhcpd.conf", return_as_list=False)

        vendor_set = 'option space %s;\r\n' % vendor
        is_vendor_set = self.is_vendor_option_43_set(vendor)
        # search dhcp option 43 for fm/zd
        product_set = {
            self.PRODUCT_INFO_FM: '%s.tr069_acs_url' % vendor,
            self.PRODUCT_INFO_ZD: '%s.zdiplist' % vendor,
        }[product]
        product_hearder_set = {
            self.PRODUCT_INFO_FM: 'option %s code 1 = text;\r\n' % product_set,
            self.PRODUCT_INFO_ZD: 'option %s code 3 = text;\r\n' % product_set,
        }[product]

        is_product_set = self.is_product_option_43_set(product, vendor)

        subnet_pat = 'subnet\s%s.*(|\s){\s' % subnet
        # - get the full setting of this subnet "subnet 192.168.0.0 netmask 255.255.255.0 {"
        subnet_set = re.search(subnet_pat, data, re.I).group(0)
        #- if vendor info is not set, set it at the position which is in front of
        # subnet string
        if not is_vendor_set:
            # Set vendor header info
            replace_str = vendor_set + subnet_set
            data = re.sub(subnet_pat, replace_str, data, 1)

        # if vendor hearder is not set, product option is not set neither
        if not is_vendor_set or not is_product_set:
            # Set product header, set it above string the first string "subnet" if
            # not subnet is empty. Otherwise, set it for that "subnet" only
            replace_str = product_hearder_set + subnet_set
            data = re.sub(subnet_pat, replace_str, data, 1)
            # Set dhcp option 43 of this product for global if no subnet is defined,
            # Otherwise, we set for that subnet only
            product_detail_set = ('vendor-option-space %s;\r\n' % vendor +
                                  'option %s "%s";\r\n' % (product_set, addr))
            replace_str = (subnet_set + product_detail_set)\
                          if subnet else\
                          (product_detail_set + subnet_set)

            # insert the prodcut detail setting into this subnet
            data = re.sub(subnet_pat, replace_str, data, 1)

        # finally, update dhcpd.conf if it change
        if not is_vendor_set or not is_product_set:
            self.cmd("echo '%s' > /etc/dhcpd.conf" % data)
            self.restart_dhcp_server()

    def replace_str(self, pattern, repl, s, replace_all=True):
        '''
        This function is to replace all or the first redundant string in the output
        command. Normally, it is the command we did
        - pattern: regular expression
        - replace_all: True, replace all. False replace the first occurence
        '''
        # get no of occurence of pattern in the data
        no = len(re.findall(pattern, s, re.I)) if replace_all else 1
        # replace all the command by empty string
        return re.sub(pattern, repl, s, no)

    def disable_option_43(self, product=PRODUCT_INFO_FM, vendor='ruckus_info'): #, subnet=''):
        '''
        This function is to disable option 43 of a product by doing comment out
        statements of option 43.
        NOTE: If there is no statements set for option 43, it will do nothing
        and return True.
        1. Comment out product header option 3
        2. Comment out product detail option 3 of a subnet

        @ NOTE: 1.Currently, re.sub() doesn't support flag re.I so we cannot use
        this function to replace. We need to get start pos and end pos to
        process the string
               2. We will disable all option 43 ((global and subnet)) for this product
               It is because, cannot define a pattern to match dhcp option 43 of this
               product for this network only
               3. Need to enhance that ignore options which was already commented out
        '''
        if not self.is_product_option_43_set(product, vendor) or \
           not self.is_vendor_option_43_set(vendor):
            logging.info('Not found dhcp option 43. No need to disable it')
            print 'Not found dhcp option 43. No need to disable it'
            return True
        # Obtain the current DHCP server configuration
        data = self.cmd(cmd_text="cat /etc/dhcpd.conf", return_as_list=False)
        #data = self._readfile()
        product_pat = {
            self.PRODUCT_INFO_FM: 'option( |\t)*%s\.tr069_acs_url' % vendor,
            self.PRODUCT_INFO_ZD: 'option( |\t)*%s\.zdiplist' % vendor,
        }[product]

        tmp, result, last_stop_pos = data, '', 0 # begin of the string
        for obj in re.finditer(product_pat, tmp, re.I):
            start_pos, end_pos = obj.start(), obj.end()
            result += self.COMMENT_SIGN + tmp[0:end_pos]\
                        if start_pos == 0 else \
                      tmp[last_stop_pos:start_pos] + self.COMMENT_SIGN + tmp[start_pos:end_pos]
            last_stop_pos = end_pos
        # After finish for loop, get the rest of the string
        result += tmp[last_stop_pos:]
        data = result

        # The data also contains the executed command "cat /etc/dhcpd.conf" so we
        # remove it before update the dhcpd.conf
        data = self.replace_str('cat /etc/dhcpd\.conf\r\n', '', data, True)
        data = self.replace_str('\[root@localhost lab\]\#', '', data, True)
        self.cmd("echo '%s' > /etc/dhcpd.conf" % data)
        self.restart_dhcp_server()

        return True

    def enable_option_43(self, product=PRODUCT_INFO_FM, vendor='ruckus_info'): #, subnet=''):
        '''
        This function is to enable option 43 of a product by doing un-comment
        statements of option 43 if they are commented out by disable_option_43.
        1. Un-comment header for product option

        @ NOTE: 1.Currently, re.sub() doesn't support flag re.I so we cannot use
        this function to replace. We need to get start pos and end pos to
        process the string
               2. We will disable all option 43 ((global and subnet)) for this product
               It is because, cannot define a pattern to match dhcp option 43 of this
               product for this network only
        '''
        if not self.is_product_option_43_set(product, vendor) or\
           not self.is_vendor_option_43_set(vendor):
            logging.info('Not found dhcp option 43. Cannot enable it')
            return False
        # Obtain the current DHCP server configuration
        data = self.cmd(cmd_text="cat /etc/dhcpd.conf", return_as_list=False)
        #data = self._readfile()

        product_pat = {
            self.PRODUCT_INFO_FM: 'option( |\t)*%s\.tr069_acs_url' % vendor,
            self.PRODUCT_INFO_ZD: 'option( |\t)*%s\.zdiplist' % vendor,
        }[product]
        comment_sign_pat = self.COMMENT_SIGN + '.*' + '(?=%s)' % product_pat

        tmp, result, stop_pos = data, '', 0 # begin of the string
        for obj in re.finditer(comment_sign_pat, tmp, re.I):
            start_pos, end_pos = obj.start(), obj.end()
            result += '' if start_pos == 0 else tmp[stop_pos:start_pos]
            stop_pos = end_pos
        # After finish for loop, get the rest of the string
        result += tmp[stop_pos:]
        data = result

        # The data also contains the executed command "cat /etc/dhcpd.conf" so we
        # remove it before update the dhcpd.conf
        data = self.replace_str('cat /etc/dhcpd\.conf\r\n', '', data, True)
        data = self.replace_str('\[root@localhost.*\]\#', '', data, True)
        self.cmd("echo '%s' > /etc/dhcpd.conf" % data)
        self.restart_dhcp_server()

        return True

    def restart_dhcp_server(self, pause=5):
        self.cmd('')
        cmd = '/sbin/service dhcpd restart'
        self.cmd(cmd)
        logging.info("wait %s sec to verify dhcp service start" % pause)
        time.sleep(pause)
        session = self.cmd('pgrep dhcpd')
        if not session:
            raise Exception('The dhcpd session [%s] is not restarted' % repr(session))

    def start_syslog(self):
        '''
        . start syslog server
        Note: this function is written/checked on Red Hat 5. Not check
        compability with Fedora yet.
        '''
        syslog_session = self.cmd("netstat -an | grep '0.0.0.0:514'")
        if not syslog_session:
            # Start syslog-ng
            self.cmd('/sbin/service syslog-ng start')
            syslog_session = self.cmd("netstat -an | grep '0.0.0.0:514'")

            if not syslog_session:
                raise Exception(
                    'Cannot start syslog server. Syslog-ng status: %s'
                    % self.cmd('/sbin/service syslog-ng status')
                )


    def ping(self, target_ip, timeout_ms = 1000):
        '''
        '''
        cmd = 'ping %s -c 4 -W 1' % target_ip
        ofmt = '(\d+) packets transmitted, (\d+) received, (\d+)% packet loss.*'
        goodreply = '(\d+) bytes from [0-9.]+: icmp_seq=(\d+) ttl=(\d+).*'
        timeout_s = timeout_ms / 1000.0
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < timeout_s:
            data = self.do_cmd(cmd)
            current_time = time.time()
            m = re.search(ofmt, data, re.M | re.I)
            if m and int(m.group(3)) == 0:
                if re.search(goodreply, data, re.I):
                    return "%.1f" % (current_time - start_time)

        return "Timeout exceeded (%.1f seconds)" % timeout_s
    
    
    def start_dns_server(self, service = "named"):
        self.cmd('')
        cmd = '/sbin/service %s start' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if not session:
            raise Exception("There's no %s session started" % service)


    def stop_dns_server(self, service = "named"):
        self.cmd('')
        cmd = '/sbin/service %s stop' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if session:
            raise Exception('The %s session [%s] was not stopped' %
                            (service, repr(session)))

    def restart_dns_server(self, service = "named"):
        self.cmd('')
        cmd = '/sbin/service %s restart' % service
        self.cmd(cmd)
        session = self.cmd('pgrep %s' % service)
        if not session:
            raise Exception("There's no %s session re-started" % service)
        
    def start_snmptrap(self, filename, params):
 
        '''
        Description:
            This function runs SNMPTrap.py to simulate trap servers to listen on port 162 and receive the trap messages from ZD.
            And after finishing reiceiving trap messags, save them into a file.
        Input:
            filename: the file name for trap messages to be saved
            paparams: the format is like params = 'filename="trapInfo" version=2 server_ip="192.168.0.252" timeout=200'
                      filename, server_ip, version are necessary, defaut timeout is 120s, the value of timeout should to be set according to trap type
        Output:
            None
        '''
        
        self.cmd("cd /home/lab/SNMPTrap")
        self.cmd('rm -rf %s' % filename)      
        
        cmd = "python SNMPTrap.py %s\r\n" % params
        self.pc.write(cmd + "\r\n")
        return
    
    def read_snmptrap(self, filename):
        
        '''
        Description: 
            This function was used to read trap messages from the file saved at start_snmptrap to verify defined trap message is sent to trap servers.
        Input:
            filename: the file name of trap memesages saved
        Output:
            trap message list
        '''
        self.cmd("cd /home/lab/SNMPTrap")
        cmd = "cat %s" % filename
        self.pc.write(cmd + "\r\n")
        time.sleep(5)
        data = self.pc.read_very_eager()
        data = self.replace_str('%s\r\n' % cmd, '', data, True)
        #@ChenTao ZF-10168
        #data = self.replace_str('\[(lab|root)@localhost SNMPTrap\]\#', '', data, True)   
        data = self.replace_str('\[(lab|root)@.*\]\#', '', data, True)         
        return eval(data)
    
    def rename_file(self,src_name='',dst_name='users',folder='/etc/raddb'):
        self.cmd('')
        self.cmd('cd %s'%folder)
        self.cmd('mv %s %s'%(src_name,dst_name))
        
        rat1=self.cmd('ls |grep ^%s$'%dst_name)
        rat2=self.cmd('ls |grep ^%s$'%src_name)
        if not dst_name in rat1 or src_name in rat2:
            logging.info("dst %s -- rat1 %s, src %s -- rat2 %s" % (dst_name, rat1, src_name, rat2))
            return False
        return True
        

    def restart_service(self, service = ""):
        self.cmd('')
        cmd = '/sbin/service %s stop' % service
        self.cmd(cmd)
        time.sleep(5)
        session = self.cmd('pgrep %s' % service)
        if session:
            logging.info('service stop failed')
            return False
        time.sleep(5)
        cmd = '/sbin/service %s start' % service
        self.cmd(cmd)
        time.sleep(5)
#        session = self.cmd('pgrep %s' % service)
#        if not session:
#            logging.info('service start failed')
#            return False
        return True
    
    def start_ping_station_wifi_addr(self, filename, wifiaddr):
 
        '''
        Description:
            This function is used to ping the wifi address of station and save the ping results to a file.
            
        Input:
            filename: the file name for ping results to be saved
            wifiaddr: the wifi address of station
            'ping 192.168.0.128 >pingResultnew.txt'
        Output:
            None
        '''
        
        self.cmd("cd /home/lab")
        self.cmd('rm -rf %s' % filename)      
        
        cmd = "ping %s >%s" % (wifiaddr, filename)
        self.pc.write(cmd + "\r\n")
        return
    
    def read_ping_station_results(self, filename):
        
        '''
        Description: 
            This function was used to read ping results from the file saved at start_ping_station_wifi_addr"
        Input:
            filename: the file name of ping results saved
        Output:
            ping result
        '''
        self.cmd("cd /home/lab")
        cmd = "cat %s" % filename
        self.pc.write(cmd + "\r\n")
        time.sleep(10)
        data = self.pc.read_very_eager()
        data = self.replace_str('%s\r\n' % cmd, '', data, True)
        data = self.replace_str('\[(lab|root)@localhost lab\]\#', '', data, True)      
        return data
        
    def restart_dhcpd6(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service dhcpd6 restart'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep dhcpd')
        if not session:
            raise Exception('There no dhcpd session is restarted')

    def stop_dhcpd6(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service dhcpd6 stop'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep dhcpd')
        if session:
            raise Exception('The dhcpd session [%s] is not stopped' % repr(session)) 
        
    def restart_radvd(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service radvd restart'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep radvd')
        if not session:
            raise Exception('There no radvd session is restarted')

    def stop_radvd(self, pause=10):
        self.cmd('')
        cmd = '/sbin/service radvd stop'
        self.cmd(cmd)
        time.sleep(pause)
        session = self.cmd('pgrep radvd')
        if session:
            raise Exception('The radvd session [%s] is not stopped' % repr(session))

    def generate_sr_license(self,sn,generate_info,file_name,file_dir = '/home/lab/zd_sr_license'):
        cmd = "cd " + file_dir
        self.cmd(cmd)
        self.cmd('rm -rf %s'%file_name)
        cmd = "./gen_license.sh %s order123 %s %s"%(generate_info,sn,file_name)
        self.cmd(cmd)
        return self.verify_file_exist(file_dir,file_name)

    def verify_file_exist(self,file_dir,file_name):
        cmd = "cd " + file_dir
        self.cmd(cmd)
        res = self.cmd('ls |grep %s'%file_name)
        if file_name not in res:
            return False
        return True
