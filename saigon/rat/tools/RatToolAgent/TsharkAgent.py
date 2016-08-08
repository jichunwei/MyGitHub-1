import subprocess as sp
import time
import threading
import pdb
import os
import re

_tshark_dict = dict(thread=None,
		    tshark_cmd=r'C:\PROGRA~1\wireshark\tshark',
		    pskill_cmd=r'C:\bin\win\pskill')

def removePacketAndReportFiles(filename):
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(filename+'.csv'):
        os.remove(filename+'.csv')
    if os.path.exists('report.'+filename+'.csv'):
        os.remove('report.'+filename+'.csv')

def getInfIndex(infname="airpcap_any",debug=False):
    if debug: pdb.set_trace()
    cmd = _tshark_dict['tshark_cmd'] + ' -D'
    output = sp.Popen(cmd, stdout=sp.PIPE).communicate()[0]
    for line in output.split('\r\n'):
        pattern=r"([\d]+)\.\s*[\.\\]*([^\s]*)"
        m = re.match(pattern, line, re.I)
        if m:
            if re.search(infname, m.group(2)):
                infindex = m.group(1)
            return infindex
    
def captureTrafficOTA(infname="", filename="", duration="", ether_host="", debug=False):
    """
    Start tshark to capture traffic over the air on the specific interface with given configuration
    - inf: used this interface to capture
    - duration: capture stop after NUM seconds
    - file_path: path of file that saves capturing information
    """
    #try: stopTshark()
    #except: pass
    work_dir=os.getcwd()+'\\'+'voice_packets'
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    _tshark_dict['work_dir'] = work_dir
    work_file=work_dir+'\\'+filename
    removePacketAndReportFiles(work_file)
    if debug: pdb.set_trace()
    inf = getInfIndex(infname)
    if not inf: raise Exception, "Can't get interface index by interface name"
    cmd = "%s -i %s -V" % (_tshark_dict['tshark_cmd'], inf)
    if ether_host: cmd += ' -f "ether host %s"' % ether_host
    if int(duration) != 0: cmd = "%s -a duration:%s" % (cmd, duration)
    #if expression: cmd = "%s %s %s" % (cmd, expression, host)
    cmd = '%s -w "%s"' % (cmd, work_file)
    #pipe = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    #_execProgram(cmd)
    #time.sleep(2)
    tshark = LaunchApp('start "tshart capture" %s' % cmd)
    _tshark_dict['thread'] = tshark
    tshark.start()
    return tshark

def generateReport(filename='a3.pcap', bssid1='00:22:7f:02:49:49', bssid1_ch='1', bssid2='00:1f:41:2a:b8:b9', bssid2_ch='11', debug=False):
    if debug: pdb.set_trace()
    work_file = _tshark_dict['work_dir']+'\\'+filename
    cmd = "Python VoiceRoaming2.py filename=%s bssid1=%s bssid1_ch=%s bssid2=%s bssid2_ch=%s" % \
	( work_file, bssid1, bssid1_ch, bssid2, bssid2_ch)  
    output = sp.Popen(cmd, stdout=sp.PIPE).communicate()[0]
    return output

def analyzeReport(filename='report.roaming.pkt.csv',debug=False):
    if debug: pdb.set_trace()
    work_file = _tshark_dict['work_dir']+'\\'+filename
    if os.path.exists(work_file):
        rdata=paserRoamingData(work_file)
        roaming_data={}
        uplink_time=[]
        downlink_time=[]
        auth_time=[]
        roaming_data['number']=len(rdata)
        for idx in rdata:
            uplink_time.append(rdata[idx]['Up Delay'])
            downlink_time.append(rdata[idx]['Dn Delay'])
            auth_time.append(rdata[idx]['Time'])
        roaming_data['uplink_time'] = uplink_time
        roaming_data['downlink_time'] = downlink_time
        roaming_data['auth_time'] = auth_time
        return roaming_data
    else:
        return {}

def paserRoamingData(filename):
    #work_file = _tshark_dict['work_dir']+'\\'+filename
    f1=open(filename, 'rb')
    title_pat=r"Station,From BSSID,To BSSID,.*Time"
#   data_pat=r"[0-9a-f:]+,[0-9a-f:]+,[0-9a-f:]+,[\d+]+,[\d+]+,[\d+.]+,[\d+]+,[\d+]+,[\d+.]+,[\d+]+,[\d+]+,[\d+]+,[\d+.]+"
    data_pat=r"[0-9a-f:]+,[0-9a-f:]+,[0-9a-f:]+,[\d]+,[\d]+,[\d.]+,[\d]+,[\d]+,[\d.]+,[\d]+,[\d]+,[\d]+,[\d.]+"
    i = 1
    roam_dict={}
    for line in f1:
        if re.match(title_pat, line, re.I):
            line=line.strip()
            title=line.split(',')
        if re.match(data_pat, line, re.I):
            line=line.strip()
            data=line.split(',')
            roam_dict['roam'+str(i)]={}
            for idx in range(0,len(title)):
                roam_dict['roam'+str(i)][title[idx]]=data[idx]
            i += 1
    return roam_dict

def killTshark():
    """
    Stop tshark by killing its process
    """
    # Find tcpdump process to kill
    cmd = _tshark_dict['pskill_cmd']+ " -t tshark"
    if _tshark_dict['thread'] != None:
    #pipe = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
        del(_tshark_dict['thread'])
        output = sp.Popen(cmd, stdout=sp.PIPE).communicate()[0]
        return output
# cmd = 'start "Tshark Capture" c:\progra~1\wireshark\tshark -i 1 -V'
# ss = laut2.LauchApp(cmd)
# ss.start()
# ss.pid
# ss.isDone()
# del(ss)
class LaunchApp(threading.Thread):
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
