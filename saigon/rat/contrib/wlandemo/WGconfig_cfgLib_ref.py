import defaultWlanConfigParams as DWCFG

from RuckusAutoTest.components.lib.zd import wlan_groups_zd as WGS
from RuckusAutoTest.components.lib.zd import wlan_zd as WLN
from RuckusAutoTest.components.lib.zd import access_points_zd as APX

def get_ap_mac_list(zd):
    mac_list = [ap_info['mac'] for ap_info in zd.get_all_ap_info()]

    return mac_list


def get_ap_xs_info(zd):
    ap_xs_list = [dict(mac = ap['mac'], model = ap['model'], radio = get_ap_radio_type(ap['model'])) \
                  for ap in zd.get_all_ap_info()]

    return ap_xs_list


def get_ap_radio_type(ap_model):
    if ap_model in ['zf7962', 'zf7762']:
        return ['ng', 'na']

    elif ap_model in ['zf7942', ]:
        return ['ng']

    return ['bg']


def update_ap_xs_info(zd, apXs, description, wgs_name):
    ap_rp = {}

    for radio in apXs['radio']:
        ap_rp[radio] = dict(wlangroups = wgs_name)

    APX.cfg_wlan_groups_by_mac_addr(zd, apXs['mac'], ap_rp, description)

    ap_xs_info = APX.get_cfg_info_by_mac_addr(zd, apXs['mac'])

    return ap_xs_info


def create_wlans(zd, mytb):
    for wlan_id in mytb['wlans']:
        try:
            wlan_cfg = DWCFG.get_cfg(wlan_id)
            WLN.create_wlan(zd, wlan_cfg)
            print "Wlan %s [ssid %s] created" % (wlan_id, wlan_cfg['ssid'])

        except Exception, e:
            print "WlanConfig named %s cannot be created:\n%s" % (wlan_id, e.message)


def create_wlan_group(zd, mytb):
    wlan_cfg = DWCFG.get_cfg(mytb['wlans'][0])
    WGS.create_wlan_group(zd, mytb['wgs_name'], wlan_cfg['ssid'])


def create_multi_wlan_groups(zd, mytb):
    #wlan_cfg = DWCFG.get_cfg(mytb['wlans'][3])
    ssid_list = get_ssid_list(zd, mytb)
    WGS.create_multi_wlan_groups(zd, mytb['wgs_name'], ssid_list, num_of_wgs = 2, description = 'automationisfuntool', pause = 1.0)


def align_wlan_group_sn_wlan(zd, mytb):
    ssid_list = get_ssid_list(zd, mytb)
    #WGS.cfg_wlan_group_members(zd, mytb['wgs_name'], ssid_list, True)
    # no WLAN belong to Default WlanGrup
    WGS.cfg_wlan_group_members(zd, 'Default', ssid_list, False)


#put all configured into a list
def get_wlan_groups_list(zd):
    wgs_list = WGS.get_wlan_groups_list(zd)

    return wgs_list


def get_ssid_list(zd, mytb):
    ssid_list = []
    for wlan_id in mytb['wlans']:
        wlan_cfg = DWCFG.get_cfg(wlan_id)
        ssid_list.append(wlan_cfg['ssid'])

    return ssid_list


def remove_wlan_config(zd):
    WGS.remove_wlan_groups(zd, get_ap_mac_list(zd))
    zd.remove_all_cfg()

