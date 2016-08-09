# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
   Description: Verify the mesh tree in mesh summary table in DashBoard page
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010
   
   tea.py u.zd.zd_dashboard_man |[ip_addr=ZD IP address][username=ZD login user name][password=ZD login password]
   
   Ex: tea.py u.zd.zd_dashboard_man ip_addr=192.168.0.2
"""
   
import time
import copy
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(
    ip_addr = '192.168.0.2',
    username = 'admin',
    password = 'admin',
)

def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('ip_addr'))

    return _cfg

def do_test(cfg):
    # Unit test for Dashboard management
    zd = cfg['zd']
    lib.zd.dboard.add_mesh_topology_widget_to_dashboard(zd)
    time.sleep(5)
    
    ap_info_list = lib.zd.ap.get_all_ap_info(zd).keys()
    mtree = lib.zd.dboard.detect_mesh_tree(zd, ap_info_list)
    print 'Mesh tree on DashBoard:\n %s' % pformat(mtree, 4, 20)
    
    cfg['result'] = 'PASS'
    cfg['message'] = 'Mesh tree on DashBoard: %s' % mtree
    return cfg

def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    tcfg = do_config(kwa)

    res = None
    try:
        res = do_test(tcfg)

    except Exception, ex:
        print ex.message

    do_clean_up(tcfg)

    return res