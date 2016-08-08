###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE WLANs PAGE.                    #
# NOTE: + THIS MODULE IS TO REPLACE wlan_zd.py and wlan_groups_zd.py           #
#       + CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR Wlan and Wlan Group#
#                                                                             #
#    1. SET: TO CONFIGURE FOR WLAN AND WLAN GROUP                             #
#        - FOR BOTH: Use set function                                         #
#    2. GET: TO GET CONFIGURATION OF WLAN AND WLAN GROUP                      #
#        - FOR BOTH: Use get function                                         #
###############################################################################
import copy

from RuckusAutoTest.components.lib.zd import wlan_zd as zd_lib_wlan, \
    wlan_groups_zd as zd_lib_wlan_group
from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp


Locators = dict(
    create_wlan_link = "//span[contains(@id,'new-wlan')]",
    wlan_name = "//input[contains(@id,'name')]",
    wlan_desc = "//input[@id='description']",
    wlan_type = dict(
        standard = "//input[@id='usage-user']",
        guest_access = "//input[@id='usage-guest']",
        hotspot_service = "//input[@id='usage-wispr']",
    ),
    auth_method = dict(
        open = "//input[@id='auth_open']",
        shared = "//input[@id='auth_shared']",
        eap = "//input[@id='auth_eap']",
        mac_addr = "//input[@id='auth_mac']",
    ),
    encrypt_method = dict(
        none = "//input[@id='enc_none']",
        wpa = "//input[@id='enc_wpa']",
        wpa2 = "//input[@id='enc_wpa2']",
        wep64 = "//input[@id='enc_wep64']",
        wep128 = "//input[@id='enc_wep128']",
    ),
    algorithm = dict(
        tkip = "//input[@id='wpa-cipher-tkip']",
        aes = "//input[@id='wpa-cipher-aes']",
    ),

    # locators for wlan group
    create_new_group_link = Ctrl("//table[@id='wgroup']//span[@id='new-wgroup']", type = 'button'),
    edit_group_link = "", # define later
    clone_group_link = "", # define later

    group_name = Ctrl("//input[@id='wgroup-name']", type = 'text'),
    group_desc = Ctrl("//input[@id='wgroup-description']", type = 'text'),
    enable_vlan_override = Ctrl("//input[@id='has-vlan']", type = 'check'),

    # This key of the input cfg will be a list of wlan member names and its atrributes.
    # This one is a tmpl
    group_member_chk = "//table[@id='wlanTable']//input[contains(following-sibling::label, '%(wlan_name)s')]",
    # group member attribute tmpl
    vlan_attr = dict(
        no_change = "//table[@id='wlanTable']//tr[contains(., '%(wlan_name)s')]//input[contains(@id, 'vo-asis')]",
        untag = "//table[@id='wlanTable']//tr[contains(., '%(wlan_name)s')]//input[contains(@id, 'vo-untag')]",
        tag = "//table[@id='wlanTable']//tr[contains(., '%(wlan_name)s')]//input[contains(@id, 'vo-tag')]",
    ),
    # this one is a tmpl
    tag_id = "//table[@id='wlanTable']//tr[contains(., '%(wlan_name)s')]//input[contains(@id, 'vlan')]",
    ok_btn = "//form[@id='form-wgroup']//input[@id='ok-wgroup']",

    # locators for wlan group table. It is a table without navigator
    wlan_group_tbl = Ctrl(
        loc = "//table[@id='wgroup']",
        type = 'table',
        cfg = dict(
            hdrs = [
                'chk_box', 'group_name', 'group_desc',
            ],
            get = 'all',
        ),
    ),

)

FULL_CFG_KEYS = dict(
    wlan = ['wlan_ssid', 'wlan_description', 'encrypt_method', 'auth', 'wlan_type'],
    wlan_group = ['group_name', 'group_desc', 'enable_vlan_override', 'wlan_members', ]
)
def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

