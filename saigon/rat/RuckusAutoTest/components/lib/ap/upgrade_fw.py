import shutil
import logging

from RuckusAutoTest.common.utils import remove_file as delete_file
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.fm.lib_FM import wait4_ap_stable

#--------------------------------------------
#     Public Methods
#--------------------------------------------
def upgrade_fw_via_cli(ap_cli, fw_upgrade_cfg, timeout = 360):
    '''
    Upgrade firmware via CLI, the procedures are:
    1. update firmware setting based on specified config
    2. For manual upgrade: 
        a. upgrade firmware, wait for upgrading
        b. reboot AP.
    3. For auto upgrade:
        Do nothing after updated setting.
    '''    
    
    res_d = {}
    try:
        ap_cli.change_fw_setting(fw_upgrade_cfg)
        
        updated_fw_cfg = ap_cli.get_fw_upgrade_setting()
        res_setting_d = {}
        
        for key, value in fw_upgrade_cfg.items():
            is_pass = False
            if fw_upgrade_cfg['proto'].lower()!= 'ftp' and key in ['user', 'password']:
                is_pass = True
            if not fw_upgrade_cfg['auto'] and key in ['interval','boottime']:
                is_pass = True
                
            if not is_pass:
                if updated_fw_cfg.has_key(key):
                    new_value = str(updated_fw_cfg[key]).strip()
                    value = str(value).strip()
                    if key in ['firstcheck', 'interval']:
                        #new value origin is '10  (minutes)', we only get 10.
                        new_value = new_value.split(' ')[0]                                                
                    if value.lower() != new_value.lower():
                        res_setting_d[key] = 'Expected: %s, Actual: %s' % (value, updated_fw_cfg[key])
        
        if res_setting_d:    
            res_d['UpdateSetting'] = res_setting_d         
            logging.warning('Firmware upgrade setting were not updated successfully: %s' % (res_setting_d))
            
        logging.debug('Expected setting: %s' % fw_upgrade_cfg)
        logging.debug('Updated setting: %s' % updated_fw_cfg)
        
        if not (fw_upgrade_cfg.has_key('auto') and fw_upgrade_cfg['auto']):
            res = ap_cli.update_ap_fw(timeout = timeout)            
            #Other error will raise exception.
            if 'no update' in res.lower():
                res_d['Upgrade'] = "No Upgrade. AP is running an expected image"
                            
    except Exception, e:
        if 'no update' in e.__str__().lower():
            err_msg = 'Exception: No need to do upgrade.'
        else:
            err_msg = 'Fail to upgrade to firmware version: %s. Error: %s' % (fw_upgrade_cfg['control'], e.__str__())
        
        res_d['Error'] = err_msg
        logging.warning(err_msg)
    
    return res_d  

def upgrade_fw_via_gui(ap_webui, upgrade_cfg):
    '''
    Upgrade firmware via AP web UI, the procedures are:
    1. For manual upgrade:
        a. Updated setting in web UI and click "Perform upgrade"
        b. Wait for upgrading
        c. Reboot AP
    2. For auto upgrade:
        a. Updated setting in web UI and click "Save parameters only"
    '''
    errmsg = ''
    ap_webui.start(15)
    try:
        #import pdb
        #pdb .set_trace()
        ui_cfg = _convert_upgrade_cfg_for_gui(upgrade_cfg)
        ts, msg = lib.ap.fwup.set_cfg(ap_webui, ui_cfg)
        logging.info(msg)
        
        # TODO: Whether we treat a situation "Unecessary to do upgrade" as failed case?
        # We may see this problem if the upgrade fw is the same with current fw on AP
        # ts = 3, Got alert pop up: A firmware upgrade is unnecessary.  Please click "OK" to continue.
        if lib.ap.fwup.UPGRADE_STATUS_FAILED == ts or lib.ap.fwup.UPGRADE_STATUS_TIMEOUT == ts or lib.ap.fwup.UPGRADE_STATUS_UNNECESSARY == ts:
            errmsg = msg
    except Exception, e:
        errmsg = ('Fail to upgrade to firmware version: %s. Error: %s' %
                     (upgrade_cfg['control'], e.__str__()))

        logging.warning(errmsg)

    ap_webui.stop()
    
    return errmsg

def create_control_file(ap_cli, fw_file_path):
    '''
    This function is to use RuckusAP instance to create a ctrl file to do
    upgrade and restore firmware.
    '''    
    try:
        fw_ctrl_file_path = ap_cli.create_ctrl_file(fw_file_path)
        return fw_ctrl_file_path
    except Exception, e:
        err_msg = "Error during creating control file for %s. Error is %s" % (fw_file_path, e.__str__())
        logging.warning(err_msg)  
        
def copy_file(dest_file_path, source_file_full_path, new_file_name):
    '''
    This function is copy source file include path to destination root path and rename as new_file_name. 
    '''    
    try:
        shutil.copyfile(source_file_full_path, '%s\\%s' % (dest_file_path, new_file_name))
    except Exception, e:
        # ignore error if cannot delete the file in the root_path
        err_msg = 'Warning: Can not copy file %s to %s. Error is %s' % (new_file_name, dest_file_path, e.__str__())
        logging.info(err_msg)
        return err_msg
    
def remove_file(source_file_path, remove_file_name):
    '''
    This function is to remove specified file from source file path.
    '''    
    try:
        # remove ctrl files
        delete_file('%s\\%s' % (source_file_path, remove_file_name))        
    except Exception, e:
        err_msg = 'Warning: Can not remove file %s from %s. Error is %s' % (remove_file_name, source_file_path, e.__str__())
        logging.info(err_msg)
        return err_msg    
    
