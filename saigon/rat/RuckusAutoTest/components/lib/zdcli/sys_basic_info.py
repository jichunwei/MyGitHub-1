'''
Author#cwang@ruckuswireless.com
date#2010-10-28
This file is used for system  information [Country Code, NTP, System Name, Log] getting/setting/searching etc.
'''
import re

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output


#=============================================#
#             Access Methods            
#=============================================#
def get_sys_info(zdcli):
    '''
    Get system information.
    '''  
    res = zdcli.do_show(SHOW_SYS)
    rr = output.parse(res)
    return rr

def get_version(zdcli):
    return get_sys_info(zdcli)['System Overview']['Version'].replace(' build ','.')
def get_sys_uptime(zdcli):
    ret_up_time = None
    
    sys_info = get_sys_info(zdcli)
    key_sys = 'System Overview'
    if sys_info.has_key(key_sys):
        up_time = sys_info[key_sys].get('Uptime')
        if up_time:
            ret_up_time = _resolve_uptime(up_time)
            
    return ret_up_time

def get_cfg_sys_info(zdcli):
    '''
    Go to config>>system,
    and show.
    '''
    res = zdcli.do_cfg_show(CONFIG_SYS_SHOW)
    rr = output.parse(res)
    return rr
    

def verify_devices_overview(gui_d, cli_d):
    '''
    Checking devices information under dash board
    '''
    return _verify_devices_overview(gui_d, cli_d)


def verify_sys_overview(gui_d, cli_d):
    '''
    Checking system overview under dash board 
    '''
    return _verify_sys_overview(gui_d, cli_d)

#usage information checking
HOUR = 1
DAY = 24
def verify_usage_summary(gui_d, cli_d, type = HOUR):
    '''
    Checking usage summary under dash board
    '''
    return _verify_usage_summary(gui_d, cli_d, type)


def verify_sys_name(gui_d, cli_d):
    '''
    Checking System name, between GUI and CLI.
    '''
    return _verify_sys_name(gui_d, cli_d)


def verify_country_code(gui_d, cli_d):
    '''
    Checking country code between GUI and CLI.
    '''
    return _verify_country_code(gui_d, cli_d)


def verify_ntp(gui_d, cli_d):
    '''
    Checking NTP information between GUI and CLI.
    '''
    return _verify_ntp(gui_d, cli_d)


def verify_log(gui_d, cli_d):
    '''
    Checking LOG information between GUI and CLI.
    '''
    return _verify_log(gui_d, cli_d)

def get_zd_mac(zdcli):
    cmd = 'show sysinfo'
    res = zdcli.do_cmd(cmd)
    return res.split('MAC Address=')[1].split('Uptime=')[0].strip()

#===============================================#
#           Protected Constant
#===============================================#
SHOW_SYS = '''
sysinfo
'''
CONFIG_SYS_SHOW = '''
system
'''
C_CODE_K_MAP = {'Code':'label',}
LOG_K_MAP = {'Address':'remote_syslog_ip',
             'Status':'enable_remote_syslog',
             }
DEVICES_OVERVIEW_K_MAP ={'Number of APs':'num-aps',
                         'Number of Client Devices':'num-client',
                         'Number of Rogue Devices':'num-rogue',
                         } 
#===============================================#
#           Protected Method
#===============================================#

def _resolve_uptime(uptime):
    res = re.search("(\d+d)?\s*(\d+h)?\s*(\d+m)", uptime)
    if not res:
        raise Exception("Invalid format %s" % uptime)
    
    _dd = int(res.group(1)[:-1]) * 60 * 60 * 24 if res.group(1) else 0
    _hh = int(res.group(2)[:-1]) * 60 * 60 if res.group(2) else 0
    _mm = int(res.group(3)[:-1]) * 60
    
    return _dd + _hh + _mm

        

def _verify_sys_overview(gui_d, cli_d):
    '''
    GUI:
    {'System Name':'Ruckus',
     'IP Address':'192.168.0.2',
     'MAC Address':'00:24:82:32:CF:B6',
     'Uptime':'6d 22h 23m',
     'Model':'ZD3000',
     'Licensed APs':'500',
     'Serial Number':'SN1234',
     'Version':'9.1.0.0 build 5',
    }
    CLI:
     {'IP Address': '192.168.0.2',
      'Licensed APs': '500',
      'MAC Address': '00:24:82:32:CF:B6',
      'Model': 'ZD3500',
      'Name': 'Ruckus',
      'Serial Number': 'SN1234',
      'Uptime': '2d 3h 35m',
      'Version': '9.1.0.0 build 5'}
    '''
    return _validate_dict_value(gui_d, cli_d)

def _verify_mem_utilization_overview(gui_d, cli_d):
    '''
    CLI:
    {'Free Bytes': '847843328',
     'Free Percentage': '92%',
     'Used Bytes': '80125952',
     'Used Percentage': '8%'}
    '''
    pass

