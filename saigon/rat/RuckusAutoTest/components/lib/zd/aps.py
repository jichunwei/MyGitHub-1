'''
Access Points table headers:
['mgmt_vlan_id',
 'description',
 'ip',
 'devname',
 'num_sta',
 'state',
 'mesh_mode',
 'radio_channel',
 'mac',
 'model']
'''
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
import time

#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------

def get_all_ap_details(zd):
    '''
    '''
    all_ap_details = {}
    for mac_addr in get_all_ap_briefs(zd).iterkeys():
        all_ap_details.update(
            {mac_addr: get_ap_detail_by_mac_addr(zd, mac_addr)}
        )

    return all_ap_details


def set_query_option(zd, option = 'and'):
    '''
    '''
    _nav_to(zd)
    if option == 'or':
        zd.s.click_and_wait(locators['ap_tbl_search_or_radio'])

    else:
        zd.s.click_and_wait(locators['ap_tbl_search_and_radio'])


def query_ap_details_by_dict(zd, key = '', value = ''):
    '''
    Query APs with given key
    '''
    search_key = key
    search_value = value

    detail = _query_ap_brief_by(zd, {'%s' % search_key:'%s' % search_value})

    return detail


def query_ap_details_by_sub_mac_addr(zd, sub_mac_addr):
    '''
    Query APs with given sub_mac_addr
    '''
    detail = _query_ap_brief_by(zd, dict(mac = sub_mac_addr))
    zd.re_navigate()

    return detail


def query_ap_details_by_sub_ip_addr(zd, sub_ip_addr):
    '''
    Query APs with given sub_ip_addr
    '''
    detail = _query_ap_brief_by(zd, dict(ip = sub_ip_addr))
    zd.re_navigate()

    return detail


def sort_ap_details_by_mac_addr(zd, sort_type = "asc", wait = 1, ):
    '''
    Sort APs with given head of field which want to sort
    input:
    . sort_type = asc | desc

    '''
    detail = _sort_ap_brief_by(zd, match = None,
                               sort = dict(field = "mac", type = sort_type),
                               wait = wait, )
    zd.re_navigate()

    return detail


def sort_ap_details_by_mac_addr_with_mac_filter(zd, sub_mac_addr, sort_type = "asc", wait = 1, ):
    '''
    Sort APs with given head of field which want to sort
    input:
    . sub_mac_addr: sub of mac addr to ap
    . sort_type: asc | desc

    '''
    filter = locators['ap_tbl_filter_txt'] % tbl_id['ap_summary']

    detail = _sort_ap_brief_by(zd, match = dict(mac = sub_mac_addr),
                               sort = dict(field = "mac", type = sort_type),
                               filter = filter, wait = wait,)
    zd.re_navigate()

    return detail

def get_all_ap_mac_list(zd):
    return [ap['mac'] for ap in _get_all_ap_briefs(zd)]

def get_ap_detail_by_mac_addr(zd, mac_addr):
    '''
    '''
    detail = _get_ap_detail_by(zd, dict(mac = mac_addr))
    zd.re_navigate()

    return detail


def get_ap_detail_mesh_tree_by_mac_addr(zd, mac_addr):
    '''
    Get MeshTree of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dictionary of sub-dictionaries:
        {uplink = {
            'ap': Uplink AP
            'desc': Description
            'type': Type
            'assoc': Connected Since
            'rssi': Avg Signal (%)
            'rx': Packets/Bytes Received
            'tx': Packets/Bytes Transmitted
            'retries': Retries
        },
        downlink = {
            '<mac addr>': {
                'ap': Access Point
                'description': Description
                'type': Type
                'first-assoc': Connected Since
                'rssi': Signal (%)
                'total-rx-bytes': Bytes Received
                'total-tx-bytes': Bytes Transmitted
            }
        },
        }
    '''
    mesh_tree = _get_ap_detail_mesh_tree_by(zd, dict(mac = mac_addr))

    zd.re_navigate()

    return mesh_tree


