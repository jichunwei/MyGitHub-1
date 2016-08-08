#===============================================================================
# Support for tea.py:
#    + Run tea.py by command line:
#        tea.py lib_ATTDataCollection te_root=RuckusAutoTest.components.lib doTask=your_task
#
#        You must specify what kind of info to get for these tasks belows. We have 5 kind of info:
#        'device_info', 'device_time', 'lan_info' , 'lan_host_conf', 'lan_host_conf_interface'
#        Each kind of info store some specific information.
#            + device_info: X_001392_STATS_INTERVAL, X_001392_STATS_INTERVAL_BINS, ModelName,
#                SerialNumber, SoftwareVersion, UpTime
#            + device_time :  CurrentLocalTime
#            + lan_info : X_001392_LAN_Index, LANWLANConfigurationNumberOfEntries
#            + lan_host_conf : IPInterfaceNumberOfEntries
#            + lan_host_conf_interface : X_001392_IP_INTERFACE_Index, Enable,
#                X_001392_MGT_MAC,  IPInterfaceIPAddress
#
#        List of tasks are supported by this lib and their arguments.
#        + Task 1: get_cli_info
#            + Use: get all ap's information from command line
#            + Arg:
#                + cfg : a dict store config of ap, usually we only need ipaddr
#                + type : 1 of 5 types above
#            + Ex: tea.py lib_ATTDataCollection te_root=RuckusAutoTest.components.lib \
#                doTask=get_cli_info cfg=dict(ipaddr = '192.168.2.1') type=device_info
#        + Task 2: get_xml_info
#            + Use: run jar file to get information of ap
#            + Arg:
#                + path : this is path to directory that store jar and config files
#                + type : 1 of 5 types above
#            + Ex: tea.py lib_ATTDataCollection te_root=RuckusAutoTest.components.lib \
#                    doTask=get_xml_info path='C:\temp\data\' type=device_info
#        + Task 3: verify_info
#            + Arg:
#                + iperf_path : path to dir that store iperf.
#                    Default value: 'rat\\tools\\RatToolAgent\\',
#                + java_path : path to dir that store java program.
#                    Default value: 'rat\\tools\\datacollection\\'
#                + sta_ip_addr : ip address of window station behind adapter 7111
#                    Default value : 192.168.2.4
#                + ipaddr : ip address of ap 7811. Default value: 192.168.2.1
#                + timeout : this is timeout for run iperf server and client on window
#                    machines. Default value : 600 seconds
#                + type: 1 of 5 types above. Default value : device_info
#                + info : this is info that you want to verify. You must choose info that have in list of
#                    info of one type above
#                    Default value : ModelName
#            + Ex: tea.py reg_status_mgmt te_root=RuckusAutoTest.components.lib \
#                    doTask=verify_info type=device_info info=SoftwareVersion
#        + Task 4: will add later
#            + Arg:
#            + Ex:
#
#        + Task 5: will add later
#            + Arg: none
#            + Ex:
#
#        + Task 6: will add later
#            + Arg:
#            + Ex: tea.py reg_status_mgmt te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=upload_inven_file file_path=C:\123.txt mode=manufact
#
#
# Author: Tu Bui. Email: tubn@s3solutions.com.vn. Date: Sept 29th, 2009
#===============================================================================

import os
import time
import datetime
import logging
import re
from xml.dom import minidom
#from RuckusAutoTest.models import Test
#from RuckusAutoTest.common.Ratutils import logging
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC
from pprint import pprint

#from django.core.management import setup_environ

# define some constant
LAN_INDEX = 0
LAN_WAN_CONFIG_NUMBER_OF_ENTRIES = 1
HOST_INTERFACE_ENABLED = 1
HOST_INTERFACE_DISABLED = 0
DEFAULT_INTERFACE = '192.168.0.1'

# create path to directories that store IPERF and java program
PATH_IPERF = os.path.join("tools", "RatToolAgent")
PATH_JAVA = os.path.join("tools", "datacollection")

