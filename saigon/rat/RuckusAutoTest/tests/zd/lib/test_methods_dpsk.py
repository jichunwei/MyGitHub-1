"""
Description: This module includes the functions that support to verify for DPSK


"""

import os
import time
import datetime
import logging
import csv
import re

from RuckusAutoTest.components import Helpers as lib

expire_time = {
    'Unlimited': 0,
    'One day': 24,
    'One week': 168,
    'Two weeks': 336,
    'One month': 720,
    'Two months': 1440,
    'Three months': 2160,
    'Half a year': 4380,
    'One year': 8760,
    'Two years': 17520,
    }

def _get_default_config(facility = None):
    conf = {'testcase': '',
            'wlan_cfg': {},
            'auth_server_type': 'local',
            'auth_server_info': {},
            'psk_expiration': 'One day',
            'number_of_dpsk': 100,
            'max_dpsk_allowable': 1000,
            'check_status_timeout': 150,
            'expected_response_time': 30,
            'target_station_ip': '192.168.1.11',
            'target_ping_ip': '192.168.0.252',
            }

    return conf


def _get_default_wlan_config(facility = None):
    conf = {'ssid': 'wlan-dpsk',
            'auth': 'PSK',
            'wpa_ver': 'WPA',
            'encryption': 'AES',
            'type': 'standard',
            'key_string': '1234567890',
            'key_index': '',
            'auth_svr': '',
            'do_zero_it': True,
            'do_dynamic_psk': True,
            }

    return conf

def _get_default_dlg_config(zd):
    zd_url = zd.selenium_mgr.to_url(zd.ip_addr, zd.https)

    # The total number of DPSK accounts has reached the maximum \
    # allowable size.  Please contact your network administrator to \
    # remove unused accounts before creating new ones.
    dlg_text_maxdpsk = zd.messages['E_FailDpskExceedMax']
    dlg_text = dlg_text_maxdpsk.split('.')[0]

    conf = {'dlg_title': "The page at %s says:" % zd_url,
            'dlg_text_maxdpsk': dlg_text,
            }

    return conf


def _get_num_of_psks(zd, pause = 5):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_GENERATED_PSK_CERTS)
    time.sleep(pause)

    total = zd._get_total_number(zd.info['loc_mon_total_generated_psk_span'], "Generated Dynamic-PSK")

    return int(total)

#
# test()
#

def test_generate_mutiple_dpsk(zd, dpsk_conf):
    
    generate_multiple_dpsk(zd, dpsk_conf)

    verify_dpsk_info_on_webui(zd, dpsk_conf)


def test_export_dpsk(zd, dpsk_conf):
    
    generate_multiple_dpsk(zd, dpsk_conf)

    verify_dpsk_info_in_record_file()


def test_delete_dpsk(zd):
    logging.info('Try to delete the generated PSKs')
    zd._remove_all_generated_psks()

    logging.info("Make sure the entries disappear from the table")
    total = _get_num_of_psks()

    if total != 0:
        errmsg = 'Error in deleting generated PSKs'
        return (0, errmsg)
    passmsg = 'Generated PSKs can be deleted successfully.'
    return (1, passmsg)

def test_verify_max_dpsk(zd, dpsk_conf):

    _generate_large_dpsk(zd, dpsk_conf, dpsk_conf['max_dpsk_allowable'])


def _generate_large_dpsk(zd, dpsk_conf, number):
    count = 0
    while True and count <= 1:
        try:
            generate_multiple_dpsk(zd, dpsk_conf)
            total = _get_num_of_psks(dpsk_conf['expected_response_time'])
            if number - total < dpsk_conf['number_of_dpsk']:
                count += 1

        except Exception, e:
            _check_exception_of_dpsk(e)
            break


def test_scalability_dpsk(zd, dpsk_conf):
    # first phase
    batch_file = _generate_csv_file(dpsk_conf['wlan_cfg']['ssid'], dpsk_conf['number_of_dpsk'])

    dpsk_conf.update({'profile_file': '\\'.join((os.getcwd(), batch_file.name)),
                      'repeat': False,
                      })

    _generate_large_dpsk(zd, dpsk_conf, dpsk_conf['max_dpsk_allowable'] / 2)


    # second phase

    _generate_large_dpsk(zd, dpsk_conf, dpsk_conf['max_dpsk_allowable'])

