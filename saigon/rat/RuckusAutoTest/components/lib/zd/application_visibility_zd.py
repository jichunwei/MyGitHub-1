'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswireless.com
'''

Locators = dict(avp_table= r"//table[@id='avppie-details']",
                show_avp_detail_btn = r"//input[@id='show-details']")

def get_application_visibility_info_by_index(zd):
    '''
{1: {u'desc': u'Common-Internet-File-System',
     u'downlink': u'56',
     u'percent': u'34.12%',
     u'uplink': u'< 1',
     u'usage': u'56'},
 2: {u'desc': u'DNS',
     u'downlink': u'9',
     u'percent': u'27.05%',
     u'uplink': u'35',
     u'usage': u'44'},
 3: {u'desc': u'Windows-File-and-Print-Services',
     u'downlink': u'22',
     u'percent': u'13.73%',
     u'uplink': u'< 1',
     u'usage': u'22'},
 4: {u'desc': u'Miscellaneous',
     u'downlink': u'< 1',
     u'percent': u'10.9%',
     u'uplink': u'17',
     u'usage': u'17'},
 5: {u'desc': u'ARP',
     u'downlink': u'9',
     u'percent': u'10.09%',
     u'uplink': u'7',
     u'usage': u'16'},
 6: {u'desc': u'ICMP',
     u'downlink': u'< 1',
     u'percent': u'4.04%',
     u'uplink': u'6',
     u'usage': u'6'},
 7: {u'desc': u'L2',
     u'downlink': u'< 1',
     u'percent': u'0.03%',
     u'uplink': u'< 1',
     u'usage': u'< 1'}}
    '''

    zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
    if zd.s.is_element_present(Locators['show_avp_detail_btn']):
        zd.s.safe_click(Locators['show_avp_detail_btn'])
    if not zd.s.is_element_present(Locators['avp_table']):
        return {}
    avp_table_header = zd.s.get_tbl_hdrs_by_attr(Locators['avp_table'])
    avp_table_content = zd.s.iter_table_rows(Locators['avp_table'], avp_table_header)
    avp_table_content_dict = {}
#get avp info by index
    for row in avp_table_content:
        app_id = row['idx']
        row['row'].pop('#')
        avp_table_content_dict[str(app_id)] = row['row']
    return avp_table_content_dict

def get_application_visibility_info_by_description(zd):
    '''
{u'ARP': {u'downlink': u'9',
          'idx': '5',
          u'percent': u'10.09%',
          u'uplink': u'7',
          u'usage': u'16'},
 u'Common-Internet-File-System': {u'downlink': u'56',
                                  'idx': '1',
                                  u'percent': u'34.12%',
                                  u'uplink': u'< 1',
                                  u'usage': u'56'},
 u'DNS': {u'downlink': u'9',
          'idx': '2',
          u'percent': u'27.05%',
          u'uplink': u'35',
          u'usage': u'44'},
 u'ICMP': {u'downlink': u'< 1',
           'idx': '6',
           u'percent': u'4.04%',
           u'uplink': u'6',
           u'usage': u'6'},
 u'L2': {u'downlink': u'< 1',
         'idx': '7',
         u'percent': u'0.03%',
         u'uplink': u'< 1',
         u'usage': u'< 1'},
 u'Miscellaneous': {u'downlink': u'< 1',
                    'idx': '4',
                    u'percent': u'10.9%',
                    u'uplink': u'17',
                    u'usage': u'17'},
 u'Windows-File-and-Print-Services': {u'downlink': u'22',
                                      'idx': '3',
                                      u'percent': u'13.73%',
                                      u'uplink': u'< 1',
                                      u'usage': u'22'}}
    '''
    
    zd.navigate_to(zd.MONITOR, zd.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
    if zd.s.is_element_present(Locators['show_avp_detail_btn']):
        zd.s.safe_click(Locators['show_avp_detail_btn'])
    if not zd.s.is_element_present(Locators['avp_table']):
        return {}
    avp_table_header = zd.s.get_tbl_hdrs_by_attr(Locators['avp_table'])
    avp_table_content = zd.s.iter_table_rows(Locators['avp_table'], avp_table_header)
    avp_table_content_dict = {}
#get avp info by description
    for row in avp_table_content:
        app_id = row['idx']
        app_desc = row['row']['desc']
        row['row']['idx'] = str(app_id)
        row['row'].pop('#')
        row['row'].pop('desc')
        avp_table_content_dict[app_desc] = row['row']
    return avp_table_content_dict

