import logging
import time
from RuckusAutoTest.components.Station import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP

def verifyStaConnection(station_obj, src_ip_addr, dest_ip_addr, timeout = 120000, ping_ok = True):

    msg = "Try to ping to station %s from station %s" % (dest_ip_addr, src_ip_addr)
    logging.info(msg)
    ping_result = station_obj.ping(dest_ip_addr, timeout)
    if ping_result.find("Timeout") != -1:
        if not ping_ok:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping FAILED. Incorrect behavior")
            raise Exception("The connection between %s and %s is down" % (src_ip_addr, dest_ip_addr))
    else:
        if not ping_ok:
            logging.info("Ping OK. Incorrect behavior")
            raise Exception("Ping successfully while wireless network is down")
        else:
            logging.info("Ping OK. The connection between %s and %s is up now" % (src_ip_addr, dest_ip_addr))

def analyzeCapturedTraffic(filename, station_obj, src_ip_addr, dest_ip_addr):
    logging.info("Analyze traffic to verify tos value after capturing traffic by tcpdump tool")
    cap_traffic_res = station_obj.analyze_traffic(filename)
    cap_tos_value = ""
    for res in cap_traffic_res:
        if res['src_ip'] == src_ip_addr and res['dst_ip'] == dest_ip_addr:
            cap_tos_value = res['tos']
            break
    if not cap_tos_value:
        msg = "Can not capture traffic with the following information: "
        msg += "source station ----> %s, " % src_ip_addr
        msg += "destination station ----> %s" % dest_ip_addr
        raise Exception(msg)

    logging.info("ToS value of captured traffic: %s" % cap_tos_value)
    return cap_tos_value

def analyzeTrafficOTA(filename, station_obj, src_ip_addr, dest_ip_addr, queue = "", verify_tos = True,
                      ad_model = "", ap_mode = ""):
    logging.info("Analyze traffic over the air to make sure that QoS control field is correct")
    ota_traffic_res = station_obj.analyze_traffic_ota(filename, dest_ip_addr, src_ip_addr)
    print ota_traffic_res
    ok = False
    msg_temp = "Traffic from [%s] to [%s]: " % (src_ip_addr, dest_ip_addr)
    correct_rate = ''
    radio = ''

    if not ota_traffic_res:
        msg = "Can not capture traffic from [%s] to [%s] over the air" % (src_ip_addr, dest_ip_addr)
        return ["FAIL", msg]

    for res in ota_traffic_res:
        if verify_tos:
            if res['qos'].startswith('best effort'):
                temp = 'data'
            else:
                temp = res['qos']
            if temp != queue:
                logging.debug("Captured traffic: %s" % str(ota_traffic_res))
                msg = msg_temp + "priority value in QoS Control field is %s " % temp
                msg += "while packets are inserted to the %s queue on the AP" % queue
                return ["FAIL", msg]
        else:
            # Verify data rate instead
            if ad_model.lower() == 'vf2111':
                if ap_mode.lower() == '11ng': rate = '11.0'
                else: rate = '1.0'
                radio = '2.4 GHz'
            else:
                rate = '6.0'
                radio = '5.0 GHz'

            if res['data_rate'] != rate:
                logging.debug("Data rate of captured packets: %s" % res['data_rate'])
                msg = msg_temp + "Data rate of non-unicast traffic in %s is not %s Mb/s" % (radio, rate)
                return ["FAIL", msg]

    if verify_tos:
        msg = msg_temp + "priority value of QoS Control field is %s. Correct behavior" % res['qos']
        logging.info(msg)
    else: msg = msg_temp + "Data rate of non-unicast traffic is %s Mb/s. Correct behavior" % rate
    return ["PASS", ""]

