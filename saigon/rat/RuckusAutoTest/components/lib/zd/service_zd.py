'''
@author: serena.tan@ruckuswireless.com
'''


LOCATORS_CFG_SERVICE = dict(
    # Self Healing
    #enable_adjust_ap_channel_chk = r"//input[@id='auto-ap-channel']",
    enable_adjust_ap_power_chk = r"//input[@id='auto-ap-power']",
    enable_adjust_ap_channel_chk = r"//input[@id='autoChan-2_4G']",#yuyanan 2014-7-14 bug:ZF-7817
    self_healing_apply_btn = r"//input[@id='apply-selfheal']",

    # Intrusion Prevention
    enable_protect_network_chk = r"//input[@id='auto-probe-limit']",
    enable_block_client_chk = r"//input[@id='auto-authfail-block']",
    block_client_interval_txt = r"//input[@id='blocktime']",
    intrusion_prevention_apply_btn = r"//input[@id='apply-ips']",

    # Background Scanning
    enable_scan_24g_chk = r"//input[@id='scan']",
    scan_24g_interval_txt = r"//input[@id='sleep']",
    enable_scan_5g_chk = r"//input[@id='scan_5g']",
    scan_5g_interval_txt = r"//input[@id='sleep_5g']",
    enable_report_rogue_device_chk = r"//input[@id='report-rogue-ap']",
    background_scan_apply_btn = r"//input[@id='apply-scan']",

    #Rogue DHCP Server Detection
    enable_detect_rogue_dhcp_chk = r"//input[@id='dhcpp']",
    rouge_dhcp_apply_btn = r"//input[@id='apply-dhcpp']",
    
    #Radar Avoidance Pre-Scanning
    enable_radar_avoid_prescan_chk = r"//input[@id='raps-enabled']",
    radar_avoid_prescan_apply_btn = r"//input[@id='apply-raps']",
    
    #AeroScout RFID
    enable_detect_aeroscout_rfid_chk = r"//input[@id='aeroscout-enabled']",
    aeroscout_rfid_apply_btn = r"//input[@id='apply-aeroscout']",
    
    #Active Client Detection
    enable_detect_rssi_chk = r"//input[@id='detect-rssi']",
    detect_rssi_interval_txt = r"//input[@id='clientrssi']",
    detect_rssi_apply_btn = r"//input[@id='apply-clientwarn']",
    
    #Tunnel Configuration
    enable_tunnel_encryption = r"//input[@id='encrypt']",
    tunnel_block_multicast = r"//input[@id='block-mcast']",
    tunnel_block_broadcast = r"//input[@id='block-bcast']",
    tunnel_enable_proxy_arp = r"//input[@id='tun-parp']",
    tunnel_cfg_apply_btn = r"//input[@id='apply-tun-cfg']",
	
	#Load Balancing(jluh added by 2013-09-26)
    client_load_balancing_24g_checkbox = r"//input[@id='clb2_4g']",
    client_load_balancing_5g_checkbox = r"//input[@id='clb5g']",
    client_load_balancing_24g_adjacent_radio_threshold_inputbox = r"//input[@id='adjacent-2_4g']",
    client_load_balancing_5g_adjacent_radio_threshold_inputbox = r"//input[@id='adjacent-5g']",
    client_load_balancing_apply_button = r"//input[@id='apply-client-load-balancing']",
    band_balancing_checkbox = r"//input[@id='bandbalance']",
    band_balancing_inputbox = r"//input[@id='percent_2_4g']",
    band_balancing_apply_button = r"//input[@id='apply-band-balancing']",
)


