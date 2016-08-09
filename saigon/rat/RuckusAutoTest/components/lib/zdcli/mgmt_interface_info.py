'''
This module define library of Smart Redundancy information
by Louis Lou (louis.lou@ruckuswireless.com)
'''

import time
import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

MGMT_IF_SHOW = """
system
mgmt-if
show
"""

SET_MGMT_IF_IP_ADDR = """
system
    mgmt-if
        ip addr $ip_addr $net_mask
"""

SET_NO_MGMT_IF = """
system
    no mgmt-if
"""

SET_MGMT_VLAN = """
system
    mgmt-if
        vlan $vlan_id
"""

SET_NO_MGMT_VLAN = """
system
    mgmt-if
        no vlan
"""

info = dict(
    mgmt_if_v4 = "IPv4 Management Interface",
)

def set_mgmt_if(zdcli,conf):
    _set_mgmt_if_ip_addr(zdcli,conf)
    _set_mgmt_if_vlan(zdcli,conf)


def set_no_mgmt_if(zdcli):
    cmd = SET_NO_MGMT_IF
    logging.info("[ZDCLI:] Remove ZD MGMT interface")
    _do_excute_cmd(zdcli,cmd)

def _set_mgmt_if_ip_addr(zdcli,conf):
    ip_addr = conf['ip_addr']
    net_mask = conf['net_mask']
    cmd = Template(SET_MGMT_IF_IP_ADDR).substitute(dict(ip_addr=ip_addr,
                                                        net_mask = net_mask
                                                        ))

    logging.info("[ZDCLI:] Set Management IP address/net-mask [%s/%s]" %(ip_addr,net_mask))
    _do_excute_cmd(zdcli,cmd)


def _set_mgmt_if_vlan(zdcli,conf):
    if conf['vlan_id']:
        vlan_id = conf['vlan_id']
        cmd = Template(SET_MGMT_VLAN).substitute(dict(vlan_id = vlan_id))
        logging.info("[ZDCLI:] Set MGMT IF VLAN: [%s]" % (vlan_id))
        _do_excute_cmd(zdcli,cmd)

def _set_no_mgmt_if_vlan(zdcli):
    cmd =SET_NO_MGMT_VLAN
    logging.info("[ZDCLI:] Remove VLAN from MGMT interface")
    _do_excute_cmd(zdcli,cmd)

def show_mgmt_if_info(zdcli):
    cmd_block = MGMT_IF_SHOW
    logging.info("======config-sys-mgmt-if)#show ==========")

    mgmt_if_info = zdcli.do_cfg_show(cmd_block)

    logging.info('The result\n:%s',mgmt_if_info)
    mgmt_if_info_on_cli = output.parse(mgmt_if_info)

    return mgmt_if_info_on_cli

def verify_mgmt_if_info(mgmt_if_info_cli,mgmt_if_info_zd):
    '''

    '''
    mgmt_info_cli = mgmt_if_info_cli[info['mgmt_if_v4']]


    if mgmt_info_cli == mgmt_if_info_zd:
        return True

    else:
        return False

def verify_no_mgmt_if_info(mgmt_info_cli):
    mgmt_info_cli = mgmt_info_cli[info['mgmt_if_v4']]

    if mgmt_info_cli['IP Address']:
        return False
    if mgmt_info_cli['Netmask']:
        return False

    if mgmt_info_cli['Status'] == 'Disabled':
        logging.info('Mgmt interface Status is Disabled')
        return True
    else:
        return False

def _do_excute_cmd(zdcli,cmd):
    try:
        time.sleep(1)
        logging.info("CLI is: %s" %cmd)
        zdcli.do_cfg(cmd)
        time.sleep(2)
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)

