import time
import logging
#from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import RuckusAPSerial

from RuckusAutoTest.common.Ratutils import get_network_address

def getStation(station_ip_addr, station_list):
    """
    Find exactly station from station list using ip address in testbed
    """
    target_station = None
    for station in station_list:
        if station.get_ip_addr() == station_ip_addr:
            target_station = station
            break
    if not target_station:
        raise Exception("Station %s not found" % station_ip_addr)

    return target_station

def getWinsIpAddr(station_obj, subnet, get_ifname = False):
    """
    Find exactly ip address on the windows station that belongs to the specific subnet in testbed
    """
    win_sta_ip_addr = ""
    if_name = ""
    if_info = station_obj.get_if_info()
    logging.info(if_info)
    for key, value in if_info.iteritems():
        for item in value:
            network = get_network_address(item['addr'], item['mask'])
            if '.'.join(network.split('.')[:-1]) == '.'.join(subnet['network'].split('.')[:-1]):
                win_sta_ip_addr = item['addr']
                if_name = key
                break
        if win_sta_ip_addr:
            break
    if not get_ifname:
        return win_sta_ip_addr
    else:
        return win_sta_ip_addr, if_name

def getLinuxIpAddr(station_obj, subnet, get_ifname = False):
    """
    Find exactly ip address on the Linux station that belongs to the specific subnet in testbed
    """
    if type(subnet) == str:
        subnet = dict(network=subnet)
    linux_sta_ip_addr = ""
    linux_sta_if_name = ""
    if_info = station_obj.get_if_config()
    for key, value in if_info.iteritems():
        network = get_network_address(value['ip_addr'], value['mask'])
        if '.'.join(network.split('.')[:-1]) == '.'.join(subnet['network'].split('.')[:-1]):
            linux_sta_ip_addr = value['ip_addr']
            linux_sta_if_name = key
            break
    if not get_ifname:
        return linux_sta_ip_addr
    else:
        return linux_sta_ip_addr, linux_sta_if_name


def getTestbedActiveAP(testbed, ap_sym_name, ap_list, channel, wlan_if, announce_name='ActiveAP'):
    """
    Find an active AP object in testbed
    @ channel: If this value is null, AP should choose channel automatically. Otherwise AP is configured
    with channel 'channel'
    @ wlan_if: determines what interface that AP should use
    """
    ap_ip_addr = testbed.getAPIpAddrBySymName(ap_sym_name)

    active_ap = None
    for ap in ap_list:
        profile = ap.get_profile()
        if profile.lower() == 'ruckus05':
            if_info_tmp = ap.get_mgmt_ip_addr()
        else:
            if_info_tmp = ap.get_bridge_if_cfg()
        found = False
        for key, value in if_info_tmp.iteritems():
            if value.has_key('ip_addr'):
                if value['ip_addr'] == ap_ip_addr:
                    if testbed.dict_aps[ap_sym_name].has_key('use_serial'):
                        if isinstance(ap,RuckusAPSerial.RuckusAPSerial):
                            found=True
                            break
                    else:
                        if isinstance(ap, RuckusAP):
                            found = True
                            break
        if found:
            active_ap = ap
            logging.info('%s(%s) found in testbed with ip_addr=%s' %
                         (announce_name, ap_sym_name, ap_ip_addr))
            break
    if not active_ap:
        raise Exception("Active AP %s with ip_addr=%s not found in the testbed" %
                        (ap_sym_name, ap_ip_addr))

    # Change channels of wlan interfaces so that they are not channel 11
    if channel:
        active_ap.set_channel(wlan_if, channel)

    if wlan_if:
        logging.info("Up %s interface on the active AP %s" % (wlan_if, ap_ip_addr))
        active_ap.set_state(wlan_if, "up")
        time.sleep(5)

    return active_ap

def getADConfig(testbed, ad_sym_name, ad_list, announce_name="Active AD"):
    """
    Get configuration information of an adapter in testbed
    """
    ad_ip_addr = testbed.getAdIpAddrBySymName(ad_sym_name)

    ad_config = {}
    for ad_info in ad_list:
        if ad_info['ip_addr'] == ad_ip_addr:
            logging.info("%s(sym name=%s) found in the testbed with ip_addr=%s" %
                         (announce_name, ad_sym_name, ad_ip_addr))
            ad_config = ad_info
            break
    if not ad_config:
        raise Exception("%s(sym name=%s) with ip_addr=%s not found in the testbed" %
                        (announce_name, ad_sym_name, ad_ip_addr))
    return ad_config

def saveCurPortMatchingFilterStatus(ap_obj, eth_interface):
    #cur_port_match_status = ""
    cur_port_match_status = ap_obj.get_port_match_status(eth_interface)
    if cur_port_match_status:
        ap_obj.set_port_match_status('enable', eth_interface)
    logging.info("Remove all port match filters on the active AP")
    ap_obj.remove_port_matching_rule(eth_interface)

def saveToSValues(ap_obj, media):
    res = ap_obj.get_tos_values(True)
    cur_tos_classify_value = ""
    for key in res.keys():
        if key.lower() == media:
            cur_tos_classify_value = res[key]
            logging.debug("Current ToS classify value: %s" % cur_tos_classify_value)
            break
    return cur_tos_classify_value

