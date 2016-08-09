import logging
import time

from RuckusAutoTest.common.utils import try_interval
from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import Ctrl

from RuckusAutoTest.components.lib.fm import _device_filter_fm as df
from RuckusAutoTest.components.lib import common_fns as fns

from RuckusAutoTest.components import get_fmdv_com


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_view_names(fm):
    return _get(fm, dict(view = dict(get='all')), is_nav = True)['view'].keys()


def get_all_aps(fm):
    return get_all_devices_by_view_name(fm, view_name = 'All Standalone APs')


def get_all_zds(fm):
    return get_all_devices_by_view_name(fm, view_name = 'All ZoneDirectors')


def get_all_devices_by_view_name(fm, view_name = 'All Standalone APs'):
    return _get_view_devices(fm, view = view_name)


def get_device_brief_by_ip_addr(fm, ip_addr,
                                view_name = 'All Standalone APs'):
    return _get_view_device(fm, dict(ip = ip_addr), view_name)


def get_device_brief_by_serial(fm, serial_no,
                               view_name = 'All Standalone APs'):
    return _get_view_device(fm, dict(serial = serial_no), view_name)


def get_ap_device_view_by_serial(fm, serial_no,
                                 view_name = 'All Standalone APs'):
    return _get_ap_device_view(
        fm, get_device_brief_by_serial(fm, serial_no, view_name)
    )


def get_ap_device_view_by_ip_addr(fm, ip_addr,
                                  view_name = 'All Standalone APs'):
    return _get_ap_device_view(
        fm, get_device_brief_by_ip_addr(fm, ip_addr, view_name)
    )


def cleanup_ap_device_view(fm, device_view):
    '''
    . after using the DeviceView, clean it up
    steps
    . reset the device_view to initial state
    . close the pop up window
    . go back to the main window
    '''
    device_view.reset()
    fm.s.get_eval('window.close()')
    fm.s.select_window(FM_MAIN_WINDOW_NAME) # the main window
    time.sleep(1)


def create_ap_view(fm, view_name, options):
    return create_view(fm, view_name, 'Standalone APs', options)


#-----------------------------------------------------------------------------
#  PRIVATE SECTION
#-----------------------------------------------------------------------------
DEVICE_TH_MAP = {
    'device_name': 'name',
    'serial_#': 'serial',
    'ip_address': 'ip',
    'external_ip': 'ex_ip',
    'model': 'model',
    'last_seen': 'last_seen',
    'uptime': 'uptime',
    'connection': 'conn',
    'tag': 'tag',
    'software': 'firmware',
    'actions': 'action',
}

VIEW_TBL = "//div[@label='Saved Views']//table[@widgetid='DeviceEntityTable']"
SEARCH_TAB = "//div[@label='New Search']"
DEVICE_VIEW_WINDOW_NAME = 'Support'
FM_MAIN_WINDOW_NAME = ''

# NOTE
# . since this link is clicked after finding unique device
#   so the row index must be 1
DEVICE_VIEW_LINK = VIEW_TBL + "//tr[%s]//div[@class='deviceLink']/span" % '1'


def get_conn(se, tr):
    '''
    HACK! TBD a better way
    input
    . row: is the table row when running on verbose mode
    '''
    k = 'conn'
    if k not in tr:
        k = 'status' # another hack for client table on FM 9, too bad!
    is_conn_loc = "//img[@title='connected']"
    tr['row'][k] = 'disconnect'
    if se.is_element_present((tr['tmpl'] % tr['idx']) + is_conn_loc, .2):
        tr['row'][k] = 'connected'