# define tag name in xml file and list of info need to get for this tag
TAGNAME_INFO = dict(
    DeviceInfo = [
        'ModelName' , 'SerialNumber',
        'X_001392_STATS_INTERVAL', 'SoftwareVersion',
        'X_001392_STATS_INTERVAL_BINS', 'UpTime'
    ],

    Time = ['CurrentLocalTime'],

    LANDevice = [
        'X_001392_LAN_Index',
        'LANWLANConfigurationNumberOfEntries'
    ],

    LANHostConfigManagement = ['IPInterfaceNumberOfEntries'],

    IPInterface = [
        'X_001392_IP_INTERFACE_Index', 'Enable',
        'X_001392_MGT_MAC', 'IPInterfaceIPAddress'
    ],

    X_001392_WLANStats = [
        'X_001392_WLAN_STATS_Index', 'X_001392_WLAN_NF',
        'X_001392_WLAN_RX_PKTS', 'X_001392_WLAN_RX_OCTETS',
        'X_001392_WLAN_TX_PKTS', 'X_001392_WLAN_TX_OCTETS'
    ],

    WLANConfiguration = [
        'X_001392_WLAN_Index', 'X_001392_WLAN_NAME',
        'Enable', 'Channel', 'SSID', 'BeaconType',
        'Standard', 'WPAEncryptionModes', 'TotalAssociations'
    ],

    AssociatedDevice = ['AssociatedDeviceMACAddress',
        'X_001392_STA_NUM_ETHERNET', 'X_001392_STA_Index'
    ],

    X_001392_ClientStats = ['X_001392_STA_STATS_Index', 'X_001392_STA_TX_RSSI',
        'X_001392_STA_THROUGHPUT_EST', 'X_001392_STA_RX_PKTS',
        'X_001392_STA_TX_PKTS_XMIT', 'X_001392_STA_TX_PKTS_QUEUED',
        'X_001392_STA_TX_PKTS_DROP_OVERFLOW', 'X_001392_STA_TX_PKTS_DROP_XRETRIES',
        'X_001392_STA_TX_PKTS_DROP_OVERDUE'
    ],

    X_001392_STA_ETHER_MAC = [
        'X_001392_STA_ETHER_Index', 'X_001392_STA_ETHER_ADDR'
    ]

)

# mapping between user input and tag name in xml file
INPUT_TAGNAME = dict(
    device_info = 'DeviceInfo',
    device_time = 'Time',
    lan_info = 'LANDevice',
    lan_host_conf = 'LANHostConfigManagement',
    lan_host_conf_interface = 'IPInterface',
    wlan_conf_info = 'WLANConfiguration',
    wlan_conf_wlanstat = 'X_001392_WLANStats',
    associate_device = 'AssociatedDevice',
    station_ethernet_mac = 'X_001392_STA_ETHER_MAC',
    associate_client_stat = 'X_001392_ClientStats',
)

# define threshold for value that get from cli and from xml file
THRESHOLD = dict(
    UpTime = 10,
    CurrentLocalTime = 10,
    X_001392_WLAN_RX_PKTS = 20,
    X_001392_WLAN_RX_OCTETS = 1000,
    X_001392_WLAN_TX_PKTS = 10,
    X_001392_WLAN_TX_OCTETS = 1000,
    X_001392_WLAN_NF = 10,
    X_001392_STA_RX_PKTS = 20,
    X_001392_STA_TX_PKTS_XMIT = 10,
    X_001392_STA_TX_RSSI = 10
)


