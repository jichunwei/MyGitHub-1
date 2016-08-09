import logging
import re
import time

EXPECTED_INFO = dict(
wlaninfo_v_expected_info = {'vap':'VAP\s*:?=?\s*([\da-fA-F:]{17})',
                            'ap':'AP\s*:?=?\s*([\da-fA-F:]{17})\(([\d.]{7,15})',
                            'ssid':'SSID.*"(.*)"',
                            'auth_server':'auth server\s*:?=?\s*([\d.]{7,15})',
                            'acct_server':'acct server\s*:?=?\s*([\d.]{7,15})',
                            'total_vap':'Total VAP Entries\s*:?=?\s*(\d+)'},
wlaninfo_s_expected_info = {'station':'Station.*([\da-fA-F:]{17})',
                            'ip':'IP\s*:?=?\s*([\d.]{7,15})',
                            'vap':'VAP\s*:?=?\s*([\da-fA-F:]{17})',
                            'total_sta':'Total STA Entries:\s*(\d+)\s*'},
wlaninfo_t_expected_info = {'current_clock':'Current clock ?:?\s*(.*)\r',
                            'total_timer_pops': 'Total timer pops ?:?.*(\d+)',
                            'total_nowait_timers':'Total no-wait timers ?:?.*(\d+)',
                            'total_active_timers':'Active timers ?:?.*(\d+)',
                            'timers': 'Timer\s*(\d+)\s*(.*)\r'},
wlaninfo_c_expected_info = {'model': 'Model\s*=?:?\s*(\S+)',
                            'mac':'ether MAC.*([\da-fA-F:]{17})',
                            'ip': 'IP Addr.* ([\d.]{7,15})',
                            'net_mask':'Netmask.* ([\d.]{7,15}),',
                            'gateway':'Gateway.* ([\d.]{7,15})',
                            'tunnel_mode':'Tunnel Mode\s*:?=?\s*(.*),',
                            'dns1': 'DNS1.* ([\d.]{7,15})',
                            'dns2': 'DNS2.* ([\d.]{7,15})',
                            'management_vlan': 'Management VLAN\s*=?:?\s*(.*),',
                            'mesh_enabled': 'Mesh Enabled.*(true|false)',
                            'mesh_mode': 'Mesh Mode.*(Auto|RAP|MAP)',
                            'version': 'Version\s*:?=?\s*(.*)\r',
                            'state': 'State\s*:?=?\s*(\S*)',
                            'description': 'Description\s*:?=?\s*(\S*)',
                            'country_code': 'Country\s*:?=?\s*(\S+)',
                            'num_radios': 'Num Radios\s*:?=?\s*(\d+)',
                            'radio': 'Radio\s*(\d)+.*type=?:?\s*(\S+)\s*enabled.*(Yes|No)',
                            'total_ap': 'Total Configured AP Entries\s*:?=?\s*(\d+)'},
wlaninfo_w_expected_info = {'wlan_id': 'WLAN ID\s*=?:?\s*(\d+)',
                            'ssid': 'SSID\s*=?:?\s*"(.*)"',
                            'guest_access': 'Guest-WLAN\s*=?:?\s*(Yes|No)',
                            'wispr': 'WISPr-WLAN\s*=?:?\s*(Yes|No)',
                            'num_of_access_policy': 'Access Policy\s*=?:?\s*(\d+)',
                            'web_auth': 'Web Auth\s*=?:?\s*(Yes|No)',
                            'max_clients': 'max clients\s*=?:?\s*(\d+)',
                            'uplink_rate': 'uplink\s*=?:?\s*(\S+)',
                            'downlink_rate': 'downlink\s*=?:?\s*(\S+)',
                            'wep_key_index': 'wep key index\s*=?:?\s*(\d+)',
                            'wep_key_len': 'wep key len\s*=?:?\s*(\d+)',
                            'acl': 'ACL\s*(\d+)\s*\((.*)\)\s*=?:?\s*(.*)\r',
                            'auth_algorithms': 'Auth Algorithms\s*=?:?\s*(.*)\r',
                            'auth_server_type': 'Auth Server Type\s*=?:?\s*(.*)\r',
                            'num_of_vap': 'Num of VAP.*\s*=?:?\s*(\d+)',
                            'vap': 'VAP\s*=?:?\s*([\da-fA-F:]{17}),?\s*number of stations\s*=?:?\s*(\d+)',
                            'total_wlan': ' Total WLAN Entries\s*:?=?\s*(\d+)'},
wlaninfo_r_expected_info = {'rogue_device': 'Rogue Device ([\da-fA-F:]{17}) (.*)    \((.*)\) (.*)\r',
                            'rogue_info': '([\da-fA-F:]{17})\s+([\d\S]+)\s+(\d+)\s+(\d+)\s+(.*)\r',
                            'total_rogue_device': 'Total Rogue Entries\s*:?=?\s*(\d+)'},
wlaninfo_p_expected_info = {'name': 'Access Policy.*\'(.*)\'',
                            'id': 'id\s*=?:?\s*(\d+)',
                            'default_action': 'default action.*(Pass|Block)',
                            'num_of_entries': 'Num of entries\s*=?:?\s*(\d+)',
                            'l2_acl': '([\da-fA-F:]{17})\s+([\da-fA-F:]{17})\s+(\S+)\s+(Pass|Block)',
                            'l3_acl': '([\d.]{7,15}/\d+)\s+([\d.]{7,15}/\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(Pass|Block)'},
wlaninfo_u_expected_info = {'username': 'User\s+(\S+)\r',
                            'id': 'id\s*=?:?\s*(\d+)',
                            'role': 'role\s*=?:?\s*(\d+)',
                            'eap_method': 'EAP methods\s*=?:?\s*(.*),',
                            'num_of_conn': 'num of conn\s*=?:?\s*(\d+)',
                            'password': 'password\s*=?:?\s*(\S+)',
                            'total_user': 'Total User in Database\s*:?=?\s*(\d+)',
                            'user_info': 'User\s+(\S+)\s+id\s*=?:?\s*(\d+)\s*role\s*=?:?\s*(\d+)\s*EAP methods\s*=?:?\s*(.*),\s*num of conn\s*=?:?\s*(\d+)\s+password\s*=?:?\s*(.*)\r'},
wlaninfo_m_expected_info = {'mesh_info': 'Mesh\s*\d\s*"(.*)"',
                            'ap': 'AP\s*=?:?\s*([\da-fA-F:]{17}).*uplink\s*=?:?\s*(\d+).*downlinks\s*=?:?\s*(\d+)',
                            'total_mesh_entry': 'Total Mesh Entries\s*:?=?\s*(\d+)'},
wlaninfo_a_expected_info = {'ap': 'AP\s*([\da-fA-F:]{17})',
                            'ip': 'IP Addr\s*=?:?\s*([\d.]{7,15})',
                            'net_mask':'Netmask\s*=?:?\s*([\d.]{7,15}),',
                            'gateway':'Gateway\s*=?:?\s*([\d.]{7,15})',
                            'dns1': 'DNS1.* ([\d.]{7,15})',
                            'dns2': 'DNS2.* ([\d.]{7,15})',
                            'management_valn_id': 'Management VLAN ID\s*=?:?\s*(\d+)',
                            'model': 'Model\s*=?:?\s*(\S+)',
                            'tunnel_mode':'Tunnel Mode\s*:?=?\s*(.*)\r',
                            'version': 'Version\s*:?=?\s*(.*)\r',
                            'state': 'State\s*:?=?\s*(\S*),?',
                            'classification_status': 'Classification status\s*:?=?\s*(disabled|enabled)',
                            'tx_failure_threshold': 'Tx Failure Threshold\s*:?=?\s*(\d+)',
                            'mesh_enabled': 'mesh_enabled\s*:?=?\s*(Y|N)',
                            'mesh_mode': 'mesh_node_type\s*:?=?\s*(Auto|RAP|MAP)',
                            'country_code': 'Country\s*:?=?\s*(\S+)',
                            'num_radios': 'Num of Radios\s*:?=?\s*(\d+)',
                            'radio': 'Radio\s*(\d)+.*type\s*=?:?\s*(\S+)\s*channel\s*=?:?\s*(\d+)\s*c?\S*n?\s*=?:?\s*(Auto|\d+)\s*enabled.*(Yes|No)\s*Num of clients\s*=?:?\s*(\d+)\s*group_id\s*=?:?\s*(\d+)\s*Number of VAP\s*=?:?\s*(\d+)',
                            'num_of_clients': 'Num of clients\s*=?:?\s*(\d+)',
                            'group_id': 'group_id\s*=?:?\s*(\d+)',
                            'num_of_vap': 'Number of VAP\s*=?:?\s*(\d+)',
                            'total_ap': 'Total Active AP Entries\s*:?=?\s*(\d+)'},
wlaninfo_system_expected_info = {'ip_addr': 'ip_addr\s*=?:?\s*([\d.]{7,15})',
                                 'web_redirect_port': 'web redirect port\s*=?:?\s*(\d+)',
                                 'management_vlan': 'management VLAN\s*=?:?\s*(disabled|enabled),?\s*VLAN ID\s*=?:?\s*(\d+)',
                                 'max_ap_allowed': 'max ap allowed\s*:?=?\s(\d+)',
                                 'max_client_allowed': 'max clients allowed\s*=?:?\s*(\d+)',
                                 'guest_policy': 'guest policy id\s*=?:?\s*(\d+),?\s*(.*)\r',
                                 'ap_policy': 'ap policy\s*:?=?\s*allow all\s*=?:?\s*(true|false),\s*authentication\s*=?:?\s*(\S+)\s+auto psk\s*=?:?\s*(enabled|diabled) global psk\s*=?:?\s*(enabled|disabled)\s*.*\s*connect to primary/secondary ZD.*(enabled|disabled),\s*primary ZD IP\s*=?:?\s*([\d.]{7,15}),\s*secondary ZD IP\s*=?:?\s*([\d.]{7,15})\s*.*\s*management VLAN\s*=?:?(.+),\s*VLAN ID=(\d+)',
                                 'dpsk_expiration_time': 'DPSK e\S+ time\s*=?:?\s*(.+)\r',
                                 'system_wide_acl': 'system wide acl\s*=?:?(.*)\r',
                                 'mesh_id': 'mesh id\s*:?=?\s*(\d+)',
                                 'mesh_enabled': 'mesh enabled.*(Yes|No)',
                                 'bg_scan_interval': 'bg_scan_interval\s*=?:?\s*(.*),',
                                 'bg_scan_channel_win': 'bg_scan_channel_win\s*=?:?\s*(.*)\r',
                                 'active_scan_interval': 'active_scan_interval\s*=?:?\s*(.*),',
                                 'active_scan_channel_win': 'active_scan_channel_win\s*=?:?\s*(.*)\r',
                                 'rogue_reporting': 'rogue reporting.*(enabled|disabled)',
                                 'remote_syslog': 'remote_sys_log\s*(enable|disable)\s*ip\s*=?:?\s*([\d.]{7,15})',
                                 'self_healing': 'self-healing.*(enabled|disabled)',
                                 'auto_tx_power': 'auto tx power.*(enabled|disabled)',
                                 'auto_channel': 'auto channel.*(enabled|disabled)',
                                 'probe_req_rate_limiting': 'rate limiting\s*=?:?\s*(enabled|disabled)',
                                 'auth_fail_tmp_block': 'tmp block.*(enabled|disabled).*block time\s*:?=?(.*)\r',
                                 'mobile_capability': 'mobile_capability\s*=?:?\s*(\S+)',
                                 'ntp_server': 'ntp\s*(enabled|disabled).*server\s*=?:?\s*(.*)\r',
                                 'ap_images': '(\S+)\s*([\d./]+)\s*\(bkup\s*=?:?\s*([\d.]+)\)'},
show_system_expected_info = {'system_name': 'System.*:\s*(.*)\r',
                             'ip': 'IP.*:\s*([\d.]{7,15})/([\d.]{7,15})',
                             'mac': 'MAC.*:\s*([\da-fA-F:]{17})',
                             'model': 'Model.*:\s*(.*)\r',
                             'serial': 'Serial.*:\s*(.*)\r',
                             'version': 'Version.*:\s*(.*)\r',
                             'management_vlan': 'Management.*:\s*(.*)\r',
                             'memory': 'Memory.*:\s*(\d+%)\s*\((.*)\).*(\d+%)\s*\((.*)\)', },
apmgrinfo_a_expected_info = {'ap': 'AP\s*:?=?\s*([\da-fA-F:]{17})\s*/\s*([\d.]{7,15})',
                             'name': 'Name\s*:?=?\s*(\S*)\r',
                             'tunnel_mode': 'Tunnel.*\s+:?=?\s*(\S*)\s*/\s*(\S*)\r',
                             'state': 'State\s*:?=?\s*(\S*)\r',
                             'mesh_role': 'Mesh Role\s*:?=?\s*(\S*)\r',
                             'psk': 'PSK\s*:?=?\s*(\S*)\r',
                             'timer': 'Timer\s*:?=?\s*(.*)\r',
                             'hw_sw_version': 'Version\s*:?=?\s*(\S*)\s*/\s*(\S*)\r',
                             'model_serial': 'Num\s*:?=?\s*(\S*)\s*/\s*(\S*)\r',
                             'zd_found': 'thru\s*:?=?\s*(.*)\r',
                             'total_ap': '(\d+) APs are connected'},
wlaninfo_web_auth_expected_info = {'sta': '([\da-fA-F:]{17})\s*(\d+)\s*(\d+)\s*(\d+/\s*\d+)\s*(.*)\s*(.*)\r?'},
mesh_history_expected_info = {'ap': 'AP\s*([\da-fA-F:]{17})',
                              'scan_by': '([\da-fA-F:]{17})\s+([\da-fA-F:]{17})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)\r'},
wlaninfo_acl_expected_info = {'acl': 'ACL\s*(\d+)\s*\((.*)\)\s*:?=?\s*.*(Denied|Allowed).*(yes|no)'},
wlaninfo_role_expected_info = {'role': 'Role\s*(.*)\r\n\s*id\s*=?:?\s*(\d+)\s*.*(true|false)'},
wlaninfo_mesh_ap_expected_info = {'ap': 'AP\s*([\da-fA-F:]{17}).*uplink\s*=?:?\s*(\d+).*downlinks\s*=?:?\s*(\d+)\r?'},
ping_expected_info = {'ping_statistics': '(\d+) packets transmitted,\s*(\d+) packets received,\s*(\d+)% packet loss'},
wlaninfo_dpsk_expected_info = {'psk': 'PSK\s*(\d+)\s*for\s*(\S*)\((.*)\).*\r\n\s*last rekey\s*(.*)\r\n\s*next rekey\s*(.*)\r?'},
wlaninfo_dcert_expected_info = {'cert': '(\d+)\s+(\S+)\s+(\S*)\s+(\S*)\s+(.*)\r?'},
wlaninfo_auth_expected_info = {'auth_ser': 'Server\s*(\d+)\s*\((.*)\)\s*:?=?\s*(.*\S)\r?'},
wlaninfo_pmk_expected_info = {'pmk': 'Total\s*(\d+)\s*in VAP\s*(.*\S)\r?'},
wlaninfo_wlangroup_expected_info = {'wlangroup': 'group_id\[(\d*)\] *:?=? *(.*)\r'},
wlaninfo_apgroup_expected_info = {'apgroup': 'group_id\[(\d*)\] *:?=? *(.*)\r'},
wlaninfo_disc_ap_expected_info = {'ap': 'Model\s*=?:?\s*(.*)\r\n\s*ether MAC\s*:?=?\s*([\da-fA-F:]{17}).*IP Addr\s*:?=?\s*([\d.]{7,15})\r',
                                  'total_disc_ap': 'Total Disconnected AP Entries\s*:?=?\s*(\d+)\s*\*'},
show_ap_expected_info = {'ap':'([\d.]{7,15})\s+([\da-fA-F:]{17})\s+(\S*)\s+(\S*)\s+(\S*)\s+(\d*).*\r',
                         'total_ap':'Total.*:\s*(\d+)\s*'},
show_station_expected_info = {'sta':'\n(\S*)\s+([\d.]{7,15})\s+([\da-fA-F:]{17})\s+(\S*)\s+(\d+)\s+([\da-fA-F:]{17})\r',
                              'total_sta':'Total.*:\s*(\d+)\s*'},
)

