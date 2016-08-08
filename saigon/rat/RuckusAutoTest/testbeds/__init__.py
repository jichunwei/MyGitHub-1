
#
# add testbeds here so python 'import *' works properly!
#

import sys

if sys.platform == "win32":
    __all__ = [
        'AP',
        'AP_ATT',
        'AP_IPTV',
        'AP_PC_Conducted',
        'AP_Single_Station',
        'AP_Stations',
        'SimplifiedFM_Stations',
        'ZD_Scaling',
        'ZD_SM',
        'ZD_Stations',
        'ZD_Stations_IPV6',
        'ZD_Port_Base_Vlan',
        'ZD_Voice',
        'CPE_Stations',
    ]

else:
    __all__ = [
        'AP',
        'AP_ATT',
        'AP_IPTV',
        'AP_PC_Conducted',
    ]
