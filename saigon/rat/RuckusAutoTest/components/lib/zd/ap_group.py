'''
module for create/edit/delete/search ap group feature, 
it bases on Udaipur 9.2

Created on 2011-10-19
@author: cwang@ruckuswireless.com
'''
import logging
import time
import re
import copy

from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.common import lib_List

#-----------------------------------------------------------------------------
# ACCESS SECTION
#-----------------------------------------------------------------------------

def query_ap_group_brief_info_by_name(zd, name, op = 'in'):
    '''
    Query AP Groups brief info from table with given group name
    '''
    _nav_to(zd)
    detail = _query_ap_group_brief_by(zd, dict(name = name), op = op)
#    zd.re_navigate()

    return detail

def get_all_ap_group_brief_info(zd):
    '''
    Get all AP groups brief info from table
    '''
    all_ap_group_cfg = {}    
    ll = _get_all_ap_group_brief_info(zd)
    for apg in ll:        
        all_ap_group_cfg.update({apg['name']: apg})
        
    return all_ap_group_cfg


def get_ap_group_cfg_by_name(zd, name):
    '''
    Get AP Group configuration with given group name.
    '''
    return _get_ap_group_cfg_by_name(zd, name)


def get_ap_group_general_info_by_name(zd, name):
    '''
    Get AP Group general info with given group name.
    '''
    return _get_ap_group_general_info_by_name(zd, name)

def get_port_vlan_by_ap_model(zd, group_name, ap_model):
    '''
    @param zd: ZoneDirector
    @param group_name: ap group name
    @param model: ap model like: zf2942, zf7942cm   
    '''
    _cfg = {}    
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)
    options = zd.s.get_all_options(xloc['select_model_control'])
    for option in options:
        #Updated by Zoe.Huang@2012-06-08
        try:
            match_res = re.match('ZoneFlex (\d{4}[\S]*)', option, re.I)
            if match_res is None:
                match_res = re.match('zf(\d{4}[\S]*)', option, re.I)
        except:
            match_res = re.match('zf(\d{4}[\S]*)', option, re.I)

        model = match_res.group(1)
        model = 'zf' + model.lower()
        if ap_model.lower() == str(model):
            zd.s.select_value(xloc['select_model_control'], ap_model)
            _cfg = _get_port_vlan_setting(zd)
            break

    _cancel_and_close_ap_group_dialog(zd)
    
    return _cfg

def get_all_port_vlans_by_ap_group_name(zd, group_name):
    _dict = {}
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)    
    options = zd.s.get_all_options(xloc['select_model_control'])
    for option in options:             
        model = re.match('(\w{2}\d{4}[\S]*)', option, re.I).group()
        model = model.lower()
        zd.s.select_value(xloc['select_model_control'], model)
        _cfg = _get_port_vlan_setting(zd)            
        _dict[model] = _cfg
    
    _cancel_and_close_ap_group_dialog(zd)    
    
    return _dict


def get_apg_total_number(zd):
    xloc = locators
    _nav_to(zd)
    time.sleep(3)    
    tot_wgs = zd.s.get_text(xloc['get_totals'])
    res = re.match(".*\((\d+)\)", tot_wgs)
    return int(res.group(1))
    

def create_ap_group(zd, name, **kwargs):
    '''
    Create a new AP Group.
    kwargs sample:
        {
            'description':'',
            'gn':{'channelization':None,
                   'channel':None,
                   'power':None,
                   'mode': None,
                   'wlangroups':None, 
                   'ac':None,          
                   },
            'an':{'channelization':None,
                   'channel':None,
                   'power':None,
                   'mode': None,
                   'wlangroups':None,
                   'ac':None,           
                 },
            
            'move_to_member_list':['ac:ff:33:33:44:11',]
            'ip_mode': '*'
        }
    '''        
    _nav_to(zd)    
#    apg_list = _query_ap_group_brief_by(zd, dict(name = name), op = 'xeq')    
#    fnd = False
#    for apg in apg_list:
#        if apg['name'] == name:
#            fnd = True
#            break
#    if fnd:
#        logging.warning('Want to create AP Group %s existed' % name)
#        return set_ap_group_general_by_name(zd, name, **kwargs)
#            
    _open_ap_group_dialog_via_create_btn(zd)    
    description = ""
    if kwargs.has_key("description"):
        description = kwargs['description']
    
     
    _create_ap_group(zd, name, description)
    
    
    if kwargs.has_key('gn'):
        _set_24G_cfg(zd, kwargs['gn'])
    
    if kwargs.has_key('an'):
        _set_5G_cfg(zd, kwargs['an'])
    
    time.sleep(1)
    if kwargs.has_key('move_to_member_list'):
        m_list = kwargs['move_to_member_list']
        for ap_mac in m_list:
            _move_to_member_list(zd, ap_mac)
    
    time.sleep(1)
    
    if kwargs.has_key('ip_mode'):
        xloc = LOCATORS_CFG_AP_GROUP
        if kwargs['ip_mode'] == '*':
            zd.s.click_if_checked(xloc['ip_mode_override_parent'])
        else:
            zd.s.click_if_not_checked(xloc['ip_mode_override_parent'])
            zd.s.type_text(xloc['ip_mode_value'], kwargs['ip_mode'])
        
        time.sleep(1)
    
    _save_and_close_ap_group_dialog(zd)
    logging.info('Create AP Group %s successfully' % name)
    
    zd.re_navigate()


def clone_ap_group(zd, clone_name, new_name):
    '''
        clone_name: Try to clone this AP group.
        new_name: Cloned AP Group.
    '''
    _nav_to(zd)    
    apg_list = query_ap_group_brief_info_by_name(zd, clone_name, op = 'xeq')
    fnd = False
    for apg in apg_list:
        if apg['name'] == clone_name:
            fnd = True
            break
    if fnd:
        logging.info('Want to clone AP Group %s ' % clone_name)
        zd.s.click(locators['clone_by_name'])
        _set_ap_group_name(zd, new_name)
        _save_and_close_ap_group_dialog(zd)
        logging.info('Clone AP Group %s successfully' % clone_name)
    else:
        raise Exception('Does not find AP Group %s' % clone_name)

    zd.re_navigate()

def delete_all_ap_group(zd):
    _nav_to(zd)
    _delete_all_ap_group(zd)
    zd.re_navigate()

def delete_ap_group_by_name(zd, name):
    _nav_to(zd)
    msg =  _delete_ap_group(zd, name)    
    zd.re_navigate()
    return msg


def update_ap_group_name(zd, old_name, new_name):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, old_name)
    _set_ap_group_name(zd, new_name)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def update_ap_group_cfg(zd, name, **kwargs):
    '''
    Update AP Group configurations with given name.
        Example:
        kwargs:
        {
         'description':'ap_group_1',
         'an': {'channel': '36',
               'channelization': '20',
               'mode': 'Auto',
               'power': 'Full',
               'wlangroups': 'rat_wlangroup_999'},
         'bgn': {'channel': '11',
                'channelization': '40',
                'mode': 'N-only',
                'power': '-1dB',
                'wlangroups': 'rat_wlangroup_0'},  
          'move_to_member_list':['00:aa:ff:33:22:11'],
          'move_to_ap_group_name':'System Default',
          'move_to_ap_list':['11:22:44:ee:22:33'], 
         }
    '''
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    if 'description' in kwargs:
        _set_ap_group_general(zd, kwargs.pop('description'))
    
    default_ap_group = True if name == "System Default" else False        
    if kwargs.has_key('bgn'):
        _set_24G_cfg(zd, kwargs['bgn'],default_ap_group = default_ap_group)
    
    if kwargs.has_key('an'):
        _set_5G_cfg(zd, kwargs['an'],default_ap_group = default_ap_group)
    
    if kwargs.has_key('move_to_member_list') and kwargs['move_to_member_list']:
        m_list = kwargs['move_to_member_list']        
        _move_to_member_list(zd, m_list)
    
    
    if kwargs.has_key('move_to_ap_group_name'):
        move_to_ap_group_name = kwargs['move_to_ap_group_name']
        if kwargs.has_key('move_to_ap_list') and kwargs['move_to_ap_list']:
            m_list = kwargs['move_to_ap_list']
            _move_aps_to_ap_group(zd, m_list, move_to_ap_group_name)
          
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def set_ap_group_general_by_name(zd, name, description = None):
    '''
    general_info = {        
        'description': '',        
    }
    '''
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    
    info = _set_ap_group_general(
        zd, description)

    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

    return info

