'''
'''
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt


locators = dict(
    zd_eth_tbl_loc = "//table[@id='%s']",
    client_tbl_nav_loc = "//table[@id='%s']/tfoot",
)

tbl_id = dict(
    eth_summary = 'ethsummary',
)

ZD_ETH_INFO_HDR_MAP = {
    'portid': 'port_id',
    'mac': 'mac',
    'ethname': 'eth_name',
    'state': 'status',
    'ethspeed': 'speed',
    'inpkts': 'input_pkts',
    'inbytes': 'input_bytes',
    'outpkts': 'output_pkts',
    'outbytes': 'output_bytes',
}

def _nav_to(zd):
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_SYSTEM_INFO,10)

def _get_all_zd_ethernet_info(zd):
    '''
    return a list of dict
    '''
    _nav_to(zd)
    tbl = locators['zd_eth_tbl_loc'] % tbl_id['eth_summary']

    return wgt.get_tbl_rows(zd.s, tbl, tbl) #no 'nav' existed

def get_all_zd_ethernet_info(zd):
    """
    get information of all rogue devices  in page Monitor->Rogue Devices and
    returns a list of dictionaries each of which contains information of one client:
    [{'mac':'', 'channel':'', 'radio_type':'', 'rogue_type':'', 'is_open':'', 'ssid':'', 'last_seen':'', 'action':''}]
    """    
    return wgt.map_rows(
        _get_all_zd_ethernet_info(zd),
        ZD_ETH_INFO_HDR_MAP
    )
