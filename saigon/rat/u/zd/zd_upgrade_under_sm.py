'''
Created on 2010-8-9

@author: cwang@ruckuswireless.com

tea.py u.zd.zd_upgrade_under_sm
'''
import time
import os
import logging
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.common.DialogHandler import (
    BaseDialog,
    DialogManager
    )
from contrib.download import image_resolver as imgres
from RuckusAutoTest.components.lib import FeatureUpdater
default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(**kwargs):
    args = dict()
    args.update(kwargs)
    active_zd = create_zd_by_ip_addr(**default_cfg)
    default_cfg['ip_addr'] = '192.168.0.3'
    standby_zd = create_zd_by_ip_addr(**default_cfg)
    
    return (active_zd, standby_zd)

def do_test(active_zd, standby_zd, **kwargs):
    new_conf =  {'wireless1_enabled':True,
                 'dhcp_enabled':True} 
    cfg = dict(default = True)
    cfg.update(kwargs)
    
    _downgrade_from_active_zd(active_zd, standby_zd, default = cfg['default'], new_conf = new_conf)
    

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    active_zd, standby_zd = do_config(**kwargs)
#    import pdb
#    pdb.set_trace()
    try:
        do_test(active_zd, standby_zd, **kwargs)
            
    finally:
        do_clean_up()
        pass

def _start_dialog_manger(active_zd):
    dlg_manager = DialogManager()

    dlg1 = None
    dlg2 = None

    # Handle IE browser
    if (active_zd.conf['browser_type'] == 'ie'):
        dlg1 = BaseDialog("Security Alert", "You are about to view pages over a secure", "OK")
        dlg2 = BaseDialog("Security Alert", "The security certificate was issued by a company", "&Yes")

    # Handle Firefox browser
    elif (active_zd.conf['browser_type'] == 'firefox'):
        dlg1 = BaseDialog("Website Certified by an Unknown Authority", "", "", "{ENTER}")
        dlg2 = BaseDialog("Security Error: Domain Name Mismatch", "", "", "{TAB}{TAB}{ENTER}")

    dlg_manager.add_dialog(dlg1)
    dlg_manager.add_dialog(dlg2)

    # Start dialog manager to manage the two dialogs that we have added
    dlg_manager.start()
    return dlg_manager


def _downgrade_from_standby_zd(standby_zd, conf, default = False, new_conf = {}):
    _update_feature(standby_zd, conf)
    if default:
        standby_zd._setup_wizard_cfg({}, new_conf)


def _downgrade_from_active_zd(active_zd, standby_zd, default = True, wait_for_time = 180, new_conf = {}):
    conf = dict(image_file_path = 'D:\\p4\\tools\\rat-branches\\saigon\\rat\\zd3k_8.2.0.1.8.ap_8.2.0.1.8.img')
    fname = conf['image_file_path']
    filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
#    img_filename = imgres.get_image(fname, filetype = filetype)
    img_path_file = os.path.realpath(fname)
            
    try:                
        dialog_manager = _start_dialog_manger(active_zd)
        active_zd._upgrade_zd(img_path_file, default = default)
        time.sleep(wait_for_time)
        _shut_down_dlg_manager(dialog_manager)
        conf = dict(zd_build_stream = '8.2.0.1')
        _update_feature(active_zd, conf)
        active_zd._check_upgrade_sucess(default = default, new_conf = new_conf)                
        active_zd.s.refresh()                
        active_zd.login()
        msg = 'The upgrade process worked successfully'
        logging.info(msg)
        
        _downgrade_from_standby_zd(standby_zd, conf, default, new_conf)
         
    except Exception, e:
        errmsg = '[Upgrade error]: %s' % e.message
        logging.warning(errmsg)
    

def _update_feature(zd, conf):
    if conf['zd_build_stream']:
        FeatureUpdater.FeatureUpdater.notify(zd, conf['zd_build_stream'])
            
def _shut_down_dlg_manager(dlg_manager):
    
    dlg_manager.shutdown()

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)