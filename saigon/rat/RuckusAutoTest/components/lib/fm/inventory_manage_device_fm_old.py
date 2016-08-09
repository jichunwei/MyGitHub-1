"""
Examples:

import scaling.initFmScaling as IFS
import scaling.dimark_dict as DMKINFO
import RuckusAutoTest.components.lib.fm_inventory_manage_device_old as IMD
from pprint import pprint

zd1 = IMD.get_manage_devices_by(myfm, category="ZoneDirectors", type="Device Name", ope="Starts With", value="vmware-")
pprint(DMKINFO.ViewMgmt_DimarkAP['views']['set_18'])
IMD.is_view_exist(fm, 'scaling: set_18 Dimark APs')
IMD.make_view(fm,  **DMKINFO.ViewMgmt_DimarkAP['views']['set_18'])

"""
import re
import logging
import time

from RuckusAutoTest.components.lib.fm import admin_view_mgmt_fm_old as AVM

def fm_work_area():
    return ('Inventory', ['Manage Device'])

Locators_INVENTORY_MANAGE_DEVICE = dict(
    # Saved Views
    viewSelect = r"//td[@id='textView']//div[@id='views']/span",
    viewResult = r"//label[@id='DeviceentityCountValueLabel']",
    # New Search
    searButton = r"//input[@id='searchButton']",
    searResult = r"//label[@id='entitySearchCountValueLabel']",
    searTbl = r"//form[@id='searchRequestForm']/div[@id='tableArea']/table",
    searNav = r"//form[@id='searchRequestForm']/div[@id='tableArea']/table//td[@class='pageSelecter']",
)

def nav_to_my_page(FM):
    FM.navigate_to(FM.INVENTORY, FM.INVENTORY_MANAGE_DEVICES)

def get_manage_devices_by(FM, **kwargs):
    fcfg = dict(debug = False,
                category = 'Standalone APs',
                type = 'Serial Number',
                op = 'Starts with',
                value = '',
                totalonly = False)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    nav_to_my_page(FM)
    locx = FM.resource['Locators'] 
    locInv = Locators_INVENTORY_MANAGE_DEVICE
    fcfg['type'] = _m_device_type(fcfg['type'])
    fcfg['op'] = _m_device_op(fcfg['op'])
    FM.selenium.safe_click(locx['ManageDevice_NewSearchTab'])
    FM.select_cb_option(locx['NewSearch_DeviceCateCb'], fcfg['category'])
    FM.fill_in_search_expr_simple(0, fcfg['type'], fcfg['op'], fcfg['value'])
    FM.selenium.click_and_wait(locInv['searButton'], 1.25)
    nDevice = FM.selenium.get_text(locInv['searResult'], 5.00)
    if fcfg['totalonly']:
        return {'count': nDevice}
    locx_Tbl = r"//form[@id='searchRequestForm']/div[@id='tableArea']/table"
    locx_Nav = r"//form[@id='searchRequestForm']/div[@id='tableArea']/table//td[@class='pageSelecter']"
    rows = FM.get_list_table(table = locInv['searTbl'], navigator = locInv['searNav'])

    return {'count': nDevice, 'rows': rows}

def is_view_exist(FM, view_name = None, **kwargs):
    fcfg = dict(debug = False,)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    return AVM.is_device_view_exists(FM, view_name)

def find_view_info(FM, view_name = None, **kwargs):
    fcfg = dict(debug = False,)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    return AVM.find_view_info(FM, view_name)

