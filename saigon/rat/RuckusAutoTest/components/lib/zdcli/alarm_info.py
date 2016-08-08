'''
Author#cwang@ruckuswireless.com
date#2010-10-28
This file is used for system  information [Country Code, NTP, System Name, Log] getting/setting/searching etc.
'''
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

import re

#=============================================#
#             Access Methods            
#=============================================#
def get_alarm_info(zdcli):
    '''
    Go to config>>alarm,
    and show.
    Issue: after show alarm information, use exist to return,
    it will change email alarm to enabled.    
    Output:
    {'Alarm Status': 'Enabled',
     'Email Address': 'cherry.cheng@ruckuswireless.com',
     'E-mail From': '',
     'Encryption Options': 'STARTTLS'/'TLS'/'None',
     'SMTP Authentication Password': '123456789',
     'SMTP Authentication Username': 'CherryTest7v3',
     'SMTP Server Name': 'CherryTest6v3',
     'SMTP Server Port': '587'
   }
    '''
    res = zdcli.do_cfg_show(ALARM_INFO_SHOW)    
    
    rr = output.parse(res)  
    
    rr = _parse_encrypt_options(rr)

    return rr

#===============================================#
#           Protected Constant
#===============================================#
ALARM_INFO_SHOW = '''
alarm
'''

#===============================================#
#           Protected Method
#===============================================#


#Updated by cwang@20130529, just support from 9.5
def _parse_encrypt_options(alarm_info):
    '''
    Input:
    {'Alarm': {'Status': 'Enabled',
               'Email Address': 'cherry.cheng@ruckuswireless.com',
               'E-mail From': '',
               'SMTP Encryption Options': {'TLS': 'Enabled',
                                           ['STARTTLS': 'Enabled']
                                          },
               'SMTP Authentication Password': '123456789',
               'SMTP Authentication Username': 'CherryTest7v3',
               'SMTP Server Name': 'CherryTest6v3',
               'SMTP Server Port': '587'
               }
    }
    Output:
    {'Alarm Status': 'Enabled',
     'Email Address': 'cherry.cheng@ruckuswireless.com',
     'E-mail From': '',
     'Encryption Options': 'STARTTLS'/'TLS'/'None',
     'SMTP Authentication Password': '123456789',
     'SMTP Authentication Username': 'CherryTest7v3',
     'SMTP Server Name': 'CherryTest6v3',
     'SMTP Server Port': '587'
    }
    '''
    
    _info = alarm_info['Alarm']
    
    _info['Alarm Status']= _info.pop('Status')
    #SMTP Encryption Options
    if _info.has_key('SMTP Encryption Options'):
        encrytion_options = _info.pop('SMTP Encryption Options')
        tls = encrytion_options['TLS']
        #when 'TLS' is disabled, 'STARTTLS' doesn't show in ZD CLI.
        starttls = encrytion_options.get('STARTTLS')
        
        _opts = 'None'
        if tls == 'Enabled' and starttls == 'Enabled':
            _opts = 'STARTTLS'
        
        elif tls == 'Enabled':
            _opts  = 'TLS'
            
        _info['Encryption Options'] = _opts
            
    return _info
    
