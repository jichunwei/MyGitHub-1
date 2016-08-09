# Defining the dictionary of FM Device View locators
Locators = {
    # login info is disabled here
    'LoginUsernameTxt': "",
    'LoginPasswordTxt': "",
    'LoginBtn'        : "",
    'LogoutBtn'       : "//a[contains(@href,'j_acegi_logout')]",

    #Device View tabs
    'SummaryLink'    : "//a[contains(.,'Summary')]",
    'DetailsLink'    : "//a[contains(.,'Details')]",
    'DiagnosticsLink': "//a[contains(.,'Diagnostics')]",

    # Sub menus of Details tab
    'DeviceLink'          : "//a[contains(@href,'device.support.do')]",
    'InternetWANLink'     : "//a[contains(@href,'wan.support.do')]",
    'WirelessLink'        : "//a[contains(@href,'wlan.support.do')]",
    'WirelessLinkRd2'     : "//a[contains(@href,'wlan.2.support.do')]",
    'RateLimitingLink'    : "//a[contains(@href,'rateLimiting.support.do')]",
    'AssociatedDeviceLink': "//a[contains(@href,'associatedDevice.support.do')]",
    'DeviceEventLink'     : "//a[contains(@href,'deviceevent.support.do')]",
    'VLANLink'            : "//a[contains(@href,'vlan.support.do')]",
    'ManagementLink'      : "//a[contains(@href,'management.support.do')]",

    # Diagnostics menus
    'DiagPingTestLink' : "//a[contains(@href,'ping.support.do')]",
    'DiagDeviceLogLink': "//a[contains(@href,'log.support.do')]",

    #'StatusArea_Tbl' : "//div[@class='MsgWindowClip']//table[contains(., 'task:') or contains(.,'Task:')]",
    'StatusArea_Tbl' : "//div[@class='MsgWindowClip'][contains(@style, 'top: 0px')]//table",
    'StatusArea_ShowLink' : "//a[contains(.,'Show Device Status')]",
}

