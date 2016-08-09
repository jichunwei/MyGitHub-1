# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.

"""
HuaweiL3Switch interfaces with Huawei L3 managed switch via telnet CLI.
@author: An Nguyen
@contact: an.nguyen@ruckuswireless.com
@since: April 2012

Example:

    from ratenv import *
    ng = HuaweiL3Switch.HuaweiL3Switch(dict(init=False))
    ng.initialize()
    d1 = ng.do_cmd('show mac-addr-table')
    print d1

"""
import time
import logging
import re
import telnetlib
import socket
from copy import deepcopy
from RuckusAutoTest.models import TestbedComponent, ComponentBase
from RuckusAutoTest.common.Ratutils import *

class HuaweiL3Switch(ComponentBase):
    def __init__(self, config):
        """
        Component's constructor
        Initialized configuration should include the following values:
        - ip_addr: IP address of the switch
        - prompt: the based prompt on the CLI of the switch
        - timeout: default timeout value to be used in expect commands
        """
        component_info = TestbedComponent.objects.get(name = "HuaweiL3Switch")
        ComponentBase.__init__(self, component_info, config)
        self.conf = dict(ip_addr = '192.168.0.253',
                         prompt = "[a-zA-Z0-9]+", #An Nguyen: change to use the regex to cover all Netgear Switch name
                         timeout = 15,
                         init = True,
                         debug = 0
                         )
        self.conf.update(config)
        if self.conf['init']: self.initialize()
        #@author:chen.tao 2014-10, self.mac_addr is the mgmt mac addr of the switch
        self.mac_addr = self.get_switch_mac_addr()
        self.delete_all_port_isolate_groups()
    def initialize(self):
        self.branch = 'huawei'
        self.ip_addr = self.conf['ip_addr']
        self.prompt = self.conf['prompt']
        self.user_exec_prompt = "%s>" % self.prompt
        self.priv_exec_prompt = "%s]" % self.prompt
#        self.global_cfg_prompt = "%s \(Config\)#" % self.prompt Quidway-Ethernet0/0/15
        self.interface_cfg_prompt = "%s-[\w]+[0-9/]+\]" % self.prompt
