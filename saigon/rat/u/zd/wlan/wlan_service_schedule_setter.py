'''
Instance for wlan service schedule setting.
    support on/off/specific to WLAN.
How to:
    python tea.py u.zd.wlan.wlan_service_schedule_setter on=True
    python tea.py u.zd.wlan.wlan_service_schedule_setter off=True
    python tea.py u.zd.wlan.wlan_service_schedule_setter specific=True
Created on 2011-4-18
@author: cwang@ruckuswirelss.com
'''
import logging
from datetime import datetime
import random
import re

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from contrib.wlandemo import defaultWlanConfigParams as wlan_param_helper
from RuckusAutoTest.components import Helper_ZD

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(cfg):
    zd = create_zd_by_ip_addr(**default_cfg)
    zd.remove_all_wlan()
    wlan_cfg = wlan_param_helper.get_cfg('open-none')    
    wlan_cfg['ssid'] = 'rat-wlan-service-schedule-%d' % random.randint(10000, 20000)
    _schedule = {'on':False,
                'off':True,
                'specific':None,
                }
    if cfg['on']:
        _schedule['on'] = True
        _schedule['off'] = False
        _schedule['specific'] = None
    elif cfg['off']:        
        _schedule['on'] = False
        _schedule['off'] = True
        _schedule['specific'] = None
    elif cfg['specific']:        
        _schedule['on'] = False
        _schedule['off'] = False
        #sync-up pc time
        zd.get_current_time(True)
        #schedule 15 Mins for current WLAN
        dt = datetime.today()        
        wd = dt.weekday() + 1
        h = dt.hour
        m = dt.minute
        init_pos = h * 4 + m/15 + 1
        _basetime = None
        if init_pos + 1 >= 97:
            if wd < 6:                        
                _basetime = {'%s' % wd : [init_pos],
                             '%s' % (wd+1) : [1], 
                             }
            else:
                _basetime = {'%s' % wd : [init_pos],
                             '%s' % (wd-7) : [1],
                             }
        else:
            _basetime = {'%s' % wd : [init_pos, init_pos + 1],}
        
        _schedule['specific'] = _basetime
    
    wlan_cfg['do_service_schedule'] = _schedule
    return (zd, wlan_cfg)
        

def do_test(zd, wlan_conf):
    try:
        zd.clear_all_events()
        Helper_ZD.wlan.create_wlan(zd, wlan_conf)
        #WLAN[rat-wlan-service-schedule-18420] has been deployed on radio [11a/n] of AP[ac:67:06:33:78:90] with BSSID[ac:67:06:33:78:9d]
        e_list = zd.get_events()
        exp_11an = 'WLAN\[%s\] has been deployed on radio \[11a/n\] of AP\[[0-9a-fA-F:]{17}\] with BSSID\[[0-9a-fA-F:]{17}\]' % wlan_conf['ssid']
        exp_11gn = 'WLAN\[%s\] has been deployed on radio \[11g/n\] of AP\[[0-9a-fA-F:]{17}\] with BSSID\[[0-9a-fA-F:]{17}\]' % wlan_conf['ssid']
        
        (res, info) = _check_event(exp_11an, e_list)
        if not res:
            return ('FAIL', info)
        
        (res, info) = _check_event(exp_11gn, e_list)
        if not res:
            return ('FAIL', info)
        
        logging.info('wlan %s set is successful' % wlan_conf)
        return ('PASS', 'wlan %s set is successful' % wlan_conf)
    except Exception, e:
        logging.error(e.message)
        return ('FAIL', e.message)

def do_clean_up():
    clean_up_rat_env()

def _check_event(expr, e_list):
    fnd = False
    for e in e_list:
        if re.match(expr, e[3], re.I):
            fnd = True
            break
    if fnd:
        logging.info('event %s has reported' % expr)
        return (True, '')
    else:
        return (False, "event %s hasn't been reported correctly" % expr)
    
            
def main(**kwargs):
    cfg = {'on':False,
           'off':False,
           'specific':False,
           }
    cfg.update(kwargs)
    try:
        (zd, wlan_cfg) = do_config(cfg)
        return do_test(zd, wlan_cfg)        
    except Exception, e:
        return ('FAIL', e.message)
    finally:
        do_clean_up()

