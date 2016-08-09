import os
import copy
import re
import time
import logging
import datetime
import traceback
from pprint import pformat

from RuckusAutoTest.common.utils import (
        log, log_trace, log_cfg, try_interval, try_times, to_str_dict_items
)
from RuckusAutoTest.components import (
    create_com,
    create_ruckus_ap_by_ip_addr,
    create_server_by_ip_addr
)

FailMessages = {
    'ApNotFound':           'AP (%s) is found on FlexMaster but not in the testbed',
    'VersionMismatch':      'Software versions are mismatch. FM displays "%s" whereas AP (%s) displays "%s"',
    'ModelMismatch':        'Models are mismatch. FM displays "%s" whereas AP (%s) displays "%s"',
    'NumberOfApsMismatch':  'Number of APs is mismatch. FM displays %s whereas numbers of AP in testbed is %s',

    'CannotGetModelInfo':   'Cannot get the device model on AP (%s)',
    'SearchResultMismatch': 'The expected item (Serial#= %s) is not found on search results',
    'AttribValueMismatch':  'Attribute "%s" is mismatch. FM displays "%s" whereas AP (%s) displays "%s"',
    'SearchStringMismatch': 'The expected search string is "%s" whereas the actual is "%s"',

    'NoApFoundWithInputModel': 'No ap with model "%s" found',
    'FirmwareMismatch':        'Firmware mismatch (AP %s:%s; Expected: %s). Upgrade task reports %s',
    'ApUpgradedFmReportsFail': 'AP firmwares are upgraded successfully but FM reports failed',
    'ApCfgUpgradedFmReportsFail': 'AP configuration are upgraded successfully but FM reports failed',
    'ApRebootedFmReportsFail': 'APs have just rebooted successfully but FM reports failed',
    'ApFactoryResetedFmReportsFail': 'APs have just factory-reset successfully but FM reports failed',
    'ApFailedToReboot': 'AP %s failed to reboot. Uptime is %s. FM reports %s',
    'ApFailedToFactoryReset': 'AP %s failed to reboot. Current device name is %s. FM reports %s',
  }


def wait4_ap_up(**kwa):
    '''
    kwa:
    - config
    - timeout: in mins
    return:
    - boolean
    '''
    _kwa = {
        'config': get_ap_default_cli_cfg(),
        'timeout': 4
    }
    _kwa.update(kwa)

    # Wait for the ap to be up before testing it
    logging.info('Wait for the AP %s to be up after rebooting' % \
                 _kwa['config']['ip_addr'])
    end_time = time.time() + (_kwa['timeout'] * 60)
    ap_cli = None
    while time.time() < end_time:
        try:
            ap_cli = create_ruckus_ap_by_ip_addr(**_kwa['config'])
            ap_cli = None
            return True
        except:
            del ap_cli
            ap_cli = None
        time.sleep(6)
    return False


def wait_for_ap_go_into_reboot_status(**kwa):
    '''
    This function is to wait for AP go into reboot status
    kwa:
    - config
    - timeout: in mins
    return:
    - boolean
    '''
    _kwa = {
        'config': get_ap_default_cli_cfg(),
        'timeout': 3
    }
    _kwa.update(kwa)

    # Wait for the ap to be up before testing it
    logging.info('Wait for the AP %s to be up after rebooting' % \
                 _kwa['config']['ip_addr'])
    end_time = time.time() + (_kwa['timeout'] * 60)
    ap_cli = None
    reboot_status = False
    while time.time() < end_time and not reboot_status:
        try:
            ap_cli = create_ruckus_ap_by_ip_addr(**_kwa['config'])
            ap_cli = None
            time.sleep(6)
        except:
            del ap_cli
            ap_cli = None
            reboot_status = True

    if reboot_status:
        return True
    else:
        return False


def _reboot_ap(**kwa):
    '''
    OBSOLETE: Use reboot_ap instead
    kwa:
    - config
    return:
    - boolean
    '''
    logging.info('Rebooting the AP %s' % kwa['config']['ip_addr'])
    ap_cli = None
    try:
        ap_cli = create_ruckus_ap_by_ip_addr(**kwa['config'])
        ap_cli.reboot()
        del ap_cli
        return True
    except:
        log_trace()
        del ap_cli
    return False


