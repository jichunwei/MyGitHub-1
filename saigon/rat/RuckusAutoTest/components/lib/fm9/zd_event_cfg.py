'''
Support page:
    Configure > ZoneDirectors > Event Configuration.
Support its sub tab: Event Configuration and Configured ZDs
1. Event Configuration tab:
Support following functions
    1.1 Create a new event configuration:
        Support to configure all its sub tabs: System Admin, Mesh, Configuration, Client, AP Admin and Performance.

    1.2 Assign ZD devices to an event config template
    1.3 Edit an event cfg template.
    1.4 Delete an event cfg template.
    1.5: Copy an event cfg template.

2. Configured ZDs tab:
   Support following functions
    2.1 Fill in and do query ZD device
    2.2 Get event configuration assigned to a ZD.
Note:
. Not support Config Task Log tab.

'''
import logging
import time
from pprint import pformat
from RuckusAutoTest.components.lib.AutoConfig import (
                                                Ctrl,
                                                set as ac_set,
                                                get as ac_get
                                              )
from RuckusAutoTest.components.lib import common_fns as fns
from RuckusAutoTest.components.lib.fm9 import _report_filter as rf
#-------------------------------------------------------------------------------
#                        PUBLIC METHODs
def create_event_cfg(fm,
                     cfg_name,
                     cfg
    ):
    '''
    To create an event cfg
    '''
    s, l = fm.s, locators

    nav_to(fm, TAB_1, True)
    ac_set(
        fm.s, l, {'cfg_name': cfg_name},
        ['create_event_cfg', {'sleep': 5}, 'cfg_name']
    )
    _un_select_all_event_cfgs(s)
    _fill_in_cfg(fm, cfg)
    s.click_and_wait(l['save_btn'])

    msg = _get_save_event_cfg_msg(fm)
    if msg:
        raise Exception('Cannot save the event cfg. Error: %s' % msg)


def assign_zds(fm,
               cfg_name,
               ip_list, view = 'All ZoneDirectors'
    ):
    '''
    to assign ZDs to an ZD event cfg template.
    . fm: FM object
    . cfg_name: name of event cfg template
    . ip_list: list of ZD ips to assign to the cfg_name
    . view: zd view

    . return: raise exception if any error
    '''
    r = find_event_cfg_tmpl(fm, cfg_name)
    if not r:
        raise Exception('Not found the event cfg template %s' % cfg_name)

    fm.s.click_and_wait(r['links']['assign_zds'])

    _select_zd(fm.s, ip_list, view)
    fm.s.click_and_wait(locators['save_btn'])


def edit_event_cfg(fm,
                   cfg_name,
                   new_cfg
    ):
    '''
    to edit an event cfg template
    . cfg_name: event cfg name template to do edit
    . new_cfg: a new cfg to do edit
    '''
    s, l = fm.s, locators
    nav_to(fm, TAB_1, True)

    r_info = find_event_cfg_tmpl(fm, cfg_name)
    if not r_info:
        raise Exception('Not found the event cfg template %s' % cfg_name)

    s.click_and_wait(r_info['links']['edit'])
    time.sleep(5)

    _un_select_all_event_cfgs(s)
    _fill_in_cfg(fm, new_cfg)
    s.click_and_wait(l['save_btn'])


def delete_event_cfg(fm, cfg_name):
    '''
    To delete an event cfg template
    '''
    r_info = find_event_cfg_tmpl(fm, cfg_name)
    if not r_info:
        raise Exception('Not found the event cfg template %s' % cfg_name)

    fm.s.click_and_wait(r_info['links']['delete'])
    # Get OK, Cancel pop up. Otherwise, an exception will be raised
    if fm.s.is_confirmation_present():
        logging.info('Got a pop up window "%s"' % fm.s.get_confirmation())

    msg = _get_delete_status_msg(fm)

    if msg:
        raise Exception(
            'Cannot delete the event cfg %s. Error: %s' % (cfg_name, msg)
        )


def copy_event_cfg(fm,
                   cfg_name,
                   new_name
    ):
    '''
    to copy an event cfg template to another one.
    '''
    s, l = fm.s, locators

    r_info = find_event_cfg_tmpl(fm, cfg_name)
    if not r_info:
        raise Exception('Not found the event cfg template %s' % cfg_name)

    s.click_and_wait(r_info['links']['copy'])
    #s.type_text(l['cfg_name'], new_name)
    ac_set(s, l, {'cfg_name': new_name})
    s.click_and_wait(l['save_btn'])

    msg = _get_save_event_cfg_msg(fm)
    if msg:
        raise Exception('Cannot save the event cfg. Error: %s' % msg)


def find_event_cfg_tmpl(fm, cfg_name):
    '''
    to find a saved event cfg template
    '''
    nav_to(fm, TAB_1, True)
    time.sleep(1)
    return _get_tbl(
        fm, 'event_cfg_tbl',
        dict(
             match=dict(name = cfg_name),
             op = 'equal',
             get = '1st'
        )
    )


def find_configured_zd_by_ip(fm,
                             ip,
                             view = 'All ZoneDirectors'
    ):
    '''
    to find a configured zd by ip in a view. By default, it will find it in
    'All ZoneDirectors' view.
    . fm: FM instance.
    . ip: zd ip to find
    . view: ZD view to find.
    '''
    return _find_configured_zd(fm, dict(ip = ip), view)


def find_configured_zd_by_zd_name(fm,
                               name,
                               view = 'All ZoneDirectors'
    ):
    '''
    to find a configured zd by name in a view. By default, it will find it in
    'All ZoneDirectors' view.
    . fm: FM instance.
    . name: zd name to find
    . view: ZD view to find.
    '''
    return _find_configured_zd(fm, dict(name = name), view)


def find_configured_zd_by_cfg_name(fm,
                                   cfg_name,
                                   view = 'All ZoneDirectors'
    ):
    '''
    to find a zd is configured by event cfg_name in a view. By default,
    it will find it in 'All ZoneDirectors' view.
    . fm: FM instance.
    . cfg_name: zd event cfg name template to find
    . view: ZD view to find.
    '''
    return _find_configured_zd(fm, dict(cfg_name = cfg_name), view)


def find_configured_zd_by_match(fm,
                                match,
                                view = 'All ZoneDirectors'
    ):
    '''
    to find a configured zd by a match in a view. By default, it will find it in
    'All ZoneDirectors' view.
    Note:
         Its API is quite complex method. Not recommend using this one.
    . fm: FM instance.
    . match: a match to find. Refer to _query_configured_zd for detail.
    . view: ZD view to find.
    '''
    return _find_configured_zd(fm, match, view)


