import os
import re
import sys
from lib_KwList import asDict
_tshark_cmd = r"C:\PROGRA~1\wireshark\tshark"

class pkt2csv:
    def __init__(self, pktfilename, bssid1, bssid1_ch, bssid2, bssid2_ch):
        self.filename       = pktfilename
        self.header			= False
	ch2freq = {'1':'2412',
		   '2':'2417',
		   '3':'2422',
		   '4':'2427',
		   '5':'2432',
		   '6':'2437',
		   '7':'2442',
		   '8':'2447',
		   '9':'2452',
		   '10':'2457',
		   '11':'2462',
		   '12':'2467',
		   '13':'2472',
		   '14':'2484',
		   '36':'5180',
		   '40':'5200',
		   '44':'5220',
		   '48':'5240',
		   '149':'5745',
		   '153':'5765',
		   '157':'5785',
		   '161':'5805'}

        #self.filter_exp 	= '-R "((!wlan.fcs_good) or (wlan.fcs_good==1))"'
        self.filter_exp 	= '-R "((wlan.bssid == %s)  && (radiotap.channel.freq == %s))||((wlan.bssid == %s) && (radiotap.channel.freq == %s))"' % \
			               (bssid1, ch2freq[str(bssid1_ch)], bssid2, ch2freq[str(bssid2_ch)])

        self.field_names 	= ('frame.number', 'frame.protocols', 'frame.time_relative', 'frame.len', \
                               'wlan.channel', 'wlan.data_rate', 'wlan.signal_strength',\
                               'wlan.fc.type', 'wlan.fc.subtype', 'wlan.fc.retry', 'wlan.fc.fromds', 'wlan.fc.tods',\
                               'wlan.bssid', 'wlan.sa', 'wlan.da', 'wlan.ta', 'wlan.ra', 'wlan.seq', 'wlan.duration', \
                               'wlan.fcs_good' , 'eth.src', 'eth.dst', 'ip.src_host', 'ip.dst_host')

    def CheckTshark(self):
        os.system("%s -h > aaa.txt" % _tshark_cmd)
        f   = open('aaa.txt')
        atext = f.readlines()
        f.close()
        os.remove('aaa.txt')
        return re.search('www.wireshark.org', atext[2])

# There are some duplicate packets with different channel shown on multi-channel sniffer at station,
# add this procedure filter the packets with wrong chanel info
    def filterByBssidAndChannel(self):
	self.fltfile = 'flt.'+self.filename
	filter_cmd='%s -r %s %s -w %s' % (_tshark_cmd, self.filename, self.filter_exp, self.fltfile)
	os.system(filter_cmd)

    def DoParse(self):
        if self.CheckTshark():
            print "tshark is ready..."
            fields_options = ''
            for field in self.field_names:
                fields_options += ' -e ' + field

            print "Please wait while tshark is running"
            self.filterByBssidAndChannel()
            filter_cmd='%s -r %s -T fields %s -Eheader=y -Eseparator=,> %s' % (_tshark_cmd, self.fltfile, fields_options, self.filename+'.csv')
            os.system(filter_cmd)
            print "Converting to csv is done"
        else:
            print "Please make sure you can call tshark from here first"
#
# Test Driver
#
def Usage_01():
    print """
Usage: pkt2csv.py filename=<filename> bssid1=<ap1 bssid> bssid1_ch=<ap1 channel> bssid2=<ap2 bssid> bssid2_ch=<ap2 bssid2_ch>
    where:
	<filename>: file saved packets captured by tshark or omnipeek
	<bssid1>: AP1 bssid for filter packets 
	<bssid1_ch>: AP1 channel for filter packets 
	<bssid2>: AP2 bssid for filter packets
	<bssid2_ch>: AP2 channel for filter packets
Examples:
    pkt2csv.py filename=roaming.pkt bssid1=00:22:7f:02:49:49 bssid1_ch=1 bssid2=00:1f:41:2a:b8:b9 bssid2_ch=11

    """
def main(**kwargs):
    import pdb
    pdb.set_trace()
    if len(sys.argv) < 2:
	Usage_01()
	exit(1)
    fcfg=dict(filename='roaming.pkt', bssid1='00:22:7f:02:49:49', bssid1_ch='1', bssid2='00:1f:41:2a:b8:b9', bssid2_ch='11')
    fcfg.update(kwargs)
    x = pkt2csv(fcfg['filename'], fcfg['bssid1'], fcfg['bssid1_ch'], fcfg['bssid2'], fcfg['bssid2_ch'])
    x.DoParse()

if __name__ == "__main__":
    kwargs = asDict(sys.argv[1:]) 
    main(**kwargs)
    #if len(sys.argv) < 2:
    #    print 'give me pkt file name, better same folder'
    #    sys.exit(1)

    #x = pkt2csv(sys.argv[1])
    #x.DoParse()

    #sys.exit(1)

# End Test Driver