def _check_exception_of_dpsk(e, dlg_cfg, timeout):
    total = _get_num_of_psks(timeout)
    if dlg_cfg['dlg_text_maxdpsk'] in e.message:
        passmsg = '%s PSKs were generated on the ZD. ' % total
        passmsg = passmsg + "ZD does not allow to generate more batch PSKs " \
                             "when maximum allowable size has reached. "
        passmsg = passmsg
        logging.info(passmsg)

    elif 'ZD took over %s seconds to perform the action.' % timeout in e.message:
        errmsg = e.message
        logging.info(e.message)
        raise

    else:
        errmsg = "Failed to generate large number of PSKs. "
        logging.info(errmsg)
        raise

def test_import_csv(zd, profile_file, dpsk_conf):
    dpsk_conf.update({'profile_file': profile_file})
    
    generate_multiple_dpsk(zd, dpsk_conf)

    verify_dpsk_info_on_webui(zd, dpsk_conf)

def generate_multiple_dpsk(zd, dpsk_conf):
    if dpsk_conf.has_key('profile_file') and dpsk_conf['profile_file']:
        gen_msg = "Import the CSV file [%s] to generate Dynamic PSKs. " % dpsk_conf['profile_file']
        pass_msg = "Dynamic PSKs generation by importing the CSV file [%s] successfully. "
        pass_msg = pass_msg % dpsk_conf['profile_file']

    elif dpsk_conf.has_key('number_of_dpsk'):
        gen_msg = "Try to generate %s Dynamic PSKs automatically." % \
                  dpsk_conf['number_of_dpsk']
        pass_msg = "%s Dynamic PSKs were generated successfully. "
        pass_msg = pass_msg % dpsk_conf['number_of_dpsk']

    logging.info(gen_msg)

    #Serena Tan. 2010.12.7. To fix bug 16593.
    zd.login(True)

    lib.zd.wlan.generate_multiple_dpsk(zd, dpsk_conf)
    logging.info(pass_msg)

def _generate_csv_file(wlan_ssid, number_of_dpsk):
    # Delete the file if it exists
    try:
        os.remove('batch_dpsk_file.csv')
    except: pass

    batch_file = open('batch_dpsk_file.csv', 'wb')
    writer = csv.writer(batch_file)
    dpsk_info_list = []
    expected_webui_info = {}

    logging.info("Generate a CSV file with predefined user names")
    for idx in range(1, number_of_dpsk + 1):
        dpsk_info = 'Predefined-DPSK-User-%s' % idx
        dpsk_info_list.append([dpsk_info])
        expected_webui_info[dpsk_info] = {'wlan': wlan_ssid}

    writer.writerows(dpsk_info_list)
    batch_file.close()
    
    return batch_file


def _verify_dpsk_info(source_info, expected_info, user_only = True, mapped_keys = {}):
    """
    """
    if not isinstance(source_info, dict) or not isinstance(expected_info, dict):
        logging.debug("Either expected_info or source_info is not a dictionary")
        return -1
    
    verify_mapped_keys = {}
    if not mapped_keys:
        if source_info == expected_info:
            return 0
        else:
            for key in expected_info.values()[0].keys():
                verify_mapped_keys[key] = key
    
    else:
        verify_mapped_keys.update(mapped_keys)      
    
    errpsk = []
    if user_only:
        for user in expected_info.keys():
            if user not in source_info.keys():
                errpsk.append((user, 'not exist'))
                logging.debug('The PSK for %s does not exist' % user)
        return errpsk
    
    try:
        # either the user does not exist, or its value is not identical to the expected one
        for user in expected_info.keys():
            if user not in source_info.keys():
                errpsk.append((user, 'not exist'))
                logging.debug('The PSK for %s does not exist' % user)
                continue
            
            err_value = []
            for key in verify_mapped_keys.keys():
                map_key = verify_mapped_keys[key]
                if source_info[user][key] != expected_info[user][map_key]:
                    err_value.append(key)
                    msg = 'PSK for %s with %s is %s instead of %s as expected'
                    msg = msg % (user, key, source_info[user][key], expected_info[user][map_key])
                    logging.debug(msg)
                    
            if err_value:
                errpsk.append((user, 'diff by %s value' % err_value))                
            else:
                return 0
                
    except Exception, e:
        print e.message
        logging.debug(e.message)
        return -1

    return errpsk