def get_event_cfg_tmpl(fm,
                       cfg_name,
                       cfg_ks = {}
    ):
    '''
    to get events which are confiugred in an event template cfg
    . cfg_name: event config to get.
    . cfg_ks:
    '''
    r = find_event_cfg_tmpl(fm, cfg_name)
    if not r:
        raise Exception('Not found the event cfg template %s' % cfg_name)

    fm.s.click_and_wait(r['links']['edit'])

    return _get_configured_events(fm, cfg_ks)


def get_configured_events_by_zd(fm,
                                ip,
                                view = 'All ZoneDirectors',
                                cfg_ks = {}
    ):
    '''
    to get events which are configured in a zd. By default, get all.
    . zd_ip: an zd ip to get events which are configured on this ZD.
    . cfg_ks: keys to get values.
    '''
    nav_to(fm, TAB_2, True)

    r = find_configured_zd_by_ip(fm, ip, view)
    if not r:
        raise Exception('Not found zd ip %s in view %s' % (ip, view))

    fm.s.click_and_wait(r['links']['cfg_name'])

    return _get_configured_events(fm, cfg_ks)

def get_configured_zd_ip_by_cfg_name(fm, cfg_name, view = 'All ZoneDirectors'):
    '''
    to get zd ip configured by an event cfg_name in a "view".
    '''
    r = find_configured_zd_by_cfg_name(fm, cfg_name, view)
    if not r:
        raise Exception(
            'Not found zd configured by %s in view %s' % (cfg_name, view)
        )

    return r['row']['ip']
#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
TAB_1 = 'event_cfg'
TAB_2 = 'configured_zds'
TAB_3 = 'config_task_log'

default_event_key_locs = dict(
    sys_admin = dict(
        sa_admin_init_dhcpp = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10037']", 'check'),
        sa_admin_rouge_dhcp_srv = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10040']", 'check'),
        sa_admin_stop_dhcp = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10038']", 'check'),

        sa_admin_sys_upgraded_success = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10017']", 'check'),
        sa_admin_templic_expired = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10034']", 'check'),
        sa_admin_temp_lic_oneday = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10035']", 'check'),
        sa_admin_templic_twodays = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10036']", 'check'),
        sa_admin_trig_dhcpp = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10039']", 'check'),
    ),
    mesh = dict(
        m_ap_activate_mesh = Ctrl("//input[contains(@name, 'Mesh') and @value='10090']", 'check'),
        m_map_isolate = Ctrl("//input[contains(@name, 'Mesh') and @value='10086']", 'check'),
        m_map_uplink_connected = Ctrl("//input[contains(@name, 'Mesh') and @value='10077']", 'check'),
    ),
    cfg = dict(
        c_admin_sys_installed = Ctrl("//input[contains(@name, 'Config') and @value='10016']", 'check'),
    ),
    performance = dict(),
    client = dict(
        cl_client_disconect = Ctrl("//input[contains(@name, 'Client') and @value='10154']", 'check'),
        cl_client_join = Ctrl("//input[contains(@name, 'Client') and @value='10148']", 'check'),
    ),
    ap_admin = dict(
        aa_ap_delete = Ctrl("//input[contains(@name, 'APAdmin') and @value='10087']", 'check'),
        aa_ap_factory_restore = Ctrl("//input[contains(@name, 'APAdmin') and @value='10089']", 'check'),

        aa_ap_joined = Ctrl("//input[contains(@name, 'APAdmin') and @value='10097']", 'check'),
        aa_ap_lost = Ctrl("//input[contains(@name, 'APAdmin') and @value='10076']", 'check'),
        aa_ap_lost_heartbeat = Ctrl("//input[contains(@name, 'APAdmin') and @value='10075']", 'check'),
        aa_ap_reset = Ctrl("//input[contains(@name, 'APAdmin') and @value='10088']", 'check'),
        aa_admin_scan_ap = Ctrl("//input[contains(@name, 'APAdmin') and @value='10033']", 'check'),
    ),

)