def config_default_ap_group_radio_24g(zd, **kwargs):
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None, 
           'ac':None,          
           }
    cfg.update(kwargs)
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, 'System Default')    
    info = _set_24G_cfg(zd, cfg, default_ap_group=True)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()
    return info


def set_ap_group_radio_24g_by_name(zd, name, **kwargs):
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None, 
           'ac': None,         
           }
    cfg.update(kwargs)
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)  
    default_ap_group = True if name == "System Default" else False 
    info = _set_24G_cfg(zd, cfg, default_ap_group = default_ap_group)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

    return info


def config_default_ap_group_radio_5g(zd, **kwargs):
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None,
           'ac':None,        
           }
    cfg.update(kwargs)
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, 'System Default')    
    info = _set_5G_cfg(zd, cfg, default_ap_group=True)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()
    return info


def set_ap_group_radio_5g_by_name(zd, name, **kwargs):
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None,
           'ac':None,           
           }
    cfg.update(kwargs)
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)   
    default_ap_group = True if name == "System Default" else False 
    info = _set_5G_cfg(zd, cfg, default_ap_group = default_ap_group)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()
    return info


def set_ap_group_radio_by_name(zd, name, bgn=None, an=None):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    default_ap_group = True if name == "System Default" else False
    _set_24G_cfg(zd, bgn, default_ap_group = default_ap_group)    
    _set_5G_cfg(zd, an, default_ap_group = default_ap_group)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()



