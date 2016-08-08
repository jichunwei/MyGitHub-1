# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

import os
import re
import time
import tempfile
from RuckusAD import RuckusAD
from SocketServer import TCPServer, StreamRequestHandler

_service_port = 10010
_iperf_cmd = "./iperf"
_tcpdump_cmd = "tcpdump"
_tshark_cmd = "tshark"
_vconfig_cmd = "vconfig"
_zing_cmd = "./zing"


def ping(target_ip, timeout_ms = 1000, ping_params = ""):
    """
    ping performs a basic connectivity test to the specified target
    @param target_ip: An IP address to ping to
    @param tries: number of retry
    @param timeout_ms: maximum time for a ping to be done
    @param ping_params: additional ping params to the default, for e.g. from which eth
    @return: "ok" if ping is done successfully; otherwise return a message
    """
    cmd = "ping %s -c 1 -W 1 %s > /dev/null" % (target_ip, ping_params)

    timeout_s = timeout_ms / 1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        err = os.system(cmd)
        current_time = time.time()
        if not err:
            return "%.1f" % (current_time - start_time)

        time.sleep(0.05)

    return "Timeout exceeded (%.1f seconds)" % timeout_s


def start_iperf(
        serv_addr = "", test_udp = True, packet_len = "", bw = "", timeout = "",
        tos = "", multicast_srv = False
    ):
    """
    Execute iperf to send traffic with the given configuration
    - serv_addr: ip_address of iperf server
    - test_udp: This is the bool value. If it's True, sent traffic is udp. Otherwise, sent traffic is tcp
    - packet_len: number of bytes of each packet
    - bw: bandwidth
    - timeout: maximum time to send traffic
    - tos: send traffic with ToS value
    - multicast_srv: option to bind multicast address to igmp table in the AP
    """
    cmd = "%s -C" % _iperf_cmd
    if multicast_srv:
        cmd = "%s -s -B %s" % (cmd, serv_addr)

    else:
        if serv_addr:
            cmd = "%s -c %s" % (cmd, serv_addr)

        else:
            cmd = "%s -s" % cmd

    if test_udp:
        cmd = "%s -u" % cmd

    if packet_len:
        cmd = "%s -l %s" % (cmd, packet_len)

    if bw:
        cmd = "%s -b %s" % (cmd, bw)

    if timeout:
        cmd = "%s -t %s" % (cmd, timeout)

    if tos:
        cmd = "%s -S %s" % (cmd, tos)

    cmd = "%s &" % cmd
    # Execute the command
    os.system(cmd)


def stop_iperf():
    """
    Stop iperf by kill its process
    """
    # Find iperf process to kill
    fd, file_path = tempfile.mkstemp(".txt")
    os.system("ps aux | grep ./iperf > %s" % file_path)
    pfile = open("%s" % file_path, 'r')
    try:
        for line in pfile:
            if "iperf" in line:
                pid = line.split()[1]
                print("iperf process id %s" % pid)
                os.system("kill -9 %s" % pid)

    finally:
        pfile.close()

    os.remove(file_path)


def get_ip_cfg():
    """
    Get interface configuration.
    Return a dictionary that contains configuration information of each interface
    """
    cmd = "ifconfig -a"
    buf = [line.strip("\r").strip("\n").strip() for line in os.popen(cmd)]
    if_info = {}
    for line in buf:
        temp = {}
        if line.startswith('inet addr'):
            index = buf.index(line) - 1
            if not buf[index].startswith('lo'):
                inf = buf[index].split()[0]
                mac = buf[index].split()[-1]
                inet_addr = line.split()[1:]
                temp['ip_addr'] = inet_addr[0].split(':')[1]
                temp['mask'] = inet_addr[2].split(':')[1]
                if_info['%s' % inf] = temp

    return if_info


def set_route(option = "", ip_addr = "", net_mask = "", if_name = ""):
    """
    add/delete multicast route which used to send multicast traffic with iperf
    - option: add or del
    """
    cmd = "route %s -net %s netmask %s %s" % (option, ip_addr, net_mask, if_name)
    os.system(cmd)


