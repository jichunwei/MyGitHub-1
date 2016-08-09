'''
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
)


'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    shell_key = '!v54!',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'))
    _cfg['zd_cli'] = create_zd_cli_by_ip_addr(
                         _cfg['zd'].ip_addr,
                         _cfg['zd'].username,
                         _cfg['zd'].password,
                         _cfg['shell_key'],
                     )
    _cfg['zd'].init_messages_bundled(_cfg['zd_cli'])

    return _cfg


def do_test(cfg):
    logging.info('[TEST 01] Get ZD messages bundled')

    for x in cfg['zd'].messages.iteritems():
        print x

    pp(cfg['zd'].messages['MSG_admin_login'])

    cfg['result'] = 'PASS'
    cfg['message'] = ''
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

'''
2010-07-14 09:35:40,743 INFO     [TEA.Module u.zd.zd_messages_tea] tcfg:
{'u.zd.zd_messages_tea': None}
2010-07-14 09:35:50,477 DEBUG    Creating the Selenium Manager
2010-07-14 09:35:55,486 INFO     Creating Zone Director component [192.168.0.2]
2010-07-14 09:35:55,486 DEBUG    {'browser_type': 'firefox',
 'config': {'password': 'admin', 'username': 'admin'},
 'https': True,
 'ip_addr': '192.168.0.2',
 'selenium_mgr': <RuckusAutoTest.common.SeleniumControl.SeleniumManager instance at 0x036BDDF0>}
2010-07-14 09:36:18,279 DEBUG    Updating info in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-07-14 09:36:18,279 DEBUG    Updating const in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-07-14 09:36:18,279 DEBUG    Updating _log_to_the_page in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-07-14 09:36:18,279 DEBUG    Updating xlocs in RuckusAutoTest.components.lib.zd.control_zd module to the version 8.0.0.0
2010-07-14 09:36:18,296 DEBUG    Updating LOCATORS_SPEEDFLEX in RuckusAutoTest.components.lib.zd.speedflex_zd module to the version 9.0.0.0
2010-07-14 09:36:18,296 DEBUG    Updating LOCATORS_CFG_WLANS in RuckusAutoTest.components.lib.zd.wlan_zd module to the version 9.0.0.0
2010-07-14 09:36:18,296 DEBUG    Updating info in RuckusAutoTest.components.ZoneDirector class instance to the version 8.0.0.0
2010-07-14 09:36:18,296 DEBUG    Updating info in RuckusAutoTest.components.ZoneDirector class instance to the version 8.2.0.0
2010-07-14 09:36:18,296 DEBUG    Updating info in RuckusAutoTest.components.ZoneDirector class instance to the version 9.0.0.0
2010-07-14 09:39:08,733 INFO     Creating ZoneDirectorCLI component [192.168.0.2]
2010-07-14 09:39:08,733 DEBUG    {'ip_addr': '192.168.0.2',
 'password': 'admin',
 'shell_key': '!v54!',
 'username': 'admin'}
2010-07-14 09:39:08,733 DEBUG    starting thread (client mode): 0x3b97730L
2010-07-14 09:39:08,733 INFO     Connected (version 2.0, client dropbear_0.48)
2010-07-14 09:39:08,749 DEBUG    kex algos:['diffie-hellman-group1-sha1'] server key:['ssh-rsa', 'ssh-dss'] client encrypt:['aes128-cbc', '3des-cbc', 'aes256-cbc', 'twofish256-cbc', 'twofish-cbc', 'twofish128-cbc', 'blowfish-cbc'] server encrypt:['aes128-cbc', '3des-cbc', 'aes256-cbc', 'twofish256-cbc', 'twofish-cbc', 'twofish128-cbc', 'blowfish-cbc'] client mac:['hmac-sha1-96', 'hmac-sha1', 'hmac-md5'] server mac:['hmac-sha1-96', 'hmac-sha1', 'hmac-md5'] client compress:['none'] server compress:['none'] client lang:[''] server lang:[''] kex follows?False
2010-07-14 09:39:08,749 DEBUG    Ciphers agreed: local=aes128-cbc, remote=aes128-cbc
2010-07-14 09:39:08,749 DEBUG    using kex diffie-hellman-group1-sha1; server key type ssh-rsa; cipher: local aes128-cbc, remote aes128-cbc; mac: local hmac-sha1, remote hmac-sha1; compression: local none, remote none
2010-07-14 09:39:08,875 DEBUG    Switch to new keys ...
2010-07-14 09:39:08,890 DEBUG    Attempting password auth...
2010-07-14 09:39:08,890 DEBUG    userauth is OK
2010-07-14 09:39:08,890 INFO     Authentication (password) successful!
2010-07-14 09:39:08,905 DEBUG    [chan 1] Max packet in: 34816 bytes
2010-07-14 09:39:08,905 DEBUG    [chan 1] Max packet out: 8000 bytes
2010-07-14 09:39:08,905 INFO     Secsh channel 1 opened.
2010-07-14 09:39:08,921 DEBUG    [chan 1] Sesch channel 1 request ok
2010-07-14 09:39:08,921 DEBUG    [chan 1] Sesch channel 1 request ok
2010-07-14 09:39:10,232 INFO     Login to ZD [192.168.0.2] successfully!
2010-07-14 09:39:10,232 INFO     ZoneDirectorCLI is next generation CLI
2010-07-14 09:39:11,980 DEBUG    System Name         : ruckus

    IP Addr             : 192.168.0.2/255.255.255.0

    MAC Addr            : 00:07:18:01:02:01

    Model               : ZD3250

    Serial              : 800-782587

    Version             : 9.0.0.0 build 25

    Management VLAN:    : disabled

    Memory Utilization  : 8% (75100160 bytes) used, 92% (852869120 bytes) free

    Smart Redundancy    : active/disconnected

    Active Eth          : eth1
2010-07-14 09:39:13,290 INFO     Login to ZD [192.168.0.2] successfully!
2010-07-14 09:39:13,729 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:14,165 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:14,602 INFO     Creating SSH session for Zone Director  192.168.0.2
2010-07-14 09:39:14,602 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:16,788 DEBUG
2010-07-14 09:39:18,098 INFO     Login to ZD [192.168.0.2] successfully!
2010-07-14 09:39:18,536 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:27,523 DEBUG    Getting bundled messages at /bin/messages
2010-07-14 09:39:29,270 DEBUG    # This is a message file. First line should be either a comment or blank

# use '#' to indicate comments

# a line starting with ' ' will not be processed, either.



# this is for ALL locales (currently events will NOT be localized for easier support and prevention of awkard terminologies)

MSG_admin_restarted=System restarted

MSG_admin_restart=System restarted by administrator.

MSG_admin_shutdown=System shutdown by administrator.

MSG_admin_upgrade=System upgraded.

MSG_admin_replace_cert=SSL certificate replaced by administrator.

MSG_admin_replace_privatekey=Private key replaced by administrator.

MSG_admin_renew_cert=Private key and SSL certificate renewed by administrator.

MSG_admin_auto_restore_cert=The certificate does not match ZD's private key, ZD will restore default certificate and private key.

MSG_admin_restore_saved=System configuration restored by administrator.

MSG_admin_restore_default=System configuration restored to factory default by administrator.

MSG_admin_set_dhcp=System uses DHCP to obtain IP address.

MSG_admin_set_ip=System IP address is set to {ip}.

MSG_admin_set_hostname=System name is set to {hostname}.

MSG_admin_change_passwd=Admin password changed.

MSG_admin_system_installed=Admin has completed the Installation Wizard.

MSG_admin_system_upgraded_success=ZD image has been upgraded from {old-version} to {new-version}

MSG_admin_system_upgraded_rollback=ZD upgrade failed rollback to {old-version}

MSG_admin_system_upgraded_reboot_rollback=ZD upgrade failed, a system reboot is required to rollback to {old-version}

MSG_admin_system_upgraded_fail=ZD upgrade failed, please try again

MSG_admin_system_integrity_check_success=ZD {image} image integrity check passed.

MSG_admin_system_integrity_check_fail=ZD {image} image is corrupted, use Software Upgrade to repair

MSG_admin_system_auto_recovery_success=ZD auto-recovery successful

MSG_admin_system_auto_recovery_fail=ZD auto-recovery failed



MSG_fm_login=FM logs in from {ip}

MSG_fm_login_failed=FM logs in failure from {ip}

MSG_admin_login={admin} logs in from {ip}

MSG_admin_login_failed={admin} logs in failure from {ip}

MSG_admin_auth_conn_error=Unable to authenticate {admin} from {ip} using the specified authentication server (connection error or timeout)

MSG_admin_login_lockout={admin} from {ip} is locked out for 5 minutes (3 failed login attempts)

MSG_admin_login_attack_lockout={admin} is locked out for 1 hour (20 failed login attempts in 5 minutes)

MSG_admin_logout={admin} logged out from {ip}

MSG_admin_delall_clients=All clients disconnected by admin

MSG_admin_scan_all=Administrator initiates an active scan from all AP's

MSG_admin_scan_ap=Administrator initiates an active scan from {ap}

MSG_admin_templic_expired=Temporary license {name} has expired and all features of this license are disabled

MSG_admin_templic_oneday=Temporary license {name} will expire within one day

MSG_admin_templic_twodays=Temporary license {name} will expire within two days

MSG_admin_init_dhcpp=Rogue DHCP server detector enabled

MSG_admin_stop_dhcpp=Rogue DHCP server detector disabled

MSG_admin_trig_dhcpp=Rogue DHCP server detector detected

MSG_admin_rogue_dhcp_server=Rogue DHCP server detected on {ip}

MSG_admin_set_dhcps=DHCP server enabled with IP range from {ip-start} to {ip-end}

MSG_admin_set_dhcps_failed=Failure to enable DHCP server

MSG_admin_stop_dhcps=DHCP server disabled

MSG_admin_enable_tr069=FlexMaster management enabled from {url}

MSG_admin_disable_tr069=FlexMaster management disabled

MSG_admin_enable_snmpd=SNMP agent enabled with RO-community {ro-community} and RW-community {rw-community}

MSG_admin_disable_snmpd=SNMP agent disabled

MSG_admin_enable_snmptrap=SNMP Trap {trap-ip} enabled

MSG_admin_disable_snmptrap=SNMP Trap disabled

MSG_admin_enable_ap_mgmt_vlan=Set AP management VLAN to {vlan}

MSG_admin_disable_ap_mgmt_vlan=AP management VLAN setting disabled

MSG_admin_keep_ap_mgmt_vlan=AP management VLAN enabled with AP settings

MSG_admin_enable_zd_mgmt_vlan=ZoneDirector management VLAN enabled with {vlan}

MSG_admin_disable_zd_mgmt_vlan=ZoneDirector management VLAN disabled

MSG_admin_enable_both_limited_zd=Provision all AP's with primary ZoneDirector {ip1} and secondary ZoneDirector {ip2}

MSG_admin_enable_one_limited_zd=Provision all AP's with primary ZoneDirector {ip1}

MSG_admin_disable_limited_zd=Remove AP's primary and secondary ZoneDirector settings

MSG_admin_change_workmode=Change ZoneDirector working mode to {mode}

MSG_admin_create_addif=Additional management interface {ip} created

MSG_admin_remove_addif=Additional management interface {ip} removed

MSG_admin_update_addif=Additional management interface {ip} updated

MSG_admin_enable_cltr=Smart Redundancy is {type}

MSG_admin_cltr_peerip=[Smart Redundancy] Peer Device IP Address changed by Administrator

MSG_admin_cltr_password=[Smart Redundancy] Shared Secret changed by Administrator



MSG_user_login_failed_for_guestpass={user-name} from {ip} failed to log in for guest pass generation

MSG_user_login_failed_for_prov={user-name} from {ip} failed to log in for wireless access provisioning

MSG_user_login_failed_for_access={user} from {ip} failed to log in. No permission or incorrect credentials.

MSG_user_login_failed_for_access2={user} failed to log in. No permission or incorrect credentials.

MSG_user_auth_conn_error=Unable to authenticate {user-name} from {ip} using the specified authentication server (connection error or timeout)

MSG_RADIUS_service_outage=Radius server {server} has not responded to multiple requests.  {reason}.



MSG_guest_ok={user} from {ip} approved for guest access (guest pass was generated by {created-by})

MSG_guest_noauth_ok=Guest from {ip} approved for guest access



MSG_AC_license_ap_different=ZoneDirector and redundant ZoneDirector have different number of licensed APs.

MSG_AC_working_mode=ZoneDirector automatically swaps working mode to {mode}

MSG_AP_joined={ap} joins with uptime {uptime} s

MSG_AP_join_failed={ap} fails to join

MSG_AP_join_failed_model=Model{model} is not supported; connection request from {ap} refused

MSG_AP_join_too_many=Connection request from {ap} refused; AP limit reached.

MSG_AP_join_invalid_country_code=Connection request from {ap} refused; country code mismatch.

MSG_AP_hardware_problem=Hardware problem detected during {ap} attempt to join {reason}.

MSG_AP_lost_heartbeat={ap} heartbeats lost

MSG_AP_lost=Lost contact with {ap}

MSG_MESH_STATE_UPDATE_ROOT_NO_CHAN={ap} state set to {new-state} with downlink {downlink-state}

MSG_MESH_STATE_UPDATE_ROOT={ap} state set to {new-state} on channel {channel-radio} with downlink {downlink-state}

MSG_MESH_STATE_UPDATE_MAP_NO_CHAN={ap} state set to {new-state} uplinks to {meshap} across {hops} hops with downlink {downlink-state}

MSG_MESH_STATE_UPDATE_MAP={ap} state set to {new-state} uplinks to {meshap} across {hops} hops on channel {channel-radio} with downlink {downlink-state}

MSG_MAP_uplink_connected=Mesh {ap} connects to Mesh {meshap} with RSSI {rssi} across {mesh-depth} links

MSG_MAP_uplink_to_root_connected=Mesh {ap} connects to Root {rootap} with RSSI {rssi} across {mesh-depth} links

MSG_MAP_downlink_connected=Mesh {ap} accepts Mesh {meshap} connection

MSG_MAP_root_downlink_connected=Root {ap} accepts Mesh {meshap} connection

MSG_MAP_connect_fail_auth=Mesh {meshap} fails to connect to {ap} (authentication invalid)

MSG_MAP_connect_fail_depth_exceeded=Mesh {mashap} fails to connect; (no AP within {max-hops} mesh links was found)

MSG_MAP_connect_block=Mesh {meshap} fails multiple authentication attempts when joining {ap}. Mesh {meshap} is temporarily blocked from this ap for {block}

