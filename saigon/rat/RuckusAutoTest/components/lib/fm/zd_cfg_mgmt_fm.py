##################################################################################
# THIS MODULE IS TO PROVIDE UTILITY FUNCTIONS FOR FM CONFIGURE > ZONEDIRECTORS > #
# MANAGE ZD CONFIGURATIONS                                                       #
##################################################################################
import time
import re
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
     get as ac_get, set as ac_set

OBTAIN_CFG_TBL_HDRS = [
    'device_name', 'serial', 'internal_ip', 'external_ip', 'model', 'last_seen', 'uptime',
    'connection_status', 'tag', 'fw_version',
]

ZD_CFG_TBL_HDRS = [
    'file_name', 'cfg_desc', 'fw_version', 'created_time', 'created_by'
]

OBTAIN_CFG_TH_MAP = {
    'device_name': 'name',
    'serial_#': 'serial',
    'ip_address': 'internal_ip',
    'external_ip': 'ex_ip',
    'model': 'model',
    'last_seen': 'last_seen',
    'uptime': 'uptime',
    'connection': 'conn',
    'tag': 'tag',
    'software': 'firmware',
    'actions': 'action',
}

SUCCESS_MSG = 'The configuration file has been sav'

Locators = dict(
    obtain_zd_cfg = Ctrl(loc = "//div[@id='new-file']//span[contains(., 'New ZoneDirector Configuration')]",
                         type = 'button'),
    cfg_desc = Ctrl(loc = "//input[@id='description']", type = 'text'),
    ok_btn = Ctrl(loc = "//input[@id='cmdSave']", type = 'button'),
    cancel_btn = Ctrl(loc = "//input[@id='cancel-ap']", type = 'button'),
    update_btn = Ctrl(loc = "//input[@id='cmdUpdate']", type = 'button'),
    result_msg = "//a[@id='statusMessageLink']",

    zd_cfg_tbl = Ctrl(
        dict(
             tbl = "//table[@widgetid='configlist']",
             nav = "//td[contains(preceding-sibling::td, 'Number of files')]/table"
        ),
        type = 'ltable',
        cfg = dict(
            hdrs = ZD_CFG_TBL_HDRS,
            links = dict(
                edit = "//a[contains(.,'Edit')]",
                delete = "//a[contains(.,'Delete')]",
            ),
            get = '1st',
        ),
    ),
    obtain_cfg_tbl = Ctrl(
        dict(
             tbl = "//table[@widgetid='ZoneDirectorEntityTable']",
             nav = "//td[contains(preceding-sibling::td, 'Number of devices')]/table"
        ),
        type = 'ltable',
        cfg = dict(
            #hdrs = OBTAIN_CFG_TBL_HDRS,
            hdr_attr = 'id',
            hdr_map = OBTAIN_CFG_TH_MAP,
            links = dict(select = "//input[@type='checkbox']",),
            get = '1st',
        ),
    ),
)

def nav_to(fm, force = True):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_ZD_CONFIGS, force = force)

def obtain_zd_cfg(fm, match_expr = {}, cfg = {}, time_to_save = 12):
    '''
    OBSOLETE: Please obtain_cfg_by_ip instead.

    This function is to obtain a zd cfg. It bases on combination of
    serial/model/internal_ip/external_ip.
    Input:
    - cfg: a dictionary of items to set for this cfg. Current it has only one
           item "cfg_desc". It looks like below dict
           {
               'cfg_desc': 'description for this cfg',
           }
           Note: A dict would be easy to extend this function later if this UI
                 is added more items beside "cfg_desc".
    - match_expr: a dictionary. It is a combination of conditionary to find and get ZD cfg.
        dict(
            serial = 'serial device',
            model = 'zd model',
            internal_ip = 'internal ip',
            external_ip = 'external_ip',

        )
    '''
    s, l = fm.selenium, Locators

    nav_to(fm)
    # find a ZD match "match_expr" and click "select" link to get
    zd_r = ac_get(
        s, l,
        {'obtain_cfg_tbl': dict(get = '1st', matches = [match_expr], op = 'in', link = 'select')},
        ['obtain_zd_cfg', 'obtain_cfg_tbl', ]
    )['obtain_cfg_tbl']

    if not zd_r:
        raise Exception('Cannot find any ZD match condition "%s"' % match_expr)

    # Fill description for this cfg
    ac_set(s, l, cfg, ['cfg_desc', 'ok_btn'])
    # wait for the cfg is saved
    time.sleep(time_to_save)