def start_tcp_dump(ip_addr = "", count = "", proto = "", file_path = "", host = "", **args):
    """
    Start tcpdump to capture traffic on the specific interface with given configuration
    - ip_addr: used to find exactly interface to capture
    - count: the maximum packets that satisfy requirement are captured
    - file_path: path of file that saves capturing information
    - host: specify ip address (destination or source) to capture
    """
    # Find interface's name to capture
    inf = ""
    for key, value in get_ip_cfg().iteritems():
        if value['ip_addr'] == ip_addr:
            inf = key

    if ip_addr:
        cmd = "%s -i %s" % (_tcpdump_cmd, inf)

    else:
        cmd = "%s" % _tcpdump_cmd

    if not args.has_key('not_use_verbose'):
        cmd = "%s -vv" % cmd

    if args.has_key('snaplen'):
        cmd = "%s -s %s" % (cmd, args['snaplen'])

    if args.has_key('read'):
        cmd = "%s -r %s" % (cmd, args['file_to_read'])

    if args.has_key('print_content'):
        cmd = "%s -XX" % cmd

    if args.has_key('port'):
        cmd = "%s port %s" % (cmd, args['port'])

    if count:
        cmd = "%s -c %s" % (cmd, count)

    if proto:
        cmd = "%s %s" % (cmd, proto)

    if host:
        cmd = "%s host %s" % (cmd, host)

    cmd = "%s -nn" % cmd
    if args.has_key('write'):
        cmd = "%s -U -w %s" % (cmd, file_path)

    else:
        cmd = "%s > %s" % (cmd, file_path)

    cmd = "%s &" % cmd

    os.system(cmd)


def stop_tcp_dump():
    """
    Stop tcpdump by killing its process
    """
    # Find tcpdump process to kill
    fd, file_path = tempfile.mkstemp(".txt")
    os.system("ps aux | grep tcpdump > %s" % file_path)
    pfile = open("%s" % file_path, 'r')
    try:
        for line in pfile:
            if "tcpdump" in line:
                pid = line.split()[1]
                print("tcpdump process id %s" % pid)
                os.system("kill -9 %s" % pid)

    finally:
        pfile.close()

    os.remove(file_path)