#        self.interface_range_cfg_prompt = "%s \(conf-if-range-[0-9/\-]+\)#" % self.prompt
        self.timeout = int(self.conf["timeout"])

        self.more_or_quit_prompt = re.escape("---- More ----")

        self.login()
        logging.info("Created HuaweiL3Switch %s" % self.ip_addr)

    def _expect(self, expect_list, timeout = 0):
        """
        A wrapper around the telnetlib expect().
        This uses the configured timeout value.
        Returns the same tuple as telnetlib expect()
        """
        if not timeout:
            timeout = self.timeout
        ix, mobj, rx = self.telnet_client.expect(expect_list, timeout)
        return (ix, mobj, rx)

    def _expect_prompt(self, prompt = "", timeout = 0):
        """Expect a prompt and raise an exception if we don't get one. Returns only input."""
        if self.conf['debug']:
            import pdb
            pdb.set_trace()
        if not prompt:
            target_prompts = [self.prompt, self.more_or_quit_prompt]
        elif type(prompt) is list:
            target_prompts = prompt[:]
            target_prompts.append(re.compile(self.more_or_quit_prompt, re.M | re.I))
        else:
            target_prompts = [prompt, self.more_or_quit_prompt]
        mqp_pos = len(target_prompts) - 1

        buf = ""
        while True:
            timeout = 6 if timeout == 0 else timeout
            ix, mobj, rx = self._expect(target_prompts, timeout)
            if ix == -1:
                raise Exception("Prompt %s not found in %s" % (target_prompts , rx))
            buf += rx
            # Quit the loop if the prompt is found
            if ix != mqp_pos: break
            # Otherwise, press Enter to continue showing
            self.telnet_client.write("\n")

        return buf

    def close(self):
        """Terminate the telnet session"""
        try:
            self.telnet_client.close()
        except:
            pass

    def login(self):
        """
        Login to the switch and enter privileged exec mode.
        If a telnet session is already active this will close that session and create a new one.
        """
        self.close()
        self.telnet_client = telnetlib.Telnet(self.ip_addr)

        # Try to login privileged exec mode
        self.step_into_priv_exec_mode()

    def step_into_priv_exec_mode(self):
        self.telnet_client.write("system-view\n")
        logging.info("Telnet_cmd is system-view\n")
        
        try:
            self._expect_prompt(self.priv_exec_prompt)
        except Exception, e:
            logging.info("Telnet session had been disconnected. Try to relogin")
            self.login()
            time.sleep(1)
            self.telnet_client.write("system-view\n")
            self._expect_prompt(self.priv_exec_prompt)

    def do_cmd(self, cmd_text, prompt = "", timeout = 0):
        return self._do_cmd(cmd_text, prompt = prompt, timeout = timeout, return_raw = True)

    def _do_cmd(self, cmd_text, prompt = "", timeout = 0, return_raw = False):
        """
        Issue the specified cmd_text and return the complete response
        as a list of lines stripped of the following:
           Echo'd cmd_text
           CR and LR from each line
           Final prompt line
        A timeout value of 0 means use the default configured timeout.
        """
        if not prompt:
            # Default to privileged exec mode
            prompt = self.priv_exec_prompt
        if not timeout:
            timeout = self.timeout

        try:
            # Empty input buffer
            self.telnet_client.read_very_eager()
            # Issue command
            logging.debug('[HWSW CMD INPUT] %s' % cmd_text)
            self.telnet_client.write(cmd_text + "\n")
            # Read data
            r = self._expect_prompt(prompt, timeout)
            logging.debug('[HWSW CMD OUTPUT] %s' % r)
        except (Exception):
            logging.info("Telnet session had been disconnected. Try to relogin")
            self.login()
            # Try to issue the command one more time
            self.telnet_client.write(cmd_text + "\n")
            # Read data
            r = self._expect_prompt(prompt, timeout)

        if return_raw: return r

        # Split at newlines
        rl = r.split("\n")
        # Remove any trailing \r
        rl = [x.rstrip('\r') for x in rl]
        # Filter empty lines and prompt
        rl = [x for x in rl if x and not x.startswith(prompt)]

        # Remove cmd_text from output and return the rest
        return rl[1:]

#    def _goto_global_cfg_mode(self):
#        """ Jump into global configuration mode """
#        self._do_cmd("configure terminal", self.global_cfg_prompt)
    
    def _read_interface_info(self, inf):
        """
        """
        if_type = {'': 'Ethernet',
                   'eth': 'Ethernet',
                   'ge': 'GigabitEthernet'}
#        Eth0/0/2
        pattern = '([a-zA-Z]*)([0-9/]+)'
        mobj = re.match(pattern, inf)
        inf_type = mobj.group(1)
        inf_port = inf.strip(inf_type)
        if_info = {'type': if_type[inf_type.lower()],
                   'inf': inf_port,
                   'interface': if_type[inf_type.lower()]+inf_port}
        return if_info
    
    def _goto_interface_cfg_mode(self, inf):
        """ Jump into interface configuration mode """
        self._do_cmd("interface %s" % inf, self.interface_cfg_prompt)

