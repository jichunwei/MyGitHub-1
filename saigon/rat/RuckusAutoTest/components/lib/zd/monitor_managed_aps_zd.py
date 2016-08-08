"""
Examples: [Execute following statements from the 'rat' directory]

from ratenv import *
from RuckusAutoTest.components.lib import monitor_managed_aps_zd as MMA
from pprint import pprint

zd = ZoneDirector.ZoneDirector({})  # default ZD ip_addr='192.168.0.2'

MMA.restart_ap_by_ip_addr(zd, [u'192.168.0.186',u'192.168.0.235',u'192.168.0.182',])

aps_mac = MMA.get_ap_status_by_mac(zd, ['00:1d:2e:16:4f:60', '00:22:7f:04:63:50'])
aps_ipa = MMA.get_ap_status_by_ip_addr(zd, ['192.168.0.235', '192.168.0.182', '192.168.0.186', ])

pprint(aps_ipa)
pprint(aps_mac)
"""

import logging
import time
from RuckusAutoTest.common import lib_Constant as constant

map_item = {'MAC Address':           'loc_mon_access_points_edit_column_mac_'  ,
            'Device Name':           'loc_mon_access_points_edit_column_device_name_' ,   
            'Description':           'loc_mon_access_points_edit_column_description_',
            'Location':              'loc_mon_access_points_edit_column_location_'      ,
            'Model':                 'loc_mon_access_points_edit_column_model_'          ,  
            'Status':                'loc_mon_access_points_edit_column_state_'         ,   
            'Mesh Mode':             'loc_mon_access_points_edit_column_mesh_mode_'    ,
            'IP Address':            'loc_mon_access_points_edit_column_ip_'          ,        
            'External IP:Port':      'loc_mon_access_points_edit_column_ext_ip_port_',
            'VLAN':                  'loc_mon_access_points_edit_column_vlan_'      ,
            'Channel':               'loc_mon_access_points_edit_column_channel_'  ,
            'Clients':               'loc_mon_access_points_edit_column_clients_' ,    
            'Bonjour Gateway':       'loc_mon_access_points_edit_column_bonjour_',
            'Application Capability':'loc_mon_access_points_edit_column_application_', }


from RuckusAutoTest.common.DialogHandler import (
    DialogManager, BaseDialog,
)

LOCATOR_MON_MANAGED_APS = dict(
    # restart_by_mac = r"//table[@id='apsummary']//td/a[text()='00:22:7f:24:a9:80']/../../td/img[@title='Restart']"
    restart_by_mac = r"//table[@id='apsummary']//td/a[text()='%s']/../../td/img[@title='Restart']",
    restart_by_ip_addr = r"//table[@id='apsummary']//td[text()='%s']/../td/img[@title='Restart']",
    # action: ['Restart', 'System Info', 'SpeedFlex', 'Configure', 'Recover']
    action_by_mac = r"//table[@id='apsummary']//td/a[text()='%s']/../../td/img[@title='%s']",

    # AP status by {mac|ip_addr}
    apstatus_by_mac = r"//table[@id='apsummary']//td/a[text()='%s']/../../td[%d]",
    apstatus_by_ip_addr = r"//table[@id='apsummary']//td[text()='%s']/../td[%d]",
    apstatus_dict_std = {
        'mac': 1, 'description': 2, 'model': 3, 'status': 4, 'mesh_mode': 0,
        'ip_addr': 5, 'vlan': 0, 'channel': 6, 'clients': 7,
    },
    apstatus_dict_mgmt_vlan = {
        'mac': 1, 'description': 2, 'model': 3, 'status': 4, 'mesh_mode': 5,
        'ip_addr': 6, 'vlan': 7, 'channel': 8, 'clients': 9,
    }
)

def nav_to(zd):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_ACCESS_POINTS)


