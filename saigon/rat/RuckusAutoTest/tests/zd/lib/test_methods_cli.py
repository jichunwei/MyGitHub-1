# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to test for the Mesh mode test suite which force the AP mesh mode to Auto/Root/Mesh/Disable
Author: An Nguyen
Email: nnan@s3solutions.com.vn
"""

import logging
import time

from RuckusAutoTest.components import Helpers as lib

def test_show_all_vap(zd_cli, expected_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -V"')
    vap_in_cli = lib.zd.cli.get_wlaninfo_v(zd_cli)
    logging.debug('Information on CLI: %s' % vap_in_cli)
    vap_in_webui = expected_info
    logging.debug('Information on WebUI: %s' % vap_in_webui)

    if ('illegal option' or 'command not found') in vap_in_cli['raw_info']:
        errmsg = vap_in_cli['raw_info']
        return (passmsg, errmsg)

    if vap_in_cli['total_vap'] == 'The information is not existed or NULL':
        if len(vap_in_webui) > 0:
            msg = 'There are %s VAP showed on WebUI but the information of total VAP is not existed'
            errmsg = msg % len(vap_in_webui)
            return (passmsg, errmsg)
        else:
            errmsg = 'The information about total VAP is not existed as expected'
            return (passmsg, errmsg)

    ssid_list = vap_in_cli['ssid']
    vap_list = vap_in_cli['vap']
    vap_info_in_cli_list = [(ssid_list[i], vap_list[i]) for i in range(len(ssid_list))]
    error_vap = []
    for vap_info in vap_info_in_cli_list:
        if vap_info not in vap_in_webui:
            error_vap.append(vap_info)
    if error_vap:
        errmsg = 'The information of VAP [%s] be showed on CLI but not on WebUI' % error_vap
        return (passmsg, errmsg)

    for vap_info in vap_in_webui:
        if vap_info not in vap_info_in_cli_list:
            error_vap.append(vap_info)
    if error_vap:
        errmsg = 'The information of VAP [%s] be showed on WebUI but not on CLI' % error_vap
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -V" worked well'
    return (passmsg, errmsg)

def test_show_a_vap(ap_list, zd, zd_cli, expected_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -v vap_mac -l7" for each of VAP')
    for ap in ap_list:
        ap_info_wlans = lib.zd.aps.get_ap_detail_wlans_by_mac_addr(zd, ap.base_mac_addr)

        for (wlan, wlan_info) in ap_info_wlans.iteritems():
            logging.info('Get information of VAP %s: ' % wlan_info['bssid'])
            vap_info_in_cli = lib.zd.cli.get_wlaninfo_v(zd_cli, 'wlaninfo -v %s -l7' % wlan_info['bssid'])
            logging.debug(vap_info_in_cli['raw_info'])
            if ('illegal option' or 'command not found') in vap_info_in_cli['raw_info']:
                errmsg = vap_info_in_cli['raw_info']
                return (passmsg, errmsg)

            expected_info.update({'ap': (ap.base_mac_addr, ap.ip_addr),
                                  'vap': wlan_info['bssid'],
                                  'ssid': wlan_info['wlan']})

            logging.debug(expected_info)

            for key in expected_info.keys():
                if vap_info_in_cli[key][0] != expected_info[key]:
                    msg = 'The "%s" information on CLI of VAP[%s] of AP[%s] is "%s" instead of "%s"'
                    errmsg = msg % (key, vap_info_in_cli[key], ap.base_mac_addr,
                                         vap_info_in_cli[key], expected_info[key])
                    return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -v vap_mac -l7" worked well'
    return (passmsg, errmsg)

def test_delete_a_vap(ap_list, zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -v vap_mac -D" for each of VAP')
    for ap in ap_list:
        ap_info_wlans = lib.zd.aps.get_ap_detail_wlans_by_mac_addr(zd, ap.base_mac_addr)
        for (wlan_id, wlan_info) in ap_info_wlans.iteritems():
            logging.info('Deleting VAP %s' % wlan_info['bssid'])
            vap_info_in_cli = lib.zd.cli.get_wlaninfo_v(zd_cli, 'wlaninfo -v %s -D' % wlan_info['bssid'])
            time.sleep(2)
            if ('illegal option' or 'command not found') in vap_info_in_cli['raw_info']:
                errmsg = vap_info_in_cli['raw_info']
                return (passmsg, errmsg)

            if 'Delete VAP %s successfully' % wlan_info['bssid'] in vap_info_in_cli['raw_info']:
                logging.info(vap_info_in_cli['raw_info'])
            else:
                errmsg = vap_info_in_cli['raw_info']
                return (passmsg, errmsg)

            check_cli_info = lib.zd.cli.get_wlaninfo_v(zd_cli, 'wlaninfo -v %s' % wlan_info['bssid'])
            if 'VAP %s not found' % wlan_info['bssid'] in check_cli_info['raw_info']:
                logging.info('[Correct behavior]: %s' % check_cli_info['raw_info'])
            else:
                errmsg = check_cli_info['raw_info']
                return (passmsg, errmsg)
            current_ap_info_wlans = lib.zd.aps.get_ap_detail_wlans_by_mac_addr(zd, ap.base_mac_addr)
            check_vap_list = [current_ap_info_wlans[wlan]['bssid'] for wlan in current_ap_info_wlans if wlan]
            if wlan_info['bssid'] in check_vap_list:
                errmsg = 'VAP[%s] is still existed after be delete by CLI command' % wlan_info['bssid']
                return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -v vap_mac -D" worked well'
    return (passmsg, errmsg)

def test_show_all_station(zd_cli, expected_sta_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -S"')
    sta_info_in_cli = lib.zd.cli.get_wlaninfo_s(zd_cli)
    logging.debug('Information on CLI: %s' % sta_info_in_cli)

    if ('illegal option' or 'command not found') in sta_info_in_cli['raw_info']:
        errmsg = sta_info_in_cli['raw_info']
        logging.debug(errmsg)
        return (passmsg, errmsg)

    if sta_info_in_cli['station'] == 'The information is not existed or NULL' \
    or sta_info_in_cli['ip'] == 'The information is not existed or NULL':
        errmsg = '[Incorrect behavior] The information of station mac and ip are not showed'
        logging.debug(errmsg)
        return (passmsg, errmsg)

    if len(sta_info_in_cli['station']) != int(sta_info_in_cli['total_sta'][0])\
    or len(sta_info_in_cli['ip']) != int(sta_info_in_cli['total_sta'][0]):
        errmsg = '[Error Info] There are %s stations in total but %s stations, %s ips are recorded'
        errmsg = errmsg % (sta_info_in_cli['total_sta'][0], len(sta_info_in_cli['station']), len(sta_info_in_cli['ip']))
        logging.debug(errmsg)
        return (passmsg, errmsg)

    sta_list_in_cli = []
    for idx in range(int(sta_info_in_cli['total_sta'][0])):
        sta_list_in_cli.append((sta_info_in_cli['station'][idx], sta_info_in_cli['ip'][idx]))

    for sta in expected_sta_info:
        if sta not in sta_list_in_cli:
            errmsg = 'The information of station[%s] is not showed in CLI' % str(sta)
            logging.debug(errmsg)
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -S" worked well'
    logging.debug(passmsg)
    return (passmsg, errmsg)

def test_show_a_station(zd_cli, sta_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -s %s -l7"' % sta_info[0])
    sta_info_in_cli = lib.zd.cli.get_wlaninfo_s(zd_cli, 'wlaninfo -s %s -l7' % sta_info[0])
    logging.debug('Information on CLI: %s' % sta_info_in_cli)

    if ('illegal option' or 'not found') in sta_info_in_cli['raw_info']:
        errmsg = sta_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if sta_info != (sta_info_in_cli['station'][0], sta_info_in_cli['ip'][0]):
        errmsg = 'The information of station is [%s] instead of [%s]'
        errmsg = errmsg % ((sta_info_in_cli['station'][0], sta_info_in_cli['ip'][0]), sta_info)
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -s sta_mac -l7" worked well'
    return (passmsg, errmsg)

def test_delete_a_station(zd_cli, sta_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -s %s -D"' % sta_info[0])
    sta_info_in_cli = lib.zd.cli.get_wlaninfo_s(zd_cli, 'wlaninfo -s %s -D' % sta_info[0])
    logging.debug('Information on CLI: %s' % sta_info_in_cli)

    if ('illegal option' or 'command not found') in sta_info_in_cli['raw_info']:
        errmsg = sta_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if ('Delete STA %s successfully') % sta_info[0] in sta_info_in_cli['raw_info']:
        logging.info(sta_info_in_cli['raw_info'])
    else:
        logging.info(sta_info_in_cli['raw_info'])
        errmsg = sta_info_in_cli['raw_info']
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -s sta_mac -D" worked well'
    return (passmsg, errmsg)

def test_show_timer(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -s sta_mac -D"')
    timer_info_in_cli = lib.zd.cli.get_wlaninfo_t(zd_cli)
    logging.debug('Information on CLI: %s' % timer_info_in_cli)

    if ('illegal option' or 'command not found') in timer_info_in_cli['raw_info']:
        errmsg = timer_info_in_cli['raw_info']
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -T" worked well'
    return (passmsg, errmsg)

def test_show_all_config_ap(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -C"')
    all_ap_info_in_webui = zd.get_all_ap_info()
    if not all_ap_info_in_webui:
        raise Exception('[Error] There is no AP under Zone Director control')
    logging.debug('Information on WebUI: %s' % all_ap_info_in_webui)
    cfg_ap_info_in_cli = lib.zd.cli.get_wlaninfo_c(zd_cli)

    if ('illegal option' or 'command not found') in cfg_ap_info_in_cli['raw_info']:
        errmsg = cfg_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_ap_info_in_webui and cfg_ap_info_in_cli['mac'] == 'The information is not existed or NULL':
        errmsg = cfg_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if len(cfg_ap_info_in_cli['mac']) != len(all_ap_info_in_webui):
        errmsg = 'There are %s AP(s) on WebUI but %s AP(s) on CLI'
        errmsg = errmsg % (len(all_ap_info_in_webui), len(cfg_ap_info_in_cli['mac']))
        return (passmsg, errmsg)

    logging.info('The APs list on CLI: %s' % cfg_ap_info_in_cli['mac'])
    for ap_info in all_ap_info_in_webui:
        if ap_info['mac'] not in cfg_ap_info_in_cli['mac']:
            errmsg = 'AP[%s] is showed on ZD WebUI but not in CLI' % ap_info
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -C" worked well'
    return (passmsg, errmsg)

def test_show_a_config_ap(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    all_ap_info_in_webui = zd.get_all_ap_info()
    logging.debug('Information on WebUI: %s' % all_ap_info_in_webui)
    if not all_ap_info_in_webui:
        raise Exception('[Error] There is no AP under Zone Director control')
    logging.info('Verifying command "wlaninfo -c ap_mac -l7" for each of AP')
    for ap in all_ap_info_in_webui:
        cfg_ap_info_in_cli = lib.zd.cli.get_wlaninfo_c(zd_cli, 'wlaninfo -c %s -l7' % ap['mac'])
        logging.debug('Information on CLI: %s' % cfg_ap_info_in_cli)
        if ('illegal option' or 'command not found') in cfg_ap_info_in_cli['raw_info']:
            errmsg = cfg_ap_info_in_cli['raw_info']
            return (passmsg, errmsg)

        if cfg_ap_info_in_cli['mac'] == 'The information is not existed or NULL':
            errmsg = cfg_ap_info_in_cli['raw_info']
            return (passmsg, errmsg)

        if cfg_ap_info_in_cli['mac'][0] != ap['mac']\
        or cfg_ap_info_in_cli['model'][0] != ap['model']\
        or cfg_ap_info_in_cli['ip'][0] != ap['ip_addr']:
            errmsg = 'The information on CLI is %s instead of %s'
            errmsg = errmsg % (cfg_ap_info_in_cli, ap)
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -c ap_mac -l7" worked well'
    return (passmsg, errmsg)

def test_show_rogue(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -R"')
    all_rogue_device_in_cli = lib.zd.cli.get_wlaninfo_r(zd_cli)
    if ('illegal option' or 'command not found') in all_rogue_device_in_cli['raw_info']:
        errmsg = all_rogue_device_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_rogue_device_in_cli['total_rogue_device'] == 'The information is not existed or NULL':
        errmsg = 'The total rouge device is not existed at expected'
        return (passmsg, errmsg)

    if all_rogue_device_in_cli['total_rogue_device'][0] == '0':
        passmsg = 'command "wlaninfo -R" worked well'
        return (passmsg, errmsg)

    logging.debug('[Rouge device list]: %s' % all_rogue_device_in_cli['rogue_device'])

    logging.info('Verifying command "wlaninfo -r rouge_mac -l7" for each of rouge device')
    for rogue_device in all_rogue_device_in_cli['rogue_device']:
        rouge_detail_info = lib.zd.cli.get_wlaninfo_r(zd_cli, 'wlaninfo -r %s -l7' % rogue_device[0])
        logging.debug(rouge_detail_info['raw_info'])
        if ('illegal option' or 'command not found') in rouge_detail_info['raw_info']:
            errmsg = rouge_detail_info['raw_info']
            return (passmsg, errmsg)

        if rouge_detail_info['rogue_device'] == 'The information is not existed or NULL':
            errmsg = 'The detail information is not existed as expected'
            return (passmsg, errmsg)

        if rouge_detail_info['rogue_device'][0] != rogue_device:
            errmsg = 'The rouge information is %s instead of %s'
            errmsg = errmsg % (rouge_detail_info['rogue_device'][0], rogue_device)
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -R" and "wlaninfo -r rouge_mac -l7" worked well'
    return (passmsg, errmsg)

def test_show_wlan_info(zd_cli, expected_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -W"')
    all_wlan_in_cli = lib.zd.cli.get_wlaninfo_w(zd_cli)
    if ('illegal option' or 'command not found') in all_wlan_in_cli['raw_info']:
        errmsg = all_wlan_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_wlan_in_cli['total_wlan'] == 'The information is not existed or NULL'\
    or all_wlan_in_cli['total_wlan'][0] == '0':
        errmsg = 'The total WLAN is not existed at expected'
        return (passmsg, errmsg)

    for key in expected_info.keys():
        if expected_info[key] not in all_wlan_in_cli[key]:
            errmsg = 'The %s[%s] is not existed as expected'
            errmsg = errmsg % (key, expected_info[key])
            return (passmsg, errmsg)

    logging.info('Verifying command "wlaninfo -w wlan_name"')
    wlan_in_cli = lib.zd.cli.get_wlaninfo_w(zd_cli, 'wlaninfo -w "%s"' % expected_info['ssid'])
    if ('illegal option' or 'command not found') in wlan_in_cli['raw_info']:
        errmsg = wlan_in_cli['raw_info']
        return (passmsg, errmsg)

    for key in expected_info.keys():
        if expected_info[key] not in wlan_in_cli[key]:
            errmsg = 'The %s[%s] is not existed as expected[%s]'
            errmsg = errmsg % (key, expected_info[key], wlan_in_cli[key])
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -W" and "wlaninfo -w wlan_name" worked well'
    return (passmsg, errmsg)

def test_show_user_info(zd_cli, expected_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -U"')
    all_user_in_cli = lib.zd.cli.get_wlaninfo_u(zd_cli)
    if ('illegal option' or 'command not found') in all_user_in_cli['raw_info']:
        errmsg = all_user_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_user_in_cli['total_user'] == 'The information is not existed or NULL'\
    or all_user_in_cli['total_user'][0] == '0':
        errmsg = 'The total user is not existed at expected'
        return (passmsg, errmsg)

    if expected_info['username'] not in all_user_in_cli['username']:
        errmsg = 'The user[%s] is not existed in CLI as expected'
        errmsg = errmsg % (key, expected_info['username'])
        return (passmsg, errmsg)

    logging.info('Verifying command "wlaninfo -u user_name"')
    user_in_cli = lib.zd.cli.get_wlaninfo_u(zd_cli, 'wlaninfo -u "%s" -l7' % expected_info['username'])
    if ('illegal option' or 'command not found') in user_in_cli['raw_info']:
        errmsg = user_in_cli['raw_info']
        return (passmsg, errmsg)

    for key in expected_info.keys():
        if expected_info[key] not in user_in_cli[key]:
            errmsg = 'The %s[%s] is not existed as expected[%s]'
            errmsg = errmsg % (key, expected_info[key], user_in_cli[key])
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -U" and "wlaninfo -u user_name" worked well'
    return (passmsg, errmsg)

def test_show_mesh_info(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -M"')
    mesh_conf_in_webui = zd.get_mesh_cfg()
    logging.debug('Mesh info on WebUI: %s' % mesh_conf_in_webui)
    mesh_info_in_cli = lib.zd.cli.get_wlaninfo_m(zd_cli)
    if ('illegal option' or 'command not found') in mesh_info_in_cli['raw_info']:
        errmsg = mesh_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if mesh_info_in_cli['total_mesh_entry'] == 'The information is not existed or NULL':
        errmsg = 'The total Mesh entry is not existed at expected'
        return (passmsg, errmsg)

    logging.debug(mesh_info_in_cli['raw_info'])
    if mesh_info_in_cli['mesh_info'][0] != mesh_conf_in_webui['mesh_name']:
        errmsg = 'Mesh name is "%s" instead of "%s"'
        errmsg = errmsg % (mesh_info_in_cli['mesh_info'][0], mesh_conf_in_webui['mesh_name'])
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -M" worked well'
    return (passmsg, errmsg)

def test_display_ap_info(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "apmgrinfo -a"')
    all_ap_info_in_webui = zd.get_all_ap_info()
    if not all_ap_info_in_webui:
        raise Exception('[Error] There is no AP under Zone Director control')
    logging.debug('Information on WebUI: %s' % all_ap_info_in_webui)
    all_ap_info_in_cli = lib.zd.cli.get_apmgrinfo_a(zd_cli)

    if ('illegal option' or 'command not found') in all_ap_info_in_cli['raw_info']:
        errmsg = all_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_ap_info_in_webui and all_ap_info_in_cli['ap'] == 'The information is not existed or NULL':
        errmsg = all_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if len(all_ap_info_in_cli['ap']) != len(all_ap_info_in_webui):
        errmsg = 'There are %s AP(s) on WebUI but %s AP(s) on CLI'
        errmsg = errmsg % (len(all_ap_info_in_webui), len(all_ap_info_in_cli['ap']))
        return (passmsg, errmsg)

    logging.info('The APs list on CLI: %s' % all_ap_info_in_cli['ap'])
    for ap_info in all_ap_info_in_webui:
        if (ap_info['mac'], ap_info['ip_addr']) not in all_ap_info_in_cli['ap']:
            errmsg = 'AP[%s] is showed on ZD WebUI but not in CLI' % ap_info
            return (passmsg, errmsg)

    passmsg = 'command "apmgrinfo -a" worked well'
    return (passmsg, errmsg)

def test_ping_ap_mgr(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "apmgrinfo -p"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'apmgrinfo -p', is_shell_cmd = True)
    logging.debug(result)

    if 'APMgr_Ping Reply message received' not in result['raw_info']:
        errmsg = result['raw_info']
        return (passmsg, errmsg)
    else:
        passmsg = 'command "apmgrinfo -p" is supported'
        return (passmsg, errmsg)

def test_ping_command(zd_cli, dest_ip, allowed_ping = True):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "ping"')
    result = lib.zd.cli.ping(zd_cli, dest_ip)
    logging.debug(result)

    if ('illegal option' or 'command not found') in result['raw_info']:
        errmsg = result['raw_info']
        return (passmsg, errmsg)

    if allowed_ping:
        if result['ping_statistics'] == 'The information is not existed or NULL':
            errmsg = '[Ping %s failed][Incorrect behavior]' % dest_ip
            return (passmsg, errmsg)
        if result['ping_statistics'][0][2] == '100':
            errmsg = '[Ping %s failed][Incorrect behavior]' % dest_ip
            return (passmsg, errmsg)

    if not allowed_ping:
        if result['ping_statistics'] == 'The information is not existed or NULL':
            passmsg = '[Ping %s failed][Correct behavior]' % dest_ip
            return (passmsg, errmsg)
        if result['ping_statistics'][0][2] != '100':
            errmsg = '[Ping %s ok][Incorrect behavior]' % dest_ip
            return (passmsg, errmsg)

    passmsg = 'command "ping" worked well'
    return (passmsg, errmsg)

def test_setting_stp(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "stp disable"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'stp disable')
    logging.debug(result)
    if 'Spanning-tree protocol disabled' not in result['raw_info']:
        errmsg = '[STP Disable failed] %s' % result['raw_info']
        return (passmsg, errmsg)

    logging.info('Verifying command "stp enable"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'stp enable')
    logging.debug(result)
    if 'Spanning-tree protocol enabled' not in result['raw_info']:
        errmsg = '[STP Enable] %s' % result['raw_info']
        return (passmsg, errmsg)

    passmsg = 'command "stp" worked well'
    return (passmsg, errmsg)

def test_setting_upnp(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "upnp disable"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'upnp disable')
    logging.debug(result)
    if 'UPnP Service is disabled' not in result['raw_info']:
        errmsg = '[UPNP Disable failed] %s' % result['raw_info']
        return (passmsg, errmsg)

    logging.info('Verifying command "upnp enable"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'upnp enable')
    logging.debug(result)
    if 'UPnP Service is enabled' not in result['raw_info']:
        errmsg = '[UPNP Enable failed] %s' % result['raw_info']
        return (passmsg, errmsg)

    passmsg = 'command "upnp" worked well'
    return (passmsg, errmsg)

def test_show_all_active_ap(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo -A"')
    all_ap_info_in_webui = zd.get_all_ap_info()
    if not all_ap_info_in_webui:
        raise Exception('[Error] There is no AP under Zone Director control')
    logging.debug('Information on WebUI: %s' % all_ap_info_in_webui)
    all_ap_info_in_cli = lib.zd.cli.get_wlaninfo_a(zd_cli)

    if ('illegal option' or 'command not found') in all_ap_info_in_cli['raw_info']:
        errmsg = all_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if all_ap_info_in_webui and all_ap_info_in_cli['ap'] == 'The information is not existed or NULL':
        errmsg = all_ap_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if len(all_ap_info_in_cli['ap']) != len(all_ap_info_in_webui):
        errmsg = 'There are %s AP(s) on WebUI but %s AP(s) on CLI'
        errmsg = errmsg % (len(all_ap_info_in_webui), len(all_ap_info_in_cli['ap']))
        return (passmsg, errmsg)

    logging.info('The APs list on CLI: %s' % all_ap_info_in_cli['ap'])
    for ap_info in all_ap_info_in_webui:
        if ap_info['mac'] not in all_ap_info_in_cli['ap']:
            errmsg = 'AP[%s] is showed on ZD WebUI but not in CLI' % ap_info
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -A" worked well'
    return (passmsg, errmsg)

def test_show_an_active_ap(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    all_ap_info_in_webui = zd.get_all_ap_info()
    logging.debug('Information on WebUI: %s' % all_ap_info_in_webui)
    if not all_ap_info_in_webui:
        raise Exception('[Error] There is no AP under Zone Director control')
    logging.info('Verifying command "wlaninfo -a ap_mac" for each of AP')
    for ap in all_ap_info_in_webui:
        ap_info_in_cli = lib.zd.cli.get_wlaninfo_a(zd_cli, 'wlaninfo -a %s' % ap['mac'])
        logging.debug('Information on CLI: %s' % ap_info_in_cli)
        if ('illegal option' or 'command not found') in ap_info_in_cli['raw_info']:
            errmsg = ap_info_in_cli['raw_info']
            return (passmsg, errmsg)

        if ap_info_in_cli['ap'] == 'The information is not existed or NULL':
            errmsg = ap_info_in_cli['raw_info']
            return (passmsg, errmsg)

        if ap_info_in_cli['ap'][0] != ap['mac']\
        or ap_info_in_cli['model'][0] != ap['model']\
        or ap_info_in_cli['ip'][0] != ap['ip_addr']:
            errmsg = 'The information on CLI is %s instead of %s'
            errmsg = errmsg % (ap_info_in_cli, ap)
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo -A" worked well'
    return (passmsg, errmsg)

def test_show_system_parameters(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --system"')
    system_parameters = lib.zd.cli.get_wlaninfo_system(zd_cli)
    logging.debug(system_parameters)

    if ('illegal option' or 'command not found') in system_parameters['raw_info']:
        errmsg = system_parameters['raw_info']
        return (passmsg, errmsg)

    if system_parameters['ip_addr'] == 'The information is not existed or NULL'\
    or system_parameters['ip_addr'][0] != zd_cli.ip_addr:
        errmsg = all_ap_info_in_cli['"ip_addr" value is "%s" instead of "%s"' % (system_parameters['ip_addr'], zd_cli.ip_addr)]
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --system" worked well'
    return (passmsg, errmsg)

def test_show_dos_info(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --dos"')
    result = lib.zd.cli.get_expected_info_from_command(zd_cli, 'wlaninfo --dos')
    logging.debug(result)

    if ('illegal option' or 'command not found') in result['raw_info']:
        errmsg = result['raw_info']
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --dos" is supported'
    return (passmsg, errmsg)

def test_show_authen_client(zd_cli, expected_sta):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --web-auth"')
    all_auth_client = lib.zd.cli.get_wlaninfo_web_auth(zd_cli)
    logging.info(all_auth_client)

    if ('illegal option' or 'command not found') in all_auth_client['raw_info']:
        errmsg = all_auth_client['raw_info']
        return (passmsg, errmsg)

    auth_client_list = [client[0] for client in all_auth_client['sta']]
    if expected_sta.lower() not in auth_client_list:
        errmsg = 'The station [%s] is authorized but not shown in the CLI' % expected_sta
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --web-auth" worked well'
    return (passmsg, errmsg)

def test_show_dynamic_psk(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --all-dpsk"')
    all_dpsk_info = lib.zd.cli.get_wlaninfo_dpsk(zd_cli)
    logging.debug(all_dpsk_info)

    if ('illegal option' or 'command not found') in all_dpsk_info['raw_info']:
        errmsg = all_dpsk_info['raw_info']
        return (passmsg, errmsg)

    if all_dpsk_info['psk'] == 'The information is not existed or NULL':
        errmsg = 'There is not any PSK shown on CLI'
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-dpsk" worked well'
    return (passmsg, errmsg)

def test_show_dynamic_cert(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --dcert"')
    all_dcert_info = lib.zd.cli.get_wlaninfo_dcert(zd_cli)
    logging.debug(all_dcert_info)

    if ('illegal option' or 'command not found') in all_dcert_info['raw_info']:
        errmsg = all_dcert_info['raw_info']
        return (passmsg, errmsg)

    if all_dcert_info['cert'] == 'The information is not existed or NULL':
        errmsg = 'There is not any PSK shown on CLI'
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --dcert" worked well'
    return (passmsg, errmsg)

def test_show_l2_acl(zd_cli, expected_acl):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --all-acl"')
    all_l2_acl = lib.zd.cli.get_wlaninfo_acl(zd_cli)
    logging.debug(all_l2_acl)

    if ('illegal option' or 'command not found') in all_l2_acl['raw_info']:
        errmsg = all_l2_acl['raw_info']
        return (passmsg, errmsg)

    if all_l2_acl['acl'] == 'The information is not existed or NULL':
        errmsg = 'There is not any L2 ACL shown on CLI'
        return (passmsg, errmsg)

    l2_acl_list = [acl[1] for acl in all_l2_acl['acl']]
    if expected_acl not in l2_acl_list:
        errmsg = 'The L2 ACL [%s] is not shown in the CLI' % expected_acl
        return (passmsg, errmsg)

    expected_l2_acl_info_in_cli = lib.zd.cli.get_wlaninfo_acl(zd_cli, 'wlaninfo --acl %s' % expected_acl)
    logging.debug(expected_l2_acl_info_in_cli)

    if ('illegal option' or 'command not found') in expected_l2_acl_info_in_cli['raw_info']:
        errmsg = expected_l2_acl_info_in_cli['raw_info']
        return (passmsg, errmsg)

    if expected_l2_acl_info_in_cli['acl'][0][1] != expected_acl:
        errmsg = 'The infomation of ACL[%s] is not shown on CLI' % expected_acl
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-acl" and "wlaninfo --acl acl_name" worked well'
    return (passmsg, errmsg)

def test_show_role(zd_cli, expected_role):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --all-role"')
    all_role = lib.zd.cli.get_wlaninfo_role(zd_cli)
    logging.debug(all_role)

    if ('illegal option' or 'command not found') in all_role['raw_info']:
        errmsg = all_role['raw_info']
        return (passmsg, errmsg)

    if all_role['role'] == 'The information is not existed or NULL':
        errmsg = 'There is not any role shown on CLI'
        return (passmsg, errmsg)

    role_list = [role[0] for role in all_role['role']]
    if expected_role not in role_list:
        errmsg = 'The Role [%s] is not shown in the CLI' % expected_role
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-role" worked well'
    return (passmsg, errmsg)

def test_show_auth_server(zd_cli, expected_auth_server):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --all-auth"')
    all_auth_ser = lib.zd.cli.get_wlaninfo_auth(zd_cli)
    logging.debug(all_auth_ser)

    if ('illegal option' or 'command not found') in all_auth_ser['raw_info']:
        errmsg = all_auth_ser['raw_info']
        return (passmsg, errmsg)

    if all_auth_ser['auth_ser'] == 'The information is not existed or NULL':
        errmsg = 'Could not get the authentication server information'
        return (passmsg, errmsg)

    auth_ser_name_list = [server[1] for server in all_auth_ser['auth_ser']]
    if expected_auth_server not in auth_ser_name_list:
        errmsg = 'The server[%s] is not shown on CLI' % expected_auth_server
        return (passmsg, errmsg)

    logging.info('Verifying command "wlaninfo --auth ser_id"')
    for server in all_auth_ser['auth_ser']:
        info = lib.zd.cli.get_wlaninfo_auth(zd_cli, 'wlaninfo --auth %s' % server[0])
        logging.debug(info)
        if ('illegal option' or 'command not found') in info['raw_info']:
            errmsg = info['raw_info']
            return (passmsg, errmsg)

        if info['auth_ser'] == 'The information is not existed or NULL':
            errmsg = 'Could not get the information of server %s' % server[1]
            return (passmsg, errmsg)

        if info['auth_ser'][0] != server:
            errmsg = 'The server info is %s instead of %s'
            errmsg = errmsg % (info['auth_ser'][0], server)

    passmsg = 'command "wlaninfo --all-auth" and "wlaninfo --auth ser_id" worked well'
    return (passmsg, errmsg)

def test_show_mesh_ap(zd_cli, expected_mesh_ap_list):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --all-mesh-ap"')
    all_mesh_ap = lib.zd.cli.get_wlaninfo_mesh_ap(zd_cli)
    logging.debug(all_mesh_ap)

    if ('illegal option' or 'command not found') in all_mesh_ap['raw_info']:
        errmsg = all_mesh_ap['raw_info']
        return (passmsg, errmsg)

    if not expected_mesh_ap_list:
        passmsg = 'command "wlaninfo --mesh-ap" is supported'
        return (passmsg, errmsg)

    if all_mesh_ap['ap'] == 'The information is not existed or NULL':
        errmsg = 'There is not any role shown on CLI'
        return (passmsg, errmsg)

    mesh_ap_list_in_cli = [mesh_ap[0] for mesh_ap in all_mesh_ap['ap']]
    if len(expected_mesh_ap_list) != len(mesh_ap_list_in_cli):
        errmsg = 'There are %s mesh aps are shown on CLI instead of %s'
        errmsg = errmsg % (len(mesh_ap_list_in_cli), len(expected_mesh_ap_list))
        return (passmsg, errmsg)

    for mesh_ap in expected_mesh_ap_list:
        if mesh_ap not in mesh_ap_list_in_cli:
            errmsg = 'Mesh AP[%s] is not shown in CLI' % mesh_ap
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-mesh-ap" and "wlaninfo --mesh-ap ap_mac" worked well'
    return (passmsg, errmsg)

def test_mesh_topology(zd_cli, expected_mesh_ap_list):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --mesh-topology"')
    mesh_topo_info = lib.zd.cli.get_expected_info_from_command(zd_cli, 'wlaninfo --mesh-topology')
    logging.debug(mesh_topo_info)

    if ('illegal option' or 'command not found') in mesh_topo_info['raw_info']:
        errmsg = mesh_topo_info['raw_info']
        return (passmsg, errmsg)

    for mesh_ap in expected_mesh_ap_list:
        if mesh_ap not in mesh_topo_info['raw_info']:
            errmsg = 'Mesh AP[%s] is not recorded in Mesh topology' % mesh_ap
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --mesh-topology" worked well'
    return (passmsg, errmsg)

def test_mesh_history(zd_cli, expected_mesh_ap_list):
    errmsg = ''
    passmsg = ''
    logging.info('Verifying command "wlaninfo --mesh-history"')
    mesh_history_info = lib.zd.cli.get_wlaninfo_mesh_history(zd_cli, 'wlaninfo --mesh-history')
    logging.debug(mesh_history_info)

    if ('illegal option' or 'command not found') in mesh_history_info['raw_info']:
        errmsg = mesh_history_info['raw_info']
        return (passmsg, errmsg)

    for mesh_ap in expected_mesh_ap_list:
        if not mesh_history_info.get(mesh_ap)\
        or mesh_history_info.get(mesh_ap) == 'The information is not existed or NULL':
            errmsg = 'There is not any Mesh AP[%s] in CLI' % mesh_ap
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --mesh-history" worked well'
    return (passmsg, errmsg)

def test_show_pmk_info(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --pmk-cache"')
    all_pmk_info = lib.zd.cli.get_wlaninfo_pmk(zd_cli)
    logging.debug(all_pmk_info)

    if ('illegal option' or 'command not found') in all_pmk_info['raw_info']:
        errmsg = all_pmk_info['raw_info']
        return (passmsg, errmsg)

    if 'No PMK cache found' not in all_pmk_info['raw_info']\
    and all_pmk_info['pmk'] == 'The information is not existed or NULL':
        errmsg = 'There is not any PMK shown on CLI'
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --pmk-cache" worked well'
    return (passmsg, errmsg)

def test_show_wlan_group(zd_cli, expected_wlangroup):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --all-wlangroup"')
    all_wlangroup_info = lib.zd.cli.get_wlaninfo_wlangroup(zd_cli)
    logging.debug(all_wlangroup_info)

    if ('illegal option' or 'command not found') in all_wlangroup_info['raw_info']:
        errmsg = all_wlangroup_info['raw_info']
        return (passmsg, errmsg)

    if all_wlangroup_info['wlangroup'] == 'The information is not existed or NULL':
        errmsg = 'There is not any WLAN group shown on CLI'
        return (passmsg, errmsg)

    wlangroup_name_list = [wlangroup[1] for wlangroup in all_wlangroup_info['wlangroup']]
    if expected_wlangroup not in wlangroup_name_list:
        errmsg = 'The information of WLAN group [%s] is not shown in CLI' % expected_wlangroup
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-wlangroup" worked well'
    return (passmsg, errmsg)

def test_show_ap_group(zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --all-apgroup"')
    all_apgroup_info = lib.zd.cli.get_wlaninfo_apgroup(zd_cli)
    logging.debug(all_apgroup_info)

    if ('illegal option' or 'command not found') in all_apgroup_info['raw_info']:
        errmsg = all_apgroup_info['raw_info']
        return (passmsg, errmsg)

    if all_apgroup_info['apgroup'] == 'The information is not existed or NULL':
        errmsg = 'There is not any AP group shown on CLI'
        return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-apgroup" worked well'
    return (passmsg, errmsg)

def test_show_disc_ap(zd_cli, expected_ap):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "wlaninfo --all-disc-ap"')
    all_disc_ap_info = lib.zd.cli.get_wlaninfo_disc_ap(zd_cli)
    logging.debug(all_disc_ap_info)

    if ('illegal option' or 'command not found') in all_disc_ap_info['raw_info']:
        errmsg = all_disc_ap_info['raw_info']
        return (passmsg, errmsg)

    if expected_ap:
        if all_disc_ap_info['ap'] == 'The information is not existed or NULL'\
        or expected_ap not in all_disc_ap_info['ap']:
            errmsg = 'The information of AP[%s] is not shown in CLI'
            return (passmsg, errmsg)

    passmsg = 'command "wlaninfo --all-disc-ap" worked well'
    return (passmsg, errmsg)

def test_command_show_ap(zd, zd_cli):
    errmsg = ''
    passmsg = ''
    logging.info('Get all APs Info on ZD WebUI')
    all_ap_info_in_webui = zd.get_all_ap_info()
    logging.debug(all_ap_info_in_webui)

    logging.info('Verify command "show ap"')
    all_ap_info = lib.zd.cli.get_show_ap(zd_cli)
    logging.debug(all_ap_info)

    if ('illegal option' or 'command not found') in all_ap_info['raw_info']:
        errmsg = all_disc_ap_info['raw_info']
        return (passmsg, errmsg)

    if len(all_ap_info['ap']) != int(all_ap_info['total_ap'][0]):
        errmsg = 'There are %s aps in total but %s are recorded'
        errmsg = errmsg % (all_ap_info['total_ap'][0], len(all_ap_info['ap']))
        return (passmsg, errmsg)

    ap_info_on_webui = []
    for ap in all_ap_info_in_webui:
        ap_info_on_webui.append((ap['mac'], ap['ip_addr']))

    ap_info_in_cli = [(ap[1], ap[0]) for ap in all_ap_info['ap']]
    for ap in ap_info_on_webui:
        if ap not in ap_info_in_cli:
            errmsg = 'The information of the AP[%s] is not recorded in ZD CLI' % str(ap)
            return (passmsg, errmsg)

    passmsg = 'All APs%s are shown on ZD CLI correctly' % ap_info_on_webui
    return (passmsg, errmsg)

def test_command_show_station(zd_cli, expected_sta_info):
    errmsg = ''
    passmsg = ''
    logging.info('Verify command "show station"')
    all_sta_info = lib.zd.cli.get_show_station(zd_cli)
    logging.debug(all_sta_info)

    if ('illegal option' or 'command not found') in all_sta_info['raw_info']:
        errmsg = all_disc_ap_info['raw_info']
        return (passmsg, errmsg)

    if len(all_sta_info['sta']) != int(all_sta_info['total_sta'][0]):
        errmsg = 'There are %s stations in total but %s are recorded'
        errmsg = errmsg % (all_sta_info['total_sta'][0], len(all_sta_info['sta']))
        return (passmsg, errmsg)

    sta_info_in_cli = [(ap[2], ap[1]) for ap in all_sta_info['sta']]
    for sta in expected_sta_info:
        if sta not in sta_info_in_cli:
            errmsg = 'The information of the station[%s] is not recorded in ZD CLI' % str(sta)
            return (passmsg, errmsg)

    passmsg = 'All stations%s are shown on ZD CLI correctly' % expected_sta_info
    return (passmsg, errmsg)