def get_mqstatsInfo(mq_statistics, queue):

    right_queue_info = {}
    empty_queues = []
    empty_deq = []
    traffic_deq = ""
    traffic_enq = ""
    traffic_reenq = ""
    traffic_qued = ""
    traffic_xretry = ""
    traffic_xtlimit = ""
    for each_queue in mq_statistics.keys():
        if each_queue == "bkgnd":
            temp = "background"
        else:
            temp = each_queue
        if queue == temp:
            traffic_deq = int(mq_statistics[each_queue]['deq'])
            traffic_enq = int(mq_statistics[each_queue]['enq'])
            traffic_reenq = int(mq_statistics[each_queue]['reenq'])
            traffic_xretry = int(mq_statistics[each_queue]['XRetries'])
            if mq_statistics[each_queue]['Qued'] != ':':
                traffic_qued = int(mq_statistics[each_queue]['Qued'])
            else:
                traffic_qued = 0
            if mq_statistics[each_queue].has_key('XTLimits'):
                traffic_xtlimit = int(mq_statistics[each_queue]['XTLimits'])
            else:
                traffic_xtlimit = -1
        else:
            empty_deq.append(int(mq_statistics[each_queue]['deq']))
            empty_queues.append(each_queue)

    right_queue_info = {'traffic_deq':traffic_deq, 'traffic_reenq':traffic_reenq, 'traffic_enq':traffic_enq,
                        'traffic_qued':traffic_qued, 'traffic_xretry':traffic_xretry,
                        'traffic_xtlimit':traffic_xtlimit}

    return (right_queue_info, empty_queues, empty_deq)

def verifyMQStats(right_queue, right_queue_info, empty_queues, empty_deqs, timeout, ad_mac):

    # If traffic is not put to the right queue, or if many packets are put to the wrong queues
    # return FAIL immediately
    deq = right_queue_info['traffic_deq']
    reenq = right_queue_info['traffic_reenq']
    enq = right_queue_info['traffic_enq']
    deq = right_queue_info['traffic_deq']
    qued = right_queue_info['traffic_qued']
    xretry = right_queue_info['traffic_xretry']
    xtlimit = right_queue_info['traffic_xtlimit']

    if not deq:
        return ["FAIL", "Station %s: queue %s is empty" % (ad_mac, right_queue)]

    invalid_packet = int(timeout) * 5
    for i in range(len(empty_deqs)):
        if empty_deqs[i] > invalid_packet:
            logging.debug("\tTotal deq packets of %s queue: %d" %(right_queue, right_queue_info['traffic_deq']))
            logging.debug("\tTotal deq packets of %s queue: %d" %(empty_queues[i], empty_deqs[i]))
            logging.info("\tThere are %d packets in the %s queue" % (empty_deqs[i], empty_queues[i]))
            return ["FAIL", "Station %s: too many packets in the %s queue while it must be empty (%d packets)" %
                    (ad_mac, empty_queues[i], empty_deqs[i])]

    msg = "\tTraffic information: reenq packets ---> %d, enq packets ---> %d, " % (reenq, enq)
    msg += "deq ---> %d, Qued ---> %d" % (deq, qued)
    logging.debug(msg)
    if (reenq + enq) != (deq + qued):
        xretries_ok = False
        xtlimit_ok = False
        # Check if XRetries column is empty or not
        if xretry:
            logging.debug("\tXRetries packets ---> %d" % xretry)
            xretries_ok = True
        else:
            # Check if XTlimits column is empty or not
            if xtlimit != -1 and xtlimit:
                logging.debug("\tXTlimits packets ---> %d" % xtlimit)
                xtlimit_ok = True
        if not xretries_ok and not xtlimit_ok:
            msg = "\Total packets of reenq and enq columns does not equal total packets of " % ad_mac
            msg += "deq and qued columns while XRetries and XTlimits columns are empty"
            return ["FAIL", msg]
    else:
        logging.info("\tTotal packets of reenq and enq columns equals total packets of deq and qued columns")

    logging.info("\tTraffic is inserted to the %s queue correctly" % right_queue)
    return ["PASS", ""]

def verifyStaMGMT(ap_obj = None, station_obj = None, timeout = 0, ad_config = None, wlan_if = 'wlan0'):

    # Verify on the AP
    start_time = time.time()
    while True:
        if ap_obj:
            sta_mgmt = ap_obj.get_sta_mgmt(wlan_if)
            device = "AP"
        if station_obj:
            sta_mgmt = station_obj.get_ad_sta_mgmt(ad_config, 'wlan0')
            device = "adapter"
        if sta_mgmt['enable'] and sta_mgmt['active']:
            break
        if time.time() - start_time > timeout:
            if not sta_mgmt['enable']:
                return ["FAIL", "The %s STA-Management is still disabled after %d seconds although it's turned on" %
                        (device, timeout)]
            if not sta_mgmt['active']:
                return ["FAIL", "The %s STA-Management is not active after %d seconds" % (device, timeout)]

    return ["PASS", ""]

