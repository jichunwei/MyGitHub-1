'''
Client table headers:
['mac',
 'user',
 'ap',
 'port-id',
 'status'
]
'''
import time
import logging
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt


#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_clients_briefs(zd):
    '''
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
    '''
    _nav_to(zd)
    _open_client_detail_page(zd, dict(mac = mac_addr))

    detail = _get_client_detail(zd)

    zd.re_navigate()

    return detail

def open_client_pingtool_by_mac_addr(zd, mac_addr):
    return _open_client_pingtool_by_mac_addr(zd, dict (mac = mac_addr))



def delete_clients(zd, mac_string):
    """
    Search and delete the existing clients whose mac address includes  in 'Currently Active Clients' page.
    Input:
        mac_string: a regular string is a part of or a full mac address.
    """
    _nav_to(zd)
    zd.s.click_and_wait(zd.info['loc_mon_wired_clients_refresh_image'], 2)

    # Search the expected client base on the mac address
    zd.s.type_keys(zd.info['loc_mon_wired_clients_search_textbox'], mac_string.lower())
    time.sleep(2)

    # Get the total number of clients in search result
    total_clients = zd._get_total_number(zd.info['loc_mon_wired_clients_total_number_span'], "Active Wired Clients")

    # Delete all clients if they existed
    if int(total_clients) > 0:
        first_client_span = zd.info['loc_mon_wired_clients_delete_span'].replace("$_$", "0")
        for i in range(int(total_clients)):
            zd.s.click_and_wait(first_client_span)
        logging.info("Delete %s active clients with [%s] in mac address successfully" % (total_clients, mac_string))
        
    else:
        logging.info('"Current Active Clients" table does not have any client with [%s] in mac address' % mac_string)
            
            

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locators = dict(
    client_tbl_loc = "//table[@id='%s']",
    client_tbl_nav_loc = "//table[@id='%s']/tfoot",
    client_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
    client_detail_page_btn = "//a[contains(@href, 'mon_wireclient.jsp')]",    
)

tbl_id = dict(
    client_summary = 'wireclient',
    client_detail = 'wireclient',
)

client_detail_hdrs = [
    'mac', 'user', 'ip', 'ipv6', 'ap', 'port', 'firstConn', 'rx', 'tx'
]
client_detail_ks = client_detail_hdrs


LOCATORS_MON_ACTIVECLIENTS = dict(
    get_user_by_client_mac = r"//table[@id='wireclient']//tr/td/a[text()='%s']/../../td[2]",
    get_ap_by_client_mac = r"//table[@id='wireclient']//tr/td/a[text()='%s']/../../td[3]",
    get_port_id_by_client_mac = r"//table[@id='wireclient']//tr/td/a[text()='%s']/../../td[4]",            
    get_status_by_client_mac = r"//table[@id='wireclient']//tr/td/a[text()='%s']/../../td[6]",    
)
 
def _nav_to(zd):    
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_WIRED_CLIENTS)


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
    p = dict(
        loc = locators['client_tbl_loc'] % tbl_id['client_detail'],
        hdrs = client_detail_hdrs,
        ks = client_detail_ks,
    )

    return zd.s.get_htable_rows2(**p)


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

#
# Monitor>Current Active Clients
#
def get_status_by_mac(zd, client_mac_addr):
    return get_active_client_status_by_mac(zd, client_mac_addr)


def get_active_client_status_by_mac(zd, client_mac_addr):
    _nav_to(zd)
    result = _get_active_client_status_by_mac(zd, client_mac_addr)

    return result


def _get_active_client_status_by_mac(zd, client_mac_addr):
    xloc = LOCATORS_MON_ACTIVECLIENTS
    result = {'mac': client_mac_addr}    
    for xid in ['user', 'ap', 'port_id', 'status']:
        locid = 'get_%s_by_client_mac' % xid
        result[xid] = zd.s.get_text(xloc[locid] % client_mac_addr.lower())

    return result
