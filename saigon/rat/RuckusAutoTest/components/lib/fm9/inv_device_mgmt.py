'''
IMPORTANT WARNING ON _get and _get_tbl:
. locators['tbl'] is used for 3 pages and the table headers are different for
  each page. Before accessing this, please check out the _get_view_devices()

pp(fm.lib.idev.get_all_ap_views(fm))
pp(fm.lib.idev.get_all_zd_views(fm))
pp(fm.lib.idev.get_all_client_views(fm))

pp(fm.lib.idev.get_all_aps_by_view_name(fm))
pp(fm.lib.idev.get_all_aps_by_view_name(fm, 'ruckus'))
pp(fm.lib.idev.get_ap_brief_by_ip_addr(fm, '192.168.0.1'))
dv = fm.lib.idev.get_ap_device_view_by_ip_addr(fm, '192.168.0.1')
fm.lib.idev.cleanup_ap_device_view(fm, dv)

fm.lib.idev.create_ap_view(fm, 'ruckus', [['AP Name', 'Contains', 'ruckus']])
'''

from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.common.utils import try_interval
from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.fm9 import _device_filter as df
from RuckusAutoTest.components.lib import common_fns as fns

from RuckusAutoTest.components.lib.fm import inv_device_mgmt_fm as idev


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_ap_views(fm):
    return _get_views(fm, 'ap')


def get_all_zd_views(fm):
    return _get_views(fm, 'zd')


def get_all_client_views(fm):
    return _get_views(fm, 'client')


def get_all_aps(fm):
    return get_all_aps_by_view_name(fm, view_name = '')


def get_all_zds(fm):
    return get_all_zds_by_view_name(fm, view_name = '')


def get_all_aps_by_view_name(fm, view_name = ''):
    return _get_view_devices(fm, 'ap', view_name, {})


def get_all_zds_by_view_name(fm, view_name = ''):
    return _get_view_devices(fm, 'zd', view_name, {})


def get_all_clients_by_view_name(fm, view_name = ''):
    return _get_view_devices(fm, 'client', view_name, {})


def get_ap_brief_by_ip_addr(fm, ip_addr, view_name = ''):
    return _get_view_device(fm, dict(ip = ip_addr), 'ap', view_name)


def get_ap_device_view_by_ip_addr(fm, ip_addr, view_name = ''):
    return _get_ap_device_view(
        fm, get_ap_brief_by_ip_addr(fm, ip_addr, view_name)
    )


def cleanup_ap_device_view(fm, device_view):
    return idev.cleanup_ap_device_view(fm, device_view)


def get_zd_brief_by_ip_addr(fm, ip_addr, view_name = ''):
    return _get_view_device(fm, dict(ip = ip_addr), 'zd', view_name)


def get_client_brief_by_ip_addr(fm, ip_addr, view_name = ''):
    return _get_view_device(fm, dict(ip = ip_addr), 'client', view_name)


def get_zd_device_view_by_ip_addr(): pass
def cleanup_zd_device_view(): pass

def create_model_group_for_ap(fm, **kwa):
    '''
    create a model group for ap in Inventory > Search (AP group)
    '''
    create_ap_view(
        fm, kwa['model'],
        [['Model', 'Exactly equals', kwa['model'].upper()]],
    )

def create_ap_view(fm, view_name, options):
    return _create_view(fm, view_name, options, device_type = 'ap')


def create_zd_view(fm, view_name, options):
    return _create_view(fm, view_name, options, device_type = 'zd')


def create_client_view(fm, view_name, options):
    return _create_view(fm, view_name, options, device_type = 'client')


def delete_ap_view(): pass
def delete_zd_view(): pass
def delete_client_view(): pass


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
AP_TH_MAP = {
    'devicename': 'name',
    'serialnumber': 'serial',
    'ipaddress': 'ip',
    'natipaddress': 'ex_ip',
    'modelname': 'model',
    'lastseen': 'last_seen',
    'uptime': 'uptime',
    'connect': 'conn',
    'tagname': 'tag',
    'fwversion': 'firmware',
    'undefined': 'action',
    'location': 'location',
}

