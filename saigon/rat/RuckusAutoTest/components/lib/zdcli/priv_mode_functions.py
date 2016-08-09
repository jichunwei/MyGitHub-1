"""
This module include the functions support to execute the privileged mode commands:
   ruckus#
   exit                 Ends the CLI session.
   help                 Shows available commands.
   quit                 Ends the CLI session.
   history              Shows a list of previously run commands.
   disable              Disables privileged commands.
   ping <IP-ADDR/DOMAIN-NAME>
                        Sends ICMP echo packets to an IP/IPv6 address or domain name.
   reboot               Reboots the controller.
   set-factory          Set factory default.
   config               Configures options and settings.
   debug                Manages system debug options.
   show                 Displays system options and settings.
   session-timeout <NUMBER>
                        Sets the CLI session timeout.
   monitor              Monitors system options and settings.


@author: An Nguyen, Mar 2013
"""
import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#
# PUBLIC FUNCTIONS
#

def set_qos_sys_tunnel_tos_marking(zdcli, type, tos_value):
    """
    set_qos sys [tunnel-tos-val] [data|ctrl] [inner|<TOS value (hex)>]
    """
    cmd =  'set_qos sys tunnel-tos-val %s %s' % (type, tos_value)
    return zdcli.do_cmd(cmd)

#
# PRIVATE FUNCTIONS
#