def get_ap_detail_downlink_aps_by_mac_addr(zd, mac_addr):
    '''
    Get MeshTree downlinks of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dictionary of downlinks:
        {'<mac addr>': {
            'ap': Access Point
            'description': Description
            'type': Type
            'first-assoc': Connected Since
            'rssi': Signal (%)
            'total-rx-bytes': Bytes Received
            'total-tx-bytes': Bytes Transmitted
        }}
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    zd.re_navigate()

    return _get_ap_detail_downlink_aps(zd)


def get_ap_detail_uplink_ap_by_mac_addr(zd, mac_addr):
    '''
    Get MeshTree uplink of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dictionary of uplink:
        {
            'ap': Uplink AP
            'desc': Description
            'type': Type
            'assoc': Connected Since
            'rssi': Avg Signal (%)
            'rx': Packets/Bytes Received
            'tx': Packets/Bytes Transmitted
            'retries': Retries
        }
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_uplink_ap(zd)

    zd.re_navigate()

    return detail


def get_ap_detail_uplink_aps_history_by_mac_addr(zd, mac_addr):
    '''
    Get MeshTree uplink history of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dictionary of uplink history:
        {'<mac addr>': {
            'ap': Access Point
            'description': Description
            'type': Type
            'channel': Channel
            'rssi': Signal (%)
            'first-assoc': Last Connect
            'last-seen': Last Disconnect
        }}
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    zd.re_navigate()

    return _get_ap_detail_uplink_aps_history(zd)


def get_ap_detail_general_by_mac_addr(zd, mac_addr):
    '''
    Get AP detail in General table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of General detail
      {
        'devname': Device Name
        'description': Description
        'location': Location
        'gps': GPS Coordinates
        'mac': MAC Address
        'ip': IP Address
        'model': Model
        'serial_number': S/N
        'firmware_version': Version
      }
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_general(zd)

    zd.re_navigate()

    return detail

def get_ap_detail_general_by_mac_addr2(zd, mac_addr):
    '''
    Get AP detail in General table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of General detail
      {
        'devname': Device Name
        'description': Description
        'location': Location
        'gps': GPS Coordinates
        'mac': MAC Address
        'ip': IP Address
        'model': Model
        'serial_number': S/N
        'firmware_version': Version
      }
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_general2(zd)

    zd.re_navigate()
    
    detail_info = {}
    for key in detail.keys():
        detail_info[ap_detail_general_title_map[key]] = detail[key]    

    return detail_info


def get_ap_client_detail_by_mac(zd, ap_mac ,client_mac=''):
    '''
    '''
    _nav_to(zd)    
    _open_ap_detail_page(zd, {'mac':ap_mac})
    return _get_client_info_by(zd,{'mac':client_mac})


def get_ap_detail_info_by_mac_addr(zd, mac_addr):
    '''
    Get AP detail in Info table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of Info detail
      {
        'status': Status
        'uptime': Uptime
        'tunnel_mode': Connection Mode
        'wlan_id': VLAN
        'num_sta': Associated Clients
      }
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_info(zd)

    zd.re_navigate()

    return detail


def get_ap_detail_radio_by_mac_addr(zd, mac_addr):
    '''
    Get AP detail in Radio table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of Radio detail
      {
        'channel': Current Channel
        'channelization': Channelization
        'wlangroup': WLAN Group
        'bgscan': Background Scanning
        'tx_power': TX Power
        'num_sta': # of Client Devices
        'retries': % Retries/% Drops
        'mcast': % Non-unicast
        'rx': Packets/Bytes Received
        'tx': Packets/Bytes Transmitted
        'noisefloor': Noise Floor
        'phyerr': PHY Errors
        'airtime': % AirTime (total/busy/RX/TX)
      }
    @note: 'channelization' is availble in Radio 802.11g/n and 802.11a/n
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_radio(zd)

    zd.re_navigate()

    return detail

def get_ap_detail_under_radio_by_mac_addr(zd, mac_addr,radio):
    '''
    Get AP detail in Radio table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP and radio of AP
    @return: a dict of Radio detail
      {
        'channel': Current Channel
        'channelization': Channelization
        'wlangroup': WLAN Group
        'bgscan': Background Scanning
        'tx_power': TX Power
        'num_sta': # of Client Devices
        'retries': % Retries/% Drops
        'mcast': % Non-unicast
        'rx': Packets/Bytes Received
        'tx': Packets/Bytes Transmitted
        'noisefloor': Noise Floor
        'phyerr': PHY Errors
        'airtime': % AirTime (total/busy/RX/TX)
      }
    @note: 'channelization' is availble in Radio 802.11g/n and 802.11a/n
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = {}
    if zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11%s' % radio], 0.5):        
        if radio == 'bg':
            detail = _get_ap_detail_of_detail(
            zd, locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11%s' % radio],
            radio_11bg_hrds, radio_11bg_ks)
        else:
            detail = _get_ap_detail_of_detail(
            zd, locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11%s' % radio],
            radio_11ng_hrds, radio_11ng_ks)

    zd.re_navigate()

    return detail

