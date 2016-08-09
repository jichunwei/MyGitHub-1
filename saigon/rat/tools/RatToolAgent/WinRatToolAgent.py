# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

import os
import re
import sys
import platform
import time
import tempfile
import subprocess
from RuckusAD import RuckusAD
from SocketServer import TCPServer, StreamRequestHandler
from process import *

_service_port = 10010
_windump_cmd = "Windump.exe"
_windump_process = ""
_iperf_cmd = "iperf.exe"
_iperf_process = ""

def ping(target_ip, timeout_ms=1000):
    """
    ping performs a basic connectivity test to the specified target
    @param target_ip: An IP address to ping to
    @param tries: number of retry
    @param timeout_ms: maximum time for a ping to be done
    @return: "ok" if ping is done successfully; otherwise return a message
    """
    cmd = "ping %s -n 1 -w 1 > NUL" % (target_ip)

    timeout_s = timeout_ms/1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        err = os.system(cmd)
        current_time = time.time()
        if not err:
            return "%.1f" % (current_time-start_time)
        time.sleep(0.05)
    return "Timeout exceeded (%.1f seconds)" % timeout_s

def addIpIf(if_name, addr, mask):
    """
    Add a new IP interface to the Ethernet NIC
    @if_name: Name of the interface (e.g: "Local Area Connection")
    @param addr: IP address
    @param mask: subnet mask
    """
    cmd = "netsh interface ip add address \"%s\" %s %s" % (if_name, addr, mask)
    buf = [line.strip("\r").strip("\n") for line in os.popen(cmd)]
    ok = False
    for line in buf:
        if line == "Ok.":
            ok = True
            break
    if not ok and _getWinVer() == "51":
        raise Exception("".join(buf))
    time.sleep(5)

def _removeIpIf(if_name, addr):
    """
    Remove an IP interface from the Ethernet NIC
    @if_name: Name of the interface (e.g: "Local Area Connection")
    @param addr: IP address
    """
    cmd = "netsh interface ip del address \"%s\" %s" % (if_name, addr)
    buf = [line.strip("\r").strip("\n") for line in os.popen(cmd)]
    ok = False
    for line in buf:
        if line == "Ok.":
            ok = True
            break
    if not ok and _getWinVer() == "51":
        raise Exception("".join(buf))
    time.sleep(6)

def getIfInfo():
    """
    Get information about the interface configured with static ip address
    @return: a dictionation in format
        {'name of the interface' : [{'addr':'IP address', 'mask':'Subnet mask'}, ...]}
        or None if not found
    """
    cmd = "netsh interface ip show address"
    buf = [line.strip("\r").strip("\n").strip() for line in os.popen(cmd)]
    buf = [line for line in buf if line]
    temp = {}
    ip_info = []
    if_name = ""
    res = {}
    for line in buf:
        if line.startswith("Configuration for interface"):
            if_name = line.split('"')[1]
            temp = {}
            ip_info = []
            continue
        if line.startswith("IP Address"):
            temp['addr'] = line.split(':')[1].strip()
        elif line.startswith("Subnet"):
            temp['mask'] = line.split(':')[1].strip().split(')')[0]
        if len(temp) == 2:
            ip_info.append(temp)
            temp = {}
        if ip_info:
            res['%s' % if_name] = ip_info

    return res

def verifyIf(addr):
    """
    Ensure that there is only the given IP address is configured on the interface
    Remove other addresses
    @param addr: IP address of the interface needs to be verified
    """
    if_info = getIfInfo()
    if not if_info:
        raise Exception("No interface configured with static ip address")
    for key, value in if_info.iteritems():
        if len(value) > 1:
            for inf in value:
                if inf['addr'] != addr:
                    _removeIpIf(key, inf['addr'])

def _getWinVer():
    """
    @return: Version of Windows on the system. "51" is Windows XP and "60" is Vista
    """
    win_ver_major, win_ver_minor, win_ver_build, win_ver_platform, win_ver_text = sys.getwindowsversion()
    return "%s%s" % (win_ver_major, win_ver_minor)

def loginAPWebUI(username, password, ip_addr):
    """
    Call the loginAP function in HttpClient module to perform login to AP WebUI
    @param username: username to login
    @param password: password to login
    @param ip_addr: ip address of AP
    """
    params = "{'username':'%s', 'password':'%s', 'ip_addr':'%s'}" % (username, password, ip_addr)
    output = os.popen("HttpClient.py loginAP \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def logoutAPWebUI(ip_addr):
    """
    Call the logoutAP in HttpClient module to perform logout from the AP WebUI
    """
    param = "{'ip_addr':'%s'}" % ip_addr
    output = os.popen("HttpClient.py logoutAP \"%s\"" % param)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def getAPWirelessStatus(ip_addr):
    """
    Call the getstatus function in HttpClient module to get wireless status from AP WebUI
    """
    param = "{'ip_addr':'%s'}" % ip_addr
    output = os.popen("HttpClient.py getstatus \"%s\"" % param)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)
    info = buffer.strip("\r").strip("\n").strip()
    return info