def get_expected_info_from_command(zd_cli, command, expected_values = {}, is_shell_cmd = True, timeout = 10):
    result = {}
    if is_shell_cmd:
        raw_info = zd_cli.do_shell_cmd(command, timeout)
    else:
        raw_info = zd_cli.do_cmd(command, timeout = timeout)
    result = {'raw_info': raw_info}

    for key in expected_values.keys():
        result[key] = get_info_by_key(expected_values[key], raw_info)

    return result

def get_info_by_key(pattern, raw_info):
    result = re.findall(pattern, raw_info)
    if not result:
        result = 'The information is not existed or NULL'

    return result

def get_wlaninfo_v(zd_cli, command = 'wlaninfo -V'):
    """
    Supporting for the command:
        wlaninfo -V: show all VAP
        wlaninfo -v vap_mac -l7: show a specific vap
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_v_expected_info'])
    return result

def get_wlaninfo_s(zd_cli, command = 'wlaninfo -S'):
    """
    Supporting for command:
        wlaninfo -S: show all station
        wlaninfo -s sta_mac -l7: show an specific station
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_s_expected_info'])
    return result

def get_wlaninfo_t(zd_cli, command = 'wlaninfo -T'):
    """
    Supporting for command:
        wlaninfo -T: show all timer
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_t_expected_info'])
    return result

def get_wlaninfo_c(zd_cli, command = 'wlaninfo -C'):
    """
    Supporting for command:
        wlaninfo -C: show all configured AP
        wlaninfo -c ap_mac -l7: show a specific configured AP
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_c_expected_info'])
    return result

