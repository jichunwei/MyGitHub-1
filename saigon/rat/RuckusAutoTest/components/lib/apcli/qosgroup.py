# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library support to execute the command in RadioGroup
rkscli: help qosgroup
==========
QOS Group:
==========
qos        : get qos
                 -- Displays global state and attributes of Ruckus QOS processing
        get qos <ifname>
                 -- Displays state and attributes of Ruckus QOS processing for the specified interface
qos        : set qos...
        set qos heuristics [voice|video] classify <octet count>
                 -- Sets octet count for Heuristic-based classification
        set qos heuristics [voice|video] noclassify <octet count>
                 -- Sets octet count for Heuristic-based no-classification window
        set qos heuristics [voice|video] [ipg|pktlen] <minimum> <maximum>
                 -- Sets parameters for Heuristic-based classification
        set qos tos classify [voice|video] [<comma separated TOS value(s)>|none]
                 -- Sets values for TOS-based classification
        set qos tos mark [voice|video] <TOS value>
                 -- Sets TOS values for each type of traffic
        set qos dot1p classify [voice|video] [<comma separated Dot1p value(s)>|none]
                 -- Sets values for DOT1P-based classification
        set qos dot1p mark [voice|video] <Dot1p value>
                 -- Sets Dot1p values for each type of traffic
        -------------------------------------------------------------
        set qos txFailThreshold <new threshold>
                 -- Sets # of consecutive TX failures to consider a STA is 'dead'
        set qos QueryInterval <new interval>
                 -- Sets the periodical time interval for issuing IGMP/MLD General Query messages. Setting <new interval> to zero means that periodical IGMP/MLD General Query mechanism will be disabled.
        set qos aging [enable|disable]
                 -- Sets the state of IGMP/MLD Aging Mechanism
        set qos igmp_query [v2|v3] [enable|disable]
                 -- Sets IGMP General Query version for IGMP General Query Mechanism
        set qos mld_query [v1|v2] [enable|disable]
                 -- Sets MLD General Query version for MLD General Query Mechanism
        set qos <ifname> directed multicast [enable|disable]
                 -- Sets the state of egress packet processing for the specified interface
        set qos <ifname> igmp [enable|disable]
                 -- Sets the state of IGMP Snooping for the specified interface
        set qos <ifname> mld [enable|disable]
                 -- Sets the state of MLD Snooping for the specified interface
        -------------------------------------------------------------
        set qos <ifname> classification [enable|disable]
                 -- Enables QOS processing on the specified interface
        set qos <ifname> heuristics udp [enable|disable]
                 -- Enables UDP Heuristics-based classification on the specified interface
        set qos <ifname> mac [add|delete] [ucast|bcast|nonip|all] [dest|src] <xx:xx:xx:xx:xx:xx> [drop|[tos|priority] [voice|video]] [<comment-text>]
                 -- Sets L2 MAC Filters on the specified interface
        set qos <ifname> ip [add|delete] [ucast|bcast] [dest|src] <xxx.xxx.xxx.xxx>/<fff.fff.fff.fff> [drop|[tos|priority] [voice|video]] [<comment-text>]
                 -- Sets L3 IP Filters on the specified interface
        set qos <ifname> port [add|delete] [ucast|bcast] [tcp|udp] [dest|src] <xxxx|xxxx-yyyy> [drop|[tos|priority] [voice|video]] [<comment-text>]
                 -- Sets L4 Port Filters on the specified interface
        set qos <ifname> tos classify [enable|disable]
                 -- Enables TOS-based processing on the specified interface
        set qos <ifname> dot1p classify [enable|disable]
                 -- Enables Dot1p-based processing on the specified interface
        set qos <ifname> dot1p [classify|mark] [<vid>|<vid1-vid2>|all] [enable|disable]
                 -- Enables Dot1p-based processing on the specified interface among VIDs
        set qos <ifname> vlanid [classify] [voice|video|data|background] [<vid>|<vid1-vid2>|all] [enable|disable]
                 -- Enables VLANID-based processing on the specified interface

OK
rkscli:

