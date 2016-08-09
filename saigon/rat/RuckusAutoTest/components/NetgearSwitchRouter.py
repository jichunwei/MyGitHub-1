"""
    Subclass of NetgearL3Switch.
    Has all the functionalities of NetgearL3Switch and more.

    The main function is do_cfg() that allows you to configure
    the netgear by passing the config command block.
    NegearL3Switch._expect_prompt() was modified to support do_cfg().

    Please see the following example for howto use the component.

Example:

    from ratenv import *
    from RuckusAutoTest.components import NetgearSwitchRouter
    ng2 = NetgearSwitchRouter.NetgearSwitchRouter(dict())
    data = ng2.perform('show interface 1/0/12')
    print data
    ng2.remove_all_interface_vlan('1/0/12')
    cmd_block1 = ng2.get_auto_test_default_interface_cfg_cmds('1/0/12')
    cmd_block2 = ng2.get_default_interface_cmds('1/0/12')
    ng2.do_cfg(cmd_block1)
    data = ng2.perform('show run interface 1/0/12', print_out=False)
    print data
"""

import re
import logging
from string import Template

from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
from RuckusAutoTest.common import lib_Debug as bugme
# when not move nsr_hlp here as class's methods? add/mod functions without kill/create class's instance
from RuckusAutoTest.components.lib.zd import nsr_hlp as HLP

#
# Automation standard parameters (for reference only)
#
AUTOTEST_VLAN = dict(native = 301, mgmt_zd = 301, mgmt_ap = 302, l3test = 333, testLowNumber = 2, testHighNumber = 3677)

#
# Config command templates
#
TMPL_AUTOTEST_STD_INTF_CONF_t = """
interface $interface
    vlan pvid 301
    vlan participation auto 1
    vlan participation include 2
    vlan tagging 2
    vlan participation include 301
    vlan participation include 302
    vlan tagging 302
    vlan participation include 3677
    vlan tagging 3677
exit
"""

TMPL_ADD_INTF_TAG_VLAN_t = """
interface $interface
    vlan participation include $vid
    vlan tagging $vid
"""

TMPL_CHANGE_PVID_t = """
interface $interface
    vlan pvid $pvid_new
    vlan participation auto $pvid_original
    vlan participation include $pvid_new
exit
"""

TMPL_REMOVE_INTF_VLAN_t = """
interface $interface
    vlan participation auto $vlan
"""

netgear_prompts = []
# user exec prompt, getp() return 1
netgear_prompts.append(re.compile(r'\(FSM\d+[^\)]+\)\s+\>', re.M | re.I))
# priv exec prompt, getp() return 2
netgear_prompts.append(re.compile(r'\(FSM\d+[^\)]+\)\s+\#', re.M | re.I))
# configure terminal mode entry, getp() return 3
netgear_prompts.append(re.compile(r'\(FSM\d+[^\)]+\)\s+\(Config\)#', re.M | re.I))
# configure an object prompt, getp() return 4
netgear_prompts.append(re.compile(r'\(FSM\d+[^\)]+\)\s+\([^\)]+\)#', re.M | re.I))

