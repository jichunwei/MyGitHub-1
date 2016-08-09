# defining the dictionary of all WebUI locators
Locators = {
    # Login & Logout
    'LoginUsernameTxt': "//input[contains(@id,'username')]",
    'LoginPasswordTxt': "//input[contains(@name,'password')]",
    'LoginBtn'        : "//input[contains(@value,'Login') or contains(@value,'Log In')]",
    'LogoutBtn'       : "//a[contains(@href,'j_acegi_logout')]",

    # tabs
    'DashboardLink'   : "//a[contains(.,'Dashboard')]",
    'InventoryLink'   : "//a[contains(.,'Inventory')]",
    'SysAlertsLink'   : "//a[contains(.,'Monitor')]",
    'ProvisioningLink': "//a[contains(.,'Configure')]",
    'AdminLink'       : "//a[contains(.,'Administer')]",

    # INVENTORY menu
    'InvManageDevicesLink': "//a[contains(@href,'manageDevices.admin.do')]",
    'InvReportsLink'      : "//a[contains(@href,'newReport.admin.do')]",
    'InvDeviceRegLink'    : "//a[contains(@href,'deviceRegistration.admin.do')]",

    # SYSTEM ALERTS menu
    'SysAlertsEventsLink'    : "//a[contains(@href,'sysevents.admin.do')]",
    'SysAlertsReportsLink'   : "//a[contains(@href,'systemAlertsReports.admin.do')]",
    'SysAlertsPropertiesLink': "//a[contains(@href,'systemAlertsProperty.admin.do')]",

    # PROVISIONING menu
    'ProvConfigTmplsLink'    : "//a[contains(@href,'configTemplates.admin.do')]",
    'ProvConfigUpgradeLink'  : "//a[contains(@href,'configUpdate.admin.do')]",
    'ProvFactoryResetLink'   : "//a[contains(@href,'setfactory.admin.do')]",
    'ProvZdCloningLink'      : "//a[contains(@href,'clone.admin.do')]",
    'ProvManageZdConfigsLink': "//a[contains(@href,'manageConfigs.admin.do')]",
    'ProvFirmwareUpgradeLink': "//a[contains(@href,'firmwareUpgrade.admin.do')]",
    'ProvRebootLink'         : "//a[contains(@href,'reboot.admin.do')]",
    'ProvManageFirmwareFilesLink': "//a[contains(@href,'manageFiles.admin.do')]",
    'ProvFirmwareStatusLink': "//a[contains(@href,'firmwareStatus.admin.do')]",

    # ADMINISTRATION menu
    'AdminAuditLogLink'   : "//a[contains(@href,'auditLog.admin.do')]",
    'AdminLicenseLink'    : "//a[contains(@href,'license.admin.do')]",
    'AdminSysSettingsLink': "//a[contains(@href,'systemSettings.admin.do')]",
    'AdminUsersLink'      : "//a[contains(@href,'users.admin.do')]",
    'AdminGroupMgmtLink'  : "//a[contains(@href,'groupManagement.admin.do')]",
    'AdminSslCertsLink'   : "//a[contains(@href,'sslCertificate.admin.do')]",
    'AdminSupportLink'    : "//a[contains(@href,'support.admin.do')]",
    'AdminManagedDeviceAssignmentLink': "//a[contains(@href,'deviceGroupManagement.admin.do')]",
    'AdminAssignGroupOwnwersLink': "//a[contains(@href,'userGroupManagement.admin.do')]",
    'FlexMasterVersion': "//span[@id='flexMasterVersion']",

    # Status Area on FM GUI
    'StatusArea': "//div[@id='statusarea']",


    # DASHBOARD, db: dashboard
    # Device Firmware pane
    'DeviceFirmware': {
        'self': "//td/div[.//span='Active Firmware'][./table[@id='firmwaredetailtable']]",
        'Tbl' : {
            'self'    : "//table[@id='firmwaretableList']",
            'LinkTmpl': "/tbody/tr[%s]//span[contains(@class, 'Number')]"
          },
        'RefreshBtn': "//img[contains(@title, 'Refresh')]",
        'Nav'       : "//table[@id='firmwarepageContrl']"
      },


    # INVENTORY > Manage Devices
    'ManageDevice': {
        'self'      : "//td[@id='textView']", #"//div[@id='mainTabContainer']",
        'RefreshBtn': "//img[contains(@title, 'Refresh')]",

        # tabs, click to switch
        'SavedGroupsTab': "//span[contains(., 'Saved Views')]",
        'NewSearchTab'  : "//span[contains(., 'New Search')]",
        'SearchBoxTxt'  : "//input[@id='Device_SearchBox']",
      },

    # INVENTORY > Manage Devices > Saved Groups tab
    'SavedGroups_LoadingIndicator': "//img[@id='manageDevicesImgLoad']",
    'SavedGroups' : {
        'self': "//div[contains(@label, 'Saved Views')]",
        'Ctrl': {
            'self': "//div[@class='scrollSection']",
            'SelectGroupCb'   : "//span[contains(@class,'dojoComboBoxOuter')]",
            'GroupDetailsLink': "//span[@id='viewGroupDetailsLink']", # toggle
            'GroupDetailsInfo': "//div[@id='detailsParagraph']"
          },

        'Tbl': {
            'self': "//table[@widgetid='DeviceEntityTable']",

            # click this will open the device view window
            'DeviceViewLinkTmpl': "/tr[%s]//div[@class='deviceLink']/span"
          },
        'Nav': "//td[@class='pageSelecter']",
      },

    'DeviceReg': {
        'self': "//div[@id='deviceregistrationmainTabContainer']",
        'RefreshBtn': "//img[contains(@title, 'Refresh')]",

        'RegStatusTab': "//span[contains(., 'Registration Status')]",
        'AutoCfgSetupTab'  : "//span[contains(., 'Auto Configuration Setup')]",
    },

    # Inventory > Device Registration > Registration Status
    'RegStatus': {
        'self': "",

        'EditLink': "//a[contains(.,'Edit')]",
        'Tbl': "//table[@widgetid='InventoryEntityTable']",
        'Nav': "//td[contains(preceding-sibling::td, 'Total inventory count')]/table",

        'UpDvInvFileLink': "//div[@id='uploadInventoryLink']",
        'SaveInvLink': "//a[contains(., 'Save This Inventory as XLS')]",
        'PreRegDataRd': "//input[@id='format.autoconfig']",
        'ManufactDataRd': "//input[@id='format.manufact']",
        'SelectInvFileTxt': "//input[@id='feederSample']",

        'RefreshBtn': "//img[@id='refreshEntity' and contains(@title, 'Refresh')]",
        'UploadOkBtn': "//input[@id='cmdupload']",
        'UploadCancelBtn': "//input[@id='cancel-ap']",

        'InvStatusDjCb': "//div[@id='inventoryStatusArea']/span",
        'CommentTxt': "//textarea[@id='commentsTextArea']",
        # It seems there is a typo mistake of developer in EditStatusOkBtn.
        # It should be "id" instead of "d". This minor problem has been fixed in 8.1.0.0.2
        'EditStatusOkBtn': "//div[@id='changePermission']//input[@id='okEditStatus']",
        'EditStatusCancelBtn': "//div[@id='changePermission']//input[@id='cancelEditStatus']",

        #define Registered column
        'RegCol': "//td[4]",
        'AutoCfgCol': "//td[6]",

        'SearchBoxTxt': "//input[@id='Inventory_SearchBox']",
        'CloseSearchImg': "//img[@id='Inventory_CleanSearchBox']",
    },

    # # Inventory > Device Registration > Auto Configuration Setup
    'AutoCfgSetup': {
        'self': "", #"//div[contains(@label, 'Auto Configuration Setup')]",

        'ViewLink': "//span[contains(., 'View')]",
        'StopLink': "//span[contains(., 'Stop')]",
        'RestartLink': "//span[contains(., 'Restart')]",

        'CfgNameTxt': "//input[@id='autoConfigautoConfigName']",
        'DeviceGroupCb': "//td[contains(preceding-sibling::th, 'Device View')]//span",
        'ModelTypeCb': "//td[contains(preceding-sibling::th, 'Model Type')]//span",
        'CfgTemplateCb': "//td[contains(preceding-sibling::th, 'Configuration Template')]//span",

        'CreateRuleLink': "//div[@id='autoConfigcreareNew']/span",
        'Tbl': "//table[@id='autoConfigtableList']",
        #'Nav': "//tr/td/div[@align='right']",
        'Nav': "//table[@id='autoConfigpageContrl']",

        # 'RefreshBtn': "//img[contains(@title, 'Refresh')]",
        'SaveBtn': "//input[@id='autoConfigb_save']",
        'CancelBtn': "//input[@id='autoConfigb_cancel']",

        # Detail table of each rule
        'RuleDetailTbl': "//table[@id='autoConfigTaskDetailtableList']",
        'RuleDetailNav': "//div[@id='autoConfigTaskDetailpageContrl']",

    },

    'Reports_RefreshLink': "//img[contains(@title, 'Refresh')]",
    # INVENTORY > Reports page/pane
    'Reports': {
        'self'       : "//div/fieldset",
        'Tbl'        : "//div/table[@class='dashboard']", # where results are displayed
        'Nav'        : "//tr[contains(td, 'Number of devices')]/td/table",
      },

    # ADMINISTRATION > Group Management
    'GroupMgmt': {
        'self'        : "",
        'GroupsTab'   : "//span[contains(.,'Groups')]",
        'InvStatusTab': "//span[contains(.,'Inventory Status')]"
      },

    # ADMINISTRATION > Group/View Management > Groups tab pane
    'Groups': {
        'self': "",
        'Tbl' : {
            'self': "//table[@widgetid='ViewEntityTable']",
            'DeleteLinkTmpl': "//tr[%s]//a[contains(.,'Delete')]"
          },

        'Nav'    : "//td[contains(preceding-sibling::td, 'Number of Groups')]/div",
        'TotalNo': "//td[contains(., 'Number of Groups')]/label[contains(@id, 'Value')]"
      },

    # PROVISIONINGI > Configuration Templates

    'ConfTemplates': {
        'self': "//td[@id='provisiontemp-main']",
        'Status': {
            'self': "//div[@id='div-templatelist']",
            'Tbl': {
                'self': "//table[@id='Templatelist']",
                # We only need define Edit, Delete items. The function iterVTableRows
                # will return a locator pointing to these items.
                'EditLinkTmpl': "//a[contains(.,'Edit')]",
                'DeleteLinkTmpl': "//a[contains(.,'Delete')]"
            },
            'Nav': "//td[contains(preceding-sibling::td, 'Number of templates')]/table"
        },
        'GeneralConf': {
            'self': "",
            'GeneralConfTbl': "//fieldset[@id='config-new']//table",
            'TemplateNameTxt': "//input[@id='templatename']",
            # Name of Product type
            'ProductTypeCb'     : "//select[@id='select-profilelist']",
            #List of configuration options
            'DvGeneralChkB'     : "//input[@id='group-0' and @value='device']",
            'InternetChkB'      : "//input[@id='group-1' and @value='Internet']",
            'WLANCommonChkB'    : "//input[@id='group-2' and @value='WLANCommon']",
            'Wireless_1ChkB'    : "//input[@id='group-3' and @value='HZ1']",
            'Wireless_2ChkB'    : "//input[@id='group-4' and @value='HZ2']",
            'Wireless_3ChkB'    : "//input[@id='group-5' and @value='HZ3']",
            'Wireless_4ChkB'    : "//input[@id='group-6' and @value='HZ4']",
            'Wireless_5ChkB'    : "//input[@id='group-7' and @value='HZ5']",
            'Wireless_6ChkB'    : "//input[@id='group-8' and @value='HZ6']",
            'Wireless_7ChkB'    : "//input[@id='group-9' and @value='HZ7']",
            'Wireless_8ChkB'    : "//input[@id='group-10' and @value='HZ8']",
            'MgmtChkB'          : "//input[@id='group-11' and @value='manage']",
            'DevRegSettingsChkB': "//input[@id='group-12' and @value='ACS']",
            'VLANSettingChkB'   : "//input[@id='group-13' and @value='VLAN']"
            # The other ones such as Internet, Wireless Common... will be defined later
        },

        # Configuration for each item option in detail
        # The locator of tiltle of each page, such as: Device General, Internet,...
        # and Configuration Parameters and Values
        'OptionTitle': "//span[@id='group-name']",
        # After click Save to save a new template, if any error happends, it will show this title
        'ResultTitle': "//span[@id='validate-result']",
        'CreateNewLink': "//div[@id='new-template']",

        'DvGeneralDet': {
            'self': "",
            # Device General item
            'DeviceGeneralTitle': "//span[@id='group-name' and contains(.,'Device General')]", # Title of this page
            # Device Name check box and input box
            'DeviceNameChk': "//input[@id='check-device.name']",
            'DeviceNameTxt': "//input[@id='device.name']",

            # Super User Name check box and input box
            'SuperUserNameChk': "//input[@id='check-device.SPloginname']",
            'SuperUserNameTxt': "//input[@id='device.SPloginname']",

            'SuperPasswordChk': "//input[@id='check-device.SPloginpwd']",
            'SuperPasswordTxt': "//input[@id='device.SPloginpwd']",
            'SuperCPasswordTxt': "//input[@id='c-device.SPloginpwd']", # confirm password input box
        },#'DvGeneralDet'

        'WLANCommon':{
            'self': "",
            #Wireless Mode
            'WModeChk': "//input[@id='check-WLANCommon.mode']",
            'WModeCb': "//select[@id='WLANCommon.mode']",

            #Channel
            'ChannelChk': "//input[@id='check-WLANCommon.channel']",
            'ChannelCb': "//select[@id='WLANCommon.channel']",

            #Country Code
            'CountryCodeChk': "//input[@id='check-WLANCommon.countrycode']",
            'CountryCodeCb': "//select[@id='WLANCommon.countrycode']",

            #Transmit Power
            'TxPowerChk': "//input[@id='check-WLANCommon.txpower']",
            'TxPowerCb': "//select[@id='WLANCommon.txpower']",

            #Transmit Power
            'ProtModeChk': "//input[@id='check-WLANCommon.protmode']",
            'DisabledRd': "//input[@id='WLANCommon.protmode.0']",
            'CTS-onlyRd': "//input[@id='WLANCommon.protmode.1']",
            'RTS-CTSRd': "//input[@id='WLANCommon.protmode.2']"
        },#WLANCommonDet

        'WLANDet':{
            #############Wireless 1################
            #Wireless 1 Availability
            'self': "",
            'WAvailChk': "//input[@id='check-HZ%s.wireless']",
            'WAvailERd': "//input[@id='HZ%s.wireless.0']",
            'WAvailDRd': "//input[@id='HZ%s.wireless.1']",

            #Wireless 1 Broadcast SSID
            'WBroadcastChk': "//input[@id='check-HZ%s.broadcast']",
            'WBroadcastERd': "//input[@id='HZ%s.broadcast.0']",
            'WBroadcastDRd': "//input[@id='HZ%s.broadcast.1']",

            #Wireless 1 Client Isolation
            'WIsolationChk': "//input[@id='check-HZ%s.isoloation']",
            'WIsolationERd': "//input[@id='HZ%s.isoloation.0']",
            'WIsolationDRd': "//input[@id='HZ%s.isoloation.1']",

            #Wireless 1 Name
            'WNameChk': "//input[@id='check-HZ%s.name']",
            'WNameTxt': "//input[@id='HZ%s.name']",

            #Wireless 1 SSID
            'WSSIDChk': "//input[@id='check-HZ%s.ssid']",
            'WSSIDTxt': "//input[@id='HZ%s.ssid']",

            #Wireless 1 Data Beacon Rate (DTIM)
            'WDTIMChk': "//input[@id='check-HZ%s.dtim']",
            'WDTIMTxt': "//input[@id='HZ%s.dtim']",
            #Valid value: (1, 255)
            'WDTIMErrMsg': "//label[@id='validate-HZ%s.dtim']",

            #Fragment Threshold: This item is removed out from FM MR1 version
            #'WFragThresChk': "//input[@id='check-HZ%s.fragment']",
            #'WFragThresTxt': "//input[@id='HZ%s.fragment']",
            # Valid: (256, 2346)
            #'WFragThresErrMsg': "//label[@id='validate-HZ%s.fragment']",

            #Wireless 1 RTS / CTS Threshold
            'WRTSCTSChk': "//input[@id='check-HZ%s.rtscts']",
            'WRTSCTSTxt': "//input[@id='HZ%s.rtscts']",
            # Valid: (256, 2346)
            'WRTSCTSErrMsg': "//label[@id='validate-HZ%s.rtscts']",

            #Wireless 1 Rate Limiting
            'WRateLimitingChk': "//input[@id='check-HZ%s.rate.set']",
            'WRateLimitingERd': "//input[@id='HZ%s.rate.set.0']",
            'WRateLimitingDRd': "//input[@id='HZ%s.rate.set.1']",

            #Wireless 1 Downlink Rate
            'WDownlinkChk': "//input[@id='check-HZ%s.rate.downlink']",
            'WDownlinkCb': "//select[@id='HZ%s.rate.downlink']",

            #Wireless 1 Uplink Rate
            'WUplinkChk': "//input[@id='check-HZ%s.rate.uplink']",
            'WUplinkCb': "//select[@id='HZ%s.rate.uplink']",

            #Wireless 1 Encryption Method
            'WEncryptChk': "//input[@id='check-HZ%s.securitymode']",
            'WEncryptCb': "//select[@id='HZ%s.securitymode']",

            #Detail for WEP mode
            'WWEPModeChk': "//input[@id='check-HZ%s.wepmode']",
            'WOpenRd': "//input[@id='HZ%s.wepmode.0']",
            'WSharedKeyRd': "//input[@id='HZ%s.wepmode.1']",
            'WAutoRd': "//input[@id='HZ%s.wepmode.2']",

            #Wireless 1 Encryption Strength
            'WEncryptLenChk': "//input[@id='check-HZ%s.encryptlength']",
            'WEncryptLenCb': "//select[@id='HZ%s.encryptlength']", #13, 26, 5, 10

            #Wireless 1 WEP Key Index
            'WKeyIndexChk': "//input[@id='check-HZ%s.keyindex']",
            'WKeyIndexCb': "//select[@id='HZ%s.keyindex']", #1,2,3,4

            #Wireless 1 WEP Key
            #This one is a special item. There are four keys (1, 2, 3, 4). Accordingly each key, locator of textbox
            #password and cpassword will be different. In this case, we need to use attribute "@style"
            #to filter the invisible items. More detail:
            #Criteria 1: //tr[contains(@id, 'wepkey') and not(contains(@style, 'display: none'))]: To filter invisible "WEP Key" rows.
            # Criteria 2: //input[contains(@id,'check-HZ%s.wepkey')]: To point to the expected item in the visible row.
            'WWEPKeyPassChk': "//tr[contains(@id, 'wepkey') and not(contains(@style, 'display: none'))]//input[contains(@id,'check-HZ%s.wepkey')]",
            'WWEPKeyPassTxt': "//tr[contains(@id, 'wepkey') and not(contains(@style, 'display: none'))]//input[@type='password' and contains(@id,'HZ%s.wepkey') and not(contains(@id,'c-'))]",
            'WCWEPKeyPassTxt': "//tr[contains(@id, 'wepkey') and not(contains(@style, 'display: none'))]//input[@type='password' and contains(@id,'c-HZ%s.wepkey')]",
            #'WWEPKeyPassTxt': "//input[@id='HZ%s.wepkey.%s']",
            #'WCWEPKeyPassTxt': "//input[@id='c-HZ%s.wepkey.%s']",

            #Wireless 1 WPA Version
            'WWPAVerChk': "//input[@id='check-HZ%s.wpaversion']",
            'WWPAVer1Rd': "//input[@id='HZ%s.wpaversion.0']", #WPA
            'WWPAVer2Rd': "//input[@id='HZ%s.wpaversion.1']", #WPA2
            'WWPAVerAutoRd': "//input[@id='HZ%s.wpaversion.2']", #Auto

            #Wireless 1 WPA Algorithm:
            #7942 has only AES and Auto. Its locators for these two items are different from other model
            'WWPAAlgorithmChk': "//input[@id='check-HZ%s.wpamode']",
            'WWPATKIPRd': "//input[@name='HZ%s.wpamode' and @value='tkip']", #TKIP
            'WWPAAESRd': "//input[@name='HZ%s.wpamode' and @value='aes']", #AES
            'WWPAAutoRd': "//input[@name='HZ%s.wpamode' and @value='auto']", #Auto

            #Wireless 1 Authentication:
            'WAuthChk'     : "//input[@id='check-HZ%s.wpa-auth']",
            'WAuthPSKRd'   : "//input[@id='HZ%s.wpa-auth.0']", #TKIP
            'WAuth802.1xRd': "//input[@id='HZ%s.wpa-auth.1']", #WPA2
            'WAuthAutoRd'  : "//input[@id='HZ%s.wpa-auth.2']",

            #Wireless 1 PSK Passphrase:
            'WPassphraseChk': "//input[@id='check-HZ%s.wpapassphrase']",
            'WPassphraseTxt': "//input[@id='HZ%s.wpapassphrase']",
            'WCPassphraseTxt': "//input[@id='c-HZ%s.wpapassphrase']",

            #Wireless 1 Radius NAS-ID
            'WRadiusChk': "//input[@id='check-HZ%s.wpa_nas_id']",
            'WRadiusTxt': "//input[@id='HZ%s.wpa_nas_id']",

            #Wireless 1 Authentication IP address
            'WAuthIPChk': "//input[@id='check-HZ%s.auth-ip']",
            'WAuthIP1Txt': "//input[@id='HZ%s.auth-ip.1']",
            'WAuthIP2Txt': "//input[@id='HZ%s.auth-ip.2']",
            'WAuthIP3Txt': "//input[@id='HZ%s.auth-ip.3']",
            'WAuthIP4Txt': "//input[@id='HZ%s.auth-ip.4']",

            #Wireless 1 Authentication Port:
            'WAuthPortChk': "//input[@id='check-HZ%s.auth-port']",
            'WAuthPortTxt': "//input[@id='HZ%s.auth-port']",

            #Wireless 1 Authentication Server Secret:
            'WAuthSecretChk': "//input[@id='check-HZ%s.auth-secret']",
            'WAuthSecretTxt': "//input[@id='HZ%s.auth-secret']",
            'WCAuthSecretTxt': "//input[@id='c-HZ%s.auth-secret']",

            #Wireless 1 Accounting IP address:
            'WAcctIPChk': "//input[@id='check-HZ%s.acct-ip']",
            'WAcctIP1Txt': "//input[@id='HZ%s.acct-ip.1']",
            'WAcctIP2Txt': "//input[@id='HZ%s.acct-ip.2']",
            'WAcctIP3Txt': "//input[@id='HZ%s.acct-ip.3']",
            'WAcctIP4Txt': "//input[@id='HZ%s.acct-ip.4']",

            #Wireless 1 Accounting Port:
            'WAcctPortChk': "//input[@id='check-HZ%s.acct-port']",
            'WAcctPortTxt': "//input[@id='HZ%s.acct-port']",

            #Wireless 1 Accounting Server Secret:
            'WAcctSecretChk': "//input[@id='check-HZ%s.acct-secret']",
            'WAcctSecretTxt': "//input[@id='HZ%s.acct-secret']",
            'WCAcctSecretTxt': "//input[@id='c-HZ%s.acct-secret']",

        },#WLAN_Det

        # Items for Internet, Wireless Common, ... will be define later
        # Items for internet
        'Internet': {
            #################Internet #########################
            'self': "",
            #Gateway
            'GatewayChk': "//input[@id='check-Internet.gateway']",
            #%d: from 1 to 4
            'GatewaryTxtTmpl': "//input[@id='Internet.gateway.%d']",
            'Gateway1Txt': "//input[@id='Internet.gateway.1']",
            'Gateway2Txt': "//input[@id='Internet.gateway.2']",
            'Gateway3Txt': "//input[@id='Internet.gateway.3']",
            'Gateway4Txt': "//input[@id='Internet.gateway.4']",
            'GatewayErrMsg': "//label[@id='validate-Internet.gateway']",

            #DNS Server List
            'DNSChk': "//input[@id='check-Internet.DNS']",
            'DNSTxt': "//input[@id='Internet.DNS']",

            #NTP Server
            'NTPChk': "//input[@id='check-Internet.NTP']",
            'NTPTxt': "//input[@id='Internet.NTP']",

            # Internet Connection Type
            'ConnTypeChk': "//input[@id='check-device.connecttype']",
            'ConnTypeDynRd': "//input[@id='device.connecttype.0']",
            'ConnTypeStaticRd': "//input[@id='device.connecttype.1']",

            #IP Address
            'IPChk': "//input[@id='check-Internet.IP']",
            #%d: from 1 to 4
            'IPTxtTmpl': "//input[@id='Internet.IP.%d']",
            'IP1Txt': "//input[@id='Internet.IP.1']",
            'IP2Txt': "//input[@id='Internet.IP.2']",
            'IP3Txt': "//input[@id='Internet.IP.3']",
            'IP4Txt': "//input[@id='Internet.IP.4']",
            'IPErrMsg': "//label[@id='validate-Internet.IP']",

            #Mask
            'MaskChk': "//input[@id='check-Internet.MASK']",
            #%d: from 1 to 4
            'MaskTxtTmpl': "//input[@id='Internet.MASK.%d']",
            'Mask1Txt': "//input[@id='Internet.MASK.1']",
            'Mask2Txt': "//input[@id='Internet.MASK.2']",
            'Mask3Txt': "//input[@id='Internet.MASK.3']",
            'Mask4Txt': "//input[@id='Internet.MASK.4']",
            'MaskErrMsg': "//label[@id='validate-Internet.MASK']",
        },

        'Mgmt': {
            'self': "",
            'TelnetChk': "//input[@id='check-manage.telnet']",
            'TelnetERd': "//input[@id='manage.telnet.0']",
            'TelnetDRd': "//input[@id='manage.telnet.1']",

            'TelnetPortChk': "//input[@id='check-manage.telnetport']",
            'TelnetPortTxt'  : "//input[@id='manage.telnetport']",
            'TelnetErrMsg': "//label[@id='validate-manage.telnetport']",

            # SSH Radio options
            'SSHChk': "//input[@id='check-manage.ssh']",
            'SSHERd'  : "//input[@id='manage.ssh.0']",
            'SSHDRd'  : "//input[@id='manage.ssh.1']",

            'SSHPortChk': "//input[@id='check-manage.sshport']",
            'SSHPortTxt'  : "//input[@id='manage.sshport']",
            'SSHErrMsg': "//label[@id='validate-manage.sshport']",

            # HTTP Radio options
            'HTTPChk': "//input[@id='check-manage.http']",
            'HTTPERd'  : "//input[@id='manage.http.0']",
            'HTTPDRd'  : "//input[@id='manage.http.1')]",

            'HTTPPortChk': "//input[@id='check-manage.httpport']",
            'HTTPPortTxt'  : "//input[@id='manage.httpport']",
            'HTTPErrMsg': "//label[@id='validate-manage.httpport']",

            # HTTPS Radio options
            'HTTPSChk': "//input[@id='check-manage.ssl']",
            'HTTPSERd'  : "//input[@id='manage.ssl.0']",
            'HTTPSDRd'  : "//input[@id='manage.ssl.1']",

            'HTTPSPortChk': "//input[@id='check-manage.sslport']",
            'HTTPSPortTxt'  : "//input[@id='manage.sslport']",
            'HTTPSErrMsg': "//label[@id='validate-manage.sslport']",

            # Log Server info
            'SystemLogChk': "//input[@id='check-manage.logaccess']",
            'SystemLogERd': "//input[@id='manage.logaccess.0']",
            'SystemLogDRd': "//input[@id='manage.logaccess.1']",
            #%d: from 1 to 4
            'LogSrvChk': "//input[@id='check-manage.logip']",
            'LogSrvIPTmpl': "//input[@id='manage.logip.%d']",
            'LogSrvIP1Txt': "//input[@id='manage.logip.1']",
            'LogSrvIP2Txt': "//input[@id='manage.logip.2']",
            'LogSrvIP3Txt': "//input[@id='manage.logip.3']",
            'LogSrvIP4Txt': "//input[@id='manage.logip.4']",
            'LogSrvIPErrMsg': "//label[@id='validate-manage.logip']",

            'LogSrvPortChk': "//input[@id='check-manage.logport']",
            'LogSrvPortTxt'  : "//input[@id='manage.logport']",
            'LogSrvIPErrMsg': "//label[@id='validate-manage.logip']",
            'LogSrvPortErrMsg': "//label[@id='validate-manage.logport']",

            #'AUTORd'      : "//input[@id='radio_rmm_auto')]",
            #'FlexMasterRd': "//input[@id='radio_rmm_tr069')]",
            #'SNMPRd'      : "//input[@id='radio_rmm_snmp')]",
        },

        'VLANSetting': {
            'self': "",
            'VLANIdTmpl': "//table[contains(@id,'vlan_tableList')]//tr[%d]//input[@class='vlanid']",
            'VLANMgmgIdTxt': "//table[contains(@id,'vlan_tableList')]//tr[1]//input[@class='vlanid']",
            'VLANTunelIdTxt': "//table[contains(@id,'vlan_tableList')]//tr[2]//input[@class='vlanid']",
            'VLANErrMsg': "//span[@id='vlan-validation']",
        },

        'BackBtn': "//input[@id='backWizard']",
        'CancelBtn': "//input[@id='cancel-ap']",
        # Save and Next buttion has the same @id so we differentiate them by @value attribute
        'NextBtn': "//input[@id='nextWizard'and @value='Next']",
        'SaveBtn': "//input[@id='nextWizard'and @value='Save']"
    },

    'SelectDevice': { # NOTE: backware compatible for CfgUpgrade
        'self': "",
        'SelectDevicesTab': "//span[contains(.,'Select Devices')]",

        'GroupCb': "//div[contains(.,'Select a view of devices')]/span",

        'GroupTbl': "//table[contains(@widgetid,'EntityTable')]",
        'GroupNav': "//table[preceding-sibling::table[contains(@widgetid,'EntityTable')]]//td[contains(preceding-sibling::td, 'Number of devices')]/table",

        'DeviceTbl': {
            'self': "//table[contains(@widgetid,'SelectEntityTable')]",
            'DeviceChkTmpl': "//tr[%s]//input[@type='checkbox']",
        },
        'DeviceNav': "//table[preceding-sibling::table[contains(@widgetid,'SelectEntityTable')]]//td[contains(preceding-sibling::td, 'Number of devices')]/table",
    },

    'CfgUpgrade': {
        'self': "",
        'RefreshBtn': "//img[@id='cmdrefresh']",
        'Tbl': {
            'self': "//table[@id='tasklist']",
            'ViewLinkTmpl': "//tr[%s]//a[contains(.,'%s')]",
            'CancelLinkTmpl': "//tr[%s]//a[contains(.,'Cancel')]",
        },
        'Nav': "//td[contains(preceding-sibling::td, 'Number of tasks')]/table",
        'NewTaskLink': "//span[contains(.,'Create a task')]",

        'TemplateCb': "//select[@id='template']",
        'TaskNameTxt': "//input[@id='taskname']",

        'ScheduleRadio': "//input[@id='rdoschedule2']",
        'ScheduleDateTxt': "//span[@id='scheduledate']/input[@type='text']",
        'ScheduleTimeTxt': "//span[@id='scheduletime']/input[@type='text']",

        'SaveBtn': "//input[contains(@id,'-ok-ap')]",

        'DetailsTbl': "//table[@id='devicestatus']",
        # old 'DetailsNav': "//td/div[//img[@id='pdeviceDisabled']][preceding-sibling::div[@id='tb-detail']]",
        # new in FM 8.1.0.0.3:
        'DetailsNav': "//td[@class='pageSelecter'][.//img[@id='pdeviceDisabled']]",
    },

    'AuditLog': {
        'self': "",
        'LoadingImg': "//img[@id='AuditLogMail.loadImg']", # and not(contains(@style,'display: none'))
        'Tbl': "//table[@id='auditlogtableList']",
        'Nav': "//table[contains(@id, 'auditlogpageContrl')]",

        # Table detail for each audit type item
        'DetailTbl': "//table[@id='auditLogDetailList']",
        'DetailNav': "//td[preceding-sibling::td/span[@id='auditLogDetailTotalCount']]",
    },

    'TaskStatus':{
        'self': "//div[@dojoattachpoint='contentNode']",
        'LeftArrowImg': "//img[contains(@src,'imgArrow_left.gif')]",
        'RightArrowImg': "//img[contains(@src,'img_Arrow_right.gif')]",
        'Tbl': "//tbody[@dojoattachpoint='tableBodyNode']",
    },
}