"""

import re
from RuckusAutoTest.components.lib.apcli.cli_regex import *

#
# 
#

GLOBAL_QOS_OPTION = {
    'tx_failure_threshold': TX_FAILURE_THRESHOLD,
    'dead_station_count': DEAD_STA_COUNT,

    'tos_classification_voice': TOS_CLASSIFICATION_VOICE,
    'tos_classification_video': TOS_CLASSIFICATION_VIDEO,

    'heuristic_octet_count_voice': HEURISTIC_OCTET_COUNT_VOICE,
    'heuristic_octet_count_video': HEURISTIC_OCTET_COUNT_VIDEO,
    
    'no_heuristic_octet_count_voice': NO_HEURISTIC_OCTET_COUNT_VOICE,
    'no_heuristic_octet_count_video': NO_HEURISTIC_OCTET_COUNT_VIDEO,

    'heuristic_max_pkt_len_voice': HEURISTIC_MAX_PKT_LEN_VOICE,
    'heuristic_max_pkt_len_video': HEURISTIC_MAX_PKT_LEN_VIDEO,

    'heuristic_min_pkt_len_voice': HEURISTIC_MIN_PKT_LEN_VOICE,
    'heuristic_min_pkt_len_video': HEURISTIC_MIN_PKT_LEN_VIDEO,

    'heuristic_max_pkt_gap_voice': HEURISTIC_MAX_PKT_GAP_VOICE,
    'heuristic_max_pkt_gap_video': HEURISTIC_MAX_PKT_GAP_VIDEO,

    'heuristic_min_pkt_gap_voice': HEURISTIC_MIN_PKT_GAP_VOICE,
    'heuristic_min_pkt_gap_video': HEURISTIC_MIN_PKT_GAP_VIDEO,
                     }

GET_GLOBAL_QOS_CMD = 'get qos'
#
#
#

def get_qos(apcli, **kwargs):
    """
    Get the return of get qos command:
    
    Tx Failure Threshold:      50           Dead Station Count: 0

    IGMP/MLD Query Interval:   125
    IGMP/MLD aging mechanism:  Enabled
    IGMP General Query V2/V3:  Disabled/Enabled
    MLD  General Query V1/V2:  Disabled/Enabled

    TOS Classification:        Voice=0xE0,0xC0,0xB8, Video=0xA0,0x80, Data=0x0, Background=0x0
    TOS marking:               VoIP=0x0, Video=0xA0, Data=0x0, Background=0x0

    Dot1p Classification:      Voice=none, Video=none, Data=none, Background=none
    Dot1p marking:             VoIP=0, Video=0, Data=0, Background=0

    Tunnel TOS Marking:        0xA0

    Heuristic Classifier:         VoIP      Video           Data    Background
    Octet Count During Classify:  600       50000           0       0
    Octet Count Between Classify: 10000     500000          0       0
    Min/Max Avg Packet Length:    70/400    1000/1518       0/0     0/0
    Min/Max Avg Inter Packet Gap: 15/275    0/65            0/0     0/0

    Prioritization (packet):        Off
    Bklog Queue Info       :        0 (max: 0) [size: 1000]
    Prioritized Packet Drop:        Voice   Video   Data    Background
    Hi-Watermark threshold :        0       0       0       0
    Low-Watermark threshold:        0       0       0       0
    Packet Drop Count      :        0       0       0       0
    Drop State             :        0       0       0       0
    Drop State Tripped     :        0       0       0       0
    """
    cfg = {}
    if kwargs: cfg.update(kwargs)
    
    res = execute_cmd(apcli, GET_GLOBAL_QOS_CMD, GLOBAL_QOS_OPTION, **cfg)
    qos_conf = {}
    for key in res.keys():
        if key in GLOBAL_QOS_OPTION.keys() and 'tos_classification' not in key:
            qos_conf[key] = res[key][0]
        if 'tos_classification' in key:
            qos_conf[key] = res[key][0].strip(',').split(',')
        if key == 'raw_info':
            qos_conf[key] = res[key]
    
    return qos_conf            
    
def get_tunnel_tos_making(apcli):
    tos_setting = get_qos(apcli)['tunnel_tos_marking']
    rgex = '(\w+)[:=]+(\w+)'
    tos_setting = tos_setting.split(',')
    tos_val = {}
    for ele in tos_setting:
        if re.match(rgex, ele.strip()):
            val = re.findall(rgex, ele)
            tos_val[val[0][0]] = val[0][1]
    return tos_val                        
#
#
#