def get_ap_detail_wlans_by_mac_addr(zd, mac_addr, group_by = 'wlan'):
    '''
    Get AP detail in WLANs table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of WLANs detail
        {'<wlan>': {
            'wlan': Name/ESSID
            'bssid': BSSID
            'radio-type': Radio
        }}
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_wlans(zd, group_by)

    zd.re_navigate()

    return detail

def get_ap_detail_wlan_list_by_mac_addr(zd, mac_addr):
    '''
    Get all records in WLANs table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a list of WLANs detail
    
    Output:
     [{u'bssid': u'04:4f:aa:07:50:08',
         u'radio_type': u'802.11g/n',
         u'vap_up': u'Up',
         u'wlan': u'ZoeWlan1'},
      {u'bssid': u'04:4f:aa:47:50:08',
         u'radio_type': u'802.11g/n',
         u'vap_up': u'Up',
         u'wlan': u'Wlan2'},
      {u'bssid': u'04:4f:aa:87:50:08',
         u'radio_type': u'802.11g/n',
         u'vap_up': u'Up',
         u'wlan': u'Wlan3'}
    ]
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    wlans = []
    wlans = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['ap_detail_wlans'],
                             locators['ap_tbl_nav_loc'] % tbl_id['ap_detail_wlans'])
    zd.re_navigate()
    return wlans