#    def _goto_interface_range_cfg_mode(self, inf_range):
#        """ Jump into range interface configuration mode """
#        self._do_cmd("interface range %s" % inf_range, self.interface_range_cfg_prompt)

    def _goto_priv_exec_mode(self):
        """ Jump back to privileged exec mode from any modes except user exec mode """
        self.telnet_client.write("return\n")
        self.step_into_priv_exec_mode()

    def ping(self, target_addr):
        """ Perform a ping from the switch to a target device """
        res = self._do_cmd("ping %s" % target_addr)

        mobj = re.search("Receive count=([0-9]+)", res[0])
        if mobj and int(mobj.group(1)) > 0:
            return True
        return False

    def get_mac_table(self):
        """ Return the MAC table on the switch """
        res = self._do_cmd("display mac-address")
        "044f-aa2e-e450 1           -      -      Eth0/0/2        dynamic   -"
        #@author: Anzuo, to adapt Huawei SW VRP (R) Software, Version 5.70 (V100R006C03) and VRP (R) Software, Version 5.70 (S3700 V100R005C01SPC100)
        pattern = r"([0-9a-f\-]{14}) +([0-9]{1,4}).* + .* +([\w0-9/]+) + ([a-zA-Z]+)"
#        pattern = r"([0-9a-f\-]{14}) +([0-9]+) + .* +([\w0-9/]+) + ([a-zA-Z]+)"
        mac_table = []
        for line in res:
            mobj = re.match(pattern, line)
            if not mobj: continue            
            mac_table.append({"mac":mac_address_standardized(mobj.group(1)).lower(), 
                              "inf":self._read_interface_info(mobj.group(3))['interface'],
                              "vlan":mobj.group(2), "status":'Learned'})
        return mac_table
    
    def get_disabled_interface(self):
        """ get the disabled interfaces """
        
        disable_int_list = []
        res = self._do_cmd("display interface brief | I *down")
        for x in res:
            if " *down " in x:
                disable_int_list.append(x.split()[0])
        logging.info("Disabled interface: %s" % disable_int_list)        
        return disable_int_list
        

    def get_mac_by_interface(self, interface = 'Ethernet 0/0/1'):
        """
            Return the MAC if interface on the switch 
            @author: Jane.Guo
            @since: 2013-7-22
        """
        res = self._do_cmd("display interface %s" %interface )
        #Hardware address is 1047-8025-896a
        pattern = "Hardware address is (.*)"
        mac = ""
        for line in res:
            mobj = re.search(pattern, line)
            if not mobj: continue 
            mac = mobj.group(1)
            break
        
        mac_new = ""
        #1047-8025-896a to 10:47:80:25:89:6a
        if mac:
            mac = mac.replace('-','')
            for i in range(0,6):
                mac_new += str(mac[i*2:i*2+2])
                if not i == 5:
                    mac_new += ":"  

        return mac_new
          
    def get_vlan_ip_table(self):
        """ Return the show ip vlan on the switch"""
        res = self.do_cmd("display ip interface")
        ip_pattern = r"Internet Address is ([0-9.]+)\/([0-9]+)"
        inf_pattern = r"if([0-9]+)"
        subnet_match = {'22': '255.255.252.0',
                        '23': '255.255.254.0',
                        '24': '255.255.255.0',
                        }
        
        res = res.split('Vlan')
        
        vlan_ip_table = []
        for info in res:
            inf = re.findall(inf_pattern, info)
            ip = re.findall(ip_pattern, info)
            if not inf or not ip: continue
            
            vlan_ip_table.append({"vlan_id":inf[0], "inf":'vlanif%s' % inf[0],
                                  "ip_addr":ip[0][0], "subnet_mask":subnet_match[ip[0][1]]})
        return vlan_ip_table

    def mac_to_interface(self, mac_addr):
        """ Detect the switch port that the device with given MAC address connects to """
        mac_table = self.get_mac_table()
        for device in mac_table:
            if device["mac"].upper() == mac_addr.upper():
                return device["inf"]
        return ""
    
	#@author:chen.tao 2014-10, in mesh env, ap's mac may exist in multiple ports in switch
    def mac_to_multi_interface(self, mac_addr):
        interface_list = []
        mac_table = self.get_mac_table()
        for device in mac_table:
            if device["mac"].upper() == mac_addr.upper():
                interface_list.append(device["inf"])
        return interface_list

    def enable_interface(self, inf):
        """
        Enable the given switch port. Use this function with care. Disable the port that connects
        to the test controller will terminate the telnet session
        """
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("undo shutdown", self.interface_cfg_prompt)
        self._goto_priv_exec_mode()
    
    def enable_range_interface(self, inf):
        """
        Enable the given switch port. Use this function with care. Disable the port that connects
        to the test controller will terminate the telnet session
        """
        for interface in inf:
            self.enable_interface(interface)

    def disable_interface(self, inf):
        """
        Disable the given switch port.
        """
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("shutdown", self.interface_cfg_prompt)
        self._do_cmd("display this")
        self._goto_priv_exec_mode()

    def verify_component(self):
        """ Device should already be logged in. """
        try:
            self._goto_priv_exec_mode()
        except:
            pass

    def add_interface_to_vlan(self, inf, vlan, set_pvid = True, tagging = False):
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)     
        
        if tagging:
            self._do_cmd("port hybrid tagged vlan %s" % vlan, self.interface_cfg_prompt)
        else:
            self._do_cmd("port hybrid untagged vlan %s" % vlan, self.interface_cfg_prompt)
            
        if set_pvid:
            self._do_cmd("port hybrid pvid vlan %s" % vlan, self.interface_cfg_prompt)
            
        self._goto_priv_exec_mode()

    def remove_interface_from_vlan(self, inf, vlan):
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        
        self._do_cmd("undo port hybrid vlan %s" % vlan, self.interface_cfg_prompt)
        self._do_cmd("undo port hybrid pvid vlan", self.interface_cfg_prompt)
        
        self._goto_priv_exec_mode()

    def get_vlan_interfaces(self):
        vlan_ip_table = self.get_vlan_ip_table()
        vlan_if_list = [] 
        for vlan in vlan_ip_table:
            vlan_if_list.append({"vlan_id": vlan["vlan_id"],
                                 "inf": vlan["inf"],
                                 "ip_addr": vlan["ip_addr"],
                                 "mask": vlan["subnet_mask"]})
        return vlan_if_list