def obtain_zd_cfg_by_ip(fm, ip, desc, timeout = 12):
    '''
    A simplified version of obtain_zd_cfg
    . ip: internal ip of zd
    . desc: configuration description (consider this as its name).
    '''
    obtain_zd_cfg(fm, {'internal_ip':ip}, {'cfg_desc': desc}, timeout)
    # Note: Not sure _get_result_status is compatible with older FM version
    # so not implement it in obtain_zd_cfg.
    _get_result_status(fm)

def find_zd_cfg(fm, match_expr = {}, op = 'in'):
    '''
    This is to find a zd cfg base on match_expr. match_expr may be a combination
    of several items such as: file_name, cfg_desc, fw_version, created_by.
    Input:
    - match_expr: a dictionary of expression to find a zd cfg. It supports to
                  match following items: file_name, cfg_desc, fw_version, created_by.
    Return:
    - a dictionary of a row matches the "match_expr" or {} if not found.
    '''
    s, l = fm.selenium, Locators

    nav_to(fm)
    # find a ZD match "match_expr" and click "select" link to get
    cfg_r = ac_get(
        s, l,
        {'zd_cfg_tbl': dict(get = '1st', match = match_expr, op = op)}
    )['zd_cfg_tbl']

    return cfg_r

def operate_zd_cfg(fm, match_expr = {}, action = 'edit', new_cfg = {}):
    '''
    This is to support edit/delete the first zd cfg match with "match_expr".
    - match_expr: a dictionary. It is a combination of conditionary to find and get ZD cfg.
        dict(
            serial = 'serial device',
            model = 'zd model',
            internal_ip = 'internal ip',
            external_ip = 'external_ip',
        )
    - action: 'edit'|'delete',
    - new_cfg: just in case edit. It's a dictionary of items to set for this cfg.
               Current it has only one
           item "cfg_desc". It looks like below dict
           {
               'cfg_desc': 'description for this cfg',
           }
           Note: A dict would be easy to extend this function later if this UI
                 is added more items beside "cfg_desc".

    Return: Raise exception if error.
    '''
    s, l = fm.selenium, Locators

    cfg_r = find_zd_cfg(fm, match_expr)
    if not cfg_r:
        raise Exception('Not found any ZD cfg match "%s"' % match_expr)

    # click edit/delete link first
    s.click_and_wait(cfg_r['links'][action.lower()])

    if 'edit' == action.lower():
        # Modify ZD description of this cfg
        ac_set(s, l, new_cfg, ['cfg_desc', 'update_btn'])


def edit_zd_cfg(fm, match_expr = {}, new_cfg = {}):
    '''
    This function is to edit the first zd cfg match with "match_expr". Actually, It simply
    modifies the description.
    - new_cfg: a dictionary of items to set for this cfg. Current it has only one
           item "cfg_desc". It looks like below dict
           {
               'cfg_desc': 'description for this cfg',
           }
           Note: A dict would be easy to extend this function later if this UI
                 is added more items beside "cfg_desc".
    - match_expr: a dictionary. It is a combination of conditionary to find and get ZD cfg.
        dict(
            serial = 'serial device',
            model = 'zd model',
            internal_ip = 'internal ip',
            external_ip = 'external_ip',
        )
    Return: Raise exception if error.
    '''
    operate_zd_cfg(fm, match_expr, 'edit', new_cfg)


def delete_zd_cfg(fm, match_expr = {}):
    '''
    OBSOLETE. Please use the simplified version delete_zd_cfg_by_desc.

    This function is to delete the first zd cfg match with "match_expr".
    - match_expr: a dictionary. It is a combination of conditions to delete a zd.
        {
            'cfg_desc': 'description for this cfg',
            'file_name': '',

        }
    Return: Raise exception if error.
    '''
    operate_zd_cfg(fm, match_expr, 'delete')


def delete_zd_cfg_by_desc(fm, desc):
    '''
    A simplified version of delete_zd_cfg.
    . desc: description of the zd cfg to delete
    '''
    operate_zd_cfg(fm, {'cfg_desc': desc}, 'delete')

#------------------------------------------------------------------------------
def _get_result_status(fm):
    '''
    . return
        None if success
        raise exception if other.
    '''
    s, l = fm.selenium, Locators
    msg = s.get_text(l['result_msg'])
    print msg
    if re.search(SUCCESS_MSG, msg, re.I):
        return None

    raise Exception('Cannot obtain the zd cfg. Error: %s' % msg)