def reboot_ap(cfg):
    ''' most of the time, cfg just needs 'ip_addr' of AP '''
    return _reboot_ap(config = cfg)


def set_ap_mgmt_to_snmp(**kwa):
    '''
    kwa:
    - ap
    '''
    kwa['ap'].set_mgmt_type(**{'type': 'snmp'})
    time.sleep(6) # wait a bit


def set_ap_mgmt_to_auto(**kwa):
    '''
    kwa:
    - ap
    '''
    kwa['ap'].set_mgmt_type(**{'type': 'auto'})
    time.sleep(2)


UPTIME_SEP = dict(day = 'days', hr = 'hours', min = 'minutes', sec = 'seconds')

def convert_str_to_time_delta(**kwa):
    '''
    - don't pass the extra 's' in 'mins' to this function
    kwa:
    - str
    - seperators
    return:
    - a dict
    '''
    time = kwa['str']
    uptime = {}
    for sep in kwa['seperators'].keys():
        r = re.search('(\d+) %ss?' % sep, time) # ex: '(\d+) secs?'
        if r and r.group(1): uptime[kwa['seperators'][sep]] = int(r.group(1))

    logging.debug('Uptime as dict: %s' % uptime)
    return datetime.timedelta(**uptime)


def get_up_time(str):
    return convert_str_to_time_delta(**dict(str = str, seperators = UPTIME_SEP))


def clear_persistent_cfg(**kwa):
    '''
    - create a RuckusAP CLI instance
    - goto linux shell and delete persistence_data file
    kwa:
    - config: AP's config
    '''
    ap_cli = create_ruckus_ap_by_ip_addr(**kwa['config'])
    ap_cli.clear_persistent_cfg()
    del ap_cli


def get_ap_default_cli_cfg():
    '''
    Define a defaul config for AP
    '''
    config = {
              'ip_addr' : '192.168.0.1',
              'username': 'super',
              'password': 'sp-admin',
              'port'    : 23,
              'telnet'  : True,
              'timeout' : 360, # sec
    }
    return config


def set_ap_serial(**kwa):
    '''
    This function is to change serial number of an AP
    kwa:
    - serial: 'A new serial number'
    - config: {
        'ip_addr'
        'username'
        password
        timeout:
    }
    '''
    serial = kwa['serial']
    config = get_ap_default_cli_cfg()
    config.update(kwa['config'])

    logging.info('Setting a new serial %s for AP %s' % (serial, config['ip_addr']))

    tries = 1
    while tries <= 5:
        try:
            ap_cli = create_ruckus_ap_by_ip_addr(**config)
            ap_cli.set_serial(serial)
            new_serial = ap_cli.get_serial()
            break
        except Exception:
            logging.info('Error: %s. Trying to set a new serial %s times...' %
                         (traceback.format_exc(), tries))
            time.sleep(60)
            tries += 1
            if tries > 5:
                logging.info('Cannot set new serial for AP %s', config['ip_addr'])
                return False

    del ap_cli

    if  new_serial != serial:
        logging.info('Cannot set the new serial %s for AP %s' % (serial, config['ip_addr']))
        return False

    logging.info('Set the new serial %s for AP %s successfully' % (serial, config['ip_addr']))
    return True