MSG_MAP_connect_unblock=Removed temporary blocking from Mesh {meshap} to {ap}

MSG_MAP_disconnect=Mesh {meshap} disconnects from {ap}

MSG_MAP_uplink_disconnect=Mesh {ap} disconnects from uplink {meshap}

MSG_MAP_isolate=Isolated Mesh {ap} detected

MSG_LAP_uplink_connected=eMesh {ap} connects to Mesh {meshap} across {mesh-depth} links {rea}

MSG_MAP_uplink_LAP_connected=Mesh {ap} connects to eMesh {linkap} with RSSI {rssi} across {mesh-depth} links {rea}

MSG_MAP_downlink_LAP_connected=Mesh {ap} accepts eMesh {linkap} connection

MSG_LAP_downlink_MAP_connected=eMesh {ap} accepts Mesh {meshap} connection

MSG_LAP_uplink_MAP_disconnect=eMesh {ap} disconnects from uplink Mesh {meshap}

MSG_MAP_uplink_LAP_disconnect=Mesh {ap} disconnects from uplink eMesh {linkap}

MSG_MAP_downlink_LAP_disconnect=eMesh {linkap} disconnects from Mesh {ap}

MSG_LAP_downlink_MAP_disconnect=Mesh {meshap} disconnects from eMesh {ap}

MSG_MAP_accept_MAP_hops_warn={ap} accepts Mesh {meshap} with {hops} hops (hop count exceeds the threshold {threshold} hops).

MSG_MAP_accept_MAP_fanout_warn={ap} accepts Mesh {meshap} and current AP's downlinks {fanout} exceeds threshold {threshold}.

MSG_AP_delete={ap} deleted by administrator

MSG_AP_reset={ap} restarted by administrator

MSG_AP_factory_restore={ap} reset to factory default by administrator

MSG_AP_activate_mesh={ap} reset to enable mesh function

MSG_AP_deactivate_mesh={ap} reset to disable mesh function

MSG_AP_country_code_change={ap} reset due to country code change

MSG_AP_chan_comp_change={ap} reset due to channel compatibility change

MSG_AP_mgmt_vlan_change={ap} reset due to management vlan change

MSG_AP_ip_change={ap} reset due to ip address change

MSG_AP_mesh_mode_change={ap} reset due to mesh mode change

MSG_AP_config_out_of_sync={ap} reset because its configuration is out of sync with ZoneDirector

MSG_AP_approv_auto=A new {ap} requests to join and is automatically approved

MSG_AP_approv_pending=A new {ap} requests to join, pending approval of administrator

MSG_AP_incorrect_config={ap} fails to join because of incorrect configuration; unable to authenticate this AP.

MSG_AP_incorrect_config_remove_ap=An previously known {ap} fails to join due to incorrect configuration. Remove its record from the system.

MSG_AP_auth_failed=An {ap} fails to join because of failed authentication.

MSG_AP_no_mesh_uplink=An {ap} fails to join because uplink Mesh {meshap} not found.

MSG_AP_channel_change={ap} detects interference on radio {radio} and switches from channel {from-channel} to channel {to-channel}.

MSG_AP_dfs_radar_event={ap} detects radar burst on radio {radio} and channel {dfs-channel} goes into non-occupancy period.

MSG_AP_dfs_channel_change={ap} non-occupancy period expires on radio {radio} and switches back to channel {to-channel}.

MSG_AP_tx_power_decrease={ap} detects interference on radio {radio} and changes transmit power from {from-tx} power to {to-tx} power.

MSG_AP_tx_power_increase={ap} detects less interference on radio {radio} and changes transmit power from {from-tx} power to {to-tx} power.

MSG_AP_speedflex_to_ap=SpeedFlex: {ap} to {apto} - downlink {downlink}, uplink {uplink}

MSG_AP_speedflex_to_ap_downlink=SpeedFlex: {ap} to {apto} - downlink {downlink}

MSG_AP_speedflex_to_ap_uplink=SpeedFlex: {ap} to {apto} - uplink {uplink}

MSG_AP_speedflex_to_zd=SpeedFlex: {ap} to ZoneDirector - downlink {downlink}, uplink {uplink}

MSG_AP_speedflex_to_zd_downlink=SpeedFlex: {ap} to ZoneDirector - downlink {downlink}

MSG_AP_speedflex_to_zd_uplink=SpeedFlex: {ap} to ZoneDirector - uplink {uplink}



MSG_rogue_AP_detected=A new {rogue} with {ssid} is detected

MSG_lanrogue_AP_detected={rogue}/{ip} with {ssid} is detected by {ap} on the local wired network

MSG_ad_hoc_network_detected=A new ad-hoc network {adhoc} with {ssid} is detected

MSG_SSID_spoofing_AP_detected=A new SSID-spoofing {rogue} with {ssid} is detected

MSG_MAC_spoofing_AP_detected=A new MAC-spoofing {rogue} with {ssid} is detected

MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.

MSG_AP_80211_DOS_probe_req_flood={ap} detects excessive probe requests on radio {radio}.

MSG_AP_80211_DOS_mgmt_flood={ap} detects excessive 802.11 management frames on radio {radio}.

MSG_AP_being_upgraded={ap} joins with different firmware/custom file version and is being upgraded.

MSG_AP_image_upgrade_success={ap} image has been upgraded from {old-ver} to {new-ver}

MSG_AP_image_upgrade_success_w_err={ap} image has been upgraded from {old-ver} to {new-ver} after {err-cnt} retries.

MSG_AP_image_upgrade_failed=Failure to upgrade {ap} image from {old-ver} to {new-ver}

MSG_AP_image_upgrade_failed_ip=Failure to upgrade {ap} image from {old-ver} to {new-ver}, possibly due to incorrect IP address on AP.

MSG_AP_image_upgrade_failed_w_err=Failure to upgrade {ap} image from {old-ver} to {new-ver} after {err-cnt} retries

MSG_AP_bkupimg_upgrade_success={ap} backup image has been upgraded from {old-ver} to {new-ver}

MSG_AP_bkupimg_upgrade_success_w_err={ap} backup image has been upgraded from {old-ver} to {new-ver} after {err-cnt} retries.

MSG_AP_bkupimg_upgrade_failed=Failure to upgrade {ap} backup image from {old-ver} to {new-ver}

MSG_AP_bkupimg_upgrade_failed_ip=Failure to upgrade {ap} backup image from {old-ver} to {new-ver}, possibly due to incorrect IP address on AP.

MSG_AP_bkupimg_upgrade_failed_w_err=Failure to upgrade {ap} backup image from {old-ver} to {new-ver} after {err-cnt} retries

MSG_AP_upgrade_custom_succ={ap} custom file has been upgraded to {new-custom}.

MSG_AP_upgrade_custom_fail=Fail to upgrade {ap} custom file to {new-custom}.

MSG_AP_gen_supportxt=Receiving System Info from {ap}

MSG_AP_populate_failed=Failure to initialize the configuration of all APs because AP limit exceeded.

MSG_AP_gen_RFInfo=Receiving RF Info from {ap}



MSG_ad_hock_interference_detected=An ad-hock network {adhoc} with {ssid} interferes with {ap} on channel {channel}.

MSG_mgmtip_changed=Management IP changed by {admin}

MSG_sysname_changed=System identification changed by {admin}

MSG_systime_changed=System time changed by {admin}

MSG_WLAN_modified={wlan} modified by {admin}

MSG_WLAN_created={wlan} created by {admin}

MSG_WLAN_deleted={wlan} deleted by {admin}

MSG_WLAN_enabled={wlan} enabled by administrator.

MSG_WLAN_disabled={wlan} disabled by administrator.

MSG_WLAN_enabled_by_schedule={wlan} enabled according to service schedule.

MSG_WLAN_disabled_by_schedule={wlan} disabled according to service schedule.



MSG_AP_radio_enabled=Radio {radio} of {ap} enabled by administrator.

MSG_AP_radio_disabled=Radio {radio} of {ap} disabled by administrator.

MSG_WLAN_group_switch=Radio {radio} of {ap} has switched wlan group from {old-group} to {new-group}



MSG_cltr_restore_saved=[Smart Redundancy] Peer ZoneDirector{peer-ip} has been restored.

MSG_cltr_upgrade_from_peer=[Smart Redundancy] System is being upgraded per command from peer ZoneDirector{peer-ip}

MSG_cltr_restore_saved_from_peer=[Smart Redundancy] System restored command received from peer ZoneDirector{peer-ip}

MSG_cltr_no_file=[Smart Redundancy] Could not retrieve necessary file from peer ZoneDirector{peer-ip}. Operation aborted.

MSG_cltr_system_upgraded_success=[Smart Redundancy] Peer ZoneDirector{peer-ip} image has been upgraded from {old-version} to {new-version}. System is being upgraded.

MSG_cltr_req_peer_upgrade=[Smart Redundancy] System upgraded, peer ZoneDirector upgrade pending.

MSG_cltr_system_upgraded_fail=[Smart Redundancy] Peer ZoneDirector{peer-ip} upgrade failed.

MSG_cltr_sync_local_conf=[Smart Redundancy] Configuration sent to peer ZoneDirector{peer-ip}

MSG_cltr_sync_peer_conf=[Smart Redundancy] System ready to sync configuration from peer ZoneDirector{peer-ip}

MSG_cltr_sync_last_conf=[Smart Redundancy] Sync configuration from peer ZoneDirector{peer-ip}

MSG_cltr_sync_conf_failed=[Smart Redundancy] Failed to sync configuration from peer ZoneDirector{peer-ip} due to {lmsg}

MSG_cltr_send_failover=[Smart Redundancy] Admin forces a failover to peer ZoneDirector{peer-ip}

MSG_cltr_receive_failover=[Smart Redundancy] Received failover command to change state to {to-state} from peer ZoneDirector{peer-ip}

MSG_cltr_version_mismatched=[Smart Redundancy] <strong>Failed!</strong> Firmware version mismatch

MSG_cltr_model_mismatched=[Smart Redundancy] <strong>Failed!</strong> Model mismatch (i.e. ZD1000 cannot pair with ZD3000)

MSG_cltr_ip_mismatched=[Smart Redundancy] <strong>Failed!</strong> Connection from peer ZoneDirector IP address is different from that configured

MSG_cltr_maxap_mismatched=[Smart Redundancy] <strong>Failed!</strong> Both ZoneDirectors must have licenses for the same number of APs

MSG_cltr_password_mismatched=[Smart Redundancy] Received unrecognized command from peer ZoneDirector{peer-ip}, it may be caused by Shared Secret mismatch

MSG_cltr_change_state=[Smart Redundancy] System state changed to {state} due to {reason}

MSG_cltr_same_conf=[Smart Redundancy] Configuration of peer ZoneDirector{peer-ip} is in sync.

MSG_cltr_change_to_active=[Smart Redundancy] Peer ZoneDirector{peer-ip} not found, system changed to active state.

MSG_cltr_active_connected=[Smart Redundancy] Peer ZoneDirector{peer-ip} connected, system is in active state.

MSG_cltr_standby_connected=[Smart Redundancy] Peer ZoneDirector{peer-ip} connected, system is in standby state.

MSG_cltr_active_disconnected=[Smart Redundancy] Lost connection to peer ZoneDirector{peer-ip}, system is in active state.

MSG_cltr_standby_disconnected=[Smart Redundancy] Lost connection to peer ZoneDirector{peer-ip}, system is in standby state.

MSG_cltr_upgrade_disconnected=[Smart Redundancy] System is currently being upgraded; disconnected from peer ZoneDirector.

MSG_cltr_peer_upgrade_disconnected=[Smart Redundancy] Peer ZoneDirector is being upgraded.

MSG_cltr_peer_not_back=[Smart Redundancy] Peer ZoneDirector did not reconnect after upgrade. System is being upgraded automatically.

MSG_cltr_local_action_done=[Smart Redundancy] System received command {cmd} from peer ZoneDirector but the command has been completed already due to connection timeout.

MSG_cltr_failed_get_uploaded=[Smart Redundancy] Failure to retrieve user customization files, eg. map files, from peer ZoneDirector{peer-ip}.

MSG_cltr_failed_untar_uploaded=[Smart Redundancy] User customization files, eg. map files, received from peer ZoneDirector{peer-ip}, but failed to extract.

MSG_cltr_admin_upg_from_local=[Smart Redundancy] Peer ZoneDirector{peer-ip} is being upgraded by administrator to sync up firmware version.

MSG_cltr_admin_upg_from_peer=[Smart Redundancy] System is being upgraded by administrator to sync up firmware version.



MSG_VAP_init={wlan} has been deployed on radio {radio} of {ap} with {vap}

MSG_VAP_del= {wlan} with {vap} has been removed from radio {radio} of {ap}

MSG_VAP_upd={wlan} with {vap} configuration has been updated on radio {radio} of {ap}

MSG_VAP_init_retry={wlan} with {vap} has been deployed on radio {radio} of {ap} after retry.

MSG_VAP_upd_retry={wlan} with {vap} configuration has been updated on radio {radio} of {ap} after retry

MSG_VAP_del_retry={wlan} with {vap} has been removed from radio {radio} of {ap} after retry

MSG_VAP_init_failed=Failure to deploy {wlan} on radio {radio} of {ap}

MSG_VAP_del_failed=Failure to remove {wlan} from radio {radio} of {ap}

MSG_VAP_upd_failed=Failure to update {wlan} configuration of radio {radio} of {ap}

MSG_VAP_init_failed_retry=Failure to deploy {wlan} on radio {radio} of {ap}, try again.

MSG_VAP_upd_failed_retry=Failure to update {wlan} configuration of radio {radio} of {ap},try again.

MSG_VAP_del_failed_retry=Failure to remove {wlan} configuration of radio {radio} of {ap},try again.



MSG_client_join={user} joins {wlan} from {ap}

MSG_client_join_with_vlan={user} with {vlan} joins {wlan} from {ap}

MSG_client_join_failed={user} fails to join {wlan} from {ap}

MSG_client_join_failed_AP_busy={user} is refused access to {wlan} from {ap} because there are too many users on that AP, WLAN, or Radio.

MSG_client_policy_mismatch={user} fails to join {wlan} from {ap}

MSG_client_auth_failed={user} fails to join {wlan} from {ap} due to authentication failure

MSG_client_timeout={user} idle timeout and disconnected from {wlan} at {ap}

MSG_client_disconnect={user} disconnects from {wlan} at {ap}