def _verify_usage_summary(gui_d, cli_d, type = 1):
    '''
    
    GUI:    
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
    
    CLI:
     {'Usage of 1 hr': {'Bytes Transmitted': '0B',
                        'Max Concurrent Users': '0',
                        'Number of Rogue Devices': '0'},
      'Usage of 24 hr': {'Bytes Transmitted': '0B',
                         'Max Concurrent Users': '0',
                         'Number of Rogue Devices': '0'}}    
    '''
    g_h = gui_d['h']
    _tran_v(g_h)
    c_h = cli_d['Usage of 1 hr']
    _tran_v(c_h)
    
    g_d = gui_d['d']
    _tran_v(g_d)
    c_d = cli_d['Usage of 24 hr']
    _tran_v(c_d)
    
    if type == 1:
        return _validate_dict_value(g_h, c_h)
    elif type == 24:
        return _validate_dict_value(g_d, c_d)
    else:
        raise Exception('Un-support type [%d]' % type)

def _tran_v(c_h):
    if c_h.has_key('Bytes Transmitted'):
        bt = c_h['Bytes Transmitted']
        if bt[-1] not in ['B', 'K', 'M']:
            bt = bt + 'B'
        v = bt[:-1]
        try:
            v = int(round(v))
        except:
            v = int(round(float(v)))
        v = '%d%s' % (v, bt[-1])
        c_h['Bytes Transmitted'] = v    

    

def _verify_devices_overview(gui_d, cli_d):
    '''
    GUI:
    {'num-aps': u'4294967295', 
     'num-client': u'0', 
     'num-rogue': u'0'}
    
    CLI:
    {'Number of APs': '4294967295',
     'Number of Client Devices': '0',
     'Number of Rogue Devices': '0'}
    '''
    r_d = _map_k_d(gui_d, cli_d, DEVICES_OVERVIEW_K_MAP)
    return _validate_dict_value(r_d, cli_d)

def _verify_sys_name(gui_d, cli_d):
    '''
    GUI:
    {'Name': 'Ruckus'}
    CLI:
    {'Name': 'Ruckus'},
    '''
    r_d = {'Name':gui_d}
    return _validate_dict_value(r_d, cli_d)

def _verify_country_code(gui_d, cli_d):
    '''
    GUI:
        {'label': u'United States', 'value': u'US'}
    CLI:
        {'Code': 'United States'}
    '''
    r_d = _map_k_d(gui_d, cli_d, C_CODE_K_MAP)
    return _validate_dict_value(r_d, cli_d)

def _verify_ntp(gui_d, cli_d):
    '''
    GUI:
     {'Address':u'ntp.ruckuswireless.com}
    CLI:
     {'Address': 'ntp.ruckuswireless.com', 'Status': 'Enabled'}
    '''
    if cli_d['Status'] == 'Enabled':
        if gui_d['Address'] == cli_d['Address']:
            return (True, '')
        else:
            return (False, 'Address is different between GUI [%s] and CLI [%s]' % (gui_d['Address'], cli_d['Address']))
    elif cli_d['Status'] == 'Disabled':
        return (True, 'NTP server is disabled')
    else:
        return (False, 'Unknown status [%s] from CLI' % cli_d['Status'])
    
def _verify_log(gui_d, cli_d):
    '''
    GUI:
        {'enable_remote_syslog': True,
         'log_level': 'show_more',
         'remote_syslog_ip': u'192.168.0.252'}        
    CLI:
        {'Address': '192.168.0.252', 'Status': 'Enabled'}
    '''
    if gui_d['enable_remote_syslog']:
        gui_d['enable_remote_syslog'] = 'Enabled'
    else:
        gui_d['enable_remote_syslog'] = 'Disabled'
    
    r_d = _map_k_d(gui_d, cli_d, LOG_K_MAP)
    return _validate_dict_value(r_d, cli_d)


def _map_k_d(gui_d, cli_d, k_map):
    '''
    Mapping GUI key to CLI key.
    '''
    r_d = {}
    for key in gui_d.keys():
        for k, v in k_map.items():
            if key == v:
                r_d[k] = gui_d[v]
                
    return r_d


def _validate_dict_value(gui_d, cli_d):
    for g_k, g_v in gui_d.items():
        for c_k, c_v in cli_d.items():                            
            if g_k == c_k:
                if g_k == "Uptime":
                    g_v = _resolve_uptime(g_v)
                    c_v = _resolve_uptime(c_v)
                    if abs(g_v - c_v) < 120:
                        continue
                    else:
                        return (False, 
                                'value of key [%s] is not equal with diff 120s' % g_k)
                if g_v == c_v:
                    continue
                else:
                    return (False, 'value of key [%s] is not equal' % g_k)
                            
    return (True, 'All of value are matched')