def set(zd, cfg = {}, operation = 'create'):
    '''
    This
    cfg: a dictionary of cfg item. Support following keys:
        {
            # keys for wlan
            'wlan_ssid': 'TestRuckusZD2',
            'wlan_description': 'TestRuckusZD',
            'wlan_type': 'standard',
            'auth': 'open',
            'encrypt_method': None,

            # keys for wlan group
            'group_name': 'Test_Wlan_Group_1',
            'group_desc': 'Test Wlan Group',
            'enable_vlan_override': True,
            'wlan_members': [
                {'wlan_name': 'Ruckus-Wireless-1', 'vlan_attr': 'no_change'},
                {'wlan_name': 'TestRuckusZD', 'vlan_attr': 'tag', 'tag_id': 200},
            ]
        }

    Ideas: Pass a flatten dictionary of cfg items for set then parse it to make
           it become a dictionary with some level. This is to make it back compatiple
           ZD library and AutoConfig later.
    1. Parse to get keys of config items: WLAN and Wlan group,
       Global Configuration with format as below first:
        {
            'wlan': dictionary of items for Access Points.
            'wlan_group': a dictionary of items for Access Point Policies.
        }
    2. Base on each item, invoke exactly wrapper get function for that item
    '''
    _cfg = wr_sp.parse_cfg_for_set(cfg, FULL_CFG_KEYS)
    nav_to(zd)
    for item, sub_cfg in _cfg.iteritems():
        set_fn = {
            'wlan': _set_wlan,
            'wlan_group': _set_wlan_group,
        }[item]
        set_fn(zd, sub_cfg, operation)

WLAN_MAP_KS = {
    'ssid': 'wlan_ssid',
    'description': 'wlan_description',
    'type': 'wlan_type',
    'auth': 'auth',
    'encryption': 'encrypt_method',
}
def _set_wlan(zd, cfg = {}, operation = 'create'):
    '''
    Warning: Don't access this function from outside
    This function is to support create/edit/clone a wlan.
    Note: Currently support "create" only.
    - cfg: a dictionary
        A basic sample for this function
            'wlan_ssid': 'TestRuckusZD2',
            'wlan_description': 'TestRuckusZD',
            'wlan_type': 'standard',
            'auth': 'open',
            'encrypt_method': None,
    '''
    _cfg = wr_sp.convert_fm_zd_cfg(WLAN_MAP_KS, cfg, to_fm = False)
    if operation == 'create':
        zd_lib_wlan.create_wlan(zd, _cfg)


def _build_wlan_group_locators(cfg_list, enable_vlan_override = False):
    '''
    This function is to build locators for wlan members of a group base on input
    values for wlan_members.
    - Return a generator
    '''
    l = Locators
    modified_keys = ['group_member_chk', 'vlan_attr', 'tag_id']
    # these types is according to elements of modified_keys.
    # 'group_member' --> check box, vlan_attr --> radioGroup.
    key_type = ['check', 'radioGroup', 'text']
    loc_str = str(dict(
        group_member_chk = l['group_member_chk'],
        vlan_attr = l['vlan_attr'],
        tag_id = l['tag_id'],
    ))

    for wlan in cfg_list:
        group_member_loc = eval(loc_str % wlan)
        # modify locator of Locators
        for i, k in enumerate(modified_keys):
            group_member_loc[k] = Ctrl(group_member_loc[k], key_type[i])

        # by default select only group_member_chk item of wlan group
        group_member_val = dict(
            group_member_chk = True,
            enable_vlan_override = enable_vlan_override,
        )
        # if vlan override option is enabled, add vlan_attr and tag_id items to group_member_val
        if enable_vlan_override:
            group_member_val.update(dict(vlan_attr = wlan.get('vlan_attr', 'no_change')))
            # if this wlan is tagged, add tag id to group_member_val
            if group_member_val['vlan_attr'] == 'tag':
                group_member_val['tag_id'] = wlan['tag_id']

        yield group_member_loc, group_member_val

create_order_ctrls = ['create_new_group_link', 'group_name', 'group_desc']
edit_order_ctrls = ['edit_group_link', 'group_name', 'group_desc'] # not support edit yet
clone_order_ctrls = ['clone_group_link', 'group_name', 'group_desc'] # not support clone yet

vlan_order_ctrls = ['enable_vlan_override', 'group_member_chk', 'vlan_attr', 'tag_id']