MSG_client_roam_out={ap} radio {radiofrom} detects {user} in {wlan} roams out to {apto}

MSG_client_roam_in={ap} radio {radioto} detects {user} in {wlan} roams from {apfrom}

MSG_client_del_by_admin={user} disconnected by admin from {wlan} at {ap}

MSG_client_disconnect_internal_err={user} disassociated from {wlan} due to timeout waiting for AP to add station.

MSG_client_join_rssi_warning={user} joins {wlan} from {ap} with {rssi} and client's rssi is below threshold {rssi-threshold}



MSG_client_disconnect_auth_timeout={user} disassociated from {wlan} due to timeout during authentication.

MSG_low_signal={user} of {wlan} encountered low signal

MSG_client_unauthorized={user} tries to connect to an unauthorized {wlan}

MSG_client_session_expired={user} session time limit exceeded; session terminated

MSG_client_web_auth={user} of {wlan} is authorized

MSG_client_web_not_auth_internal_error={user} of {wlan} not authorized due to internal error

MSG_client_web_not_auth_no_such_user={user} of {wlan} not authorized; no such user

MSG_client_repeat_auth_fail={user} repeatedly fails authentication when joining {wlan} at {ap}.

MSG_client_auth_fail_block={user} fails authentication too many times in a row when joining {wlan} at {ap}. {user} is temporarily blocked from the system for {block}.

MSG_user_login_fail_block={user} fails to login {wlan} at {ap} too many times and is temporarily blocked from login for {block}.

MSG_client_too_many_login={mac} attempts to login to {wlan} at {ap} too many times and is temporarily blocked from login for {block}.

MSG_user_unblock=Temporary blocking of User{user-name} unblocked.

MSG_client_unblock=Temporary blocking of {mac} unblocked.

MSG_user_DPSK_acquire=User{user-name} has acquired a new Dynamic PSK.

MSG_batch_DPSK_acquire=Administrator has acquired batch generation of {num} new Dynamic PSKs.

MSG_client_DPSK_expired={user}'s access is restricted because of an expired Dynamic PSK.

MSG_client_DPSK_renew_done={user} has renewed a Dynamic PSK.

MSG_client_reconnect_within_grace_period={user} reconnects to {ap} within grace period.  No additional authentication is required.



MSG_TR069d_verify_download_file_fail=FlexMaster {url} sends a bad {file} file.

MSG_TR069d_upgrade_image=FlexMaster {url} issues image upgrade command.

MSG_TR069d_execute_reboot_command=FlexMaster {url} issues restart command.

MSG_TR069d_clone_configuration=FlexMaster {url} issues restore command {action}.

MSG_TR069d_inform_return=ZoneDirector contacts FlexMaster {status}.

MSG_TR069d_write_template=FlexMaster {url} issues command to write configuration template.

MSG_TR069d_template_success=ZoneDirector successfully writes configuration template successfully cmdkey {cmdkey}.

MSG_TR069d_template_fail=Write template fail due to {err} cmdkey {cmdkey}.

MSG_TR069d_download_file_fail= ZoneDirector fails to retrieve template file from FlexMaster{url} cmdkey {cmdkey}.

MSG_TR069d_download_file_timeout= ZoneDirector file download from FlexMaster{url} timeout cmdkey {cmdkey}.

MSG_TR069d_fmalarm_list_changed=FlexMaster {url} changes the FlexMaster monitoring event list.

MSG_TR069d_standby_skip_command=ZoneDirector is not Active and skips FlexMaster {url} command cmdkey {cmdkey}.



MSG_RADIUS_auth_failover=SSID{id} RADIUS authenticaion server {change} to {server}.

MSG_RADIUS_acct_failover=SSID{id} RADIUS accounting server {change} to {server}.

MSG_RADIUS_webauth_failover=RADIUS authenticaion server {change} to {server}.



# Some common terminologies that shouldn't be localized

IPAddress=IP Address

MgmtVlanID=VLAN

IP_Address=IP Address

MAC_Address=MAC Address

Netmask=Netmask

Gateway=Gateway

AccessPoint=Access Point

BSSID=BSSID

Diagnostics=Diagnostics



# API-level error messages

API_IdMissing='id' is required

API_NameMissing='name' is required

API_OneObjRequired=One and only one object with name '{objname}' should be supplied

API_ObjNotExist=The saving conf {name} does not exist in current or default database

API_AdminNameInvalid=Invalid username for 'admin'

API_AdminPassInvalid=Invalid password for 'admin'



CF_PSK=PSK

CF_open=Open

CF_shared=Shared

CF_802.1x-eap=802.1x EAP

CF_mac-auth=MAC Address

CF_wpa=WPA

CF_wpa2=WPA2

CF_wpa-mixed=WPA-Mixed

CF_wep64=WEP-64 (40 bit)

CF_wep128=WEP-128 (104 bit)

CF_tkip=TKIP

CF_aes=AES

CF_auto=AUTO

CF_none=None

CF_HEX=HEX

CF_VLAN=VLAN

CF_WLAN=WLAN

CF_AP=AP

CF_SSID=SSID



CLI=CLI

ZDCLI=ZD CLI

AD_APCli=AP/ZD CLI

AD_APCliDesc=Enter your command and click the CLI of an AP/ZD to execute.  Tips: Once you have selected an AP/ZD, you can execute directly by pressing the Enter key.

AD_APCliCmdSeperator=------ Executing CMD [{1}] at Machine [{2}]{3} ------



# User



UR_Username=User Name

UR_Password=Password

UR_Next=Next &gt;

UR_Back=&lt; Back

UR_Login=Log In

UR_Print=Print Instructions

UR_PrintAll=Print All Instructions Below



UR_GuestAuthenticated=Authenticated

UR_GuestAuthenticatedDesc=You are successfully authenticated as a wireless network guest, with limited Internet access (Web, email) per company policies.

UR_GuestTou=Terms of Use

UR_GuestTouDesc=Please review the terms of use before continuing to use the wireless network:

UR_Redirecting=Redirecting

UR_RedirectingDesc=Please wait for a few seconds...

UR_WifiValid=Your guest access is valid until

UR_WirelessAccess=Wireless Access

UR_WelcomeWifi=Welcome to the Guest Access login page.

UR_ApplyGuest=Type or paste in the text of your guest pass.

UR_GuestPass=Guest Pass

UR_InvalidGuest=This is an invalid Guest Pass. Please try again.

UR_GuestInfo=Guest Information

UR_GuestInfoDesc=Please enter the following information about your guest pass user

UR_GuestGenType=Creation Type

UR_PersonVisit=Person to visit

UR_ReasonVisit=Reason of visit

UR_GuestRemarks=Remarks

UR_ValidFor=Valid for

UR_GuestKey=Key

UR_GuestNumber=Number

UR_GuestWlan=WLAN



UR_GuestPassGene=Guest Pass Generated

UR_GuestPassDesc=Here is the generated guest pass for

UR_GuestPassValid1=This guest pass is valid for

UR_GuestPassValid2=once activated, and has to

UR_GuestPassValid3=be activated before

UR_GuestPassValidUntil=This guest pass is valid until

UR_GuestSharedGuestpass=Allow multiple guests to share a single guest pass

UR_GuestSharable=Sharable

UR_GuestReauth=Session

UR_GuestReauthDesc=Each guest re-logs in after



UR_ForAdmin=For admin

UR_ClickHere=click here



UR_WlanConf=Corporate WLAN Configuration

UR_WlanInstruction1=To set up your wireless network connection, follow these steps:

UR_WlanInstruction2=If the WLAN Connector download does not start in five seconds, please

UR_WlanProv=Save prov.exe to your desktop. Once completed, go to your desktop, double-click the prov.exe icon.

UR_ProvExe=prov.exe

UR_ProvDone=After your network connection is activated, the wireless icon (in the system tray) will change. Your computer will be automatically reconnected to the secured corporate network.

UR_WlanImportCert1=Install certificate by

UR_WlanImportCert2=and leave the default setting when you go through the certificate installation wizard (For Mac/iPhone users, installation password is the same as login password)

UR_ProvAuto=To download the auto activation script,

UR_ProvManual=If you encounter any problem or would like to manually set up your wireless access,



UR_RequestGuest=Request a Guest Pass

UR_WlanProvision=WLAN Connection Activation

UR_LoginDesc=Please log in, using your user name and password.

UR_LoginFail=Either your user name or password is incorrect. Please try again.

UR_Authenticating=Authenticating...

UR_Authenticated=Authenticated

UR_Abort=Abort

UR_CantGeneratePass=Guest Pass generation is not allowed

UR_CantGeneratePassDesc=You are not authorized to generate guest passes. Please contact the network administrator for more information.

UR_CantAuthGuest=Guest Pass cannot be used

UR_CantAuthGuestDesc=Guest passes can only be used when you are connected to the guest WLAN. Please make sure you are connected to the guest WLAN

UR_ErrBack=To go back to the previous screen,

UR_EmptyBatchPass=The uploaded profile does not contain correct information. Please try another file.

UR_NoGuestWlan=No Guest WLAN

UR_NoGuestWlanDesc=There is no guest WLAN for guest. Please contact the network administrator for more information.

UR_NoProfile=No Wireless Access Granted

UR_NoProfileDesc=No Zero-IT activated WLAN configuration can be provided for you. Please contact the network administrator for more information or connect to the desired WLAN directly.

UR_NoReauthTime=Re-auth time must be a positive integer.

UR_WebAuthRequired=Authentication Required for Wireless Access

UR_UserAuthenticated=Authenticated

UR_UserAuthenticatedDesc=You are successfully authenticated as a wireless network user.

UR_WebAuthNotAuthorized=Wireless Access Denied

UR_WebAuthNotAuthorizedDesc=You are not allowed to access this WLAN

UR_WifiAccess=Wireless Network Access

UR_WifiChanged=Wireless Network Access Re-Activation

UR_WifiChangedDesc=Your computer's wireless access configuration has expired, and you must re-activate your authorization.

UR_WifiChangedWizard=This wizard will help you quickly re-configure your access authorization. Click Next to get started.



UR_WelWifi=Getting Started with the Wireless Access Activation

UR_WelWifiDesc=This will help you activate your wireless access quickly. First, please identify yourself:

UR_WelUser=Wireless Access Portal

UR_WelUserDesc=Welcome to the ZoneDirector's Wireless Access Portal. Who would you like to provide wireless access to?

UR_UserReactivate=I would like to activate my secure wireless connection to the corporate network.

UR_UserCreatePass=I would like to generate a "guest pass" and activate a guest's wireless connection to the Internet.

UR_AmGuest=I'm a guest

UR_AskAccess=and would like to access the Internet.

UR_GuestRequired=A guess pass is required.

UR_AmEmployee=I'm an employee

UR_AskConf=and want to activate my wireless network connection.

UR_PwdRequired=Your user name / password is required.

UR_AskRequest=and would like to request a guest pass.



UR_WelLogin=Welcome to Ruckus Wireless ZoneDirector Manager.

UR_WelLoginDesc=To manage your wireless network, please log in with your administrative user name and password.

UR_ForWireless=For wireless access

UR_ExceedMaxClients=Wireless Access Denied

UR_ExceedMaxClientsDesc=Access Point maximum capacity has been reached. No more clients are allowed to access. Please contact the network administrator or try again later.



UR_ManageIPNotAllows=Web Management Access Denied

UR_ManageIPNotAllowDesc=This IP isn't allowed to manage ZoneDirector.

RuckusWireless=Ruckus Wireless

ZoneDirector=ZoneDirector
2010-07-14 09:39:30,598 INFO     Login to ZD [192.168.0.2] successfully!
2010-07-14 09:39:31,036 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:31,471 DEBUG    Parsing messages...
2010-07-14 09:39:33,109 DEBUG    Getting bundled messages at /bin/messages.en_US
2010-07-14 09:39:35,311 DEBUG    # This is a message file. First line should be either a comment or blank

# use '#' to indicate comments

# a line starting with ' ' will not be processed, either.

locale=en_US

UI_Direction=LTR

welcome=Welcome!

test1=You should see (1 2 3):({1} {2} {3})

test2=You should see (2 3 1):({2} {3} {1})

dashboard=Dashboard

monitor=Monitor

configure=Configure

admin=Administer

As_Is=Keep AP's Setting

DHCP=DHCP

Manual=Manual

DNS1=Primary DNS Server

DNS2=Secondary DNS Server

Name_ESSID=Name (ESSID)

Order=Order

Type=Type

Protocol=Protocol

DstAddr=Destination Address

DstPort=Destination Port

Company=Company

Company_Name=Company Name

CompanyAddr=Company Address

CompanyName={cn}

CompanyShort={sh}

CompanyDomain={dm}

DefaultWlanName={wn}

Email=Email

Phone=Phone

SupportURL=Support URL

Support=Support

Shared=Shared



LoginInvalid=The login information that you entered is incorrect. Please try again.

Logout=Log Out

Help=Help

Preference=Preferences

Backup=Back up

Restore=Restore

Upgrade=Upgrade

Restart=Restart

Import=Import

License=License

Certificate=Certificate

Operations=Operations

Diagnostic=Diagnostics

Registration=Registration

Language_Desc=Select the display language that you want to use on the Web interface.

ZeroITProv=Zero-IT Activation<sup><small>TM</small></sup>

GuestPolicy=Wireless Client Isolation

Refresh=Refresh

NextPage=Next

PerviousPage=Pervious

Edit=Edit

Clone=Clone

High=High

Medium=Medium

Low=Low

SettingApplied=Your changes have been saved.

Processing=Processing...

NA=N.A.

Unknown=Unknown

System=System

SystemInfo=System Info

RFInfo=RF Info

Identity=Identity

Created=Created

ExpiredTime=Expires

ReauthTime=Session

Delta=Delta

LoadBalancing=Load Balancing



# General

Bytes=bytes

PoweredBy=Powered by {cn}

More=Show More

Normal=Warning and Critical Events

Less=Critical Events Only

Description=Description

Location=Location

GPS=GPS Coordinates

DeviceName=Device Name

Latitude=Latitude

Longitude=Longitude

Authentication=Authentication

Encryption=Encryption

Actions=Actions

Editing=Editing

General=General Options

None=None

Passphrase=Passphrase

Advanced=Advanced Options

NetworkMgmt=Network Management

Application=Application

OK=OK

Save=Save

CreateNew=Create New

Delete=Delete

DeleteAll=Delete All

NewName=New Name

Approved=Approved

Allow=Allow

Deny=Deny

Apply=Apply

Generate=Generate

Test=Test

Channel=Channel

Full=Full

Auto=Auto

