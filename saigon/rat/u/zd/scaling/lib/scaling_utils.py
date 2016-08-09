"""
Created on 2010-2-9
@author: cwang@ruckuswireless.com
"""
import logging

from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC

def resolve_real_path(img_path):
    import os
    fname = os.path.realpath(img_path)
    logging.info('image file path [%s] ' % fname)
    if os.path.isfile(fname) :
        return fname
    else:
        raise Exception(' the file [%s] is\'t exists' % fname)
    
def create_zd(**kwargs):
    fcfg = dict(ip_addr='192.168.0.2', username='admin', password='admin')
    fcfg.update(kwargs)
    zd = ZoneDirector(fcfg)
    return zd

def create_zd_cli(**kwargs):
    fcfg = dict(ip_addr='192.168.0.2', username='admin', password='admin', shell_key='!v54!')
    fcfg.update(kwargs)
    zdcli = ZoneDirectorCLI(fcfg)
    return zdcli

def create_station(**kwargs):
    fcfg = dict(sta_ip_addr='192.168.1.11')
    fcfg.update(kwargs)
    station = RemoteStationWinPC(fcfg)
    return station

def halt(debug=False):
    if debug :
        import pdb
        pdb.set_trace()
        
        
def update_keywords(s, d):
    for k, v in s.items():
        if d.has_key(k):
            d[k] = v