configurable_event_key_locs = dict(
    #locators for System Admin (sa)
    sys_admin = dict(
        # locators for System Admin tab
        sa_ac_license_ap_diff = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10187']", 'check'),
        sa_ac_working_mode = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10188']", 'check'),
        sa_ap_80211_dos_mgmt_flood = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10115']", 'check'),
        sa_ap_80211_dos_probe_req_flood = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10114']", 'check'),

        sa_ap_mgmt_url_changed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='16']", 'check'),
        sa_adhoc_network_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10110']", 'check'),
        sa_adhoc_interference_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10110']", 'check'),

        sa_admin_auth_conn_err = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10027']", 'check'),
        sa_admin_auto_restore_cert = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10008']", 'check'),
        sa_admin_change_workmode = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10245']", 'check'),
        #sa_admin_init_dhcp = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10037']", 'check'),
        sa_admin_login = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10025']", 'check'),
        sa_admin_login_attack_lockout = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10029']", 'check'),
        #####
        sa_admin_login_failed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10026']", 'check'),
        sa_admin_login_lockout = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10028']", 'check'),
        sa_admin_logout = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10030']", 'check'),
        sa_admin_remove_addif = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10255']", 'check'),
        sa_admin_renew_cert = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10007']", 'check'),
        sa_admin_replace_cert = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10005']", 'check'),

        sa_admin_replace_privatekey = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10006']", 'check'),
        sa_admin_restart = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10002']", 'check'),
        sa_admin_restarted = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10001']", 'check'),

        #sa_admin_rouge_dhcp_server = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10040']", 'check'),
        sa_admin_set_dhcp = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10012']", 'check'),
        sa_admin_shutdown = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10003']", 'check'),

        sa_admin_system_auto_recovery_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10024']", 'check'),
        sa_admin_system_auto_recovery_success = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10023']", 'check'),
        sa_admin_system_integrity_check_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10022']", 'check'),
        sa_admin_system_integrity_check_success = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10021']", 'check'),

        sa_admin_system_upgraded_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10020']", 'check'),
        sa_admin_system_upgraded_reboot_rollback = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10019']", 'check'),
        sa_admin_system_upgraded_rollback = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10018']", 'check'),
        sa_admin_update_addiff = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10249']", 'check'),
        sa_admin_upgrade = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10004']", 'check'),

        sa_associated_with_zd = Ctrl("//input[contains(@name, 'SysAdmin') and @value='12']", 'check'),

        sa_ctrl_model_mismatched = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10212']", 'check'),
        sa_ctrl_admin_upg_from_local = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10231']", 'check'),


        sa_ctrl_admin_upg_from_peer = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10233']", 'check'),
        sa_ctrl_failed_get_uploaded = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10235']", 'check'),

        sa_ctrl_failed_untar_uploaded = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10239']", 'check'),
        sa_ctrl_local_action_done = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10247']", 'check'),
        sa_ctrl_peer_not_back = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10242']", 'check'),
        sa_ctrl_peer_upgrade_disconnected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10253']", 'check'),
        ###########
        sa_ctrl_receive_failover = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10256']", 'check'),
        sa_ctrl_req_peer_upgrade = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10248']", 'check'),
        sa_ctrl_send_failover = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10258']", 'check'),
        sa_ctrl_upgrade_disconnected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10241']", 'check'),

        sa_fm_login = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10185']", 'check'),
        sa_fm_login_failed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10186']", 'check'),
        sa_fw_downloaded = Ctrl("//input[contains(@name, 'SysAdmin') and @value='17']", 'check'),
        sa_lanrouge_ap_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10109']", 'check'),
        sa_mac_spoofing_ap_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10112']", 'check'),

        sa_radius_acct_failover = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10227']", 'check'),
        sa_radius_auth_failover = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10226']", 'check'),
        sa_radius_webauth_failover = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10228']", 'check'),
        sa_reboot_because_of_system_failure = Ctrl("//input[contains(@name, 'SysAdmin') and @value='13']", 'check'),
        sa_reboot_request_failed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='14']", 'check'),

        sa_rouge_ap_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10108']", 'check'),
        sa_rouge_interference_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10113']", 'check'),
        sa_ssid_spoofing_ap_detected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10111']", 'check'),

        sa_tr069d_clone_cfg = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10179']", 'check'),
        sa_tr069d_download_file_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10224']", 'check'),
        sa_tr069d_download_file_timeout = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10225']", 'check'),
        sa_tr069d_execute_reboot_command = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10178']", 'check'),
        sa_tr069d_fmalarm_list_changed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10184']", 'check'),
        sa_tr069d_inform_return = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10180']", 'check'),
        sa_tr069d_tmpl_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10183']", 'check'),
        sa_tr069d_tmpl_success = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10182']", 'check'),
        sa_tr069d_upg_img = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10177']", 'check'),
        sa_tr069d_verify_download_file_fail = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10176']", 'check'),
        sa_tr069d_write_tmpl = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10181']", 'check'),
        sa_tr069d_standby_skip_command = Ctrl("//input[contains(@name, 'SysAdmin') and @value='10236']", 'check'),

        sa_zd_cloned_succes_for_old_ver = Ctrl("//input[contains(@name, 'SysAdmin') and @value='204']", 'check'),
        sa_zd_mgmt_server_changed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='206']", 'check'),
        sa_zd_mesh_ap_uplink_disconnected = Ctrl("//input[contains(@name, 'SysAdmin') and @value='417']", 'check'),

        sa_zd_reboot_after_restarted_for_old_ver = Ctrl("//input[contains(@name, 'SysAdmin') and @value='201']", 'check'),
        sa_zd_reboot_after_shutdown_for_old_ver = Ctrl("//input[contains(@name, 'SysAdmin') and @value='202']", 'check'),
        sa_zd_upg_failed = Ctrl("//input[contains(@name, 'SysAdmin') and @value='205']", 'check'),
        sa_zd_upg_success_for_old_ver = Ctrl("//input[contains(@name, 'SysAdmin') and @value='203']", 'check'),
    ),
    # locators for Mesh (m) tab
    mesh = dict(
        m_ap_deactivate_mesh = Ctrl("//input[contains(@name, 'Mesh') and @value='10091']", 'check'),
        m_ap_mesh_mode_change = Ctrl("//input[contains(@name, 'Mesh') and @value='10095']", 'check'),
        m_ap_no_mesh_uplink = Ctrl("//input[contains(@name, 'Mesh') and @value='10102']", 'check'),
        m_admin_enable_ctrl = Ctrl("//input[contains(@name, 'Mesh') and @value='10232']", 'check'),

        m_map_conn_block = Ctrl("//input[contains(@name, 'Mesh') and @value='10083']", 'check'),
        m_map_conn_fail_auth = Ctrl("//input[contains(@name, 'Mesh') and @value='10081']", 'check'),
        m_map_conn_fail_depth_exceeded = Ctrl("//input[contains(@name, 'Mesh') and @value='10082']", 'check'),
        m_map_conn_unblock = Ctrl("//input[contains(@name, 'Mesh') and @value='10084']", 'check'),
        m_map_disconn = Ctrl("//input[contains(@name, 'Mesh') and @value='10085']", 'check'),
        m_map_downlink_connected = Ctrl("//input[contains(@name, 'Mesh') and @value='10079']", 'check'),
        m_map_root_downlink_connected = Ctrl("//input[contains(@name, 'Mesh') and @value='10080']", 'check'),
        m_map_uplink_to_root_connected = Ctrl("//input[contains(@name, 'Mesh') and @value='10078']", 'check'),

        m_map_accept_map_fanout_warn = Ctrl("//input[contains(@name, 'Mesh') and @value='10250']", 'check'),
        m_map_accept_map_hops_warn = Ctrl("//input[contains(@name, 'Mesh') and @value='10246']", 'check'),

        m_mesh_state_update_map = Ctrl("//input[contains(@name, 'Mesh') and @value='10252']", 'check'),
        m_mesh_state_update_map_no_chan = Ctrl("//input[contains(@name, 'Mesh') and @value='10251']", 'check'),
        m_mesh_state_update_root = Ctrl("//input[contains(@name, 'Mesh') and @value='10230']", 'check'),
        m_mesh_state_update_root_no_chan = Ctrl("//input[contains(@name, 'Mesh') and @value='10234']", 'check'),

        m_zd_emesh_ap_downlink_connected_with_map = Ctrl("//input[contains(@name, 'Mesh') and @value='424']", 'check'),
        m_zd_emesh_ap_downlink_disconnected_with_map = Ctrl("//input[contains(@name, 'Mesh') and @value='425']", 'check'),
        m_zd_emesh_ap_uplink_connected_with_map = Ctrl("//input[contains(@name, 'Mesh') and @value='422']", 'check'),
        m_zd_emesh_ap_uplink_disconnected_with_map = Ctrl("//input[contains(@name, 'Mesh') and @value='423']", 'check'),

        m_zd_mesh_ap_downlink_connected_with_emap = Ctrl("//input[contains(@name, 'Mesh') and @value='420']", 'check'),
        m_zd_mesh_ap_downlink_disconnected_with_emap = Ctrl("//input[contains(@name, 'Mesh') and @value='421']", 'check'),
        m_zd_mesh_ap_uplink_connected_with_emap = Ctrl("//input[contains(@name, 'Mesh') and @value='418']", 'check'),
        m_zd_mesh_ap_uplink_disconnected_with_emap = Ctrl("//input[contains(@name, 'Mesh') and @value='419']", 'check'),
    ),
    # locators for Configuration (c) tab
    cfg = dict(
        c_admin_change_pass = Ctrl("//input[contains(@name, 'Config') and @value='10015']", 'check'),
        c_admin_ctrl_pass = Ctrl("//input[contains(@name, 'Config') and @value='10243']", 'check'),
        c_admin_ctrl_peerip = Ctrl("//input[contains(@name, 'Config') and @value='10238']", 'check'),
        c_admin_create_addif = Ctrl("//input[contains(@name, 'Config') and @value='10237']", 'check'),
        c_admin_disable_ap_mgmt_vlan = Ctrl("//input[contains(@name, 'Config') and @value='10051']", 'check'),
        c_admin_disable_zd_mgmt_vlan = Ctrl("//input[contains(@name, 'Config') and @value='10054']", 'check'),
        c_admin_disable_limited_zd = Ctrl("//input[contains(@name, 'Config') and @value='10057']", 'check'),
        c_admin_disable_snmpd = Ctrl("//input[contains(@name, 'Config') and @value='10047']", 'check'),
        c_admin_disable_snmptrap = Ctrl("//input[contains(@name, 'Config') and @value='10049']", 'check'),
        c_admin_disable_tr069 = Ctrl("//input[contains(@name, 'Config') and @value='10045']", 'check'),

        c_admin_enable_ap_mgmt_vlan = Ctrl("//input[contains(@name, 'Config') and @value='10050']", 'check'),
        c_admin_enable_zd_mgmt_vlan = Ctrl("//input[contains(@name, 'Config') and @value='10053']", 'check'),
        c_admin_enable_both_limited_zd = Ctrl("//input[contains(@name, 'Config') and @value='10055']", 'check'),
        c_admin_enable_one_limited_zd = Ctrl("//input[contains(@name, 'Config') and @value='10056']", 'check'),
        c_admin_enable_snmpd = Ctrl("//input[contains(@name, 'Config') and @value='10046']", 'check'),
        c_admin_enable_snmptrap = Ctrl("//input[contains(@name, 'Config') and @value='10048']", 'check'),
        c_admin_enable_tr069 = Ctrl("//input[contains(@name, 'Config') and @value='10044']", 'check'),

        c_admin_keep_ap_mgmt_vlan = Ctrl("//input[contains(@name, 'Config') and @value='10052']", 'check'),
        c_admin_restore_default = Ctrl("//input[contains(@name, 'Config') and @value='10011']", 'check'),
        c_admin_restore_saved = Ctrl("//input[contains(@name, 'Config') and @value='10010']", 'check'),
        c_admin_set_dhcps = Ctrl("//input[contains(@name, 'Config') and @value='10041']", 'check'),
        c_admin_set_dhcps_failed = Ctrl("//input[contains(@name, 'Config') and @value='10042']", 'check'),
        c_admin_set_hostname = Ctrl("//input[contains(@name, 'Config') and @value='10014']", 'check'),
        c_admin_set_ip = Ctrl("//input[contains(@name, 'Config') and @value='10013']", 'check'),
        c_admin_stop_dhcps = Ctrl("//input[contains(@name, 'Config') and @value='10043']", 'check'),

        c_ctrl_active_connected = Ctrl("//input[contains(@name, 'Config') and @value='10219']", 'check'),
        c_ctrl_active_disconnected = Ctrl("//input[contains(@name, 'Config') and @value='10221']", 'check'),
        c_ctrl_change_state = Ctrl("//input[contains(@name, 'Config') and @value='10216']", 'check'),
        c_ctrl_change_to_active = Ctrl("//input[contains(@name, 'Config') and @value='10218']", 'check'),
        c_ctrl_failover = Ctrl("//input[contains(@name, 'Config') and @value='10210']", 'check'),
        c_ctrl_ip_mismatched = Ctrl("//input[contains(@name, 'Config') and @value='10213']", 'check'),
        c_ctrl_max_ap_mismatched = Ctrl("//input[contains(@name, 'Config') and @value='10214']", 'check'),
        c_ctrl_no_file = Ctrl("//input[contains(@name, 'Config') and @value='10203']", 'check'),
        c_ctrl_pass_mismatched = Ctrl("//input[contains(@name, 'Config') and @value='10215']", 'check'),
        c_ctrl_restore_saved = Ctrl("//input[contains(@name, 'Config') and @value='10200']", 'check'),
        c_ctrl_restore_saved_from_peer = Ctrl("//input[contains(@name, 'Config') and @value='10202']", 'check'),
        c_ctrl_same_cfg = Ctrl("//input[contains(@name, 'Config') and @value='10217']", 'check'),
        c_ctrl_standby_connected = Ctrl("//input[contains(@name, 'Config') and @value='10220']", 'check'),

        c_ctrl_sync_cfg_failed = Ctrl("//input[contains(@name, 'Config') and @value='10209']", 'check'),
        c_ctrl_sync_last_cfg = Ctrl("//input[contains(@name, 'Config') and @value='10208']", 'check'),
        c_ctrl_sync_local_cfg = Ctrl("//input[contains(@name, 'Config') and @value='10206']", 'check'),
        c_ctrl_sync_peer_cfg = Ctrl("//input[contains(@name, 'Config') and @value='10207']", 'check'),

        c_ctrl_system_upgraded_failed = Ctrl("//input[contains(@name, 'Config') and @value='10205']", 'check'),
        c_ctrl_system_upgraded_success = Ctrl("//input[contains(@name, 'Config') and @value='10204']", 'check'),
        c_ctrl_upgrade_from_peer = Ctrl("//input[contains(@name, 'Config') and @value='10201']", 'check'),
        c_ctrl_version_mismatched = Ctrl("//input[contains(@name, 'Config') and @value='10211']", 'check'),
        c_mgmt_ip_changed = Ctrl("//input[contains(@name, 'Config') and @value='10130']", 'check'),

        c_sysname_changed = Ctrl("//input[contains(@name, 'Config') and @value='10131']", 'check'),
        c_systime_changed = Ctrl("//input[contains(@name, 'Config') and @value='10229']", 'check'),
        c_wlan_created = Ctrl("//input[contains(@name, 'Config') and @value='10133']", 'check'),
        c_wlan_deleted = Ctrl("//input[contains(@name, 'Config') and @value='10134']", 'check'),
        c_wlan_disabled = Ctrl("//input[contains(@name, 'Config') and @value='10199']", 'check'),
        c_wlan_enabled = Ctrl("//input[contains(@name, 'Config') and @value='10198']", 'check'),
        c_wlan_modified = Ctrl("//input[contains(@name, 'Config') and @value='10132']", 'check'),
    ),
    # locators for Configuration tab
    client = dict(
        cl_admin_del_all_clients = Ctrl("//input[contains(@name, 'Client') and @value='10031']", 'check'),
        cl_batch_dpsk_acquire = Ctrl("//input[contains(@name, 'Client') and @value='10223']", 'check'),
        cl_client_dpsk_expired = Ctrl("//input[contains(@name, 'Client') and @value='10173']", 'check'),
        cl_client_dpsk_renew_done = Ctrl("//input[contains(@name, 'Client') and @value='10174']", 'check'),
        cl_client_auth_fail_block = Ctrl("//input[contains(@name, 'Client') and @value='10167']", 'check'),
        cl_client_auth_failed = Ctrl("//input[contains(@name, 'Client') and @value='10152']", 'check'),
        cl_client_del_by_admin = Ctrl("//input[contains(@name, 'Client') and @value='10157']", 'check'),
        cl_client_disconn_auth_timeout = Ctrl("//input[contains(@name, 'Client') and @value='10159']", 'check'),
        cl_client_disconn_internal_err = Ctrl("//input[contains(@name, 'Client') and @value='10158']", 'check'),

        cl_client_join = Ctrl("//input[contains(@name, 'Client') and @value='10148']", 'check'),
        cl_client_join_failed = Ctrl("//input[contains(@name, 'Client') and @value='10149']", 'check'),
        cl_client_join_failed_ap_busy = Ctrl("//input[contains(@name, 'Client') and @value='10150']", 'check'),
        cl_client_join_rssi_warning = Ctrl("//input[contains(@name, 'Client') and @value='10254']", 'check'),
        cl_client_join_with_vlan = Ctrl("//input[contains(@name, 'Client') and @value='10261']", 'check'),
        cl_client_policy_mismatch = Ctrl("//input[contains(@name, 'Client') and @value='10151']", 'check'),
        cl_client_reconn_within_grace_period = Ctrl("//input[contains(@name, 'Client') and @value='10175']", 'check'),
        cl_client_repeat_auth_fail = Ctrl("//input[contains(@name, 'Client') and @value='10166']", 'check'),
        cl_client_roam_in = Ctrl("//input[contains(@name, 'Client') and @value='10156']", 'check'),
        cl_client_roam_out = Ctrl("//input[contains(@name, 'Client') and @value='10155']", 'check'),

        cl_client_session_expired = Ctrl("//input[contains(@name, 'Client') and @value='10162']", 'check'),
        cl_client_timeout = Ctrl("//input[contains(@name, 'Client') and @value='10153']", 'check'),
        cl_client_too_many_login = Ctrl("//input[contains(@name, 'Client') and @value='10169']", 'check'),
        cl_client_unauthorized = Ctrl("//input[contains(@name, 'Client') and @value='10161']", 'check'),
        cl_client_unblock = Ctrl("//input[contains(@name, 'Client') and @value='10171']", 'check'),
        cl_client_web_auth = Ctrl("//input[contains(@name, 'Client') and @value='10163']", 'check'),
        cl_client_web_not_auth_internal_err = Ctrl("//input[contains(@name, 'Client') and @value='10164']", 'check'),
        cl_client_web_not_auth_no_such_user = Ctrl("//input[contains(@name, 'Client') and @value='10165']", 'check'),

        cl_guest_noauth_ok = Ctrl("//input[contains(@name, 'Client') and @value='10070']", 'check'),
        cl_guest_ok = Ctrl("//input[contains(@name, 'Client') and @value='10069']", 'check'),
        cl_low_signal = Ctrl("//input[contains(@name, 'Client') and @value='10160']", 'check'),
        cl_radius_service_outage = Ctrl("//input[contains(@name, 'Client') and @value='10068']", 'check'),

        cl_user_dpsk_acquire = Ctrl("//input[contains(@name, 'Client') and @value='10172']", 'check'),
        cl_user_auth_conn_err = Ctrl("//input[contains(@name, 'Client') and @value='10067']", 'check'),
        cl_user_login_fail_block = Ctrl("//input[contains(@name, 'Client') and @value='10168']", 'check'),
        cl_user_login_failed_access = Ctrl("//input[contains(@name, 'Client') and @value='10066']", 'check'),
        cl_user_login_failed_for_guestpass = Ctrl("//input[contains(@name, 'Client') and @value='10064']", 'check'),
        cl_user_login_failed_for_prov = Ctrl("//input[contains(@name, 'Client') and @value='10065']", 'check'),
        cl_user_unblock = Ctrl("//input[contains(@name, 'Client') and @value='10170']", 'check'),
    ),
    # locators for Performance (p) tab
    performance = dict(
        p_ap_speedflex_to_ap = Ctrl("//input[contains(@name, 'Performance') and @value='10191']", 'check'),
        p_ap_speedflex_to_ap_downlink = Ctrl("//input[contains(@name, 'Performance') and @value='10192']", 'check'),
        p_ap_speedflex_to_ap_uplink = Ctrl("//input[contains(@name, 'Performance') and @value='10193']", 'check'),
        p_ap_speedflex_to_zd = Ctrl("//input[contains(@name, 'Performance') and @value='10194']", 'check'),
        p_ap_speedflex_to_zd_downlink = Ctrl("//input[contains(@name, 'Performance') and @value='10195']", 'check'),
        p_ap_speedflex_to_zd_uplink = Ctrl("//input[contains(@name, 'Performance') and @value='10196']", 'check'),

        p_admin_speedflex_to_ap = Ctrl("//input[contains(@name, 'Performance') and @value='10058']", 'check'),
        p_admin_speedflex_to_ap_downlink = Ctrl("//input[contains(@name, 'Performance') and @value='10059']", 'check'),
        p_admin_speedflex_to_ap_uplink = Ctrl("//input[contains(@name, 'Performance') and @value='10060']", 'check'),
        p_admin_speedflex_to_zd = Ctrl("//input[contains(@name, 'Performance') and @value='10061']", 'check'),
        p_admin_speedflex_to_zd_downlink = Ctrl("//input[contains(@name, 'Performance') and @value='10062']", 'check'),
        p_admin_speedflex_to_zd_uplink = Ctrl("//input[contains(@name, 'Performance') and @value='10063']", 'check'),
    ),
    # locators for AP Admin (aa) tab
    ap_admin = dict(
        aa_ap_approv_auto = Ctrl("//input[contains(@name, 'APAdmin') and @value='10097']", 'check'),
        aa_ap_approv_pending = Ctrl("//input[contains(@name, 'APAdmin') and @value='10098']", 'check'),
        aa_ap_auth_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10101']", 'check'),
        aa_ap_being_upgraded = Ctrl("//input[contains(@name, 'APAdmin') and @value='10116']", 'check'),

        aa_ap_bkup_img_ugprade_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10124']", 'check'),
        aa_ap_bkup_img_ugprade_failed_ip = Ctrl("//input[contains(@name, 'APAdmin') and @value='10125']", 'check'),
        aa_ap_bkup_img_ugprade_failed_w_err = Ctrl("//input[contains(@name, 'APAdmin') and @value='10126']", 'check'),
        aa_ap_bkup_img_ugprade_success = Ctrl("//input[contains(@name, 'APAdmin') and @value='10122']", 'check'),
        aa_ap_bkup_img_ugprade_success_w_err = Ctrl("//input[contains(@name, 'APAdmin') and @value='10123']", 'check'),

        aa_ap_channel_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10103']", 'check'),
        aa_ap_config_out_of_sysc = Ctrl("//input[contains(@name, 'APAdmin') and @value='10096']", 'check'),
        aa_ap_country_code_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10092']", 'check'),
        aa_ap_dfs_channel_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10105']", 'check'),
        aa_ap_dfs_radar_event = Ctrl("//input[contains(@name, 'APAdmin') and @value='10104']", 'check'),

        aa_ap_gen_rf_info = Ctrl("//input[contains(@name, 'APAdmin') and @value='10128']", 'check'),
        aa_ap_gen_support_txt = Ctrl("//input[contains(@name, 'APAdmin') and @value='10127']", 'check'),
        aa_ap_hardware_problem = Ctrl("//input[contains(@name, 'APAdmin') and @value='10190']", 'check'),

        aa_ap_img_ugprade_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10119']", 'check'),
        aa_ap_img_ugprade_failed_ip = Ctrl("//input[contains(@name, 'APAdmin') and @value='10120']", 'check'),
        aa_ap_img_ugprade_failed_w_err = Ctrl("//input[contains(@name, 'APAdmin') and @value='10121']", 'check'),
        aa_ap_img_ugprade_success = Ctrl("//input[contains(@name, 'APAdmin') and @value='10117']", 'check'),
        aa_ap_img_ugprade_success_w_err = Ctrl("//input[contains(@name, 'APAdmin') and @value='10118']", 'check'),

        aa_ap_incorrect_cfg = Ctrl("//input[contains(@name, 'APAdmin') and @value='10099']", 'check'),
        aa_ap_incorrect_cfg_remove_ap = Ctrl("//input[contains(@name, 'APAdmin') and @value='10100']", 'check'),

        aa_ap_ip_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10094']", 'check'),
        aa_ap_join_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10072']", 'check'),
        aa_ap_join_failed_model = Ctrl("//input[contains(@name, 'APAdmin') and @value='10189']", 'check'),
        aa_ap_join_invalid_country_code = Ctrl("//input[contains(@name, 'APAdmin') and @value='10074']", 'check'),
        aa_ap_join_too_many = Ctrl("//input[contains(@name, 'APAdmin') and @value='10073']", 'check'),
        aa_ap_mgmt_vlan_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10093']", 'check'),
        aa_ap_populate_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10197']", 'check'),

        aa_ap_tx_power_decrease = Ctrl("//input[contains(@name, 'APAdmin') and @value='10106']", 'check'),
        aa_ap_tx_power_increase = Ctrl("//input[contains(@name, 'APAdmin') and @value='10107']", 'check'),

        aa_ap_admin_scan_all = Ctrl("//input[contains(@name, 'APAdmin') and @value='10032']", 'check'),
        aa_ap_channel_compatiblity_change = Ctrl("//input[contains(@name, 'APAdmin') and @value='10259']", 'check'),
        aa_ap_radio_disabled = Ctrl("//input[contains(@name, 'APAdmin') and @value='10260']", 'check'),
        aa_ap_radio_enabled = Ctrl("//input[contains(@name, 'APAdmin') and @value='10257']", 'check'),

        aa_ctrl_standby_disconnected = Ctrl("//input[contains(@name, 'APAdmin') and @value='10222']", 'check'),
        aa_user_login_failed_for_access = Ctrl("//input[contains(@name, 'APAdmin') and @value='10262']", 'check'),

        aa_vap_del = Ctrl("//input[contains(@name, 'APAdmin') and @value='10137']", 'check'),
        aa_vap_del_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10143']", 'check'),
        aa_vap_del_failed_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10147']", 'check'),
        aa_vap_del_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10141']", 'check'),

        aa_vap_init = Ctrl("//input[contains(@name, 'APAdmin') and @value='10136']", 'check'),
        aa_vap_init_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10142']", 'check'),
        aa_vap_init_failed_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10145']", 'check'),
        aa_vap_init_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10139']", 'check'),

        aa_vap_update = Ctrl("//input[contains(@name, 'APAdmin') and @value='10138']", 'check'),
        aa_vap_update_failed = Ctrl("//input[contains(@name, 'APAdmin') and @value='10144']", 'check'),
        aa_vap_update_failed_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10146']", 'check'),
        aa_vap_update_retry = Ctrl("//input[contains(@name, 'APAdmin') and @value='10140']", 'check'),

        aa_wlan_group_switch = Ctrl("//input[contains(@name, 'APAdmin') and @value='10135']", 'check'),
        aa_wlan_disabled_by_schedule = Ctrl("//input[contains(@name, 'APAdmin') and @value='10244']", 'check'),
        aa_wlan_enabled_by_schedule = Ctrl("//input[contains(@name, 'APAdmin') and @value='10240']", 'check'),
    ),
)#End for configurable_event_key_locs

