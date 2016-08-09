# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library support to execute the command under shell mode

"""

import re
import time
import logging

from RuckusAutoTest.common import lib_Constant as const
#
# 
#

def do_shell_cmd(ap, cmd, **kwargs):
    """
    """    
    ap.goto_shell()
    result = ap.do_cmd(cmd, prompt = "#")
    ap.exit_shell()
    return result
    
def set_meshd_option(ap, option, value = '', **kwargs):
    """
    """
    meshd_cmd = "meshd -%s %s"  % (option, value)
    do_shell_cmd(ap, meshd_cmd)

def read_mlog(ap, keyword = '', **kwargs):
    """
    """
    read_cmd = "mlogread |grep %s" % keyword if keyword else "mlogread"
    value = do_shell_cmd(ap, read_cmd)
    
    return value

def get_arping_log(ap, **kwargs):
    """
    """
    return read_mlog(ap, "arping")

def get_ndisc6_log(ap, **kwargs):
    """
    """
    return read_mlog(ap, 'ndisc6')

def set_bangradar(ap, interface = 'wifi1', **kwargs):
    """
    For AP dual bands the 5G interface is wifi1
    For AP single band the 5G interface is wifi0
    """
    cmd = "radartool -i %s bangradar" % interface
    do_shell_cmd(ap, cmd) 
    
def get_blocked_dfs_channel(ap, interface = 'wifi1', **kwargs):
    """
    For AP dual bands the 5G interface is wifi1
    For AP single band the 5G interface is wifi0
    """
    cmd = "radartool -i %s shownol" % interface
    info =  do_shell_cmd(ap, cmd)
    blocked_list = re.findall('(\d+)\s+(\d+)\s+\d+', info)
    blocked_channels = []
    for channel, time in blocked_list:
        blocked_channels.append({'channel': channel,
                                 'remain_time': time})
        
    return {'raw_info': info, 'blocked_channels': blocked_channels}


def get_radio_tx_power(ap,radio):
    if radio not in [5,2.4,'5','2.4']:
        raise('wrong parameter radio:%s'%radio)
    ap.goto_shell()
    buf = ap.cmd("iwconfig", prompt = "#")
    ap.exit_shell()
    radio_str='Frequency:%s'%radio
    for lineNum in range(len(buf)):
        if radio_str in buf[lineNum]:
            power=int(buf[lineNum].split()[4].split(':')[1])
            logging.info('power is %s'%power)
            break
    logging.info('radio %s power is %s'%(radio,power))
    return power

# @author: Xu, Yang 
# @since: 2013-7-22 Parse the 'wifi * Frequency:* Tx-Power:*' line output of the 'iwconfig',
# return Frequency and Tx-Power values of 2.4G and 5G as
# {'2.4G': {'Frequency':Freq24, 'Channel':str(channel24), 'Power':power24}, '5G': {'Frequency':Freq5,'Channel':str(channel5),'Power':power5}}
def get_2radio_tx_power(ap):
    """
    @return
    {'2.4G': {'Frequency':Freq24, 'Channel':str(channel24), 'Power':power24}, '5G': {'Frequency':Freq5,'Channel':str(channel5),'Power':power5}}
    Freq24 is str
    channel24 is int, 'Channel' key's value has been string -- str(channel24)
    power24 is int
    """
    ap.goto_shell()
    buf = ap.cmd("iwconfig", prompt = "#")
    ap.exit_shell()
    
    Freq24 = Freq5 = '0'
    channel24 = power24 = channel5 = power5 = 0
    for lineNum in range(len(buf)):
        line = buf[lineNum]
        if  ('wifi' in line) and ('Frequency:2.4' in line):
            Freq24=str(buf[lineNum].split()[2].split(':')[1])
            power24=int(buf[lineNum].split()[4].split(':')[1])
            
            channel24 = const.d24GFreq2Chan[int(float(Freq24)*1000)]
            logging.info('%s G, Channel %s , txPower is %s'% (Freq24, channel24, power24))
            continue

        if  ('wifi' in line) and ('Frequency:5' in line):
            Freq5=str(buf[lineNum].split()[2].split(':')[1])
            power5=int(buf[lineNum].split()[4].split(':')[1])

            channel5 = const.d5GFreq2Chan[int(float(Freq5)*1000)]
            logging.info('%s G, Channel %s , txPower is %s'% (Freq5, channel5, power5))
            break
    
    return {'2.4G': {'Frequency':Freq24, 'Channel':str(channel24), 'Power':power24}, '5G': {'Frequency':Freq5,'Channel':str(channel5),'Power':power5}}


def get_radio_band(ap):
    '''
    dule band ap return 2
    single band ap return 1
    '''
    res = do_shell_cmd(ap,'iwconfig')
    if 'wifi1' in res:
        return 2
    else:
        return 1
    
def get_single_dule_band_aps_list(ap_list):
    single_list=[]
    dule_list=[]
    for ap in ap_list:
        if 1==get_radio_band(ap):
            single_list.append(ap)
        else:
            dule_list.append(ap)
    return single_list,dule_list

def enable_all_debug_log(ap):
    """
    enable all debug log on ap by command:
        apmgrinfo -d 7 -m all
    """
    cmd = 'apmgrinfo -d 7 -m all'
    return do_shell_cmd(ap, cmd)

def read_log(ap, keyword = '', **kwargs):
    """
    """
    read_cmd = "logread |grep %s" % keyword if keyword else "logread"
    value = do_shell_cmd(ap, read_cmd)
    
    return value

def read_comming_log(ap, keyword = '', reading_time = 60, **kwargs):
    """
    """
    raw = _read_comming_log(ap, keyword, reading_time, **kwargs)
    val = raw.strip().split('\r\n')
    return val

def enable_80211debug_mode(ap, wlan, scan=True):
    """
    Support to enable the 80211debug mode on AP shell  
    """
    cmd = '80211debug -i %s +scan' if scan else '80211debug -i %s -scan'
    return do_shell_cmd(ap, cmd % wlan)
#
#
#

def _read_comming_log(ap, keyword = '', reading_time = 60, **kwargs):
    """
    """
    ap.goto_shell()
    read_cmd = "logread -f |grep %s" % keyword if keyword else "logread -f"
    ap.tn.read_very_eager()
    logging.debug('[AP CMD INPUT] %s' % read_cmd)
    ap.tn.write(read_cmd + '\n')
    logging.info('sleep %s seconds' % reading_time)
    time.sleep(reading_time)
    ap.tn.write('\x03 \n')
    value = ap.expect_prompt(prompt = '#')
    logging.debug('[AP CMD OUTPUT] %s' % value)
    ap.exit_shell()
    
    return value