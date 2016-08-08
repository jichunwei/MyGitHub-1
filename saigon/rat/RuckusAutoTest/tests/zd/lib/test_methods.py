import logging
import time
import os
import random

def touch_ssid(ssid):
    if os.environ.has_key('RAT_SSID_SUFFIX'):
        new_ssid = ssid + '-' + os.environ['RAT_SSID_SUFFIX']
    else:
        new_ssid = "%s-%06d" % (ssid, random.randrange(1, 999999))
    return new_ssid

def assoc_station_with_ssid(target_station, wlan_cfg, check_status_timeout, break_time = 2):
    logging.info("Configure a WLAN with SSID %s on the target station %s"
                % (wlan_cfg['ssid'], target_station.get_ip_addr()))
    target_station.cfg_wlan(wlan_cfg)
    return check_station_is_connected_to_wlan(target_station, check_status_timeout, break_time)

def check_station_is_connected_to_wlan(target_station, check_status_timeout, break_time = 2, restart_cnt = 15):
    logging.info("Check association status of the target station %s" % target_station.get_ip_addr())
    start_time = time.time()
    while True:
        if target_station.get_current_status() == "connected":
            break
        restart_cnt -= 1
        if (restart_cnt == 0):
            try:
                target_station.do_cmd('restart_adapter')
            except Exception, e:
                logging.debug("[STA restart_adapter] %s" % e.message)
        time.sleep(break_time)
        if time.time() - start_time > check_status_timeout:
            return "The station %s didn't associate to the wireless network after %d seconds" % \
                   (target_station.get_ip_addr(), check_status_timeout)
    return None

def renew_wifi_ip_address(target_station, check_status_timeout, breaktime = 2):
    logging.info("Renew IP address of the wireless adapter on the target station")
    target_station.renew_wifi_ip_address()

    logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" %
        target_station.get_ip_addr())
    start_time = time.time()
    sta_wifi_ip_addr = None
    sta_wifi_mac_addr = None
    while time.time() - start_time < check_status_timeout:
        sta_wifi_ip_addr, sta_wifi_mac_addr = target_station.get_wifi_addresses()
        if sta_wifi_mac_addr and sta_wifi_ip_addr and not bogus_ip_address(sta_wifi_ip_addr):
            break
        time.sleep(breaktime)
    logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
    if not sta_wifi_mac_addr:
        msg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
            target_station.get_ip_addr()
        return(False, None, msg)
    if not sta_wifi_ip_addr:
        msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
            target_station.get_ip_addr()
        return(False, None, msg)
    if bogus_ip_address(sta_wifi_ip_addr):
        msg = "The target station %s could not get IP address from DHCP server" % \
            target_station.get_ip_addr()
        return (False, "FAIL", msg)
    return (True, sta_wifi_ip_addr, sta_wifi_mac_addr)

def bogus_ip_address(ip_addr):
    if ip_addr == "0.0.0.0" or ip_addr.startswith("169.254"):
        return True
    else:
        return False

# remove_wlan_on_non_active_ap(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])
def remove_wlan_on_non_active_ap(active_ap, wlan_ssid, aplist):
    # Remove the WLAN on the non-active APs and verify the status on the active AP
    for ap in aplist:
        if ap is not active_ap:
            # it takes time to push wlan to all APs in ZD's network; let's verify_wlan() is down
            cntdown = 1
            while cntdown <= 10:
                logging.info("Remove all WLAN on non-active AP [%s %s] [try #%d]" % (ap.get_base_mac(), ap.ip_addr, cntdown))
                ap.remove_all_wlan()
                if not ap.verify_wlan(): break
                cntdown += 1
                time.sleep(0.5)

def get_active_client_by_mac_addr(sta_wifi_mac_addr, zd):
    for client_info in zd.get_active_client_list():
        logging.debug("Found info of a station: %s" % client_info)
        if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
            return client_info
    return None

def verify_zd_client_is_unauthorized(zd, sta_wifi_ip_addr, sta_wifi_mac_addr, check_status_timeout):
    exp_client_info = {"ip": sta_wifi_ip_addr, "status": "Unauthorized"}
    return verify_zd_client_status(zd, sta_wifi_mac_addr, exp_client_info, check_status_timeout)

def verify_zd_client_is_authorized(zd, sta_wifi_ip_addr, sta_wifi_mac_addr, check_status_timeout):
    exp_client_info = {"ip": sta_wifi_ip_addr, "status": "Authorized"}
    return verify_zd_client_status(zd, sta_wifi_mac_addr, exp_client_info, check_status_timeout)

