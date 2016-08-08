from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import access_points_zd as ap

import logging
import time
import re
mesh_topo_widget_title = 'Mesh Topology'
mesh_img_to_role = {'root_ap_s.gif': 'root_ap',
                    'mesh_ap_s.gif': 'mesh_ap',
                    'link_ap_s.gif': 'link_ap',
                     }

mesh_title_map = {'Root AP': 'root_ap',
                  'Mesh AP (1 hop)': 'mesh_ap_1_hop',
                  'Mesh AP (2 hops)': 'mesh_ap_2_hops',
                  'eMesh AP (2 hops)': 'emesh_ap_2_hops',
                  'eMesh AP (3 hops)': 'emesh_ap_3_hops'}

LOCATORS_DASHBOARD = {
    #System overview
    'loc_dashboard_system_name_cell':r"//td[@id='sysname']",
    'loc_dashboard_system_ipaddr_cell':r"//td[@id='sysip']",
    'loc_dashboard_system_macaddr_cell':r"//td[@id='sysmac']",
    'loc_dashboard_system_uptime_cell':r"//td[@id='sysuptime']",
    'loc_dashboard_system_model_cell':r"//td[@id='sysmodel']",
    'loc_dashboard_system_licensed_aps_cell':r"//td[@id='maxap']",
    'loc_dashboard_system_sn_cell':r"//td[@id='sysserial']",
    'loc_dashboard_system_version_cell':r"//td[@id='sysversion']",
        
    #Usage summary, 1 hr
    'loc_dashboard_usage_max_users_cell_h':r"//td[@id='num-sta-h']",
    'loc_dashboard_usage_byte_transimitted_cell_h':r"//td[@id='tx-bytes-h']",
    'loc_dashboard_usage_average_signal_cell_h':r"//td[@id='avg-rssi-h']",
    'loc_dashboard_usage_rogue_devices_cell_h':r"//td[@id='num-rogue-h']",
    
    #24 hrs
    'loc_dashboard_usage_max_users_cell_d':r"//td[@id='num-sta-d']",
    'loc_dashboard_usage_byte_transimitted_cell_d':r"//td[@id='tx-bytes-d']",
    'loc_dashboard_usage_average_signal_cell_d':r"//td[@id='avg-rssi-d']",
    'loc_dashboard_usage_rogue_devices_cell_d':r"//td[@id='num-rogue-d']",
        
    #Support
    'loc_dashboard_support_company_cell':r"//td[@id='company']",
    'loc_dashboard_support_registration_cell':r"//td/a[@id='reg']",
    'loc_dashboard_support_email_cell':r"//td/a[@id='email']",
    'loc_dashboard_support_support_url_cell':r"//td/a[@id='url']",
    
    #Devices overview
    'loc_dashboard_devices_aps_cell':r"//a[@id='num-ap']",
    'loc_dashboard_devices_client_cell':r"//a[@id='num-client']",
    'loc_dashboard_devices_rogue_cell':r"//a[@id='num-rogue']",    
    
    }

#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------

def add_mesh_topology_widget_to_dashboard(zd, **kwargs):
    target_location = zd.info['loc_dashboard_column2_top']
    _goto_dashboard(zd, **kwargs)
    
    if zd.s.is_visible(zd.info['loc_dashboard_meshsummary_table']):
        msg = 'The Mesh Topology is existing in the Dashboard page. Do not to add Mesh Topology widget.'
        logging.debug(msg)
        return
    
    wgt.drag_the_widget_out_to_dashboard(zd, mesh_topo_widget_title, target_location)
    if zd.s.is_visible(zd.info['loc_dashboard_meshsummary_table']):
        msg = 'The Mesh Topology widget is added to Dashboard page successfully.'
        logging.debug(msg)
        return
    else:
        msg = 'Adding Mesh Topology widget is not successfully'
        raise Exception(msg)    

def detect_mesh_tree(zd, ap_mac_list, **kwargs):
    return _detect_mesh_tree(zd, ap_mac_list, **kwargs)

def close_mesh_topology_table(zd, **kwargs):
    close_button = zd.info['loc_dashboard_mesh_topology_close_button']
    _goto_dashboard(zd, **kwargs)
    _close_a_table_in_dashboard(zd, close_button, **kwargs)