#    def set_bandwidth(self, inf, bandwidth):
#        self._goto_global_cfg_mode()
#        self._goto_interface_range_cfg_mode(inf)
#        self._do_cmd("traffic-shape %s" % bandwidth, self.interface_range_cfg_prompt)
#        self._goto_priv_exec_mode()
    
    # An Nguyen, Mar 2013
    # Add the function to support execute the set of command (Reference to the NetgearSwitchRouter)
    def do_cfg(self, cmd_block, print_out = True):
        self._goto_priv_exec_mode()
        for cmd in cmd_block.split('\n'):
            cmd = cmd.strip()
            lresp = self.do_cmd(cmd)
            if print_out:
                print lresp
        self._goto_priv_exec_mode()
        
    def clear_mac_table(self):
        self._do_cmd("undo mac-address all")
    
    def configure_dhcp_relay(self, **kwargs):
        """
        This function is added to configure the dhcp relay option on Netgear Switch
        @author: An Nguyen, Jul 2013
        """
        relay_cfg = {'enable': True,
                     'vlans': [],
                     'dhcp_srv_ip': '192.168.0.252'}
        relay_cfg.update(kwargs)
        
        cmd_block = ""
        for vlan in relay_cfg['vlans']:
            cmd_block += 'interface vlanif %s\n' % vlan
            if relay_cfg['enable']:
                cmd_block += "dhcp select relay\ndhcp relay server-ip %s\nquit\n" % relay_cfg['dhcp_srv_ip']
            else:
                cmd_block += "undo dhcp select relay\nquit\n"
        
        self.do_cfg(cmd_block)

    def __del__(self):
        self.close()