def get_ap_detail_neighbor_by_mac_addr(zd, mac_addr):
    '''
    Get AP detail in Neighbor APs table of an AP with given mac_addr
    Input:
    @param mac_addr: MAC address of the AP
    @return: a dict of Neighbor APs detail
        {'<mac addr>': {
            'mac': Access Point
            'radio-channel': Channel
            'rssi': Signal (%)
            'mesh-uplink-rc': Uplink Availability / Path Score (status) *** (8.2 / 9.0)
        }}
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, dict(mac = mac_addr))

    detail = _get_ap_detail_neighbor(zd)

    zd.re_navigate()

    return detail


def get_all_ap_briefs(zd):
    '''
    . get all ap info on Monitors > Access Points
    return
    . as a dict of dicts with mac addresses as keys

    '''
    ap_info_list = _get_all_ap_briefs(zd)

    return list_to_dict(ap_info_list, 'mac')


def get_ap_brief_by_mac_addr(zd, mac_addr):
    return _get_ap_brief_by(zd, dict(mac = mac_addr))


def reboot_all_aps(zd):
    return _reboot_aps(zd)


def reboot_ap_by_mac_addr(zd, mac_addr):
    return _reboot_ap(zd, match = dict(mac = mac_addr))

def open_pingtool_by_mac_addr(zd, mac_addr):
    return _open_pingtool_by_mac_addr(zd, match = dict(mac = mac_addr))


def allow_ap_joining_by_mac_addr(zd, mac_addr):
    return _allow_ap_joining(zd, match = dict(mac = mac_addr))


def click_mon_apsummary_refresh(zd):
    return _click_mon_aps_refresh_btn(zd)
#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locators = dict(
    ap_th_mac_addr = "//th[@attr='mac']",
    ap_tbl_loc = "//table[@id='%s']",
    ap_tbl_nav_loc = "//table[@id='%s']/tfoot",
    ap_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
#    ap_restart_btn = "/td[@class='action']/img[contains(@id, 'restart')]",
    ap_restart_btn = "/td[@class='action']/img[contains(@id, 'restart-apsummary')]",
    ap_pingtool_btn = "/td[@class='action']/img[contains(@id, 'pingtool')]",
    ap_allow_joining_btn = "/td[@class='action']" +
                           "/img[contains(@id, 'approve-apsummary-')]",
    ap_detail_page_btn = "//a[contains(@href, 'mon_ap.jsp')]",
    ap_detail_htbl_loc = "//table/caption[text()='%s']/..",
    #cwang@2010-9-2, add search radio including '&' and '|'
    ap_tbl_search_or_radio = r"//table[@id='apsummary']//input[@id='sop-apsummary|']",
    ap_tbl_search_and_radio = r"//table[@id='apsummary']//input[@id='sop-apsummary&']",
    #jluh@2012-06-08, add apsummary refresh button
    ap_mon_apsummary_refresh = r"//img[@id='refresh-apsummary']",
)

tbl_id = dict(
    ap_summary = 'apsummary',
    ap_detail_wlans = 'wlans',
    ap_detail_neighbors = 'neighbors',
    ap_detail_radio_11bg = 'radio-11bg',
    ap_detail_radio_11ng = 'radio-11ng',
    ap_detail_radio_11na = 'radio-11na',
    downlink = 'downlinks',
    uplink = 'uplink',
    uplink_history = 'uplink-history',
    client = 'client',
    lan_port_conf = 'pvlan',
    lan_status = 'lan',
)

tbl_captions = dict(
    general = 'General',
    info = 'Info',
    wlans = 'WLANs', # not being used
    radio_11bg = 'Radio 802.11b/g', # not being used
    radio_11ng = 'Radio 802.11g/n', # not being used
    radio_11na = 'Radio 802.11a/n',
    neighbor = 'Neighbor APs', # not being used
    uplink = 'Uplink', # not being used
)

ap_detail_hdrs_general = [
    'devname', 'description', 'location', 'gps', 'mac',
    'ip', 'external_ip_port', 'ip_type', 'model', 
    'serial_number', 'firmware_version'
]

ap_detail_hdrsid_general = [
    'devname', 'description', 'location', 'gps', 'mac',
    'ip', 'external-ip-port', 'ip-type', 'model', 
    'serial-number', 'firmware-version', 'ipv6'
]

ap_detail_general_title_map = {'Description': 'description',
                               'Device Name': 'devname',
                               'External IP:Port': 'external_ip_port',
                               'GPS Coordinates': 'gps',
                               'IP Address': 'ip',
                               'IPv6 Address': 'ipv6',
                               'IP Type': 'ip_type',
                               'Location': 'loaction',
                               'MAC Address':'mac',
                               'Model': 'model',
                               'S/N': 'serial_number' ,
                               'Version': 'firmware_version'}

ap_detail_ks_general = [
    'devname', 'description', 'location', 'gps', 'mac',
    'ip', 'external_ip_port', 'ip_type', 'model', 
    'serial_number', 'firmware_version'
]

ap_detail_hdrs_info = [
    'status', 'uptime', 'tunnel_mode', 'wlan_id', 'num_sta',
]
ap_detail_ks_info = ap_detail_hdrs_info

ap_detail_hdrs_radio = [
    'channel', 'config channel','channelization','wlangroup', 'spectralink','wlan_number',
    'bgscan', 'tx_power',
    'num_sta', 'retries', 'mcast', 
    'rx', 'tx', 'wlan_data_rx', 'wlan_data_tx',
    'noisefloor', 'phyerr', 'airtime',
    'avail_channel', 'block_channel', 'dfs_block_channel'
]

ap_detail_hdrs_uplink = [
    'ap', 'desc', 'type', 'assoc',
    'rssi', 'rx', 'tx', 'retries',
]
ap_detail_ks_uplink = ap_detail_hdrs_uplink

radio_11bg_hrds = ap_detail_hdrs_radio
radio_11bg_ks = radio_11bg_hrds

radio_11ng_hrds = ap_detail_hdrs_radio
radio_11ng_ks = radio_11ng_hrds

radio_11na_hrds = radio_11ng_hrds
radio_11na_ks = radio_11na_hrds


def _nav_to(zd):
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_ACCESS_POINTS)


def _get_all_ap_briefs(zd):
    '''
    return
    . a list of dict
    '''
    _nav_to(zd)
    time.sleep(3)
    return _get_all_ap_brief_info(zd)


def _get_all_ap_brief_info(zd):
    ap_info_list = wgt.get_tbl_rows(
                       zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
                       locators['ap_tbl_nav_loc'] % tbl_id['ap_summary']
                   )

    return update_ipv4_ipv6(ap_info_list)

#@author: Liang Aihua,@since: 2015-3-11,@change: get correct ipv4 and ipv6 address to fix bug zf-12242
#************
#def _parse_ipv4_ipv6(item):
#    if item.find('/') != -1:
#        res = item.split('/')
#        if 1 >= len(res):
#            return('', res[0])
#        else:
#            return(res[0],res[1])
#    elif item.find(':') != -1:
#        return('', item)
#    else:
#        return(item,'')

def _parse_ipv4_ipv6(item, sep = '/'):
    '''
    '''
    res = item.split(sep)
    if 1 >= len(res):
        return (res[0], '')

    else:
        return (res[0], res[1])
#**********************************************
   
def update_ipv4_ipv6(ap_data):
    '''
    '''
    ap_info_list = [ap_data] if type(ap_data) is not list else ap_data

    for ap_info in ap_info_list:
        count = 0
        for (k, v) in ap_info.iteritems():
            if 'ip' == k:
                (v4, v6) = _parse_ipv4_ipv6(v)
                count += 1
                break

        if 0 < count:
            ap_info.update({k: v4, 'ipv6': v6})

    return ap_info_list if type(ap_data) is list else ap_info


def _get_ap_brief_by(zd, match, verbose = False):
    '''
    '''
    _nav_to(zd)
    #####zj  2014-0324 fix ZF-7703
    start_time = time.time()
    timeout_refresh = 240
    while True:
        if time.time() - start_time > timeout_refresh :
            raise Exception("Error: APs summary find failed.")
        
        if not zd.s.is_element_present(locators['ap_tbl_filter_txt'] % tbl_id['ap_summary'], 5):
            continue
        
        #Chico@2014-6-19, if the loc is not exsit, method is_element_visible reports exception. ZF-8789
        #Chico, 2014-11-26, add the other tolerance to no finding some GUI factor 
        try:
            if zd.s.is_element_present(locators['ap_th_mac_addr'], 2):
                if zd.s.is_element_visible(locators['ap_th_mac_addr']):
                    break
        except:
            pass
        #Chico, 2014-11-26, add the other tolerance to no finding some GUI factor 
        #Chico@2014-6-19, if the loc is not exsit, method is_element_visible reports exception. ZF-8789
        time.sleep(10)
        
    #####zj  2014-0324 fix ZF-7703
    ap_info = wgt.get_first_row_by(
        zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
        locators['ap_tbl_nav_loc'] % tbl_id['ap_summary'], match,
        filter = locators['ap_tbl_filter_txt'] % tbl_id['ap_summary'],
        verbose = verbose,
    )

    return update_ipv4_ipv6(ap_info)


def _get_client_info_by(zd, match, verbose = False):
    '''
    '''
    client_info = wgt.get_first_row_by(
        zd.s, locators['ap_tbl_loc'] % tbl_id['client'],
        locators['ap_tbl_nav_loc'] % tbl_id['client'], match,
        filter = locators['ap_tbl_filter_txt'] % tbl_id['client'],
        verbose = verbose,
    )

    return client_info


def _query_ap_brief_by(zd, match, verbose=False):
    '''
    return
    . a list of dict
    '''
    _nav_to(zd)
    ap_info_list = wgt.get_tbl_rows_by(
        zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
        locators['ap_tbl_nav_loc'] % tbl_id['ap_summary'], match,
        filter = locators['ap_tbl_filter_txt'] % tbl_id['ap_summary'],
        verbose = verbose,
    )

    return update_ipv4_ipv6(ap_info_list)


def _sort_ap_brief_by(zd, match, sort, filter = None, verbose=False, wait = 2):
    '''
    return
    . a sorted list of dict.
    '''
    _nav_to(zd)
    return wgt.sort_tbl_col_by(
        zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
        locators['ap_tbl_nav_loc'] % tbl_id['ap_summary'],
        match, sort, filter = filter, verbose = verbose,
        wait = wait)


def _get_ap_detail_uplink_ap(zd):
    '''
    '''
    if not zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['uplink'], 0.5):
        return {}

    return _get_ap_detail_of_detail(
        zd, locators['ap_tbl_loc'] % tbl_id['uplink'],
        ap_detail_hdrs_uplink, ap_detail_ks_uplink
    )


def _get_ap_detail_general(zd):
    '''
    '''
    return _get_ap_detail_of_detail(
        zd, locators['ap_detail_htbl_loc'] % tbl_captions['general'],
        ap_detail_hdrs_general, ap_detail_ks_general
    )

def _get_ap_detail_general2(zd):
    '''
    '''
    return _get_ap_detail_of_detail2(
        zd, locators['ap_detail_htbl_loc'] % tbl_captions['general'],
        ap_detail_hdrsid_general
    )

def _get_ap_detail_info(zd):
    '''
    '''
    return _get_ap_detail_of_detail(
        zd, locators['ap_detail_htbl_loc'] % tbl_captions['info'],
        ap_detail_hdrs_info, ap_detail_ks_info
    )


def _get_ap_detail_radio(zd):
    '''
    '''
    radio = {}
    if zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11ng'], 0.5):
        radio = _get_ap_detail_of_detail(
            zd, locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11ng'],
            radio_11ng_hrds, radio_11ng_ks
        )
    elif zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11bg'], 0.5):
        radio = _get_ap_detail_of_detail(
            zd, locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11bg'],
            radio_11bg_hrds, radio_11bg_ks
        )

    return radio

def _get_ap_detail_radio_na(zd):
    '''
    '''
    radio_na = {}
    if zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11na'], 0.5):
        radio_na = _get_ap_detail_of_detail(
            zd, locators['ap_tbl_loc'] % tbl_id['ap_detail_radio_11na'],
            radio_11na_hrds, radio_11na_ks
        )

    return radio_na

def _get_ap_detail_wlans(zd, group_by = 'wlan'):
    '''
    For dual band ap, there will be two rows in detail wlans table.
    If status column exist:
        If at least one of them are up, return wlan status is up.
        If both wlan are up, the secondary wlan is returned.
        If both wlan are down, no wlan are returned.
    If no status column:
        Return secondary wlan. 
    
    Output:
      group_by = 'wlan':
    {u'open-none-193-532': {u'bssid': u'04:4f:aa:2a:62:48',
                            u'radio_type': u'802.11b/g',
                            u'vap_up': u'Up',
                            u'wlan': u'open-none-193-532'}}
    '''
    wlans = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['ap_detail_wlans'],
                             locators['ap_tbl_nav_loc'] % tbl_id['ap_detail_wlans'])
    
    if len(wlans) > 1:
        new_wlans = []
        for wlan in wlans:
            if wlan.has_key('vap_up'):
                if wlan['vap_up'].lower() == 'up':
                    new_wlans.append(wlan)
            else:
                #Return first row if no status column.
                new_wlans.append(wlans[0])
                break
    else:
        new_wlans = wlans
    
    wlans = list_to_dict(new_wlans, group_by)

    return wlans


def _get_ap_detail_neighbor(zd):
    '''
    '''
    neighbor = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['ap_detail_neighbors'],
                                locators['ap_tbl_nav_loc'] % tbl_id['ap_detail_neighbors'])
    neighbor = list_to_dict(neighbor, 'mac')

    return neighbor


def _get_ap_detail_mesh_tree_by(zd, match):
    '''
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, match)

    return dict (
        uplink = _get_ap_detail_uplink_ap(zd),
        downlink = _get_ap_detail_downlink_aps(zd),
    )