def verifyStaMGMT(ap_ip_addr, aid, sta_mac_addr):
    """
    Call the verifyStaMgmt function in HttpClient module to verify information of STA-Management on the AP WebUI
    """
    params = "{'ap_ip_addr':'%s', 'aid':%s, 'sta_mac_addr':'%s'}" % (ap_ip_addr, aid, sta_mac_addr)
    output = os.popen("HttpClient.py verifyStaMgmt \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)
    info = buffer.strip('\r').strip('\n').strip()
    return info

def loginADWebUI(ap_ip_addr, aid):
    """
    Call the loginAD function in HttpClient module to login to Adapter WebUI
    """
    params = "{'ap_ip_addr':'%s', 'aid':%s}" % (ap_ip_addr, aid)
    output = os.popen("HttpClient.py loginAD \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def getADEncryption(config, wlan_if):
    """
    Get wlan configuration information on the adapter on the specific interface
    Return a dictionary of wlan information
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.getEncryption(wlan_if)
    time.sleep(1)
    return res

def configWlan(config, wlan_cfg):
    """
    Create a wlan on the adapter
    @param wlan_cfg: a dictionary of wlan parameters
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.configWlan(wlan_cfg)
    time.sleep(2)

def setRuckusADState(config, state, wlan_if):
    """
    Telnet to the Ruckus Adapter and set status for svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.setState(wlan_if, state)
    time.sleep(2)

def getRuckusADState(config, wlan_if):
    """
    Telnet to the Ruckus Adapter and get status of svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.getState(wlan_if)
    time.sleep(1)
    return res

def getADWirelessMac(config):
    """
    Telnet to the Adapter and get mac address of wlan0
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.getWirelessMac()
    time.sleep(1)
    return res

def setADSSIDWebUI(config, ssid, is_vf7111):
    """
    Login to Adapter WebUI and change SSID value
    """
    ad_obj = RuckusAD(config)
    ad_obj.setSSIDWebUI(ssid, is_vf7111)
    time.sleep(3)

def setADEncryptionWebUI(config, encryption_cfg, is_vf7111):
    """
    Login to Adapter WebUI and set encryption method for adapter
    Please refer to the set_encryption_web_ui on RuckusAD for detail of parameters
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_encryption_web_ui(encryption_cfg, is_vf7111)
    time.sleep(3)

def getADDeviceStatusWebUI(config):
    """
    Get status of adapter from WebUI
    @return a dictionary of device information
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.getDeviceStatusWebUI()
    time.sleep(2)
    return res

def setADSystemNameWebUI(config, system_name):
    """
    Set system name for adapter from its WebUI
    """
    ad_obj = RuckusAD(config)
    ad_obj.setSystemNameWebUI(system_name)
    time.sleep(2)

def setADHomeProtectionWebUI(config, enable):
    """
    Set Home Protection status for adapter from its WebUI
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_home_protection(enable)
    time.sleep(2)

def setADSSID(config, wlan_if, ssid):
    """
    Set SSID value for the specific interface on the adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.setSSID(wlan_if, ssid)
    time.sleep(2)

def getADHomeLoginInfo(config):
    """
    Get Home login information from WebUI
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_home_login_info()
    time.sleep(2)
    return res

def startWindump(ip_addr = "", count = "", proto = "", file_path = "", host = ""):
    """
    Start tcpdump to capture traffic on the specific interface with given configuration
    - ip_addr: used to find exactly interface to capture
    - count: the maximum packets that satisfy requirement are captured
    - file_path: path of file that saves capturing information
    - host: specify ip address (destination or source) to capture
    """
    global _windump_process
    # Find interface's name to capture
    inf = ""
    if_list = os.popen("%s -D" % _windump_cmd).readlines()
    for inf in if_list:
        if ip_addr in inf:
            inf = inf.split(".")[0]
            break
    print "Found interface for capture is: %s " % inf

    cmd = "%s -i %s -vv -nn" % (_windump_cmd, inf)
    cmd = "%s -w %s" % (cmd, file_path)
    if count: cmd = "%s -c %s" % (cmd, count)
    if proto: cmd = "%s %s" % (cmd, proto)
    if host: cmd = "%s host %s" % (cmd, host)

    print cmd
    stopWindump()
    _windump_process = createProcess(cmd)

def stopWindump():
    """ Stop Windump by killing process """
    global _windump_process
    if _windump_process:
        _windump_process.kill()
        _windump_process = ""

def analyzeTraffic(file_path, proto = "UDP", get_qos = True):
    """
    Analyze traffic that captured by tcpdump
    Return a list of dictionaries, in there each dictionary contains source ip address, destination ipaddress
    and tos value of each packet.
    """
    traffic = os.popen("%s -vv -nn -r %s" % (_windump_cmd, file_path)).readlines()
    buf = [line.strip('\r').strip('\n') for line in traffic]
    traffic_info = []
    for item in buf:
        temp = {}
        src_ip_pat = ".*\) ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+) >.*"
        mobj  = re.match(src_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            temp['src_ip'] = ".".join(txt.split('.')[:-1])

        dst_ip_pat = ".* > ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+): %s.*" % proto
        mobj  = re.match(dst_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            temp['dst_ip'] = ".".join(txt.split('.')[:-1])

        tos_pat = ".*\(tos (0x[\w]+).*$"
        mobj  = re.match(tos_pat, item)
        if mobj:
            temp['tos'] = mobj.group(1)

        if len(temp) > 1:
            traffic_info.append(temp)

        if len(traffic_info) == 20:
            break

    return traffic_info

def startIperf(serv_addr = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = "", multicast_srv = False):
    """
    Execute iperf to send traffic with the given configuration
    - serv_addr: ipaddress of iperf server
    - test_udp: This is the bool value. If it's True, sent traffic is udp. Otherwise, sent traffic is tcp
    - packet_len: number of bytes of each packet
    - bw: bandwidth
    - timeout: maximum time to send traffic
    - tos: send traffic with ToS value
    - multicast_srv: option to bind multicast address to igmp table in the AP
    """
    global _iperf_process
    cmd = "%s -C" % _iperf_cmd
    if multicast_srv:
        cmd = "%s -s -B %s" % (cmd, serv_addr)
    else:
        if serv_addr: cmd = "%s -c %s" % (cmd, serv_addr)
        else: cmd = "%s -s" % cmd
    if test_udp: cmd = "%s -u" % cmd
    if packet_len: cmd = "%s -l %s" % (cmd, packet_len)
    if bw: cmd = "%s -b %s" % (cmd, bw)
    if timeout: cmd= "%s -t %s" % (cmd, timeout)
    if tos: cmd = "%s -S %s" % (cmd, tos)

    # Execute the command
    stopIperf()
    _iperf_process = createProcess(cmd)

def stopIperf():
    """
    Stop iperf on the windows by killing its process
    """
    global _iperf_process
    if _iperf_process:
        _iperf_process.kill()
        _iperf_process = ""

def addRoute(route = "", netmask = "", gateway = ""):
    """
    add multicast route which used to send multicast traffic with iperf
    - option: add or del
    """
    cmd = "route add %s mask %s %s" % (route, netmask, gateway)
    os.system(cmd)
    time.sleep(1)

def delRoute(route):
    cmd = "route delete %s" % route
    os.system(cmd)
    time.sleep(2)

class RatToolAgentHandler(StreamRequestHandler):
    """
    This class implements the command dispatcher. Its main duty is to receive commands from the client,
    execute them and return the result
    """
    def handle(self):
        print "Serving the client from " + str(self.client_address) + "\n"

        self.wfile.write("ok;Welcome to RAT Tool Agent\r\n")

        cmd_pattern = '([a-zA-Z0-9]+);(.*)'

        while True:
            time.sleep(1)
            try:
                data = self.rfile.readline().strip()
                if len(data) == 0: continue
                print "---> Received command: %s" % data

                obj = re.match(cmd_pattern, data)
                if obj:
                    cmd = obj.group(1)
                    param_str = obj.group(2).strip()
                else:
                    raise Exception("Invalid format")

                param_obj = {}
                if param_str:
                    param_obj = eval(param_str)

                if cmd == "quit":
                    self.wfile.write("ok;bye bye !!!\r\n")
                    break

                res = None
                exec("res = %s(**param_obj)" % cmd)
                print "---> Result: %s\n" % str(res)
                self.wfile.write("ok;%s\r\n" % str(res))

            except Exception, e:
                try:
                    self.wfile.write("error;%s\r\n" % e.message)
                except Exception, ex:
                    print "ERROR: %s" % ex.message
                    break
        # End of while
        print "Closed the connection\n"

def getIpConfig(adapter_name=""):
    """
    Return a dictionary with all the information of the current adapter or the given adapter_name
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a dictionary with the keys are parsed from the output of the command IPCONFIG /all
    """
    output = os.popen("ipconfig /all")
    found_name = False
    ip_info = {}
    for line in output:
        line = line.strip()
        if not line:
            if found_name and ip_info: break
            continue
        if line.find(adapter_name) != -1:
            found_name = True
        elif found_name:
            x = line.split(' :')
            tag = x[0].rstrip('. ')
            val = x[1].lstrip(' ')
            if tag == "IP Address" or tag == "IPv4 Address":
                ip_info['ip_addr'] = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                ip_info['mac_addr'] = ":".join(val.split("-"))
            elif tag == "Subnet Mask":
                ip_info['subnet_mask'] = val
            elif tag == "Lease Obtained":
                ip_info['lease_obtained'] = val
            elif tag == "Lease Expires":
                ip_info['lease_expires'] = val
            elif tag == "DHCP Server":
                ip_info['dhcp_server'] = val

    output.close()
    return ip_info

if __name__ == "__main__":
    server = TCPServer(("", _service_port), RatToolAgentHandler)
    print "RAT Tool Agent is listening on port %d ..." % _service_port
    server.serve_forever()