#@author:chen.tao 2014-10, to support lldp configure in switch
    def get_switch_mac_addr(self,interface = 'Ethernet 0/0/1'):
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(interface)
        interface_info = self._do_cmd("display this interface", self.interface_cfg_prompt,\
                                      return_raw = True)
        self._goto_priv_exec_mode()
        mac_addr_pattern = 'Hardware\s*address\s*is\s*([0-9a-f\-]{14})'
        m = re.search(mac_addr_pattern,interface_info)
        if not m: raise Exception('Can not get switch mac address')
        else: return m.group(1)

#@author:chen.tao 2014-10, to support lldp configure in switch
    def enable_lldp(self):
        
        self._goto_priv_exec_mode()
        self._do_cmd("lldp enable")

#@author:chen.tao 2014-10, to support lldp configure in switch        
    def disable_lldp(self):

        self._goto_priv_exec_mode()
        self._do_cmd("undo lldp enable\ny")

#@author:chen.tao 2014-10, to support lldp configure in switch        
    def get_lldp_config(self):
        
        self._goto_priv_exec_mode()
        #chen.tao 2015-3-13, wait 1 second because "dis curr" takes much time.
        time.sleep(1)
        res = self._do_cmd("display current-configuration | include lldp")
        return res

#@author:chen.tao 2014-10, to support lldp configure in switch    
    def is_lldp_enabled(self):

        lldp_config = self.get_lldp_config()
        for config in lldp_config:
            if 'lldp enable' in config:
                return True
        return False

#@author:chen.tao 2014-10, to support lldp configure in switch    
    def set_lldp_mgmt_ip(self,mgmt_ip = "192.168.0.253"):
        self._goto_priv_exec_mode()
        self._do_cmd("lldp management-address %s"%mgmt_ip)

#@author:chen.tao 2014-10, to support lldp configure in switch    
    def set_switch_name(self,sw_name = "Quidway"):
        self._goto_priv_exec_mode()
        self._do_cmd("system name %s"%sw_name)

#@author:chen.tao 2014-10, to support lldp configure in switch        
    def set_port_description(self,inf,port_desc):
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("description %s"%port_desc)
        self._goto_priv_exec_mode()

#@author:chen.tao 2014-10, to support lldp configure in switch        
    def remove_port_description(self,inf):
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("undo description")
        self._goto_priv_exec_mode()

#@author:chen.tao 2014-10, to support lldp configure in switch        
    def _get_lldp_neighbor_by_interface(self,inf):
        """
        [Quidway]dis lldp neighbor interface Ethernet 0/0/2
        Ethernet0/0/2 has 1 neighbors:
        
        
        Neighbor index : 1
        Chassis type   :macAddress
        Chassis ID     :6caa-b33d-65b0
        Port ID type   :macAddress
        Port ID        :6caa-b33d-65b3
        Port description    :eth0
        System name         :RuckusAP
        System description  :Ruckus R500 Multimedia Hotzone Wireless AP/SW Version: 9.9.0.0.99
        System capabilities supported   :bridge wlanAccessPoint router
        System capabilities enabled     :bridge wlanAccessPoint
        Management address type  :ipV4
        Management address       : 192.168.0.129
        Expired time   :114s
        
        
        Port VLAN ID(PVID)  :0
        Protocol identity   :
        
        Auto-negotiation supported    :No
        Auto-negotiation enabled      :No
        OperMau   :speed(0)/duplex(Half)
        
        Power port class         :PD
        PSE power supported      :No
        PSE power enabled        :No
        PSE pairs control ability:No
        Power pairs              :Unknown
        Port power classification:Unknown
        
        Link aggregation supported:No
        Link aggregation enabled :No
        Aggregation port ID      :0
        Maximum frame Size       :0
        
        MED Device information
        Device class   :NA
        
        HardwareRev       :NA
        FirmwareRev       :NA
        SoftwareRev       :NA
        SerialNum         :NA
        Manufacturer name :NA
        Model name        :NA
        Asset tracking identifier :NA
        
        Media policy type   :Unknown
        Unknown Policy      :Defined
        VLAN tagged         :No
        Media policy VlanID      :0
        Media policy L2 priority :0
        Media policy Dscp        :0
        
        Power Type               :PSE
        PoE PSE power source     :Unknown
        Port PSE Priority        :Unknown
        Port Available power value:0
        [Quidway]
        """    
        
        self._goto_priv_exec_mode()
        res = self._do_cmd("display lldp neighbor interface %s"%inf)
        return res