def set_ap_factory(**kwa):
    '''
    Set default factory for the AP.
    kwa:
    - config: {
        ip_addr
        username
        password
        timeout
    }
    '''
    config = get_ap_default_cli_cfg()
    config.update(kwa['config'])
    DEFAULT_USER = 'super'
    DEFAULT_PWD = 'sp-admin'
    timeout = int(config['timeout']) / 60 if config.has_key('timeout') else 6

    #Sometimes, the paramiko lib has problem so we retry several time if any error
    tries, ap_cli = 1, None
    while tries <= 5:
        try:
            ap_cli = create_ruckus_ap_by_ip_addr(**config)
            ap_cli.set_factory()
            ######################################
            # NOTE: If the username/pwd are different from default, we need to re-set it
            #       back to default user/pwd before calling RuckusAP.reboot() function.
            #       It is because after calling setfactory() func to do set factory for AP,
            #       then call reboot() function to do set factory. The reboot function
            #       will use the new user/pass, which you establish RuckusAP session, to detect the
            #       AP ready or not. But after set factory, the AP back to use default user/pwd.
            # IMPORTANT: this function may fail if the AP has user/pwd as persistent data and
            # the persistent user/pwd are different from the default user/pwd.
            ######################################
            if 'username' in kwa['config'] and kwa['config']['username'] != DEFAULT_USER:
                ap_cli.set_cfg_info(username = DEFAULT_USER)
                config['username'] = DEFAULT_USER
            if 'password' in kwa['config'] and kwa['config']['password'] != DEFAULT_PWD:
                ap_cli.set_cfg_info(password = DEFAULT_PWD)
                config['password'] = DEFAULT_PWD
            ap_cli.reboot(timeout * 60, telnet = False)
            break
        except Exception:
            log_trace()
            logging.info('Trying to set factory %s times' % tries)
            tries += 1
            time.sleep(30)
            if tries > 5:
                del ap_cli
                logging.info('Cannot set factory default for AP %s', config['ip_addr'])
                return False

    # Sometime ap is rebooted after factory setting but it reboots again so
    # sleep a little time before do check whether AP is ready or not. And if
    # the AP rebooted again the function wait4_ap_up(...) will wait
    logging.info('Sleeping a moment to wait for AP enter reboot status')
    time.sleep(30)

    del ap_cli
    if not wait4_ap_up(**{'config': config, 'timeout':timeout}):
        logging.info('Set factory default for AP %s but it cannot boot up', config['ip_addr'])
        return False

    logging.info('Sleeping a moment to wait for AP ready for the test')
    time.sleep(30)

    logging.info('Set default factory for AP %s successfully' % config['ip_addr'])
    return True


def get_ap_serial(**kwa):
    '''
    This function is to change serial number of an AP.
    kwa:
     - config: {
        ip_addr
        username
        password
        timeout
    }
    '''
    config = get_ap_default_cli_cfg()
    config.update(kwa['config'])
    #Sometimes, the paramiko lib has problem so we retry several time if any error
    tries = 1
    while tries <= 5:
        try:
            ap_cli = create_ruckus_ap_by_ip_addr(**config)
            serial = ap_cli.get_serial()
            break
        except Exception:
            logging.info('Error: %s' % traceback.format_exc())
            logging.info('Trying to get AP serial %d times' % tries)
            tries += 1
            time.sleep(60)
            if tries > 5:
                logging.info('Cannot get AP serial of AP %s', config['ip_addr'])
                raise Exception('Cannot get AP serial of AP %s', config['ip_addr'])

    logging.info('AP %s has serial %s' % (config['ip_addr'], serial))
    del ap_cli
    return serial


def init_aliases(**kwa):
    '''
    WARNING: obsoleted by init_coms()
    - init common used aliases for test classes
    kwa:
    - testbed
    '''
    class Aliases:
        tb = kwa['testbed']
        fm, aps = tb.components['FM'], tb.components['APs']
        sfm, lfm, cfm = fm.selenium, fm.resource['Locators'], fm.resource['Constants']
        clients = tb.components.get('Clients', [])
    return Aliases()


