''' AP WebUIs '''
from RuckusAutoTest.components.APWebUI import APWebUI


class ZF2925WebUI(APWebUI):
    resource_file = None
    resource = None


class ZF2942WebUI(APWebUI):
    resource_file = None
    resource = None


class ZF7942WebUI(APWebUI):
    resource_file = None
    resource = None


class ZF2741WebUI(APWebUI):
    resource_file = None
    resource = None
class ZF7363WebUI(APWebUI):
    resource_file = None
    resource = None

class ZF7962WebUI(APWebUI):
    resource_file = None
    resource = None

    def _init_navigation_map(self):
        APWebUI._init_navigation_map(self)
        # update menu 5G for this model
        self.CONFIG_WIRELESS_5G = self.info['ConfigWirelessLink_5G']


class VF7811WebUI(APWebUI):
    resource_file = None
    resource = None

    status_device_ths = [
        'name', 'mac', 'serial', 'firmware', 'uptime', 'cur_time', 'protection',
    ]