Constants = {
    # Successful when containing these words
    # New successful messages should be added in order to help the function getStatus()
    # operating correctly
    'StatusAreaSuccessfulIndicators': ['successful'],

    # Indicator of opening status of an optional pane
    # Add more keywords here if new type of messages is encountered
    # These optional panes are found at: Inventory > Manage Devices >
    #   New Search > Save Search,
    #   Saved Groups > Group Details
    'OpeningIndicators': ['Hide'],

    'MainWindowName'      : '',
    'DeviceViewWindowName': 'Support',

    # Constants for Configuration Provisioning page. These keys are options of creating new template page.
    # They will be used to compare in the function. FlexMaster.createNewConfTemplate().
    'PRO_DEV_GENERAL_TITLE': 'Device General',
    'PRO_INTERNET_TITLE': 'Internet',
    'PRO_WLAN_COMMON_TITLE': 'Wireless Common',
    'PRO_WLAN_1_TITLE': 'Wireless 1',
    'PRO_WLAN_2_TITLE': 'Wireless 2',
    'PRO_WLAN_3_TITLE': 'Wireless 3',
    'PRO_WLAN_4_TITLE': 'Wireless 4',
    'PRO_WLAN_5_TITLE': 'Wireless 5',
    'PRO_WLAN_6_TITLE': 'Wireless 6',
    'PRO_WLAN_7_TITLE': 'Wireless 7',
    'PRO_WLAN_8_TITLE': 'Wireless 8',
    'PRO_MGMT_TITLE': 'Management',
    'PRO_DEV_REG_SETTINGS_TITLE': 'Device Registration Settings',
    'PRO_VLAN_TITLE': 'VLAN Setting',
    # It is the tiltle on the last page which shows summary for your selection.
    'PRO_SUMMARY_TITLE': 'Configuration Parameters and Values',
    'PRO_WARNING_TITLE': 'Select the configuration options you would like to modify.',
    'PRO_ERROR_TITLE'  : 'No parameter checked',

    # WARNING:
    # This one is order list. Whenever you want to add a new element, please
    # add the new one at the end of the list. Otherwise, it may cause error
    # for other scripts
    'TaskStatuses': ['started', 'incomplete', 'success', 'failed', 'not started yet',
                     'canceled', 'expired',],
    'FmLoginIdleTime': 15 * 60, # const (in secs)
    # define accept image and denied/close image
    'TickImg': "//img[contains(@src,'tick.png')]",
    'CrossImg': "//img[contains(@src,'cross.png')]",

    # Define error message for Auto Config Rule
    'AutoCfgNotMatchModelMsg':    'Model & Template are not matched',
    'AutoCfgNotFillAllFieldsMsg': 'Please fill in all fields.',
    # this message is to inform when we search a device from Inventory > Manage Devices
    # or Inventory > Device Registration page
    'NotFoundDeviceMsg': 'Inventory list is empty',

  }

