import logging
import time
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
    tbl = "//div[@id='main_body_area']//table", # table locator for fm8
    refresh_btn = "//img[@title='Refresh']",
    edit_btn = "//div[@class='dojoButton' and div='Edit Settings']",
    back_btn = "//div[@class='dojoButton' and div='Back']",
    submit_btn = "//div[@class='dojoButton' and div='Submit']",
    reset_btn = "//div[@class='dojoButton' and div='Reset']",

    # define name of items, these name will be used as keys of input config
    gateway = Ctrl("//input[contains(@name, 'DefaultGateway')]", type = 'text'),
    pri_dns = Ctrl("//input[contains(@name, 'keyPriDNS')]", type = 'text'),
    sec_dns = Ctrl("//input[contains(@name, 'keySecDNS')]", type = 'text'),
    ntp_server = Ctrl("//input[contains(@name, 'NTPServer1')]", type = 'text'),
    connection_type = Ctrl(dict(
        dhcp = "//input[@value='DHCP']",
        static = "//input[@value='Static IP']",
    ), type = 'radioGroup'),
    ip = Ctrl("//input[contains(@name, 'ExternalIPAddress')]", type = 'text'),
    net_mask = Ctrl("//input[contains(@name, 'SubnetMask')]", type = 'text'),
)

Locators.update(
    tbl = "//div[contains(@id,'displayDiv')]//table", # table locator for FM saigon
)

OrderedCtrls = [
    dict(
        enter = 'connection_type',
        items = [
            'ip', 'encryption_len', 'net_mask',
        ],
        exit = '',
    ),
]


def _nav_to(dv, force = False):
    return dv.navigate_to(dv.DETAILS, dv.DETAILS_INTERNET_WAN, force = force)


def get_cfg(dv, cfgKs = []):
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
        Netmask: 255.255.255.0
        Gateway: 192.168.0.124
        Primary DNS: 192.168.0.124
        NTP Server: ntp.ruckuswireless.com
        Internet Connection Type: Static IP
        Internet Connection Status:Connected
        Total Bytes Sent: 98418
        Total Bytes Received: 18947
        Total Packets Received: 189
        Total Packets Sent: 204
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
         'pri_dns': u'192.168.0.124'}
    '''

    s, l = dv.selenium, Locators
    _nav_to(dv, force = True)
    logging.info('Getting FM Device View summary Internet info...')
    # click refresh button
    s.click_and_wait(l['refresh_btn'])

    # get encryption info
    summary_items = s.get_htable_content(l['tbl'], ignore_case = True)
    # NOTE: l2tp_status: currently don't know how to verify this item
    removed_items = ['totalbytessent', 'totalbytesreceived',
                     'totalpacketsreceived', 'totalpacketssent',
                     'l2tp_status']
    # remove items which cannot be verified or don't need to verify
    # Some item only available on either 2942 or 7942 so we need to do check
    # before delete it
    for k in removed_items:
        if summary_items.has_key(k): del summary_items[k]

    # Convert the returned items to keys as they are in provisioning config.
    # The purpose is to compare the output
    provisioning_items = map_summary_to_provisioning_cfg(summary_items)

    # filter items not in cfgKs
    ret_items = {}
    for k in cfgKs: ret_items[k] = provisioning_items[k]

    return map_cfg_value(ret_items if ret_items else provisioning_items, False)


def set_cfg(dv, cfg, timeout = 360):
    '''
    '''
    s, l, ordered_list = dv.selenium, Locators, cfgDataFlow(cfg.keys(), OrderedCtrls),

    _nav_to(dv, force = True)
    logging.info('Setting info for Internet/WAN: %s' % pformat(cfg))

    s.click_and_wait(l['edit_btn'])

    set(s, l, map_cfg_value(cfg), ordered_list)
    s.click_and_wait(l['submit_btn'])

    return dv.get_task_status(dv.get_task_id(), timeout)


