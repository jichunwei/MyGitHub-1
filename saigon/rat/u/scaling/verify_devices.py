'''
Created on Oct 5, 2010

@author: webber.lin

Purpose: Tea program training only.  
This script is to verify all devices connected to FM (192.168.30.252)

Ex: 

tea.py u.scaling.verify_devices fm_ip_addr=192.168.30.252

'''

import logging,time
from pprint import pformat
from RuckusAutoTest.components import (
                                       create_fm_by_ip_addr,
                                       create_zd_by_ip_addr,
                                       #create_ruckus_ap_by_ip_addr, 
                                       create_ap_by_model,
                                       clean_up_rat_env)

def get_device_ip_addr_and_model_name(info_list):
    ''' this function will return one or more ip address'''
    ip_list=[]
    for d in info_list:
        if d['ip_addr']:
            ip_list.append(dict(ip_addr = d['ip_addr'],model = d['model']))
    return ip_list

def turnOn_zd(zd_ip_addr):
    try:
        create_zd_by_ip_addr(ip_addr=zd_ip_addr)
        logging.info('create ZD (%s) successfully' % zd_ip_addr)
    except:
        logging.error('create ZD (%s) failed' % zd_ip_addr)
    
def turnOn_ap(ap_ip_addr, ap_model):
    
    try:
        ap = create_ap_by_model(ip_addr=ap_ip_addr,model=ap_model)
        logging.info('create AP (%s) successfully' % ap_ip_addr)
        ap.start()
    except:
        logging.error('create AP (%s) failed' % ap_ip_addr)


def do_config(cfg):
    ''' configure FM '''
    logging.info('FM information')
    p = dict(
        fm_ip_addr = '192.168.30.252',
    )
    p.update(cfg)
    logging.info('FM IP information: %s' % p['fm_ip_addr'])
    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    logging.info('Create FM Successfully:(obj) %s' % p['fm'])
    return p


def do_test(cfg):
    
    logging.debug('\n%s' % pformat(cfg))
    #get device information: zd and ap
    #format: list of dictionary 
    try:
        zd_info_list=cfg['fm'].get_all_zds() #get zd information 
        ap_info_list=cfg['fm'].get_all_aps() #get ap information
        zd_ip_list = get_device_ip_addr_and_model_name(zd_info_list)
        logging.debug('%s' % zd_ip_list)
        for zd_ip in zd_ip_list:
            turnOn_zd(zd_ip['ip_addr'])
            time.sleep(5)
        
        ap_ip_list = get_device_ip_addr_and_model_name(ap_info_list)
        logging.debug('%s' % ap_ip_list)
        for ap_ip in ap_ip_list:
            turnOn_ap(ap_ip['ip_addr'],ap_model=ap_ip['model'])
            time.sleep(5)
        
        return dict(result='PASS', message='All devices are accessed' )
    except:
        return dict(result='FAIL',message='Unable to open WebUIs')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