ZD_TH_MAP = {
    'devicename': 'name',
    'serialnumber': 'serial',
    'ipaddress': 'ip',
    'natipaddress': 'ex_ip',
    'modelname': 'model',
    'lastseen': 'last_seen',
    'uptime': 'uptime',
    'connect': 'conn',
    'tagname': 'tag',
    'fwversion': 'firmware',
    'action': 'action',
    'location': 'location',
    'admin.inventory.managedevices.ui.zdredundancystatus': 'redun_status',
}

CLIENT_TH_MAP = {
    'zonedirector': 'name',
    'mac': 'mac',
    'userip': 'userip',
    'accesspoint': 'ap_name',
    'wlan': 'wlan',
    'channel': 'channel',
    'radio': 'radio',
    'signal': 'signal',
    'status': 'status',
}

DEVICE_VIEW_LINK = "//table[@dojoattachpoint='tableArea']" \
                   "//tr[%s]//span[@class='deviceLink']" % '1'

get_conn = idev.get_conn # use old function

locators = dict(
    # on 'Search' pages ---
    refresh_btn = Ctrl("//div[@id='refreshButtonArea']/img[contains(@src,'img_Refresh.gif')]", 'button'), # for FM9.0
    tbl = Ctrl(
        dict(tbl = "//table[@dojoattachpoint='tableArea']",
             nav = "//table[@class='pageSelector']",             
             search_box = "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            links = dict(lnk_tmpl = "//span[.='%s']"),
            fns = [get_conn,]
        ),
    ),
    xls_export_btn = Ctrl("//input[@value='XLS File']", 'button'),
    csv_export_btn = Ctrl("//input[@value='CSV File']", 'button'),

    # save as view ---
    view_name = Ctrl("//input[@dojoattachpoint='viewNameTextField']"),
    view_desc = Ctrl("//input[@dojoattachpoint='viewDesTextField']"),
    save_btn = Ctrl("//input[@dojoattachpoint='saveViewButton']", 'button'),

    # on 'Manage * Views' pages ---
    view_tbl = Ctrl(
        dict(tbl = "//table[@dojoattachpoint='tableArea']",
             nav = "//table[@class='pageSelector']",
             search_box = "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            links = dict(query = "//span[@class='sb'][.='Query']"),
        ),
    ),
)


ctrl_order = '''
tbl xls_export_btn cvs_export_btn
[None view_name view_desc save_btn]
'''

save_view_co = '''
[None view_name view_desc save_btn]
'''

def _get_loc(fm, page):
    return dict(
        ap = fm.INVENTORY_SEARCH_AP,
        zd = fm.INVENTORY_SEARCH_ZD,
        client = fm.INVENTORY_SEARCH_CLIENT,

        ap_view = fm.INVENTORY_MANAGE_AP,
        zd_view = fm.INVENTORY_MANAGE_ZD,
        client_view = fm.INVENTORY_MANAGE_CLIENT,
    )[page]


def nav_to(fm, page = 'ap', force = False):
    fm.navigate_to(fm.INVENTORY, _get_loc(fm, page), force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)


def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)

def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)

def _get_tbl(fm, tbl, cfg, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)


def _get_views(fm, device_type = 'ap'):
    nav_to(fm, device_type + '_view')
    return _get_tbl(fm, 'view_tbl', {})


def _set_view(fm, device_type = 'ap', view = '', force = False):
    '''
    . if view is given
      . navigate to the manage page, find the view and click on it
    . else just go to the page
    '''
    if view:
        nav_to(fm, device_type + '_view', force)
        lnk = _get(fm, dict(view_tbl = dict(get = '1st',
                                            match = dict(viewname = view,))),
                   'view_tbl')['view_tbl']['links']['query']
        fm.s.safe_click(lnk)
        fm.s.wait_for_page_to_load()
        fm.current_menu = _get_loc(fm, device_type)
        return
    nav_to(fm, device_type, force)