Min=Min

Approval=Approval

Yes=Yes

No=No

Thumbnail=Thumbnail

Name=Name

Username=User Name

Password=Password

Password1=Password

Password2=Confirm Password

CurPassword=Current Password

NewPassword1=New Password

NewPassword2=Confirm New Password

ShowPassword=Show Password

Policies=Policies

Authorization=Authorization

Role=Role

Size=Size

Port=Port

Retry=Retry

Times=times

Seconds=seconds

Hours=hours

Timeout=Timeout

EmailAddress=Email Address

Enable=Enable

Disable=Disable

Enabled=Enabled

Disabled=Disabled

Services=Services

Login=Log In

Print=Print

Action=Action

Radio=Radio

Signal=Signal

Search=Search terms

SearchAnd=Include all terms

SearchOr=Include any of these terms

ClickHere=click here

Clients=Clients

Connected=Connected

PrimarySrv=Primary Server

SecondarySrv=Secondary Server

UseGlobalConfiguration=Use Global Configuration



Monday=Monday

Tuesday=Tuesday

Wednesday=Wednesday

Thursday=Thursday

Friday=Friday

Saturday=Saturday

Sunday=Sunday



Hops=Hops

Fanout=Downlinks



User=User

UserOrIp=User/IP

DateTime=Date/Time

Severity=Severity

Activities=Activities

Location=Location

Loading=Loading

Users=Users

Alarms=Alarms

Clear=Clear

ClearAll=Clear All

ShowMore=Show More

Events=Events/Activities

Status=Status

TunnelMode=Tunnel Mode

ChannelA=11a Channel

ChannelBG=Channel

SixHours=Six hours

TwelveHours=Twelve hours

FiveMins=Five mins

OneHour=One hour

OneDay=One day

TwoDays=Two days

OneWeek=One week

TwoWeeks=Two weeks

OneMonth=One month

TwoMonths=Two months

ThreeMonths=Three months

HalfYear=Half a year

OneYear=One year

TwoYears=Two years

Unlimited=Unlimited



# Wizard

Back=&lt; Back

Cancel=Cancel

Finish=Finish

Language=Language

Next=Next &gt;

Adminname=Admin Name

Setup_Wizard=Setup Wizard

WebAuth=Web Authentication

EnableWebAuth=Enable Web Authentication

SystemName=System Name



WIZ_TITLE_general=General

WIZ_TITLE_language=Language

WIZ_TITLE_mgmtip=Management IP

WIZ_TITLE_wlan=Wireless LANs

WIZ_TITLE_admin=Administrator

WIZ_TITLE_user=User

WIZ_TITLE_confirm=Confirmation

WIZ_TITLE_finished=Finish

WIZ_DESC_general=Enter a system name for {zd}. The name should be between 1 and 32 characters--numbers and letters--but not including spaces.

WIZ_DESC_language=Welcome to the {cn} {zd} Setup Wizard. Use this wizard to prepare {zd} to run your wireless network. To start, select the display language that you want to use on the Web interface.

WIZ_DESC_mgmtip=Select the network addressing mode--"Manual" or "DHCP". If you select "DHCP," no further configuration is needed. If you select "Manual," enter the relevant IP addressing information. (Fields marked with an asterisk (*) are required.)

WIZ_DESC_wlan=If you make no changes to the default settings, a default WLAN "Wireless 1" with Open authentication is created. You can change it to a secure WLAN by choosing WPA_PSK authentication and providing a passphrase. Optionally, a "Guest" WLAN can be created for temporary guest access. (More WLANs can be added later, for restricted use.)

WIZ_DESC_admin=Enter an "Admin" user name and password that permits administrative access to the Web interface. (Use this information to log into the Web interface after this setup is complete, to further configure your new wireless network.)

WIZ_DESC_user=Use these features (optional) to create a single network user account at this time. (Or, if you prefer, use the Web interface to create user accounts at a later time.)

WIZ_DESC_confirm=Please review the following settings. If changes need to be made, click Back to edit your settings. If the settings are ready for use, click Finish.

WIZ_DESC_mesh={zd} provides mesh capability. Each mesh-enabled {zd} requires a unique name (SSID) for the mesh WLAN for the backbone traffic.

WIZ_TITLE_mesh=Mesh

WIZ_DoMesh=Enable Mesh

WIZ_AuthOpen=Open

WIZ_AuthPSK=WPA_PSK

WIZ_AuthEAP=802.1X EAP

WIZ_DoDPSK=Enable WPA-DynamicPSK<SUP><SMALL>TM</SMALL></SUP>

WIZ_DPSK=Dynamic PSK

WIZ_DESC_finished=Your {cn} {zd} is now active. [ALERT] If you changed the IP address on your administrative PC for this setup procedure, reset the IP address before reconnecting your PC to the network.

WIZ_CorpDesc=Wireless 1-- Create your first Wireless LAN

WIZ_CreateProv=Provisioning

WIZ_ProvDesc=Use Guest WLAN for Zero-IT Activation<SUP><SMALL>TM</SMALL></SUP>

WIZ_GuestDesc=Guest WLAN-- Temporary access for visitors.

WIZ_Reconnect=Click this link to reconnect to your {zd} at

WIZ_Passphrase=WPA Passphrase

WIZ_WEPKey=WEP Key #0

WIZ_DoUsers=Create a user account

WIZ_Time=System Time

WIZ_REQUEST_DHCP=Request IP

WIZ_REQUESTING_DHCP=Requesting IP Address...

WIZ_DHCP_FAILED=Unable to obtain an IP address from DHCP. Verify that you are connected to your network, and then try again. Or, if you have access to the required network addressing information, you may choose Manual IP assignment and manually configure the connection.

WIZ_NoMesh=Mesh capability is disabled

WIZ_NoWLANs=No wireless LAN will be created

WIZ_WLAN1ZeroIT= (Zero-IT Activation enabled)

WIZ_SETWLAN1=Wireless 1, <strong>{1}</strong>, will be created <br/>

WIZ_SETWLAN2=Guest WLAN, <strong>{1}</strong>, will be created

WIZ_SETAccount=Account <strong>{1}</strong> will be created

WIZ_SETTIME=System time will be automatically set. <br/> (Your current PC time is {1})

WIZ_CheckUpdate=* After completing the setup wizard, please check the <a href="http://support.{dm}/" target="blank">{cn} Support</a> Web site for the latest software updates.



# Portlets

NumAP=# of APs

P_Devices_Title=Devices Overview

NumClients=# of Client Devices

MaxNumClients=Max Concurrent Users

NumRogues=# of Rogue Devices

P_SysEvents_Title=Most Recent System Activities

P_SysInfo_Title=System Overview

SysName=System Name

SysVersion=Version

Model=Model

MaxAP=Licensed APs

SysSerial=S/N

SysUpTime=Uptime

P_TopAp_Title=Most Frequently Used Access Points

P_TopClient_Title=Most Active Client Devices

P_UserEvents_Title=Most Recent User Activities

P_Usage_Title=Usage Summary

Usage=Usage

BytesTransmited=Bytes Transmitted

AverageSignal=Average Signal

P_WlanEssid=Names/ESSIDs

P_MapView=Map View

P_SnmpSettings=SNMP Settings

P_Rogue=Currently Active Rogue Devices

P_LastDetection=Last Detected

P_LastConnect=Last Connect

P_LastDisconnect=Last Disconnect

P_APSummary=Currently Managed APs

P_WlanSummary=Currently Active WLANs

P_WlanGroupSummary=Currently Active WLAN Groups

P_RogueType=Type

P_RogueIsOpen=Encryption

P_AddWidgets=Add Widgets

P_HideWidgets=Finish

P_Cluster_Title=Smart Redundancy

P_ClusterConfTime=Config Modified Time

P_ClusterConfLast=Config Last Sync

P_ClusterDisabled=Smart Redundancy is disabled.

P_ClusterWaitingConf=Intended configuration is not decided yet. Smart Redundancy is not fully operational.

CpuUtil=CPU Util

MemUtil=Memory Util



# Errors

E_Error=Error

E_InvalidAccess=You may have accessed this page incorrectly.

E_XRequired={1} is a required field.

E_NameRequired=Name is a required field.

E_NameDuplicated=The name {name} already exists. Please enter a different name.

E_KeyDuplicated=The key {1} already exists. Please enter a different key.

E_WlanReferedByRole=WLAN {from} is referred to by Role {name} and cannot be deleted.

E_WlanReferedByWlanGroup=WLAN {from} is referred to by Wlan Group {name} and cannot be deleted.

E_RoleReferedByUser=Role {from} is referred to by User {name} and cannot be deleted.

E_MapIsDefault=The default map cannot be deleted. You can change the name or upload your own map image.

E_MapReferedByAp=Map {from} is referred to by access point {name} and cannot be deleted.

E_AclReferedByWlan=ACL {from} is referred to by WLAN {name} and cannot be deleted.

E_WlanGroupReferedByAp=WLAN group {from} is referred to by AP {name} and cannot be deleted.

E_HotspotReferedByWlan=Hotspot service {from} is referred to by WLAN {name} and cannot be deleted.

E_JSDisabled=Your browser does not support JavaScript, or you do not have JavaScript enabled. This site requires JavaScript for operation.



E_RoleIsDefault=This default role cannot be deleted.

E_AclIsDefault=This default ACL cannot be deleted.

E_AuthsvrReferedByGuestAccess=Auth Server {from} is used for guest pass generation and cannot be deleted.

E_AuthsvrReferedByZeroIT=Auth Server {from} is used for Zero-IT Activation and cannot be deleted.

E_AuthsvrReferedByWlan=Auth Server {from} is used by WLAN {name} and cannot be deleted.

E_AuthsvrReferedByAdmin=Auth Server {from} is used by Admin Auth and cannot be deleted.

E_AuthsvrNoneForAdminAuth=Please select a Authentication Server first.

E_AuthsvrReferedByHotspotService=Auth Server {from} is used by Hotspot Service {name} and cannot be deleted.



I_EditingNotSaved=The Editing dialog is still opening and has not yet been saved.  Are you sure you want to ignore it?

E_FailMACAuth={1} must authenticate with a RADIUS server

E_FailEmpty={1} cannot be empty

E_FailLength={1} has to be no less than {2} and no greater than {3} characters.

E_FailAlphaNumeric={1} can only contain alphanumeric characters (A-Z, a-z, and 0-9).

E_FailIP={1}, {2}, is not a valid IP address.

E_FailNetmask={1}, {2}, is not a valid netmask (example: 255.255.255.0).

E_FailSubnet={1}, {2}, is not a valid subnet (example: 192.168.0.1/24).

E_FailMAC={1}, {2} is not a valid MAC address (example: 00:01:02:03:04:05).

E_FailSame={1} and {2} must be identical.

E_FailDiff={1} and {2} must be different.

E_FailEmail={1}, {2} is not a valid email address (example: john@theDomain.com).

E_FailInteger={1} must be an integer.

E_FailPosInteger={1} must be a positive integer.

E_FailEssid={1} can only contain between 2 and 32 characters, including characters from ! (char 33) to ~ (char 126).

E_FailPassphrase={1} can only contain between 8 and 63 characters, including characters from ! (char 33) to ~ (char 126), or 64 HEX characters.

E_FailWEP64={1} can only contain 10 HEX characters.

E_FailWEP128={1} can only contain 26 HEX characters.

E_FailVLAN={1} must be a number between 2 and 4094.

E_FailProtocol={1} must be a number between 0 and 254.

E_FailPort={1} is not a valid port number or port range (example: 80 or 80-443).

E_FailUsername=The user name can only contain up to 32 alphanumeric characters, underscores (_), periods (.), and cannot start with a number.

E_FailPassword=The password can only contain between 4 and 32 characters, including characters from ! (char 33) to ~ (char 126).

E_FailOldPassword= Please provide current Admin password.

E_FailInputCurrentPassword=The Current Password is not correct.

E_FailGuestDuration={1} must be a positive integer and valid time must be less than 10 years.

E_FailGuestKey={1} can only contain between 2 and 16 characters, including characters from ! (char 33) to ~ (char 126).

E_FailGuestRemarksTooLong=Text too long. Must be {1} characters or less.

E_FailBatchGuestNum=The input value must be a number between 1 and {1}.

E_FailGuestExceedMax=The total number of guest and user accounts has reached the maximum allowable size {1}.  Please contact your network administrator to remove unused accounts before creating new ones.

E_FailDpskExceedMax=The total number of DPSK accounts has reached the maximum allowable size.  Please contact your network administrator to remove unused accounts before creating new ones.

E_FailBatchPassUpload=There is an error at line {1}. The length of {2} is {3}. It exceeds the maximum allowed length({4}). Please modify the uploaded file.

E_FailSysname=The system name can only contain up to 32 alphanumeric characters, underscores (_), and hyphens (-).

E_FailDeviceName=The device name can only contain up to 64 alphanumeric characters, space, underscores (_), and hyphens (-).

E_FailGPS=The value is invalid.

E_InvalidBackup=The backup file that you selected is not a valid configuration file or it may be corrupted. Please select another backup file.

E_BackupFromFuture=The backup file that you are trying to upload is incompatible with the current software version. Please select another backup file.

I_RestoreOptions=Choose a restore type:

I_RestoreRestore=Restore everything.

I_RestoreFailover=Restore everything, except system name and IP address settings (for failover deployment at the same site).

I_RestorePolicy=Restore only WLAN settings, access control list, roles, and users (use this as a template for different sites).

I_ShowPassword=Password displayed on screen may be cached by Web browser.  Are you sure you want to continue?

E_InvalidUpgrade=This does not seem to be a valid upgrade image. Please try another file.

E_FailRequireUpgradeVersions=This {1} upgrade package is applicable to ({2}).

E_FailRequireDowngradeVersions=This {1} downgrade package is applicable to ({2}).

E_FailBlockDowngrade=Downgrading from {1} to {2} is not supported.

E_FailUpgradeCheck={1}

E_MemoryNotEnough={zd} memory is insufficient.  Please delete unnecessary events/alarms or reboot {zd} before uploading file.

E_ImageTooBig=The image you uploaded exceeds the maximum allowed file size. Please try another file.

E_ImageFormat=The image must be in .PNG, .GIF, or .JPG format.

E_ImageFull=Total map size exceeds {1}MB. Please try another file or remove unused maps.

E_MapEmpty=No map has been imported. Please upload a map first.

E_MapInvalid=The imported map seems to be invalid. Please upload another map.

E_FailRange={1} must be a number between {2} and {3}