def _set_wlan_group(zd, cfg = {}, operation = 'create'):
    '''
    Warning: Don't access this function from outside
    This function is to support create/edit/clone a wlan group.
    Note: Currently support "create" only.
    - Data structure for input cfg of wlan group
        'operation': create|edit|clone,
        'group_name': name of wlan group
        'group_desc': description for group
        'enable_vlan_override': True/False
        'group_members': a list of wlans which belong to this group. Each elemnet
                        has structure as below
            [
                {'wlan_name': 'name of wlan 1', 'vlan_attr': no_change|untag|tag, 'tag_id': 'tag id if tagged'},
                {'wlan_name': 'name of wlan 2', 'vlan_attr': no_change|untag|tag, 'tag_id': 'tag id if tagged'},
                ..........
            ]
    - A sample of input cfg:
        cfg = {
            'operation': create,
            'group_name': 'Test_Wlan_Group_1',
            'group_desc': 'Test Wlan Group',
            'enable_vlan_override': True,
            'wlan_members': [
                {'wlan_name': 'Ruckus-Wireless-1', 'vlan_attr': 'no_change'},
                {'wlan_name': 'TestRuckusZD', 'vlan_attr': 'tag', 'tag_id': 200},
            ]
        }
    '''
    _cfg = dict(
        operation = 'create'
    )
    _cfg.update(cfg)
    l, s = copy.deepcopy(Locators), zd.selenium
    nav_to(zd)

    # Fill common items: group_name, group_desc first
    # Get common order controls for wlan group
    common_order_ctrls = {
        'create': create_order_ctrls,
        'edit': edit_order_ctrls,
        'clone': clone_order_ctrls,
    }[_cfg['operation']]

    # Common setting
    common_setting = dict(
        group_name = _cfg['group_name'],
        group_desc = _cfg.get('group_desc', ''), # optional element
    )
    ac_set(s, l, common_setting, common_order_ctrls)

    # Fill specific items
    #gen_fn =
    for member_loc, member_val in _build_wlan_group_locators(
                                    _cfg['wlan_members'], _cfg.get('enable_vlan_override', False)
                                  ):
        l.update(member_loc)
        ac_set(s, l, member_val, vlan_order_ctrls)

    s.click_and_wait(l['ok_btn'])
    # zd.logout()

def remove_wlan_group(zd):
    '''
    Currently, still use old functions of zd_wlanGroups so it will remove all wlan
    group by default.
    @TODO: this is a wrapper function. It will be re-written later
    '''
    zd_lib_wlan_group.remove_wlan_groups(zd)

def get(zd, cfg_ks = []):
    '''
    A wrapper function to get wlan and wlan group. It will get list of wlan and
    wlan group only.
    - cfg_ks: + a list of key to get
              + valid keys: 'wlan', 'wlan_group'
    Return:
            Return a dictionary as below.
        dict(
            wlan = [list of wlans],
            wlan_group = [list of wlan groups],
        )
    '''

    _cfg_ks = copy.deepcopy(cfg_ks)
    if not _cfg_ks:
        _cfg_ks = ['wlan', 'wlan_group']

    # nav_to(zd) # currently should not call nav_to here, let zd lib do it
    data = {}
    for item in _cfg_ks:
        sub_ks = []
        get_fn = {
            'wlan': _get_wlan,
            'wlan_group': _get_wlan_group,
        }[item]
        data.update(get_fn(zd, sub_ks))

    # # zd.logout() # currently should not call logout here, let zd lib do it

    return data

def _get_wlan(zd, cfg_ks = []):
    '''
    Warning: Don't access this function from outside
    A wrapper function to get all wlans and their details.
    Input:
    - cfg_ks: place holder only

    NOTE: Currently get all wlans and returnas a dictionary.

    @TODO: Will support to get all wlan, a specific wlan and its detail later.

    Return: a dictionary as below
    {
        'wlan': [list of wlans]
    }

    '''
    # nav_to(zd) # currently should not call nav_to here, let zd lib do it

    return {'wlan': zd_lib_wlan.get_wlan_list(zd)}

def _get_wlan_group(zd, cfg_ks = []):
    '''
    Warning: Don't access this function from outside.
    This function is to get a list of wlan group.
    Input:
    - cfg_ks: place holder only

    @TODO: Will support to get all group or a specific group and its detail later.
    Return: a dictionary as below:
    {
        'wlan_group': [a list of wlan group]
    }
    '''
    s, l = zd.selenium, Locators
    nav_to(zd)
    data = ac_get(s, l, ['wlan_group_tbl'])['wlan_group_tbl']
    # zd.logout()

    return {'wlan_group': data}

if __name__ == '__main__':
    from pprint import pprint
    cfg = {
        'group_name': 'Test_Wlan_Group_1',
        'group_desc': 'Test Wlan Group',
        'enable_vlan_override': True,
        'wlan_members': [
            {'wlan_name': 'Ruckus-Wireless-1', 'vlan_attr': 'no_change'},
            {'wlan_name': 'TestRuckusZD', 'vlan_attr': 'tag', 'tag_id': 200},
        ]
    }
    for loc, val in _build_wlan_group_locators(cfg['wlan_members']):
        print '-' * 80
        #pprint(loc)
        pprint(loc['tag_id'].loc)
        pprint(loc['vlan_attr'].loc)
        pprint(val)
        print '-' * 80