def get_system_info(zd, **kwargs):
    '''
    return:
        dict:
            {'System Name':'Ruckus',
             'IP Address':'192.168.0.2',
             'MAC Address':'00:24:82:32:CF:B6',
             'Uptime':'6d 22h 23m',
             'Model':'ZD3000',
             'Licensed APs':'500',
             'Serial Number':'SN1234',
             'Version':'9.1.0.0 build 5',
            }
    '''
    _goto_dashboard(zd, **kwargs)
    locs = LOCATORS_DASHBOARD
    sys_info =  {'System Name':'',
                 'IP Address':'',
                 'MAC Address':'',
                 'Uptime':'',
                 'Model':'',
                 'Licensed APs':'',
                 'Serial Number':'',
                 'Version':'',
                }
    
    _get_text(zd, locs['loc_dashboard_system_name_cell'], sys_info, 'System Name')
    _get_text(zd, locs['loc_dashboard_system_ipaddr_cell'], sys_info, 'IP Address')
    _get_text(zd, locs['loc_dashboard_system_macaddr_cell'], sys_info, 'MAC Address')
    _get_text(zd, locs['loc_dashboard_system_uptime_cell'], sys_info, 'Uptime')
    _get_text(zd, locs['loc_dashboard_system_model_cell'], sys_info, 'Model')
    _get_text(zd, locs['loc_dashboard_system_licensed_aps_cell'], sys_info, 'Licensed APs')
    _get_text(zd, locs['loc_dashboard_system_sn_cell'], sys_info, 'Serial Number')
    _get_text(zd, locs['loc_dashboard_system_version_cell'], sys_info, 'Version')
    
    return sys_info
    
    

def get_usage_info(zd, **kwargs):
    '''
    return:
      dict:
          {
              'h':
                  {'Max Concurrent Users':'0',
                   'Bytes Transmitted':'3.0M',
                   'Average Signal (%)':'N/A',
                   'Number of Rogue Devices':'425',
                   },
             'd':
                 {'Max Concurrent Users':'0',
                  'Bytes Transmitted':'520M',
                  'Average Signal (%)':'30%',
                  'Number of Rogue Devices':'526',
                  },
          }
    '''    
    h = {'Max Concurrent Users':'',
         'Bytes Transmitted':'',
         'Average Signal (%)':'',
         'Number of Rogue Devices':'',
        }
    d = {'Max Concurrent Users':'',
         'Bytes Transmitted':'',
         'Average Signal (%)':'',
         'Number of Rogue Devices':'',
        }
    _goto_dashboard(zd, **kwargs)
    locs = LOCATORS_DASHBOARD
    #get hour
    _get_text(zd, locs['loc_dashboard_usage_max_users_cell_h'], h, 'Max Concurrent Users')
    _get_text(zd, locs['loc_dashboard_usage_byte_transimitted_cell_h'], h, 'Bytes Transmitted')
    _get_text(zd, locs['loc_dashboard_usage_average_signal_cell_h'], h, 'Average Signal (%)')
    _get_text(zd, locs['loc_dashboard_usage_rogue_devices_cell_h'], h, 'Number of Rogue Devices')
    
    #get day
    _get_text(zd, locs['loc_dashboard_usage_max_users_cell_d'], d, 'Max Concurrent Users')
    _get_text(zd, locs['loc_dashboard_usage_byte_transimitted_cell_d'], d, 'Bytes Transmitted')
    _get_text(zd, locs['loc_dashboard_usage_average_signal_cell_d'], d, 'Average Signal (%)')
    _get_text(zd, locs['loc_dashboard_usage_rogue_devices_cell_d'], d, 'Number of Rogue Devices')
    
    return {'h':h, 'd':d}
    


def get_support_info(zd, **kwargs):
    '''
    return:
      dict:
          {'Company':'Ruckus Wireless',
           'Registration':'Product Registration',
           'Email':'support@ruckuswireless.com',
           'Support URL':'http://support.ruckuswireless.com/',
          }
    '''
    s = {'Company':'',
         'Registration':'',
         'Email':'',
         'Support URL':''
         }
    _goto_dashboard(zd, **kwargs)
    locs = LOCATORS_DASHBOARD
    _get_text(zd, locs['loc_dashboard_support_company_cell'], s, 'Company')
    _get_text(zd, locs['loc_dashboard_support_registration_cell'], s, 'Registration')
    _get_text(zd, locs['loc_dashboard_support_email_cell'], s, 'Email')
    _get_text(zd, locs['loc_dashboard_support_support_url_cell'], s, 'Support URL')
    
    return s


