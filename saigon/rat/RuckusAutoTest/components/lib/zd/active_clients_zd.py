'''
Client table headers:
['mac',
 'user',
 'ap',
 'wlan',
 'vlan',
 'channel',
 'radio_type',
 'rssi',
 'status'
]
'''
import logging
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt


#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_clients_briefs(zd):
    '''
    return
    . as a dict of dicts with client mac addresses as keys
    >>> pp(lib.zd.cac.get_all_clients_briefs(zd))
    {u'c4:17:fe:75:95:1f': {u'ap': u'00:1d:2e:16:3a:c0',
                            u'channel': u'1',
                            u'mac': u'c4:17:fe:75:95:1f',
                            u'radio_type': u'802.11b/g',
                            u'rssi': u'N/A',
                            u'status': u'Authorized',
                            u'user': u'192.168.0.109',
                            u'vlan': u'None',
                            u'wlan': u'beLoc'}}
    '''
    return list_to_dict(_get_all_clients_briefs(zd), 'mac')


def get_client_brief_by_mac_addr(zd, mac_addr):
    '''
    '''
    return _get_client_brief_by(zd, dict(mac = mac_addr))


def get_all_clients_details(zd):
    '''
    '''
    all_client_detail = {}
    for mac_addr in get_all_clients_briefs(zd).iterkeys():
        all_client_detail.update(
            {mac_addr: get_client_detail_by_mac_addr(zd, mac_addr)}
        )

    return all_client_detail


def get_client_detail_by_mac_addr(zd, mac_addr):
    '''
    return 
    {'ap': u'50:a7:33:2e:42:e0',
     'authMethod': u'OPEN',
     'bssid': u'50:a7:33:6e:42:e8',
     'channel': u'11',
     'channelization': u'20',
     'firstAssoc': u'2012/10/17  14:38:33',
     'ip': u'192.168.0.147',
     'mac': u'00:15:af:ed:94:3b',
     'radio-type': u'802.11g/n',
     'retries': u'701 pkts',
     'rx': u'94 pkts / 13K bytes',
     'signal': u'99%',
     'tx': u'3.3K pkts / 312K bytes',
     'user': u'',
     'vlan': u'1',
     'wlan': u'west.test'}
    '''
    _nav_to(zd)
    _open_client_detail_page(zd, dict(mac = mac_addr))

    detail = _get_client_detail(zd)

    zd.re_navigate()

    return detail

def open_client_pingtool_by_mac_addr(zd, mac_addr):
    return _open_client_pingtool_by_mac_addr(zd, dict (mac = mac_addr))

def go_to_blocked_clients_from_monitor_page(zd,level='super'):
    cfg_acl_span = r"//span[@id='configure_acls']"
    new_acl_span = r"//span[@id='new-acl']"
    
    loc = LOCATORS_MON_ACTIVECLIENTS
    super_link = loc['go_to_blocked_clients']
    
    _nav_to(zd)
    if not zd.s.is_element_present(super_link):
        raise Exception('the super link to acl page not exist')
    zd.s.click_and_wait(super_link)
    
    if level=='monitor' and (zd.s.is_element_present(cfg_acl_span) or zd.s.is_element_present(new_acl_span)):
        logging.error('monitor user go into cfg page')
        return False
    else:
        zd.current_tab = zd.DASHBOARD
    
    if level!='monitor' and (not zd.s.is_element_present(cfg_acl_span) or not zd.s.is_element_present(new_acl_span)):
        logging.error('super or operator user not go into cfg page')
        return False
    else:
        zd.current_tab = zd.CONFIGURE
    
    return True


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locators = dict(
    client_tbl_loc = "//table[@id='%s']",
    client_tbl_nav_loc = "//table[@id='%s']/tfoot",
    client_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
    client_detail_page_btn = "//a[contains(@href, 'mon_client.jsp')]",
    client_pingtool_btn = "/td[@class='action']/img[contains(@id, 'pingtool')]",
    client_value_loc = "//td[@id='%s']",
)

tbl_id = dict(
    client_summary = 'clients',
    client_detail = 'client',
)

client_detail_hdrs = ['mac', 'dvcinfo', 'hostname', 'user', 'authMethod', 'wlan', 'vlan', 'ip',
 'ipv6', 'ap', 'bssid', 'firstAssoc', 'channel', 'channelization',
 'radio-type', 'signal', 'rx', 'tx', 'retries',] 

client_detail_ks = client_detail_hdrs

# when access activeClient from WLAN tab; the table@id is 'client' not 'clients'
LOCATORS_MON_ACTIVECLIENTS =  {
            'get_ip_addr_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[4]",
            'get_apmac_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[6]",
            'get_wlan_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[7]",
            'get_vlan_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[8]",
            'get_channel_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[9]",
            'get_radio_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[10]",
            'get_signal_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[11]",
            'get_status_by_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td[12]",
            'speedflex_on_client_mac': r"//table[@id='clients']//tr/td/a[text()='%s']/../../td/span[text()='SpeedFlex']",
            'go_to_blocked_clients':r"//a[@href='conf_acls.jsp']",
        }

