# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
'''
   @author: An Nguyen, an.nguyen@ruckuswireless.com
   @since: Aug, 2011
   
   This module is supported to test upgrade between to expected build in a number of cycles.
   Support on build streams: 9.1.0.0.x, 9.2.0.0.x and 9.1.1.0.x
   Upgrade between the build stream may cause the FAIL be cause the mesh APs could not reconnect if ZD be set factory

   tea.py u.zd.verify_upgrade
               | [ip_add='ip address of ZD', username='login user name', password='login password']
               | [img_list=['list of image file with .img extension']]
               | [loop_time='number test cycles']
               | [debug=True|False]

   Examples:
       tea.py u.zd.verify_upgrade # execute the test with parameter be defined in file
       tea.py u.zd.mesh.verify_upgrade img_list=['c:\\tmp\\zd3k_9.1.0.0.28.img','c:\\tmp\\zd3k_9.2.0.0.89.img'] # execute with user input
       

'''
import time
import pprint
import logging

from RuckusAutoTest.tests.zd import Test_Methods as tmethod
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

#
# test parameters, will be updated if there is any user input
#

zd_cfg = {'ip_addr': '192.168.0.2',
          'username': 'admin',
          'password': 'admin'}

img_cfg = {'img_list': ['\\\\172.18.35.32\\Builds\\ZD3k\\zd3k_9.1.0.0.38.ap_9.1.0.0.38.img',
                        '\\\\172.18.35.32\\Builds\\ZD3k\\zd3k_9.2.0.0.80.ap_9.2.0.0.80.img']}

test_cfg = {'loop_time': 1}

#
# Private functions
#

def _init_parameters(kwa):
    conf = {}
    conf.update(zd_cfg)
    conf.update(img_cfg)
    conf.update(test_cfg)
    conf.update(kwa)
    logging.info('Test parameters:')
    pprint.pprint(conf)
    
    conf['zd'] = create_zd_by_ip_addr(conf['ip_addr'], conf['username'], conf['password'])
    conf['expected_tree'] = _get_mesh_tree(conf['zd'])
         
    return conf 

def _get_mesh_tree(zd):
    aps_info = lib.zd.ap.get_all_ap_info(zd, pause=5)
    pprint.pprint(aps_info)
    mesh_tree = tmethod.emesh.detect_mesh_tree(aps_info.values())
    
    return mesh_tree

def _verify_mesh_tree(expected_tree, exist_tree):
    return exist_tree == expected_tree

def _upgrade_sw(zd, **kwargs):
    conf = {'img_file_path': '',
            'do_backup': True}
    conf.update(kwargs)
    
    if conf['do_backup']:
        _backup_config(zd)
    
    start_time = time.time()
    logging.info('Upgrade ZoneDirector by using image file "%s"' % conf['img_file_path'])
    _upgrade_img(zd, conf['img_file_path'])
    zd.update_feature()
    upgrade_time = time.time() - start_time
    
    return upgrade_time

def _upgrade_img(zd, img_file_path): 
    zd._upgrade(img_file_path)
    
def _backup_config(zd):
    lib.zd.bkrs.backup(zd)

def _upgrade_zd(zd, img_path):
    try:
        elapsed = _upgrade_sw(zd, **{'img_file_path': img_path})
        return (1, 'ZD upgrade successfully to build "%s" after %s seconds' % (zd.get_version(), elapsed))
    except Exception, e:
        if "Error: AP upgrading failed. Timeout" in e.message:
            return (0, e.message)
        else:
            return (-1, e.message)
    
def _verify_zd_info(conf):
    logging.info('Verify ZD mesh tree information:')
    logging.info('ZD version is: %s' % conf['zd']._get_version()['version'])
    exist_tree = _get_mesh_tree(conf['zd'])
    if _verify_mesh_tree(conf['expected_tree'], exist_tree):
        logging.info('The mesh tree is same as expected:')
        pprint.pprint(exist_tree)
    else:
        logging.info('The current mesh tree is:')
        pprint.pprint(exist_tree)
        logging.info('not same as expected:')
        pprint.pprint(conf['expected_tree'])
        
#
# Test functions
#
    
def do_config(cfg):
    _cfg = _init_parameters(cfg)    
       
    return _cfg

def do_test(cfg):
    loop = 0
    while loop < cfg['loop_time']:
        logging.info('[LOOP %s] Test ZD upgrade for list %s' % ((loop+1), cfg['img_list']))
        for img_path in cfg['img_list']:
            res, msg = _upgrade_zd(cfg['zd'], img_path)
            logging.info('[Upgrade result]: %s' % msg)
            if res in [0, 1]:
                _verify_zd_info(cfg)
            if res in [-1, 0]:
                return('FAIL', msg)
              
        loop +=1
        
    passmsg = 'The upgrade test for image list %s is successful with %s cycle(s)'
    passmsg =  passmsg % (cfg['img_list'], cfg['loop_time'])
    return('PASS', passmsg)
        
def do_clean_up():
    clean_up_rat_env()

def main(**kwa):
          
    tcfg = do_config(kwa)
    pprint.pprint(type(tcfg['img_list']))
    res, msg = do_test(tcfg)
    do_clean_up()

    return (res, msg)
    