def get_wlaninfo_w(zd_cli, command = 'wlaninfo -W'):
    """
    Supporting for the command:
        wlaninfo -W: show all WLAN
        wlaninfo -w wlan_name: show a specific WLAN
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_w_expected_info'])
    return result

def get_wlaninfo_r(zd_cli, command = 'wlaninfo -R'):
    """
    Supporting for the command:
        wlaninfo -R: show all rogue devices
        wlaninfo -r rogue_mac: show a specific rogue device
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_r_expected_info'])
    return result

def get_wlaninfo_p(zd_cli, command = 'wlaninfo -P'):
    """
    Supporting for the command:
        wlaninfo -P: show all access policies
        wlaninfo -p policy_name: show a specific access policy

    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_p_expected_info'])
    return result

def get_wlaninfo_u(zd_cli, command = 'wlaninfo -U'):
    """
    Supporting for the command:
        wlaninfo -P: show all users
        wlaninfo -p user_name -l7: show a specific user
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_u_expected_info'])
    return result

def get_wlaninfo_m(zd_cli, command = 'wlaninfo -M'):
    """
    Supporting for the command:
        wlaninfo -M: show all Mesh entries
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_m_expected_info'])
    return result

def get_wlaninfo_a(zd_cli, command = 'wlaninfo -A'):
    """
    Supporting for the command:
        wlaninfo -A: show all active APs
        wlaninfo -a ap_mac: show a specific AP
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_a_expected_info'])
    return result

