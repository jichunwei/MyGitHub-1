"""
"""

def fm_work_area():
    return ('Administrator', ['View management'])

Locators_ADMIN_VIEW_MANAGEMENT = dict(
    # [Inventory>>Reports] 'Nav' : "//tr[contains(td, 'Number of devices')]/td/table",
    Tbl = "//div[@id='tableArea']/table",
    Nav = "//tr[contains(td, 'Number of Views')]/td/table",
    # r"//div[@id='tableArea']//td[text()='scaling: ALL Dimark APs']/../td[3]"
    searDeviceViewByName = r"//div[@id='tableArea']//td[text()='%s']/../td[3]",
    searViewByName = r"//div[@id='tableArea']//td[text()='%s']/../td[%d]",
)

import re
import logging
import time

from RuckusAutoTest.components.lib.fm import dashboard_fm_old as DBOD

def nav_to_my_page(FM):
    FM.navigate_to(FM.ADMIN, FM.ADMIN_GROUP_MGMT, 3)

def is_device_view_exists(FM, view_name, **kwargs):
    fcfg = dict(debug = False,)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    nav_to_my_page(FM)
    xloc = Locators_ADMIN_VIEW_MANAGEMENT
    loc_findViewByDevice = xloc['searDeviceViewByName'] % view_name
    found = FM.selenium.is_element_present(loc_findViewByDevice)
    if found:
        view_type = FM.selenium.get_text(loc_findViewByDevice)
        found = True if re.match('device', view_type, re.I) else False
    FM.logout()
    return found

# incorrect implementation
def find_view_info(FM, view_name, **kwargs):
    """
from RuckusAutoTest.components.lib.fm import admin_view_mgmt_fm_old as avm
vinfo = avm.find_view_info(fm, 'scaling: ALL Dimark APs')
pprint(vinfo)
    """
    fcfg = dict(debug = False,)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'])
    nav_to_my_page(FM)
    xloc = Locators_ADMIN_VIEW_MANAGEMENT
    loc_findViewByDevice = xloc['searViewByName'] % (view_name, 1)
    viewInfo = {}
    if FM.selenium.is_element_present(loc_findViewByDevice):
        viewInfo['name'] = FM.selenium.get_text(loc_findViewByDevice)
        for idx, coltype in ((2, 'desc'), (3, 'context')):
            loc_findViewByDevice = xloc['searViewByName'] % (view_name, idx)
            viewInfo[coltype] = FM.selenium.get_text(loc_findViewByDevice)
    FM.logout()
    return {'view': viewInfo}

# Becuase View Management does not have refresh button
# When you come to his function; logout() then login(), or you might get wrong view list
def get_all_views(FM, **kwargs):
    fcfg = dict(debug = False, wantAll = False)
    fcfg.update(kwargs)
    _halt_process(fcfg['debug'] > 1)
    nav_to_my_page(FM)
    xloc = Locators_ADMIN_VIEW_MANAGEMENT
    nav = xloc['Nav']
    tbl = xloc['Tbl']
    # rows = FM.get_list_table(table=tbl, navigator=nav)
    rows = []
    for p, r, i, t in FM.iter_list_table(table = tbl, navigator = nav):
        if fcfg['debug']:
            print r, i, t
        if fcfg['wantAll'] or (r['View Context'] == 'Device' and 'Delete' in r['Actions'].split()):
            rows.append(r)
    # fm_dashboard_old.touch_table_list_as_dict(rows, tableKey='View Name')
    return {'rows': rows, 'count': len(rows)}

def get_all_views_as_dict(FM, **kwargs):
    rows = get_all_views(FM, **kwargs)
    # touch_table_list_as_dict() will concat column name into one word
    return DBOD.touch_table_list_as_dict(rows, tableKey = 'ViewName')

def _halt_process(debug):
    if debug:
        import pdb
        pdb.set_trace()