locators = dict(
    refresh_btn = Ctrl("//div/img[@id='refreshEntity']", 'button'),
    view_tab = Ctrl("//span[.='Saved Views']", 'button'),
    search_tab = Ctrl("//span[.='New Search']", 'button'),

    view = Ctrl("//div[contains(.,'Select all devices in the view')]/span",
                'dojo_select'),
    set_tags_btn = Ctrl("//span[contains(.,'Set Tags')]", 'button'),
    view_details_btn = Ctrl("//span[contains(.,'View Details')]", 'button'),
    edit_view_btn = Ctrl("//span[contains(.,'Edit View')]", 'button'),
    update_view_btn = Ctrl("//span[contains(.,'Update View')]", 'button'),

    view_tbl = Ctrl(
        dict(tbl = VIEW_TBL,
             nav = "//div[@label='Saved Views']//td[@class='pageSelecter']",
			 search_box = "//input[@id='Device_SearchBox']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'id',
            hdr_map = DEVICE_TH_MAP,
            links = dict(lnk_tmpl = "//span[.='%s']"),
            fns = [get_conn,]
        ),
    ),
    device_cate = Ctrl(
        SEARCH_TAB + "//tr[contains(./td,'Device Category')]/td/span",
        'dojo_select'
    ),
    search_tmpl = None, # place holder
    search_btn = Ctrl(SEARCH_TAB + "//input[@id='searchButton']", 'button'),
    save_search_lnk = Ctrl(SEARCH_TAB + "//span[@id='saveLink']", 'button'),
    view_name = Ctrl(SEARCH_TAB + "//input[@id='viewNameTextField']"),
    view_desc = Ctrl(SEARCH_TAB + "//input[@id='viewDescTextField']"),
    save_btn = Ctrl(SEARCH_TAB + "//input[@id='saveButton']", 'button'),

    update_view_name = Ctrl(
        SEARCH_TAB + "//input[@id='updateViewNameTextField']"
    ),
    update_btn = Ctrl(SEARCH_TAB + "//input[@id='updateButton']", 'button'),

    searched_tbl = Ctrl(
        dict(tbl = SEARCH_TAB + "//table[@widgetid='DeviceSearchEntityTable']",
             nav = SEARCH_TAB + "//td[@class='pageSelecter']",),
        'ltable',
        cfg = dict(
            hdr_attr = 'id',
            hdr_map = DEVICE_TH_MAP,
            links = dict(lnk_tmpl = "//span[.='%s']")
        ),
    ),
)

ctrl_order = '''
[refresh_btn
  [view_tab
    view set_tags_btn view_details_btn edit_view_btn view_tbl
  None]
  [search_tab
    [None
      device_cate search_tmpl
    search_btn]
    [save_search_lnk view_name view_desc save_btn]
    [search_btn searched_tbl None]
  None]
None]
'''

save_view_co = '''
[save_search_lnk view_name view_desc save_btn]
'''

edit_view_co = '''
[edit_view_btn
  [None
    device_cate search_tmpl
  search_btn]
  [update_view_btn update_view_name None]
update_btn]
'''
# [update_view_btn None None]: hack around, must have update_view_name for now

locators, (ctrl_order, edit_view_co) = df.fmt_ctrls(
    locators, [ctrl_order, edit_view_co], tmpl = 'device_mgmt',
    tmpl_k = 'search_tmpl', space_shift = 6, k_prefix = ''
)