LOCATORS_CFG_ACCESS_CONTROL = dict(
    blocked_client_all_checkbox="//input[@id='blocked-clients-sall']",
    blocked_client_checkbox = "//table[@id='blocked-clients']//tr[@idx='%s']//td[1]/input",
    blocked_client_mac_cell = "//table[@id='blocked-clients']//tr[@idx='%s']/td[2]",
    blocked_client_unblock_button = "//input[@id='del-blocked-clients']",
    blocked_client_search_textbox = "//table[@id='blocked-clients']//span[@class='other-act']/input",
    show_more_blocked_clients = "//input[@id='showmore-blocked-clients']",
    total_blocked_client = "//table[@id='blocked-clients']//div[@class='actions']/span"
)


def _nav_to(zd):
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_CLIENTS)


def _get_all_clients_briefs(zd):
    '''
    return
    . a list of dict
    '''
    _nav_to(zd)
    return wgt.get_tbl_rows(zd.s, locators['client_tbl_loc'] % tbl_id['client_summary'],
                            locators['client_tbl_nav_loc'] % tbl_id['client_summary'])


def _get_client_brief_by(zd, match, verbose = False):
    '''
    '''
    _nav_to(zd)
    return wgt.get_first_row_by(zd.s, locators['client_tbl_loc'] % tbl_id['client_summary'],
                                locators['client_tbl_nav_loc'] % tbl_id['client_summary'], match,
                                locators['client_tbl_filter_txt'] % tbl_id['client_summary'], verbose)


def _get_client_detail(zd):
    '''
    '''
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 use id to get value instead of tr no.
    client_all = {}
    for key in client_detail_hdrs:
        value = zd.s.get_text(locators['client_value_loc'] % key)
        client_all[key] = value
    return client_all
#    p = dict(
#        loc = locators['client_tbl_loc'] % tbl_id['client_detail'],
#        hdrs = client_detail_hdrs,
#        ks = client_detail_ks,
#    )    
#    return zd.s.get_htable_rows2(**p)


def _open_client_detail_page(zd, match):
    '''
    '''
    return _click_on_client_btn(zd, match,
                                locators['client_detail_page_btn'], 2)


def _click_on_client_btn(zd, match, loc, wait = 1.5):
    '''
    '''
    r = _get_client_brief_by(zd, match, True)
    btn = (r['tmpl'] % r['idx']) + loc
    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn, wait)

    else:
        raise Exception('Unable to click on the button since it is disabled')

def _open_client_pingtool_by_mac_addr(zd, match):
    r = _get_client_brief_by(zd, match, True)
    btn = (r['tmpl'] % r['idx']) + locators['client_pingtool_btn']

    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn)

    else:
        raise Exception('Unable to open network connectivity on STA [%s] since the network connectivity button'
                        ' is disabled' % r['row']['mac'])    


#
# Monitor>Current Active Clients
#
def get_status_by_mac(zd, client_mac_addr):
    return get_active_client_status_by_mac(zd, client_mac_addr)


def get_active_client_status_by_mac(zd, client_mac_addr):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
    result = _get_active_client_status_by_mac(zd, client_mac_addr)

    return result


def _get_active_client_status_by_mac(zd, client_mac_addr):
    xloc = LOCATORS_MON_ACTIVECLIENTS
    result = {'mac': client_mac_addr}
    #JLIN@20090617 add vlan for 8.2
    for xid in ['apmac', 'status', 'ip_addr', 'channel', 'signal', 'wlan', 'vlan', 'radio']:
        locid = 'get_%s_by_client_mac' % xid
        result[xid] = zd.s.get_text(xloc[locid] % client_mac_addr.lower())

    return result


def click_speedflex_by_mac(zd, client_mac_addr):
    xloc = LOCATORS_MON_ACTIVECLIENTS
    zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
    _click_speedflex_by_mac(zd, client_mac_addr)
    # do the speedfilx task here
    result = {}

    return result


def _click_speedflex_by_mac(zd, client_mac_addr):
    xloc = LOCATORS_MON_ACTIVECLIENTS
    zd.s.click_and_wait(xloc['speedflex_on_client_mac'] % client_mac_addr)

def get_blocked_clients_list(zd):
    xloc = LOCATORS_CFG_ACCESS_CONTROL
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)

    blocked_clients_list = []
    total_blocked_clients = zd._get_total_number(xloc['total_blocked_client'], 'Blocked Clients')

    while zd.s.is_visible(xloc['show_more_blocked_clients']):
        zd.s.click_and_wait(xloc['show_more_blocked_clients'])

    if not total_blocked_clients or total_blocked_clients == '0':
        blocked_clients_list = []
        return blocked_clients_list

    for idx in range(0, int(total_blocked_clients)):
        blocked_clients_list.append(zd.s.get_text(xloc['blocked_client_mac_cell'] % str(idx)))

    return blocked_clients_list