SUB_TABS = ['sys_admin', 'mesh', 'cfg', 'client', 'ap_admin', 'performance']
# Headers for device_tbl
assign_zd_tbl_hdrs = [
    'select', 'name', 'model', 'event_cfg', 'serial', 'ip', 'connection'
]
# Headers for query_result_tbl
zd_query_result_tbl_hdrs = [
    'name', 'ip', 'model', 'serial', 'cfg_name'
]

locators = dict(
    # parent tabs
    event_cfg_tab = "//div/span[contains(., 'Event Configuration')]",
    configured_zds_tab = "//div/span[contains(., 'Configured ZDs')]",
    config_task_log_tab = "//div/span[contains(., 'Config Task Log')]",

    create_event_cfg = Ctrl("//input[@id='createButton']", 'button'),
    #create_event_cfg = "//input[@id='createButton']",
    cfg_name = Ctrl("//input[@dojoattachpoint='eventCfgNameTextField']", 'text'),
    #cfg_name = "//input[@dojoattachpoint='eventCfgNameTextField']",

    # sub tabs of create a new event config
    sys_admin = "//div/span[text()='System Admin']",
    mesh = "//div/span[text()='Mesh']",
    cfg = "//div/span[text()='Configuration']",
    client = "//div/span[text()='Client']",
    ap_admin = "//div/span[text()='AP Admin']",
    performance = "//div/span[text()='Performance']",

    # check box to check all or un-check all
    sa_event_type_chk = "//input[@id='SysAdminSelect_header_Id']",
    m_event_type_chk = "//input[@id='MeshSelect_header_Id']",
    c_event_type_chk = "//input[@id='ConfigSelect_header_Id']",
    cl_event_type_chk = "//input[@id='ClientSelect_header_Id']",
    aa_event_type_chk = "//input[@id='APAdminSelect_header_Id']",
    p_event_type_chk = "//input[@id='PerformanceSelect_header_Id']",

    save_btn = "//input[@value='Save']", # don't use AC lib for this control
    cancel_btn = "//input[@value='Cancel']",
    err_status = "//span[@id='validate-eventCfgName']",
    expand_delete_status = Ctrl("//a[@id='statusMessageLink']", 'button'),
    delete_status_msg = Ctrl("//td[@class='MsgWindowError']", 'html'),

    event_cfg_tbl = Ctrl(
        dict(
             tbl = "//div[@id='eventCfgDiv']//table[@class='tableArea']",
             nav = "//div[@id='eventCfgDiv']//table[@class='pageSelector']",
        ),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            links = dict(
                assign_zds = "//span[.='Assign ZDs']",
                edit = "//span[.='Edit']",
                delete = "//span[.='Delete']",
                copy = "//span[.='Copy']",
            ),
        ),
    ),

    device_tbl = Ctrl(
        dict(
             tbl = "//div[@id='bottomDiv']//table[@class='tableArea']",
             nav = "//div[@id='eventCfgDiv']//table[@class='pageSelector']",
        ),
        type = 'tbl_click',
        cfg = dict(
            hdrs = assign_zd_tbl_hdrs,
            links = dict(
                select = "//input[@type='checkbox']",
            ),
        ),
    ),
    view = Ctrl(
        "//div[@id='bottomDiv']//td[preceding-sibling::td[text()= 'Select a ZD View:']]//span",
        'dojo_select'
    ),

    # Locators for Configured ZDs tab
    query_btn = "//input[@value='Query']",
    query_result_tbl = Ctrl(
        dict(
             tbl = "//div[@id='configZDTopDiv']//table[@class='tableArea']",
             nav = "//div[@id='eventCfgDiv']//table[@class='pageSelector']",
        ),
        type = 'ltable',
        cfg = dict(
            hdrs = zd_query_result_tbl_hdrs,
            links = dict(
                cfg_name = "//span[text()]",
            ),
        ),
    ),
    zd_filter_view = "//div[@id='configZDTopDiv']//td[preceding-sibling::td[text()= 'Select a ZD View:']][%s]",
)