def init_coms(obj, cfg):
    '''
    dynamically adding aliases/components for test object
    this function is straight forward, so look at it to know the results
    cfg:
        tb: required
        ap_ip, dv_ip, srv_cfg: optional
        ap_ips: optional
    '''
    logging.info('Initialize all the required components')
    log_cfg(cfg, 'Components')

    obj.tb = tb = cfg['tb']
    obj.fm = tb.components['FM']
    obj.aps = tb.components['APs']
    obj.zds = tb.components.get('ZDs', [])
    obj.clients = tb.components.get('Clients', [])

    # additional for device view tests: target aps/ap and dv
    obj.ap = obj.dv = obj.ap_cli = obj.srv_cli = obj._aps = obj.zd = None

    # TODO: should minimize the try_interval for the error cases only
    for t in try_interval(timeout = 180, interval = 10):
        try:
            if 'ap_ip' in cfg and obj.ap is None:
                logging.info('Get AP Web UI (%s) from testbed' % cfg['ap_ip'])
                obj.ap = tb.getApByIp(cfg['ap_ip'])

            if 'ap_ips' in cfg and not obj._aps:
                logging.info('Get AP Web UIs from testbed: %s' % pformat(cfg['ap_ips']))
                obj._aps = [tb.getApByIp(ap_ip) for ap_ip in cfg['ap_ips']]

            if 'dv_ip' in cfg and obj.dv is None:
                logging.info('Get the Device View (%s) from Flex Master' % cfg['dv_ip'])
                obj.dv = obj.fm.get_device_view(ip = cfg['dv_ip'])

            if 'apcli_cfg' in cfg and obj.ap_cli is None:
                #logging.info('Connect to AP CLI (%s)' % cfg['apcli_cfg']['ip_addr'])
                obj.ap_cli = create_ruckus_ap_by_ip_addr(**cfg['apcli_cfg'])

            if 'srv_cfg' in cfg and obj.srv_cli is None:
                logging.info('Connect to Linux Server (%s)' % cfg['srv_cfg']['ip_addr'])
                obj.srv_cli = create_server_by_ip_addr(**cfg['srv_cfg'])

            if 'zd_ip' in cfg and obj.zd is None:
                logging.info('Get ZD Web UI (%s) from testbed' % cfg['zd_ip'])
                obj.zd = tb.get_zd_by_ip(cfg['zd_ip'])

            break
        except Exception, e:
            log_trace()
            logging.info('Error: %s. Try again...' % e.__str__())


def wait4_ap_stable(**kwa):
    '''
    This function is to wait for the AP CPU/Memory ready for the test
    kwa:
    - config: config to access AP: username, password, ip_addr
    - monitor: 0 to wait for CPU, 1 to wait for Memory
    - threshold: wait for CPU usage/Memory of Kernel is lower than this threshold
    - timeout: time to wait in minutes
    - interval: interval to sleep for each time to get kernel info
    - times_to_check: how many times to calculate CPU usage/Memory
    output:
    - return 1/0: 1 for ready, 0 for not ready
    '''
    MONITOR_CPU_USAGE, MONITOR_MEMORY = 0, 1
    _kwa = {
        'config': get_ap_default_cli_cfg(),
        'monitor': MONITOR_CPU_USAGE,
        'threshold': 40, # default % CPU Usage
        'timeout': 20, # in minute
        'interval': 2,
        'times_to_check': 3,
    }
    _kwa.update(kwa)

    monitor, threshold, = _kwa['monitor'], _kwa['threshold']
    timeout, times_to_check = _kwa['timeout'], _kwa['times_to_check']
    interval = _kwa['interval']

    monitor_res = 'CPU Usage' if monitor == MONITOR_CPU_USAGE else 'Memory(in KB)'

    logging.info('Start monitoring %s AP kernel %s' % \
                 (monitor_res, _kwa['config']['ip_addr']))

    #Sometimes, the paramiko lib has problem so we retry several time if any error
    tries = 1
    while tries <= 5:
        try:
            ap = create_ruckus_ap_by_ip_addr(**_kwa['config'])
            ap.goto_shell()
            for z in try_interval(timeout*60, 3):
                average_load, total_load = 0.0, 0.0
                for i in range(times_to_check):
                    cpu_usage = ap.get_kernel_info(
                        get_info = monitor, interval = interval,
                        times_to_check = times_to_check
                    )
                    if cpu_usage >= 0.0: total_load += cpu_usage

                average_load = total_load / times_to_check
                logging.info('Average %s: %0.4f' % (monitor_res, average_load))

                if average_load < threshold:
                    return 1
        except Exception:
            logging.info('Unable to connect to AP [%s], try again...' % \
                         _kwa['config']['ip_addr'])
            log_trace()
            time.sleep(20)
            tries += 1
            #del ap # it seems if cannot create a RuckusAP, the "ap" variable is not present anymore

    if tries <= 5:
        logging.info('AP %s is still too high (%0.4f) after %d minutes' % \
                     (monitor_res, average_load, timeout))
    else:
        logging.info('Cannot get kernel information after %s times retries' % tries)

    return 0