# refer to FlexMaster.save_search()
def make_view(FM, **kwargs):
    rule = dict(
        category = 'Standalone APs',
        type = "Device Name",
        ope = "Starts With",
        value = "APDimark_",
    )
    fcfg = dict(debug = False, name = '', desc = '', rule = rule)
    fcfg.update(kwargs)
    rule = fcfg['rule']
    _halt_process(fcfg['debug'])
    nav_to_my_page(FM)
    s, l, c = FM.selenium, FM.resource['Locators'], FM.resource['Constants']
    NewSearchTab = l['ManageDevice_NewSearchTab']
    NsDeviceCateCb = l['NewSearch_DeviceCateCb']
    s.click_and_wait(NewSearchTab)

    FM.select_cb_option(NsDeviceCateCb, rule['category'])
    #FM.fill_in_search_expr_simple(0, 'Model Name', 'Exactly equals', kwa['model'].upper())
    FM.fill_in_search_expr_simple(0, rule['type'], rule['ope'], rule['value'])
    doResult = FM.save_search(fcfg['name'], fcfg['desc'])
    return doResult
 
def is_view_still_loading(FM, **kwargs):
    # isLoading = r"//div[@id='mainTableSection']//td/img[contains(@src, 'ajax-loader.gif')]"
    isLoadingXloc = r"//div[@id='mainTableSection']//td/img[@id='manageDevicesImgLoad'][contains(@src, 'ajax-loader.gif')]"
    return FM.selenium.is_element_displayed(isLoadingXloc)

#
# set_ALL = IMD.get_view_items(fm, 'scaling: ALL Dimark APs')
# set_01 = IMD.get_view_items(fm, 'scaling: set_01 Dimark APs')
#
def get_view_items(FM, view_name, **kwargs):
    fcfg = dict(debug = False, wait_for = 1200, pause = 60, totalonly = False)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    nav_to_my_page(FM)
    logging.info("[Manage Devices] select [saved.view %s]" % view_name)
    s, l, c = FM.selenium, FM.resource['Locators'], FM.resource['Constants']
    SavedViewsTab = l['ManageDevice_SavedGroupsTab']
    s.click_and_wait(SavedViewsTab)

    xloc = Locators_INVENTORY_MANAGE_DEVICE
    FM.select_cb_option(xloc['viewSelect'], view_name)
    time_start = time.time()
    time_stop = time_start + int(fcfg['wait_for'])
    gotit = False
    logging.info("[Manage Devices] asking server for [saved.view %s]" % view_name)
    while time_stop > time.time():
        if not is_view_still_loading(FM):
            gotit = True
            break
        time.sleep(int(fcfg['pause']))

    time_search = time.time() - time_start
    if not gotit:
        return {'time_total': time_search, 'time_search': 0, 'rows': [],
                'errmsg': ('No items found for view named %s' % view_name)}
 
    nDevice = FM.selenium.get_text(xloc['viewResult'], 5.00)
    if fcfg['totalonly']:
        return {'time_total':time_search, 'time_search': time_search,
                'rows': [], 'count': nDevice}

    logging.info("[Manage Devices] retrieving [saved.view %s]" % view_name)
    x_Tbl = l['SavedGroups_Tbl']
    x_Nav = l['SavedGroups_Nav']
    rows = FM.get_list_table(table = x_Tbl, navigator = x_Nav)
    time_total = time.time() - time_start
    # time_getrows = time_total - time_search
    return {'time_total':time_total, 'time_search': time_search,
            'rows': rows, 'count': nDevice}

###
### Constants
###
M_DEVICE_TYPE = { 1:'Standalone APs',
                  2:'Device Name',
                  3:'Serial Number',
                  4:'IP Address',
                  5:'External IP Address',
                  6:'Model Name',
                  7:'Device Last Seen', # not supported
                  8:'Uptime', # not supported
                  9:'Tag',
                  10:'Auto Configured'}
M_DEVICE_OP = { 1:'Exactly equals',
                2:'Contains',
                3:'Starts with',
                4:'Ends with',
                5:'Greater than',
                6:'Less than'}

#
# Access methods
#
def _m_device_type(val):
    if type(val) is int and M_DEVICE_TYPE.has_key(val):
        return M_DEVICE_TYPE[val]
    return val

def _m_device_op(val):
    if type(val) is int and M_DEVICE_OP.has_key(val):
        return M_DEVICE_OP[val]
    return val


def _halt_process(debug):
    if debug:
        import pdb
        pdb.set_trace()