# update locator for locs of configurable and default keys of sub-tabs
for t in SUB_TABS:
    locators.update(default_event_key_locs[t])
    locators.update(configurable_event_key_locs[t])

ctrl_order = '''
'''

def nav_to(fm, tab = TAB_1, force = True):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_ZD_EVENTS_CONFIG, force = force)

    tab_l = {
        TAB_1: locators['event_cfg_tab'],
        TAB_2: locators['configured_zds_tab'],
        TAB_3: locators['config_task_log_tab'],
    }[tab]
    fm.s.click_and_wait(tab_l)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)

def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)

def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)

def _get_tbl(fm, tbl, cfg={}, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)

def _get_save_event_cfg_msg(fm):
    ''''''
    return fm.s.get_text(locators['err_status'])


def _get_delete_status_msg(fm):
    ''''''
    try:
        msg = ac_get(
            fm.s, locators,
            ['expand_delete_status', 'delete_status_msg'],
            ['expand_delete_status', 'delete_status_msg']
        )['delete_status_msg']
    except:# delete successfully
        msg = ''

    return msg


def _un_select_tab_cfg(se, tab):
    '''
    This function is to un tick all check boxes of a tab.
    '''
    tab_l, chk_l = {
        'sys_admin'  : (locators['sys_admin'], locators['sa_event_type_chk']),
        'mesh'       : (locators['mesh'], locators['m_event_type_chk']),
        'cfg'        : (locators['cfg'], locators['c_event_type_chk']),
        'client'     : (locators['client'], locators['cl_event_type_chk']),
        'ap_admin'   : (locators['ap_admin'], locators['aa_event_type_chk']),
        'performance': (locators['performance'], locators['p_event_type_chk']),
    }[tab]
    # click on tab to enter its cfg detail first
    se.click_and_wait(tab_l, 1)
    # Click twice to un-check all cfg items
    se.click_and_wait(chk_l)
    # if the check box is check, click again do un select all. Otherwise, n
    if se.is_checked(chk_l):
        se.click_and_wait(chk_l)