def get_devices_info(zd, **kwargs):
    """
    Get the devices info as below:
    {'num-aps':r'0',
     'num-client':r'0',
     'num-rogue':r'0'
    }
    """
    _goto_dashboard(zd)
    return _get_devices_info(zd, **kwargs)

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------

def _get_text(zd, locator, dd, k):
    if zd.s.is_element_present(locator):
        dd[k] = zd.s.get_text(locator)


def _close_a_table_in_dashboard(zd, close_button, **kwargs):
    if zd.s.is_visible(close_button):
        zd.s.click(close_button)

def _get_devices_info(zd, **kwargs):
    conf = {'num-aps':r'0',
            'num-client':r'0',
            'num-rogue':r'0'}
    info = LOCATORS_DASHBOARD
    if not zd._wait_for_element(info['loc_dashboard_devices_aps_cell'], timeout=30, is_refresh=True):
        raise Exception('Element [%s] not found' % info['loc_dashboard_devices_aps_cell'])
    
    aps = zd.s.get_text(info['loc_dashboard_devices_aps_cell'])
    clients = zd.s.get_text(info['loc_dashboard_devices_client_cell'])
    rogues = zd.s.get_text(info['loc_dashboard_devices_rogue_cell'])
    conf['num-aps'] = aps
    conf['num-client'] = clients
    conf['num-rogue'] = rogues
    
    return conf

def _detect_mesh_tree(zd, ap_mac_list, **kwargs):
    conf = {'wait':2}
    if kwargs:
        conf.update(kwargs)
    mtree = {}
    ap_info_list = ap.get_all_ap_info(zd).values()    
    mesh_topo = _get_mesh_topology_info(zd, ap_info_list, **conf)
    for ap_mac in ap_mac_list:
        for role in mesh_topo.keys():
            if mesh_topo[role].has_key(ap_mac):
                if not mesh_title_map.has_key(mesh_topo[role][ap_mac]):
                    continue
                if mtree.has_key(mesh_title_map[mesh_topo[role][ap_mac]]):
                    mtree[mesh_title_map[mesh_topo[role][ap_mac]]].append(ap_mac)
                else:
                    mtree[mesh_title_map[mesh_topo[role][ap_mac]]] = [ap_mac]
    return mtree

def _get_mesh_topology_info(zd, ap_info_list, **kwargs):
    conf = {'wait':2}
    if kwargs:
        conf.update(kwargs)
    
    mesh_topo = {}
    
    _goto_dashboard(zd)
    time.sleep(conf['wait'])
    
    for ap_info in ap_info_list:
        mesh_role, mesh_title = _get_ap_mesh_status(zd, ap_info['mac_address'], **kwargs)
        if not mesh_topo.get(mesh_role):
            mesh_topo[mesh_role] = {}
        mesh_topo[mesh_role][ap_info['mac_address']] = mesh_title
    
    return mesh_topo

def _get_ap_mesh_status(zd, ap_mac, **kwargs):
    ap_status_img = zd.info['loc_dashboard_ap_status_img'] % ap_mac.lower()
    ap_status_title = zd.info['loc_dashboard_ap_status_title'] % ap_mac.lower()
    ap_img_name = zd.s.get_attribute(ap_status_img).split('/')[-1]
    ap_title = zd.s.get_attribute(ap_status_title)
    
    return mesh_img_to_role[ap_img_name], ap_title 

def _goto_dashboard(zd, **kwargs):
    conf = {'wait':2}
    if kwargs:
        conf.update(kwargs)
    zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
    time.sleep(conf['wait'])

def get_zd_original_AP_num(zd):
    sys_info = get_system_info(zd)
    pattern = 'ZD(\d+)'
    m = re.search(pattern,sys_info['Model'])
    zd_model = m.group(1)
    if zd_model.startswith('3'):
        return int(zd_model) - 3000
    elif zd_model.startswith('5'):
        return int(zd_model) - 5000
    elif zd_model.startswith('12'):
        return int(zd_model) - 1200