def parse_csv_file(filepath,
                   header = ['User Name', 'Passphrase', 'Role', 'WLAN', 'Mac Address', 'Vlan ID', 'Expires']):
    #@author: Jane.Guo @since: 2013-9 adapt to 9.8, add Role
    data = {}
    try:
        tmpfile = open(filepath)
        reader = csv.reader(tmpfile)

        for row in reader:
            if row != header and len(row) > 0:
                a = {}
                for idx in range (0, len(header)):
                    a[header[idx].strip('#')] = row[idx]
                data[row[0]] = dict(a)

        tmpfile.close()

        logging.debug('All generated PSKs information in file are: %s' % data)

    except Exception, e:
        logging.debug(e.message)
        
    #@author: yuyanan @since:2014-7-24 bug:zf-9313 adapt elements from header change 
    if 'User Name' in data:
        del data['User Name']
    return data

def verify_dpsk_info_on_webui(zd, expected_info, user_only= False, mapped_key = {}):
    """
    """
    logging.info("Get all generated PSKs on WebUI")
    all_dpsk_info = zd.get_all_generated_psks_info()

    all_dpsk_info_on_zd = {}
    for dpsk_info in all_dpsk_info:
        all_dpsk_info_on_zd[dpsk_info['user']] = dpsk_info
    logging.debug('All PSKs information on ZD WebUI are: %s' % all_dpsk_info_on_zd.keys())

    logging.info('Verify the PSKs information shown on WebUI')
    res = _verify_dpsk_info(all_dpsk_info_on_zd, expected_info, user_only, mapped_key)
    
    if res == 0:
        msg = 'The expected PSK info is updated correctly on ZD WebUI'
        logging.info(msg)
        return ('PASS', msg)
    elif res == -1:
        msg = 'Can not not complete verifying the DPSK info on ZD WebUI'
        logging.info(msg)
        return ('FAIL', msg)
    else:
        msg = 'Unexpected info following by: %s' % res
        logging.info(msg)
        return ('FAIL', msg)

def verify_dpsk_info_under_shell(zdcli, expected_info, user_only= False, mapped_key = {}):
    """
    """
    logging.info("Get all generated PSKs from /etc/airespider/dpsk-list.xml")
    all_dpsk_info = lib.zdcli.shell.get_dpsk_list(zdcli)

    logging.debug('All PSKs information under ZDCLI are: %s' % all_dpsk_info)

    logging.info('Verify the PSKs information under ZDCLI')
    res = _verify_dpsk_info(all_dpsk_info, expected_info, user_only, mapped_key)
    
    if res == 0:
        msg = 'The expected PSK info is updated correctly on ZDCLI'
        logging.info(msg)
        return ('PASS', msg)
    elif res == -1:
        msg = 'Can not not complete verifying the DPSK info on ZDCLI'
        logging.info(msg)
        return ('FAIL', msg)
    else:
        msg = 'Unexpected info following by: %s' % res
        logging.info(msg)
        return ('FAIL', msg)
    