E_InvalidLicense=This does not seem to be a valid license. Please try another file.

E_LicenseDuplicated=This license has already been imported. Please try another file.

E_FailUploadSizeZero=The size of the uploaded file is zero. Please try another file.

E_FailUpload=Upload failed. Verify that the file does not exceed the maximum allowed size, and then try again.

E_SessionTimeout={zd} has logged you out of the Web interface because it did not detect any activity for some time. Please log in again.

E_AclStationTooMany=The access control list has reached its maximum number of stations ({1}). To add new stations, you need to first delete inactive stations from the list.

E_AclStationDuplicated=The station {1} already exists in the access control list. Please enter another one.

ConfirmStationNotSaved=The station {1} you entered has not yet been added to the access control list. Are you sure you want to ignore it?



I_SuccessAdtestWithGroups=<strong>Success!</strong> Groups associated with this user are <strong>"{1}"</strong>. The user will be assigned a role of <strong>"{2}"</strong>.

I_SuccessAdtestWithoutGroups=<strong>Success!</strong> The user will be assigned a role of <strong>"{1}"</strong>.

E_FailAdtestConnError=<strong>Failed!</strong> Unable to connect.

E_FailAdtestTimeout=<strong>Failed!</strong> Connection timeout.

E_FailAdtestLoginAdmin=<strong>Failed!</strong> Invalid admin account.

E_FailAdtestSearchFilter=<strong>Failed!</strong> Invalid LDAP search filter.

E_FailAdtestLogin=<strong>Failed!</strong> Invalid username or password.



E_FailIPRange={1}-{2} is not a valid IP range format (example 192.168.1.1-192.168.1.100).



I_SuccessTestNotif=<strong>Success!</strong>

E_FailTestNotif=<strong>Failed!</strong>



I_DownloadInProgress=Only one system info can be downloaded at a time. Please wait until the current download is finished.

I_DownloadInProgressRFInfo=Only one RF info can be downloaded at a time. Please wait until the current download is finished.

E_FailSysInfo=Failed! Unable to download system info for {1}.

E_FailRFInfo=Failed! Unable to download RF info for {1}.

E_ClusterVersionMismitched=Version mismatch

E_ClusterModelMismitched=Model mismatch

E_ClusterIpMismitched=IP Address mismatch

E_ClusterMaxApMismitched=Licensed APs mismatch

E_ClusterPasswordMismitched=Shared Secret mismatch

E_ClusterDisconnected=Disconnected

I_ClusterLastConf=(last updated on <strong>{1}</strong>)

I_IpPairMismatch=Configuration of Limited ZD Discovery is not consistent with Smart Redundancy. Inconsistent configuration will cause Access Points to be unable to rediscover the active {zd} when failover occurs. Are you sure you want to continue?

I_ClusterUpg=(Version:{1})

I_ClusterWithDhcps=DHCP Server is enabled now but it will be disabled if Smart Redundancy is enabled. Are you sure you want to continue?



E_FailSameSubnet=The two IP addresses {1} and {2} are on different subnets with netmask {3}.

E_FailSameSubnetWithWarning=The two IP addresses {1} and {2} are on different subnets with netmask {3}. Are you sure you want to change subnet?

E_FailSameSubnetWithConfirm=The two IP addresses {1} and {2} are on different subnets with netmask {3}. Do you want the system to correct the entry for you? (Hint: Modify the netmask to increase subnet range.)

E_FailSetDhcps=DHCP server configuration failed.  This could be caused by disk full or internal error.

E_FailAPCliTimeout=Failed! Unable to execute cmd at AP[{1}].

E_FailAPCliFailed=Failed! Unable to execute cmd at AP[{1}].

E_FailAPCliTerminate=Failed! The previous cmd is still running but it will be terminated. Please try again.

E_FailAPCliNoCmd=Command line can not be empty.  Please enter again.

E_FailBlockClient=Number of blocked clients exceeds limit (128). If you want to block additional clients, please first unblock existing blocked clients.

E_WlanHasVlanOverride=VLAN Override tagging is enabled for current WLAN in WLAN Group [{1}].  Please disable VLAN Override tagging before enabling Tunnel Mode.

E_NoWepKeyCanUse=There are no empty WEP key slots available.

E_ExceedMaxWlans=The maximum number of WLANs is {1}.  Please deselect other WLANs before adding a new WLAN.

E_ExceedMaxWlansMesh=The maximum number of WLANs is {2} when Mesh is enabled.  Please remove unused WLANs from WLAN group [{1}] before enabling Mesh.

E_WlanGroupIsDefault=The default WLAN group cannot be deleted.

E_FailDestination={1}, {2}, is not a valid IP address or subnet (example: 192.168.0.1/24).

E_GuestPrintIsDefault=The default Guest Pass Printout cannot be deleted.

E_GuestPrintEmpty=No Guest Pass Printout has been imported. Please upload one first.

E_GuestPrintFailed=There is an error at line {1} / col {2}.  Script language is not allowed.

E_GuestPrintNotHtml=The uploaded file is not an html file.  Please try another file.

E_GuestPrintTooBig=The html file you uploaded exceeds the maximum allowed file size. Please try another file.

E_CertFileLost=The {zd} private key or certificate file does not exist.

E_CertNotMatchPKey=The uploaded certificate file does not match {zd}'s private key.

E_CertNotMatchPKey2=Please try another certificate file or

E_CertNotMatchPKey3= to import private key.

E_CertNotMatchIC=Intermediate certificate file does not match the installed certificate or previous intermediate certificate. Please try another intermediate certificate file.

E_CertSANFormatErr=The input format error. Please make the "{1}" blank empty or follow this format to type "IP:your IP address" or "DNS:your domain name".



E_SelectedDFSedChannel=Channel is not available at this time, current non-occupancy channel(s) is/are {1} (in timeout order), please re-try later.

E_EmbeddedJsCode=Embedding html or javascript code, e.g. < />, is not allowed.

E_MultipleItemsNotAllowed=Multiple items are not allowed in {1}.



I_LoadCertOptions=Choose an import type:

I_LoadCertReboot=Install this certificate and then reboot.

I_LoadCertIntermediate=Install this certificate and additional intermediate certificates.

I_LoadICOptions=Choose an intermediate certificate to import:

I_LoadICReboot=Install this intermediate certificate and then reboot.

I_LoadIC=Install this intermediate certificate and additional intermediate certificate(s).



E_SpeedFlexNumAPs=Checking more than two APs is not allowed.

E_SpeedFlexNumInvalid=Please select two APs for SpeedFlex test.



# Admin

AD_Login=Administrator Name/Password

AD_LoginDesc=Change the administrator name (if needed) and password. {cn} recommends that you change your admin password every 30 days.

AD_AuthByLocal=Authenticate using the admin name and password

AD_AuthByExternal=Authenticate with Auth Server

AD_FallbackToLocal=Fallback to admin name/password if failed

AD_PrivilegeLimited=Your privilege is limited to monitoring and viewing operation status.

AD_Backup=Back Up Configuration

AD_BackupDesc=Click Back Up to save an archive file of your current {zd} configuration. This archive will simplify system recovery if needed.

AD_Restore=Restore Configuration

AD_RestoreDesc=If you need to restore the system configuration, click Browse, and then select the backup file that contains the settings that you want to restore.

AD_RestoreDft=Restore to Factory Settings

AD_RestoreDftDesc=If needed, you can restore {zd} to its factory settings, which will delete all settings that you have configured. You will need to manually set up {zd} again. For more information, see the online help.

AD_RestoreDftCfm=Are you sure you want to restore {zd} (and your network) to the default state?

AD_RestoreCfm=Are you sure you want to restore {zd} (and your network) to the configuration stored in this archive?

AD_RestartShutdown=Restart / Shutdown

AD_Restart=Restart

AD_Shutdown=Shutdown

AD_RestartDesc=Click this button to restart {zd}. Network connections will be broken temporarily, and then renewed when startup is complete.

AD_ShutdownDesc=Click this button to shut down {zd}. (To restart {zd}, disconnect it from the power source, and then reconnect it.)

AD_RestartCfm=Are you sure you want to restart {zd}?

AD_ShutdownCfm=Are you sure you want to shut down {zd}?

AD_RestartSrvCfm=Are you sure you want to restart all services without reboot?



AD_Version=Current Software

AD_UpgradeCurrentVer=Your current software version is

AD_UpgradeSeeApimgs=To see the access points that can be managed,

AD_BundledAPModel=AP Model

AD_BundledAPVer=Bundled Firmware

AD_Uptodate=Your software is up-to-date. There is no update at this time.

AD_HasUpdate=A new version is available. To download the latest software,

AD_Noconnection=Unable to connect to the {cn} Update Server. Verify that you are connected to the Internet, and then try again.

AD_CheckUpdate=Check for Updates

AD_Upgrade=Software Upgrade

AD_UpgradeDesc=<strong>Important: </strong>Before the upgrade process starts, {zd} will prompt you to save a backup of the {zd} settings. Save the backup file to your local disk. To start the software upgrade of {zd} and all associated APs, click Browse, and then select the upgrade package. When "Browse" is replaced by "Upgrade", click that button to start the upgrade process. The network will be restored automatically when the upgrade process is complete.

AD_UpgradeCfm=Are you sure you want to upgrade the entire wireless network?

AD_DowngradeAndReset=Restore configuration to factory default after the downgrade.

AD_UpgradeAndReset=Restore configuration to factory default after the upgrade.

AD_DowngradeAndBackup=Restore configuration to {1} (created on <strong>{2}</strong>).

AD_UpgSaveBackupCfm={cn} strongly recommends that you back up the {zd} settings before performing a software upgrade.  To save a backup of the {zd} settings, click OK, and then save the backup file to your local disk.

AD_License=License Upgrade

AD_UpgradeLicense=Upgrade license

AD_LicenseEmpty=No license has been imported.

AD_LicenseCurFeature=Your current license is [{1}], which supports {2} APs and {3} clients.

AD_ImportLicDesc=Import a new license

AD_UpgradeLicDesc=Click the Upgrade button to start the process.

AD_Feature=Feature

AD_PO_Number=Sales Order Number

AD_UpgradeLicenseCfm=Are you sure you want to upgrade this license?

AD_ErrorLicenseDepend=You need the prerequisite license [{1}] installed before you can activate this license.

AD_LicenseSerialMismatch=This license is intended for a different {zd} with serial number [{1}].

AD_LicenseOlderVersion=This license is intended for an older version of {zd} and not applicable to this {zd}.

AD_LicenseValidFor=This temporary license is available for {1} days.

AD_LicenseExpired=This temporary license has expired.

AD_LicenseValid=Valid

AD_LicenseActive=Active

AD_LicenseInactive=Inactive



AD_Scan=Scan

AD_ActiveScan=Manual Scan

AD_ActiveScanDesc=Click this button to initiate a radio frequency scan. [ALERT] This will immediately sample all active frequencies and may temporarily interfere with wireless network communication.

AD_ActiveScanCfm=A radio frequency scan has been initiated. Network communication will be disrupted temporarily.

AD_DebugInfo=Debug Information

AD_DebugInfoDesc=This gives you a quick glance of the system information that is useful to our technical support.

AD_SaveDebug=Save Debug Info

AD_SaveDebugDesc=If you request assistance from {cn} technical support, you may be asked to supply detailed debug information from {zd}. Click the "Save Debug Info" button to generate the debug log file, and then save it to your computer.

AD_DebugLogs=Debug Logs

AD_DebugLevels=Debug Levels

AD_DebugLogFltMACDesc=Debug log per AP's or client's mac address

AD_DebugLogFltMACExample=(e.g. aa:bb:cc:dd:ee:ff)



AD_Performed=Action Performed

AD_RestoreDftIng=Restoring {zd} to factory settings...

AD_RestoreDftIngDesc={zd} is being restored to factory settings. Please wait at least one minute before using UPnP to discover it. </p><p>If {zd} does not detect a DHCP server on the network, it will assign itself the IP address 192.168.0.2/255.255.255.0.

AD_RestoreIng=Restoring...

AD_RestoreIngDesc={zd} is being restored to a previously archived configuration. Once restore is complete, you will be automatically reconnected to

AD_RestorePeerZdIngDesc=[Smart Redundancy] Peer {zd}{peer-ip} is being restored to a previously archived configuration. Once restore is complete, you will be automatically reconnected to active {zd}

AD_RestoreLocalZdIng=[Smart Redundancy] Peer {zd}{peer-ip} is disconnected now. System is being restored to a previously archived configuration. Once restore is complete, you will be automatically reconnected to

AD_UpgradeIng=Upgrading...

AD_UpgradeIngDesc={zd} is being upgraded. DO NOT disconnect {zd} from the power source or the wired network. Once upgrade is complete, you will be automatically reconnected to

AD_RestartIng=Restarting...

AD_RestartIngDesc={zd} is restarting. Once restart is complete, you will be automatically reconnected to

AD_ShutdownIng=Shutting down...

AD_ShutdownIngDesc={zd} is shutting down. To power on {zd} again, press the power button. When the Status LED is lit steadily, you can then reconnect to

AD_UploadCertIng=Loading Certificate...

AD_UploadCertIngDesc={zd} is loading the certificate file. Once {zd} is in service, you will be automatically reconnected to

AD_RestartSrvIng=Restarting Services...

AD_RestartSrvIngDesc={zd} is restarting all services. Once {zd} is in service, you will be automatically reconnected to

AD_ConnectIngZd=Connecting to {zd}...

AD_ConnectingZdDesc={zd} restarted. You are going to reconnect to

AD_UpgradePeerZdIngDesc=[Smart Redundancy] Peer {zd}{peer-ip} is being upgraded. DO NOT disconnect {zd} from the power source or the wired network. Once the upgrade is complete, you will be automatically reconnected to the active {zd}

AD_UpgradeLocalZdIng=[Smart Redundancy] Peer {zd}{peer-ip} is disconnected. System is being upgraded and will upgrade peer {zd} once it is reconnected. DO NOT disconnect {zd} from the power source or the wired network. Once upgrade is complete, you will be automatically reconnected to

AD_PeerZdDisappeared=Peer {zd} is unavailable...

AD_PeerZdDisappearedDescRestore=[Smart Redundancy] Peer {zd} was being restored but is currently unavailable. System restore will now begin. Once restore is complete, you will be automatically reconnected to the active {zd}

AD_PeerZdDisappearedDescUpgrade=[Smart Redundancy] Peer {zd} was being upgraded but is currently unavailable. System upgrade will now begin. Once upgrade is complete, you will be automatically reconnected to the active {zd}



