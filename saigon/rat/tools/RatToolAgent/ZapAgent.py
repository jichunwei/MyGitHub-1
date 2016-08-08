import subprocess as sp
import time
import threading
import pdb
import re
from RatToolAgent import _adapter_name

_zap_dict = dict(thread=None,
            zap_cmd=r'zap -s%s -d%s -X%s',
            pskill_cmd=r'C:\bin\win\pskill')

def send_zap_traffic(source_ip="", destination_ip="", duration="", speed="", proto="", length="", tos="" , debug=False):
    """
    send traffic through zap
    - source_ip: Specify the IP address of the source station.
    - destination_ip: Specify the IP address of the destination station.
    - duration: Test for specified number of seconds.
    - speed: Controls the rate in mbits/s for transmitting data
    """

    if debug: pdb.set_trace()
    cmd = _zap_dict['zap_cmd']% (source_ip, destination_ip, duration)
    if speed:
        cmd += ' -r%s' % speed
    if proto == 'tcp':
        cmd += ' -t'
    if length:
        cmd += " -l%s" % length
    if tos:
        cmd += " -q%s" % tos
    zap_thread = LaunchZap('start "zap traffic" %s' % cmd)
    _zap_dict['thread'] = zap_thread
    zap_thread.start()
    return zap_thread

def kill_zap_thread():
    """
    Stop zap by killing its process
    """
    # Find tcpdump process to kill
    cmd = _zap_dict['pskill_cmd']+ " -t zap"
    if _zap_dict['thread'] != None:
    #pipe = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
        del(_zap_dict['thread'])
        output = sp.Popen(cmd, stdout=sp.PIPE).communicate()[0]
        return output
                
def get_sta_traffic_by_if_name(if_name='Wireless Network Connection'):
    """
    get station traffic from cmd "netsh interface show ip interface"
    - if_name: user-friendly name
    return tuple (In Octets, Out Octets)
    """
    #@author: Jane.Guo @since: 2013-11 fix bug to get adapter_name from RatToolAgent
    global _adapter_name
    if_name = _adapter_name
    result = {}
    cmd_line = "netsh interface ip show interface"
    output = sp.Popen(cmd_line,  stdout=sp.PIPE).communicate()[0]
    for if_info in re.split(r'\r\n\r\n', output):
        if re.findall(if_name,if_info):
            for line in if_info.split('\r\n'):
                k, v = re.split(r':\s+',line)
                result[k]=v
    return (result['In Octets'],result['Out Octets'])
                    
class LaunchZap(threading.Thread):
    tlock = threading.Lock()
    id = 0
    def __init__(self, start_cmd):
        threading.Thread.__init__(self)
        self.command = start_cmd
        self.status = 0
        self.pid = -1

    def run(self):
        self.pipe = sp.Popen(self.command, shell=True,
                             stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
        self.status = 1
        time.sleep(5)
        self.pid = self.pipe.pid
        self.data = self.pipe.stdout.read()
        self.status = 2

    def pid(self):
        return self.pid

    def isDone(self):
        return (self.status != 1)