#@author:chen.tao 2014-10, to support lldp configure in switch            
    def get_lldp_neighbor_by_interface(self,inf):

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
        neighbors = self._get_lldp_neighbor_by_interface(inf)
        pattern_neighbor_idx = "Neighbor\s*index\s:\s*(\d+)"
        pattern_chassis_id = "Chassis\s*ID\s*:([0-9a-fA-F-]{14})"
        pattern_port_id = "Port\s*ID\s*:(.+)"
        pattern_time_to_live = "Expired\s*time\s*:(\d+s)"
        pattern_port_desc = "Port\s*description\s*:(.+)"
        pattern_sys_name = "System\s*name\s*:(.+)"
        pattern_sys_desc = "System\s*description\s*:(.+)"
        pattern_sys_capability =  "System\s*capabilities supported\s*:(.+)"
        pattern_mgmt_ip = "Management\s*address\s*:\s*(.+)"
        neighbors_dict = {}
        neighbor_idx = 0

        for line in neighbors:
            line = line.strip()
            if re.search(pattern_neighbor_idx,line):
                neighbor_idx = re.search(pattern_neighbor_idx,line).group(1)
                neighbors_dict[neighbor_idx] = deepcopy(lldp_info_dict)
            if not neighbor_idx: continue
            if re.search(pattern_chassis_id,line):
                neighbors_dict[neighbor_idx]['chassis_id'] = re.search(pattern_chassis_id,line).group(1)
            if re.search(pattern_port_id,line):
                neighbors_dict[neighbor_idx]['port_id'] = re.search(pattern_port_id,line).group(1)
            if re.search(pattern_time_to_live,line):
                neighbors_dict[neighbor_idx]['time_to_live'] = re.search(pattern_time_to_live,line).group(1)
            if re.search(pattern_port_desc,line):
                neighbors_dict[neighbor_idx]['port_description'] = re.search(pattern_port_desc,line).group(1)
            if re.search(pattern_sys_name,line):
                neighbors_dict[neighbor_idx]['system_name'] = re.search(pattern_sys_name,line).group(1)
            if re.search(pattern_sys_desc,line):
                neighbors_dict[neighbor_idx]['system_description'] = re.search(pattern_sys_desc,line).group(1)
            if re.search(pattern_sys_capability,line):
                neighbors_dict[neighbor_idx]['system_capabilities'] = re.search(pattern_sys_capability,line).group(1)            
            if re.search(pattern_mgmt_ip,line):
                neighbors_dict[neighbor_idx]['management_address'] = re.search(pattern_mgmt_ip,line).group(1)                 
                
        return neighbors_dict

#@author:chen.tao 2014-10, to support lldp configure in switch
    def _get_lldp_neighbors(self):

        self._goto_priv_exec_mode()
        res = self._do_cmd("display lldp neighbor")
        return res