#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SERVICES)
    
    
def get_service_info(zd, is_nav = True):
    '''
    This method is used to get the service information from ZDWeb->Configure->Services.
    Output:
    service_info = dict(adjust_ap_power = False,
                        adjust_ap_channel = False,
                        protect_network = False,
                        block_client = False,
                        scan_24g = False,
                        scan_5g = False,
                        report_rogue_device = False,
                        detect_rogue_dhcp = False,
                        detect_aeroscout_rfid = False,
                        detect_rssi = False,
                        block_client_interval = '',
                        scan_24g_interval = '',
                        scan_5g_interval = '',
                        detect_rssi_interval = ''
                       )
    '''
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    #@yuyanan 2014-7-14 bug:ZF-7817
    chk_info = dict(adjust_ap_power = False,
                    adjust_ap_channel = False,
                    #protect_network = False,
                    #block_client = False,
                    scan_24g = False,
                    scan_5g = False,
                    #report_rogue_device = False,
                    #detect_rogue_dhcp = False,
                    detect_aeroscout_rfid = False,
                    detect_rssi = False,
                    )
    
    txt_value = dict(#block_client_interval = '',
                     scan_24g_interval = '',
                     scan_5g_interval = '',
                     detect_rssi_interval = '',
                    )
    
    chk_loc = "enable_%s_chk"
    for k in chk_info:
        loc = xlocs[chk_loc % k]
        if zd.s.is_element_present(loc) and zd.s.is_editable(loc) and zd.s.is_checked(loc):
            chk_info[k] = True
    
    txt_loc = "%s_txt"
    for k in txt_value:
        loc = xlocs[txt_loc % k]
        if zd.s.is_element_present(loc) and zd.s.is_editable(loc):
            txt_value[k] = zd.s.get_value(loc)
    
    service_info = dict()
    service_info.update(chk_info)
    service_info.update(txt_value)
    
    return service_info

default_interval = '20' #Run a background scan on 2.4/5GHz radio every 20 seconds