def _get_ap_detail_by(zd, match):
    '''
    '''
    _nav_to(zd)
    _open_ap_detail_page(zd, match)

    return dict (
        general = _get_ap_detail_general(zd),
        info = _get_ap_detail_info(zd),
        radio = _get_ap_detail_radio(zd),
        radio_na = _get_ap_detail_radio_na(zd),
        wlans = _get_ap_detail_wlans(zd),
        neighbor = _get_ap_detail_neighbor(zd),
        uplink = _get_ap_detail_uplink_ap(zd),
        downlink = _get_ap_detail_downlink_aps(zd),
        lan_port_conf = _get_ap_detail_lan_port_conf(zd),
        lan_status = _get_ap_detail_lan_status(zd),
    )


def _get_ap_detail_of_detail(zd, loc, hdrs, ks = []):
    '''
    '''
    p = dict(
        loc = loc,
        hdrs = hdrs,
        ks = [],
    )
    if ks is not None:
        p.update({'ks': ks})

    return zd.s.get_htable_rows2(**p)

def _get_ap_detail_of_detail2(zd, loc, hdrs):
    '''
    '''
    p = dict(
        loc = loc,
        hdrs = hdrs,
    )

    return zd.s.get_htable_rows3(**p)

def _get_ap_detail_uplink_aps_history(zd):
    '''
    '''
    if not zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['uplink_history'], 0.5):
        return {}

    uplink_ap = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['uplink_history'],
                                 locators['ap_tbl_nav_loc'] % tbl_id['uplink_history'])
    uplink_ap = list_to_dict(uplink_ap, 'ap')

    return uplink_ap