def _un_select_all_event_cfgs(se):
    '''
    Un-select all check boxes of all tabs
    '''
    tabs = ['sys_admin', 'mesh', 'cfg', 'client', 'ap_admin', 'performance']
    for t in tabs: _un_select_tab_cfg(se, t)


def _fill_in_cfg(fm, cfg):
    '''
    to cfg all tabs of event cfg
    cfg = dict(
        sys_admin = dict(dict of cfg items),
        mesh = dict(dict of cfg items),
        cfg = dict(dict of cfg items),
        client = dict(dict of cfg items),
        ap_admin = dict(dict of cfg items),
        performance = dict(dict of cfg items),
    )
    '''
    for t, t_cfg in cfg.items():
        fm.s.click_and_wait(locators[t])
        _set(fm, t_cfg)


def _build_filter_opts(match):
    '''
    to make filter options to do query base on match expression
    '''
    flt_opts = []
    for k, v in match.items():
        try:
            cri = dict(
                ip = ['IP Address', 'Contains', v],
                name = ['ZD Name', 'Contains', v],
                serial = ['Serial Number', 'Exactly equals', v],
                model = ['Model', 'Exactly equals', v],
            )[k]
        except:
            # assign empty list for un-supported query key
            continue
        flt_opts.append(cri)

    return flt_opts