def analyze_traffic(file, proto = "UDP", get_qos = True):
    """
    Analyze traffic that captured by tcpdump
    Return a list of dictionaries, in there each dictionary contains source ip address, destination ip_address
    and tos value of each packet.
    """
    fo = open(file, 'r')
    try:
        buf = [line.strip('\r').strip('\n') for line in fo]

    finally:
        fo.close()

    if get_qos:
        src_ip_pat = ".*\) ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+) >.*"
        dst_ip_pat = ".*> ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+):.*%s" % proto

    else:
        src_ip_pat = ".*\) ([\w]+\.[\w]+\.[\w]+\.[\w]+) >.*"
        dst_ip_pat = ".*> ([\w]+\.[\w]+\.[\w]+\.[\w]+):.*%s" % proto

    traffic_info = []
    for item in buf:
        temp = {}
        mobj = re.match(src_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            if len(txt.split('.')) != 4:
                temp['src_ip'] = ".".join(txt.split('.')[:-1])

            else:
                temp['src_ip'] = txt

        time.sleep(1)
        mobj = re.match(dst_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            if len(txt.split('.')) != 4:
                temp['dst_ip'] = ".".join(txt.split('.')[:-1])

            else:
                temp['dst_ip'] = txt

        time.sleep(1)
        if get_qos:
            tos_pat = ".*\(tos (0x[\w]+).*$"
            mobj = re.match(tos_pat, item)
            if mobj:
                temp['tos'] = mobj.group(1)

            if len(temp) == 3:
                traffic_info.append(temp)

        else:
            if len(temp) == 2:
                traffic_info.append(temp)

        if len(traffic_info) == 20:
            break

    time.sleep(2)
    os.remove(file)

    return traffic_info


def set_ruckus_ad_state(config, state, wlan_if):
    """
    Telnet to the Ruckus Adapter and set status for svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.set_state(wlan_if, state)


def get_ruckus_ad_state(config, wlan_if):
    """
    Telnet to the Ruckus Adapter and get status of svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_state(wlan_if)
    time.sleep(1)

    return res


def get_ad_wireless_mac(config):
    """
    Telnet to the Adapter and get mac address of wlan0
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_wireless_mac()
    time.sleep(1)

    return res


def get_ad_sta_mgmt(config, wlan_if):
    """
    Telnet to the adapter and get sta-mgmt status on the specified interface
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_sta_mgmt(wlan_if)
    time.sleep(2)

    return res


def set_ad_sta_mgmt(config, wlan_if, enabled):
    """
    Telnet to the adapter and set sta-mgmt status on the specified interface
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.set_sta_mgmt(wlan_if, enabled)
    time.sleep(2)


def get_ad_if_brd_config(config):
    """
    Telnet to the adapter and get interface configuration information at Linux shell
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_bridge_if_cfg()
    time.sleep(1)

    return res


def ping_from_ad(config, target_ip, timeout_ms = 1000):
    """
    Do a ping to the target ip address from the adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.ping(target_ip, timeout_ms)
    time.sleep(1)

    return res


def get_ad_encryption(config, wlan_if):
    """
    Get wlan configuration information on the adapter on the specific interface
    Return a dictionary of wlan information
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_encryption(wlan_if)
    time.sleep(1)

    return res


def cfg_wlan(config, wlan_cfg):
    """
    Create a wlan on the adapter
    @param wlan_cfg: a dictionary of wlan parameters
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.cfg_wlan(wlan_cfg)


def set_ad_ssid(config, wlan_if, ssid):
    """
    Set SSID value for the specific interface on the adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.set_ssid(wlan_if, ssid)
    time.sleep(2)


def get_ad_ssid(config, wlan_if):
    """
    Telnet to the adapter to get its SSID value
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_ssid(wlan_if)
    time.sleep(2)

    return res


def get_ad_serial_num(config):
    """
    Get Serial number of adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_serial_num()
    time.sleep(2)

    return res


def get_ad_version(config):
    """
    Get software version of adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_version()
    time.sleep(2)

    return res


def get_ad_device_type(config):
    ad_obj = RuckusAD(config)
    res = ad_obj.get_device_type()
    time.sleep(1)

    return res


def get_ad_base_mac(config):
    ad_obj = RuckusAD(config)
    res = ad_obj.get_base_mac()
    time.sleep(1)

    return res


def get_ad_channel(config, wlan_if):
    ad_obj = RuckusAD(config)
    channel, mode = ad_obj.get_channel(wlan_if)
    time.sleep(1)

    return channel, mode


def set_ad_channel(config, wlan_if, channel):
    ad_obj = RuckusAD(config)
    ad_obj.set_channel(wlan_if, channel)
    time.sleep(2)


def start_tcp_replay(if_name = "", file_name = "", rate = ""):
    """
    Start tcpreplay to resend pcap packets
    - if_name: interface use to sent packets
    - file_name: pcap file name
    """
    cmd = "tcpreplay -i %s %s" % (if_name, file_name)
    if rate:
        cmd = "%s -r %s" % (cmd, rate)

    os.system(cmd)
    time.sleep(5)


def capture_traffic_ota(ip_addr = "", filename = "", expression = "", host = "", count = ""):
    """
    Start tshark to capture traffic over the air on the specific interface with given configuration
    - ip_addr: used to find exactly interface to capture
    - count: the maximum packets that satisfy requirement are captured
    - file_path: path of file that saves capturing information
    - host: specify ip address (destination or source) to capture
    - expression: expression filter rule
    """
    # Find interface's name to capture
    try:
        stop_tshark()

    except:
        pass

    inf = ""
    for key, value in get_ip_cfg().iteritems():
        if value['ip_addr'] == ip_addr:
            inf = key

    cmd = "%s -i %s -V" % (_tshark_cmd, inf)
    if count:
        cmd = "%s -c %s" % (cmd, count)

    if expression:
        cmd = "%s %s %s" % (cmd, expression, host)

    cmd = "%s > %s" % (cmd, filename)
    cmd = "%s &" % cmd
    os.system(cmd)
    time.sleep(2)


def stop_tshark():
    """
    Stop tshark by killing its process
    """
    # Find tcpdump process to kill
    fd, file_path = tempfile.mkstemp(".txt")
    os.system("ps aux | grep tshark > %s" % file_path)
    pfile = open("%s" % file_path, 'r')
    try:
        for line in pfile:
            if "tshark" in line:
                pid = line.split()[1]
                print("tshark process id %s" % pid)
                os.system("kill -9 %s" % pid)

    finally:
        pfile.close()

    os.remove(file_path)
    time.sleep(2)


def analyze_traffic_ota(filename, dest_ip, src_ip):
    """
    Analyze traffic that captured by tshark
    Return a list of dictionaries, in there each dictionary contains destination ip_address and QoS Control field
    """
    try:
        stop_tshark()

    except:
        pass

    fo = open(filename, 'r')
    try:
        buf = [line.strip('\r').strip('\n') for line in fo]

    finally:
        fo.close()

    frame_pat = "Frame [0-9]+ \(.*"
    qos_pat = "Priority: [0-9]+ \(([a-zA-Z ]+)\).*"
    src_ip_addr = "Source: [0-9.]+ \(([0-9.]+)\)"
    dst_ip_addr = "Destination: [0-9.]+ \(([0-9.]+)\)"
    data_rate = "Data Rate: ([0-9]+\.[0-9]+) Mb/s"

    # Find total number of frames in captured file
    list_of_frame = []
    for line in buf:
        mobj = re.search(frame_pat, line)
        if mobj:
            list_of_frame.append(buf.index(line))

    # Find content of each frame
    temp_list = []
    traffic_ota_info = []
    for pos in range(len(list_of_frame)):
        each_frame = {}
        if pos == len(list_of_frame) - 1:
            temp_list = buf[int(list_of_frame[pos]):len(buf)]

        else:
            temp_list = buf[int(list_of_frame[pos]):int(list_of_frame[pos + 1])]

        for item in temp_list:
            mobj_qos = re.search(qos_pat, item)
            if mobj_qos:
                each_frame['qos'] = mobj_qos.group(1).lower()

            mobj_dest = re.search(dst_ip_addr, item)
            if mobj_dest:
                if mobj_dest.group(1) == dest_ip:
                    each_frame['dest_ip_addr'] = mobj_dest.group(1)

            mobj_src = re.search(src_ip_addr, item)
            if mobj_src:
                if mobj_src.group(1) == src_ip:
                    each_frame['src_ip_addr'] = mobj_src.group(1)

            mobj_data_rate = re.search(data_rate, item)
            if mobj_data_rate:
                each_frame['data_rate'] = mobj_data_rate.group(1)

        if len(each_frame) == 3 or len(each_frame) == 4:
            traffic_ota_info.append(each_frame)
            if len(traffic_ota_info) == 10:
                break

    time.sleep(2)
    os.remove(filename)

    return traffic_ota_info


def cfg_wlan_if(ip_addr = "", channel = ""):
    """
    Use tool iwconfig to config information for wlan interface on Linux PC.
    @ip_addr: used to find exactly wlan interface name
    @mode: operation mode of wlan interface, e.g: managed, monitor...
    @channel: operation channel of wlan inte
    """
    inf = ""
    for key, value in get_ip_cfg().iteritems():
        if value['ip_addr'] == ip_addr:
            inf = key

    os.system('ifconfig %s down' % inf)
    time.sleep(4)
    if channel:
        cmd = 'iwconfig %s channel %s' % (inf, channel)
        os.system(cmd)

    time.sleep(1)
    res = os.system('ifconfig %s up' % inf)
    if res:
        time.sleep(25)
        os.system('ifconfig %s up' % inf)


def set_vlan_qos(vlan_if = "", vlan_qos = "", egress_map = True):

    if egress_map:
        cmd = "%s set_egress_map" % _vconfig_cmd

    else:
        cmd = "%s set_ingress_map" % _vconfig_cmd

    cmd = "%s %s 0 %s" % (cmd, vlan_if, vlan_qos)
    os.system(cmd)
    time.sleep(2)


def start_zing(server_addr = "", pkt_gap = "", pkt_len = "", test_udp = True, timeout = "", tos = ""):
    """
    Execute zing to send traffic with the given configuration
    - serv_addr: ip_address of zing server
    - test_udp: This is the bool value. If it's True, sent traffic is udp. Otherwise, sent traffic is tcp
    - pkt_len: number of bytes of each packet
    - timeout: maximum time to send traffic
    - tos: send traffic with ToS value
    - pkt_gap: the delay between two continuous packets
    """
    if not server_addr:
        cmd = "%s --server" % _zing_cmd

    else:
        cmd = "%s --client %s" % (_zing_cmd, server_addr)

    if test_udp:
        cmd = "%s -u" % cmd

    else:
        cmd = "%s -p" % cmd

    if pkt_gap:
        cmd = "%s -d%s" % (cmd, pkt_gap)

    if pkt_len:
        cmd = "%s -l%s" % (cmd, pkt_len)

    if timeout:
        cmd = "%s -S%s" % (cmd, timeout)

    if tos:
        cmd = "%s -q%s" % (cmd, tos)

    cmd = "%s &" % cmd

    # Execute the command
    os.system(cmd)
    time.sleep(2)


def stop_zing():
    """
    Stop zing by kill its process
    """
    # Find iperf process to kill
    fd, file_path = tempfile.mkstemp(".txt")
    os.system("ps aux | grep ./zing > %s" % file_path)
    pfile = open("%s" % file_path, 'r')
    try:
        for line in pfile:
            if "zing" in line:
                pid = line.split()[1]
                print("zing process id %s" % pid)
                os.system("kill -9 %s" % pid)

    finally:
        pfile.close()

    os.remove(file_path)


def add_vlan(interface, vlan_id, ip_addr):
    '''
    '''
    vlan_interface = '%s.%s' % (interface, vlan_id)

    try:
        rem_vlan(vlan_interface)

    except:
        pass

    os.system('vconfig add %s %s' % (interface, vlan_id))
    time.sleep(1)

    # Assign ip address for this interface
    os.system('ifconfig %s %s' % (vlan_interface, ip_addr))
    os.system('ifconfig %s up' % vlan_interface)

    return vlan_interface


def rem_vlan(vlan_interface):
    '''
    '''
    os.system('ifconfig %s down' % vlan_interface)
    os.system('vconfig rem %s' % vlan_interface)
    time.sleep(2)


def add_sub_intf(interface, ip_addr, subid):
    '''
    '''
    subif = '%s:%s' % (interface, subid)
    try:
        rem_sub_intf(subif)

    except:
        pass

    os.system('ifconfig %s %s' % (subif, ip_addr))
    os.system('ifconfig %s up' % subif)
    time.sleep(1)

    return subif


def rem_sub_intf(subif):
    os.system('ifconfig %s down' % subif)
    time.sleep(1)


def set_ip_addr(interface, ip_addr):
    cmd = "ifconfig %s %s netmask 255\.255\.255\.0 up" % (interface, ip_addr)
    os.system(cmd)
    time.sleep(2)


def create_copy_image(build, path, name):
    os.system("cp %s%s %s%s" % (path, build, path, name))
    time.sleep(1)


def get_port_ftp_data_channel(pcapfile, src_ip, dst_ip):
    """
    args: proto, port, read, print_content, file_to_read
    """

    ft, filepath = tempfile.mkstemp()
    start_tcp_dump(
        file_path = filepath,
        read = True,
        file_to_read = pcapfile,
        print_content = True,
        port = '21'
    )

    time.sleep(5)

    buf = []
    ff = open(filepath, 'r')
    for line in ff:
        buf.append(line.strip('\n').strip('\r').strip('\t'))

    # header of pcapfile has been changed in Saigon.
    # header_pat_1 is for back compartitble with old version
    # header_pat_2 is for saigon branch and mayber newer version
    header_pat_1 = "[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+ IP ([0-9\.]+ > [0-9\.]+): [A-Z]+ [0-9]+:[0-9]+\("
    header_pat_2 = "[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+ IP .* ([0-9\.]+ > [0-9\.]+):.*[[]\D+[]]+ [0-9]+:[0-9]+"
    header_pat = '(%s)|(%s)' % (header_pat_1, header_pat_2)
    header_pos = []

    for line in buf:
        mo = re.search(header_pat, line)
        if mo:
            if src_ip in mo.group(0) and dst_ip in mo.group(0):
                header_pos.append(buf.index(line))

        time.sleep(0.5)

    temp_list = []
    pasv_list = []
    for pos in range(len(header_pos)):
        if pos == len(header_pos) - 1:
            temp_list = buf[int(header_pos[pos]):len(buf)]

        else:
            temp_list = buf[int(header_pos[pos]):int(header_pos[pos + 1])]

        del temp_list[0]
        hfpat = "0x[A-Fa-f0-9]+: [A-Za-z0-9 ]+[ ]+(.*)$"
        s = ""
        for line in temp_list:
            mo = re.search(hfpat, line)
            if mo:
                s = "%s%s" % (s, mo.group(1))

            time.sleep(0.2)

        if s:
            psvpat = "[0-9]+\.Entering\.Passive\.Mode\.\(([0-9,]+)\)?\.?\."
            mo = re.search(psvpat, s)
            if mo:
                tmp = mo.group(1).split(',')
                pasv_list.append(int(tmp[-2]) * 256 + int(tmp[-1]))

            time.sleep(0.2)

    os.remove(filepath)

    return pasv_list


def get_ftp_data(pcapfile, src_ip, dst_ip):
    '''
    '''
    data_channel_ports = get_port_ftp_data_channel(pcapfile, src_ip, dst_ip)
    datalist = []
    for port in data_channel_ports:
        ft, filepath = tempfile.mkstemp()
        start_tcp_dump(
            file_path = filepath,
            read = True,
            file_to_read = pcapfile,
            print_content = True,
            port = '%s' % port
        )
        time.sleep(5)
        lp = []
        fp = open(filepath, 'r')
        for line in fp:
            lp.append(line.strip('\n').strip('\r').strip('\t'))

        header_pat = "[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+ IP [0-9\.]+ > [0-9\.]+: ([A-Z]+) [0-9]+:[0-9]+\("
        idxlist = []
        flaglist = []
        for line in lp:
            m = re.search(header_pat, line)
            if m:
                idxlist.append(lp.index(line))
                flaglist.append(m.group(1))

        data = ""
        for flag in flaglist:
            if flag == "P":
                idx = flaglist.index(flag)
                if idx == len(idxlist) - 1:
                    data = lp[idxlist[idx]:len(lp)]

                else:
                    data = lp[idxlist[idx]:idxlist[idx + 1]]

        hppat = "0x[A-Fa-f0-9]+: [A-Za-z0-9 ]+[ ]+(.*)$"
        pdata = ""
        for line in data:
            mo = re.search(hppat, line)
            if mo:
                pdata = "%s%s" % (pdata, mo.group(1))

        pdata = pdata.replace(".", "")
        datalist.append(pdata)

    return datalist


class RatToolAgentHandler(StreamRequestHandler):
    """
    This class implements the command dispatcher. Its main duty is to receive commands from the client,
    execute them and return the result
    """
    def handle(self):
        print "Serving the client from " + str(self.client_address) + "\n"

        self.wfile.write("ok;Welcome to RAT Tool Agent\r\n")
        cmd_pattern = '([a-zA-Z0-9_]+);(.*)'

        while True:
            time.sleep(1)
            try:
                data = self.rfile.readline().strip()
                if len(data) == 0:
                    continue

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


if __name__ == "__main__":
    server = TCPServer(("", _service_port), RatToolAgentHandler)
    print "RAT Tool Agent is listening on port %d ..." % _service_port
    server.serve_forever()