# Examples:
#
#   restart_ap_by_mac(zd, ['00:1d:2e:16:3a:c0'])
#   restart_ap_by_mac(zd, '00:22:7f:24:a9:00')
#   restart_ap_by_mac(zd, ['00:1d:2e:16:3a:c0', '00:1d:2e:15:ff:c0', '00:22:7f:24:a9:80'])
#
def restart_ap_by_mac(zd, macAddr, **kwargs):
    nav_to(zd)
    macAddrList = macAddr if type(macAddr) is list else [macAddr]
    for mac in macAddrList:
        _restart_ap_by_mac(zd, mac, **kwargs)


def restart_ap_by_ip_addr(zd, ip_addr, **kwargs):
    nav_to(zd)
    ip_addr_list = ip_addr if type(ip_addr) is list else [ip_addr]
    for ipa in ip_addr_list:
        _restart_ap_by_ip_addr(zd, ipa, **kwargs)

def get_ap_status_by_mac(zd, macAddr, **kwargs):
    nav_to(zd)
    aps_list = {}
    macAddrList = macAddr if type(macAddr) is list else [macAddr]
    for mac in macAddrList:
        try:
            aps_list[mac] = _get_ap_status_by_mac(zd, mac, **kwargs)

        except:
            aps_list[mac] = {}

    return aps_list


def get_ap_status_by_ip_addr(zd, ip_addr, **kwargs):
    nav_to(zd)
    aps_list = {}
    ip_addr_list = ip_addr if type(ip_addr) is list else [ip_addr]
    for ipa in ip_addr_list:
        try:
            aps_list[ipa] = _get_ap_status_by_ip_addr(zd, ipa, **kwargs)

        except:
            aps_list[ipa] = {}

    return aps_list

def export_csv(zd, **kwargs):
    nav_to(zd)
    if kwargs.get('search_term'):
        zd._fill_search_txt(zd.info['loc_mon_access_points_search_text'], kwargs.get('search_term'))
    file_name = _export_ap_csv(zd)
    
    file_path, res = _check_csv_file(file_name)
    if res:
        logging.info("save csv file to %s" % file_path)
        return file_path
    else:
        raise Exception("cannot find/save csv file")
    
def edit_currently_managed_aps_column(zd, enable_columns, disable_columns):
    nav_to(zd)
    return _edit_currently_managed_aps_column(zd, enable_columns, disable_columns)
#
#
#
def _restart_ap_by_mac(zd, macAddr, **kwargs):
    rcfg = dict(retry = 2, pause = 1)
    rcfg.update(kwargs)
    xloc = LOCATOR_MON_MANAGED_APS
    rloc = xloc['restart_by_mac'] % macAddr
    logging.info("[RESTART AP] [MAC %s]" % (macAddr))
    while rcfg['retry'] > 0:
        if zd.s.is_element_present(rloc):
            zd.s.click_and_wait(rloc)
            return

        time.sleep(rcfg['pause'])
        rcfg['retry'] -= 1

    raise Exception("[Status AP] [MAC %s] does not exist in 'Currently Managed APs' table." % macAddr)

def _restart_ap_by_ip_addr(zd, ip_addr, **kwargs):
    rcfg = dict(retry = 2, pause = 1)
    rcfg.update(kwargs)
    xloc = LOCATOR_MON_MANAGED_APS
    rloc = xloc['restart_by_ip_addr'] % ip_addr
    logging.info("[RESTART AP] [IPADDR %s]" % (ip_addr))
    while rcfg['retry'] > 0:
        if zd.s.is_element_present(rloc):
            zd.s.click_and_wait(rloc)
            return

        time.sleep(rcfg['pause'])
        rcfg['retry'] -= 1

    raise Exception("[Status AP] [IPADDR %s] does not exist in 'Currently Managed APs' table." % ip_addr)

def _get_ap_status_by_mac(zd, macAddr, **kwargs):
    xloc = LOCATOR_MON_MANAGED_APS
    apstatus_dict = xloc['apstatus_dict_mgmt_vlan'] if zd.has_mgmt_vlan else xloc['apstatus_dict_std']
    apstatus_by_mac = xloc['apstatus_by_mac']
    apstatus = {}
    for key, val in apstatus_dict.items():
        if val > 0:
            element_xpath = apstatus_by_mac % (macAddr, val)
            apstatus[key] = zd.s.get_text(element_xpath)

    return apstatus

