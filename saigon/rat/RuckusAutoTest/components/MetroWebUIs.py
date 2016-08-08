''' Metro WebUIs
This file inherits from APWebUI and override some of its functions (actually most of its functions)
to enable accesibilty to Metro's webUI.

'''
from RuckusAutoTest.components.APWebUI import APWebUI


class MF2211WebUI(APWebUI):
    resource_file = 'RuckusAutoTest.components.resources.MetroWebUIResource'
    def __init__ (self, selenium_mgr, browser_type, ip_addr, config, https = True):
        APWebUI.__init__(self, selenium_mgr, browser_type, ip_addr, config, https = True)


class MF7211WebUI(APWebUI):
    resource_file = 'RuckusAutoTest.components.resources.MetroWebUIResource'#add new resource file for Metro

    def __init__(self, selenium_mgr, browser_type, ip_addr, config, https = True):
        APWebUI.__init__(self, selenium_mgr, browser_type, ip_addr, config, https = True)

        self.STATUS_SYSTEM     = self.info['status_system_link']
        self.STATUS_WIRELESS   = self.info['status_wireless_link']
        self.STATUS_COMMON     = self.info['status_common']
        self.STATUS_WAN        = self.info['status_wan']
        self.STATUS_WLAN_1     = self.info['status_wlan1']
        self.STATUS_WLAN_2     = self.info['status_wlan2']
        self.CONFIG_SYSTEM     = self.info['config_system_link']
        self.CONFIG_WIRELESS   = self.info['config_wireless_link']
        self.CONFIG_COMMON     = self.info['config_common']
        self.CONFIG_WAN        = self.info['config_wan']
        self.CONFIG_WLAN_1     = self.info['config_wlan1']
        self.CONFIG_WLAN_2     = self.info['config_wlan2']
        self.CONFIG_WIZARD     = self.info['config_wizard_link']
        self.CONFIG_ACCESS_CONTROLS = self.info['config_acl_link']
        self.CONFIG_ACL_1      = self.info['acl_wlan1']
        self.CONFIG_ACL_2      = self.info['acl_wlan2']
        self.CONFIG_PORT_FWD   = self.info['config_port_fwd_link']