def parseXmlInfo(file_path, list_info, tag_name, dict_path):
    """
    This function use to get information from xml file according to tag name, dict path and
    list information argument.
    Ex: tag_name = "LANHostConfigManagement", list_info = ["IPInterfaceNumberOfEntries", "Testing"]
        dict_tag = {name : "LanDevice", index : 0, child : {name : "LANHostConfigManagement", index : 0 }}
        --> It will get first element have tag name equal with "LanDevice". Then get its first child
        that have tag name "LANHostConfigManagement". At the end, it get attribute "Testing",
        "IPInterfaceNumberOfEntries" and put them into a dict.
        Result will have format: {'IPInterfaceNumberOfEntries' : 1, 'Testing' : 'test'}
    """

    result = {}
    xmldoc = minidom.parse(file_path)
    temp = dict_path
    list_element = xmldoc.getElementsByTagName(temp['name'])[temp['index']]

    # get element according to dict path
    while temp.has_key('child'):
        temp = temp['child']
        index = 0
        for element in list_element.childNodes:
            if element.nodeName == temp['name']:
                if index == int(temp['index']):
                    list_element = element
                    break
                else:
                    index += 1

    # get info for element above
    for info in list_info:
        result[info] = list_element.getAttribute(info)

    return result


def getAP(cfg):
    """
    Get ap from testbed if resist, else create a new one
    """

    if not cfg.has_key('ap'):
        ap = RuckusAP(cfg)
    else:
        ap = cfg['ap']

    return ap


def getFinalIndex(cfg):
    """
    This function get final index of an element in a dict
    Ex: cfg = {"name" : "LANDevice", "index" : 0,
        "child" : {"name" : "LANHostConfigManagement", "index" : 0,
        "child" : {"name" : "IPInterface", "index" : 1 }}}
        --> result = 1
    """

    my_cfg = cfg
    while my_cfg.has_key('child'):
        my_cfg = my_cfg['child']

    return my_cfg['index']


def getIndexByName(cfg, name):
    """
    This function get index of an element according to its name in a dict
    Ex: + name = "LANDevice"
        + cfg = {"name" : "LANDevice", "index" : 0,
        "child" : {"name" : "LANHostConfigManagement", "index" : 0,
        "child" : {"name" : "IPInterface", "index" : 1 }}}
        --> result = 0
    """

    my_cfg = cfg

    while my_cfg.has_key('child'):
        if my_cfg['name'] == name:
            return my_cfg['index']
        else:
            my_cfg = my_cfg['child']

    return my_cfg['index']


def getWlanId(cfg):
    """
    This function get wlan_id from dict
    Ex: dict_tag = {"name" : "LANDevice", "index" : 0,
        "child" : {"name" : "LANHostConfigManagement", "index" : 1,
        "child" : {"name" : "IPInterface", "index" : 0 }}}
        --> result = 1
    """

    my_cfg = cfg
    while my_cfg['name'] != 'LANHostConfigManagement' and my_cfg['name'] != 'WLANConfiguration' and my_cfg.has_key('child'):
        my_cfg = my_cfg['child']

    return 'wlan' + str(my_cfg['index'])


def getStationMacAddr(ap, wlan_id, associate_index):
    '''
    This function get mac address of adapter
    '''

    dict_stations_info = ap.get_station_info(wlan_id)

    for station in dict_stations_info.keys():
        if station != 'total_station' and int(dict_stations_info[station]['aid']) - 1 == associate_index:
            return station


def returnMessage(result, info, cli_value, xml_value):
    """
    This function define return message (PASS or FAIL) as a result after finish verifying.
    """

    return [result, "Verify %s %s. %s from cli = %s, %s from xml = %s"
            % (info, result, info, cli_value, info, xml_value)]


def getDeviceInfo(**kwargs):
    """
    This function get some information about device from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(X_001392_STATS_INTERVAL = '', X_001392_STATS_INTERVAL_BINS = '',
        ModelName = '', SerialNumber = '', SoftwareVersion = '', UpTime = ''
        )

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    # get stats_interval and stats_interval_bins
    dc = ap.get_data_collection()
    result.update(dc)

    # get model name and serial number
    model_name = ap.get_board_data_item('Model')
    serial_number = ap.get_board_data_item('Serial')
    result['ModelName'] = model_name
    result['SerialNumber'] = serial_number

    # get software version
    software_version = ap.get_version()
    result['SoftwareVersion'] = software_version

    # get uptime
    uptime = ap.get_up_time()
    result['UpTime'] = uptime

    return result


def getDeviceTime(**kwargs):
    """
    This function get some information about device time from command line.
    Now this function only get CurrentLocalTime, but we use dict here for enhancement later
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(CurrentLocalTime = '')

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    result.update(ap.get_local_date_time())

    return result