def _get_ap_status_by_ip_addr(zd, ip_addr, **kwargs):
    xloc = LOCATOR_MON_MANAGED_APS
    apstatus_dict = xloc['apstatus_dict_mgmt_vlan'] if zd.has_mgmt_vlan else xloc['apstatus_dict_std']
    apstatus_by_ip_addr = xloc['apstatus_by_ip_addr']
    apstatus = {}
    for key, val in apstatus_dict.items():
        if val > 0:
            element_xpath = apstatus_by_ip_addr % (ip_addr, val)
            apstatus[key] = zd.s.get_text(element_xpath)

    return apstatus

def _export_ap_csv(zd, save_to=''):
    try:
        # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
        time.sleep(2)
        dlg_mgr = DialogManager()
        # navigate to the Save to Disk option
        dlg1 = BaseDialog(title = None, text = "", button_name = "", key_string = "{PAUSE 3} %s {PAUSE 1} {ENTER}")
        # set the dialog title which matches this regex
        dlg1.set_title_re("Opening .+.csv")

        dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "OK", key_string = "{PAUSE 3} %{F4}")
        
        dlg_mgr.add_dialog(dlg1)
        dlg_mgr.add_dialog(dlg2)
        
        dlg_mgr.start()
        time.sleep(10)
        
        logging.info('start to export csv!')
        button = zd.info['loc_mon_access_points_export_csv_button']
        if zd.s.is_element_visible(button):
            zd.s.click_and_wait(button)
        else:
            raise Exception("cannot find export csv button")
        
        time.sleep(5)
    except Exception, e:
        logging.info('[export csv error]: %s' % e.message)
    finally:
        # Regardless what has happened, stop the dialog handlers
        file_name = dlg1.get_title()
        file_name = file_name.split(' ')[-1]
        logging.info("csv file name is %s" % file_name)
        dlg_mgr.shutdown()
        return file_name

def _check_csv_file(file_name):
    import os
    path = constant.save_to
    ret = os.path.isfile(os.path.join(path, file_name))#Chico, 2015-8-13, correct a error
    if ret:
        return os.path.join(path, file_name), ret#Chico, 2015-8-13, correct a error
    else:
        return None, ret

def _edit_column_if_visible(zd, item):
    try:
        if zd.s.is_element_present(zd.info[item]):
            zd.s.click_and_wait(zd.info[item])
    except Exception, e:
        logging.info('[edit column error]: %s' % e.message)
        raise e


def _edit_currently_managed_aps_column(zd, enable_columns, disable_columns):
    '''
    this function is for edit currently mananged APs column 
    params: zd                  ZoneDirector instance
            enable_columns      the list of columns which should be shown
            disable_columns     the list of columns which should not be shown
            
    column list must be a set of ['Application Capability','Bonjour Gateway','Channel',
                                  'Clients','Description','Device Name','External IP:Port',
                                  'IP Address','Location','MAC Address','Mesh Mode','Model','Status','VLAN',]
    '''
    try:
        logging.info('start edit currently managed APs column')
        logging.info('[enable column] %s' % enable_columns)
        logging.info('[disable column] %s' % disable_columns)
        button = zd.info['loc_mon_access_points_edit_column_button']
        if zd.s.is_element_visible(button):
            zd.s.click_and_wait(button)
        else:
            raise Exception("cannot find edit currently managed APs column button")
        
        for i in enable_columns:
            _edit_column_if_visible(zd, map_item[i]+'add')
        
        for i in disable_columns:
            _edit_column_if_visible(zd, map_item[i]+'del')
        
        button = zd.info['loc_mon_access_points_done_column_button']    
        if zd.s.is_element_visible(button):
            zd.s.click_and_wait(button)
        else:
            raise Exception("cannot find done currently managed APs column button")
    except Exception, e:
        logging.info('[edit currently managed APs column error]: %s' % e.message)
        button = zd.info['loc_mon_access_points_done_column_button'] 
        if zd.s.is_element_visible(button):
            zd.s.click_and_wait(button)
        return e.message
            
    return ''    