def verify_dpsk_info_in_record_file(zd, dpsk_conf, expected_info = None, mapped_key = {},mobile_fri = None):
    """
    """
    number_of_dpsk = ''
    vlan_id = ''
    wlan_ssid = ''
           
    if expected_info is None:
        if dpsk_conf.get('profile_file'):
            expected_info = parse_csv_file(dpsk_conf['profile_file'], 
                                          ['#User Name', 'Mac Address', 'Vlan ID'])
            for user in expected_info.keys():
                expected_info[user].update({'WLAN': dpsk_conf['wlan'] if dpsk_conf.get('wlan') else ''})
                if not expected_info[user].get('Mac Address'):
                    expected_info[user]['Mac Address'] = '00:00:00:00:00:00'
                vl = expected_info[user].get('Vlan ID')
                if not vl or '1' > str(vl) or str(vl) > '4094':
                    expected_info[user]['Vlan ID'] = '0'
        elif dpsk_conf.get('number_of_dpsk'):
            number_of_dpsk = int(dpsk_conf['number_of_dpsk'])
            vlan_id = dpsk_conf.get('vlan')
            wlan_ssid = dpsk_conf.get('wlan')
        else:
            raise Exception('There is not any suitable for verifying from dpsk configuration info')        
    
    logging.info('Download the generated PSKs record file')
    record_file_path = lib.zd.wlan.download_generated_dpsk_record(
                       zd, filename_re = "batch_dpsk_\d{6}_\d{2}_\d{2}.csv",
                       pause = 3)
    
    logging.debug("Parse the CSV file")
    all_info_in_file = parse_csv_file(record_file_path)
    os.remove(record_file_path)
    
    print 'expected'
    print expected_info
    print 'get from file'
    print all_info_in_file
    
    if number_of_dpsk:
        if int(number_of_dpsk) != len(all_info_in_file.keys()):
            msg = 'The number of generated psks is %s instead of %s as configuration' 
            msg = msg % (len(all_info_in_file.keys()), number_of_dpsk)
            logging.debug(msg)
            return ('FAIL', msg)
        
        errpsk = []
        for user in all_info_in_file.keys():
            msg = ''
            if all_info_in_file[user]['WLAN'] != wlan_ssid:
                msg = 'WLAN name [%s] does not match with expected [%s],'
                msg = msg % (all_info_in_file[user]['WLAN'], wlan_ssid)
            logging.info("%s",vlan_id)
            logging.info("get %s",all_info_in_file[user]['Vlan ID'])
            #@author: yin.wenling @since: 2014-09 adapt to 9.9 dpsk default vlan changed to "0"
            if all_info_in_file[user]['Vlan ID'] != vlan_id and all_info_in_file[user]['Vlan ID'] != "0":
                msg += 'VLAN ID [%s] does not match with expected [%s]'
            #@author: yin.wenling @since: 2014-09 adapt to 9.9 Mobile Friendly
            if dpsk_conf.get('mobile_friendly') == True:
                logging.info("Passphrase: %s",all_info_in_file[user]['Passphrase'])
                m = re.match('[0-9a-zA-Z]{8,63}',all_info_in_file[user]['Passphrase'])
                if not m:
                    msg += 'The Mobile Friendly Dpsk Passphrase contains illegal character'
                    
            if msg:
                errpsk.append((user, msg))
        if errpsk:
            return ('FAIL', 'Fail by unmatched info: %s' % errpsk)
        else:
            return ('PASS', 'The PSKs info in file matched as expected')
        
    elif expected_info:
        res = _verify_dpsk_info(all_info_in_file, expected_info, False)
    
        if res == 0:
            msg = 'The expected PSK info is updated correctly on file'
            logging.info(msg)
            return ('PASS', msg)
        elif res == -1:
            msg = 'Can not not complete verifying the DPSK info file'
            logging.info(msg)
            return ('FAIL', msg)
        else:
            msg = 'Unexpected info following by: %s' % res
            logging.info(msg)
            return ('FAIL', msg)

def _check_valid_dpsk_expiration(zd, dpsk_info, dpsk_expiration):
    max_expire_time = zd.get_current_time()
    max_expire_time = time.strftime("%Y/%m/%d %H:%M:%S",
                                    time.strptime(max_expire_time, "%A, %B %d, %Y %H:%M:%S %p"))
    max_expire_time = time.mktime(time.strptime(max_expire_time.split()[0], "%Y/%m/%d")) \
                    + expire_time[dpsk_expiration] * 3600

    dpsk_expire_time = dpsk_info['expired_time']
    dpsk_expire_time = time.mktime(time.strptime(dpsk_expire_time.split()[0], "%Y/%m/%d"))

    if dpsk_expire_time != max_expire_time:
        logging.info("The configured expire time for Generated PSK is: %s" % dpsk_expire_time)
        logging.info("The right expire time for Generated PSK is: %s" % max_expire_time)
        errmsg = "The expire time for the Generated PSK %s is not right. " % dpsk_info['passphrase']
        errmsg = errmsg + errmsg
        logging.info(errmsg)


def _check_expirity_status(zd, target_station, timeout = 60):
    # Make sure that target station status is not "Authorized" after doing
    # authentication with expired PSK
    time.sleep(2)
    logging.info("Verify information of the target station shown on the ZD")
    client_info_on_zd = None
    start_time = time.time()
    sta_wifi_ip_addr, sta_wifi_mac_addr = target_station.get_wifi_addresses()
    contd = True
    while contd:
        active_client_list = zd.get_active_client_list()
        for client in active_client_list:
            if client['mac'].upper() == sta_wifi_mac_addr.upper():
                if client['status'] == 'Authorized':
                    logging.debug("Active Client: %s" % str(client))
                    errmsg = "Station status is %s after doing authentication " \
                             "with expired PSK. " % client['status']
                    errmsg = errmsg + errmsg
                    logging.debug(errmsg)
                    return

                client_info_on_zd = client
                contd = False

                break #the for loop

        if not contd or time.time() - start_time > timeout:
            logging.debug("Active Client: %s" % str(client_info_on_zd))
            logging.info("The status of station is %s now" % client_info_on_zd['status'])

            break #the while loop

    if not client_info_on_zd:
        logging.debug("Active Client List: %s" % str(active_client_list))
        errmsg = "ZD didn't show any info about the target station (with MAC %s). " % \
                 sta_wifi_mac_addr
        errmsg = errmsg + errmsg
        logging.debug(errmsg)