def _select_zd(se,
               ip_list,
               view = 'All ZoneDirectors'
    ):
    '''
    to select zd
    '''
    # cfg to select a zd view and select zds of that view
    cfg = dict(
        view = view,
        device_tbl = dict(
             match = [dict(ip = ip) for ip in ip_list],
             op = 'equal',
             get = '1st',
             link = 'select',
        ),
    )
    ac_set(se, locators, cfg, ['view', 'device_tbl'])


def _query_configured_zd_by_ip(fm,
                              ip,
                              view = 'All ZoneDirectors'
    ):
    '''
    this is a simplified method to do query a configured zd by ip
    '''
    _query_configured_zd(fm, _build_filter_opts(dict(ip=ip)), view)


def _query_configured_zd_by_name(fm,
                                 name,
                                 view = 'All ZoneDirectors'
    ):
    '''
    this is a simplified method to do query a configured zd by ip
    '''
    _query_configured_zd(fm, _build_filter_opts(dict(name=name)), view)


def _query_configured_zd(fm,
                         flt_opts,
                         view = 'All ZoneDirectors'
    ):
    '''
    this is a general method to do query configured zds base on zd view and
    filter options.
    . flt_opts = [
        [criteria 1],
        [criteria 2]
        ....
    ]
    ex:
        [
            ['IP Address', 'Contains', '192.168.30.251'],
            ['ZD Name', 'Contains', 'Ruckus'],
            ['Model', 'Exactly equals', 'ZD1050'],
        ]
    . view: a zd view name to do query
    '''
    # Use report filter to do query ZD device view
    # It's just different from locator for the report option so re-update it
    rf.REPORT_TOP_TMPL = locators['zd_filter_view']
    logging.info(
        'Do query with criteria. (View, filter opts): (%s, %s)' %
        (view, pformat(flt_opts))
    )
    rf.fill_in(fm, [view], flt_opts)

    fm.s.click_and_wait(locators['query_btn'])


