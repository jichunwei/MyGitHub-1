
# defining the dictionary of all WebUI locators
Locators = {
    'self': "", # standardizing based on the constructLocators recursive function

    # Login & Logout
    'LoginUsernameTxt': "//input[contains(@id,'login-username')]",
    'LoginPasswordTxt': "//input[contains(@id,'password')]",
    'LoginBtn' : "//input[contains(@title,'Login')]",  # login button
    'LogoutBtn': "//input[contains(@title,'Logout')]", # logout button


    # MAIN tab > actually, AP has only one tab.
    # So the homepage (logged in page) is chosen to be main tab
    'MainPageLink': "//a[contains(@href,'status/device.asp')]",

    # STATUS menu
    'StatusDeviceLink'  : "//a[contains(@href,'status/device.asp')]",
    'StatusInternetLink': "//a[contains(@href,'status/internet.asp')]",
    'StatusWirelessLink': "//a[contains(@href,'sWireless.asp?wifi=0&subp=common')]",
    'StatusLocalServicesLink': "//a[contains(@href,'status/services.asp')]",

    # CONFIG menu
    'ConfigDeviceLink'     : "//a[contains(@href,'configuration/device.asp')]",
    'ConfigInternetLink'   : "//a[contains(@href,'configuration/internet.asp')]",
    'ConfigWirelessLink'   : "//a[contains(@href,'/cWireless.asp?wifi=0&subp=common')]",
    'ConfigWirelessLink_5G'   : "//a[contains(@href,'/cWireless.asp?wifi=1&subp=common')]", # For 5G config
    'ConfigAccessCtrlsLink': "//a[contains(@href,'cAcl.asp?subp=wlan0')]",
    'ConfigVlanLink'       : "//a[contains(@href,'configuration/vlan.asp')]",

    # MAINTENANCE menu
    'MtcUpgradeLink'    : "//a[contains(@href,'maintenance/upgrade.asp')]",
    'MtcRebootResetLink': "//a[contains(@href,'maintenance/reboot.asp')]",
    'MtcSupportInfoLink': "//a[contains(@href,'maintenance/support_info.asp')]",

    # ADMIN menu
    'AdminMgmtLink' : "//a[contains(@href,'administrator/management.asp')]",
    'AdminDiagsLink': "//a[contains(@href,'administrator/diagnostics.asp')]",
    'AdminLogLink'  : "//a[contains(@href,'administrator/log.asp')]",


    # STATUS > Device
    'StatusDeviceTbl': "//div[@id='content']/table",

    'StatusInternetGeneralTbl': "//div[@id='content']/table[1]",
    'StatusInternetConnTbl'   : "//div[@id='content']/table[2]",

    'DeviceGeneral': {
        'self': "",
        'DeviceNameTxt': "",
    },
    # STATUS > Wireless
    'StatusWireless': {
        'self': "",
        #'CommonTab'  : "//a[contains(@href,'sWireless.asp?subp=Common')]",
        'ItemTabTmpl': "//a[contains(@href,'sWireless.asp?subp=wlan%s')]"
      },

    'WLANCommon': {
        'self': "",
        'Tbl': "//div[@id='content']/table",
        # Link to go WLAN Common page
        'HomePage': "//a[contains(@href,'/cWireless.asp?wifi=0&subp=Common')]",
        # Items in detail for Wireless Common
        'WModeCb': "//select[@id='freqband']",
        'ChannelCb': "//select[@id='channel']",
        'ChannelWidthCb': "//select[@id='channelwidth']",
        'CountryCodeCb': "//select[@id='countrycode']",
        'CountryCodeCb': "//select[@id='countrycode']",
        # Item in Advance Setting
        'TxPowerCb': "//select[@id='txpower']",
        'ProtModeDisabledRd': "//input[@id='modeD']",
        'ProtModeCTSRd': "//input[@id='modeC']",
        'ProtModeRTSCTSRd': "//input[@id='modeRC']",
        'EditCommonBtn': "//input[@id='advancedsettings']",
      },

    'WirelessItem': {
        'self': "",
        'Tbl': "//div[@id='content']/table[1]",
        'IsDeviceConnected': "//div[@id='content']",
        'ConnectedDevicesTbl': "//div[@id='content']/table[2]",
      },
    'WLANDet': {
        'self': "",
        'Tbl': "//div[@id='content']/table[1]",
        'IsDeviceConnected': "//div[@id='content']",
        'ConnectedDevicesTbl': "//div[@id='content']/table[2]",

        # Items in detail for Wireless 1 to 8
        # Link to go to wlan 1 to 8
        'HomePageTmpl': "//a[contains(@href,'/cWireless.asp?wifi=0&subp=tab%d')]",

        'WAvailERd': "//input[@id='wireless-y']",
        'WAvailDRd': "//input[@id='wireless-n']",

        # Wireless 1 Broadcast SSID
        'WBroadcastERd': "//input[@id='broadcast-y']",
        'WBroadcastDRd': "//input[@id='broadcast-n']",

        # Wireless Client Isolation: This option is not available on AP WebUI
        #'WIsolationChk': "//input[@id='check-HZ%d.isoloation']",
        #'WIsolationERd': "//input[@id='HZ%d.isoloation.0']",
        #'WIsolationDRd': "//input[@id='HZ%d.isoloation.1']",

        #Wireless Name
        'WNameTxt': "//input[@id='wlan-tabname']",

        #Wireless SSID name
        'WSSIDTxt': "//input[@id='ssid']",

        #Edit Threshold Setting button
        'EditThresBtn': "//input[@id='advancedsettings']",
        'EditRateLimitingBtn': "//input[@id='trafficsettings']",

        # Wireless Data Beacon Interval is not available on FM WebUI
        'WBeaConIntTxt': "//input[@id='beacon']",

        # Wireless 1 Data Beacon Rate (DTIM)
        'WDTIMTxt': "//input[@id='dtim']",

        #Wireless 1 Fragment Threshold
        'WFragThresTxt': "//input[@id='fragment']",

        #Wireless 1 RTS / CTS Threshold
        'WRTSCTSTxt': "//input[@id='rtscts']",

        #Wireless 1 Downlink Rate
        'WDownlinkCb': "//select[@id='downlink']",

        #Wireless 1 Uplink Rate
        'WUplinkCb': "//select[@id='uplink']",

        #Wireless 1 Encryption Method
        'WEncryptCb': "//select[@id='securitymode']",

        #Detail for WEP mode
        'WOpenRd': "//input[@id='wep-auth-open']",
        'WSharedKeyRd': "//input[@id='wep-auth-shared']",
        'WAutoRd': "//input[@id='wep-auth-auto']",

        #Wireless 1 Encryption Strength
        'WEncryptLenCb': "//select[@id='wepkeylen']", #13, 26, 5, 10

        # Key Entry Method
        'WKeyEntryHexaRd': "//input[@id='keymethod-hex']",
        'WKeyEntryAsciiRd': "//input[@id='keymethod-ascii']",

        #Wireless 1 WEP Key Index
        'WKeyIndexCb': "//select[@id='defkeyidx']", #1,2,3,4

        #Wireless 1 WEP Key
        #This one is a special item. There are four keys (1, 2, 3, 4). Accordingly each key, locator of textbox
        #password and cpassword will be different. In this case, we need to use attribute "@style"
        #to filter the invisible items. More detail:
        #Criteria 1: //tr[contains(@id, 'wepkey') and not(contains(@style, 'display: none'))]: To filter invisible "WEP Key" rows.
        # Criteria 2: //input[contains(@id,'check-HZ%d.wepkey')]: To point to the expected item in the visible row.
        'WWEPPassphraseTxt': "//input[@id='weppassphrase']",
        'WGenPassphraseBtn': "//input[@id='generatebtn']",
        'WWEPKeyTxt': "//input[@id='wepkey']",
        #'WWEPKeyPassTxt': "//input[@id='HZ%d.wepkey.%d']",
        #'WCWEPKeyPassTxt': "//input[@id='c-HZ%d.wepkey.%d']",

        #Wireless 1 WPA Version
        'WWPAVer1Rd': "//input[@id='wpa-version-wpa']", #WPA
        'WWPAVer2Rd': "//input[@id='wpa-version-wpa2']", #WPA2
        'WWPAVerAutoRd': "//input[@id='wpa-version-auto']", #Auto

        #Wireless 1 Authentication:
        'WAuthPSKRd'   : "//input[@id='wpa-auth-psk']", #PSK
        'WAuth802.1xRd': "//input[@id='wpa-auth-1x']", #WPA2
        'WAuthAutoRd'  : "//input[@id='wpa-auth-auto']", # Auto


        #Wireless 1 WPA Algorithm:
        #7942 has only AES and Auto. Its locators for these two items are different from other model
        'WWPATKIPRd': "//input[@id='wpa-alg-tkip']", #TKIP
        'WWPAAESRd': "//input[@id='wpa-alg-aes']", #AES
        'WWPAAutoRd': "//input[@id='wpa-alg-auto']", #Auto

        #Passphrase for PSK
        'WPSKPassphraseTxt': "//input[@id='wpapassphrase']",

        #Wireless 1 Radius NAS-ID
        'WRadiusTxt': "//input[@id='wpa_nas_id']",

        #Wireless 1 Authentication IP address
        'WAuthIPTxtTmpl': "//input[@id='auth-ip%d']",
        'WAuthIP1Txt': "//input[@id='auth-ip0']",
        'WAuthIP2Txt': "//input[@id='auth-ip1']",
        'WAuthIP3Txt': "//input[@id='auth-ip2']",
        'WAuthIP4Txt': "//input[@id='auth-ip3']",

        #Wireless 1 Authentication Port:
        'WAuthPortTxt': "//input[@id='auth-port']",

        #Wireless 1 Authentication Server Secret:
        'WAuthSecretTxt': "//input[@id='auth-secret']",

        #Wireless 1 Accounting IP address:
        'WAcctIPTxtTmpl': "//input[@id='acct-ip%d']",
        'WAcctIP1Txt': "//input[@id='acct-ip0']",
        'WAcctIP2Txt': "//input[@id='acct-ip1']",
        'WAcctIP3Txt': "//input[@id='acct-ip2']",
        'WAcctIP4Txt': "//input[@id='acct-ip3']",

        #Wireless 1 Accounting Port:
        'WAcctPortTxt': "//input[@id='acct-port']",

        #Wireless 1 Accounting Server Secret:
        'WAcctSecretTxt': "//input[@id='acct-secret']",

        # Update Setting button
        'UpdateBtn': "//input[@id='submit-button']",
        'BackLinkLnk' : "//a[contains(@href, 'wireless.asp')]",

      },

    # MAINTENANCE > Support Info
    'SupportInfo': {
        'self': "",
        'CurrentLog': "//pre[@id='currentlog']"
      },

    'Management': {
        'self': "//div[@id='content']",

        'TelnetERd': "//input[@id='telnet-y']",
        'TelnetDRd': "//input[@id='telnet-n']",
        'TelnetPort': "//input[@id='telnetport']",

        'SSHERd': "//input[@id='ssh-y']",
        'SSHDRd': "//input[@id='ssh-n']",
        'SSHPort': "//input[@id='sshport']",

        'HTTPERd': "//input[@id='http-y']",
        'HTTPDRd': "//input[@id='http-n']",
        'HTTPPort': "//input[@id='httpport']",

        'HTTPSERd': "//input[@id='https-y']",
        'HTTPSDRd': "//input[@id='https-n']",
        'HTTPSPort': "//input[@id='httpsport']",

        # TR069/ SNMP Management Choice
        'AutoRadio': "//input[@id='remote_management_mode_0']",
        'SnmpRadio': "//input[@id='remote_management_mode_2']",

        'CallHomeIntCb': "//select[@id='tr069periodicinforminterval']",
        'FmUrlTxt': "//input[@id='tr069dnsmapurl']",

        # TR069 Status
        'Tr069StatusTbl': "//table[@id='tr069_options2']",

        'SubmitBtn': "//input[@id='submit-button']",
    }
  }

# all the string constants which will be helpful on detecting the WebUI info
Constants = {
    'NoDeviceConnectedMsg': "No stations are currently associated with this WLAN",

    # MAINTENANCE > SUPPORT INFO, getting device model
    'SupportInfoDeviceModelRe': ".*Model/Serial Num.*:(.*)/.*",

    'CallHomeInterval': {
        'Min': '1 min.*', # re
    },

  }