def get_wlaninfo_system(zd_cli, command = 'wlaninfo --system'):
    """
    Supporting for the command:
        wlaninfo --system: show system parameters
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_system_expected_info'])
    return result

def get_show_system(zd_cli, command = 'show system'):
    """
    Supporting for the command:
        show system: show system information
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['show_system_expected_info'])
    return result

def get_apmgrinfo_a(zd_cli, command = 'apmgrinfo -a'):
    """
    Supporting for the command:
        apmgrinfo -a: display APs info
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['apmgrinfo_a_expected_info'])
    return result

def get_wlaninfo_web_auth(zd_cli, command = 'wlaninfo --web-auth'):
    """
    Supporting for the command:
        apmgrinfo --web-auth: display all authenthorized clients
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_web_auth_expected_info'])
    return result

def get_wlaninfo_mesh_history(zd_cli, command = 'wlaninfo --mesh-history'):
    """
    Supporting for the command:
        wlaninfo --mesh-history: show mesh history information
    """
    result = get_expected_info_from_command(zd_cli, command)
    raw_data = result['raw_info'].split('\r\n\r\n')

    for data in raw_data:
        if 'AP' in data:
            info = {}
            for key in EXPECTED_INFO['mesh_history_expected_info']:
                info[key] = get_info_by_key(EXPECTED_INFO['mesh_history_expected_info'][key], data)
            result[info['ap'][0]] = info['scan_by']
    return result