def _associate_client(target_station, wlan_cfg, dpsk_info, timeout = 300):
    logging.info("Configure a WLAN with SSID %s on the target station %s" %
                 (wlan_cfg['ssid'], target_station.get_ip_addr()))
    client_wlan_cfg = wlan_cfg
    client_wlan_cfg.update({'key_string': dpsk_info['passphrase']})
    target_station.cfg_wlan(client_wlan_cfg)

    logging.info("Make sure the station associates to the WLAN")

    errorMsg = "The station didn't associate to the wireless network after %d seconds"

    _check_connection_status(target_station, "connected", timeout, errorMsg)

    logging.info("Renew IP address of the wireless adapter on the target station")
    target_station.renew_wifi_ip_address()

    logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % \
                 target_station.get_ip_addr())

    start_time = time.time()

    while time.time() - start_time < timeout:
        sta_wifi_ip_addr, sta_wifi_mac_addr = \
            target_station.get_wifi_addresses()

        if sta_wifi_mac_addr and sta_wifi_ip_addr \
        and sta_wifi_ip_addr != "0.0.0.0" \
        and not sta_wifi_ip_addr.startswith("169.254"):
            break

        time.sleep(1)


def _check_traffic(target_station, target_ping_ip, timeout = 60, when = 'Expired'):
    logging.info("Ping to %s from the target station" % 'target_ping_ip')
    ping_result = target_station.ping('target_ping_ip', 10 * 1000)
    errmsg = ''
    if when == 'Expired':
        if ping_result.find("Timeout") != -1:
            logging.info('Ping FAILED. Correct behavior.')
        else:
            logging.info('Ping OK. Incorrect behavior.')
            errmsg = "The target station could send traffic after its PSK had been expired"
            
    elif when == 'Authorized':
        if ping_result.find("Timeout") != -1:
            logging.info('Ping FAILED. Incorrect behavior.')
            errmsg = "The target station could not send traffic after %s seconds" % timeout
        else:
            logging.info('Ping OK. Correct behavior.')
    
    if errmsg:
        return 0, errmsg
    
    return 1, ''

def _check_auth_status(zd, target_station, dpsk_info, **kwargs):
    cfg = {'check_status_timeout': 120}
    cfg.update(kwargs)
    
    logging.info("Verify information of the target station shown on the ZD")
    timed_out = False
    start_time = time.time()
    sta_wifi_ip_addr, sta_wifi_mac_addr = target_station.get_wifi_addresses()
    while True:
        all_good = True
        client_info_on_zd = None

        active_client_list = zd.get_active_client_list()
        for client in active_client_list:
            logging.debug("Found info of a station: %s" % client)
            if client['mac'].upper() == sta_wifi_mac_addr.upper():
                client_info_on_zd = client
                if client['status'] != 'Authorized':
                    if timed_out:
                        errmsg = "The station status shown on ZD was %s instead of "\
                                 "'Authorized'" % client['status']
                        errmsg = errmsg + errmsg
                        logging.debug(errmsg)
                        return 0, errmsg

                    all_good = False
                    break

                if client['ip'] != dpsk_info['user']:
                    if timed_out:
                        errmsg = "The station username shown on ZD was %s instead of %s" % \
                                 (client['ip'], dpsk_info['user'])
                        errmsg = errmsg + errmsg
                        logging.debug(errmsg)
                        return 0, errmsg

                    all_good = False
                    break

                if client['wlan'] != dpsk_info['wlans']:
                    if timed_out:
                        errmsg = "The station's SSID shown on ZD was %s instead of %s" % \
                                 (client['wlan'], dpsk_info['wlans'])
                        errmsg = errmsg + errmsg
                        logging.debug(errmsg)
                        return

                    all_good = False
                    break

        # End of for

        # Quit the loop if everything is good
        if client_info_on_zd and all_good: break

        # Otherwise, sleep
        time.sleep(1)

        timed_out = time.time() - start_time > cfg['check_status_timeout']
        # And report error if the info is not available
        if not client_info_on_zd and timed_out:
            errmsg = "ZD didn't show any info about the target station "\
                     "while it had been associated"
            errmsg = errmsg + errmsg
            logging.debug(errmsg)
            return 0, errmsg

    return 1, ''