def _get_ap_detail_downlink_aps(zd):
    '''
    '''
    if not zd.s.is_element_present(locators['ap_tbl_loc'] % tbl_id['downlink'], 0.5):
        return {}

    downlink_aps = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['downlink'],
                                    locators['ap_tbl_nav_loc'] % tbl_id['downlink'])
    downlink_aps = list_to_dict(downlink_aps, 'ap')

    return downlink_aps

def _get_ap_detail_lan_port_conf(zd):
    '''
    '''
    port_conf = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['lan_port_conf'],
                             locators['ap_tbl_nav_loc'] % tbl_id['lan_port_conf'])
    
    return port_conf

def _get_ap_detail_lan_status(zd):
    '''
    '''
    status = wgt.get_tbl_rows(zd.s, locators['ap_tbl_loc'] % tbl_id['lan_status'],
                             locators['ap_tbl_nav_loc'] % tbl_id['lan_status'])
    
    return status

def _click_on_ap_btn(zd, match, loc, wait = 1.5):
    r = _get_ap_brief_by(zd, match, True)
    btn = (r['tmpl'] % r['idx']) + loc
    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn, wait)

    else:
        raise Exception('Unable to click on the button since it is disabled')


def _reboot_aps(zd):
    _nav_to(zd)
    #zd.s.choose_ok_on_next_confirmation()
    for r in wgt.iter_tbl_rows_with_pages(
            zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
            locators['ap_tbl_nav_loc'] % tbl_id['ap_summary']):

        btn = (r['tmpl'] % r['idx']) + locators['ap_restart_btn']
        if zd.s.is_visible(btn):
            zd.s.click_and_wait(btn)

        else:
            raise Exception('Unable to reboot AP [%s] since the reboot button'
                            ' is disabled' % r['row']['mac'])


def _reboot_ap(zd, match):
    r = _get_ap_brief_by(zd, match, True)
    zd.s.choose_ok_on_next_confirmation()
    btn = (r['tmpl'] % r['idx']) + locators['ap_restart_btn']
    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn, wait=3, timeout=3)
    else:
        raise Exception('Unable to reboot AP [%s] since the reboot button'
                        ' is disabled' % r['row']['mac'])
        

def _click_mon_aps_refresh_btn(zd):
    _nav_to(zd)
    if zd.s.is_visible(locators['ap_mon_apsummary_refresh']):
        zd.s.click_and_wait(locators['ap_mon_apsummary_refresh'])


def _open_pingtool_by_mac_addr(zd, match):
    r = _get_ap_brief_by(zd, match, True)
    btn = (r['tmpl'] % r['idx']) + locators['ap_pingtool_btn']

    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn)

    else:
        raise Exception('Unable to open network connectivity on AP [%s] since the network connectivity button'
                        ' is disabled' % r['row']['mac'])


def _allow_ap_joining(zd, match):
    return _click_on_ap_btn(zd, match, locators['ap_allow_joining_btn'])


def _open_ap_detail_page(zd, match):
    return _click_on_ap_btn(zd, match, locators['ap_detail_page_btn'], 5)