AD_CountryCode=Country Code

AD_CountryCodeDesc=Different countries have different regulations on the usage of radio channels. To ensure that {zd} is using an authorized radio channel, select the correct country code for your location.

AD_OptimizationDesc=On the 5.0 GHz band, certain channels won't be utilized if "Optimize for Interoperability" is selected, otherwise, all available channels will be utilized.

AD_PingTool=Network Connectivity

AD_PingToolDesc=Troubleshoot your network connectivity.



AD_Registration=Product Registration

AD_RegRequestFields=Required fields

AD_RegDesc=To start the registration process, fill out the required information, and then click Apply to generate the registration request file (.csv). Save the file, and then send it as an email attachment to



AD_APActivities=AP Activities

AD_APInfo=AP Logs

AD_APInfoDesc=To show current APs' logs,



# Conf

CF_ChannelOpt=Channel Optimization

CF_Opt4Intprb=Optimize for Interoperability

CF_Opt4Perf=Optimize for Performance

CF_ConfirmDeleteOne=Are you sure you want to delete the selected entry?

CF_ConfirmDeleteMany=Are you sure you want to delete the selected entries?

CF_ConfirmChangeCountry=Changing the country code will reset ALL channels of access points to Auto. Click OK to continue.

CF_NetworkSetting=Network Setting

CF_MgmtIp=Device IP Settings

CF_MgmtIpDesc=If {zd} was assigned static network addressing, click "Manual" and make the correct entries. If you click DHCP, no "Manual" entries are needed.

CF_ZdIp=Limited ZD Discovery

CF_MgmtAddIf=Management Interface

CF_MgmtAddIfDesc=Enable Management Interface to have an additional interface for management.

CF_AddIfShowConfig=If {zd} needs another interface for management traffic,

CF_AddIfEnabled=Enable Management Interface

CF_ZdIpEnabled=Only connect to the following {zd}

CF_ZdPrimIp=Primary {zd} IP

CF_ZdSecIp=Secondary {zd} IP

CF_MgmtVlan=Management VLAN

CF_Cluster=Smart Redundancy

CF_ClusterDesc=Enable Smart Redundancy to ensure continued operation of your network in the event of a {zd} failure or power loss. If the active {zd} loses connection, the standby {zd} will automatically take over.

CF_ClusterEnabled=Enable Smart Redundancy

CF_ClusterLocalState=Local State

CF_ClusterPeerState=Peer State

CF_ClusterLocalIp=Local Device IP Address

CF_ClusterPeerIp=Peer Device IP Address

CF_ClusterMgmtIp=Management IP Address

CF_ClusterFailover=Force Failover

CF_ClusterGotoConf=To configure Smart Redundancy,

CF_ClusterConfirmFailover=Are you sure you want to force failover?

CF_ClusterLimited=This {zd} is in standby state with limited configuration change and viewing features available.

CF_ClusterConfirmConf=Smart Redundancy is not fully operational yet. Select which correct configuration to synchronize.

CF_ClusterConfirmConfShort=Waiting for config decision...

CF_ClusterWaiting=Connecting to peer...

CF_ClusterMgmtIpDesc=Configured in [Device IP Settings]->[Management Interface]

CF_ClusterSyncToPeer=Sync to peer

CF_ClusterSyncFromPeer=Sync from peer

CF_ClusterConfirmUpg=Versions of {zd}s are mismatched. You can select one {zd} to be upgraded.

CF_ClusterUpgLocal=Upgrade local {zd}

CF_ClusterUpgPeer=Upgrade peer {zd}

CF_ClusterUpgLocalCfm=Are you sure you want to upgrade local {zd}?

CF_ClusterUpgPeerCfm=Are you sure you want to upgrade peer {zd}?

CF_ZdMgmtVlanEnabled={zd} management traffic is restricted to VLAN

CF_ApMeshModeAuto=Auto (Mesh role is automatically assigned)

CF_ApMeshModeRap=Root AP (Only runs as a root AP)

CF_ApMeshModeMap=Mesh AP (Only runs as a mesh AP)

CF_ApMgmtVlanDisabled=Disable

CF_ApMgmtVlanEnabled=Enable with VLAN ID

CF_ApMgmtVlanKeep=Keep AP's setting

CF_MgmtIPAclTitle=Management Access Control

CF_MgmtIPAclDesc=This table lists the specific IP addresses which are allowed access to the {zd}. Click Create New to add another IP address, or click Edit to make changes to an existing entry.

CF_MgmtIPAcl=IP address

CF_single=Single

CF_range=Range

CF_subnet=Subnet

CF_Dhcps=DHCP Server

CF_DhcpsOption43Enabled=DHCP Option 43

CF_DhcpsOption43Note=Layer 3 discovery protocol for AP to find {zd}

CF_DhcpsDesc=If a DHCP server does not exist on your network, you can enable this function to provide DHCP service to clients.

CF_DhcpsEnabled=Enable DHCP server

CF_DhcpsIpStart=Starting IP

CF_DhcpsRange=Number of IPs

CF_DhcpsLease=Lease Time

CF_DhcpsShowLease=To view all IP addresses that have been assigned by the DHCP server,

CF_DhcpsHidden=To enable DHCP server, Manual mode must be selected in Device IP Settings and Smart Redundancy must be disabled.

CF_SystemTime=System Time

CF_SystemTimeDesc=Click Refresh to update the time displayed on this page. Click Sync Time with Your PC to manually synchronize the internal {zd} clock with your administrative PC clock.

CF_SyncTime=Sync Time with Your PC

CF_SystemTimeIs=Your current system time is

CF_NtpSync=Use NTP to synchronize the {zd} clock automatically

CF_NtpServer=NTP Server

CF_LogSettings=Log Settings

CF_RemoteSyslog=Remote Syslog

CF_EnableRemoteSyslogAt=Enable reporting to remote syslog server at

CF_RemoteSyslogdIP=Remote Syslog IP

CF_EventLogLevel=Event Log Level

CF_FlexMaster=FlexMaster Management

CF_ACSurlDesc=Enter the FlexMaster server URL and set the time interval at which {zd} will send status updates to FlexMaster.

CF_BeManaged=Enable management by FlexMaster

CF_ACSurl=URL

CF_InformInterval=Interval

CF_InformFail=Previous contact attempt failed

CF_InformBusy=. FlexMaster may be busy or offline.

CF_InformDoing=. Attempting to contact FlexMaster again...

CF_InformNever=Never

CF_FMStatus=Last successful contact

CF_Minutes=minutes

CF_Wlans=WLANs

CF_WlansDesc=This table lists your current WLANs and provides basic details about them. Click Create New to add another WLAN, or click Edit to make changes to an existing WLAN.

CF_WlanGroups=WLAN Groups

CF_WlanGroupsDesc=This table lists your current WLAN groups and provides basic details about them. Click Create New to add another WLAN group, or click Edit to make changes to an existing WLAN group.

CF_WlanGroupHasVlan=Enable VLAN override

CF_WlanGroup=WLAN Group

CF_GroupedWlans=Member WLANs

CF_TunnelModeEnabled=Tunnel Mode is enabled

CF_OrigVlan=Original VLAN

CF_VlanOverride=VLAN override

CF_VlanNote=VLAN is a number between 2 and 4094

CF_VlanTag=Tag

CF_VlanUntag=Untag

CF_VlanNoChange=No Change

CF_EnableDynamicVLAN=Enable Dynamic VLAN

CF_NameEssid=Name/ESSID

CF_WlanUsage=Usage Options

CF_Authentication=Authentication Options

CF_Encryption=Encryption Options

CF_UsageType=Type

CF_AuthMethod=Method

CF_AuthMacServiceUnavailable=There is no available RADIUS Authentication Service.  Please configure AAA servers first.

CF_EncryptMethod=Method

CF_EncryptAlgo=Algorithm

CF_DynamicPSK=Dynamic PSK<SUP><SMALL>TM</SMALL></SUP>

CF_EnableDynamicPSK=Enable Dynamic PSK

CF_WepKey=WEP Key

CF_WepKeyGenerate=Generate

CF_ApplyGuestPcy=Full

CF_ApplyGuestPcyNote=(Wireless clients will be unable to communicate with each other or access any of the restricted subnets.)

CF_ApplyLocalIsolation=Local

CF_ApplyLocalIsolationNote=(Wireless clients associated with the same AP will be unable to communicate with one another locally.)

CF_WebAuth=Web Authentication

CF_WebAuthDesc=Enable captive portal/Web authentication

CF_WebAuthNote=(Users will be redirected to a Web portal for authentication before they can access the WLAN.)

CF_RateLimiting=Rate Limiting

CF_PresetNote=(Per Station Traffic Rate)

CF_UplinkPreset=Uplink

CF_DownlinkPreset=Downlink

CF_DISABLE=Disabled

CF_100kbps=100Kbps

CF_250kbps=250Kbps

CF_500kbps=500Kbps

CF_1mbps=1Mbps

CF_2mbps=2Mbps

CF_5mbps=5Mbps

CF_10mbps=10Mbps

CF_20mbps=20Mbps

CF_50mbps=50Mbps

CF_EnableZeroITProv=Enable Zero-IT Activation

CF_EnableZeroITProvNote=WLAN users are provided with wireless configuration installer after they log in.

CF_AttachVlanTag=Attach VLAN Tag

CF_HideSsid=Hide SSID

CF_HideSsidDesc=Hide SSID in Beacon Broadcasting (Closed System)

CF_VoiceOptim=Voice Optimization

CF_80211dSupport=Support for 802.11d

CF_VoiceOptimDesc=This WLAN is optimized for voice deployment

CF_TunnelMode=Tunnel Mode

CF_TunnelModeDesc=Tunnel WLAN traffic to {zd}

CF_TunnelModeNote=Recommended for VoIP clients and PDA devices.

CF_TimeBasedWLAN=Service Schedule

CF_Dpsk=Dynamic PSK

CF_DpskExpireDesc=To provide maximum security, each user is assigned a unique pre-shared key (PSK) when they activate their wireless access. You can set when the PSK should expire, at which time users will be prompted to reactivate their wireless access.

CF_DpskExpireInHours=PSK Expiration:

CF_BatchDpsk=Dynamic PSK Batch Generation

CF_BatchDpskDesc=DPSK batch generation provides two facilities to create multiple Dynamic PSKs at once. You can specify the number of DPSK or upload a profile file (*.csv) which contains information necessary to create DPSKs. Once the generation is done, a result file will be downloaded for your reference. To download an example of profile,

CF_BatchDpskMaxDesc=The maximum allowable number of DPSKs is {1}.

CF_BatchDpskGenNum=Number to Create

CF_BatchDpskUploaded=The profile has been uploaded. {1} DPSKs will be generated after you click the Generate button.

CF_BatchDpskWlan=Target WLAN

CF_BatchDpskUpload=or Upload a Profile

CF_BatchDpskNewRecord=To download the new DPSK record,

CF_BatchDpskGenRecord=To download the generated DPSK record,

E_BatchDpskNoAction=Unrecognizable command for Dynamic PSK Generation.

E_BatchDpskNoWlan=A WLAN with Dynamic PSK enabled in the Default Role is needed before performing Dynamic PSK Batch Generation.

E_BatchDpskNoEntry=The uploaded profile does not contain correct information. Please try another file.

E_BatchDpskUploadTooMuch=Using the uploaded profile will generated {1} DPSKs, but the maximum allowed number of generated batch DPSKs at a time is {2}. Please reduce your profile size and upload it again.

E_InvalidCSV=This does not seem to be a valid CSV file. Please try another file.

E_CsvTooBig=The CSV file you uploaded exceeds the maximum allowed file size. Please try another file.

E_BatchDpskFailName=There is an error at line {1}. The length of the first column is {2} which exceeds {3} characters. Please modify the file and upload it again.

E_BatchDpskFailMacAddr=There is an error at line {1}. The second column "{2}" is not a correct MAC Address format. Please modify the file and upload it again.

CF_ZeroIT=Zero-IT Activation

CF_ZeroITDesc=Zero-IT Activation simplifies the configuration of users' wireless settings. Ask users to connect their wireless devices to the wired network, and then go to the Activation URL shown below. After they download and run the Zero-IT Activation application, their wireless devices will be configured automatically for WLANs that support Zero-IT Activation.

CF_ZeroITURL=Activation URL:

CF_AuthBy=Authentication Server:

CF_RootCA=Root CA

CF_RootCADesc=If you use 802.1X EAP as the authentication method, you will need to install this Root CA certificate on the wireless devices.

CF_RootCAExport=Export Root CA

CF_AdvancedEAP=EAP Server

CF_AdvancedEAPDesc=If you use 802.1X EAP as the authentication method, you may further choose the internal EAP server or an external RADIUS server for 802.1X EAP authentication.

CF_EAPCert=Internal EAP server (certificates will be generated and installed during Zero-IT Wireless Activation)

CF_EAPRadius=External RADIUS server (an EAP-aware RADIUS server is required and must be properly configured)

CF_WlanMaxClient=Max Clients

CF_WlanMaxClientDesc1=Allow only up to

CF_WlanMaxClientDesc2=clients per AP radio to associate with this WLAN

CF_GPSExample=(example: 37.3881398, -122.0258633)

CF_DVlanNoRadius=There is no available RADIUS server.  Please configure RADIUS server first.

CF_BgScan=Background Scanning

CF_BgScanDesc=Do not perform background scanning for this WLAN service.

CF_BgScanNote=Any radio that supports this WLAN will not perform background scanning

CF_BgScanShowWlan=To view all WLANs with background scanning off,

CF_LoadBalanceDesc=Do not perform client load balancing for this WLAN service.

CF_LoadBalanceNote=Applies to this WLAN only. Load balancing may be active on other WLANs



CF_Acls=Access Control

CF_L2AclPolicy=L2/MAC Access Control

CF_L2AclPolicyDesc=You can define L2/MAC access control lists and apply them to WLANs later. Set up an L2/MAC access control list to allow or deny wireless devices based on their MAC addresses.

CF_NoAcls=No ACLs

CF_AclRestriction=Restriction

CF_AclInputMethod=Input Method

CF_AclStations=Stations

CF_AclCreateStation=Create Station

CF_AclAllowAllDesc=Only allow all stations listed below

CF_AclDenyAllDesc=Only deny all stations listed below

CF_AclAllowListed=Only allow listed stations

CF_AclDenyListed=Only deny listed stations

CF_AclSingleInput=Single

CF_AclMultipleInput=Multiple

CF_Policy=L3/4/IP address Access Control