def verify_background_scan_factory_setting(zd, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    if not zd.s.is_checked(xlocs['enable_scan_24g_chk'])\
        or not zd.s.is_checked(xlocs['enable_scan_5g_chk']):
        return "either 2.4G or 5G background scanning options is't enabled after setting factory default"

    if default_interval != zd.s.get_value(xlocs['scan_24g_interval_txt']) \
        or default_interval != zd.s.get_value(xlocs['scan_5g_interval_txt']):
        return "either 2.4G or 5G background scanning interval time is't default value %s s" % default_interval

def set_background_scan_options(zd, option_2_4G, option_5G, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    if option_2_4G is None or option_2_4G == '' or option_2_4G == '0':
        zd.s.click_if_checked(xlocs['enable_scan_24g_chk'])
    else:
        zd.s.click_if_not_checked(xlocs['enable_scan_24g_chk'])
        zd.s.type_text(xlocs['scan_24g_interval_txt'], option_2_4G)

    if option_5G is None or option_5G == '' or option_5G == '0':
        zd.s.click_if_checked(xlocs['enable_scan_5g_chk'])
    else:
        zd.s.click_if_not_checked(xlocs['enable_scan_5g_chk'])
        zd.s.type_text(xlocs['scan_5g_interval_txt'], option_5G)        

    zd.s.click_and_wait(xlocs['background_scan_apply_btn'])    

#jluh added by 2013-09-26
def enable_load_balancing(zd, clb_24g=True, clb_5g=True, bandb=True, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    if clb_24g:
        zd.s.click_if_not_checked(xlocs['client_load_balancing_24g_checkbox'])
    if clb_5g:
        zd.s.click_if_not_checked(xlocs['client_load_balancing_5g_checkbox'])
    zd.s.click_and_wait(xlocs['client_load_balancing_apply_button'])
    if bandb:
        zd.s.click_if_not_checked(xlocs['band_balancing_checkbox'])
        zd.s.click_and_wait(xlocs['band_balancing_apply_button'])
        
#jluh added by 2013-09-26        
def disable_load_balancing(zd, clb_24g=False, clb_5g=False, bandb=False, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    if not clb_24g:
        zd.s.click_if_checked(xlocs['client_load_balancing_24g_checkbox'])
    if not clb_5g:
        zd.s.click_if_checked(xlocs['client_load_balancing_5g_checkbox'])
    zd.s.click_and_wait(xlocs['client_load_balancing_apply_button'])
    if not bandb:
        zd.s.click_if_checked(xlocs['band_balancing_checkbox'])
        zd.s.click_and_wait(xlocs['band_balancing_apply_button'])
        
#jluh added by 2013-09-26        
def set_load_balancing_value(zd, **kwargs):
    lb_args = {}
    lb_args = lb_args.update(kwargs)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    clb_24g = True
    clb_5g = True
    bandb = True
    clb_24g_value = ''
    clb_5g_value = ''
    bandb_percent_value = ''
    
    if lb_args.has_key('clb_24g') and lb_args['clb_24g']:
        clb_24g = lb_args['clb_24g']
    if lb_args.has_key('clb_5g') and lb_args['clb_5g']:
        clb_5g = lb_args['clb_5g']
    if lb_args.has_key('clb_24g_value') and lb_args['clb_24g_value']:
        clb_24g_value = lb_args['clb_24g_value']
    if lb_args.has_key('clb_5g_value') and lb_args['clb_5g_value']:
        clb_24g_value = lb_args['clb_5g_value']
    if lb_args.has_key('bandb') and lb_args['bandb']:
        bandb = lb_args['bandb']
    if lb_args.has_key('bandb_percent_value') and lb_args['clb_24g_valuebandb_percent_value']:
        bandb_percent_value = lb_args['bandb_percent_value']       
    
    enable_load_balancing(zd, clb_24g, clb_5g, bandb)
    
    #set the value of client balancing and band balancing value
    if clb_24g_value:
        zd.s.type_text(xlocs['client_load_balancing_24g_adjacent_radio_threshold_inputbox'], clb_24g_value)
    if clb_5g_value:
        zd.s.type_text(xlocs['client_load_balancing_5g_adjacent_radio_threshold_inputbox'], clb_5g_value)
    zd.s.click_and_wait(xlocs['client_load_balancing_apply_button'])
    if bandb_percent_value:
        zd.s.type_text(xlocs['band_balancing_inputbox'], bandb_percent_value)
        zd.s.click_and_wait(xlocs['client_load_balancing_apply_button'])
        
    
def background_scan_2_4G_enabled(zd): 
    nav_to(zd)
    xlocs = LOCATORS_CFG_SERVICE
    if zd.s.is_checked(xlocs['enable_scan_24g_chk']):
        return True
    else:
        return False
     
def set_tunnel_encryption_option(zd, enable=False, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    if enable:
        zd.s.click_if_not_checked(xlocs['enable_tunnel_encryption'])
    else:
        zd.s.click_if_checked(xlocs['enable_tunnel_encryption'])

    zd.s.click_and_wait(xlocs['tunnel_cfg_apply_btn'])
    
#2014-0221 ZF-7537 Fix the problem caused by the modification of change list 191150.
def set_2_4_G_background_scan_options(zd,option):
    nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    if option is None or option == '' or option == '0':
        zd.s.click_if_checked(xlocs['enable_scan_24g_chk'])
    else:
        zd.s.click_if_not_checked(xlocs['enable_scan_24g_chk'])
        zd.s.type_text(xlocs['scan_24g_interval_txt'], option)
    zd.s.click_and_wait(xlocs['background_scan_apply_btn']) 
#2014-0221 ZF-7537

#@zj 20140805 fix ZF-7267
def get_radio_avoidance_prescanning_option(zd, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    option = ''
    if zd.s.is_element_disabled(xlocs['enable_radar_avoid_prescan_chk'], timeout = 0.2, disabled_xpath = "[@disabled]"):
        option = 'checkbox_grey'
    else:
        if zd.s.is_checked(xlocs['enable_radar_avoid_prescan_chk']):
            option = 'enable'
        else:
            option = 'disable'

    return option

def set_radio_avoidance_prescanning_option(zd, option, is_nav = True):
    if is_nav:
        nav_to(zd)
    
    xlocs = LOCATORS_CFG_SERVICE
    
    if zd.s.is_element_disabled(xlocs['enable_radar_avoid_prescan_chk'], timeout = 0.2, disabled_xpath = "[@disabled]"):
        raise Exception("Radio avoidance pre-scanning checkbox is grey in ZD GUI, cannot operate it")

    if option == 'enable':
        zd.s.click_if_not_checked(xlocs['enable_radar_avoid_prescan_chk'])
    else:
        zd.s.click_if_checked(xlocs['enable_radar_avoid_prescan_chk'])

    zd.s.click_and_wait(xlocs['radar_avoid_prescan_apply_btn'])   
#@zj 20140805 fix ZF-7267

    