class NetgearSwitchRouter(NetgearL3Switch):
    def __init__(self, config):
        NetgearL3Switch.__init__(self, config)

    def get_default_interface_cmds(self, interface):
        return self.get_auto_test_default_interface_cfg_cmds(interface)

    def get_auto_test_default_interface_cfg_cmds(self, interface):
        cmd_blocks = Template(TMPL_AUTOTEST_STD_INTF_CONF_t).substitute(dict(interface = interface))
        return cmd_blocks

    # specialized command assuming you are using the automation's stardardized configuration
    def change_interface_native_vlan(self, interface, native_vlan_new, native_vlan_original = None, print_out = True):
        return self._change_interface_pvid(interface, native_vlan_new, native_vlan_original, print_out)

    def change_interface_pvid(self, interface, pvid_new, pvid_original = None, print_out = True):
        return self._change_interface_pvid(interface, pvid_new, pvid_original, print_out)

    def _change_interface_pvid(self, interface, pvid_new, pvid_original = None, print_out = True):
        if self.conf['debug']:
            bugme.pdb.set_trace()
        if not pvid_original:
            cmd_line = "show running-config interface %s" % (interface)
            data = self.do_cmd(cmd_line, netgear_prompts)
            if print_out:
                print data
            m = re.search(r"^\s*vlan\s+pvid\s+(\d+)", data, re.M)
            if not m:
                raise Exception("Is interface %s valid? Can not find pvid:\n%s" % (interface, data))
            pvid_original = m.group(1)
        dd = dict(interface = interface, pvid_original = pvid_original, pvid_new = pvid_new)
        chgPvidCmdBlock = Template(TMPL_CHANGE_PVID_t).substitute(dd)
        if print_out and self.conf['debug']:
            print "[DEBUG] Configure those command:\n%s" % chgPvidCmdBlock
        data = self.do_cfg(chgPvidCmdBlock, print_out)
        return data

    def remove_interface_vlan(self, interface, print_out = True):
        return self.remove_all_interface_vlan(interface, print_out)
        
    def remove_all_interface_vlan(self, interface, print_out = True):
        cmd_line = "show running-config interface %s" % (interface)
        data = self.do_cmd(cmd_line, netgear_prompts)
        if print_out:
            print data
        
        cfgCmdBlock = "interface %s" % interface
        for line in data.split('\n'):
            m = re.match(r"\s*vlan participation\s+([^\s]+)\s+(\d+)", line)
            if m:
                cfgCmdBlock += "\nvlan participation auto %s" % m.group(2)
        self.do_cfg(cfgCmdBlock, print_out = print_out)
        cmd_line = "show running-config interface %s" % (interface)
        data = self.do_cmd(cmd_line, netgear_prompts)
        return data

    def add_interface_tag_vlan(self, intf, vid, pout=True):
        return self._add_interface_tag_vlan(intf, vid, pout)

    def _add_interface_tag_vlan(self, intf, vid, pout=True):
        if self.conf['debug']:
            bugme.pdb.set_trace()
        dd = dict(interface=intf, vid = vid)
        chgvidCmdBlock = Template(TMPL_ADD_INTF_TAG_VLAN_t).substitute(dd)
        if pout and self.conf['debug']:
            print "[DEBUG] Configure those command:\n%s" % chgvidCmdBlock
        data = self.do_cfg(chgvidCmdBlock, pout)
        return data

    # Examples:
    #
    #   from ratenv import *
    #   from RuckusAutoTest.components import NetgearSwitchRouter
    #   ng2 = NetgearSwitchRouter.NetgearSwitchRouter(dict())
    #   cmdblock = """interface 1/0/12
    #       vlan pvid 301
    #       vlan participation include 2
    #       vlan tagging 2
    #       vlan participation include 302
    #       vlan tagging 302
    #       vlan participation include 3677
    #       vlan tagging 3677
    #   """
    #   ng2.do_cfg(cmdblock)
    #   cmdblock = """interface range 1/0/1-1/0/12
    #       shutdown
    #   """
    #   ng2.do_cfg(cmdblock)
    #
    def do_cfg(self, cmd_block, print_out = True):
        if self.conf['debug']:
            bugme.pdb.set_trace()
        self.position_at_priv_exec_mode()
        lresp = self.do_cmd('configure terminal', netgear_prompts)
        if print_out:
            print lresp
        for cmd_line in cmd_block.split('\n'):
            lresp = self.do_cmd(cmd_line.strip(), netgear_prompts)
            if print_out:
                print lresp
        ppos = self.getp(lresp)
        if ppos == 1:
            return self.step_into_priv_exec_mode()
        return self.back_to_priv_exec_mode()

        
    def back_to_priv_exec_mode(self):
        try:
            self.telnet_client.write("\032")
        except socket.error:
            logging.info("Telnet session has been disconnected. Try to relogin")
            self.login()
        return self._expect_prompt(netgear_prompts)


    def getp(self, data):
        for idx, ptn in enumerate(netgear_prompts):
            m = ptn.search(data)
            if m:
                return (idx + 1)
        return 0

    def perform(self, cmd_line = '', timeout = 0, print_out = True):
        # if we not at at user/priv exec mode; force it to user/priv mode
        data = self.do_cmd('', netgear_prompts, timeout)
        if not cmd_line:
            return data
        if self.getp(data) > 2:
            self.back_to_priv_exec_mode()
        return self._perform(cmd_line, timeout, print_out)

    def _perform(self, cmd_line = '', timeout = 0, print_out = True):
        data = self.do_cmd(cmd_line, netgear_prompts, timeout)
        if print_out:
            print data
        return data

    def position_at_priv_exec_mode(self, timeout = 0, print_out = True):
        cnt = 5
        while cnt > 0:
            data = self.do_cmd('', netgear_prompts, timeout)
            if print_out:
                print data
            climode = self.getp(data)
            if climode == 1:
                return self.step_into_priv_exec_mode()
            elif climode > 2:
                self.back_to_priv_exec_mode()
            elif climode == 2:
                return
            cnt -= 1