CF_PolicyDesc=You can define L3/4/IP address access control lists and apply them to WLANs later. Set up a L3/4/IP address access control list to allow or deny wireless devices based on their IP addresses.

CF_PolicyDefaultMode=Default Mode

CF_PolicyDefaultAction=Default Action if no rule is matched:

CF_PolicyDefaultDeny=Deny all by default

CF_PolicyDefaultAllow=Allow all by default

CF_PolicyRule=Rules

CF_RuleDstPortNote=Destination Port can be [1] An integer value from 1 to 65534; [2] A string for port range such as 80-443

CF_SelectAcl=L2/MAC

CF_SelectPolicy=L3/4/IP address

CF_AccessPoints=Access Points

CF_AccessPointsDesc=This table lists access points that have already been approved to join the network, or are pending approval.

CF_ApTemplate=Access Point Template

CF_UplinkSelection=Uplink Selection

CF_SmartUplink=Smart (Mesh APs will automatically select the best uplink)

CF_ManualUplink=Manual (Only selected APs can be used for uplink)

CF_MeshDisabled=Disable

CF_ShowAll=Show All APs

CF_MacAddress=MAC Address

CF_ApprovedDesc=Allow this AP to join

CF_RadioA=Radio A (5.0 GHz)

CF_TXPower=TX Power

CF_MeshNoAuto=Note: A mesh AP will choose the channel and TX power automatically.

CF_RadioBG=Radio B/G (2.4 GHz)

CF_RadioN24=Radio B/G/N (2.4 GHz)

CF_RadioNA=Radio A/N (5.0 GHz)

CF_Channelization=Channelization

CF_AccessPointPcy=Access Point Policies

CF_ApprovalDesc=Automatically approve all join requests from APs.

CF_ApprovalNote=To enhance wireless security, deactivate this option. This means you must manually "allow" each newly discovered AP.

CF_AutoPSK=Auto-PSK

CF_AutoPSKDesc=Enable Auto-PSK Injection

CF_GlobalPSK=Global-PSK

CF_GlobalPSKDesc=Use global PSK

CF_APLoadBalacingDesc=Balances the number of clients across adjacent APs.

CF_APMaxClient=Max Clients

CF_APMaxClientDesc=To guarantee wireless connection to all clients, you can limit the number of clients that each radio will manage.

CF_ApGlobalConf=Global Configuration

CF_ApGlobalConfDesc=Use this feature to apply global configuration settings to all Access Points.

CF_ApGlobalModelConfDesc=Use this feature to apply global configuration settings to all Access Points of the particular model.

CF_ApGlobalTxPower=TX Power Adjustment

CF_ApGlobalInternalHeater=Internal Heater

CF_InternalHeaterDescNote=Requires 802.3at or custom PoE injector

CF_GlobalInternalHeaterDesc=Enable internal heater

CF_ApGlobalPoEOut=PoE OUT Port

CF_PoEOutDescNote=requires custom PoE injector

CF_GlobalPoEOutDesc=Enable 'PoE OUT' port

CF_ApGlobalNMode=11N only Mode

CF_GlobalLedOff=Disable Status LEDs

CF_ModelZf7300=ZF 7343/7363

CF_ModelZf7762=ZF 7762



CF_ShowAdvanced=Show Advanced Options

CF_HideAdvanced=Hide

CF_Options=Options

CF_WlanUsage=WLAN Usages

CF_UsageGuest=Guest Access

CF_UsageUser=Standard Usage

CF_UsageAuth=WLAN for authentication only

CF_UsageUserNote=(For most regular wireless network usages.)

CF_UsageGuestNote=(Guest access policies and access control will be applied.)

CF_Wlan11nDesc=(11n APs will operate in 11g mode if you select WEP-64/WEP-128/TKIP.)

CF_WlanTkipDesc=(If you select TKIP, each AP can support only up to 26 clients.)

CF_WLANService=WLAN Service

CF_WLANEnabledPerRadio=Enable WLAN service for this radio.



CF_BlockedClients=Blocked Clients

CF_BlockedClientsDesc=This table lists client devices that are blocked from the WLAN. To unblock a client and allow it to access the WLAN, delete it from the list.

CF_ToClients=To view a list of currently active clients,

CF_Unblock=Unblock

CF_ClientMAC=Client MAC Address



CF_Maps=Maps

CF_MapImage=Map Image

CF_MapImageDesc=Use this workspace to import your worksite floorplans. Floorplan images should be no larger than 720x720 pixels and must be in .PNG, .GIF, or .JPG format. The maximum allowable total size is {1} MB.

CF_MapImageCurrent=Current Image

CF_MapImageImport=Import a floorplan image file

CF_UseMapImage=Import

CF_ImageInfo=Image information

CF_FullName=Full Name

CF_GuestFullName=Guest Name

CF_CreatedBy=Creator

CF_Remarks=Remarks



CF_RolesPolicies=Roles and Policies

CF_Roles=Roles

CF_RolesDesc=Use these features to add new roles and apply policies. You can also update existing roles, which are listed in this table.

CF_GroupAttrs=Group Attributes

CF_AllowWlans=Allow All WLANs

CF_AllowWlansDesc=Allow access to all WLANs

CF_NotAllowWlans=Specify WLAN access

CF_GuestPass=Guest Pass

CF_GuestPassDesc=Allow guest pass generation

CF_Administration=Administration

CF_AdministrationDesc=Allow {zd} Administration

CF_AdminRwDesc=Full privileges (Perform all configuration and management tasks)

CF_AdminRoDesc=Limited privileges (Monitoring and viewing operation status only)

CF_GuestAccess=Guest Access

CF_EnableGuestAccess=Enable Guest Access

CF_GuestAuthDesc=Use these features to set limits for guest pass access to your wireless network.

CF_GuestAuth=Authentication

CF_GuestAuthGuestpass=Use guest pass authentication

CF_GuestAuthNoAuth=No authentication

CF_GuestSharedGuestpass=Allow users to create a single guest pass which can be shared by multiple guests.

CF_GuestTou=Terms of Use

CF_GuestShowTou=Show terms of use

CF_GuestRedirect=Redirection

CF_GuestRedirectOriginal=Redirect to the URL that the user intends to visit.

CF_GuestRedirectUrl=Redirect to the following URL:

CF_GuestAccessPolicies=Guest Access Policies

CF_GuestPassGen=Guest Pass Generation

CF_GuestPassGenDesc=Authenticated users can generate guest passes at the URL shown below.

CF_GuestPassGenURL=Guest Pass Generation URL

CF_GuestPassCountdown=Validity Period

CF_GuestPassCountdownByIssued=Effective from the creation time

CF_GuestPassCountdownByUsed=Effective from first use

CF_GuestAccessValid1=Expire new guest passes if not used within

CF_GuestAccessValid2=days

CF_GuestAccessValid=Valid Days

CF_GuestPrintCustom=Guest Pass Printout Customization

CF_GuestPrintDesc=Use this workspace to import your custom Guest Pass Printout in HTML format. The maximum allowable size is 20KB and javascript is not allowed. There are several system tags inside the sample file, which you can leave in to display dynamic information within your custom Guest Pass Printout. To download a sample,

CF_GuestPrint=Instruction Printout

CF_GuestPrintImportDesc=Import an HTML file for Instruction Printout

CF_GuestPrintPreview=Preview

CF_GuestPrintPreviewUploaded=Preview uploaded instructions

CF_DeniedAccess=Restricted Subnet Access

CF_DeniedAccessDesc=Guest users are automatically blocked from the subnets to which {zd} and its managed APs are connected. If there are other subnets on which you want to block or allow guest users, you can create and configure up to 22 guest access rules below. Note that guest access rules are prioritized in the order that they are listed (1 has highest priority).

CF_DeniedMgmtSubnet=Hint: Layer 3 APs are typically on subnets different from the {zd} subnet.

CF_DeniedSubnet=Denied Subnet

CF_DefaultWebRoot=Default Login Page

CF_DefaultWebRootDesc=Specify the Web page that appears when '/' is accessed. Note: Administrative access is available through the Wireless Access page -- via a link in the lower right corner.

CF_WebRootAdmin=For administrative access to the Web interface

CF_WebRootUser=For user/guest access to the wireless network.

CF_WebCustomLogo=Web Portal Logo

CF_WebCustomLogoDesc=Upload your logo to show it on the Web portal pages. The recommended image size is 138 x 40 pixels and the maximum file size is 20KB.

CF_GuestCustom=Guest Access Customization

CF_GuestCustomDesc=Use this feature to customize the guest user login page. Refer to the picture shown below for the places where the changes will take effect.

CF_GuestLogo=Logo

CF_GuestTitle=Title

CF_GuestDesc=Welcome Text



CF_UserAuth=Users

CF_UserAuthDesc=For authentication and user management purposes, you may choose [1] to use the {zd} internal database, or [2] to use a Windows Active Directory server -- integrating {zd} with your existing infrastructure.

CF_UserAuthentication=User Authentication

CF_InternalUsers=Internal User Database (on {zd})

CF_InternalUsersDesc=This table lists all current user accounts along with basic details. You can add, edit, or delete user accounts. You can also click the Print button to print out the First-time Wireless Network Connection Guide for the user.

CF_Radius=External RADIUS Server

CF_PriRadius=Primary RADIUS Server

CF_SharedSecret=Shared Secret

CF_ConfirmSecret=Confirm Secret

CF_BackupRadius=Backup RADIUS

CF_BackupRadiusEnabled=Enable Backup RADIUS support

CF_BackupRadiusAcctEnabled=Enable Backup RADIUS Accounting support



CF_FailoverPolicy=Failover Policy

CF_FailoverTrial=Max Number of Retries

CF_RequestTimeout=Request Timeout

CF_RetryInterval=Reconnect Primary



CF_GroupOf=Group Of

CF_UpdateInterval=Accounting Update Interval

CF_SecRadius=Secondary RADIUS Server

CF_ActiveDirectory=Active Directory

CF_RADIUS=RADIUS

CF_ADSearchBase=Windows Domain Name

CF_ADSearchBaseExample=(example: domain.{dm})

CF_ADGlobalCatalog=Global Catalog

CF_ADGlobalCatalogEnabled=Enable Global Catalog support

CF_ADAdminDN=Admin DN

CF_ADAdminDNExample=(example: admin@domain.{dm})

CF_ADAdminPassword=Admin Password

CF_ADConfirmPassword=Confirm Password



CF_LDAP=LDAP

CF_LDAPSearchBase=Base DN

CF_LDAPSearchBaseExample=(example: dc=ldap,dc=com)

CF_LDAPAdminDN=Admin DN

CF_LDAPAdminDNExample=(example: uid=admin,dc=ldap,dc=com)

CF_LDAPAdminPassword=Admin Password

CF_LDAPConfirmPassword=Confirm Password

CF_LDAPKeyAttribute=Key Attribute

CF_LDAPKeyAttributeExample=(example: uid)

CF_LDAPFilter=Search Filter

CF_LDAPFilterExample=(example: objectClass=Person, show more...)

CF_LDAPFilterExampleMore=example1: &(attr1=value1)(attr2=value2), example2: |(attr1=value1)(attr2=value2)





CF_AuthAcctSvrsShort=AAA Servers

CF_AuthAcctSvrs=Authentication/Accounting Servers

CF_AuthSvrsDesc=This table lists all authentication mechanisms that can be used whenever authentication is needed.

CF_AuthSvrType=Type

CF_AuthTest=Test Authentication Settings

CF_AuthTestDesc=You may test your authentication server settings by providing a user name and password here. Groups to which the user belongs will be returned and you can use them to configure the role.

CF_AuthTestAgainst=Test Against

CF_AuthSvr=Authentication Server

CF_AcctSvr=Accounting Server

CF_AuthTestSvr=Test Server



CF_Rogues=Rogue Devices

CF_KnownRogues=Known/Recognized Rogue Devices

CF_KnownRoguesDesc=This table lists active rogue wireless devices, which are access points outside of this wireless network but that are in your worksite and interfering with WLAN performance. In addition, rogue devices might pose a security risk if they are connected to your local network.

CF_ToRogues=To review the Monitor tab options,

CF_MarkAsKnown=Mark As Known

CF_RemoveFromKnown=Remove



CF_GeneratedPSK=Generated Dynamic PSKs

CF_GeneratedCert=Generated Dynamic Certs

CF_GeneratedGuestPass=Generated Guest Passes



CF_Mesh=Mesh

CF_MeshMode=Mesh Mode

CF_MeshWlan=Mesh Settings

CF_MeshDesc=Mesh capability allows you to deploy your access points without using wires.

CF_MeshName=Mesh Name (ESSID)

CF_MeshPsk=Mesh Passphrase

CF_MeshKeyGenerate=Generate

CF_MeshChanged=Before you perform another change, please wait a few minutes for the changes to propagate through your mesh network.

CF_MeshTopologyWarn=Mesh Topology Detection

CF_MeshTopologyWarnDesc=The system will trigger a warning event when the following threshold is exceeded.

CF_EnableMesh=Enable mesh hop count detection with a threshold of

CF_EnableFanout=Enable mesh downlinks detection with a threshold of

CF_HopsValue=Hops threshold

CF_FanoutValue=Downlinks threshold

CF_ActiveClientWarn=Active Client Detection

CF_ActiveClientWarnDesc=The {zd} monitors the currently active clients and will trigger a warning event when the active client's rssi is under the threshold.

CF_EnableClientRSSI=Enable client rssi detection with a threshold of

CF_ClientRSSIValue=Client RSSI threshold



CF_AlarmSettings=Alarm Settings

CF_AlarmDef=Alarm Definitions

CF_AlarmNotif=Email Notification

CF_AlarmNotifDesc=Use these features to send email notifications when alarms are triggered in {zd}.

CF_AlarmEmail=Send an email message when an alarm is triggered.

CF_AlarmSnmp=Send an SNMP trap when an alarm is triggered.

CF_SmtpServer=SMTP Server Name

CF_SmtpPort=SMTP Server Port

CF_SmtpUser=SMTP Authentication Username

CF_SmtpPass=SMTP Authentication Password

CF_SmtpPass2=Confirm SMTP Authentication Password

CF_SmtpEnc=SMTP Encryption Options

CF_SnmpServer=SNMP Server IP Address

CF_SnmpPwd=SNMP Password



CF_SelfHealing=Self Healing

CF_SelfHealingDesc={zd} utilizes built-in network "self healing" diagnostics and tuning tools to maximize wireless network performance.

CF_EnableSelfHealing=Activate self healing, including the following options:

