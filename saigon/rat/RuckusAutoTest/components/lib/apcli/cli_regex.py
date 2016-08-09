# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library includes the regular expression of the values return by command.
"""

import re
from RuckusAutoTest.common.lib_Logging import *

#
#
#

WLAN_SSID = 'SSID\s?:?=?\s?(.+)\r'
WLAN_PASSPHRASE = 'PassPhrase\s?\(\d+\)\s?:?=?\s?(.+)\r'

#Jane.Guo@Add for Force DHCP
WLAN_FORCE_DHCP = 'Force DHCP is (.*)\r'

TX_FAILURE_THRESHOLD = 'Tx Failure Threshold\s*:?=?\s*(\d+)'
DEAD_STA_COUNT = 'Dead Station Count\s*:?=?\s*(\d+)'
IGMP_MLD_QUERY_INTERVAL = 'IGMP/MLD Query Interval\s*:?=?\s*(\d+)'
IGMP_MLD_AGING_MECHANISM = 'IGMP/MLD aging mechanism\s*:?=?\s*(Enabled|Disabled)'
IGMP_GEN_QUERY_V2 = 'IGMP General Query V2/V3\s*:?=?\s*(Disabled|Enabled)/'
IGMP_GEN_QUERY_V3 = 'IGMP General Query V2/V3\s*:?=?\s*/(Disabled|Enabled)'
MLD_GEN_QUERY_V1 = 'MLD  General Query V1/V2\s*:?=?\s*(Disabled|Enabled)/'
MLD_GEN_QUERY_V2 = 'MLD  General Query V1/V2\s*:?=?\s*/(Disabled|Enabled)'

TOS_CLASSIFICATION_VOICE = 'TOS Classification\s*:?=?\s*Voice\s*=?:?\s*(.*)\sV'
TOS_CLASSIFICATION_VIDEO = 'TOS Classification\s*:?=?.*Video\s*=?:?\s*(.*)\sD'
TOS_CLASSIFICATION_DATA = 'TOS Classification\s*:?=?.*Data\s*=?:?\s*(.*)\sB'
TOS_CLASSIFICATION_BKGD = 'TOS Classification\s*:?=?.*Background\s*=?:?\s*(.*)\s'

TOS_MARKING_VOICE = 'TOS marking\s*:?=?\s*VoIP\s*:?=?\s*(.*)\sV'
TOS_MARKING_VIDEO = 'TOS marking\s*:?=?.*Video\s*:?=?\s*(.*)\sD'
TOS_MARKING_DATA = 'TOS marking\s*:?=?.*Data\s*:?=?\s*(.*)\sB'
TOS_MARKING_BKGD = 'TOS marking\s*:?=?.*Background\s*:?=?\s*(.*)\s'

TUNNEL_TOS_MARKING = 'Tunnel TOS Marking\s*:?=?\s*(.*)\r\n'

HEURISTIC_OCTET_COUNT_VOICE = 'Octet Count During Classify\s*:?=?\s*(\d+)\s+\d+\s+\d+\s+\d+\s'
HEURISTIC_OCTET_COUNT_VIDEO = 'Octet Count During Classify\s*:?=?\s*\d+\s+(\d+)\s+\d+\s+\d+\s'
HEURISTIC_OCTET_COUNT_DATA = 'Octet Count During Classify\s*:?=?\s*\d+\s+\d+\s+(\d+)\s+\d+\s'
HEURISTIC_OCTET_COUNT_BKGD = 'Octet Count During Classify\s*:?=?\s*\d+\s+\d+\s+\d+\s+(\d+)\s'

NO_HEURISTIC_OCTET_COUNT_VOICE = 'Octet Count Between Classify\s*:?=?\s*(\d+)\s+\d+\s+\d+\s+\d+\s'
NO_HEURISTIC_OCTET_COUNT_VIDEO = 'Octet Count Between Classify\s*:?=?\s*\d+\s+(\d+)\s+\d+\s+\d+\s'
NO_HEURISTIC_OCTET_COUNT_DATA = 'Octet Count Between Classify\s*:?=?\s*\d+\s+\d+\s+(\d+)\s+\d+\s'
NO_HEURISTIC_OCTET_COUNT_BKGD = 'Octet Count Between Classify\s*:?=?\s*\d+\s+\d+\s+\d+\s+(\d+)\s'

HEURISTIC_MAX_PKT_LEN_VOICE = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/(\d+)\s+\d+/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_LEN_VIDEO = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+\d+/(\d+)\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_LEN_DATA = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/(\d+)\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_LEN_BKGD = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/\d+\s+\d+/(\d+)\s'

HEURISTIC_MIN_PKT_LEN_VOICE = 'Min/Max Avg Packet Length\s*:?=?\s*(\d+)/\d+\s+\d+/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_LEN_VIDEO = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+(\d+)/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_LEN_DATA = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+(\d+)/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_LEN_BKGD = 'Min/Max Avg Packet Length\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/\d+\s+(\d+)/\d+\s'

HEURISTIC_MAX_PKT_GAP_VOICE = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/(\d+)\s+\d+/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_GAP_VIDEO = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+\d+/(\d+)\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_GAP_DATA = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/(\d+)\s+\d+/\d+\s'
HEURISTIC_MAX_PKT_GAP_BKGD = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/\d+\s+\d+/(\d+)\s'

HEURISTIC_MIN_PKT_GAP_VOICE = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*(\d+)/\d+\s+\d+/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_GAP_VIDEO = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+(\d+)/\d+\s+\d+/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_GAP_DATA = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+(\d+)/\d+\s+\d+/\d+\s'
HEURISTIC_MIN_PKT_GAP_BKGD = 'Min/Max Avg Inter Packet Gap\s*:?=?\s*\d+/\d+\s+\d+/\d+\s+\d+/\d+\s+(\d+)/\d+\s'

#@author: Jane.Guo @since: 2013-7-15 Add for Client Isolation
CLIENT_ISOLATION_MODE = 'wlan.* Client Isolation Mode  : (.*)\r'
CLIENT_ISOLATION_FILTER_MODE = 'Client Isolation Filter Mode : (.*)\r'
CLIENT_ISOLATION_FILTER_ACL = '(.*\s+\d+\.\d+\.\d+\.\d+|\S+\:.*\s+0)\r'
#
#
#

INVALID_CMD_MSG = 'Invalid command'
INCOMPLETE_CMD_MSG = 'The command is either unrecognized or incomplete'
SUCCESS_CMD_MSG = 'The command was executed successfully'


def execute_cmd(apcli, cmd, regex_dict, **kwargs):
    cfg = {'prompt': '',
           'timeout': 0}
    res = {}

    if kwargs: cfg.update(kwargs)
    raw_res =  apcli.do_cmd(cmd, cfg['timeout'], cfg['prompt'])
    log_info('ap cli', cmd, raw_res)
    res['raw_info'] = raw_res
    
    for key in regex_dict.keys():
        val = re.findall(regex_dict[key], raw_res)
        res[key] = val if val != [] else 'DID NOT EXIST'
    
    return res
    