def verify_zd_client_status(zd, client_mac, exp_client_info, check_status_timeout):
    """
    @param zd: the ZoneDirector object
    @param client_mac: MAC address of the wireless client that is being looked for
    @param exp_client_info: a dictionary of keys and values that are being matched with the
                            similar dictionary obtained from the ZD's active client table
    @param check_status_timeout: maximum allowed time to verify

    @return a tuple with message explains the problem together with the information found
    """
    logging.info("Verify information of the target station with MAC [%s] shown on the Zone Director" % client_mac)
    timed_out = False
    start_time = time.time()
    while True:
        all_good = True
        client_info = get_active_client_by_mac_addr(client_mac, zd)
        if client_info:
            if client_info['radio'] == u'802.11b/g/n':
                client_info.update({'radio': u'802.11g/n'})
            for key, value in exp_client_info.iteritems():
                matched = False
                if type(value) in [list, tuple]:
                    if client_info[key].lower() in [x.lower() for x in value]:
                        matched = True
                else:
                    try:
                        if client_info[key].lower() == value.lower():
                            matched = True
                    except:
                        logging.debug('tmethod.verify_zd_client_status [MAC %s] [onKey %s] [onVal %s] client_info:\n%s' \
                                     % (client_mac, key, value, client_info))
                if not matched:
                    if timed_out:
                        msg = "The information [%s] of the client with MAC [%s] was [%s] instead of [%s]" % \
                              (key, client_mac, client_info[key], exp_client_info[key])
                        return (msg, client_info)
                    all_good = False
                    break
        # Quit the loop if everything is good
        if client_info and all_good: break
        # Otherwise, pause for a while
        time.sleep(1)
        timed_out = time.time() - start_time > check_status_timeout
        # Report error if the info is not available after a long time checking
        if not client_info and timed_out:
            msg = "Zone Director didn't show any information about the client with MAC [%s]" % client_mac
            return (msg, client_info)
        # Or give it another try
    # End of while

    return ("", client_info)

#   client_ping_dest_not_allowed(self.target_station, self.ip_addr)
def client_ping_dest_not_allowed(target_station, dest_ip_addr, **kwargs):
    args = dict(ping_timeout_ms = 5000)
    args.update(kwargs)

    logging.info("Client ip_addr %s to dest ip_addr %s is not allowed." % (target_station.get_ip_addr(), dest_ip_addr))
    ping_result = target_station.ping(dest_ip_addr, args['ping_timeout_ms'])
    if ping_result.find("Timeout") != -1:
        logging.info("Ping FAILED. Correct behavior")
        return ""
    else:
        logging.info("Ping OK. Incorrect behavior")
        return "The target station could send traffic while it was not authorized by the ZD"

#   tmethod.client_ping_dest_is_allowed(self.target_station, self.ip_addr)
def client_ping_dest_is_allowed(target_station, dest_ip_addr, **kwargs):
    args = dict(ping_timeout_ms = 5000)
    args.update(kwargs)

    logging.info("Client ip_addr %s to dest ip_addr %s is allowed." % (target_station.get_ip_addr(), dest_ip_addr))
    ping_result = target_station.ping(dest_ip_addr, args['ping_timeout_ms'])
    if ping_result.find("Timeout") != -1:
        logging.info("Ping FAILED. Incorrect behavior")
        return "The target station could not send traffic after being authenticated by the ZD"
    else:
        logging.info("Ping OK. Correct behavior")
        return ""

def verify_wlan_on_aps(active_ap, ssid, ap_list = None):
    """
    Verify the status of the WLAN on the active ap and turn off WLAN on others APs if they are specified
    """
    if not active_ap:
        logging.info("No Active_AP is being specified for this test on ssid:%s" % ssid)
        return ""
    logging.info("Verify the status of all the WLANs on the AP [%s]" % active_ap.get_base_mac())
    if not active_ap.verify_wlan():
        msg = "WLAN [%s] on AP [%s] was not up" % (active_ap.ssid_to_wlan_if(ssid), active_ap.get_base_mac())
        return msg

    if ap_list:
        remove_wlan_on_non_active_ap(active_ap, ssid, ap_list)

    return ""

def verify_station_info_on_ap(active_ap, station_mac, ssid, channel_no):
    logging.info("Verify information of the station [%s] shown on the AP [%s]" % (station_mac, active_ap.get_base_mac()))
    client_info_on_ap = None
    start_time = time.time()
    wlan_if = ""
    while True:
        all_good = True
        timeouted = time.time() - start_time > 15
        try:
            # Some time
            if not wlan_if:
                wlan_if = active_ap.ssid_to_wlan_if(ssid)
        except Exception, e:
            msg = "Exception on ssid_to_wlan_if(%s): %s" % (ssid, e.message)
            logging.info(msg)
            if timeouted:
                raise Exception(msg)
            continue
        for sta_info in active_ap.get_station_list(wlan_if):
            # Item 0 of the sta_info holds the MAC address of the client
            if sta_info[0].lower() == station_mac.lower():
                client_info_on_ap = sta_info
                # Item 1 holds the AID info of the station
                if sta_info[1] == "0":
                    if timeouted:
                        msg = "The station [%s] AID status was shown as [0] on the AP [%s]" % (station_mac, active_ap.get_base_mac())
                        return msg
                    all_good = False
                    break
                # Item 2 or 3 hold the station's channel info depending on builds
                if sta_info[2] != channel_no and sta_info[3] != channel_no:
                    if timeouted:
                        msg = "The station [%s] channel info on AP [%s or %s] was not the same as shown on ZD [%s]" % \
                              (station_mac, sta_info[2], sta_info[3], channel_no)
                        return msg
                    all_good = False
                    break
                break
        if all_good: return ""
        if not client_info_on_ap and timeouted:
            msg = "The AP [%s] didn't show any info about the station [%s]" % (active_ap.get_base_mac(), station_mac)
            return msg
        time.sleep(2)

def verify_wlan_in_the_air(station, ssid, timeout = 15):
    logging.info("Verify if the target station could see the SSID broadcasted in the air")
    start_time = time.time()
    while True:
        res = station.check_ssid(ssid)
        if res == ssid:
            break
        time.sleep(1)
        if time.time() - start_time > timeout:
            return "The station didn't see the WLAN with SSID [%s] in the air" % ssid
    return "The station couldn't associate to the WLAN although the beacons of the WLAN were found on the air"