def set_ap_port_config_by_ap_model(
        zd, group_name, ap_model, port_config
    ):
    '''
    @param zd: ZoneDirector
    @param group_name: AP Group name
    @param ap_model: AP model like "zf2942" 
    @param port_config:      
    {
        'override_system_default': True,
        'lan1': {
            'enabled': True,
            'dhcp82': False,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    xloc = LOCATORS_CFG_AP_GROUP
    
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, group_name)
    
#    options = zd.s.get_all_options(xloc['select_model_control'])
#    fnd = False
#    for option in options:
#        model = re.match('ZoneFlex (\d{4}[\S]*)', option, re.I).group(1)
#        model = 'zf' + model.lower()                
#        if str(model).lower() == ap_model:            
    zd.s.select_value(xloc['select_model_control'], ap_model)
    info = _set_ap_port_config(zd, port_config)
    logging.info('AP Group %s, model %s have updated' % 
                 (group_name, ap_model))
#            fnd = True
#            break
#    if not fnd:
#        raise Exception('Not found model %s' % ap_model)
#    
    _save_and_close_ap_group_dialog(zd)
        
    zd.re_navigate()

    return info

#IP mode in AP group
#*: use parent
#1: ipv4 only
#2: ipv6 only
#3: Dual (default value)
def get_ap_group_ip_mode_by_name(zd, group_name):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    
    if zd.s.is_element_present(xloc['ip_mode_override_parent']) and \
       not zd.s.is_checked(xloc['ip_mode_override_parent']):
        ip_mode = '*'
        zd.s.click_if_not_checked(xloc['ip_mode_override_parent'])
        ip_version = zd.s.get_value(xloc['ip_mode_value'])
        zd.s.click_if_checked(xloc['ip_mode_override_parent'])
    else:
        ip_mode = zd.s.get_value(xloc['ip_mode_value'])
        ip_version = ip_mode
    _cancel_and_close_ap_group_dialog(zd)    

    info = {'ip_mode':ip_mode, 'ip_version':ip_version}
    return info

def set_ap_group_ip_mode_by_name(zd, group_name, ip_mode):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)

    if group_name == 'System Default':
        zd.s.select_value(xloc['ip_mode_value'], ip_mode)
    else:
        if ip_mode == '*':
            zd.s.click_if_checked(xloc['ip_mode_override_parent'])
        else:
            zd.s.click_if_not_checked(xloc['ip_mode_override_parent'])
            zd.s.select_value(xloc['ip_mode_value'], ip_mode)

    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def set_ap_group_radio_band_by_ap_model(zd, group_name, ap_model, radio_band):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  

    zd.s.select_value(xloc['select_model_control'], ap_model)

    if group_name == 'System Default':
        zd.s.select_option(xloc['radio_band_value'], radio_band)
    else:
        zd.s.click_if_not_checked(xloc['radio_band_override_parent'])
        zd.s.select_option(xloc['radio_band_value'], radio_band)

    _save_and_close_ap_group_dialog(zd)
    if zd.s.is_element_present(xloc['ip_mode_override_parent']) and \
       not zd.s.is_checked(xloc['ip_mode_override_parent']):
        ip_mode = '*'
        zd.s.click_if_not_checked(xloc['ip_mode_override_parent'])
        ip_version = zd.s.get_value(xloc['ip_mode_value'])
        zd.s.click_if_checked(xloc['ip_mode_override_parent'])
    else:
        ip_mode = zd.s.get_value(xloc['ip_mode_value'])
        ip_version = ip_mode
    _cancel_and_close_ap_group_dialog(zd)    

    info = {'ip_mode':ip_mode, 'ip_version':ip_version}
        
    zd.re_navigate()

def get_ap_group_radio_band_by_ap_model(zd, group_name, ap_model):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  

    zd.s.select_value(xloc['select_model_control'], ap_model)

    try:
        display = zd.s.is_element_displayed(xloc['radio_band_override_parent'], 3)
    except:
        display = False

    if display:
        if zd.s.is_checked(xloc['radio_band_override_parent']):
            type = 'override' 
            value = zd.s.get_selected_option(xloc['radio_band_value'])
        else:
            type = 'reserve'
            zd.s.click_if_not_checked(xloc['radio_band_override_parent'])
            value = zd.s.get_selected_option(xloc['radio_band_value'])
    else:
        type = ''
        value = zd.s.get_selected_option(xloc['radio_band_value'])

    _cancel_and_close_ap_group_dialog(zd)    

    info = {'type':type, 'value':value}
    return info

def get_ap_group_max_client_by_name(zd, group_name):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    
    max_client = zd.s.get_text(xloc['max_client'])
    _cancel_and_close_ap_group_dialog(zd)    
    return max_client


def set_ap_group_max_client_by_name(zd, group_name, max_client=100):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  

    zd.s.type_text(xloc['max_client'], max_client)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()



def get_ap_model_max_client_by_name(zd, group_name,model):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    zd.s.select_value(xloc['select_model_control'], model)
    max_client = zd.s.get_value(xloc['max_client'])
    _cancel_and_close_ap_group_dialog(zd)  
    return max_client  

def get_multi_ap_model_max_client_by_name(zd, group_name,model_list):
    xloc = LOCATORS_CFG_AP_GROUP
    res = {}
    _nav_to(zd)    
    zd.refresh()
    _open_ap_group_dialog_by_name(zd, group_name)  
    for model in model_list:
        zd.s.select_value(xloc['select_model_control'], model)
        max_client = zd.s.get_value(xloc['max_client'])
        res[model]=max_client
    _cancel_and_close_ap_group_dialog(zd)  
    return res

def set_ap_model_max_client_by_name(zd, group_name,model, max_client):
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    zd.s.select_value(xloc['select_model_control'], model)
    if group_name !='System Default':
        zd.s.click_if_not_checked(xloc['max_client_check_box'])
    zd.s.type_text(xloc['max_client'], max_client)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def remove_all_model_specific_settings(zd, group_name):
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    
    _remove_all_model_specific_settings(zd, group_name)

    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()


def _remove_all_model_specific_settings(zd, group_name):
     
    xloc = LOCATORS_CFG_AP_GROUP
    while zd.s.is_element_present(xloc['remove_model_cfg']) and zd.s.is_visible(xloc['remove_model_cfg']):
        zd.s.click_and_wait(xloc['remove_model_cfg'])




def set_multi_ap_model_max_client_by_name(zd, group_name,number_dict):
    '''
       number_dict={
            'zf7363':'16',
            'zf2942':'100'
            }
    '''
    xloc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)    
    _open_ap_group_dialog_by_name(zd, group_name)  
    for model in number_dict:
        max_client = number_dict[model]
        logging.info('set model %s to max client %s'%(model,max_client))
        try:
            zd.s.select_value(xloc['select_model_control'], model)
            if group_name !='System Default':
                zd.s.click_if_not_checked(xloc['max_client_check_box'])
            zd.s.type_text(xloc['max_client'], max_client)
        except:
            pass
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def move_ap_to_member_list(zd, name, ap_mac):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    _move_to_member_list(zd, ap_mac)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def move_aps_to_ap_group(zd, ap_mac, name='System Default', move_to_group_name=""):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    _move_aps_to_ap_group(zd, ap_mac, move_to_group_name)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()


def check_ap_assign_to_ap_group(zd, ap_mac, name='System Default'):
    ap_group_cfg = get_ap_group_cfg_by_name(zd, name)
    ap_group_members = ap_group_cfg['members_info']
    for ap in ap_group_members:
        if ap['mac']  == ap_mac:
            return True
    
    return False


def set_channelization(zd,ap_group,channelization='20', radio='na'):
    
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)
    
    _set_channelization(zd,ap_group, radio,channelization)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()


def _set_channelization(zd,ap_group, radio='ng',channelization='20'):
    
    if radio=='ng':
        radio = '2.4G'
    else:
        radio = '5G'
    loc = LOCATORS_CFG_AP_GROUP
    check_box=loc['channelization_checkbox']%radio
    select_box = loc['select_channelization']%radio
    
    if zd.s.is_element_present(check_box):
        zd.s.click_if_not_checked(check_box)
    zd.s.select_option(select_box,channelization)
    


def get_selectable_channel_list(zd,ap_group, radio='ng',outdoor=False):
    '''
    '''
    loc = LOCATORS_CFG_AP_GROUP
    if radio=='ng':
        check_box = loc['apg_2_4G_select_channel_checkbox']
        select_box = loc['apg_channel_selection_2_4G']
    elif outdoor:
        check_box = loc['apg_5G_select_channel_checkbox_outdoor']
        select_box = loc['apg_channel_selection_5G_outdoor']
    else:
        check_box = loc['apg_5G_select_channel_checkbox_indoor']
        select_box = loc['apg_channel_selection_5G_indoor']
        
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)
    
    if zd.s.is_element_present(check_box):
        zd.s.click_if_not_checked(check_box)
    channel_list=zd.s.get_select_options(select_box)
    if 'Auto' in channel_list:
        channel_list.remove('Auto')

    _cancel_and_close_ap_group_dialog(zd)
    zd.re_navigate()

    return channel_list


def cfg_5_8G_channel(zd,ap_group,model,override=True,enable=True):
    '''
    '''
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)
    
    _cfg_5_8G_channel(zd,ap_group,model,override,enable)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()


def _cfg_5_8G_channel(zd,ap_group,model,override=True,enable=True):
    '''
    '''
    loc = LOCATORS_CFG_AP_GROUP
    select_box = loc['select_model_control']
    zd.s.select_value(select_box,model)
    if not override and zd.s.is_element_present(loc['apg_5_8G_override_default_checkbox']):
        zd.s.click_if_checked(loc['apg_5_8G_override_default_checkbox'])
    else:
        if zd.s.is_element_present(loc['apg_5_8G_override_default_checkbox']):
            zd.s.click_if_not_checked(loc['apg_5_8G_override_default_checkbox'])
        if enable:
            zd.s.click_if_not_checked(loc['apg_5_8_G_enable_checkbox'])
        else:
            zd.s.click_if_checked(loc['apg_5_8_G_enable_checkbox'])

def enable_all_channel(zd,ap_group,radio='ng',outdoor=False):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)

    _enable_all_channel(zd,ap_group,radio,outdoor)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def _enable_all_channel(zd,ap_group,radio,outdoor):
    loc = LOCATORS_CFG_AP_GROUP
    if radio=='ng':
        channel_checkbox = loc['apg_2_4G_channel_checkbox']
        enable_checkbox = loc['apg_2_4G_channel_setting_enable_checkbox']
    elif outdoor:
        channel_checkbox = loc['apg_5_0G_channel_checkbox_outdoor']
        enable_checkbox = loc['apg_5G_outdoor_channel_setting_enable_checkbox']
    else:
        channel_checkbox = loc['apg_5_0G_channel_checkbox_indoor']
        enable_checkbox = loc['apg_5G_indoor_channel_setting_enable_checkbox']
        
    if zd.s.is_element_present(enable_checkbox):
        zd.s.click_if_not_checked(enable_checkbox)
    channel_idx=1
    while True:
        check_box = channel_checkbox%channel_idx
        if zd.s.is_element_present(check_box) and zd.s.is_visible(check_box):
            zd.s.click_if_not_checked(check_box)   
        else:
            logging.info('the %sth check not found,all channel enabled'%channel_idx)
            break
        channel_idx+=1

def set_channel_range(zd,ap_group,enable=True,radio='ng',outdoor=False,enable_channel_index_list=[]):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)

    _set_channel_range(zd,ap_group,enable,radio,outdoor,enable_channel_index_list)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()

def _set_channel_range(zd,ap_group,enable=True,radio='ng',outdoor=False,enable_channel_index_list=[]):
    loc = LOCATORS_CFG_AP_GROUP
    if radio=='ng':
        channel_checkbox = loc['apg_2_4G_channel_checkbox']
        enable_checkbox = loc['apg_2_4G_channel_setting_enable_checkbox']
    elif outdoor:
        channel_checkbox = loc['apg_5_0G_channel_checkbox_outdoor']
        enable_checkbox = loc['apg_5G_outdoor_channel_setting_enable_checkbox']
    else:
        channel_checkbox = loc['apg_5_0G_channel_checkbox_indoor']
        enable_checkbox = loc['apg_5G_indoor_channel_setting_enable_checkbox']
        
    if not enable:
        zd.s.click_if_checked(enable_checkbox)
    else:
        if zd.s.is_element_present(enable_checkbox):
            zd.s.click_if_not_checked(enable_checkbox)
        channel_idx=1
        while True:
            check_box = channel_checkbox%channel_idx
            if channel_idx in enable_channel_index_list:
                zd.s.click_if_not_checked(check_box)
            elif zd.s.is_element_present(check_box) and zd.s.is_visible(check_box):
                zd.s.click_if_checked(check_box)     
            else:
                break
            channel_idx+=1

def verify_channel_range(zd,ap_group,channel_list,ap_model='',radio='ng',outdoor=False):
    #return True if in ap group configure page has and only has the channels in channel_list,or return False
    logging.info('in ap group to verify the channel range %s'%channel_list)
    
    loc = LOCATORS_CFG_AP_GROUP
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)
    if ap_model:
        zd.s.select_value(loc['select_model_control'], ap_model)
    if radio=='ng':
        channel_lable = loc['apg_2_4G_channel_lable']
        channel_checkbox = loc['apg_2_4G_channel_checkbox']
    elif outdoor:
        channel_lable = loc['apg_5_0G_channel_lable_outdoor']
        channel_checkbox = loc['apg_5_0G_channel_checkbox_outdoor']
    else:
        channel_lable = loc['apg_5_0G_channel_lable_indoor']
        channel_checkbox = loc['apg_5_0G_channel_checkbox_indoor']
    for channel in channel_list:
        lable = channel_lable%channel
        if not zd.s.is_element_present(lable):
            logging.error("channel %s not exist"%channel)
            _cancel_and_close_ap_group_dialog(zd)
            return False
    overflow_channel_index=len(channel_list)+1
    not_exist_checkbox = channel_checkbox%overflow_channel_index
    logging.info('check element %s not present'%not_exist_checkbox)
    if zd.s.is_element_present(not_exist_checkbox) and zd.s.is_visible(not_exist_checkbox):
        logging.error("channel list is longer than expected")
        _cancel_and_close_ap_group_dialog(zd)
        return False
    
    selectable_chanel_list = get_selectable_channel_list(zd,ap_group, radio,outdoor)
    for i in range(0,len(selectable_chanel_list)):
        selectable_chanel_list[i]=str(selectable_chanel_list[i])
    for i in range(0,len(channel_list)):
        channel_list[i]=str(channel_list[i])
    if not lib_List.list_in_list(selectable_chanel_list, channel_list):
        logging.error("selectable channel(%s) not in channel list(%s)"%(selectable_chanel_list, channel_list))
        _cancel_and_close_ap_group_dialog(zd)
        return False
    if not lib_List.list_in_list(channel_list,selectable_chanel_list):
        logging.error("channel list(%s) not in selectable  channel list(%s)"%(channel_list,selectable_chanel_list))
        _cancel_and_close_ap_group_dialog(zd)
        return False
    
    _cancel_and_close_ap_group_dialog(zd)
    zd.re_navigate()
    return True


def enable_all_channel(zd,ap_group):

    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)

    _enable_all_channel(zd,ap_group)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()



def _enable_all_channel(zd,ap_group):
    loc = LOCATORS_CFG_AP_GROUP
    enable_channel_checkbox=[(loc['apg_2_4G_channel_setting_enable_checkbox'],loc['apg_2_4G_channel_checkbox']),
                             (loc['apg_5G_outdoor_channel_setting_enable_checkbox'],loc['apg_5_0G_channel_checkbox_outdoor']),
                             (loc['apg_5G_indoor_channel_setting_enable_checkbox'],loc['apg_5_0G_channel_checkbox_indoor'])]
    
    for (check_enable,check_channel) in enable_channel_checkbox:
        if zd.s.is_element_present(check_enable) and zd.s.is_visible(check_enable):
            zd.s.click_if_not_checked(check_enable)
        idx = 1
        while True:
            check_box = check_channel%idx
            if zd.s.is_element_present(check_box) and zd.s.is_visible(check_box):
                zd.s.click_if_not_checked(check_box)
                idx+=1
            else:
                break




def disable_channel_selection_related_default_override(zd,ap_group):

    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)

    disable_channel_selection_related_default_override(zd,ap_group)
    
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()



def _disable_channel_selection_related_default_override(zd,ap_group): 
    if ap_group== 'System Default':
        logging.info('this function only for none default group')
        return
    loc = LOCATORS_CFG_AP_GROUP
    override_checkbox_list=[loc['apg_2_4G_channel_setting_enable_checkbox'],
                            loc['apg_5G_outdoor_channel_setting_enable_checkbox'],
                            loc['apg_5G_indoor_channel_setting_enable_checkbox'],
                            loc['channelization_checkbox']%'2.4G',
                            loc['channelization_checkbox']%'5G',
                            loc['apg_2_4G_select_channel_checkbox'],
                            loc['apg_5G_select_channel_checkbox_outdoor'],
                            loc['apg_5G_select_channel_checkbox_indoor']] 
    
    for checkbox in override_checkbox_list:
        zd.s.click_if_checked(checkbox)
        

def clear_channel_selection_related_settings(zd,ap_group):
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, ap_group)
    _remove_all_model_specific_settings(zd, ap_group)
    
    if ap_group=='System Default':
        logging.info("default apgroup enable all channels")
        _enable_all_channel(zd,ap_group)
        _set_channelization(zd,ap_group,'ng','Auto')
        _set_channelization(zd,ap_group,'na','Auto')
    else:
        logging.info('not default group,disable default override')
        _disable_channel_selection_related_default_override(zd,ap_group)
    _save_and_close_ap_group_dialog(zd)
    zd.re_navigate()   
    
#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
AP_GROUP_INFO_HDR_MAP = {
    'name': 'name',
    'description': 'description',
    'member-num': 'member-num',
}
locators = dict(apg_tbl_loc = "//table[@id='apgroup']",
                apg_tbl_nav_loc = "//table[@id='apgroup']/tfoot",
                apg_tbl_filter_txt = "//table[@id='apgroup']/tfoot//input[@type='text']",
                apg_tbl_chk_all = "//input[@id='apgroup-sall']",
                check_name_default = r"//table[@id='apgroup']//tr/td[text()='System Default']/../td/input[@name='apgroup-select']",
                apg_tbl_chk = "//input[@name='apgroup-select']",                
                edit_by_name = r"//span[text()='Edit']",
                clone_by_name = r"//span[text()='Clone']",
                apg_detail_dialog_create_btn = "//span[contains(@id, 'new-apgroup')]",
                apg_delete_btn = r"//input[@id='del-apgroup']",
                apg_show_more_btn = r"//input[@id='showmore-apgroup']",
                apg_next_img = r"//img[@id='next-apgroup']",
                get_totals = r"//table[@id='apgroup']//div[@class='actions']/span"               
                )

LOCATORS_CFG_AP_GROUP = dict(
                             edit_name = r"//input[@id='apg-name']",
                             edit_description = r"//input[@id='apg-description']",                             
                             r_bgn = dict(
                                          check_channelization=r"//input[@id='parentconf-apg-channelization-2.4G']",
                                          select_chanelization = r"//select[@id='apg-channelization-2.4G']",
                                          check_channel=r"//input[@id='parentconf-apg-channel-2.4G']",
                                          select_chanel = r"//select[@id='apg-channel-2.4G']",
                                          check_tx_power = r"//input[@id='parentconf-apg-power-2.4G']",
                                          select_tx_power = r"//select[@id='apg-power-2.4G']",
                                          check_mode = r"//input[@id='parentconf-apg-mode-2.4G']",
                                          select_mode = r"//select[@id='apg-mode-2.4G']",
                                          check_wg = r"//input[@id='parentconf-apg-wg-2.4G']",
                                          select_wg = r"//select[@id='apg-wg-2.4G']",
                                          select_auto_channel = r"//select[@id='apg-chanset-2.4G']",
                                          check_ac = r"//input[@id='parentconf-apg-ac-2.4G']",
                                          select_ac = r"//select[@id='apg-ac-2.4G']",
                                          ),
                             r_an = dict(
                                         check_channelization=r"//input[@id='parentconf-apg-channelization-5G']",
                                         select_chanelization = r"//select[@id='apg-channelization-5G']",
                                         check_channel=r"//input[@id='parentconf-apg-channel-5G']",
                                         select_chanel = r"//select[@id='apg-channel-5G']",
                                         check_tx_power = r"//input[@id='parentconf-apg-power-5G']",
                                         select_tx_power = r"//select[@id='apg-power-5G']",
                                         check_mode = r"//input[@id='parentconf-apg-mode-5G']",
                                         select_mode = r"//select[@id='apg-mode-5G']",
                                         check_wg = r"//input[@id='parentconf-apg-wg-5G']",
                                         select_wg = r"//select[@id='apg-wg-5G']",  
                                         check_ac = r"//input[@id='parentconf-apg-ac-5G']",
                                         select_ac = r"//select[@id='apg-ac-5G']",                                   
                                         ),
                                         
                            select_model_control = r"//select[@id='apg-models']",
                            button_discard_setting = r"//select[@id='apg-model-remove']",
                            #check_status_led = r"//input[@id='parentconf-apg-do-ledoff']",
                            #check_status_led_disable = r"input[@id='apg-do-ledoff']",
                            check_port_setting = r"//input[@id='parentconf-apg-port-setting']",
                                                        
#                            combo_dot1xport = r"//select[@id='ps-dot1xapg-port-setting%s']",                            
                            
                            table_port_setting = dict(check_enable=r"//input[@id='ps-enableapg-port-setting%s']",
                                                      check_dhcp82=r"//input[@id='opt82-enableapg-port-setting%s']",
                                                      select_type = r"//select[@id='ps-uplinkapg-port-setting%s']",
                                                      untag_id = r"//input[@id='ps-untagapg-port-setting%s']",
                                                      members = r"//input[@id='ps-membersapg-port-setting%s']",
                                                      guest_vlan = r"//input[@id='ps-guestapg-port-setting%s']",
                                                      check_dvlan = r"//input[@id='dvlan-enableapg-port-setting%s']",
                                                      select_encrytion_type = r"//select[@id='ps-dot1xapg-port-setting%s']",
                                                      combo_dot1x_auth_svr = r"//select[@id='ps-authsvrapg-port-setting']",
                                                      combo_dot1x_acct_svr = r"//select[@id='ps-acctsvrapg-port-setting']",  
                                                      check_dot1x_mac_bypass = r"//input[@id='ps-mac-authapg-port-setting']",
                                                        
                                                      radio_dot1x_supp_mac = r"//input[@id='ps-supp-macapg-port-setting']",
                                                      radio_dot1x_supp_auth = r"//input[@id='ps-supp-manualapg-port-setting']",
                                                      text_dot1x_supp_username = r"//input[@id='ps-supp-userapg-port-setting']",
                                                      text_dot1x_supp_password = r"//input[@id='ps-supp-pwdapg-port-setting']",
                                                      ),                                                   
                            button_add_more = r"//input[@id='do-addaps']",
                            aps_table = dict(
                                            tbl_filter_txt = r"//table[@id='addaps']/tfoot//input[@type='text']",
                                            button_add_ap = r"//input[@id='custom-addaps']",
                                            check_add_all_ap = r"//input[@id='addaps-sall']",
                                            tbl_nav_loc = "//table[@id='addaps']/tfoot",
                                            tbl_loc = "//table[@id='addaps']",
                                            ),
                            memebers_table = dict(
                                                  tbl_filter_txt = r"//table[@id='apgView']/tfoot//input[@type='text']",
                                                  select_move_to = r"//select[@id='apg-move-to']",
                                                  button_move_to = r"//input[@id='custom-apgView']",
                                                  check_all_ap = r"//input[@id='apgView-sall']",
                                                  tbl_nav_loc = "//table[@id='apgView']/tfoot",
                                                  tbl_loc = "//table[@id='apgView']",                                                                                                    
                                                  ),
                            ip_mode_override_parent = r"//input[@id='parentconf-apg-ipmode']",
                            ip_mode_value = r"//select[@id='apg-ipmode']",
                            radio_band_override_parent = r"//input[@id='parentconf-apg-do-workingradio']",
                            radio_band_value = r"//select[@id='apg-do-workingradio']",
                            max_client = r"//input[@id='apg-max-client']",
                            max_client_check_box = r"//input[@id='parentconf-apg-max-client']",
                            remove_model_cfg=r"//input[@id='apg-model-remove']",
                            edit_OK = r"//input[@id='ok-apgroup']",
                            edit_Cancel = r"//input[@id='cancel-apgroup']",
                            
                            apg_2_4G_channel_lable = r"//span[@id='apg-chl-2.4G']//label[text()='%s']",#%'1'
                            apg_5_0G_channel_lable_indoor = r"//span[@id='apg-chl-indoor-5G']//label[text()='%s']",#%'36'
                            apg_5_0G_channel_lable_outdoor = r"//span[@id='apg-chl-outdoor-5G']//label[text()='%s']",#%'149'
                            
                            apg_2_4G_channel_checkbox = r"//span[@id='apg-chl-2.4G']//input[@id='apg-chl-2.4G-%s']",#%1,2,3,4,5,6.....
                            apg_5_0G_channel_checkbox_indoor = r"//input[@id='apg-chl-indoor-5G-%s']",#%1,2,3,4,5,6.....
                            apg_5_0G_channel_checkbox_outdoor = r"//input[@id='apg-chl-outdoor-5G-%s']",#%1,2,3,4,5,6..
                            
                            apg_2_4G_channel_setting_enable_checkbox = r"//input[@id='parentconf-apg-chl-2.4G']",
                            apg_5G_indoor_channel_setting_enable_checkbox = r"//input[@id='parentconf-apg-chl-indoor-5G']",
                            apg_5G_outdoor_channel_setting_enable_checkbox = r"//input[@id='parentconf-apg-chl-outdoor-5G']",
                            
                            channelization_checkbox = r"//input[@id='parentconf-apg-channelization-%s']",#%2.4G,5G
                            select_channelization = r"//select[@id='apg-channelization-%s']",#%2.4G,5G
                            
                            apg_2_4G_select_channel_checkbox = r"//input[@id='parentconf-apg-channel-2.4G']",
                            apg_5G_select_channel_checkbox_indoor = r"//input[@id='parentconf-apg-channel-5G']",
                            apg_5G_select_channel_checkbox_outdoor = r"//input[@id='parentconf-apg-channel-outdoor-5G']",
                            apg_channel_selection_2_4G=r"//select[@id='apg-channel-2.4G']",
                            apg_channel_selection_5G_indoor=r"//select[@id='apg-channel-5G']",
                            apg_channel_selection_5G_outdoor=r"//select[@id='apg-channel-outdoor-5G']",
                            
                            
                            apg_5_8G_override_default_checkbox = r"//input[@id='parentconf-apg-do-cbandchann']",
                            apg_5_8_G_enable_checkbox = r"//input[@id='apg-do-cbandchann']",
                            )

def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)


def _get_all_ap_group_brief_info(zd):
    '''
    
    '''
    _nav_to(zd)
    ap_group_info_list = wgt.get_tbl_rows(
                       zd.s, locators['apg_tbl_loc'],
                       locators['apg_tbl_nav_loc']
                   )

    return ap_group_info_list



def _get_ap_group_brief_by(zd, match, verbose = False, op = 'in'):
    '''
    '''
    _nav_to(zd)
    ap_group_info = wgt.get_first_row_by(
        zd.s, locators['apg_tbl_loc'],
        locators['apg_tbl_nav_loc'], match,
        filter = locators['apg_tbl_filter_txt'],
        verbose = verbose,
        op = op
    )

    return ap_group_info



def _get_ap_group_cfg_by_name(zd, name):
    '''
    '''
    _nav_to(zd)        
    _open_ap_group_dialog_by_name(zd, name)    
    ginfo = _get_ap_group_general_info(zd, name)
    r_bgn = _get_24G_cfg(zd)
    r_an = _get_5G_cfg(zd)
    members = _get_memeber_list(zd)
    aps = []
    if name != 'System Default':    
        aps = _get_ap_list(zd)
    
    _cancel_and_close_ap_group_dialog(zd)
#    zd.re_navigate()
    
    ap_group_config = {'general_info': ginfo,
                       'radio_gn':r_bgn,
                       'radio_an':r_an,
                       'members_info': members,
                       'aps_info': aps,
                       }        
    
    
    return ap_group_config



def _get_24G_cfg(zd):    
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None, 
           'ac':None,          
           }    
    loc = LOCATORS_CFG_AP_GROUP['r_bgn']
    if zd.s.is_element_present(loc['check_channelization']):
        if zd.s.is_checked(loc['check_channelization']):
            cfg['channelization'] = zd.s.get_selected_option(loc['select_chanelization'])
        
        if zd.s.is_checked(loc['check_channel']):
            cfg['channel'] = zd.s.get_selected_option(loc['select_chanel'])
        
        if zd.s.is_checked(loc['check_tx_power']):
            cfg['power'] = zd.s.get_selected_option(loc['select_tx_power'])
                
        if zd.s.is_checked(loc['check_mode']):
            cfg['mode'] = zd.s.get_selected_option(loc['select_mode'])
        
        if zd.s.is_checked(loc['check_wg']):
            cfg['wlangroups'] = zd.s.get_selected_option(loc['select_wg'])
        
        if zd.s.is_checked(loc['check_ac']):
            cfg['ac'] = zd.s.get_selected_option(loc['select_ac'])
    else:
        cfg['channelization'] = zd.s.get_selected_option(loc['select_chanelization'])
        cfg['channel'] = zd.s.get_selected_option(loc['select_chanel'])
        cfg['power'] = zd.s.get_selected_option(loc['select_tx_power'])
        cfg['mode'] = zd.s.get_selected_option(loc['select_mode'])
        cfg['wlangroups'] = zd.s.get_selected_option(loc['select_wg'])
        cfg['ac'] = zd.s.get_selected_option(loc['select_ac'])
            
    return cfg
    

def _set_24G_cfg(zd, cfg, default_ap_group = False):
    _cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None,   
           'ac':None,        
           }
    _cfg.update(**cfg) 
                    
    loc = LOCATORS_CFG_AP_GROUP['r_bgn']
    if _cfg['channelization']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_channelization'])
            
        zd.s.select_option(loc['select_chanelization'], _cfg['channelization'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_channelization'])
    
    if _cfg['channel']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_channel'])
        zd.s.select_option(loc['select_chanel'], _cfg['channel'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_channel'])
        
    if _cfg['power']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_tx_power'])
        zd.s.select_option(loc['select_tx_power'], _cfg['power'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_tx_power'])
    
    if _cfg['mode']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_mode'])
        
        #@author: anzuo, @change: adapt different ZD release for APGRP mode(N/AC-only or N-only)
        mode_list = zd.s.get_select_options(loc['select_mode'])
        if mode_list and _cfg['mode'] not in mode_list:
            pattern = "N.+only"
            for mode in mode_list:
                if re.match(pattern, _cfg['mode']) and re.match(pattern, mode):
                    _cfg['mode'] = mode
                    break
            
        zd.s.select_option(loc['select_mode'], _cfg['mode'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_mode'])
    
    if _cfg['wlangroups']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_wg'])
        zd.s.select_option(loc['select_wg'], _cfg['wlangroups'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_wg'])
        
    if _cfg['ac'] or _cfg['ac'] == 0:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_ac'])
        zd.s.select_value(loc['select_ac'], _cfg.get('ac', 0))
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_ac'])
    
    

def _get_5G_cfg(zd):
    cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None,   
           'ac':None,        
           }
    loc = LOCATORS_CFG_AP_GROUP['r_an']    
    if zd.s.is_element_present(loc['check_channelization']):
        if zd.s.is_checked(loc['check_channelization']):
            cfg['channelization'] = zd.s.get_selected_option(loc['select_chanelization'])
        
        if zd.s.is_checked(loc['check_channel']):
            cfg['channel'] = zd.s.get_selected_option(loc['select_chanel'])
        
        if zd.s.is_checked(loc['check_tx_power']):
            cfg['power'] = zd.s.get_selected_option(loc['select_tx_power'])
                
        if zd.s.is_checked(loc['check_mode']):
            cfg['mode'] = zd.s.get_selected_option(loc['select_mode'])
        
        if zd.s.is_checked(loc['check_wg']):
            cfg['wlangroups'] = zd.s.get_selected_option(loc['select_wg'])
        
        if zd.s.is_checked(loc['check_ac']):
            cfg['ac'] = zd.s.get_selected_option(loc['select_ac'])
    else:
        cfg['channelization'] = zd.s.get_selected_option(loc['select_chanelization'])
        cfg['channel'] = zd.s.get_selected_option(loc['select_chanel'])
        cfg['power'] = zd.s.get_selected_option(loc['select_tx_power'])
        cfg['mode'] = zd.s.get_selected_option(loc['select_mode'])
        cfg['wlangroups'] = zd.s.get_selected_option(loc['select_wg'])
        cfg['ac'] = zd.s.get_selected_option(loc['select_ac'])
    
    return cfg

def _set_5G_cfg(zd, cfg, default_ap_group = False):
    _cfg = {'channelization':None,
           'channel':None,
           'power':None,
           'mode': None,
           'wlangroups':None,  
           'ac':None,         
           }
    _cfg.update(**cfg)
    loc = LOCATORS_CFG_AP_GROUP['r_an']
    if _cfg['channelization']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_channelization'])
        zd.s.select_option(loc['select_chanelization'], _cfg['channelization'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_channelization'])
    
    
    if _cfg['channel']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_channel'])
        zd.s.select_option(loc['select_chanel'], _cfg['channel'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_channel'])
    
    if _cfg['power']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_tx_power'])
        zd.s.select_option(loc['select_tx_power'], _cfg['power'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_tx_power'])
    
    if _cfg['mode']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_mode'])
        zd.s.select_option(loc['select_mode'], _cfg['mode'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_mode'])
    
    if _cfg['wlangroups']:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_wg'])
        zd.s.select_option(loc['select_wg'], _cfg['wlangroups'])
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_wg'])
        
    if _cfg['ac'] or _cfg['ac'] == 0:
        if not default_ap_group:
            zd.s.click_if_not_checked(loc['check_ac'])
        zd.s.select_value(loc['select_ac'], _cfg.get('ac', 0))
    else:
        if not default_ap_group:
            zd.s.click_if_checked(loc['check_ac'])
        

def _get_port_vlan_setting(zd):
    _cfg =  {
        'override_system_default': True,
        'lan1': {
            'enabled': True,
            'dchp82':False,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    xloc = LOCATORS_CFG_AP_GROUP
    override_system_default = False    
    
    override_system_default = zd.s.is_checked(xloc['check_port_setting'])
    
    if not override_system_default:
        zd.s.click_if_not_checked(xloc['check_port_setting'])
        
    _cfg['override_system_default'] =  override_system_default
    dcfg = _get_port_vlan_detail(zd)
    _cfg.update(**dcfg)
    return _cfg


def _get_port_vlan_detail(zd):
    '''    
    '''
    xloc = LOCATORS_CFG_AP_GROUP['table_port_setting']
    port_config = {}
    idx = 1
    while True:
        loc = xloc['check_enable'] % idx
        if not zd.s.is_element_present(loc, .2):
            break

        settings = {}
        settings['enabled'] = zd.s.is_checked(loc)

        loc = xloc['check_dhcp82'] % idx
        settings['dhcp82'] = zd.s.is_checked(loc)

        loc = xloc['select_type'] % idx
        settings['type'] = zd.s.get_selected_value(loc)
        
        loc = xloc['untag_id'] % idx
        settings['untagged_vlan'] = zd.s.get_value(loc)
        
        settings['vlan_members'] = ''
        loc = xloc['members'] % idx
        if not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):
            settings['vlan_members'] = zd.s.get_value(loc)
        else:
            if settings['type'] == 'trunk':
                settings['vlan_members'] = '1-4094'
            elif settings['type'] == 'access':
                settings['vlan_members'] = settings['untagged_vlan']   

        loc = xloc['select_encrytion_type'] % idx
        if zd.s.is_element_present(loc, .2):
            settings['dot1x'] = zd.s.get_selected_value(loc)
        
            if "disabled" != settings['dot1x']:
                if settings['dot1x'] in ['auth-port', 'auth-mac']:
                    loc = xloc['combo_dot1x_auth_svr']
                    settings['dot1x_auth_svr'] = zd.s.get_selected_option(loc)
                    
                    loc = xloc['combo_dot1x_acct_svr']
                    settings['dot1x_acct_svr'] = zd.s.get_selected_option(loc)
                    
                    loc = xloc['check_dot1x_mac_bypass']                    
                    settings['dot1x_mac_bypass_enabled'] = zd.s.is_checked(loc)
                    
                    #Guest VLAN, Xian-9.5 Feature.                                        
                    if settings.get('type') == 'access' \
                        and settings.get('dot1x') == 'auth-mac':
                        loc = xloc['check_dvlan'] % idx                       
                        settings['dot1x_dvlan_enabled'] = zd.s.is_checked(loc)                                                                               
                        loc = xloc['guest_vlan'] % idx
                        settings['dot1x_guest_vlan'] = zd.s.get_value(loc)                                        
                    
                elif settings['dot1x'] == 'supp':
                        loc = xloc['radio_dot1x_supp_mac']
                        settings['dot1x_supp_mac_enabled'] = zd.s.is_checked(loc)                            
                                                                            
                        loc = xloc['radio_dot1x_supp_auth']
                        if zd.s.is_checked(loc):
                            settings['dot1x_supp_auth_enabled'] = True
                            settings['dot1x_supp_username'] = zd.s.get_value(xloc['text_dot1x_supp_username'])
                            settings['dot1x_supp_password'] = zd.s.get_value(xloc['text_dot1x_supp_password'])
                        else:
                            settings['dot1x_supp_auth_enabled'] = False                                
                    


        port_config.update({'lan%s' % idx: settings})

        idx += 1 #moves on to the next lan port available

    return port_config


def _set_ap_port_config(zd, port_config):
    '''
    port_config = {
        'override_system_default': True,
        'lan1': {
            'enabled': True,
            'dhcp82': False,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    xloc = LOCATORS_CFG_AP_GROUP['table_port_setting']

    override_system_default = port_config['override_system_default']
    system_default_conf_loc = LOCATORS_CFG_AP_GROUP['check_port_setting']

    if zd.s.is_element_present(system_default_conf_loc, .2):
        if override_system_default:
            zd.s.click_if_not_checked(system_default_conf_loc)
        else:
            zd.s.click_if_checked(system_default_conf_loc)

    if zd.s.is_checked(system_default_conf_loc):
        for port, settings in port_config.iteritems():
            if not settings or type(settings) is not dict:
                continue
            # now the lan port and its config are provided
            _set_ap_port_config_detail(zd, port, settings)


def _set_ap_port_config_detail(zd, port, settings):
    '''
    port = 'lan1'
    settings = {
        'enabled': True,
        'dhcp82': True,
        'type': 'trunk',              #[trunk, access, general]
        'untagged_vlan': '1',         #[1-4094, none] (expected String type)
        'vlan_members': '50,10-20',   #[1-4094] (expected String type)
        'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        'enable_dvlan':None,
        'guest_vlan':'10',
        'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
        'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
        'dot1x_mac_bypass_enabled': False, #optional param.
        
        'dot1x_supp_mac_enabled':False, #optional param.
        'dot1x_supp_auth_enabled':True, #optional param.
        'dot1x_supp_username':'ras.local.user',
        'dot1x_supp_password': 'ras.local.user',
    }    
    '''

    xloc = LOCATORS_CFG_AP_GROUP['table_port_setting']

    pid = port[-1]

    try:
        loc = xloc['check_enable'] % pid
    except KeyError:
        logging.info("The given port '%s' is not available.")
        return

    if settings['enabled']:
        zd.s.click_if_not_checked(loc)

    else:
        zd.s.click_if_checked(loc)
        #upon unchecked, its settings are not enabled to edit
        return

    loc = xloc['check_dhcp82'] % pid
    if settings['dhcp82']:
        zd.s.click_if_not_checked(loc)
    else:
        zd.s.click_if_checked(loc)        
        
    loc = xloc['select_type'] % pid
    if settings.get('type'):
        zd.s.select_value(loc, settings['type'])

    loc = xloc['untag_id'] % pid
    if settings.get('untagged_vlan'):
        zd.s.type_text(loc, settings['untagged_vlan'])
    
    
    loc = xloc['members'] % pid
    if settings.get('vlan_members'):
        if not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):            
            zd.s.type(loc, settings['vlan_members'])    

    loc = xloc['select_encrytion_type'] % pid
    if settings.get('dot1x'):
        # dot1x is not available with mesh enabled system
        if zd.s.is_element_present(loc, .2):
            zd.s.select_value(loc, settings['dot1x'])
            
  
    if settings['dot1x'] in ['auth-port', 'auth-mac']:        
        loc = xloc['combo_dot1x_auth_svr']
        if settings.get('dot1x_auth_svr'):            
            zd.s.select_option(loc, settings['dot1x_auth_svr'])
        
        loc = xloc['combo_dot1x_acct_svr']            
        if 'dot1x_acct_svr' in settings.keys() and settings['dot1x_acct_svr']:
            zd.s.select_option(loc, settings['dot1x_acct_svr'])
        
        loc = xloc['check_dot1x_mac_bypass']            
        if 'dot1x_mac_bypass_enabled' in settings.keys():
            if settings['dot1x_mac_bypass_enabled']:
                zd.s.click_if_not_checked(loc)
            else:
                zd.s.click_if_checked(loc)
        
        #Guest VLAN, Xian-9.5 Feature.                                        
        if settings.get('type') == 'access' and \
            settings.get('dot1x') == 'auth-mac':
            
            loc = xloc['check_dvlan'] % pid
            if settings.get('enable_dvlan'):
                enable = settings.get('enable_dvlan')
                if enable == True:
                    zd.s.click_if_not_checked(loc)
                    if settings.get('guest_vlan'):
                        loc = xloc['guest_vlan'] % pid
                        zd.s.type_text(loc, settings.get('guest_vlan'))
                    
                elif enable == False:
                    zd.s.click_if_checked(loc)
    
    elif settings['dot1x'] == 'supp':
            if settings['dot1x_supp_mac_enabled']:
                loc = xloc['radio_dot1x_supp_mac']
                zd.s.click_if_not_checked(loc)
                
            elif settings['dot1x_supp_auth_enabled']:
                loc = xloc['radio_dot1x_supp_auth']
                zd.s.click_if_not_checked(loc)
                
                loc = xloc['text_dot1x_supp_username']
                zd.s.type_text(loc, settings['dot1x_supp_username'])
                
                loc = xloc['text_dot1x_supp_password']
                zd.s.type_text(loc, settings['dot1x_supp_password'])
               
            
def _get_memeber_list(zd):
    xloc = LOCATORS_CFG_AP_GROUP['memebers_table']
    members_list = []    
    if zd.s.is_element_present(xloc['tbl_loc'], .5) and \
    zd.s.is_visible(xloc['tbl_loc']):                            
        members_list = wgt.get_tbl_rows(
                       zd.s, xloc['tbl_loc'],
                       xloc['tbl_nav_loc']
                   )
    return members_list


def _move_to_member_list(zd, ap_mac):
    '''
    Move AP to group member list from AP list.
    '''
    ap_list = []
    if type(ap_mac) is str:
        ap_list.append(ap_mac)
    elif type(ap_mac) is list:
        ap_list = ap_mac
    else:
        raise Exception('Unkown type %s, support types[str, list]' % type(ap_mac))
    
    
    xloc = LOCATORS_CFG_AP_GROUP['aps_table']
    add_loc = LOCATORS_CFG_AP_GROUP['button_add_more']
    if zd.s.is_element_present(add_loc, .5) and \
    zd.s.is_visible(add_loc):
        zd.s.click_and_wait(add_loc)
    for ap_mac in ap_list:        
        row = wgt.get_first_row_by(zd.s, 
                         xloc['tbl_loc'], 
                         xloc['tbl_nav_loc'], 
                         dict(mac=ap_mac), 
                         xloc['tbl_filter_txt'],
                         op = 'xeq'
                         )
        time.sleep(2)
        
#        wgt._fill_search_txt(zd.s, xloc['tbl_filter_txt'], ap_mac)
#        time.sleep(1)
        if row:
            zd.s.click_if_not_checked(xloc['check_add_all_ap'])
            zd.s.click_and_wait(xloc['button_add_ap'])
            logging.info('move ap %s to member list successfully' % ap_mac)
        
#        wgt._clear_search_txt(zd.s, xloc['tbl_loc'])
        

def _move_aps_to_ap_group(zd, ap_mac, ap_group = 'System Default'):
    '''
    Move AP to AP list from group member list. 
    '''
    xloc = LOCATORS_CFG_AP_GROUP['memebers_table']
    ap_list = []
    if type(ap_mac) is str:
        ap_list.append(ap_mac)
    elif type(ap_mac) is list:
        ap_list = ap_mac
    else:
        raise Exeption('Unkown type %s, support types[str, list]' % type(ap_mac))
    
    for ap_mac in ap_list:    
        wgt._fill_search_txt(zd.s, xloc['tbl_filter_txt'], ap_mac)
        time.sleep(1)

        row = wgt.get_first_row_by(zd.s, 
                         xloc['tbl_loc'], 
                         xloc['tbl_nav_loc'], 
                         dict(mac=ap_mac), 
                         xloc['tbl_filter_txt'])
        
        if row:
            zd.s.click_if_not_checked(xloc['check_all_ap'])  
            zd.s.select_option(xloc['select_move_to'], ap_group)      
            zd.s.click_and_wait(xloc['button_move_to'])
            logging.info('move ap %s to AP list successfully' % ap_mac)
            
#        wgt._clear_search_txt(zd.s, xloc['tbl_loc'])        

def _get_ap_list(zd):
    xloc = LOCATORS_CFG_AP_GROUP['aps_table']
    aps_list = []    
    add_loc = LOCATORS_CFG_AP_GROUP['button_add_more']
    if zd.s.is_element_present(add_loc, .5) and \
            zd.s.is_visible(add_loc) and \
            not zd.s.is_element_disabled(add_loc):
        zd.s.click_and_wait(add_loc)    
    
    aps_list = wgt.get_tbl_rows(
                       zd.s, xloc['tbl_loc'],
                       xloc['tbl_nav_loc']
                   )
    
    return aps_list


def _get_ap_group_general_info_by_name(zd, name):    
    _nav_to(zd)
    _open_ap_group_dialog_by_name(zd, name)
    info = _get_ap_group_general_info(zd, name)
    _cancel_and_close_ap_group_dialog(zd)
    zd.re_navigate()
    
    return info


def _set_ap_group_general(zd, description = None):
    xloc = LOCATORS_CFG_AP_GROUP    
    items = ((description, xloc['edit_description']),
             )   
    for item in items:
        if item[0] is not None:
            zd.s.type_text(item[1], item[0])


def _set_ap_group_name(zd, name):
    xloc = LOCATORS_CFG_AP_GROUP    
    items = ((name, xloc['edit_name']),
             )   
    
    for item in items:
        if item[0] is not None:
            if not zd.s.is_editable(item[1]):
                raise Exception("Element %s can not edit" % item[1])
            zd.s.type_text(item[1], item[0])


def _query_ap_group_brief_by(zd, match, verbose=False, op = 'in'):
    '''
    return
    . a list of dict
    '''    
    ap_group_info_list = wgt.get_tbl_rows_by(
        zd.s, locators['apg_tbl_loc'],
        locators['apg_tbl_nav_loc'], match,
        filter = locators['apg_tbl_filter_txt'],
        verbose = verbose,
        op = op
    )

    return ap_group_info_list

def _create_ap_group(zd, name, description = ''):    
    xloc = LOCATORS_CFG_AP_GROUP
    zd.s.type_text(xloc['edit_name'], name)    
    zd.s.type_text(xloc['edit_description'], description)


def _delete_ap_group(zd, name):
    xloc = locators
    r = _get_ap_group_brief_by(zd, dict(name=name), True, op = 'xeq')
    
    chk_btn = (r['tmpl'] % r['idx']) + xloc['apg_tbl_chk']
    zd.s.click_if_not_checked(chk_btn)    
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['apg_delete_btn']) 
    time.sleep(1)
    if not zd.s.is_confirmation_present(5):
        raise Exception("No dialog confirmation for deleting %s appears on checkbox(%s)/del_button(%s)" % (element_name, checkbox, del_button))

    msg = zd.s.get_confirmation()
    time.sleep(1)
    
    
    if (zd.s.is_alert_present(5)):
            msg_alert = zd.s.get_alert()
            raise Exception(msg_alert)
        
    return msg