def nav_to(fm, force = False):
    fm.navigate_to(fm.INVENTORY, fm.INVENTORY_MANAGE_DEVICES, force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def _set(fm, cfg, is_nav = True, order = 'default'):
    return fns.set(m, fm, cfg, is_nav, order)

def _get(fm, cfg, is_nav = True, order = 'default'):
    return fns.get(m, fm, cfg, is_nav, order)

def _get_tbl(fm, tbl, cfg, is_nav = False, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav, order)


def _set_view(fm, view = 'All Standalone APs'):
    return _set(fm, dict(view = view), is_nav = True)


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


def _get_view_devices(fm, view = 'All Standalone APs', match = {}):
    '''
    . set to a view and get all devices belong to that view
    . filter by the first match criteria
    NOTE:
    . cannot apply to connection, since it is a picture (not text)
      so make sure you don't pass match=dict(conn = 'connected') in
    '''
    _set_view(fm, view)
    p = {}
    if match:
        p['match'] = match
        _select_filter_txt(p, ['conn'], match)
    return _get_tbl(fm, 'view_tbl', p, False)


def _get_view_device(fm, match, view = 'All Standalone APs'):
    '''
    . filter by search_txt then get all table rows
    . if more than one row found then raise an exception
    '''
    devs = _get_view_devices(fm, view, match)
    if len(devs) > 1:
        raise Exception('More than one device found')
    if len(devs) <= 0:
        raise Exception('No device found')

    return devs[0]


def _create_ap_device_view(fm, model, serial, ip_addr):
    '''
    Returning a FM Device View WebUI based on 'model'.
    This function creates object per needed
    '''
    model = model.lower()
    for dv in fm.device_views: # is it on the list yet?
        if dv.model == model:
            return dv
    dv = get_fmdv_com(
        dict(fm = fm, model = model, serial = serial, ip_addr = ip_addr)
    )
    fm.device_views.append(dv)
    return dv


def _get_ap_device_view(fm, device_brief, device_link = DEVICE_VIEW_LINK):
    '''
    NOTE: caller must call cleanup_ap_device_view() after using
    input
    . device_brief: is the row from _get_view_device()
    '''
    fm.s.click_and_wait(device_link)
    fm.s.wait_for_pop_up(DEVICE_VIEW_WINDOW_NAME)
    fm.s.select_window(DEVICE_VIEW_WINDOW_NAME)
    time.sleep(1)

    return _create_ap_device_view(
        fm, device_brief['model'],
        device_brief['serial'], device_brief['ip'].split(':')[0]
    )

def create_model_group_for_ap(fm, **kwa):
    '''
    create a model group for ap in Inventory > Manage Devices
    '''
    create_ap_view(
        fm, kwa['model'],
        [['Model Name', 'Exactly equals', kwa['model'].upper()]],
    )

def create_view(fm, view_name, device_category, options):
    '''
    input
    . options: refer to fill_in_search_options for details
    '''
    _fill_in_search_options(fm, options, device_category, False)
    _save_search_results_as_view(fm, view_name)
    return fm.get_status()


def _fill_in_search_options(fm, options,
                            device_category = 'Standalone APs',
                            get_results = False):
    '''
    . fill in the search criteria on the new search page and search for result
    . after calling this, save_search_results_as_view can be called for saving
      the result
    input
    . device_category
    . a list of criteria, something likes
        options = [
            ['Device Name', 'Contains', 'al'], 'and',
            ['Serial Number', 'Starts with', '1008'], 'or',
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    p = dict(
        device_cate = device_category,
    )
    p.update(df.map_where_conditions(options))
    _set(fm, p, is_nav = True)
    if get_results:
        return _get_tbl(fm, 'searched_tbl', {}, False)


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
    return _set(fm, p, is_nav = False, order = save_view_co)


#-----------------------------------------------------------------------------
# OLD FUNCTIONS - NEED VALIDATE BEFORE USING
#-----------------------------------------------------------------------------
def __set_view(obj, view):
    '''
    view: the view name
    '''
    return set(obj, dict(view = view), is_nav = True)


def _create_view(fm, cfg):
    '''
    cfg:
    1. device_cate, (attr, op, value_txt, combine_lnk) x [1..3]: search device
    2. view_name, view_desc: optional, have this means save view
    after this 'searched_tbl' can be get by get_tbl_iter() for checking up
    '''
    return _set(fm, cfg, is_nav = True)


def _edit_view(fm, cfg):
    '''
    . requiring the view is selected beforehand
    . refer to edit_view_co for details
    NOTE:
      . view_name field is changed to update_view_name
      . add update_view_btn, update_btn in for sure (since most of the cases,
        they are not added automatically)
    '''
    cfg.update(dict(update_view_btn = None, update_btn = None))
    return _set(fm, cfg, is_nav = False, order = edit_view_co)


def find_device_serial(fm, serial, timeout = 180):
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
    logging.info('Searching a device with serial "%s"', serial)
    nav_to(fm , True)
    #s.click_and_wait(l['view_tab'], 1.5)
    #s.click_and_wait("//span[.='Saved Views']", 1.5)

    data = None
    for i in try_interval(timeout, 10):
        data = ac.get(
            s, l,
            {'view_tbl': dict(
                        get = '1st', match = {'serial':serial}, op = 'eq',
                        search_box = serial,
                    ),
            },
            ['refresh_btn']
        )['view_tbl']
        if data: break

    return (None, None) if not data else (data['row'], (data['tmpl'] % data['idx']))


def get_list_device_serials(fm):
    '''
    This function is to get all of device serials in Inventory > Manage Device
    '''
    s, l = fm.selenium, locators
    #logging.info('Searching a device with serial "%s"', kwa['serial'])
    nav_to(fm , True)
    #s.click_and_wait(locators['view_tab'], 1.5)
    #s.click_and_wait("//span[.='Saved Views']", 1.5)
    serials = []
    # get generator of the table
    gen_tbl = ac.get(s, l, ['view_tbl'])['view_tbl']


    for r in gen_tbl:
        serials.append(r['serial'])

    return serials