def getLanDeviceInfo(**kwargs):
    """
    This function get some information about lan device from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(X_001392_LAN_Index = '', LANWLANConfigurationNumberOfEntries = '')

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    # get number of wlanconf of this lan device
    result['LANWLANConfigurationNumberOfEntries'] = len(ap.get_wlan_info_dict())
    result['X_001392_LAN_Index'] = getFinalIndex(cfg['path'])

    return result


def getLanHostConf(**kwargs):
    """
    This function get some information about lan configuration from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(IPInterfaceNumberOfEntries = LAN_WAN_CONFIG_NUMBER_OF_ENTRIES)

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    #ap = getAP(cfg)

        # get lan host conf value here. Will implement later

    return result


def getLanHostConfInterface(**kwargs):
    """
    This function get some information about inteface of lan device from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(X_001392_IP_INTERFACE_Index = LAN_INDEX, Enable = HOST_INTERFACE_DISABLED,
        X_001392_MGT_MAC = '',  IPInterfaceIPAddress = '')
    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    # get base mac address
    result['X_001392_MGT_MAC'] = str(ap.get_base_mac())

    # get ip address
    result['IPInterfaceIPAddress'] = ap.get_ip_addr()

    result['Enable'] = HOST_INTERFACE_ENABLED \
                       if result['IPInterfaceIPAddress'] != DEFAULT_INTERFACE else \
                       HOST_INTERFACE_DISABLED
    # get Enable, IPIndex. will implement later
    result['X_001392_IP_INTERFACE_Index'] = getFinalIndex(cfg['path'])

    return result


def getWlanConfInfo(**kwargs):
    """
    This function get some information about wlan from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(
        X_001392_WLAN_Index = '', X_001392_WLAN_NAME = '',
        Enable = '', Channel = '', SSID = '', BeaconType = '',
        Standard = '', WPAEncryptionModes = '', TotalAssociations = '')

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    # get info from cmd: get wlanlist
    wlanlist_info = ap.get_wlan_info_dict()
    wlan_index = getFinalIndex(cfg['path'])
    wlan_id = 'wlan' + str(wlan_index)
    result['X_001392_WLAN_Index'] = wlan_index
    result['X_001392_WLAN_NAME'] = wlanlist_info[wlan_id]['name']
    result['Enable'] = 1 if wlanlist_info[wlan_id]['status'] == 'up' else 0

    # get channel
    result['Channel'] = ap.get_channel(wlan_id)[0]

    # get ssid
    result['SSID'] = ap.get_ssid(wlan_id)

    # get BeaconType, WPAEncryptionModes
    encryption_result = ap.get_encryption(wlan_id)
    try:
        result['BeaconType'] = encryption_result['BeaconType']
        result['WPAEncryptionModes'] = encryption_result['WPAEncryptionModes']
    except:
        pass

    # get standard
    result['Standard'] = ap.get_phy_mode(wlan_id)

    # get totalassociation
    result['TotalAssociations'] = ap.get_station_info(wlan_id)['total_station']

    return result