def _delete_all_ap_group(zd, z_pauseDelete = 4, pause = 1.0):
    xloc = locators
#    wgt._clear_search_txt(zd.s, xloc['apg_tbl_loc'])

    if not zd.s.is_element_present(xloc['apg_tbl_loc']):
        return

    time.sleep(3)    
    tot_wgs = zd.s.get_text(xloc['get_totals'])
    if tot_wgs.find('(1)') > 0:
        logging.info('No AP groups to delete')
        return
        
    time.sleep(pause)
    while zd.s.is_visible(xloc['apg_show_more_btn']):
        zd.s.click_and_wait(xloc['apg_show_more_btn'])
        time.sleep(1)
        
    _delete_selected(zd, z_pauseDelete, pause)
    
    tot_wgs = zd.s.get_text(xloc['get_totals'])
    
    while tot_wgs.find('(1)') == -1:        
        while zd.s.is_element_present(xloc['apg_next_img']) \
        and not zd.s.is_element_disabled(xloc['apg_next_img']):
            _delete_selected(zd, z_pauseDelete, pause)        
            zd.s.click_and_wait(xloc['apg_next_img'])
            time.sleep(2)
            
        time.sleep(2)
        tot_wgs = zd.s.get_text(xloc['get_totals'])
        zd.refresh()
        _delete_selected(zd, z_pauseDelete, pause)
    
    
        
        
    
