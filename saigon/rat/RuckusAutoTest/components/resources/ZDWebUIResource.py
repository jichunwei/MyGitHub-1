Locators = {
    # Login & Logout
    'LoginUsernameTxt':r"//input[@id='username']",
    'LoginPasswordTxt':r"//input[@name='password']",
    'LoginBtn':r"//input[@name='ok']",
    'LogoutBtn':r"//a[@href='login.jsp?logout=1']",
    'loc_login_failed_div':r"//div[@id='loginfailed']", # TODO: check this! -> phannt: confirmed OK.

    # General Information
    'const_auth_method_open':r"open",
    'const_auth_method_shared':r"shared",
    'const_auth_method_eap':r"EAP",
    'const_encryption_method_none':r"none",
    'const_encryption_method_wpa':r"WPA",
    'const_encryption_method_wpa2':r"WPA2",
    'const_encryption_method_wep64':r"WEP-64",
    'const_encryption_method_wep128':r"WEP-128",
    'const_algorithm_tkip':r"TKIP",
    'const_algorithm_aes':r"AES",
    'const_wep_index1':1,
    'const_wep_index2':2,
    'const_wep_index3':3,
    'const_wep_index4':4,

    # Setup wizard
    'loc_wzd_next_button':r"//input[@id='next']",
    'loc_wzd_finish_button':r"//input[@id='finish']",
    'loc_wzd_language_option':r"//select[@id='locale']",
    'loc_wzd_system_name_textbox':r"//input[@id='sysname']",
    'loc_wzd_country_code_option':r"//select[@id='countrycode']",
    'loc_wzd_mesh_checkbox':r"//input[@id='do-mesh']",
    'loc_wzd_mesh_name_textbox':r"//input[@id='mesh-name']",
    'loc_wzd_mesh_passphrase_textbox':r"//input[@id='mesh-psk']",
    'loc_wzd_ip_manual_radio':r"//input[@id='manual']",
    'loc_wzd_ip_dhcp_radio':r"//input[@id='dhcp']",
    'loc_wzd_ip_addr_textbox':r"//input[@id='ip']",
    'loc_wzd_ip_net_mask_textbox':r"//input[@id='netmask']",
    'loc_wzd_ip_gateway_textbox':r"//input[@id='gateway']",
    'loc_wzd_ip_dns1_textbox':r"//input[@id='dns1']",
    'loc_wzd_ip_dns2_textbox':r"//input[@id='dns2']",
    'loc_wzd_1st_wlan_checkbox':r"//input[@id='do-corp']",
    'loc_wzd_1st_wlan_name':r"//input[@id='name-corp']",
    'loc_wzd_1st_wlan_open_auth_radio':r"//input[@id='do-open']",
    'loc_wzd_1st_wlan_wpapsk_auth_radio':r"//input[@id='do-psk']",
    'loc_wzd_guest_wlan_checkbox':r"//input[@id='do-guest']",
    'loc_wzd_guest_wlan_name_textbox':r"//input[@id='name-guest']",
    'loc_wzd_admin_name_textbox':r"//input[@id='admin-name']",
    'loc_wzd_admin_password1_textbox':r"//input[@id='admin-pass1']",
    'loc_wzd_admin_password2_textbox':r"//input[@id='admin-pass2']",
    'loc_wzd_create_user_checkbox':r"//input[@id='do-users']",
    'loc_wzd_user_name_textbox':r"//input[@id='user-name']",
    'loc_wzd_user_password1_textbox':r"//input[@id='user-pass1']",
    'loc_wzd_user_password2_textbox':r"//input[@id='user-pass2']",
    'loc_wzd_service_term_ckbox':r"//input[@id='agree']",
    # Login
    'loc_login_username_textbox':r"//input[@id='username']",
    'loc_login_password_textbox':r"//input[@name='password']",
    'loc_login_ok_button':r"//input[@name='ok']",
    'loc_login_failed_div':r"//div[@id='loginfailed']",

    # Logout
    'loc_logout_anchor':r"//a[@href='login.jsp?logout=1']",

    # Dashboard
    'loc_dashboard_anchor':r"//a[@href='dashboard.jsp']",

    'loc_dashboard_sysinfo_name_cell':r"//td[@id='sysname']",
    'loc_dashboard_sysinfo_ip_cell':r"//td[@id='sysip']",
    'loc_dashboard_sysinfo_serial_cell':r"//td[@id='sysserial']",
    'loc_dashboard_sysinfo_mac_cell':r"//td[@id='sysmac']",
    
    'loc_dashboard_add_widgets':r"//div[@id='content']//a[@id='showhide']",
    'loc_dashboard_finish_add_widgets':r"//div[@id='content']//td[@id='portlet-depot2']//a[@id='close-depot']",
    'loc_dashboard_portlet':r"//td[@id='portlet-depot']//img[@title='%s']",
    
    'loc_dashboard_column1_top':r"//div[@id='workarea']//td[@id='column1']/div[1]",
    'loc_dashboard_column2_top':r"//div[@id='workarea']//td[@id='column2']/div[1]",
    
    'loc_dashboard_meshsummary_table':r"//table[@id='meshsummary']",
    'loc_dashboard_meshsummary_nav':r"//table[@id='meshsummary']/tfoot",
    'loc_dashboard_ap_status_title':r"//table[@id='meshsummary']//tr[@key-value='%s']//a/..@title",
    'loc_dashboard_ap_status_img':r"//table[@id='meshsummary']//tr[@key-value='%s']//td[1]//img[2]@src",

    # Monitor
    'loc_monitor_anchor':r"//a[@href='monitor.jsp']",

    # Monitor -> Access Points
    'loc_mon_access_points_span':r"//span[@id='monitor_aps']",
    'loc_mon_access_points_total_number_span':r"//table[@id='apsummary']/tfoot/tr/td/div/span",    
    'loc_mon_access_points_export_csv_button':r"//input[@id='exp-cvs']",
    'loc_mon_access_points_search_text':r"//table[@id='apsummary']/tfoot//input[@type='text']",
    
    'loc_mon_access_points_edit_column_button':r"//input[@id='coledit-apsummary' and contains(@value, 'Edit Columns')]",
    'loc_mon_access_points_done_column_button':r"//input[@id='coledit-apsummary' and contains(@value, 'Done')]",
    'loc_mon_access_points_edit_column_mac_del':r"//img[@id='apsummarymac' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_device_name_del':r"//img[@id='apsummarydevname' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_description_del':r"//img[@id='apsummarydescription' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_location_del':r"//img[@id='apsummarylocation' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_model_del':r"//img[@id='apsummarymodel' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_state_del':r"//img[@id='apsummarystate' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_mesh_mode_del':r"//img[@id='apsummarymesh-mode' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_ip_del':r"//img[@id='apsummaryip' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_ext_ip_port_del':r"//img[@id='apsummaryExtIpPort' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_vlan_del':r"//img[@id='apsummarymgmt-vlan-id' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_channel_del':r"//img[@id='apsummaryradio-channel' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_clients_del':r"//img[@id='apsummaryassoc-stas' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_bonjour_del':r"//img[@id='apsummarybonjour-check' and contains(@title, 'Delete')]",
    'loc_mon_access_points_edit_column_application_del':r"//img[@id='apsummaryapp-reg' and contains(@title, 'Delete')]",

    'loc_mon_access_points_edit_column_mac_add':r"//img[@id='apsummarymac' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_device_name_add':r"//img[@id='apsummarydevname' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_description_add':r"//img[@id='apsummarydescription' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_location_add':r"//img[@id='apsummarylocation' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_model_add':r"//img[@id='apsummarymodel' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_state_add':r"//img[@id='apsummarystate' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_mesh_mode_add':r"//img[@id='apsummarymesh-mode' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_ip_add':r"//img[@id='apsummaryip' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_ext_ip_port_add':r"//img[@id='apsummaryExtIpPort' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_vlan_add':r"//img[@id='apsummarymgmt-vlan-id' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_channel_add':r"//img[@id='apsummaryradio-channel' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_clients_add':r"//img[@id='apsummaryassoc-stas' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_bonjour_add':r"//img[@id='apsummarybonjour-check' and contains(@title, 'Add')]",
    'loc_mon_access_points_edit_column_application_add':r"//img[@id='apsummaryapp-reg' and contains(@title, 'Add')]", 
    
    
    'loc_mon_apdetail_general_desc_cell':r"//table/caption[text()='General']/..//td[@id='description']",
    'loc_mon_apdetail_general_mac_cell':r"//table/caption[text()='General']/..//td[@id='mac']",
    'loc_mon_apdetail_general_ip_cell':r"//table/caption[text()='General']/..//td[@id='ip']",
    'loc_mon_apdetail_general_model_cell':r"//table/caption[text()='General']/..//td[@id='model']",
    'loc_mon_apdetail_general_serial_number_cell':r"//table/caption[text()='General']/..//td[@id='serial-number']",
    'loc_mon_apdetail_general_firmware_version_cell':r"//table/caption[text()='General']/..//td[@id='firmware-version']",

    'loc_mon_apdetail_info_status_cell':r"//table/caption[text()='Info']/..//td[@id='status']",
    'loc_mon_apdetail_info_uptime_cell':r"//table/caption[text()='Info']/..//td[@id='uptime']",
    'loc_mon_apdetail_info_tunnel_mode_cell':r"//table/caption[text()='Info']/..//td[@id='tunnel-mode']",
    'loc_mon_apdetail_info_num_sta_cell':r"//table/caption[text()='Info']/..//td[@id='num-sta']",

    'loc_mon_apdetail_wlans_name_cell':r"//table/caption[text()='WLANs']/..//tr[@idx='$_$']/td[1]",
    'loc_mon_apdetail_wlans_bssid_cell':r"//table/caption[text()='WLANs']/..//tr[@idx='$_$']/td[2]",
    'loc_mon_apdetail_wlans_radio_cell':r"//table/caption[text()='WLANs']/..//tr[@idx='$_$']/td[3]",

    'loc_mon_apdetail_radio_channel_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'channel-11')]",
    'loc_mon_apdetail_radio_channelization_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'channelization-11')]",
    'loc_mon_apdetail_radio_txpower_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'tx-power-11')]",
    'loc_mon_apdetail_radio_num_sta_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'num-sta-11')]",
    'loc_mon_apdetail_radio_rssi_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'rssi-11')]",
    'loc_mon_apdetail_radio_retries_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'retries-11')]",
    'loc_mon_apdetail_radio_mcast_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'mcast-11')]",
    'loc_mon_apdetail_radio_rx_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'rx-11')]",
    'loc_mon_apdetail_radio_tx_cell':r"//table[contains(caption, 'Radio 802.11')]//td[contains(@id,'tx-11')]",

    'loc_mon_apdetail_neighbor_mac_cell':r"//table[@id='neighbors']/..//tr[@idx='$_$']/td[1]",
    'loc_mon_apdetail_neighbor_channel_cell':r"//table[@id='neighbors']//..//tr[@idx='$_$']/td[2]",
    'loc_mon_apdetail_neighbor_rssi_cell':r"//table[@id='neighbors']/..//tr[@idx='$_$']/td[3]",
    'loc_mon_apdetail_neighbor_uplinkrc_cell':r"//table[@id='neighbors']/..//tr[@idx='$_$']/td[4]",

    'loc_mon_apdetail_uplink_ap_cell':r"//table[@id='uplink']/..//td[@id='uplink-ap']",
    'loc_mon_apdetail_uplink_assoc_cell':r"//table[@id='uplink']/..//td[@id='uplink-assoc']",
    'loc_mon_apdetail_uplink_rssi_cell':r"//table[@id='uplink']/..//td[@id='uplink-rssi']",
    'loc_mon_apdetail_uplink_rx_cell':r"//table[@id='uplink']/..//td[@id='uplink-rx']",
    'loc_mon_apdetail_uplink_tx_cell':r"//table[@id='uplink']/..//td[@id='uplink-tx']",
    'loc_mon_apdetail_uplink_retries_cell':r"//table[@id='uplink']/..//td[@id='uplink-retries']",

    'loc_mon_apdetail_downlink_ap_cell':r"//table[@id='downlinks']/tbody/tr[@idx='$_$']/td[1]",
    'loc_mon_apdetail_downlink_assoc_cell':r"//table[@id='downlinks']/..//tr[@idx='$_$']/td[2]",
    'loc_mon_apdetail_downlink_rssi_cell':r"//table[@id='downlinks']/..//tr[@idx='$_$']/td[3]",
    'loc_mon_apdetail_downlink_rx_cell':r"//table[@id='downlinks']/..//tr[@idx='$_$']/td[4]",
    'loc_mon_apdetail_downlink_tx_cell':r"//table[@id='downlinks']/..//tr[@idx='$_$']/td[5]",

    'const_mon_apsummary_table_size':15,

    # Monitor -> Map View
    'loc_mon_map_view_span':r"//span[@id='monitor_map']",

    # Monitor -> WLANs
    'loc_mon_wlan_span':r"//span[@id='monitor_wlans']",
    'loc_mon_wlan_name_cell':r"//table[@id='wlansummary']//tr[@idx='$_$']/td[1]",

    # Monitor -> Currently Active Clients
    'loc_mon_currently_active_clients_span':r"//span[@id='monitor_clients']",

    'loc_mon_clients_refresh_image':r"//img[@id='refresh-clients']",
    'loc_mon_clients_total_number_span':r"//table[@id='clients']//div[@class='actions']/span",
    'loc_mon_clients_delete_span':r"//img[@id='delete-clients-$_$']",
    'loc_mon_clients_block_span':r"//img[@id='block-clients-$_$']",
    'loc_mon_clients_search_textbox':r"//table[@id='clients']//span[@class='other-act']/input",

    # Monitor -> Active Wired Clients
    'loc_mon_currently_active_wired_clients_span' : r"//span[@id='monitor_wireclients']",
    
    'loc_mon_wired_clients_refresh_image':r"//img[@id='refresh-wireclient']",
    'loc_mon_wired_clients_total_number_span':r"//table[@id='wireclient']//div[@class='actions']/span",
    'loc_mon_wired_clients_delete_span':r"//img[@id='delete-wireclient-$_$']",
    'loc_mon_wired_clients_search_textbox':r"//table[@id='wireclient']//span[@class='other-act']/input",

    
    # Monitor -> Generate PSK/Certs
    'loc_mon_generated_psk_certs_span':r"//span[@id='monitor_generated']",

    'loc_mon_total_generated_psk_span':r"//table[@id='dpsk']//div[@class='actions']/span",
    'loc_mon_generated_psk_user_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[2]",
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8
    'loc_mon_generated_psk_mac_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[4]",
    'loc_mon_generated_psk_show_more_button': "//input[@id='showmore-dpsk']",    
    #JLIN@20090829 modified 8.2 add wlans column in monitor generate PSK/Certs
    'loc_mon_generated_psk_wlans_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[5]",
    #'loc_mon_generated_psk_created_time_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[5]",
    #'loc_mon_generated_psk_expired_time_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[6]",
    'loc_mon_generated_psk_next_dpsk_image':r"//img[@id='next-dpsk']",
    'loc_mon_generated_psk_all_checkbox':r"//input[@id='dpsk-sall']",
    'loc_mon_generated_psk_delete_button':r"//input[@id='del-dpsk']",
    #Updated by cwang@20130529, supported 9.5
    #'loc_mon_generated_psk_vlan_id': '',
    'loc_mon_generated_psk_vlan_id':r"//table[@id='dpsk']//tr[@idx='$_$']/td[6]",
    'loc_mon_generated_psk_created_time_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[7]",
    'loc_mon_generated_psk_expired_time_cell':r"//table[@id='dpsk']//tr[@idx='$_$']/td[8]",
    #PHANNT@20091019 added 'Clear All' button
    'loc_mon_generated_psk_delall_button':r"//input[@id='delall-dpsk']",

    'loc_mon_total_generated_certs_span':r"//table[@id='dcert']//div[@class='actions']/span",
    'loc_mon_generated_certs_all_checkbox':r"//input[@id='dcert-sall']",
    'loc_mon_generated_certs_delete_button':r"//input[@id='del-dcert']",

    'const_mon_generated_psk_table_size':15,
    'const_mon_generated_cert_table_size':15,

    # Monitor -> Generated Guest Passes
    'loc_mon_generated_guestpasses_span':r"//span[@id='monitor_guests']",

    'loc_mon_total_guestpasses_span':r"//table[@id='guest']//div[@class='actions']/span",
    'loc_mon_guestpass_guestname_cell':r"//table[@id='guest']//tr[$_$]/td[2]",
    'loc_mon_guestpass_remarks_cell':r"//table[@id='guest']//tr[$_$]/td[3]",
    'loc_mon_guestpass_expiredtime_cell':r"//table[@id='guest']//tr[$_$]/td[4]",
    'loc_mon_guestpass_user_cell':r"//table[@id='guest']//tr[$_$]/td[5]",
    'loc_mon_guestpass_nextguest_image':r"//img[@id='next-guest']",
    'loc_mon_guestpass_guestall_checkbox':r"//input[@id='guest-sall']",
    'loc_mon_guestpass_guestdel_button':r"//input[@id='del-guest']",
    #PHANNT@20091019 added 'Clear All' button
    'loc_mon_guestpass_guestdelall_button':r"//input[@id='delall-guest']",

    'const_mon_max_generated_guestpass_rows':15,

    # Monitor -> Rogue Devices
    'loc_mon_rogue_devices_span':r"//span[@id='monitor_rogues']",

    'loc_mon_roguedevices_action_cell':r"//span[@id='recognize-roguesummary-0']",
    'loc_mon_roguedevices_knownrogue_all_checkbox':r"//input[@id='knownrogue-sall']",
    'loc_mon_roguedevices_knownrogue_delete_button':r"//input[@id='del-knownrogue']",
    'loc_mon_total_rogue_devices_span':r"//table[@id='roguesummary']//div[@class='actions']/span",
    'loc_mon_total_known_rogue_devices_span':r"//table[@id='knownrogue']//div[@class='actions']/span",

    # Monitor -> All Events/Activities
    'loc_mon_all_events_activities_span':r"//span[@id='monitor_events']",

    'loc_mon_allevents_clear_all_button':r"//div[@class='actions']//input[@id='clearall-allevent']",
    'loc_mon_allevents_total_number_span':r"//div[@class='actions']//span",
    #cwang@2010-11-1, behavior change, span tag --> select tag
    'loc_mon_allevents_number_select_option':r"//div[@class='actions']//select/option[%s]",
    'loc_mon_allevents_number_select':r"//div[@class='actions']//select",
    
    'loc_mon_allevents_total_number_span':r"//div[@class='actions']//span",
    'loc_mon_allevents_time_cell':r"//table[@id='allevent']//tr[@idx='$_$']/td[1]",
    'loc_mon_allevents_severity_cell':r"//table[@id='allevent']//tr[@idx='$_$']/td[2]",
    'loc_mon_allevents_user_cell':r"//table[@id='allevent']//tr[@idx='$_$']/td[3]",
    'loc_mon_allevents_activities_cell':r"//table[@id='allevent']//tr[@idx='$_$']/td[4]",
    'loc_mon_allevents_next_img':r"//img[@id='next-allevent']",

    # Monitor -> All Alarms
    'loc_mon_all_alarms_span':r"//span[@id='monitor_alarms']",

    'loc_mon_total_alarms_span':r"//div[@class='actions']/span",
    'loc_mon_alarms_clearall_button':r"//input[@id='del-all-alarms']",
    'loc_mon_alarms_datetime_cell':r"//table[@id='alarm']//tr[@idx='$_$']/td[1]",
    'loc_mon_alarms_name_cell':r"//table[@id='alarm']//tr[@idx='$_$']/td[2]",
    'loc_mon_alarms_severity_cell':r"//table[@id='alarm']//tr[@idx='$_$']/td[3]",
    'loc_mon_alarms_activities_cell':r"//table[@id='alarm']//tr[@idx='$_$']/td[4]",
    'loc_mon_alarms_action_cell':r"//table[@id='alarm']//tr[@idx='$_$']/td[5]",
    #'loc_mon_alarms_search_box':r"//div[5]//span[@class='other-act']//input[@type='text']",
    #@author: lipingping; @bug: ZF-8397; @since: 2014-6-11
    'loc_mon_alarms_search_box':r"//div[@id='portlet-alarm']//span[@class='other-act']//input[@type='text']",

    # Monitor -> System Info
    'loc_mon_system_info_span':r"//span[@id='monitor_system']",
    # Monitor -> Real Time Monitoring
    'loc_mon_real_time_monitor':r"//span[@id='monitor_realtime']",
    
    'loc_mon_start_monitoring_button':r"//input[@value='Start Monitoring']",
    'loc_mon_stop_monitoring_button':r"//input[@value='Stop Monitoring']",

    # Configure
    'loc_configure_anchor':r"//a[@href='configure.jsp']",

    # Configure -> System
    'loc_cfg_system_span':r"//span[@id='configure_system']",

    'loc_cfg_system_time_ntp_checkbox':r"//input[@id='ntp']",
    'loc_cfg_system_time_ntp_textbox':r"//input[@id='ntp1']",
    'loc_cfg_system_time_apply_button':r"//input[@id='apply-time']",
    'loc_cfg_system_time_refresh_button':r"//form[@id='form-time']//input[@value='Refresh']",
    'loc_cfg_system_time_curtime_textbox':r"//span[@id='localTime']",
    'loc_cfg_system_time_sync_button':r"//div[@class='actions']//input[@value='Sync Time with Your PC']",

    'loc_cfg_system_syslog_enable_checkbox':r"//input[@id='enable-remote-log']",
    'loc_cfg_system_syslog_server_textbox':r"//input[@id='remote-log-server']",
    'loc_cfg_system_syslog_apply_button':r"//input[@id='apply-log']",
    'loc_cfg_system_syslog_high_radio':r"//input[@id='high']",
    'loc_cfg_system_syslog_medium_radio':r"//input[@id='medium']",
    'loc_cfg_system_syslog_low_radio':r"//input[@id='low']",

    'loc_cfg_system_name_textbox':r"//input[@id='sysname']",
    'loc_cfg_system_name_apply_button':r"//input[@id='apply-identity']",

    'loc_cfg_system_ip_addr_textbox':r"//input[@id='ip']",
    'loc_cfg_system_net_mask_textbox':r"//input[@id='netmask']",
    'loc_cfg_system_gateway_textbox':r"//input[@id='gateway']",
    'loc_cfg_system_pri_dns_textbox':r"//input[@id='dns1']",
    'loc_cfg_system_sec_dns_textbox':r"//input[@id='dns2']",
    'loc_cfg_system_mgt_ip_apply_button':r"//input[@id='apply-mgmt-ip']",
    'loc_cfg_system_ip_manual_radio':r"//input[@id='manual']",
    'loc_cfg_system_ip_dhcp_radio':r"//input[@id='dhcp']",

    'loc_cfg_system_dhcps_fieldset':r"//*[@id='fieldset-dhcps']",
    'loc_cfg_system_dhcps_enable_checkbox':r"//input[@id='dhcps']",
    'loc_cfg_system_dhcps_starting_ip_textbox':r"//input[@id='dhcps-ip']",
    'loc_cfg_system_dhcps_number_ip_textbox':r"//input[@id='dhcps-range']",
    'loc_cfg_system_dhcps_leasetime_options':r"//select[@id='dhcps-leasetime']",
    'loc_cfg_system_dhcps_assigned_showlink':r"//*[@id='show-dhcps-lease']",
    'loc_cfg_system_dhcps_assigned_table':r"//table[@id='dhcps-lease']",
    'loc_cfg_system_dhcps_search_textbox':r"//table[@id='dhcps-lease']//span[@class='other-act']/input[@type='text']",
    'loc_cfg_system_dhcps_assigned_info':r"//table[@id='dhcps-lease']/tr[@idx='$_$']",
    'loc_cfg_system_dhcps_assigned_mac_cell':r"//table[@id='dhcps-lease']//tr[@idx='$_$']/td[1]",
    'loc_cfg_system_dhcps_assigned_ip_cell':r"//table[@id='dhcps-lease']//tr[@idx='$_$']/td[2]",
    'loc_cfg_system_dhcps_assigned_leasetime_cell':r"//table[@id='dhcps-lease']//tr[@idx='$_$']/td[3]",
    'loc_cfg_system_dhcps_assigned_total_span':r"//table[@id='dhcps-lease']//div[@class='actions']/span",
    'loc_cfg_system_dhcps_apply_button':r"//input[@id='apply-dhcps']",

    'loc_cfg_sys_ctrycode_option':r"//select[@id='countrycode']",
    'loc_cfg_sys_allow_indoor_channel':r"//input[@id='do-channel-ctl']",
    'loc_cfg_sys_ctrycode_apply_button':r"//input[@id='apply-country']",
    'loc_cfg_network_management_icon':r"//img[@id='icon']",
# zj 2014-01-28  behavior change zf-7294
    'loc_cfg_network_management_icon_collapse': r"//img[@id='mgmt-icon' and contains(@src, 'collapse')]",
    'loc_cfg_network_management_icon_expand':"//img[@id='mgmt-icon' and contains(@src, 'expand')]",
#    'loc_cfg_network_management_icon_collapse': r"//img[@id='icon' and contains(@src, 'collapse')]",
#    'loc_cfg_network_management_icon_expand':"//img[@id='icon' and contains(@src, 'expand')]",
    'loc_cfg_enable_telnet_checkbox':r"//input[@id='telnetd']",
    'loc_cfg_enable_telnet_apply_button':r"//input[@id='apply-telnetd']",

    # Configure -> WLANs
    'loc_cfg_wlans_span':r"//span[@id='configure_wlans']",
    'loc_cfg_wlans_zeroit_activate_url_span':r"//span[@id='zeroit-url']",
    'loc_cfg_wlans_zeroit_auth_server_option':r"//select[@id='zeroit-authsvr']",
    'loc_cfg_wlans_zeroit_apply_button':r"//input[@id='apply-zeroit']",
    'loc_cfg_wlans_dynpsk_expire_option':r"//select[@id='expire']",
    'log_cfg_wlans_dynpsk_apply_button':r"//input[@id='apply-dpsk']",
    'loc_cfg_wlans_clone_span':r"//span[@id='clone-wlan-$_$']",

    'loc_cfg_ssid_name_textbox':r"//input[@id='name']",
    #cwang@2010-11-1, behavior change after Toranto 9.1.0.0.9
    'loc_cfg_ssid_textbox':r"//input[@id='ssid']",
    'loc_cfg_ssid_textbox':r"//input[@id='ssid']",
    'loc_cfg_open_radio':r"//input[@id='auth_open']",
    'loc_cfg_shared_radio':r"//input[@id='auth_shared']",
    'loc_cfg_eap_radio':r"//input[@id='auth_eap']",

    'loc_cfg_passphrase_textbox':r"psk",

    'loc_cfg_none_radio':r"//input[@id='enc_none']",
    'loc_cfg_wpa_radio':r"//input[@id='enc_wpa']",
    'loc_cfg_wpa2_radio':r"//input[@id='enc_wpa2']",
    'loc_cfg_wep64_radio':r"//input[@id='enc_wep64']",
    'loc_cfg_wep128_radio':r"//input[@id='enc_wep128']",

    'loc_cfg_tkip_radio':r"//input[@id='wpa-cipher-tkip']",
    'loc_cfg_aes_radio':r"//input[@id='wpa-cipher-aes']",

    'loc_cfg_generate_wep_button':r"//input[@id='generate-wep']",
    'loc_cfg_wepkey_textbox':r"//input[@id='wep-key']",
    'loc_cfg_wepkey_index1_radio':r"//input[@id='wepidx1']",
    'loc_cfg_wepkey_index2_radio':r"//input[@id='wepidx2']",
    'loc_cfg_wepkey_index3_radio':r"//input[@id='wepidx3']",
    'loc_cfg_wepkey_index4_radio':r"//input[@id='wepidx4']",

    'loc_cfg_wlan_ok_button':r"//input[@id='ok-wlan']",
    'loc_cfg_wlan_cancel_button':r"//input[@id='cancel-wlan']",
    'loc_cfg_wlan_create_span':r"//span[@id='new-wlan']",
    'loc_cfg_wlan_cell':r"//table[@id='wlan']//tr[$_$]/td[2]",

    'loc_cfg_wlan_checkbox':r"//table[@id='wlan']//tr[$_$]/td[1]/input[@name='wlan-select']",
    'loc_cfg_wlan_check_all_checkbox':r"//input[@id='wlan-sall']",
    'loc_cfg_wlan_delete_button':r"//input[@id='del-wlan']",
    'loc_cfg_wlan_row':r"//table[@id='wlan']//tr[@idx='$_$']",
    'loc_cfg_wlan_check_first_row':r"//table[@id='wlan']//tr[@idx ='0']",
    'loc_cfg_auth_server_eap_select':r"//select[@id='authsvr-eap']",
    'loc_cfg_auth_server_web_select':r"//select[@id='authsvr-web']",
    'loc_cfg_web_auth_checkbox':r"//input[@id='do-redirect']",
    'loc_cfg_client_isolation_checkbox':r"//input[@id='do-guestPcy']",

    'loc_cfg_wlans_dynamic_psk_checkbox':r"//input[@id='do-dynpsk']",
    'loc_cfg_wlans_zero_it_activation_checkbox':r"//input[@id='do-prov']",
    'loc_cfg_wlans_usage_guest_checkbox':r"//input[@id='usage-guest']",
    'loc_cfg_wlans_acl_option':r"//select[@id='acl-list']",
    'loc_cfg_wlans_uplink_preset_option':r"//select[@id='uplink-preset']",
    'loc_cfg_wlans_downlink_preset_option':r"//select[@id='downlink-preset']",
    'loc_cfg_wlans_do_vlan_checkbox':r"//input[@id='do-vlan']",
    'loc_cfg_wlans_vlan_id_textbox':r"//input[@id='vlan-id']",
    'loc_cfg_wlans_do_beacon_checkbox':r"//input[@id='do-beacon']",
    'loc_cfg_wlans_do_tunnel_checkbox':r"//input[@id='do-tunnelmode']",
    'loc_cfg_wlans_advanced_options_anchor':r"//tr[@id='cat-advanced']//a[@href='#']",

    'msg_cfg_wlans_invalid_vlanid':r"VLAN must be a number between 2\s*(and|-)\s*4094.",

    # Configure -> Access Points
    'loc_cfg_access_point_span':r"//span[@id='configure_aps']",
    'loc_cfg_access_point_table': r"//table[@id='ap']",
    'loc_cfg_access_point_search_box': r"//table[@id='ap']/tfoot/tr[2]//input[@type='text']",
    'loc_cfg_appolicy_allow_all_checkbox':r"//input[@id='allow-all']",
    'loc_cfg_appolicy_apply_button':r"//input[@id='apply-appolicy']",
    'loc_cfg_appolicy_max_clients_textbox':r"//input[@id='max-clients']",

    'loc_cfg_ap_select_all_checkbox':r"//input[@id='ap-sall']",
    'loc_cfg_ap_mac_cell':r"//table[@id='ap']//tr[$_$]/td[2]",
    'loc_cfg_ap_select_checkbox':r"//table[@id='ap']//tr[$_$]/td[1]//input[@name='ap-select']",
    'loc_cfg_ap_delete_button':r"//input[@id='del-ap']",
    'loc_cfg_ap_total_number_span':r"//table[@id='ap']//div[@class='actions']/span",
    'loc_cfg_ap_next_image':r"//img[@id='next-ap']",
    'loc_cfg_ap_actions_cell':r"//span[@id='edit-ap-$_$']",
    'loc_cfg_ap_channelization_option':r"//select[@id='channelization-11ng']",
    'loc_cfg_ap_channel_11bg_option':r"//select[@id='channel-11bg']",
    'loc_cfg_ap_txpower_11bg_option':r"//select[@id='power-11bg']",
    'loc_cfg_ap_txpower_11ng_checkbox':r"//input[@id='parentconf-power-11ng']",
    'loc_cfg_ap_channel_11ng_option':r"//select[@id='channel-11ng']",
    'loc_cfg_ap_channel_11na_option':r"//select[@id='channel-11na']",
    'loc_cfg_ap_channel_11ng_checkbox':r"//input[@id='parentconf-channel-11ng']",
    'loc_cfg_ap_channel_11na_checkbox':r"//input[@id='parentconf-channel-11na']",
    'loc_cfg_ap_txpower_11ng_option':r"//select[@id='power-11ng']",
    'loc_cfg_ap_txpower_11na_checkbox':r"//input[@id='parentconf-power-11na']",
    'loc_cfg_ap_txpower_11na_option':r"//select[@id='power-11na']",
    'loc_cfg_ap_ok_button':r"//input[@id='ok-ap']",
    'loc_cfg_ap_cancel_button':r"//input[@id='cancel-ap']",
    'loc_cfg_ap_smart_uplink_radio':r"//input[@id='apply-acl-false']",
    'loc_cfg_ap_manual_uplink_radio':r"//input[@id='apply-acl-true']",
    'loc_cfg_ap_uplink_checkbox':r"//div[@id='uplinks']//div[$_$]/input",
    'loc_cfg_ap_uplink_label':r"//div[@id='uplinks']//div[$_$]/label",
    'loc_cfg_ap_uplink_label2':r"//div[@id='uplinks']//div/label",
    'loc_cfg_ap_uplink_showall_anchor':r"//a[@id='showall']",

    'loc_cfg_ap_keep_ap_setting_radio':r"//input[@id='as-is']",
    'loc_cfg_ap_manual_ip_radio':r"//input[@id='manual']",
    'loc_cfg_ap_dhcp_ip_radio':r"//input[@id='dhcp']",
    'loc_cfg_ap_ip_address_textbox':r"//input[@id='ip']",
    'loc_cfg_ap_net_mask_textbox':r"//input[@id='netmask']",
    'loc_cfg_ap_gateway_textbox':r"//input[@id='gateway']",
    'loc_cfg_ap_pri_dns_textbox':r"//input[@id='dns1']",
    'loc_cfg_ap_sec_dns_textbox':r"//input[@id='dns2']",
    'loc_cfg_ap_show_more_button':r"//input[@id='showmore-ap']",

    'const_cfg_ap_table_size':15,

    # Configure -> Access Control
    'loc_cfg_access_controls_span':r"//span[@id='configure_acls']",
    ##zj 20140410 fix ZF-8015 8036
    'loc_cfg_acl_icon_expand':r"//img[@id='icon-acl' and contains (@src,'expand')]",
    'loc_cfg_acl_icon_collapse':r"//img[@id='icon-acl' and contains (@src,'collapse')]",


    'loc_cfg_acl_createnew_span':r"//span[@id='new-acl']",
    'loc_cfg_acl_name_textbox':r"//input[@id='name']",
    'loc_cfg_acl_allowall_radio':r"//input[@id='allowAll']",
    'loc_cfg_acl_denyall_radio':r"//input[@id='denyAll']",
    'loc_cfg_acl_mac_textbox':r"//input[@id='mac']",
    'loc_cfg_acl_createnew_station_button':r"//input[@id='create-new-station']",
    'loc_cfg_acl_mac_table':r"//table[@id='staTable']",
    'loc_cfg_acl_mac_addr_cell':r"//table[@id='staTable']//tr[$_$]/td[1]",
    'loc_cfg_acl_mac_delete_span':r"//table[@id='staTable']//tr[$_$]/td[2]/span[@id='delete']",
    'loc_cfg_acl_name_cell':r"//table[@id='acl']//tr[$_$]/td[2]",

    'loc_cfg_acl_cancel_button':r"//input[@id='cancel-acl']",
    'loc_cfg_acl_ok_button':r"//input[@id='ok-acl']",
    'loc_cfg_acl_delete_button':r"//input[@id='del-acl']",
    'loc_cfg_acl_all_checkbox':r"//input[@id='acl-sall']",    
    'loc_cfg_acl_edit_span':r"//span[@id='edit-acl-$_$']",
    'loc_cfg_acl_clone_span':r"//span[@id='clone-acl-$_$']",    
    'loc_cfg_acl_next_image':r"//img[@id='next-acl']",
    'loc_cfg_total_acls_span':r"//div[@id='actions-acl']/span",
    'loc_cfg_l2_acl_search_textbox':r"//table[@id='acl']//span[@class='other-act']/input[1]",

    'const_cfg_max_acl_rows':15,

    'loc_cfg_blocked_client_mac_cell':r"//table[@id='blocked-clients']//tr[$_$]/td[2]",
    'loc_cfg_blocked_client_all_checkbox':r"//input[@id='blocked-clients-sall']",
    'loc_cfg_blocked_client_checkbox':r"//table[@id='blocked-clients']//tr[$_$]//td[1]/input",
    'loc_cfg_blocked_client_unblock_button':r"//input[@id='del-blocked-clients']",
    'loc_cfg_blocked_client_search_textbox':r"//table[@id='blocked-clients']//span[@class='other-act']/input",
    'loc_cfg_total_blocked_client_span':r"//table[@id='blocked-clients']//div[@class='actions']/span",

    'const_cfg_max_blocked_client_rows':15,

    # Configure -> Maps
    'loc_cfg_maps_span':r"//span[@id='configure_maps']",

    'loc_cfg_maps_createnew_span':r"//span[@id='new-maps']",
    'loc_cfg_maps_name_textbox':r"//input[@id='name']",
    'loc_cfg_maps_description_textbox':r"//input[@id='description']",
    'loc_cfg_maps_browse_textbox':r"//input[@id='filename-uploadmap']",
    'loc_cfg_maps_uploaded_text':r"//span[@id='uploaded-uploadmap']",
    'loc_cfg_maps_error_uploaded_text':r"//span[@id='error-uploadmap']",
    'loc_cfg_maps_import_button':r"//input[@id='perform-uploadmap']",
    'loc_cfg_maps_cancel_link':r"//a[@id='cancel-uploadmap']",
    'loc_cfg_maps_ok_button':r"//input[@id='ok-maps']",
    'loc_cfg_maps_cancel_button':r"//input[@id='cancel-maps']",
    'loc_cfg_maps_delete_button':r"//input[@id='del-maps']",
    'loc_cfg_maps_selectall_checkbox':r"//input[@id='maps-sall']",
    'loc_cfg_maps_map_select_checkbox':r"//tr[@idx='$_$']//input[@name='maps-select']",
    'loc_cfg_maps_default_map_checkbox':r"//tr[@idx='0']//input[@name='maps-select']",
    'loc_cfg_maps_second_row':r"//tr[@idx='1']",
    'loc_cfg_maps_total_maps_span':r"//div[@id='actions-maps']//span",
    'loc_cfg_maps_next_image':r"//img[@id='next-maps']",
    'loc_cfg_maps_name_cell':r"//table[@id='maps']//tr[$_$]/td[2]",
    'loc_cfg_maps_description_cell':r"//table[@id='maps']//tr[$_$]/td[3]",
    'loc_cfg_maps_size_cell':r"//table[@id='maps']//tr[$_$]/td[4]",
	
	#add by west.li
    'loc_cfg_maps_edit_span':r"//span[@id='edit-maps-$_$']",
    'loc_cfg_maps_total_number_span':r"//div[@id='actions-maps']/span",

    'const_cfg_maps_max_row':15,
    'const_cfg_maps_supported_format':r"['.PNG', '.JPG', '.GIF']",

    # Configure -> Roles
    'loc_cfg_roles_span':r"//span[@id='configure_roles']",

    'loc_cfg_roles_createnew_span':r"//span[@id='new-role']",
    'loc_cfg_roles_rolename_textbox':r"//input[@id='rolename']",
    'loc_cfg_roles_description_textbox':r"//input[@id='description']",
    'loc_cfg_roles_radius_group_attr_textbox':r"//input[@id='radius-group-attr']",
    'loc_cfg_roles_allow_all_wlans_radio':r"//input[@id='allow-all-wlansvc-true']",
    'loc_cfg_roles_allow_specify_wlans_radio':r"//input[@id='allow-all-wlansvc-false']",
    'loc_cfg_roles_row':r"//table[@id='role']//tr[@idx='$_$']",
    'loc_cfg_roles_wlans_checkbox':r"//input[@id='wlansvc-$_$']",
    'loc_cfg_roles_wlans_label':r"//label[@for='wlansvc-$_$']",
    'loc_cfg_roles_allow_generate_pass_checkbox':r"//input[@id='can-generate-pass']",
    'loc_cfg_roles_allow_zd_admin_checkbox':r"allow-admin-priv",
    'loc_cfg_roles_full_admin_priv_radio':r"admin_rw",
    'loc_cfg_roles_operation_admin_priv_radio':r"admin_op",
    'loc_cfg_roles_limited_admin_priv_radio':r"admin_ro",
    'loc_cfg_roles_cancel_button':r"//input[@id='cancel-role']",
    'loc_cfg_roles_ok_button':r"//input[@id='ok-role']",
    'loc_cfg_roles_name_cell':r"//table[@id='role']//tr[$_$]/td[2]",
    'loc_cfg_roles_role_select_checkbox':r"//tr[@idx='$_$']//input[@name='role-select']",
    'loc_cfg_roles_roledefault_checkbox':r"//tr[@idx='0']//input[@name='role-select']",
	#edit by west.li
    'loc_cfg_roles_second_row':r"//table[@id='role']/tbody/tr[@idx='1']",
    'loc_cfg_roles_all_checkbox':r"//input[@id='role-sall']",
    'loc_cfg_roles_delete_button':r"//input[@id='del-role']",
    'loc_cfg_roles_clone_span':r"//span[@id='clone-role-$_$']",
	#added by west
    'loc_cfg_roles_edit_span1':r"//span[@id='edit-role-$_$']",

    'loc_cfg_roles_search_text':r"//table[@id='role']//tr[@class='t_search']//input[@type='text']",
    'loc_cfg_roles_edit_span':r"//table[@id='role']//tr/td[text()='%s']/../td/span[text()='Edit']",
    'loc_cfg_roles_operator_admin_priv_radio':r"admin_op",

    'const_cfg_roles_max_wlans_entries':8,

    # Configure -> Users
    'loc_cfg_users_span':r"//span[@id='configure_users']",

    'loc_cfg_user_create_span':r"//span[@id='new-user']",
    'loc_cfg_username_textbox':r"//input[@id='username']",
    'loc_cfg_fullname_textbox':r"//input[@id='full-name']",
    'loc_cfg_password_textbox':r"//input[@id='password1']",
    'loc_cfg_confirm_password_textbox':r"//input[@id='password2']",
    'loc_cfg_user_ok_button':r"//input[@id='ok-user']",
    'loc_cfg_user_cancel_button':r"//input[@id='cancel-user']",
    'loc_cfg_user_check_all_checkbox':r"//input[@id='user-sall']",
    'loc_cfg_user_delete_button':r"//input[@id='del-user']",
    'loc_cfg_user_row':r"//table[@id='user']//tr[$_$]/td[2]",
    'loc_cfg_user_next_image':r"//img[@id='next-user']",
    'loc_cfg_user_checkbox':r"//table[@id='user']//tr[$_$]/td[1]/input[@name='user-select']",
    'loc_cfg_user_total_number_span':r"//div[@id='actions-user']/span",
    'loc_cfg_user_search_textbox':r"//table[@id='user']//tr[@class='t_search']//input[@type='text']",
    'loc_cfg_user_clone_apan':r"//span[@id='clone-user-$_$']",
	#add by west
    'loc_cfg_user_edit_apan':r"//span[@id='edit-user-$_$']",
    'loc_cfg_user_name_cell':r"//table[@id='user']//tr[@idx='$_$']/td[2]",
    'loc_cfg_user_role_select':r"//select[@id='roles']",

    'const_cfg_max_row_user':15,

    # Configure -> Guest Access
    'loc_cfg_guest_access_span':r"//span[@id='configure_guests']",
    
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    'loc_cfg_guest_access_new_span':r"//span[@id='new-guestservice']",
    'loc_cfg_guest_access_name':r"//input[@id='name']",
    'loc_cfg_guest_access_edit_span' : r"//table[@id='guestservice']//tr/td[text()='%s']/../td/span[text()='Edit']",
    'loc_cfg_guest_access_check_box_before_profile' : r"//tr[@idx=%s]//input[@type='checkbox']",
    'loc_cfg_guest_access_delete_span' : r"//input[@id='del-guestservice']",
    'loc_cfg_guest_access_ok' : r"//input[@id='ok-guestservice']",
    'loc_cfg_guest_access_cancel' : r"//input[@id='cancel-guestservice']",
    'loc_cfg_guest_access_restrict_list' : r"//tr[@id='restricted-subnet']/th/a",

    'loc_cfg_guestaccess_guestauth_radio':r"//input[@id='guest-auth-guestpass']",
    'loc_cfg_guestaccess_boarding_portal_checkbox':r"//input[@id='guest-onboarding']",
    #'loc_cfg_guestaccess_shared_guestpass_checkbox':r"//input[@id='shared-guestpass']",
    'loc_cfg_guestaccess_no_guestauth_radio':r"//input[@id='guest-auth-none']",
    'loc_cfg_guestaccess_show_tou_checkbox':r"//input[@id='guest-show-tou']",
    'loc_cfg_guestaccess_redirect_orig_radio':r"//input[@id='guest-redirect-orig']",
    'loc_cfg_guestaccess_redirect_url_radio':r"//input[@id='guest-redirect-url']",
    'loc_cfg_guestaccess_redirect_url_textbox':r"//input[@id='redirect-url']",
    'loc_cfg_guestaccess_guest_apply_button':r"//input[@id='apply-guest']",

    'loc_cfg_guestaccess_guestpass_url_span':r"//span[@id='guestpass-url']",
    'loc_cfg_guestaccess_auth_server_option':r"//select[@id='authsvr']",
    'loc_cfg_guestaccess_guestpass_apply_button':r"//input[@id='apply-guestpass']",
    'loc_cfg_guestpass_countdown_by_issued_radio':r"//input[@id='guest-countdown-by-issued']",
    'loc_cfg_guestpass_countdown_by_used_radio':r"//input[@id='guest-countdown-by-used']",
    'loc_cfg_guestpass_guestvalid_textbox':r"//input[@id='guest-valid']",

    'loc_cfg_restricted_subnets_textbox':r"//table[@id='rule']/tbody/tr[$_$]/td[5]",
    'loc_cfg_restricted_subnets_apply_button':r"//input[@id='apply-subnets']",
    
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
    'loc_cfg_guestpass_selfservice_check_box': r"//input[@id='self-service']",
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226

    # for ZD8.0
    'loc_cfg_restricted_rule_row':r"//table[@id='rule']/tbody/tr[$_$]",
    'loc_cfg_restricted_rule_table':r"//table[@id='rule']",
    'loc_cfg_restricted_rule_dst_addr':r"//input[@id='rule-dst-addr']",
    'loc_cfg_restricted_rule_ok_button':r"//input[@id='ok-rule']",
    'loc_cfg_restricted_rule_del_button':r"//input[@id='del-rule']",
    'loc_cfg_restricted_rule_edit_span':r"//span[@id='edit-rule-$_$']",
    'loc_cfg_restricted_rule_create_span':r"//span[@id='new-rule']",
    'loc_cfg_restricted_rule_order_select':r"//select[@id='rule-id']",
    'loc_cfg_restricted_rule_checkbox':r"//table[@id='rule']/tbody/tr[$_$]/td[1]/input",

    'const_restricted_subnets':5,

    # Configure -> Hotspot Services
    'loc_cfg_hotspot_span':r"//span[@id='configure_hotspot']",
    'loc_cfg_wips_span':r"//span[@id='configure_wips']",

    # Configure -> Mesh
    'loc_cfg_mesh_span':r"//span[@id='configure_mesh']",

    'loc_cfg_mesh_enable_checkbox':r"//input[@id='do-mesh']",
    'loc_cfg_mesh_name_textbox':r"//input[@id='mesh-name']",
    'loc_cfg_mesh_psk_textbox':r"//input[@id='mesh-psk']",
    'loc_cfg_mesh_psk_generate_button':r"//input[@id='mesh-regenerate']",
    'loc_cfg_mesh_apply_button':r"//input[@id='apply-meshwlan']",
    
    'loc_cfg_abf_enable_checkbox':r"//input[@id='do-mesh-abf']",
    'loc_cfg_abf_rate_limit_textbox':r"//input[@id='rate-limit']",
    'loc_cfg_abf_apply_button':r"//input[@id='apply-meshabf']",

    # Configure -> Authentication Servers
    'loc_cfg_authentication_servers_span':r"//span[@id='configure_authsvrs']",

    'loc_cfg_authsvr_create_new_span':r"//span[@id='new-authsvr']",
    'loc_cfg_authsvr_ok_button':r"//input[@id='ok-authsvr']",
    'loc_cfg_authsvr_cancel_button':r"//input[@id='cancel-authsvr']",
    'loc_cfg_authsvr_name_textbox':r"//input[@id='name']",
    'loc_cfg_authsvr_type_radius_radio':r"//input[@id='type-radius-auth']",
    'loc_cfg_authsvr_type_ad_radio':r"//input[@id='type-ad']",
    'loc_cfg_authsvr_ip_address_textbox':r"//input[@id='pri-ip']",
    'loc_cfg_authsvr_port_textbox':r"//input[@id='pri-port']",
    'loc_cfg_authsvr_pwd_textbox':r"//input[@id='pri-pwd']",
    'loc_cfg_authsvr_pwd2_textbox':r"//input[@id='pri-pwd2']",
    'loc_cfg_authsvr_domain_textbox':r"//input[contains(@id,'search-base')]",

    'loc_cfg_authsvr_name_cell':r"//table[@id='authsvr']// tr[$_$]/td[2]",
    'loc_cfg_authsvr_edit_span':r"//table[@id='authsvr']//span[@id='edit-authsvr-$_$']",
    'loc_cfg_authsvr_clone_span':r"//span[@id='clone-authsvr-$_$']",
    'loc_cfg_authsvr_next_image':r"//img[@id='next-authsvr']",
    'loc_cfg_authsvr_select_checkbox':r"//table[@id='authsvr']//tr[$_$]/td[1]/input[@name='authsvr-select']",
    'loc_cfg_authsvr_select_all_checkbox':r"//input[@id='authsvr-sall']",
    'loc_cfg_authsvr_delete_button':r"//input[@id='del-authsvr']",
    'loc_cfg_authsvr_total_':r"//div[@id='actions-authsvr']/span",
    'loc_cfg_authsvr_total_number_span':r"//div[@id='actions-authsvr']/span",

    'loc_cfg_authsvr_test_authsvr_option':r"//select[@id='test-authsvr']",
    'loc_cfg_authsvr_test_authsvr_username_textbox':r"//input[@id='username-authtest']",
    'loc_cfg_authsvr_test_authsvr_password_textbox':r"//input[@id='password-authtest']",
    'loc_cfg_authsvr_test_authsvr_test_button':r"//input[@id='test-authsvrtest']",
    'loc_cfg_authsvr_msg_authtest_span':r"//span[@id='msg-authtest']",


    'const_cfg_authsvr_table_size':15,

    'const_radius_default_port':1812,
    'const_ad_default_port':389,
#@zj20150522 optimization the configuration of email alarm setting  zf-8437 
    # Configure -> Alarm Settings
    'loc_cfg_alarm_settings_span':r"//span[@id='configure_alarm']",
    'loc_cfg_alarm_settings_doemail_checkbox':r"//input[@id='do-email']",#loc_cfg_system_alarm_doemail_checkbox
    'loc_cfg_alarm_settings_email_textbox':r"//input[@id='email']",#loc_cfg_system_alarm_email_textbox
    'loc_cfg_alarm_settings_notify_apply_button':r"//input[@id='apply-notif']",#loc_cfg_system_alarm_notify_apply_button

    # Configure -> system ->Email Server    
    'loc_cfg_system_alarm_enable_checkbox':r"//input[@id='enable-email']",    
    'loc_cfg_system_alarm_smtp_ip_textbox':r"//input[@id='smtp-server']",
    'loc_cfg_system_alarm_apply_button':r"//input[@id='apply-email-server']",
#@zj20150522 optimization the configuration of email alarm setting   
    # Configure -> Services
    'loc_cfg_services_span':r"//span[@id='configure_svc']",
    'loc_cfg_services_enable_background_scan_2_4GHz_checkbox':r"//input[@id='scan']",
    'loc_cfg_services_enable_background_scan_5GHz_checkbox':r"//input[@id='scan_5g']",
    'loc_cfg_services_enable_background_scan_2_4GHz_interval':r"//input[@id='sleep']",
    'loc_cfg_services_enable_background_scan_5GHz_interval':r"//input[@id='sleep_5g']",
    'loc_cfg_services_enable_background_scan_apply_button':r"//input[@id='apply-scan']",
    
	'loc_cfg_pif_rate_limit_enable_checkbox':r"//input[@id='rate-limit-enabled']",
    'loc_cfg_pif_rate_limit_textbox':r"//input[@id='rate-limit']",
    'loc_cfg_pif_rate_limit_apply_button':r"//input[@id='apply-pif']",
	
    # Configure -> WIPS
    'loc_cfg_wips_span':r"//span[@id='configure_wips']",
    'loc_cfg_wips_report_rogue_devices_checkbox':r"//input[@id='report-rogue-ap']",
    'loc_cfg_wips_prevent_malicious_rogue_ap_checkbox':r"//input[@id='report-malicious-ap']",
    'loc_cfg_wips_apply_button':r"//input[@id='apply-wips']",
    
    #@author:yuyanan @since:2015-1-4 @change:9.9newfeature sslldap need import CA
    #Configure -> Certificate
    'loc_cfg_cerificate_span':r"//span[@id='configure_cert']",

    # Admin
    'loc_admin_anchor':r"//a[@href='admin.jsp']",

    # Admin -> Preference
    'loc_admin_preference_span':r"//span[@id='admin_pref']",

    'loc_admin_preference_auth_local_radio':r"//input[@id='auth-by-local']",
    'loc_admin_preference_auth_external_radio':r"//input[@id='auth-by-external']",
    'loc_admin_preference_auth_server_option':r"//select[@id='authsvr']",
    'loc_admin_preference_fallback_local_checkbox':r"//input[@id='fallback-local']",
    'loc_admin_preference_admin_name_textbox':r"//input[@id='admin-name']",
    'loc_admin_preference_admin_old_pass_textbox':r"//input[@id='admin-old-pass']",
    'loc_admin_preference_admin_pass1_textbox':r"//input[@id='admin-pass1']",
    'loc_admin_preference_admin_pass2_textbox':r"//input[@id='admin-pass2']",
    'loc_admin_preference_apply_button':r"//input[@id='apply-admin']",
    'loc_admin_preference_idle_timeout_textbox':r"//input[@id='idletime']",
    'loc_admin_preference_idle_timeout_apply_button':r"//input[@id='apply-idletime']",

    # Admin -> Backup
    'loc_admin_backup_span':r"//span[@id='admin_backup']",

    'loc_admin_reset_factory_button':r"//input[@id='restore-default']",

    # Admin -> Restart
    'loc_admin_restart_span':r"//span[@id='admin_restart']",

    # Admin -> Upgrade
    'loc_admin_upgrade_span':r"//span[@id='admin_upgrade']",

    'loc_admin_browse_file_button':r"//input[@id='filename-upgrade']",
    'loc_admin_perform_upgrd_button':r"//input[@id='perform-upgrade']",
    'loc_admin_current_version_span':r"//span[@id='curversion']",
    'loc_admin_error_upgrade_span':r"//span[@id='error-upgrade']",
    'loc_admin_error_restore_previous_radio':r"//input[@id='upgrade_errorinput_0']",
    'loc_admin_error_restore_default_radio':r"//input[@id='upgrade_errorinput_1']",
    'loc_admin_do_cancle_span':r"//a[@id='cancel-upgrade']",
    'loc_admin_continue_upgrade':r"//a[@id='continue-upgrade']",
    #Chico@2014-8-25, fix bug of ZF-9797
    'loc_admin_uploading':r"//span[@id='uploaded-upgrade']",
    #Chico@2014-8-25, fix bug of ZF-9797


    # Admin -> License
    'loc_admin_license_span':r"//span[@id='admin_license']",

    # Admin -> Diagnostic
    'loc_admin_diagnostic_span':r"//span[@id='admin_diag']",
    
    # Admin -> Registration
    'loc_admin_registration_span':r"//span[@id='admin_reg']",
    
    # Admin -> Support
    'loc_admin_support_span':r"//span[@id='admin_support']",
    
    'loc_admin_browse_entitlement_file_button':r"//input[@id='filename-uploadsupport']",
    'loc_admin_perform_entitlement_upload_button':r"//input[@id='perform-uploadsupport']",
    'loc_admin_entitlement_table':r"//table[@id='support']",
    'loc_admin_no_entitlement_alert_text':r"//strong",
    'loc_admin_check_entitlement_button':r"//input[@value='Check Entitlement']",
    
    
    'registration_name':r"//span[@id='reg-name']",
    'registration_email':r"//span[@id='reg-email']",
    'registration_phone':r"//span[@id='reg-phone']",
    'registration_cmp_name':r"//span[@id='reg-companyname']",
    'registration_cmp_addr':r"//span[@id='reg-companyaddr']",
    'registration_apply':r"//span[@id='apply-reg']",
    
    
    # Guest Pass Generation
    'loc_guestpass_username_textbox':r"//input[@id='username']",
    'loc_guestpass_password_textbox':r"//input[@name='password']",
    'loc_guestpass_login_button':r"//input[@name='ok']",

    'loc_guestpass_dialog_expire_span':r"//span[@id='expire']",
#    'loc_guestpass_dialog_pass_div':r"//div[@id='guestpass']",
    'loc_guestpass_dialog_pass_div':r"//div[@id='scene_single']//div[@class='key']",
    
    'loc_guestpass_loginfailed_div':r"//div[@id='loginfailed']",
    'loc_guestpass_printout_option':r"//select[@id='guestPrintList']",
    'loc_guestpass_print_instruction_anchor':r"//a[text()='Print Instructions']",
#    'loc_guestpass_guest_name_text':r"//th[contains(text(), 'the generated guest pass')]/strong",
    'loc_guestpass_guest_name_text':r"//div[@id='scene_single']//div[@class='text']/p",

    'loc_guestinfo_fullname_textbox':r"//input[@id='fullname']",
    'loc_guestinfo_duration_textbox':r"//input[@name='duration']",
    'loc_guestinfo_duration_unit_option':r"//select[@id='duration-unit']",
    'loc_guestinfo_remarks_textarea':r"//textarea[@name='remarks']",
    'loc_guestinfo_key_textbox':r"//input[@id='key']",
    # JLIN@20090713 modified for 8.2 changed
    # PHANNT@20100204: which version does this 'old' locator below apply???
    # should check and specify it in the ZDZPathUpdate accordingly
    #loc_guestinfo_next_button':r"//input[@name='ok']", # version prior to 8.2 ?
    'loc_guestinfo_next_button':r"//tr[@id='row-next']/td/input", # version 8.2 ?
    'loc_cfg_appolicy_mgmt_vlan_header':r"//form[@id='form-appolicy']//th[text()='Management VLAN']",
    'loc_mon_cac_dynamic_vlan':r"//table[@id='clients']//tr/th[contains(text(), 'VLAN')]",
    'loc_mon_aps_device_name':r"//table[@id='apsummary']//tr/th[contains(text(), 'Device Name')]",
    
    #only used in authorization cases
    'disabled_cfg_span':r"//li[@class='disabled']/span",
    #JLUH@20140423 modified for 9.8 changed
    'loc_guestaccess_email_content': r"//textarea[@id='emailset']",
    'loc_guestaccess_email_content_apply_button': r"//input[@id='apply-email-content']",
}

# all the string constants which will be helpful on detecting the WebUI info
Constants = {

}

feature_update = {
}