def getWlanConfWlanStat(**kwargs):
    """
    This function get some information about status of wlane from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(
        X_001392_WLAN_STATS_Index = 0, X_001392_WLAN_NF = '',
        X_001392_WLAN_RX_PKTS = 0, X_001392_WLAN_RX_OCTETS = 0,
        X_001392_WLAN_TX_PKTS = 0, X_001392_WLAN_TX_OCTETS = 0,
    )

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    wlan_id = getWlanId(cfg['path'])

    # get X_001392_WLAN_NF
    result['X_001392_WLAN_NF'] = ap.get_noise_level(wlan_id)

    # get netstats info
    netstats_info = ap.get_netstats_info()
    result['X_001392_WLAN_RX_PKTS'] = netstats_info['receive'][wlan_id]['packets']
    result['X_001392_WLAN_RX_OCTETS'] = netstats_info['receive'][wlan_id]['bytes']
    result['X_001392_WLAN_TX_PKTS'] = netstats_info['transmit'][wlan_id]['packets']
    result['X_001392_WLAN_TX_OCTETS'] = netstats_info['transmit'][wlan_id]['bytes']

    return result


def getAssociatedStationInfo(**kwargs):
    """
    This function get some information about associated station  from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(X_001392_STA_Index = '',
        AssociatedDeviceMACAddress = '',
        X_001392_STA_NUM_ETHERNET = 1,
    )

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)

    wlan_id = getWlanId(cfg['path'])
    associate_index = int(getFinalIndex(cfg['path']))

    dict_stations_info = ap.get_station_info(wlan_id)

    for station in dict_stations_info.keys():
        if station != 'total_station' and int(dict_stations_info[station]['aid']) - 1 == associate_index:
            result['AssociatedDeviceMACAddress'] = station
            # number of ethernet of this station
            number_of_station = len(cfg['active_ap']['active_ad'][associate_index]['local_station'])

            result['X_001392_STA_NUM_ETHERNET'] = number_of_station
            result['X_001392_STA_Index'] = associate_index

            return result


def getStationEthernetMac(**kwargs):
    """
    This function get some information about ethernet mac of station  from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    """

    result = dict(X_001392_STA_ETHER_Index = 0,
        X_001392_STA_ETHER_ADDR = ''
    )

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)

    #ap = getAP(cfg)

    station_index = int(getFinalIndex(cfg['path']))
    associate_index = int(getIndexByName(cfg['path'], 'AssociatedDevice'))
    station = cfg['active_ap']['active_ad'][associate_index]['local_station'][station_index]

    for local_station in cfg['stations']:
        if local_station.get_ip_addr() == station['ip_addr']:
            win_sta = local_station
            result['X_001392_STA_ETHER_ADDR'] = win_sta.get_ip_cfg()['mac_addr'].lower()
            result['X_001392_STA_ETHER_Index'] = station_index
            return result


def getAssociatedClientStat(**kwargs):
    '''
    This function get some information about associated client stats from command line.
    Input : dict that store config of AP - ussually only need ipaddr
    Output : see dict result below
    '''
    result = dict(
        X_001392_STA_STATS_Index = 0, X_001392_STA_TX_RSSI = '',
        X_001392_STA_THROUGHPUT_EST = '', X_001392_STA_RX_PKTS = '',
        X_001392_STA_TX_PKTS_XMIT = '', X_001392_STA_TX_PKTS_QUEUED = '',
        X_001392_STA_TX_PKTS_DROP_OVERFLOW = '', X_001392_STA_TX_PKTS_DROP_XRETRIES = '',
        X_001392_STA_TX_PKTS_DROP_OVERDUE = ''
    )

    cfg = dict(ipaddr = '192.168.2.1')
    cfg.update(kwargs)
    ap = getAP(cfg)
    wlan_id = getWlanId(cfg['path'])
    associate_index = int(getFinalIndex(cfg['path']))
    mac_addr = getStationMacAddr(ap, wlan_id, associate_index)
    # get client stats info
    client_stats_info = ap.get_station_stats_info(wlan_id)[mac_addr]
    result['X_001392_STA_TX_RSSI'] = client_stats_info['tx_rssi']
    result['X_001392_STA_THROUGHPUT_EST'] = client_stats_info['tx_kbps']
    result['X_001392_STA_RX_PKTS'] = client_stats_info['good_rx_frms']
    # get mqstat info
    mqstat_info = ap.get_mqstats(wlan_id)[mac_addr]
    result['X_001392_STA_TX_PKTS_XMIT'] = mqstat_info['video']['enq']
    result['X_001392_STA_TX_PKTS_QUEUED'] = mqstat_info['video']['Qued']
    result['X_001392_STA_TX_PKTS_DROP_OVERFLOW'] = mqstat_info['video']['ovrflw']
    result['X_001392_STA_TX_PKTS_DROP_XRETRIES'] = mqstat_info['video']['XRetries']
    result['X_001392_STA_TX_PKTS_DROP_OVERDUE'] = mqstat_info['video']['XTLimits']

    return result