def _select_filter_txt(tbl_cfg, ignore_fields = [], match= {}):
    '''
    . some of fields can not be used as filter text (i.e. conn),
      this functions select a good field text to filter results
    input
    . tbl_cfg will be updated accordingly
    '''
    for k, v in match.iteritems():
        if k not in ignore_fields:
            tbl_cfg['search_box'] = v
            return


def _get_view_devices(fm, device_type = 'ap', view = '', match = {}):
    '''
    . set to a view and get all devices belong to that view
    . filter by the first match criteria
    NOTE:
    . cannot apply to connection, since it is a picture (not text)
      so make sure you don't pass match=dict(conn = 'connected') in
    '''
    _set_view(fm, device_type, view)
    locators['tbl'].cfg['hdr_map'] = dict(
        ap = AP_TH_MAP,
        zd = ZD_TH_MAP,
        client = CLIENT_TH_MAP,
    )[device_type]
    p = {}
    if match:
        p['match'] = match
        _select_filter_txt(p, ['connect'], match)
    return _get_tbl(fm, 'tbl', p, False)


def _get_view_device(fm, match, device_type = 'ap', view = ''):
    '''
    . filter by search_txt then get all table rows
    . if more than one row found then raise an exception
    '''
    devs = _get_view_devices(fm, device_type, view, match)
    if len(devs) > 1:
        raise Exception('More than one device found')
    if len(devs) <= 0:
        raise Exception('No device found')

    return devs[0]


def _get_ap_device_view(fm, device_brief):
    return idev._get_ap_device_view(fm, device_brief, DEVICE_VIEW_LINK)


def _fill_in_search_options(fm, options,
                            device_type = 'ap',
                            get_results = False):
    '''
    . fill in the search criteria on the new search page and search for result
    . after calling this, save_search_results_as_view can be called for saving
      the result
    input
    . device_type
    . a list of criteria, something likes
        options = [
            ['Device Name', 'Contains', 'al'],
            ['Serial Number', 'Starts with', '1008'],
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    nav_to(fm, device_type)
    df.fill_in(fm, options)
#    if get_results:
        # click query first before getting result
#        return _get_tbl(fm, 'tbl', {}, False)


def _save_search_results_as_view(fm, view_name, description = ''):
    '''
    . save the searched result as a view
    NOTE: this function is called right after fill_in_search_options()
    '''
    p = dict(
        view_name = view_name,
        view_desc = description,
    )
    if not description:
        p['view_desc'] = p['view_name']
    return _set(fm, p, order = save_view_co)


def _create_view(fm, view_name, options, device_type = 'ap'):
    _fill_in_search_options(fm, options, device_type, False)
    _save_search_results_as_view(fm, view_name)
    nav_to(fm, device_type, True)


def find_device_serial(fm, serial, device_type='ap', timeout=180):
    '''
    This function is to search a device base on serial number in
    Invetory > Manage Device > Saved View.
    kwa:
    - serial
    - timeout: second
    Output:
    - (None, None) if not found.
    - Content of a row (dictionary) and Row locator if Found
    Note:
    - Row locator is a locator of a row look like:
        //table[@id='autoConfigtableList']/tbody/tr[1]
        //table[@id='autoConfigtableList']/tbody/tr[2]
        ...
        //table[@id='autoConfigtableList']/tbody/tr[n]

    - This function uses "searchbox" on FM 8.0 to search a device base on  "serial number".
    '''
    s, l = fm.selenium, locators
    nav_to(fm , device_type, True)

    data = None
    for i in try_interval(timeout, 10):
        data = ac.get(
            s, l,
            {'view_tbl': dict(
                        get = '1st', match = {'serialnumber':serial}, op = 'eq',
                        search_box = serial,
                    ),
            },
            ['refresh_btn']
        )['view_tbl']
        if data: break

    return (None, None) if not data else (data['row'], (data['tmpl'] % data['idx']))
