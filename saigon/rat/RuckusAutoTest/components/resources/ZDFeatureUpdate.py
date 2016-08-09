'''
'''
feature_params = {
    # web authentication parameters
    'web_auth_params': {
        'target_url': 'http://172.16.10.252/',
        'login_url': 'https://%s/user/user_login_auth.jsp',
        'user_login_auth': {
            'username':'testuser',
            'password': 'testuser',
            'ok': "Login",
        },
        'activate_url': 'https://%s/user/_allowuser.jsp'
    },

    # guest pass authentication parameters
    'guest_auth_params': {
        'target_url': 'http://172.16.10.252/',
        'redirect_url': '',
        'guest_auth_cfg': {
            'guest_pass': '',
            'use_tou': False,
        },
        'guest_login_url': '%s/user/guest_login.jsp',
        'guest_login': {
            'key': '',
            'ok': 'Login',
         },
         'guest_tou_url': '%s/user/guest_tou.jsp',
         'guest_tou': {
            'ok': 'Accept and Continue',
         },
        'activate_url': '%s/user/_allowguest.jsp',
        'msg_guestpass_is_invalid': 'This is an invalid Guest Pass',
        'msg_guestpass_welcome_page': 'Welcome to the Guest Access login page',
        'msg_guestpass_tou_review': 'Please review the terms of use',
        #@author: li.pingping@odc-ruckuswireless.com 2013.6.9 to fix when guest access authentication does not execute on station.
        'no_auth': False,
        'expected_data': 'It works!',
    },

    # hotspot authentication parameters
    'hotspot_auth_params': {
        'original_url': 'http://172.16.10.252/',
        'redirect_url': '',
        'user_login_auth': {
            'username': 'local.username',
            'password': 'local.password',
         },
         # these 3 params are commented out as they are not tested
         #'pattern_login_page': r"<form action=.?(?P<url>[https]+://[0-9\.]+:[0-9]+)(?P<path>/login).?>",
         #'pattern_redirect_url': r"window.location.href='(.*)';",
         #'pattern_redirect_auth': r"img.src = .?(/_allowuser.jsp.*)\";",
         'expected_data': 'It works!',
    },

    # factory setup params
    'factory_setup_params': {
        'language': 'English',
        'dhcp_enabled': False,
        'system_name': 'ruckus',
        'country_code': 'United States',
        'mesh_enabled': False,
        'wireless1_enabled':True,
        'wireless1_name': 'Ruckus-Wireless-1',
        'authentication_open': True,
        'guest_wlan_enabled': False,
        'guest_wlan_name': 'Ruckus-Guest',
        'admin_name': 'admin',
        'admin_password': 'admin',
        'create_user_account_is_checked': False,
    }

}

# alarmmail.auth for 8.2.0.0, 8.3.1.0, and others
alarmmail_auth = {
    'ip_textbox': r"//input[@id='smtp-server']",
    'port_textbox': r"//input[@id='smtp-port']",
    'user_textbox': r"//input[@id='smtp-user']",
    'pass_textbox': r"//input[@id='smtp-pass']",
    'pass2_textbox': r"//input[@id='smtp-pass2']",
}


feature_update = {
    '9.5.0.0': {
        'info': {
            # Setup wizard
            'loc_wzd_ip_dualmode_radio': r"//input[@id='dualmode']",
            'loc_wzd_ip_v4mode_radio': r"//input[@id='ipv4mode']",
            'loc_wzd_ip_v6mode_radio': r"//input[@id='ipv6mode']",
            'loc_wzd_ip_req_ip_button': r"//input[@id='get-dhcp']",

            'loc_wzd_ip_ipv6_manual_radio': r"//input[@id='manual-ipv6']",
            'loc_wzd_ip_ipv6_autoconfig_radio': r"//input[@id='autoconfig']",
            'loc_wzd_ip_ipv6_req_ip_button': r"//input[@id='get-autoconfig']",
            'loc_wzd_ip_ipv6_addr_textbox': r"//input[@id='ipv6']",
            'loc_wzd_ip_ipv6_prefix_textbox': r"//input[@id='prefixlength']",
            'loc_wzd_ip_ipv6_gateway_textbox': r"//input[@id='gateway-ipv6']",
            'loc_wzd_ip_ipv6_dns1_textbox': r"//input[@id='dns1-ipv6']",
            'loc_wzd_ip_ipv6_dns2_textbox': r"//input[@id='dns2-ipv6']",

            # for mesh table in dash board page
            'loc_dashboard_ap_status_title':r"//table[@id='meshsummary']//td//a[contains(text(), '%s')]/..@title",
            'loc_dashboard_ap_status_img':r"//table[@id='meshsummary']//td//a[contains(text(), '%s')]/../../td//img[2]@src",

            # Roles and Policies
            'loc_cfg_roles_second_row': r"//tr[@idx='1']/td/input[@name='role-select']",

            'loc_cfg_roles_wlans_checkbox':r"//input[@id='rwlans-$_$']",
            'loc_cfg_roles_wlans_label':r"//table[@id='wlans']/tbody/tr[$_$]/td[2]",

            'factory_setup_params': {
                'language': 'English',
                'system_name': 'ruckus',
                'country_code': 'United States',
                'mesh_enabled': False,
                'ip_dualmode': True,
                'dhcp_enabled': True,
                'ipv6_autoconfig': True,
                'wireless1_enabled': True,
                'wireless1_name': 'Ruckus-Wireless-1',
                'authentication_open': True,
                'guest_wlan_enabled': False,
                'admin_name': 'admin',
                'admin_password': 'admin',
                'create_user_account_is_checked': False,
            },

            # web authentication parameters
            'web_auth_params': feature_params['web_auth_params']['user_login_auth'].update({'ok': "Log In"}),
            'web_auth_params': feature_params['web_auth_params'],

            # guest pass authentication parameters
            'guest_auth_params': feature_params['guest_auth_params']['guest_login'].update({'ok': "Log In"}),
            'guest_auth_params': feature_params['guest_auth_params'],
            
            #@author: Jane.Guo @since: 2013-06-07 add hotspot authentication parameters
            'hotspot_auth_params': feature_params['hotspot_auth_params'],
        }
    },
}

# two mainline builds prior to 9.0.0.0 production
# these can be removed any time when we no longer test mainline builds of 9.0
feature_update.update({'9.6.0.0': feature_update['9.5.0.0']})
feature_update.update({'9.7.0.0': feature_update['9.5.0.0']})

if __name__ == "__main__":
    '''
    '''
    from pprint import pprint as pp
    test = feature_update
    pp(test)