def _delete_selected(zd, z_pauseDelete = 4, pause = 1.0):
    xloc = locators
    zd.s.click_and_wait(xloc['apg_tbl_chk_all'])
    if zd.s.is_element_present(xloc['check_name_default']) and \
    zd.s.is_visible(xloc['check_name_default']):
        zd.s.click_if_checked(xloc['check_name_default'])
        
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['apg_delete_btn'])
    time.sleep(z_pauseDelete)
    if zd.s.is_confirmation_present(5):
        zd.s.get_confirmation()
        
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        if not re.search('Nothing\s+is\s+selected', _alert, re.I):
            raise Exception(_alert)


def _open_ap_group_dialog_via_create_btn(zd):
    xloc = locators
    if not zd.s.is_element_disabled(xloc['apg_detail_dialog_create_btn']):
        zd.s.click_and_wait(xloc['apg_detail_dialog_create_btn'], 3)
    else:
        raise Exception('The element %s has disabled' % 
                        xloc['apg_detail_dialog_create_btn'])
    

def _open_ap_group_dialog_by_name(zd, name):
    '''
    opens Access Point Group detail dialog for setting/getting values
    '''
    xloc = locators
    return _click_on_ap_group_btn(
        zd, dict(name = name),
        xloc['edit_by_name']
    )