def get_wlaninfo_mesh_ap(zd_cli, command = 'wlaninfo --all-mesh-ap'):
    """
    Supporting for the command:
        wlaninfo --all-mesh-ap: show all mesh ap
        wlaninfo --mesh-ap ap_mac: show a specific mesh ap
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_mesh_ap_expected_info'])
    return result

def get_wlaninfo_acl(zd_cli, command = 'wlaninfo --all-acl'):
    """
    Supporting for the command:
        wlaninfo --acl acl_id: show a specific l2 acl
        wlaninfo --all-acl: show all l2 acl
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_acl_expected_info'])
    return result

def get_wlaninfo_role(zd_cli, command = 'wlaninfo --all-role'):
    """
    Supporting for the command:
        wlaninfo --all-role: show all role
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_role_expected_info'])
    return result

def ping(zd_cli, dest_ip):
    """
    Supporting for the command:
        ping: ping to an ip address
    """
    result = get_expected_info_from_command(zd_cli, 'ping %s' % dest_ip, EXPECTED_INFO['ping_expected_info'], is_shell_cmd = False)
    return result

def get_wlaninfo_dpsk(zd_cli, command = 'wlaninfo --all-dpsk'):
    """
    Supporting for the command:
        wlaninfo --all-dpsk: show all dynamic psk
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_dpsk_expected_info'])
    return result

