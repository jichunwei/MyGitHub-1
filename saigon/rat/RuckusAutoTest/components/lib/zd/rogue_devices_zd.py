'''
'''
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt


locators = dict(
    rogue_tbl_loc = "//table[@id='%s']",
    client_tbl_nav_loc = "//table[@id='%s']/tfoot",
    client_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
)

tbl_id = dict(
    rogue_summary = 'roguesummary',
)

ACTIVE_ROGUE_HDR_MAP = {
    'mac': 'mac',
    'channel': 'channel',
    'radio_type': 'radio',
    'rogue_type': 'type',
    'is_open': 'encrption',
    'ssid': 'ssid',
    'last_seen': 'timestamp',
    'action': 'action',
}

def _nav_to(zd):
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_ROGUE_DEVICES,10)

def _get_all_rogue_devices_briefs(zd, match = {}):
    '''
    return a list of dict
    '''
    _nav_to(zd)
    tbl = locators['rogue_tbl_loc'] % tbl_id['rogue_summary']
    if match:    
        wgt._fill_search_txt(zd.s, locators['client_tbl_filter_txt'] % tbl_id['rogue_summary'], match.values()[0])
        
    try:
        return wgt.get_tbl_rows(zd.s, tbl,
                            locators['client_tbl_nav_loc'] % tbl_id['rogue_summary'])
    finally:
        wgt._clear_search_txt(zd.s, tbl)
        
    


def _get_rogue_device_brief_by(zd, match, verbose = False):
    '''
    '''
    _nav_to(zd)
    return wgt.get_first_row_by(zd.s, locators['rogue_tbl_loc'] % tbl_id['rogue_summary'],
                                locators['rogue_tbl_nav_loc'] % tbl_id['rogue_summary'], match,
                                locators['rogue_tbl_filter_txt'] % tbl_id['rogue_summary'], verbose)


def get_active_rouge_devices_list(zd, mac = None):
    """
    get information of all rogue devices  in page Monitor->Rogue Devices and
    returns a list of dictionaries each of which contains information of one client:
    [{'mac':'', 'channel':'', 'radio_type':'', 'rogue_type':'', 'is_open':'', 'ssid':'', 'last_seen':'', 'action':''}]
    """    
    if mac:
        return wgt.map_rows(
            _get_all_rogue_devices_briefs(zd, match={'mac':mac}),
            ACTIVE_ROGUE_HDR_MAP
        )
    else:
        return wgt.map_rows(
            _get_all_rogue_devices_briefs(zd),
            ACTIVE_ROGUE_HDR_MAP
    )
