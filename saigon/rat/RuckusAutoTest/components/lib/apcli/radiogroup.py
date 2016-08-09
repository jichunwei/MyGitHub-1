# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library support to execute the command in RadioGroup
rkscli: help radiogroup
============
Radio Group:
============
802.11-h   : get 802.11-h <wifi name>
                 -- Get 802.11h status
802.11-h   : set 802.11-h <wifi name> [enable|disable]
                 -- Modify 802.11h support
ap-bridge  : get ap-bridge <wlan name>
                 -- Display AP WLAN's wireless bridge mode
ap-bridge  : set ap-bridge <wlan name> [enable|disable]
                 -- Modify AP WLAN's wireless bridge mode
autoconfig : get autoconfig
                 -- Display Auto-Configuration State
autoconfig : set autoconfig <wlan name> options
                
autoprov   : get autoprov
                 -- Display Auto-Provision State
autoprov   : set autoprov options
                 -> [ enable | disable ]
                 -- Modify Auto-Provision State
beacon-interval : get beacon-interval <wlan name>
                 -- Get beacon interval
beacon-interval : set beacon-interval <wlan name> [100..1000]
                 -- Modify beacon interval
blacklist  : get blacklist <wifi name>
                 -- Get channel blacklist
blacklist  : set blacklist <wifi name> options
                 -> [ enable | disable  ]
                 -> [ clear ]
                 -> [ chan_num [1(temporary) | 0(clear) | -1(permanent)] ]
                 -> [ [rx_phyerr | util_busy | nf0hi | nf0lo] val ]
                 -- Set channel blacklist (add/remove a channel or clear all)
channel    : get channel <wifi name>
                 -- Displays the radio channel in use
channel    : set channel <wifi name> [channel number | auto]
                 -- Set the radio channel
countrycode : get countrycode
                 -- Get the country code
countrycode : set countrycode <code>
                 -- Set the country code, i.e. CA,US,HK,UK,JP...***Reboot Needed***
countryie  : get countryie <wifi name>
                 -- Get Country Information Element status
countryie  : set countryie <wifi name> [enable|disable]
                 -- Enable/Disable Country Information Element support
cwmode     : get cwmode <wifi name>
                 -- Get 11N channel width mode
cwmode     : set cwmode <wifi name> [0,2] (0=20Mhz, 2=40MHz)
                 -- Set 11N channel width mode
dfsmidbandblock : get dfsmidbandblock <wifi name>
                 -- Get DFS mid-band (UNI-11 2) block status