def _find_configured_zd(fm,
                        match,
                        view = 'All ZoneDirectors',
                        op = 'in'
    ):
    '''
    this is a general method to find a configured zd. It supports to find
    the zd by all criteria supported on the GUI.

    . match: a combination criteria to do search
             Ex:
                dict(
                    ip = string of IP address,
                    name = string of zd name
                    serial = string of zd serial number,
                    model = string of zd model,
                )
    . view: ZD view to find.
    . op: operator to do search
    '''
    nav_to(fm, TAB_2, True)

    flt_opts = _build_filter_opts(match)
    _query_configured_zd(fm, flt_opts, view)

    return _get_tbl(
        fm, 'query_result_tbl',
        dict(
             match = match,
             op = op,
             get = '1st',
        )
    )


def _get_configured_events(fm, cfg_ks = {}):
    '''
    to get configuration events which are configured for a zd
    . tab:
    . cfg_ks: a dict of keys to get for each sub tab. Empty will get all keys
          of each sub tab.
    Ex: it will look like.
        ks = dict(
            sys_admin   = [list of keys] or {dict of keys} to get,
            mesh        = [list of keys] or {dict of keys} to get,
            cfg         = [list of keys] or {dict of keys} to get,
            client      = [list of keys] or {dict of keys} to get,
            ap_admin    = [list of keys] or {dict of keys} to get,
            performance = [list of keys] or {dict of keys} to get,
        )
    return a dict of configured keys.
    '''
    if not cfg_ks:
        cfg_ks = build_cfg_event_keys(True)

    return _get_sub_tab_cfgs(fm, cfg_ks)


def _get_sub_tab_cfgs(fm, cfg_ks):
    '''
    to get event cfg of all sub-tabs
    return the dict as below
        cfg = dict(
            sys_admin = dict(dict of cfg items),
            mesh = dict(dict of cfg items),
            cfg = dict(dict of cfg items),
            client = dict(dict of cfg items),
            ap_admin = dict(dict of cfg items),
            performance = dict(dict of cfg items),
        )
    '''
    cfg = {}
    for t, ks in cfg_ks.items():
        fm.s.click_and_wait(locators[t])
        cfg[t] = _get(fm, ks)

    return cfg


def build_cfg_event_keys(get_default_cfg_ks = True):
    '''
    to build and return a cfg keys to do get configured events.
    . get_default_cfg_ks: get default keys or not. Default keys are keys which
                          are configurable.
    Return as below:
        dict(
            sys_admin   = [list of keys],
            mesh        = [list of keys],
            cfg         = [list of keys],
            client      = [list of keys],
            ap_admin    = [list of keys],
            performance = [list of keys],
        )
    '''
    cfg = {}
    for t in SUB_TABS:
        cfg[t] = configurable_event_key_locs[t].keys()
        if get_default_cfg_ks:
            cfg[t].extend(default_event_key_locs[t].keys())

    return cfg
#-------------------------------------------------------------------------------
#  PRIVATE METHODS
#-------------------------------------------------------------------------------
