import logging, time
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import * # rarely reloading, so import *
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_summary_to_provisioning_cfg, map_cfg_value

'''
NOTE: Lowercase Module
'''

# we ignore case and blank in the title
MAC_ADDRESS_TITLE = 'macaddress' # MAC Address
SERIAL_NUMBER_TITLE = 'serialnumber' # Serial Number

Locators = dict(
    srv_info_tbl = "//div[@id='content']/table[1]",
    ap_info_tbl = "//div[@id='content']/table[2]",
)


def _nav_to(ap, force = False):
    return ap.navigate_to(ap.MAIN_PAGE, ap.STATUS_INTERNET, force = force)


def get_cfg(ap, cfgKs = [], fm_return = True):
    '''
    This function is to get summary info of Internet/WAN. Get following information:
        1) Mac Address:00:1D:2E:05:43:C0
        2) IP Address:1.1.1.33
        3) Netmask:255.255.255.0
        4) Gateway:1.1.1.8
        5) NTP Server:ntp.ruckuswireless.com
        6) Connection Type: Static IP
        7) Connection Status: Connected
    Other titles will be removed before ruturning the result
    Title on Internet Summary page:
        Mac Address: 00:22:7F:09:79:20
        IP Address: 192.168.0.204
        Mask: 255.255.255.0
        Gateway: 192.168.0.124
        Primary DNS Server: 192.168.0.124
        Secondary DNS Server: 192.168.0.124
        NTP Server: ntp.ruckuswireless.com
        Connection Type: Static IP
        Connection Status:Connected
    Input:
    - dv: device view instance
    - cfgKs: a list of cfg keys to get. If cfgKs is empty, return all. Otherwise return only that key.
    Output:
    - return in FM input format as below ex:
         'connection_status': u'Connected',
         'connection_type': 'static',
         'gateway': u'192.168.0.124',
         'ip': u'192.168.0.204',
         'mac': u'00:22:7F:09:79:20',
         'net_mask': u'255.255.255.0',
         'ntp_server': u'ntp.ruckuswireless.com',
         'pri_dns': u'192.168.0.124',
         'sec_dns': u'192.168.0.126'
    '''

    s, l = ap.selenium, Locators
    _nav_to(ap, force = True)
    logging.info('Getting AP summary Internet info...')

    # get server info item from the first table
    summary_items = s.get_htable_content(l['srv_info_tbl'], ignore_case = True)

    # get ap info item from the second table
    summary_items.update(s.get_htable_content(l['ap_info_tbl'], ignore_case = True))

    # NOTE: l2tp_status: currently don't know how to verify this item
    # TODO: We have a bug 9386 for connection status "connection_status" so we temporarily don
    # 't verify this item now.
    removed_items = ['dhcpactions', ]
    # remove items which cannot be verified or don't need to verify
    # Some item only available on either 2942 or 7942 so we need to do check
    # before delete it
    for k in removed_items:
        if summary_items.has_key(k): del summary_items[k]

    # Convert the returned items to keys as they are in provisioning config.
    # The purpose is to compare the output
    provisioning_items = map_summary_to_provisioning_cfg(summary_items)

    # get items in cfgKs only
    filtered_cfg = {}
    for k in cfgKs: filtered_cfg[k] = provisioning_items[k]

    ret_cfg = filtered_cfg if filtered_cfg else provisioning_items

    return map_cfg_value(ret_cfg, False) if fm_return else ret_cfg