def assoc_client(client, wlan_cfg, timeout=180):
    '''
    . try to associate the client to wlan a in "timeout" period.
    . if it is failed to do so then an exception will be raised
    '''
    logging.debug('Try to associate the station to wlan in %s(s). station=%s, wlan=%s' %
                  (timeout, client.ip_addr, wlan_cfg['ssid']))
    log_cfg(wlan_cfg, 'wlan')
    client.cfg_wlan(wlan_cfg)
    status = ''
    for z in try_interval(timeout, 5):
        try:
            status = client.get_current_status()
            if status.lower() == 'connected':
                return
        except Exception, e:
            logging.debug('Error while trying to associate the client: %s. Re-try again...' % str(e))
            log_trace()
            client.remove_all_wlan()
            client.cfg_wlan(wlan_cfg)
    raise Exception('Could NOT associate the client to Wlan after trying %s(s). Current status: %s'
                    % (timeout, status))


#def assoc_client(client, wlan_cfg, timeout = 180):
#    '''
#    . try to associate the client to wlan a in "timeout" period.
#    . if it is failed to do so then an exception will be raised
#     NOTE: This function will replace the function "assoc_client" and
#                      its name will be "assoc_client".
#    '''
#    logging.debug('Try to associate the station to wlan in %s(s). station=%s, wlan=%s' \
#                  % (timeout, client.ip_addr, wlan_cfg['ssid']))
#    log_cfg(wlan_cfg, 'wlan_cfg')
#    client.cfg_wlan(wlan_cfg)
#    status = ''
#    end_time = time.time() + timeout
#    while status.lower() != 'connected' and time.time() < end_time:
#        try:
#            time.sleep(5)
#            status = client.get_current_status()
#        except Exception, e:
#            logging.debug('Error while trying to associate the client: %s. Re-try again...' % e.__str__())
#            client.remove_all_wlan()
#            client.cfg_wlan(wlan_cfg)
#
#    if status.lower() != 'connected' :
#        raise Exception('Could NOT associate the client to Wlan after trying %s(s). Current status: %s' \
#                                % (timeout, status))

def remove_file(file_path):
    '''
    This function is to remove file. It will raise exception if the file_path is not
    a file or the file is in use.
    '''
    os.remove(file_path)


def wait_for_sync(obj, cfg, get_fn, tries = 10, interval = 25):
    '''
    wait for the provisioning config is sync on both FM/AP
    NOTE: the get_fn must call nav_to() with force=True
    Ex: wait_for_sync(dv, <cfg>, lib.fm.<dvModule>.get)
    '''
    cfg = to_str_dict_items(copy.deepcopy(cfg))
    if not cfg:
        logging.info('Sync config is blank, so no wait here...')
        return True

    time.sleep(5)
    log_cfg(cfg)
    for t in try_times(tries, interval):
        logging.info('Wait for AP - FM config to be sync...')
        _cfg = get_fn(obj, cfg.keys())

        log_cfg(_cfg)
        if _cfg == cfg:
            return True
    return False


def remove_incompatible_cfg(cfg, ks):
    '''
    Since some config in AP but not in FM, likes fm_url
    removing these out of the cfg helps comparing 2 dicts easier
    '''
    p = copy.deepcopy(cfg)
    for k in ks:
        if k in p:
            p.pop(k)
    return p


def create_fm(cfg, semgr):
    '''
    . create an FM WebUI instance and login to FM with given account
    input
    . cfg: fm cfg to create an fm instance:
      ip_addr, username, password, browser_type (optional)
    . semgr: selenium manager
    output
    . fm instance
    '''
    p = dict(browser_type = 'firefox')
    p.update(cfg)
    logging.info('Create and login to FM with given account: %s' % p['username'])
    fm = create_com('fm', p, semgr, https = False)
    fm.start()
    return fm