def getCliInfo(**kwargs):
    """
    This function get information from command line according to type of input
    from user
    """

    return {'device_info' : getDeviceInfo,
            'device_time' : getDeviceTime,
            'lan_info' : getLanDeviceInfo,
            'lan_host_conf' : getLanHostConf,
            'lan_host_conf_interface' : getLanHostConfInterface,
            'wlan_conf_info' : getWlanConfInfo,
            'wlan_conf_wlanstat' : getWlanConfWlanStat,
            'associate_device' : getAssociatedStationInfo,
            'associate_client_stat' : getAssociatedClientStat,
            'station_ethernet_mac' : getStationEthernetMac
    }[kwargs['type']](**kwargs)


def getXmlInfo(**kwargs):
    """
    This function get information from xml file according to type of input
    from user
    """

    data_file_path = kwargs['xml_file_path'] if kwargs.has_key('xml_file_path') else ''

    return parseXmlInfo(data_file_path, TAGNAME_INFO[INPUT_TAGNAME[kwargs['type']]],
                                INPUT_TAGNAME[kwargs['type']], kwargs['path'])

def getXmlResponseStatus(**kwargs):
    """
    """
    data_file_path = kwargs['xml_file_path'] if kwargs.has_key('xml_file_path') else ''
    if os.path.getsize(data_file_path) == 0:
        return {'msg': 'File error'}

    file = open(data_file_path)
    for line in file:
        msg = re.findall('Msg\s?=?\s?"(.*)"', line)
        if msg:
            file.close()
            return {'msg': msg[0]}
    file.close()
    raise Exception('[Error] Could not get the response status in %s' % data_file_path)

def getXmlFile(**kwargs):
    """
    This function get information from xml file according to type of input
    from user
    """

    cfg = dict(java_path = PATH_JAVA,
               cmd = 'ruckus_all')
    cfg.update(kwargs)
    path = cfg['java_path']

    # change directory
    #run_data_collection = 'java -jar attAp.jar cmd=ruckus_all'
    run_data_collection = 'java -jar attAp.jar cmd=%s s=perfdataresp_schema.xsd' % cfg['cmd']

    current_dir = os.getcwd()
    os.chdir(path)
    os.system(run_data_collection)
    os.chdir(current_dir)

    data_file_path = os.path.join(path, "data", "%s.xml" % cfg['cmd'])

    return data_file_path


def runIperf(**kwargs):
    """
    This function run iperf for window stations ( ussually we only have 1 station behind adapter
    and current station which run this script. By default iperf must be stored at
    tools/RatToolAgent in this station
    Input : dict conf of list stations (ussually we only need ipaddr)
    """

    cfg = dict(ipaddr = '192.168.2.1', sta_ip_addr = '192.168.2.4', timeout = 10, multicast_srv = True, iperf_path = PATH_IPERF)

    cfg.update(kwargs)

    if cfg.has_key('stations'):
        list_win_sta = cfg['stations']
    else:
        win_sta = RemoteStationWinPC(cfg)
        list_win_sta = [win_sta]

    # get current holdingtime and txpower
    ap = getAP(cfg)

    current_config = ap.get_mq_holding_time()
    current_config['txpower'] = ap.get_tx_power('wlan0')

    # change video holdingtime and txpower to make ovrflw, XRetries, XTLimits in mqstat increase
    dict_input_change = current_config
    dict_input_change['video'] = 500
    dict_input_change['txpower'] = 'min'
    ap.set_mq_holding_time(dict_input_change)
    ap.set_tx_power('wlan0', dict_input_change['txpower'])

    # start Iperf
    for win_station in list_win_sta:
    # start Iperf server at station behind Adapter
    logging.info('start iperf server for station: %s' % win_station.get_ip_addr())
    win_station.start_iperf(serv_addr = win_station.get_ip_addr(),  timeout = cfg['timeout'], multicast_srv = cfg['multicast_srv'])

    # change directory and start Iperf client at local machine
    current_dir = os.getcwd()
    os.chdir(cfg['iperf_path'])
    cmd = 'iperf -c %s -t %s -b 1000mb -u' % (win_station.get_ip_addr(), cfg['timeout'])
    logging.info('start iperf client for station: %s' % win_station.get_ip_addr())
    os.system(cmd)

    # wait for cfg['timeout'] seconds
    time.sleep(cfg['timeout'])

    # stop Iperf
    for win_station in list_win_sta:
        pprint('stop iperf server for station: %s' % win_station.get_ip_addr())
        win_station.stop_iperf()
    os.chdir(current_dir)

    # change video holdingtime and txpower to its previous values
    ap.set_mq_holding_time(current_config)
    ap.set_tx_power('wlan0', current_config['txpower'])



