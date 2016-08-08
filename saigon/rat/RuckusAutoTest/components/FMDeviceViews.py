''' FM DeviceView WebUIs '''
from RuckusAutoTest.components.FMDeviceView import FMDeviceView


class ZF2925FMDV(FMDeviceView):
    resource_file = None
    resource = None


class ZF2942FMDV(FMDeviceView):
    resource_file = None
    resource = None


class ZF7942FMDV(FMDeviceView):
    resource_file = None
    resource = None

class ZF7343FMDV(FMDeviceView):
    resource_file = None
    resource = None

class ZF2741FMDV(FMDeviceView):
    resource_file = None
    resource = None


class ZF7962FMDV(FMDeviceView):
    resource_file = None
    resource = None

    def _init_navigation_map(self):
        FMDeviceView._init_navigation_map(self)
        # update menu 5G for this model
        self.DETAILS_WIRELESS_RD_2 = self.info['WirelessLinkRd2']


class VF7811FMDV(FMDeviceView):
    resource_file = None
    resource = None