dfsmidbandblock : set dfsmidbandblock <wifi name> [enable|disable|
                 -- Set DFS mid-band (UNI-11 2) block status
dbstats    : get dbstats <wlan name>
                 -- Get the # of packets that are transferred from Bcast to Ucast.
directed-thr : get directed-thr <wlan name>
                 -- Get the upper limit on Directed Broadcast processing.
directed-thr : set directed-thr <wlan name> <new threshold>
                 -- Set the upper limit on Directed Broadcast processing (0 == disable)
dtim-period : get dtim-period <wlan name>
                 -- Get DTIM (Delivery Traffic Information Map) Period
dtim-period : set dtim-period <wlan name> [1..255]
                 -- Configure DTIM (Delivery Traffic Information Map) Period
dvlan      : get dvlan <wlan name>
                 -- Display AP WLAN's dynamic VLAN mode
dvlan      : set dvlan <wlan name> [enable|disable]
                 -- Modify AP WLAN's dynamic VLAN mode
encryption : get encryption <wlan name>
                 -- Display encryption configuration
encryption : set encryption <wlan name>
                 -- Interactive wizard to configure network encryption
event      : get event <wlan name>
                 -- Display Event-Configuration State
event      : set event <wlan name> options ...
                 -- Modify Event-Configuration State
extant     : get extant <wifi name>
                 -- Display external antenna mode
extant     : set extant <wifi name> [enable|disable|both]
                 -- Configure external antenna mode
frag-thr   : get frag-thr <wlan name>
                 -- Get fragmentation threshold
key        : get key <wifi name>
                 -- Display Key Info
leave      : set leave <wlan name>
                 -- Trigger the leave action on station interface
legacytxchainmask : get legacytxchainmask <wifi name>
                 -- Get 11N Legacy Transmit chainmask
legacytxchainmask : set legacytxchainmask <wifi name> [1|5|7]
                 -- Set 11N Legacy Transmit chainmask (1, 5, 7)
extantgain : get extantgain <wifi name>
                 -- get external antenna gain (dB)
extantgain : set extantgain <wifi name> <0 - 90dBi>
                 -- set external antenna gain (dB)
max-aid    : get max-aid <wlan name>
                 -- Get the allowed maximum assoc ID
max-aid    : set max-aid <wlan name> [value]
                 -- Set the allowed maximum assoc ID
mesh       : get mesh list
                 -- Get Mesh Neighbor List
mesh       : set mesh <auto | dormant | root | mesh | portbased>
                 -- Set Mesh state (Root AP, Mesh AP)
meshcfg    : set meshcfg [ssid|passphrase] <value>
                 -- Set Mesh SSID/PSK
mode       : get mode <wifi name>
                 -- Get Phy Mode of all wlan interfaces
mode       : set mode <wifi name> <radio mode>
                 -- Set Phy Mode of all wlan interfaces
mq         : get mq <wifi name>
                 -- Displays current Media Queue options
mq         : set mq <wifi name> options
                 -- Set the Media Queue hold time / credit / queuing options
mqstats    : get mqstats <wlan name> <assoc/all|nonassoc|def|mac_addr..>
                 -- Display Media Queue Statistics
mqstats    : set mqstats <wlan name>  clear [assoc/all|nonassoc|def|mac_addr..]
                 -- Clear Media Queue Statistics
nf         : get nf
                 -- Get refreshed 11N Noisefloor
nfmin      : get nfmin <wifi name>
                 -- Get 11N Min Noisefloor Limit Value
capture    : get capture <wlan name> [state|copy <desthost> <destfile>]
                 -- Get Packet Capture state/copy
capture    : set capture <wlan name> [idle | [stream|local][-no[b][c][d][p]] <filter>]
                 -- Set Packet Capture state/filter
passphrase : get passphrase <wlan name>
                 -- Display WPA PassPhrase
preferredap : get preferredap <wlan name>
                 -- Get Preferred AP
preferredap : set preferredap <wlan name> <xx:xx:xx:xx:xx:xx>
                 -- Set Preferred AP
preferredapmode : get preferredapmode <wlan name>
                 -- Get Preferred AP Mode
preferredapmode : set preferredapmode <wlan name> [preferred|locked]
                 -- Set Preferred AP Mode
prot-mode  : get prot-mode <wifi name>
                 -- Get protection mode for 11b/11g
prot-mode  : set prot-mode <wifi name> [none|cts-only|rts-cts]
                 -- Set protection mode for 11b/11g
rescan     : get rescan <wifi name>
                 -- Get rescan settings
rescan     : set rescan <wifi name> options
                 -- Set rescan settings
rftest     : set rftest <wifi name> <channel> [val] <startnf> [val] <endnf> [val] <dur> [val] <fname> [val] -- Set noise floor and sample air time statistics
airtime    : get airtime <wifi name> [reset|noreset] [raw] -- Get airtime utilization statistics
rts-thr    : get rts-thr <wlan name>
                 -- Get Request to Send threshold
rts-thr    : set rts-thr <wlan name> <disable | [1..65535]>
                 -- Modify Request to Send threshold
rxchainmask : get rxchainmask <wifi name>
                 -- Get 11N Receive chainmask
rxchainmask : set rxchainmask <wifi name> [1|3|5|7]
                 -- Set 11N Receive chainmask (1, 3, 5, 7)
scanap     : get scanap <wlan name>
                 -- Get Scan Results
scanap     : set scanap <wlan name>
                 -- Set Immediate Scan
schedstats : get schedstats <wlan name> <TBD..>
                 -- Display Scheduler Statistics
ssid       : get ssid <wlan name>
                 -- Display Service Set Identifier
ssid       : set ssid <wlan name> <service-set-identifer>
                 -- Set the Service Set Identifier
ssid-suppress : get ssid-suppress <wlan name>
                 -- Is SSID allowed in control frames?
ssid-suppress : set ssid-suppress <wlan name> [enable|disable]
                 -- Allow/Disallow SSID in control frames
state      : get state <wlan name>
                 -- Get state of wlan interface
state      : set state <wlan name> [up | down]
                 -- Set state of wlan interface
station    : get station <wlan name> [list|info|stats] [all|mac_addr...]
                 -- Get station information
station    : set station <wlan name> options
                 -> stats clear [all|mac_addr...]
                 -> vlan <vlan id> <mac addr>
                 -- Set station information
txchainmask : get txchainmask <wifi name>
                 -- Get 11N Transmit chainmask
txchainmask : set txchainmask <wifi name> [1|3|5|7]
                 -- Set 11N Transmit chainmask (1, 3, 5, 7)
txpower    : get txpower <wifi name>
                 -- Get transmit power
txpower    : set txpower <wifi name> <max | half | quarter | eighth | min>
                 -- Set transmit power
uplink     : get uplink <wlan name>
                 --- Get the wireless uplink status
wds-mode   : get wds-mode <wlan name>
                 -- Get Wireless Distribution Service Mode
wds-mode   : set wds-mode <wlan name> [enable|disable]
                 -- Set Wireless Distribution Service Mode
wlanlist   : get wlanlist
                 -- List all wlan interfaces and user defined names
wlantext   : get wlantext <wlan name>
                 -- Get the interface description
wlantext   : set wlantext <wlan name> text
                 -- Set the interface description
wmm        : get wmm <wlan name>
                 -- Get EDCA QoS control status
wmm        : set wmm <wlan name> [enable|disable]
                 -- Enable EDCA QoS control
wmm-params : set wmm-param <wlan name> [ap|bss] [vo|vi|be|bk] <cwmin> <cwmax> <aifs>
                 -- Configure EDCA QoS controls
zaxis      : get zaxis <wifi name>
                 -- Get Z Axis Antenna status
zaxis      : set zaxis <wifi name> [enable|disable]
                 -- Enable Z Axis Antenna
OK
rkscli:

"""

import re

from RuckusAutoTest.components.lib.apcli.cli_regex import *
from RuckusAutoTest.common.utils import *
#
# 
#

def get_ssid(ap_cli, wlan_id,force_ssh=False, **kwargs):
    regex = {'ssid': WLAN_SSID}
    cmd = "get ssid %s" % wlan_id
    if force_ssh:
        return execute_cmd(ap_cli, cmd, regex,force_ssh=True, **kwargs)
    else:
        return execute_cmd(ap_cli, cmd, regex,**kwargs)

def get_passphrase(ap_cli, wlan_id, **kwargs):
    regex = {'passphrase': WLAN_PASSPHRASE}
    cmd = "get passphrase %s" % wlan_id
    return execute_cmd(ap_cli, cmd, regex, **kwargs)

#@author:yuyanan @since:2014-8-4 bug zf-9011 add process when wlan ssid contain space
def get_wlanlist(ap_cli, force_ssh=False,**kwargs):
    cmd = "get wlanlist"
    if force_ssh:
        result = ap_cli.cmd(cmd,force_ssh=force_ssh)
    else:
        result = ap_cli.cmd(cmd)
    column_name_list = [x.lower() for x in result[0].split()]
    wlans_info = [x.split() for x in result if re.search('([0-9a-fA-F:]{17})', x)]
    
    wlans_list = []
    for wlan in wlans_info:
        if len(column_name_list) - len(wlan) > 0:
            for i in range(0,(len(column_name_list) - len(wlan))):
                wlan.append("")
        wlan_info = dict(zip(column_name_list,wlan))
        if force_ssh:
            wlan_info['ssid'] = ap_cli.get_ssid(wlan_info['wlanid'],force_ssh=True)
        else:
            wlan_info['ssid'] = ap_cli.get_ssid(wlan_info['wlanid'])
        
        wlans_list.append(wlan_info)

    return wlans_list

def get_rudb_by_wlan_id(ap_cli, wlan_id):
    """
    @author: Jane.Guo
    @since: 2013-5-10 for Force DHCP feature
    """    
#    cmd = "get rudb " + str(wlan_id) + " all"
#    result = ap_cli.cmd(cmd)
#    column_name_list = result[0].split()
#    rudb_all_info = [x.split() for x in result if re.search('([0-9a-fA-F]{8} \d* \d*)', x)]
#    
#    rudb_list = []
#    for rudb in rudb_all_info:
#        rudb_info = {}
#        for idx in range (0, len(rudb)):
#            rudb_info[column_name_list[idx].lower()] = rudb[idx]
#        rudb_list.append(dict(rudb_info))
#    
#    return rudb_list  
#
    #@author: Anzuo, @change: there is no "get rudb" cmd, use "get client-info" instead, @since: 2014-02-18
    cmd = "get client-info " + str(wlan_id)
    res = ap_cli.cmd(cmd)
    
    client_info_list = []

#    #@ZJ20150216 ZF-12129

    m = re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', ap_cli.get_version())
    if m.group(0) in ['9.9.0.99','0.0.0.99','9.10.0.0','9.12.0.0'] :
    #@ZJ20150216 ZF-12129
        b_idx = 0
        e_idx = 0
        regx = "([0-9|a-z|A-Z]{2}\:){5}[0-9|a-z|A-Z]{2}"
        for item in res:
            if re.search(regx, item):
                client_info = {}
                client_info['Mac'] = re.search(regx, item).group()
                b_idx = res.index(item, e_idx)
            elif re.search("}", item.strip()):
                e_idx = res.index(item, b_idx)
                tmp_list = res[b_idx+1:e_idx]
                #generate a dict by using each item of list, remove all spaces of key and value
                tmp_dict = dict(x.replace(re.search(' *: *', x).group(), ':').strip().split(':') for x in tmp_list)
                client_info.update(tmp_dict)
                client_info_list.append(client_info)
    else:
        column_name_list = res[0].split()
        count = len(column_name_list)
        for i in range(2, len(res)):
            if "---" in res[i]:
                break
            else:
                client_info = {}
                tmp = res[i].split('  ')#for string like "windows XP"
                for j in range(len(tmp)):
                    tmp[j] = tmp[j].strip()
                for k in range(tmp.count('')):
                    tmp.remove('')
                if len(tmp) != count:
                    raise Exception("the counts of column and content are different: \n %s" % res)
                
                for l in range(count):
                    client_info[column_name_list[l].lower()] = tmp[l]
                
                client_info_list.append(dict(client_info))
    return client_info_list
    

def get_force_dhcp_by_ssid(ap_cli, ssid, **kwargs):
    """
        Add for Force DHCP feature, can add other options
        @author: Jane.Guo
        @since: 2013-5-7

        rkscli: get force-dhcp wlan32
        Force DHCP is Enabled
        OK
    """
    wlans_list = get_wlanlist(ap_cli)
    new_wlans_list = []
    
    for wlan in wlans_list:
        if wlan['ssid'] == ssid:
            wlanid = wlan['wlanid']
            regex = {'force_dhcp': WLAN_FORCE_DHCP}
            cmd = "get force-dhcp %s" % wlanid
            result = execute_cmd(ap_cli, cmd, regex, **kwargs)
            wlan['force_dhcp'] = result['force_dhcp'][0]
            new_wlans_list.append(dict(wlan))   
    return new_wlans_list

def get_bssid_by_ssid_radio(ap_cli, ssid, radio, **kwargs):
    """
        Get bssid by ssid and radio, radio is 0 or 1
        @author: Jane.Guo
        @since: 2013-7-19

        [{'status': 'up', 
'name': 'wlan0', 
'bssid': '54:3d:37:10:57:08', 
'wlanid': 'wlan0', 
'type': 'AP', 
'radioid': '0', 
'ssid': 'Rqa-rat-client-isolation'
}]
        OK
    """
    wlan_list = get_wlanlist(ap_cli)
        
    for wlan in wlan_list:
        if wlan['status'] == 'up' and wlan['ssid'] == ssid and int(wlan['radioid']) == radio:
            bssid = wlan['bssid']
            logging.info("Get bssid is %s" % bssid)
            if bssid == '00:00:00:00:00:00':
                logging.info('Get wlan list is %s'%wlan_list)
            return bssid
        
    logging.error("Can't find bssid from %s" % wlan_list)
    return ""

def get_interface_list(ap_cli):
    cmd = 'get interface'
    res = ap_cli.cmd(cmd)
    header = res[0].split()
    body = res[2:-1]
    iflist = []
    for tr in body:
        tds = tr.split()
        item = {}
        for i in range(len(header)):                    
            td = tds[i]
            h = header[i]
            item[h] = td
        iflist.append(item)
        
    return iflist

def get_interface(ap_cli, wlan_id = 'wlan0'):
    cmd = 'get interface %s' % wlan_id
    res = ap_cli.cmd(cmd)
    header = res[0].split()
    body = res[2:-1]
    iflist = []
    for tr in body:
        tds = tr.split()
        item = {}
        for i in range(len(header)):                    
            td = tds[i]
            h = header[i]
            item[h] = td
        iflist.append(item)
        
    return iflist[0]

def get_recovery_ssid(ap_cli):
    cmd = 'get recovery-ssid'
    res = ap_cli.do_cmd(cmd)
    timeout = re.findall('Timeout\s+:\s+([\d]+)\s?second', res)
    service_wlan = re.findall('Service WLAN\s+:\s+(enabled|disabled)', res)
    return {'raw_info': res,
            'timeout': timeout[0] if timeout else '',
            'service_wlan': service_wlan[0] if service_wlan else ''}


def set_ssid(ap_cli, wlan_id,ssid):
    cmd = "set ssid %s %s" % (wlan_id,ssid)
    return execute_cmd(ap_cli, cmd,{})

def set_auto_detected_blacklist(ap_cli,wifi_if='wifi0',open=True):
    enable='enable'
    if not open:
        enable = 'disable'
    cmd='set blacklist %s %s'%(wifi_if,enable)
    res = ap_cli.do_cmd(cmd)
    if 'OK' in res:
        return True
    else:
        return False
    
def clear_blacklist(ap_cli,wifi_if='wifi0'):
    cmd='set blacklist %s clear'%(wifi_if)
    res = ap_cli.do_cmd(cmd)
    if 'Clear blacklist for wifi0 ok' in res:
        return True
    else:
        return False

def set_wifi_if_blacklist(ap_cli,channel_list,wifi_if):
    res=set_auto_detected_blacklist(ap_cli,wifi_if,False)
    if not res:
        logging.error('close auto detect blacklist failed')
        return res
    res=clear_blacklist(ap_cli,wifi_if)
    if not res:
        logging.error('clear blacklist failed')
        return res
    err_list=[]
    for channel in channel_list:
        res=_add_channel_to_blacklist(ap_cli,channel,wifi_if)
        if not res:
            err_list.append(channel)
    if err_list:
        logging.error('the channels not add to blacklist successfully: %s'%err_list)
        return False
    return True

def get_wifi_if_blacklist(ap_cli,wifi_if):
    channel_list=[]
    str = '%s Blacklisted Channel: '%wifi_if
    cmd = 'get blacklist %s'%wifi_if
    res = ap_cli.do_cmd(cmd)
    l=res.split(str)
    if len(l)==1:
        logging.info('no blacklist get ')
    else:
        for i in range(1,len(l)):
            channel_list.append(l[i].split('   (User-specified)')[0].strip())
        logging.info('blacklist get %s'%channel_list)
    return channel_list 

def verify_black_list_channel(ap_cli,channel_list,wifi_if):
    black_list_get=get_wifi_if_blacklist(ap_cli,wifi_if)
    available_channel_list=get_available_channel_list(ap_cli,wifi_if)
    for channel in channel_list:
        if (str(channel) in available_channel_list) or (str(channel) not in black_list_get):
            return False
    return True


def verify_available_channel_list(ap_cli,channel_list,wifi_if):
    black_list_get=get_wifi_if_blacklist(ap_cli,wifi_if)
    logging.info('blacklist got %s'%black_list_get)
    available_channel_list=get_available_channel_list(ap_cli,wifi_if)
    logging.info('available channel list got %s'%available_channel_list)
    if len(available_channel_list)!=len(channel_list):
        logging.error('channel list length not correct(verified-%s,got-%s)'%(len(channel_list),len(available_channel_list)))
        return False
    for channel in channel_list:
        if (str(channel) not in available_channel_list) or (str(channel) in black_list_get):
            return False
    return True


def get_available_channel_list(ap_cli,wifi_if):
    channel_list=[]
    cmd='set channel %s'%wifi_if
    res = ap_cli.do_cmd(cmd)
    l= res.split('*')
    if len(l)==1:
        logging.info('no avaliable channel list get ')
    else:
        for i in range(1,len(l)):
            channel_list.append(l[i].split('(')[0].strip())
        logging.info('avaliable channel list get %s'%channel_list)
    return channel_list 

def get_mesh_list(ap_cli):
    """
    This function suport to execute the command 'get mesh list'.
    Return a dictionary as:
    {'N': {'c0:c5:20:3b:81:00': {'AdvUpl': '260.00',
                             'BSSID': 'c0:c5:20:bb:81:07',
                             'CalcUpl': '226.00',
                             'Ch': '153',
                             'D': '1',
                             'Flt': 's',
                             'IF': '-',
                             'IP': '192.168.0.140',
                             'LastSeen': '16202',
                             'Management-MAC': 'c0:c5:20:3b:81:00',
                             'RSSI/UL/NF': '79/81/-111',
                             'S': 'N',
                             'SSID': 'Mesh-431103001647',
                             'Seen': '24',
                             'SmpUpl': '226.00',
                             'UR': '*'}},
 'R': {'c0:c5:20:3b:81:50': {'AdvUpl': '260.00',
                             'BSSID': 'c0:c5:20:3b:81:50',
                             'CalcUpl': '260.00',
                             'Ch': '157',
                             'D': '1',
                             'Flt': 'l',
                             'IF': '-',
                             'IP': '192.168.0.139',
                             'LastSeen': '19509',
                             'Management-MAC': 'c0:c5:20:3b:81:50',
                             'RSSI/UL/NF': '0/00/0',
                             'S': 'R',
                             'SSID': 'Mesh-431103001647',
                             'Seen': '0',
                             'SmpUpl': '0.00',
                             'UR': '*'}}}

    @since: Jun 2013
    @author: An Nguyen
    """
    mesh_list = {}
    cmd = 'get mesh list'
    val = ap_cli.cmd(cmd)
    rex = '([a-fA-F0-9:]{17})\s+(\w+)\s+.*([a-fA-F0-9:]{17}).*'
    for v in val:
        rv = re.findall(rex, v)
        if not rv:
            continue
        if not mesh_list.get(rv[0][1]):
            mesh_list[rv[0][1]] = {}
        mesh_list[rv[0][1]].update({rv[0][2]:dict(zip(val[0].split(), v.split()))})
    
    return mesh_list
            
#
#
#

def _add_channel_to_blacklist(ap_cli,channel,wifi_if='wifi0'):
    cmd = 'set blacklist %s %s -1'%(wifi_if,channel)
    res = ap_cli.do_cmd(cmd)
    if 'OK' in res:
        return True
    else:
        return False

def map_media_queue_info(ap_cli, media = ""):
    """
        @author: Jane.Guo
        @since: 2013-08
        Fixed bug ZF-4218
        The output of 'get mqstats wlan0 all' changed from 9.7.0.0.84
        
        rkscli: get mqstats wlan0 all

9.7.0.0.84
VAP: 50:a7:33:1e:47:c8
------------------------------------------------------------------------------------------
             Qued  ovrflw        enq        deq     reenq      deact   XRetries XTlimits
mgmt VO( 0) X:   0      0          0          0         0          0          0        0
mgmt VI( 0) X:   0      0          0          0         0          0          0        0
mgmt BE( 0) X:   0      0          0          0         0          0          0        0
mgmt BK( 0) X:   0      0          0          0         0          0          0        0
data VO( 2) X:   0      0          0          0         0          0          0        0
data VI( 6) X:   0      0          0          0         0          0          0        0
data BE(10) X:   0      0          0          0         0          0          0        0
data BK(14) X:   0      0          0          0         0          0          0        0

STA: None
------------------------------------------------------------------------------------------
        Qued  ovrflw        enq        deq     reenq      deact   XRetries XTlimits
deflt(15) X:   0      0         44         44         0         44          0        0
OK

9.7.0.0.35
rkscli: get mqstats wlan0 all

VAP: 50:a7:33:1e:47:c8
------------------------------------------------------------------------------------------
        Qued  ovrflw        enq        deq     reenq      deact   XRetries XTlimits
mgmnt( 0) X:   0      0          0          0         0          0          0        0
voice( 2) X:   0      0          0          0         0          0          0        0
video( 6) X:   0      0          0          0         0          0          0        0
data(10) X:   0      0          0          0         0          0          0        0
bkgnd(14) X:   0      0          0          0         0          0          0        0

STA: None
------------------------------------------------------------------------------------------
        Qued  ovrflw        enq        deq     reenq      deact   XRetries XTlimits
deflt(15) X:   0      0        488        500        12        494          0       17
OK

    """
    map_dict = {'voice':'data VO',
                'video':'data VI',
                'data':'data BE',
                'bkgnd':'data BK',}
    
    #@author: Jane.Guo @since: 2013-09 use common function to compare version
#    newv_list = ['9.5.0.5.71','9.7.0.0.84','0.0.0.99.738','9.9.0.99.1000','9.9.0.0.29']
#@ZJ 20140814 FIX FOR VERSION 99
    newv_list = ['9.9.0.0.29','9.8.0.0.10']
    version = ap_cli.get_version()
    res = compare_version_list(version, newv_list)
    map_media = ''
    if res >= 0:
        for key in map_dict:
            if key == media:
                map_media = map_dict[key]
                break
                
    if not map_media:
        map_media = media
    
    logging.info('[map_media_queue_info]Change media type value from %s to %s'%(media, map_media))
    return map_media

def get_client_isolation_by_ssid(ap_cli, ssid, **kwargs):
    """
        Only support ZD version in and after 9.7
        @author: Jane.Guo
        @since: 2013-5-7

        rkscli: get ci wlan0
        wlan0 Client Isolation Mode  : Enabled
         
        Client Isolation Filter Mode : Source MAC & IP based ARP filters active
        11:11:11:11:11:11     192.168.0.2
        OK
    """
    wlans_list = get_wlanlist(ap_cli)
    new_wlans_list = []
    
    for wlan in wlans_list:
        if wlan['ssid'] == ssid:
            wlanid = wlan['wlanid']
            cmd = "get ci %s" % wlanid
            regex = {'mode': CLIENT_ISOLATION_MODE,
                    'filter_mode': CLIENT_ISOLATION_FILTER_MODE,
                    'filter_acl': CLIENT_ISOLATION_FILTER_ACL,}
            result = execute_cmd(ap_cli, cmd, regex, **kwargs) 
            logging.info('get client isolation of ssid [%s] is [%s]' % (ssid, result))
            if result.get('filter_acl'):
                if result.get('filter_acl') == 'DID NOT EXIST':
                    return {}
                for idx in range(len(result.get('filter_acl'))):
                    result['filter_acl'][idx] = result['filter_acl'][idx].replace(' ','')
            wlan['client_isolation'] = result
            new_wlans_list.append(wlan)   
    return new_wlans_list