def _click_on_ap_group_btn(zd, match, loc, wait = 1.5):
    r = _get_ap_group_brief_by(zd, match, True, op = 'xeq')    
    btn = (r['tmpl'] % r['idx']) + loc
    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn, wait)
    else:
        raise Exception('Unable to click on the button since it is disabled')

def _save_and_close_ap_group_dialog(zd):
    '''
    saves and closes the Access Point Group detail dialog
    '''
    xloc = LOCATORS_CFG_AP_GROUP
    zd.s.click_and_wait(xloc['edit_OK'])

    if zd.s.is_alert_present(1.5):
        _alert = zd.s.get_alert()
        raise Exception(_alert)


def _cancel_and_close_ap_group_dialog(zd):
    '''
    cancels and closes the Access Point Group detail dialog
    '''
    xloc = LOCATORS_CFG_AP_GROUP
    zd.s.click_and_wait(xloc['edit_Cancel'])




def _get_ap_group_general_info(zd, name = ''):
    '''    
    '''
    xloc = LOCATORS_CFG_AP_GROUP
    items = (
        ('name', xloc['edit_name']),
        ('description', xloc['edit_description']),        
    )

    general_info = {}
    for item in items:
        general_info.update({item[0]: zd.s.get_value(item[1])})
    return general_info