def verifyInfo(**kwargs):
    """
    This function will verify information get from command line and xml file
    Input : see cfg dict below
    Output : PASS/FAIL or ERROR
    """

    cfg = dict(sta_ip_addr = '192.168.2.4', ipaddr = '192.168.2.1', info = 'ModelName',
        iperf_path = PATH_IPERF,
        java_path = PATH_JAVA,
        type = 'device_info'
    )
    cfg.update(kwargs)

    # verify info
    info = cfg['info']
    cli_info = cfg['cli_info']
    xml_info = cfg['xml_info']

    logging.info('Start verify info')
    if THRESHOLD.has_key(info) and info != 'CurrentLocalTime':
        cli_value = int(cli_info)
        xml_value = int(xml_info)

        if xml_value - cli_value > THRESHOLD[info]:
            result = False

        else:
            result = True

    elif info == 'CurrentLocalTime':
        cli_value = str(cli_info)
        xml_value = str(xml_info)
        cli_value_date = datetime.datetime.strptime(cli_value, '%a %b %d %H:%M:%S %Y')
        xml_value_date = datetime.datetime.strptime(xml_value, '%a %b %d %H:%M:%S %Y')

        diff_time = xml_value_date - cli_value_date

        if diff_time.seconds > THRESHOLD[info]:
            result = False
        else:
            result = True

    else:
        xml_value = str(xml_info)
        cli_value = str(cli_info)
    # comparing things here
        result = True if xml_value == cli_value else False

    return result


def main(**kwargs):
    '''
    Support for run with tea.py
    '''
    cfg = dict(doTask = '')
    cfg.update(kwargs)
    if not cfg['doTask']:
        raise Exception('Must tell me which info need to verify')
    task = cfg['doTask']
    del cfg['doTask']
    info = {'get_cli_info' : getCliInfo, 'get_xml_info' : getXmlInfo,
            'verify_info' : verifyInfo
        }[task](**kwargs)
    return info

if __name__ == '__main__':
    pprint('start test here')
    #import os

    cfg = {'active_ap' :
        [{'ip_addr' : '192.168.2.1', 'active_ad' :
        [{'ip_addr' : '192.168.2.254', 'local_station' : [{'ip_addr' : 'xxxx'}]}]}]}
    pprint (cfg)


    #pprint(parse_wlan_conf_info('D:\\workspace\\att1\\rat\\tools\\datacollection\\data\\tan_4.xml'))

    result1 = dict(CurrentLocalTime = '')

    result = dict(X_001392_STATS_INTERVAL = '', X_001392_STATS_INTERVAL_BINS = '',
        ModelName = '', SerialNumber = '', SoftwareVersion = '', UpTime = ''
        )

    cfg1 = dict(X_001392_LAN_Index = '', LANWLANConfigurationNumberOfEntries = '',
        IPInterfaceNumberOfEntries = '', X_001392_IP_INTERFACE_Index = '',
        X_001392_MGT_MAC = '', Enable = '', IPInterfaceIPAddress = ''
    )