def getAID(ap_obj, ad_ip_addr, ad_mac, timeout, wlan_if = 'wlan0'):
    """
    This function gets AID of the specific adapter on the given period of time
    """
    ad_aid = ""
    start_time = time.time()
    while True:
        res = ap_obj.get_station_info(wlan_if)
        for key, value in res.iteritems():
            if key.lower() == ad_mac.lower():
                ad_aid = value['aid']
                break
        if ad_aid:
            break
        if time.time() - start_time > timeout:
            logging.debug("Station info list on the AP: %s" % res)
            msg = "AP does not display information of the active adapter %s" % ad_ip_addr
            msg += " when getting all information of stations after %d seconds" % timeout
            raise Exception(msg)
    return int(ad_aid)


def getBSSID(ap_obj, wlan_if):
    bssid = ""
    for wlan in ap_obj.get_wlan_list():
        if wlan[3] == wlan_if:
            bssid = wlan[-1]
            break

    if not bssid:
        raise Exception("Invalid interface wlan")

    return bssid


def findCapturedPacket(station_obj, filename, src_ip= "", dst_ip = "", proto = "UDP", get_qos = True):
    cap_traffic_res = station_obj.analyze_traffic(filename, proto, get_qos)
    for res in cap_traffic_res:
        if res['src_ip'] == src_ip and res['dst_ip'] == dst_ip:
            return True
    return False

def get_igmp_table(ap_obj, multicast_group):
    igmp_table = ap_obj.get_igmp_table()
    logging.debug("IGMP table %s" % igmp_table)
    for entry in igmp_table:
        if multicast_group in entry:
            if not "Invalid" in entry:
                return True
    return False

def verifyToSValue(filename, remote_sta_obj, local_ip_addr, dst_ip_addr, verified_tos_value, tos_mark = False):

    cap_tos_value = analyzeCapturedTraffic(filename, remote_sta_obj, local_ip_addr, dst_ip_addr)

    if cap_tos_value.lower() != verified_tos_value.lower():
        if not tos_mark: logging.debug("Sent ToS value: %s" % verified_tos_value.lower())
        else: logging.debug("The correct ToS value for outgoing traffic: %s" % verified_tos_value)
        logging.debug("The received ToS value: %s" % cap_tos_value.lower())

        if not tos_mark:
            return ["FAIL", "The received ToS value is not the same as the sent ToS value"]
        else: return ["FAIL", "The marked ToS value of outgoing traffic is wrong"]
    else:
        logging.info("The ToS value at receiver is correct")

    return ["PASS", ""]

def getStaMQStatistics(ap_obj, ad_mac, wlan_if):
    logging.info("Get media queue statistics of the adatper %s on the AP after streaming traffic" %
                 ad_mac)
    res = ap_obj.get_mqstats(wlan_if)
    mq_statistics = {}
    for key in res.keys():
        if key.lower() == ad_mac.lower():
            mq_statistics = res[key]
            break
    logging.debug("Mqstats statistic: %s" % mq_statistics)
    return mq_statistics

def verifyEmptyQueue(mq_statistics, ad_mac = ""):
    for each_queue in mq_statistics.keys():
        if int(mq_statistics[each_queue]['deq']) > 150:
            return ["FAIL", "%s queue has %s packets while it must be empty" %
                    (each_queue, mq_statistics[each_queue]['deq'])]
    if ad_mac: logging.info("Station %s: all queues are empty" % ad_mac)
    else: logging.info("All queues are empty")

    return ["PASS", ""]

def setADWlanState(sta_obj, ad_conf, status, model, ad_ip_addr):
    logging.info("%s svcp interface on adapter %s" % (status, ad_ip_addr))
    sta_obj.set_ruckus_ad_state(ad_conf, status, 'wlan0')
    if status.lower() == "up":
        if model.lower() == 'vf7111': time.sleep(60)
        else: time.sleep(2)