#@author:chen.tao 2014-10, to support lldp configure in switch            
    def get_lldp_neighbors(self):

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
        pattern_neighbor_idx = "Neighbor\s*index"
        pattern_chassis_id = "Chassis\s*ID\s*:([0-9a-fA-F-]{14})"
        pattern_port_id = "Port\s*ID\s*:(.+)"
        pattern_time_to_live = "Expired\s*time\s*:(\d+s)"
        pattern_port_desc = "Port\s*description\s*:(.+)"
        pattern_sys_name = "System\s*name\s*:(.+)"
        pattern_sys_desc = "System\s*description\s*:(.+)"
        pattern_sys_capability =  "System\s*capabilities\s*supported\s*:(.+)"
        pattern_mgmt_ip = "Management\s*address\s*:\s*(.+)"
        neighbors_dict = {}
        neighbor_idx = 0

        for line in neighbors:
            line = line.strip()
            if re.search(pattern_neighbor_idx,line):
                neighbor_idx += 1
                neighbors_dict[neighbor_idx] = deepcopy(lldp_info_dict)
            if not neighbor_idx: continue
            if re.search(pattern_chassis_id,line):
                neighbors_dict[neighbor_idx]['chassis_id'] = re.search(pattern_chassis_id,line).group(1)
            if re.search(pattern_port_id,line):
                neighbors_dict[neighbor_idx]['port_id'] = re.search(pattern_port_id,line).group(1)
            if re.search(pattern_time_to_live,line):
                neighbors_dict[neighbor_idx]['time_to_live'] = re.search(pattern_time_to_live,line).group(1)
            if re.search(pattern_port_desc,line):
                neighbors_dict[neighbor_idx]['port_description'] = re.search(pattern_port_desc,line).group(1)
            if re.search(pattern_sys_name,line):
                neighbors_dict[neighbor_idx]['system_name'] = re.search(pattern_sys_name,line).group(1)
            if re.search(pattern_sys_desc,line):
                neighbors_dict[neighbor_idx]['system_description'] = re.search(pattern_sys_desc,line).group(1)
            if re.search(pattern_sys_capability,line):
                neighbors_dict[neighbor_idx]['system_capabilities'] = re.search(pattern_sys_capability,line).group(1)            
            if re.search(pattern_mgmt_ip,line):
                neighbors_dict[neighbor_idx]['management_address'] = re.search(pattern_mgmt_ip,line).group(1)                 
                
        return neighbors_dict

    def get_port_isolate_group(self,group_id):

        res = self._do_cmd("display port-isolate group %s"%group_id)
        isolate_ports = []
        if not res:
            return isolate_ports
        else:
            for line in res:
                if 'Ethernet' in line:
                        line = line.split(' ')
                        isolate_ports += [x for x in line if x]
        return isolate_ports

    def get_all_port_isolate_groups(self):
        res = self._do_cmd("display port-isolate group all")
        port_isolate_group_dict = {}
        pattern_isolate_group = "The ports in isolate group (\d+):"
        current_group = None
        for line in res:
            mobj = re.search(pattern_isolate_group, line)
            if mobj:
                group_id = mobj.group(1) 
                current_group = group_id
                port_isolate_group_dict[current_group] = []
            else:
                if current_group:
                    if 'Ethernet' in line:
                        line = line.split(' ')
                        port_isolate_group_dict[current_group] += [x for x in line if x]
                else:
                    continue
        return port_isolate_group_dict

    def delete_all_port_isolate_groups(self):

        all_groups = self.get_all_port_isolate_groups()
        if not all_groups:
            return
        for group_id,ports in all_groups.items():
            for port in ports:
                self.delete_port_from_isolate_group(port,group_id)

    def add_port_to_isolate_group(self, inf,isolate_group_id):
        logging.info('Adding port %s to isolate group %s.'%(inf,isolate_group_id))
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("port-isolate enable group %s"%isolate_group_id, self.interface_cfg_prompt)
        self._goto_priv_exec_mode()

    def delete_port_from_isolate_group(self, inf,isolate_group_id):
        logging.info('Deleting port %s from isolate group %s.'%(inf,isolate_group_id))
        self._goto_priv_exec_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("undo port-isolate enable group %s"%isolate_group_id, self.interface_cfg_prompt)
        self._goto_priv_exec_mode()
if __name__ == "__main__":
    cfg = {"ip_addr":"192.168.0.253"}
    sw = HuaweiL3Switch(cfg)

    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")
    port = sw.mac_to_interface("00:13:92:20:cd:40")
    sw.disable_interface(port)
    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")
    sw.enable_interface(port)
    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")