CF_AutoAdjRadio=Automatically adjust AP radio power to optimize coverage when interference is present.

CF_AutoAdjChannel=Automatically adjust AP channel when interference is detected.

CF_AutoBand=Automatically reallocate AP bandwidth (load balancing) when usage concentration increases.

CF_BackgroundScan=Background Scanning

CF_BackgroundScanDesc=Background scans are performed by APs to evaluate radio channel usage. The process is progressive; one frequency is scanned at a time. This scanning enables rogue device detection, AP locationing, and self-healing.

CF_EnableScan5G=Run a background scan on 5GHz radio every

CF_EnableScan=Run a background scan on 2.4GHz radio every

CF_EnableReportRogueAP=Report rogue devices in ZD event log

CF_ScanInterval=Scan Interval



CF_IPS=Intrusion Prevention

CF_IPSDesc={zd} utilizes built-in mechanisms to protect against common wireless network intrusions.

CF_AutoProbeLimit=Protect my wireless network against excessive wireless requests

CF_AutoAuthBlock=Temporarily block wireless clients with repeated authentication failures for

CF_BlockInterval=Block Time

CF_Dhcpp=Rogue DHCP Server Detection

CF_DhcppDesc={zd} can scan the network periodically for rogue DHCP servers.

CF_EnableDhcpp=Enable rogue DHCP server detection

CF_AeroScout=AeroScout RFID

CF_AeroScoutEnable=Enable AeroScout RFID tag detection



CF_WISPr=Hotspot Services

CF_WISPrDesc=Hotspot Service (WISPr)

CF_WISPrRedirection=Redirection

CF_WISPrLoginPageDesc1=Redirect unauthenticated user to

CF_WISPrLoginPageDesc2=for authentication.

CF_WISPrLoginPage=Login Page

CF_WISPrStartPage=Start Page

CF_WISPrStartPageDesc=After user is authenticated,

CF_WISPrRedirectToUserURL=redirect to the URL that the user intends to visit.

CF_WISPrRedirectToStartPage=redirect to the following URL:

CF_WISPrStartPageURL=Start Page URL

CF_WISPrSession=User Session

CF_WISPrSessionTimeout=Session Timeout

CF_WISPrSessionTimeoutDesc=Terminate user session after

CF_WISPrIdleTimeout=Idle Timeout

CF_WISPrIdleTimeoutDesc=Terminate idle user session after

CF_WISPrLocation=Location Information

CF_WISPrLocationId=Location ID

CF_WISPrLocationIdExample=(e.g. isocc=us,cc=1,ac=408,network=ACMEWISP_NewarkAirport)

CF_WISPrLocationName=Location Name

CF_WISPrLocationNameExample=(e.g. ACMEWISP,Gate_14_Terminal_C_of_Newark_Airport)

CF_WISPrWalledGarden=Walled Garden

CF_WISPrWalledGardenDesc=Unauthenticated users are allowed to access the following destinations:

CF_WISPrWalledGardenNote=(e.g. mydomain.com, 192.168.1.1:80, 192.168.1.1/24 or 192.168.1.1:80/24)

CF_WISPrWalledGardenInputField=Walled Garden input field

CF_WISPrRestrictedSubnet=Restricted Subnet Access

CF_WISPrRestrictedSubnetDesc=Users can define L3/4 IP address access control rules for each hotspot service to allow or deny wireless devices based on their IP addresses.

CF_WISPrHotspotName=Hotspot Name

CF_WISPrHotspotList=Hotspot Services

CF_WISPrHotspotTableNote=

CF_WISPrHotspotServiceUnavailable=There is no available hotspot service.  Please configure hotspot service first.

CF_WISPrStartUserPage=The user's intended page

CF_WISPrInterimUpdate=Send Interim-Update every

CF_WISPrInterimUpdateFrequency=Interim Update Frequency

CF_WISPrMoreRestrictedSubnet=More Items

CF_WISPrMoreWalledGarden=More Items

CF_WISPrMACAuthDesc=Enable MAC authentication bypass(no redirection).

CF_WISPrAdditionalRADIUSAttributes=Location Information

CF_WISPrAdditionalRADIUSAttributesNote=



CF_TelnetdDesc={zd} supports Telnet Server.

CF_TelnetdEnabled=Enable Telnet Server



CF_Snmp=SNMP Agent

CF_SnmpDesc={zd} supports SNMPv2 agent. Enter the Read-Only and Read-Write communities.

CF_SnmpEnabled=Enable SNMP Agent

CF_SnmpVer=SNMP Version

CF_SnmpRO=SNMP RO community

CF_SnmpRW=SNMP RW community

CF_SnmpSysContact=System Contact

CF_SnmpSysLocation=System Location



CF_SnmpTrap=SNMP Trap

CF_SnmpTrapDesc=Enter the SNMP Trap server IP where {zd} will send SNMP Traps to.

CF_SnmpTrapEnabled=Enable SNMP Trap

CF_SnmpTrapIP1=Trap Server IP

CF_SnmpTrapIP2=Trap Server2 IP

CF_SnmpTrapIP3=Trap Server3 IP

CF_SnmpTrapPassword=Trap Password



CF_Certificate=SSL Certificate

CF_CertGen=Generate a request

CF_CertGenDesc=Create a new certificate request. For more information,

CF_CertGenCN=Common Name

CF_CertGenDN=Subject Alternative Name

CF_CertGenOrgan=Organization

CF_CertGenOrganUnit=Organization Unit

CF_CertGenCity=Locality/ City

CF_CertGenState=State/ Province

CF_CertGenCountry=Country

CF_CertGenPW=Key pair password

CF_CertGenConfirmPW=Confirm password

CF_CertImport=Import Signed Certificate

CF_CertImportDesc=Import a signed certificate file to replace the current certificate.

CF_CertImportKeyPair=Key pair password

CF_CertInfoDesc=To show current certificate information,



CF_CertGenCNDesc=The fully qualified domain name for your web server. This must be an exact match. e.g. www.{dm}

CF_CertGenDNDesc=The subject alternative name extension allows various literal values to be included in the configuration file. These include DNS (type your domain name), IP (type your IP address).

CF_CertGenOrganDesc=The exact legal name of your organization. Do not abbreviate your organization name. e.g.{cn}, Inc.

CF_CertGenOrganUnitDesc=Division or department of the organization. e.g. Network Management

CF_CertGenCityDesc= The city where your organization is legally located. e.g. Sunnyvale

CF_CertGenStateDesc=The state or province where your organization is legally located. Can not be abbreviated. e.g. CA

CF_CertGenCountryDesc=The two-letter ISO abbreviation for your country. e.g. US= United States

CF_CertDone=I am done with importing, reboot the system now.

CF_CertDoneDesc=New certificate is installed. Please use the dialog below to import intermediate certificate.

CF_CertSavePrivateKey=Back up private key

CF_CertImportPrivateKey=Import Private Key

CF_CertImportPrivateKeyDesc=Import private key to match your certificate. After importing the private key, you must import your signed certificate again.

CF_CertPrivateKeyDone=Private key has been replaced.  Please import a new certificate that matches this private key.  Important: Mismatched certificate and private key will cause {zd} to become inaccessible.

CF_CertImportIntermediate=Import Intermediate Certificates

CF_CertImportIntermediateDesc=Import intermediate certificates for installed certificate. Please import intermediate certificates in the correct certificate chain order (i.e., in the reverse order that a certificate was signed)

CF_CertLoadICDone=The intermediate certificate has been installed. Please select next level intermediate certificate to import.

CF_CertRestore=Restore to Default Certificate/Private Key

CF_CertRestoreDesc=If needed, you can discard the imported certificate and private key.  {zd} will use factory default certificate/key after restore and reboot.

CF_CertRestoreCfm=Are you sure you want to restore {zd} to the default certificate and private key?

CF_CertBackupPrivKey=Back up private key

CF_CertBackupPrivKeyDesc=If you want to apply the same certificate from this {zd} to other {zd}s, please back up the private key from this {zd} and then apply it to other {zd}s for certificate key pairing.

CF_CertRegen=Re-generate private key of a specific key length

CF_CertRegenDesc=Re-generate a new private key of a specific key length.  This function is only needed when your certificate vendor only accepts 2048 key length instead of 1024 key length. Warning: The {zd} will be rebooted after re-generating a new private key.

CF_CertRegenCfm=Are you sure you want to re-generate {zd}'s private key?

CF_CertKeyLen=Private key length

CF_CertWildcardDesc=The imported certificate is a wildcard certificate. Please fill in the {zd} redirect URL and then click the "OK" button. If you want to modify this URL in the future, you will need to import this certificate again.



CF_WlanPriority=Priority

CF_PiorityHigh=High

CF_PriorityLow=Low



# Monitor / Portlets



MN_Wlans=WLANs

MN_WlansDesc=These tables list [1] currently active WLANs, [2] currently active WLAN Groups, and [3] an up-to-date record of WLAN events/activities. Click on a WLAN-name link, WLAN-Group-name link or MAC-address link for more details.

MN_WlanDetail=This table shows detailed information about the selected WLAN, such as the clients and events associated with it.

MN_WlanInfo=WLAN Information

MN_General=General

MN_Statistics=Statistics



MN_PacketsReceived=Packets Received

MN_BytesReceived=Bytes Received

MN_PacketsTransmitted=Packets Transmitted

MN_BytesTransmitted=Bytes Transmitted

MN_PacketsBytesReceived=Packets/Bytes Received

MN_PacketsBytesTransmitted=Packets/Bytes Transmitted



MN_PacketsBytesClientReceived=Received from client

MN_PacketsBytesClientTransmitted=Transmitted to client



MN_WlanGroupInfo=WLAN Group Information

MN_HasVlan=VLAN Override

MN_WlanGroupAP=Member APs

MN_WlanGroupDetail=This table shows detailed information about the selected WLAN Group, such as the APs, clients and events associated with it.



MN_AccessPoints=Access Points

MN_AccessPointsDesc=This table lists all currently active access points, and highlights basic details, such as number of clients per AP. Below is an AP-specific table of events and activities.

MN_AccessPointDetail=This table lists detailed information about the selected access point, such as the clients and events associated with it.

MN_APDisconnected=Disconnected

MN_APConnected=Connected

MN_APPending=Approval Pending

MN_APUpgrading=Upgrading Firmware

MN_APProvisioning=Provisioning

MN_APMeshIsland=Isolated Mesh AP

MN_APNext=Next AP[{1}]

MN_APPrev=Prev AP[{1}]

MN_RestartApCfm=Restarting AP may cause brief client usage disruption. Press OK to proceed.

MN_RecoverMesh=Recover



MN_RealTime=Real Time Monitoring

MN_DisplayTime=Period of Time for Display

MN_StartMonitoring=Start Monitoring

MN_StopMonitoring=Stop Monitoring



MN_Neighbors=Neighbor APs

MN_Uplink=Uplink

MN_Downlinks=Downlinks

MN_UplinkHistory=Uplink History



MN_Clients=Currently Active Clients

MN_ClientsDesc=This table lists all currently connected client devices. Only those devices with a status of "authorized" are permitted access to the network. To prevent an "unauthorized" client from attempting to connect to your network, click Block. To troubleshoot a problematic connection, click Delete. (That client can then reconnect to the WLAN.)

MN_ClientDetail=This shows the detailed information about the selected client, including the events associated with it.

MN_CliUnauthorized=Unauthorized

MN_CliAuthorized=Authorized

MN_CliAuthenticating=Authenticating

MN_CliPSKExpired=PSK Expired



MN_ToBlockedClients=To show a list of blocked clients,



MN_Rogues=Rogue Devices

MN_RoguesDesc=This table lists unknown access points that might pose a security threat to your network if connected to the LAN. If a rogue device neither poses a threat nor interferes with network coverage, click Mark as known, which neutralizes that AP's effect on {zd} and on Web interface monitoring.

MN_ToKnownRogues=To review a list of all known rogue devices,



MN_Generated=Generated PSK/Certs

MN_GeneratedDesc=These tables list [1] generated PSKs and [2] generated certificates. You can review the Dynamic PSKs and Dynamic Certs generated for your users. You may also remove them if necessary, which is especially useful in the event that a user should no longer have access to your wireless network.



MN_Guests=Generated Guest Passes

MN_GuestsDesc=These tables list the generated guest passes. You can review the guest passes generated for your users. You may also remove them if necessary.

MN_GuestWLAN=WLAN



MN_Events=All Events/Activities

MN_EventsDesc=This workspace displays the most recent records in {zd}'s internal log file. (For information on saving this information to a syslog server, see the Online Help.)



MN_Alarms=All Alarms

MN_AlarmsDesc=This workspace lists all uncleared alarms. If all listed alarms have been cleared or are no longer valid, click Clear All.

MN_DeletAllCfm=Are you sure you want to delete all entries?



MN_Mesh=Mesh

MN_MeshDesc=This workspace shows the mesh status and mesh topology.

MN_MeshStatus=Mesh Status

MN_MeshSSID=Mesh SSID

MN_RootAps=Root APs

MN_RootAp=Root AP

MN_MeshAps=Mesh APs

MN_MeshAp=Mesh AP

MN_LinkAps=eMesh APs

MN_LinkAp=eMesh AP

MN_LinkType=Type

MN_DisplayedOverTotal=Displayed/Total

MN_MeshTopology=Mesh Topology

MN_RSSI_Link_AP=Signal strength from/to uplink AP
2010-07-14 09:39:36,638 INFO     Login to ZD [192.168.0.2] successfully!
2010-07-14 09:39:37,075 INFO     set session-timeout to 600 seconds
2010-07-14 09:39:37,513 DEBUG    Parsing messages...
2010-07-14 09:39:44,486 INFO     [TEST 01] Get ZD messages bundled
2010-07-14 09:39:57,717 DEBUG    Clean up the Selenium Manager
2010-07-14 09:40:00,635 INFO     [TEA.Module u.zd.zd_messages_tea] Result:
{   'message': '',
    'result': 'PASS',
    'shell_key': '!v54!',
    'u.zd.zd_messages_tea': None,
    'zd': <RuckusAutoTest.components.ZoneDirector.ZoneDirector2 instance at 0x036BDD78>,
    'zd_cli': <RuckusAutoTest.components.ZoneDirectorCLI.ZoneDirectorCLI instance at 0x03B72940>}
2010-07-14 09:40:01,042 INFO     Close logging file D:\s3\p4-depot\tools\rat-branches\saigon\runlog\tea_u.zd.zd_messages_tea\log_tea_u.zd.zd_messages_tea_201007140935.txt

'''
