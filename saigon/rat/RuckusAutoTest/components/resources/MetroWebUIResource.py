
# defining the dictionary of all WebUI locators
Locators = {
    'self': "", # standardizing based on the constructLocators recursive function
    'status_system_link'   : "//a[contains(@href,'status/system.asp')]",
    'status_wireless_link' : "//a[contains(@href,'sWireless.asp?subp=common')]",
    # wireless menu HORIZONTAL for wlans
    'status_common'        : "//a[contains(@href,'/sWireless.asp?subp=Common')]",
    'status_wan'           : "//a[contains(@href,'/sWireless.asp?subp=apcli0')]", # WAN
    'status_wlan1'         : "//a[contains(@href,'/sWireless.asp?subp=ra0')]" ,   # HOME
    'status_wlan2'         : "//a[contains(@href,'/sWireless.asp?subp=ra1')]" ,   # DATA
    'stats'                : "//a[contains(@href,'/sWirelessStation.asp?mac')]" ,
    # status buttons
    'enable_auto_update'   : "//input[@name='enableautoupdate']",   #INTERNET, SYSTEM and WIRELESS
    'disable_auto_update'  : "//input[@name='disableautoupdate']",
    'renew'                : "//input[@id='renew']",
    'release'              : "//input[@id='release']",

    # CONFIGURATION > Device/Internet/System
    'config_system_link'   : "//a[contains(@href,'configuration/system.asp')]",
    'config_wireless_link' : "//a[contains(@href,'/cWireless.asp?subp=common')]",
    'config_port_fwd_link' : "//a[contains(@href,'configuration/portforward.asp')]",
    'config_acl_link'      : "//a[contains(@href,'cAcl.asp?subp=ra0')]",
    'config_wizard_link'   : "//a[contains(@href,'quickstart/mode_of_operation.asp')]",
    #wireless menu HORIZONTAL for wlans
    'config_common'        : "//a[contains(@href,'/cWireless.asp?subp=Common')]",
    'config_wan'           : "//a[contains(@href,'/cWireless.asp?subp=apcli0')]", # WAN
    'config_wlan1'         : "//a[contains(@href,'/cWireless.asp?subp=ra0')]" ,   # HOME
    'config_wlan2'         : "//a[contains(@href,'/cWireless.asp?subp=ra1')]" ,   # DATA
    'go_back'              : "//a[contains(@href,'/configuration/wireless.asp')]",
    #device
    'device_name'          : "//input[@id='devicename']",
    'home_username'        : "//input[@id='home-username']",
    'home_confirm'         : "//input[@id='confirm']",
    'sp_username'          : "//input[@id='sp-username']",
    'sp_password'          : "//input[@id='sp-password']",
    'sp_confirm'           : "//input[@id='sp-confirm']",
    #internet
    'ntp'                  : "//input[@id='ntpserver']",
    'gateway0'             : "//input[@id='gateway0']",
    'gateway1'             : "//input[@id='gateway1']",
    'gateway2'             : "//input[@id='gateway2']",
    'gateway3'             : "//input[@id='gateway3']",
    'dns0'                 : "//input[@id='primarydns0']",
    'dns1'                 : "//input[@id='primarydns1']",
    'dns2'                 : "//input[@id='primarydns2']",
    'dns3'                 : "//input[@id='primarydns3']",
    'nd_dns0'              : "//input[@id='secondarydns0']",
    'nd_dns1'              : "//input[@id='secondarydns1']",
    'nd_dns2'              : "//input[@id='secondarydns2']",
    'nd_dns3'              : "//input[@id='secondarydns3']",
    'dhcp'                 : "//input[@id='type-dhcp']",
    'static'               : "//input[@id='type-static']",
    'static0'              : "//input[@id='ipaddress0']",
    'static1'              : "//input[@id='ipaddress1']",
    'static2'              : "//input[@id='ipaddress2']",
    'static3'              : "//input[@id='ipaddress3']",
    'mask0'                : "//input[@id='mask0']",
    'mask1'                : "//input[@id='mask1']",
    'mask2'                : "//input[@id='mask2']",
    'mask3'                : "//input[@id='mask3']",
    'unicast'              : "//input[@id='dhcpcflagmode-unicast']",
    'broadcast'            : "//input[@id='dhcpcflagmode-broadcast']",
    'auto'                 : "//input[@id='dhcpcflagmode-auto']",
    #system
    'bridge_eth'           : "//input[@id='ethernet-y']",
    'bridge_wlan1'         : "//input[@id='home-wlan-y']",
    'bridge_wlan2'         : "//input[@id='data-wlan-y']",
    'route_eth'            : "//input[@id='ethernet-n']",
    'route_wlan1'          : "//input[@id='home-wlan-n']",
    'route_wlan2'          : "//input[@id='data-wlan-n']",
    'wds_en'               : "//input[@id='wdsmode-y']",
    'wds_dis'              : "//input[@id='wdsmode-n']",
    'dhcp_server_en'       : "//input[@id='dhcp-y']",
    'dhcp_server_dis'      : "//input[@id='dhcp-n']",
    'start0'               : "//input[@id='startaddress0']",
    'start1'               : "//input[@id='startaddress1']",
    'start2'               : "//input[@id='startaddress2']",
    'start3'               : "//input[@id='startaddress3']",
    'max_users'            : "//input[@id='maxusers']",
    #wireless common
    'internal'             : "//input[@id='internal-only']",
    'external'             : "//input[@id='external-only']",
    'both'                 : "//input[@id='both']",
    'bssid'                : "//input[@id='bssid']",
    'preferred'            : "//input[@id='bssid-locked-n']",
    'locked'               : "//input[@id='bssid-locked-y']",
    'survey'               : "//input[@id='last-survey']",
    'survey_tbl'           : "//table[@class='datatable']",
    'rescan'               : "//input[@id='re-scan']",
    'inner_auth'           : "//select[@id='eap-ttls-inner-auth-proto']",
    'identity'             : "//input[@id='eap-ttls-user-identity']",
    'eap_username'         : "//input[@id='eap-ttls-user-name']",
    'eap_password'         : "//input[@id='eap-ttls-password']",
    #wireless-lan
    'isolation_en'         : "//input[@id='isolation-y']",
    'isolation_dis'        : "//input[@id='isolation-n']",
    #port forward
    'add_acl'              : "//a[@id='addlink']",
    #access control list
    'acl_wlan1'            : "//a[contains(@href,'/cAcl.asp?subp=ra0')]",
    'acl_wlan2'            : "//a[contains(@href,'/cAcl.asp?subp=ra1')]",
    'acl_dis'              : "//input[@id='aclmode-0']",
    'acl_allow'            : "//input[@id='aclmode-1']",
    'acl_deny'             : "//input[@id='aclmode-2']",
    'show_mac'             : "//table[@id='knownmacstable1']//a[contains (@href, '#')]",
    'add'                  : "//table[@id='addentry']//a[contains (@href, '#')]",
    'cancel'               : "//input[@type='button']",
    #quick wizard
    'wizard_route'         : "//input[@id='metro_c_input']",
    'wizard_bridge'        : "//input[@id='metro_r_input']",
    'next'                 : "//input[@id='submitbtn']",
    'previous'             : "//div[@id='box_footer']//a[contains (@href, 'index.html')]",
    'reload'               : "//div[@id='box_footer']//a[@id='reloadbtn']",
    'wizard_ssid'          : "//input[@id='lan_ssid']",
    'wizard_open'          : "//input[@id='security_open']",
    'wizard_wep'           : "//input[@id='security_wep']",
    'wizard_wpa'           : "//input[@id='security_wpa']",

    # MAINTENANCE > Reboot/Upgrade/Support
    'refresh'              : "//div[@class='log-wrapper']//a[contains (@href, '#')]",#used on multiple pages
    # reboot
    'reboot_now'           : "//input[@value='Reboot Now']",
    'reset'                : "//a[@id='resetlink']",
    # upgrade
    'FTP'                  : "//input[@id='method-ftp']",
    'TFTP'                 : "//input[@id='method-tftp']",
    'WEB'                  : "//input[@id='method-web']",
    'LOCAL'                : "//input[@id='method-local']",
    'server_name'          : "//input[@id='servername']",
    'server_url'           : "//input[@id='url']",
    'local_url'            : "//input[@id='local_fw_file']",
    'port'                 : "//input[@id='port']",
    'image_file'           : "//input[@id='imagefile']",
    'username'             : "//input[@id='username']",
    'password'             : "//input[@id='password']",
    'indicator'            : "//div[@id='indicatorwrapper']",#track upgrade pass/fail
    'progress'             : "//div[@id='progress']",  #track progress of upgrade
    'workinginfo'          : "//div[@id='workinginfo']",  #track progress of upgrade
    'save_params'          : "//input[@id='save-button']",
    'upgrade_en'           : "//input[@id='autoupgrade-y']",
    'upgrade_dis'          : "//input[@id='autoupgrade-n']",
    'check_interval'       : "//select[@id='interval']", #interval to check for new firmware
    'reboot_time'          : "//select[@id='boottime']", #reboot time after sucessfully upgrade
    'restore'              : "//a[@id='restorelink']",# used on multiple pages
    'server0'              : "//input[@id='serveraddress0']",
    'server1'              : "//input[@id='serveraddress1']",
    'server2'              : "//input[@id='serveraddress2']",
    'server3'              : "//input[@id='serveraddress3']",
    'file_name'            : "//input[@id='filename']",
    'ftp_username'         : "//input[@id='spt-username']",
    'upload'               : "//input[@id='upload-submit']",
    'alert'                : "//dl[@id='alertbox']",

    #ADMINISTRATOR > managment,diagnostic,log
    'limit_mgmt'           : "//input[@id='manage-ip-limit-ip-range-status']",
    'allow_mgmt'           : "//input[@id='manage-ip-status']",
    # diagnostic
    'ping'                 : "//input[@id='ping']",
    'trace'                : "//input[@id='traceroute']",
    'trace_button'         : "//form[@id='tracerouteform']//input[@type='button']",
    'ping_button'          : "//form[@id='pingform']//input[@type='button']",
    'ping_output'          : "//div[@id='pingresults']/pre",
    'trace_output'         : "//div[@id='tracertresults']//pre[@class='systemoutput']",
    #log
    'log_y'                : "//input[@id='enablelog-y']",
    'log_n'                : "//input[@id='enablelog-n']",
    'host0'                : "//input[@id='sysloghost0']",
    'host1'                : "//input[@id='sysloghost1']",
    'host2'                : "//input[@id='sysloghost2']",
    'host3'                : "//input[@id='sysloghost3']",
    'host_port'            : "//input[@id='sysloghostport']",
    'admin_output'         : "//div[@class='log-wrapper']/pre",
    }