def get_wlaninfo_dcert(zd_cli, command = 'wlaninfo --dcert'):
    """
    Supporting for the command:
        wlaninfo --dcert: show all dynamic certificate
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_dcert_expected_info'])
    return result

def get_wlaninfo_auth(zd_cli, command = 'wlaninfo --all-auth'):
    """
    Supporting for the command:
        wlaninfo --all-auth: show all authentication server
        wlaninfo --auth ser_id: show a specific authentication server
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_auth_expected_info'])
    return result

def get_wlaninfo_pmk(zd_cli, command = 'wlaninfo --pmk-cache'):
    """
    Supporting for the command:
        wlaninfo --pmk-cache: show all pmk cache
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_pmk_expected_info'])
    return result

def get_wlaninfo_wlangroup(zd_cli, command = 'wlaninfo --all-wlangroup'):
    """
    Supporting for the command:
        wlaninfo --all-wlangroup: show all pmk cache
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_wlangroup_expected_info'])
    return result

def get_wlaninfo_apgroup(zd_cli, command = 'wlaninfo --all-apgroup'):
    """
    Supporting for the command:
        wlaninfo --all-apgroup: show all pmk cache
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_apgroup_expected_info'])
    return result

def get_wlaninfo_disc_ap(zd_cli, command = 'wlaninfo --all-disc-ap'):
    """
    Supporting for the command:
        wlaninfo --all-disc-ap: show all pmk cache
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['wlaninfo_disc_ap_expected_info'])
    return result

def get_show_ap(zd_cli, command = 'show ap'):
    """
    Supporting for the command:
        show ap: show all active APs
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['show_ap_expected_info'])
    return result

def get_show_station(zd_cli, command = 'show station'):
    """
    Supporting for the command:
        show ap: show all active APs
    """
    result = get_expected_info_from_command(zd_cli, command, EXPECTED_INFO['show_station_expected_info'])
    return result