def verify_ap_fw_version(ap_cli, ap_cli_cfg, expect_fw_version):
    '''
    This version is to make sure AP fw version is the expected one after
    upgrading/restoring
    '''
    _wait_ap_stable(ap_cli_cfg)
    err_msg = ''
    cur_version = ap_cli.get_version().strip()
    expected_version = expect_fw_version
    logging.info('Current version: %s; Expected version: %s' % (cur_version, expected_version))
    
    if expected_version == cur_version:
        pass_msg = 'The AP was upgraded to version %s successfully.' % (expected_version)
        logging.info(pass_msg)        
    else:
        err_msg = 'The AP was not upgraded to version %s successfully. Expected Version = %s, Actual Version = %s'\
                    % (expected_version, expected_version, cur_version)        
        logging.warning(err_msg)
        
    return err_msg

def get_verify_data(ap_cli):
    data_d = {}
    
    fw_setting_before = ap_cli.get_fw_upgrade_setting()
    if fw_setting_before.has_key('running_image'):
        data_d['running_image'] = fw_setting_before['running_image']
    data_d['Model'] = ap_cli.get_ap_model()
    data_d['Mac'] = ap_cli.get_base_mac()
    data_d['profile'] = ap_cli.get_profile()
    data_d['FixedCountryCode'] = ap_cli.get_fixed_country_code()
    
    return data_d

#--------------------------------------------
#     Private Methods
#--------------------------------------------
       
def _wait_ap_stable(ap_cli_cfg):
    '''
    This function is to check CPU usage of AP and wait for each ready to test.
    Note: if provide username password, this function will use that username/password
    instead of username/password from ap instance to connect to AP and monitor its CPU usage.
    '''
    # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
    MONITOR_CPU_USAGE = 0

    monitor_cpu_cfg= {
        #'config': config,
        'monitor': MONITOR_CPU_USAGE,
        'threshold': 40, # default % CPU Usage
        'timeout': 20, # in minute
        'interval': 2,
        'times_to_check': 3,
    }

    monitor_cpu_cfg.update({'config': ap_cli_cfg})
    if wait4_ap_stable(**monitor_cpu_cfg):
        msg = 'CPU of AP %s looks free for the test' % ap_cli_cfg['ip_addr']
        logging.info(msg)
    else:
        msg = 'WARNING: The CPU usage of AP %s is still too high' % ap_cli_cfg['ip_addr']
        logging.warning(msg)
      
def _convert_upgrade_cfg_for_gui(upgrade_cfg):
    '''
    Convert config dict:
    1. convert dict keys with gui keys
    2. update auto_upgrade values, from True/False to Enabled/Disabled
    3. If auto upgrade:
        a. Update interval values as hours/weeks.
        b. boottime default is 'Any Time'
    4. If manual upgrade:
        a. remove interval and boottime, don't need to set them.
    '''
    keys_mapping = {'control':'ctrl_file_name',
                    'proto': 'protocol',
                    'host': 'ip_addr',
                    'port': 'port',
                    'user': 'username',
                    'password': 'password',
                    'auto': 'auto_upgrade',
                    'interval': 'interval',
                    'boottime': 'boottime'
                    }
    
    ui_cfg = {}
    for key, gui_key in keys_mapping.items():
        if upgrade_cfg.has_key(key):
            ui_cfg [gui_key] = upgrade_cfg[key]
            if key == 'control':
                if upgrade_cfg['proto'].lower() == 'http':
                    ui_cfg['url'] = upgrade_cfg[key]
                elif upgrade_cfg['proto'].lower() == 'local':
                    ui_cfg['local_file_name'] = upgrade_cfg[key]
    
    if ui_cfg.has_key('auto_upgrade') and ui_cfg['auto_upgrade']:
        ui_cfg['auto_upgrade'] = 'enabled'
        #For auto upgrade, convert interval from minutes to hour or weeks.
        ui_cfg['interval'] = _convert_interval_for_gui(ui_cfg['interval'])
        if not ui_cfg.has_key('boottime') or not ui_cfg['boottime']:
            ui_cfg['boottime'] = 'Any Time'
    else:
        ui_cfg['auto_upgrade'] = 'disabled'
        if ui_cfg.has_key('interval'):
            ui_cfg.pop('interval')
        if ui_cfg.has_key('boottime'):
            ui_cfg.pop('boottime')  
            
    return ui_cfg

def _convert_interval_for_gui(interval):
    '''
    Convert interval from minutes to webui values: hours and week.
    Webui only support 1,4,12,24 Hours and 1,2,4,4 weeks.
    '''
    interval_in_hours = int(interval)/60
    new_interval = 0
    unit = ''
    
    if interval_in_hours in [1,4,12,24]:
        if interval_in_hours == 1:
            unit = 'Hour'
        else:
            unit = 'Hours'        
        new_interval = interval_in_hours
    elif interval_in_hours > (24*7):
        interval_in_weeks = interval_in_hours/(24*7)
        
        if interval_in_weeks in [1,2,4]:
            if interval_in_weeks == 1:
                unit = 'Week'
            else:
                unit = 'Weeks'
                
            new_interval = interval_in_weeks
        
    webui_interval = ''
    if new_interval and unit:
        webui_interval = '%s %s' % (new_interval,unit)
    else:
        raise Exception('In GUI, only support: 1,4,12,24 Hours and 1,2,4 weeks.')
    
    return webui_interval