def test_dpsk_expiration(zd, target_station, dpsk_conf, **kwargs):
    cfg = {'internal_timer': 20,
           'check_status_timeout': 60,
           'target_ping_ip': '192.168.0.252'}

    cfg.update(kwargs)
    
    generate_multiple_dpsk(dpsk_conf)
    
    filelist = []
    logging.info('Download the generated PSKs record file')
    record_file_path = lib.zd.wlan.download_generated_dpsk_record(
                           zd, filename_re = "batch_dpsk_\d{6}_\d{2}_\d{2}.csv",
                           pause = 3)
    filelist.append(record_file_path)

    #logging.debug("Parse the CSV file")
    all_dpsk_file = parse_csv_file(record_file_path)

    logging.info("Get all generated PSKs on WebUI")
    all_dpsk_webui = zd.get_all_generated_psks_info()

    keys = ""
    for dpsk_info in all_dpsk_webui:
        dpsk_info.update({'passphrase': all_dpsk_file[dpsk_info['user']]})

        _check_valid_dpsk_expiration(dpsk_info)

        _cfg_remove_station_wlan_profiles(target_station, cfg['check_status_timeout'])

        _associate_client(target_station, dpsk_conf['wlan_cfg'], dpsk_info)

        _check_auth_status(zd, target_station, dpsk_info)

        _check_traffic(target_station, cfg['target_ping_ip'], when = 'Authorized')

        # Change ZD system time to make Generated PSK expired by changing the PC time
        # and ZD is sync with this new PC time
        logging.info("The PSK %s is valid until %s" % \
                     (dpsk_info['user'], dpsk_info['expired_time']))
        logging.info("Change ZD time so that all the generated PSKs are expired")

        tmptime = datetime.datetime.now() + \
                  datetime.timedelta(hours = expire_time[dpsk_conf['psk_expiration']],
                                     minutes = cfg['internal_timer'])

        os.system("date %s" % str(tmptime.month) + "-" + \
                  str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(5)
        zd.get_current_time(True)

        try:
            _cfg_remove_station_wlan_profiles(target_station, cfg['check_status_timeout'])

            _associate_client(target_station, dpsk_conf['wlan_cfg'], dpsk_info)

            _check_expirity_status(zd, target_station)

            _check_traffic(target_station, cfg['target_ping_ip'], when = 'Expired')

        except:
            raise

        finally:
            logging.info("Return the previous system time for ZD")
            tmptime = datetime.datetime.now() - \
                      datetime.timedelta(hours = expire_time[dpsk_conf['psk_expiration']],
                                         minutes = cfg['internal_timer'])

            os.system("date %s" % str(tmptime.month) + "-" + \
                      str(tmptime.day) + "-" + str(tmptime.year))
            time.sleep(5)
            zd.get_current_time(True)

        keys += dpsk_info['user'] + ', '

    passmsg = "PSKs expired correctly: [%s]" % keys
    return passmsg

def _cfg_remove_files(filelist):
    for afile in filelist:
        if afile:
            os.remove(afile)

def _cfg_remove_all_config_on_zd(zd):
    logging.info("Remove all WLANs configured on the ZD")
    lib.zd.wlan.delete_all_wlans(zd)

    logging.info("Remove all Generated PSKs on the ZD")
    zd._remove_all_generated_psks()


def _cfg_remove_station_wlan_profiles(target_station, timeout = 120):
    logging.info("Remove all WLAN profiles on the remote station")
    target_station.remove_all_wlan()

    logging.info("Make sure the target station %s disconnects from wireless network" %
                 target_station.get_ip_addr())

    errorMsg = "The station did not disconnect from wireless network within %d seconds"

    return _check_connection_status(target_station,
                                  "disconnected",
                                  timeout,
                                  errorMsg)
    
def _check_connection_status(target_station, status, timeout, errorMsg):
    start_time = time.time()
    while True:
        if target_station.get_current_status() == status:
            return True

        time.sleep(1)
        if time.time() - start_time > timeout:
            errmsg = errorMsg % timeout
            errmsg = errmsg + errmsg
            raise Exception(errmsg)
