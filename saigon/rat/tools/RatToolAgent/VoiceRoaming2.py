from pkt2csv import *
import csv
import sys
import math
import time as tm
import os.path
from lib_KwList import asDict
import pdb

#define type
TypeManagement ="0"
TypeControl ="1"
TypeData ="2"
#define subtype
ASSOC="0"
ASSOC_RESP="1"
REASSOC="2"
REASSOC_RESP="3"
AUTHEN="11"
NULL_PKT="4"
QOS_NULL_PKT="12"
#defination of structure
frame_number=0
frame_protocols=1
frame_time_relative=2
frame_len=3
wlan_channel=4
wlan_data_rate=5
wlan_signal_strength=6
wlan_fc_type=7
wlan_fc_subtype=8
wlan_fc_retry=9
wlan_fc_fromds=10
wlan_fc_tods=11
wlan_bssid=12
wlan_sa=13
wlan_da=14
wlan_ta=15
wlan_ra=16
wlan_seq=17
wlan_duration=18
wlan_fcs_good = 19
eth_src=20
eth_dst=21
ip_src_host=22
ip_dst_host=23

def CheckMAC(MAClist , aMAC):
    if aMAC == "" or aMAC == "ff:ff:ff:ff:ff:ff":
        # No empty string or broadcast address
        return True
    # No multicast address as well
    if re.search('01:..:..:..:..:..', aMAC):
        return True
    for i in range(0, len(MAClist)):
        if aMAC == MAClist[i]:
            return True

    return False
# To search in a dictionary
def findkey(adic,akey):
    retval = ""
    for k, v in adic.iteritems():
        if k == akey:
            retval = k
            return retval

    return retval
def isSpectralink(amac):
    return re.search('00:90:7a:..:..:..', amac)

def isVocera(amac):
    return re.search('00:09:ef:..:..:..', amac)

def isDataPacketWithData(atype, asubtype):
    if int(atype) == 2:
        if (int(asubtype) != 4) and (int(asubtype) != 5) and (int(asubtype) != 6) and \
            (int(asubtype) != 12) and (int(asubtype) != 13) and (int(asubtype) != 14):
            return True
    return False

#count all key
def countkey(adic):
    retval = 0
    for k, v in adic.iteritems():
        retval +=1
    return retval

# count spectralink key
def countSpectralinkkey(adic):
    retval = 0
    for k, v in adic.iteritems():
        if isSpectralink(k):
            retval +=1
    return retval

# count spectralink value
def countSpectralinkval(adic):
    retval = 0
    for k, v in adic.iteritems():
        if isSpectralink(k):
            retval +=int(v)
    return retval

# count vocera key
def countVocerakey(adic):
    retval = 0
    for k, v in adic.iteritems():
        if isVocera(k):
            retval +=1
    return retval

# count vocera value
def countVoceraval(adic):
    retval = 0
    for k, v in adic.iteritems():
        if isSpectralink(k):
            retval +=int(v)
    return retval

#pdb.set_trace()
# Main
fcfg=dict(filename='roaming.pkt', bssid1='00:22:7f:02:49:49', bssid1_ch='1', bssid2='00:1f:41:2a:b8:b9', bssid2_ch='11')
if len(sys.argv) < 2:
        print 'give me pkt file name, better same folder'
        sys.exit(1)
kwargs = asDict(sys.argv[1:])
fcfg.update(kwargs)
#infile = sys.argv[1]
#if os.path.exists(infile):
    #sys.stdout.write("\nThe csv file exists. Do you want to skip rewriting it? [y/N]: ")
    #if sys.stdin.readline()[0].lower()!='y':
infile = fcfg['filename']
x = pkt2csv(fcfg['filename'], fcfg['bssid1'], fcfg['bssid1_ch'], fcfg['bssid2'], fcfg['bssid2_ch'])
x.DoParse()

data_list = []
UniqueMAClist = []
uniqueBSSID = []

dicMAC = {}
tMinAuth = 9999999.9
tMaxAuth = 0.0
tSumAuth = 0.0

tMinDLData = 9999999.9
tMaxDLData = 0.0
tSumDLData = 0.0

tMinULData = 9999999.9
tMaxULData = 0.0
tSumULData = 0.0

mydata = {}
spamReader = csv.reader(open(infile+'.csv'), delimiter=' ', quotechar='|')

for row in spamReader:
    data_list.append(row[0].split(','))

i = 1 # Ignore header
assocnum = 0
RoamingTimes = 0
CountDataUplink = 0
CountDataDownlink = 0
RoamingOutPutText = ""

print "Start reading packets..."
atime = tm.time()
while i < len(data_list):
    curPkt = data_list[i]
    # Good fcs packet and non retry packet only
    if (curPkt[wlan_fcs_good] == "1") and (curPkt[wlan_fc_retry]=="0"):
        # Store BSSID to get a list of unique BSSID
        if (CheckMAC(uniqueBSSID, curPkt[wlan_bssid]) == False):
            uniqueBSSID.append(curPkt[wlan_bssid])

        # Store list of MAC address, this is not include BSSIDs
        tlist = UniqueMAClist + uniqueBSSID

        if (CheckMAC(tlist, curPkt[wlan_sa]) == False):
            UniqueMAClist.append(curPkt[wlan_sa])

        if (CheckMAC(tlist, curPkt[wlan_da]) == False):
            UniqueMAClist.append(curPkt[wlan_da])

        # If a packet send from a bssid to station
        # AKA: curPkt[wlan_sa] is a bssid
        #      curPkt[wlan_da] is a station
        if (CheckMAC(uniqueBSSID, curPkt[wlan_sa]) == True):
            # if assoc or reassoc packet
            if (curPkt[wlan_fc_type]==TypeManagement) and ((curPkt[wlan_fc_subtype]==ASSOC_RESP) or (curPkt[wlan_fc_subtype]==REASSOC_RESP)):
                bASSOCResponse = curPkt[frame_number]
                tASSOCResponse = curPkt[frame_time_relative]

                # go up to find assoc request send from station to bssid
                j = i -1
                bGiveUpFindingAuth = 0
                bAuth = 0
                tAuth = 0.0
                while bGiveUpFindingAuth == 0:
                    lpkt = data_list[j]
                    # A packet that have source = destination of curPkt = station mac
                    # Destiontion = bssid
                    if (lpkt[wlan_sa] == curPkt[wlan_da]) and (lpkt[wlan_da] == curPkt[wlan_sa]):
                        if (lpkt[wlan_fc_type]==TypeManagement) and (lpkt[wlan_fc_subtype]==AUTHEN):
                            # Have to exclude retry packet
                            if (lpkt[wlan_fc_retry]=="0"):
                                bAuth = lpkt[frame_number]
                                tAuth = lpkt[frame_time_relative]
                    j = j - 1
                    # Check if we should quit finding
                    if j == 1:
                        # No more packet to look into
                        bGiveUpFindingAuth = 2
                    elif (bAuth != 0):
                        bGiveUpFindingAuth = 1
                    elif (float(curPkt[frame_time_relative]) - float(lpkt[frame_time_relative]) > 1):
                        # Too long to wait
                        bGiveUpFindingAuth = 2

                # go down to find last eapol packet (use time to stop)
                j = i + 1
                bGiveUpFindingEAPOL1 = 0
                bLastEAPOL1 = 0
                tLastEAPOL1 = 0.0
                while bGiveUpFindingEAPOL1 == 0:
                    lpkt = data_list[j]
                    # This is a packet send from station to bssid
                    if (lpkt[wlan_sa] == curPkt[wlan_da]) and (lpkt[wlan_da] == curPkt[wlan_sa]):
                        if (lpkt[wlan_fc_type]==TypeData) and (lpkt[wlan_fc_subtype]=="8"):
                            # Have to exclude retry packet
                            if (lpkt[wlan_fc_retry]=="0"):
                                # We have what we need here
                                bLastEAPOL1 = lpkt[frame_number]
                                tLastEAPOL1 = lpkt[frame_time_relative]
                                bGiveUpFindingEAPOL1 = 1
                    j = j + 1
                    # Check if we should quit finding
		    # JLIN@20091101 fix out of index
		    #if j == len(data_list)
                    if j >= len(data_list)-1:
                        # No more packet to look into
                        bGiveUpFindingEAPOL1 = 2
                    elif (float(lpkt[frame_time_relative]) - float(curPkt[frame_time_relative]) > 1):
                        # Too long to wait
                        bGiveUpFindingEAPOL1 = 2

                # Just do it one more time
                bGiveUpFindingEAPOL = 0
                bLastEAPOL = 0
                tLastEAPOL = 0.0
                while bGiveUpFindingEAPOL == 0:
                    lpkt = data_list[j]
                    # This is a packet send from station to bssid
                    if (lpkt[wlan_sa] == curPkt[wlan_da]) and (lpkt[wlan_da] == curPkt[wlan_sa]):
                        if (lpkt[wlan_fc_type]==TypeData) and (lpkt[wlan_fc_subtype]=="8"):
                            # Exclude retry packet
                            if (lpkt[wlan_fc_retry]=="0"):
                                # Found it
                                bLastEAPOL = lpkt[frame_number]
                                tLastEAPOL = lpkt[frame_time_relative]
                                bGiveUpFindingEAPOL = 1
                    j = j + 1
                    # Check if we should quit finding
		    # JLIN@20091101 fix out of index
		    #if j == len(data_list)
                    if j >= len(data_list)-1 :
                        # No more packet
                        bGiveUpFindingEAPOL = 2
                    elif (float(lpkt[frame_time_relative]) - float(curPkt[frame_time_relative]) > 1):
                        # Too long to wait
                        bGiveUpFindingEAPOL = 2

                # If i can't find the second uplink eapol packet, i use the first information
                # Note: Some cases, EAPOL packet is missing, should take a warning here
                if (bGiveUpFindingEAPOL != 1) and (bGiveUpFindingEAPOL1 == 1):
                    bLastEAPOL = bLastEAPOL1
                    tLastEAPOL = tLastEAPOL1
                    bGiveUpFindingEAPOL = 1

                #########################################################################################
                # From here, go further to find data packet to get the data information
                if bGiveUpFindingEAPOL == 1:
                    iStartFrom = bLastEAPOL
                else:
                    iStartFrom = bASSOCResponse
                # Find the last uplink and downlink of this station to/from old AP
                # Boundary is from the last eapol packet or the assocresp to the first auth packet
                # or go use time
                j = int(iStartFrom) - 1
                bLastDataUpLink = 0
                tLastDataUpLink = 0.0
                bLastDataDownLink = 0
                tLastDataDownLink = 0.0
                bGiveupFindingData = 0
                oldbssid = ""

                while bGiveupFindingData ==0:
                    lpkt = data_list[j]
                    # Get oldbssid, this section can be use with vocera as well
                    if oldbssid == "":
                        # Any packet send from/to this station with different bssid
                        if (lpkt[wlan_sa] == curPkt[wlan_da]) or (lpkt[wlan_da] == curPkt[wlan_da]):
                            if (lpkt[wlan_bssid] != curPkt[wlan_sa]):
                                oldbssid = lpkt[wlan_bssid]

                    # prevent duplicate
                    if bLastDataUpLink == 0:
                        #This is a data packet send from station to something other than bssid
                        if (lpkt[wlan_sa] == curPkt[wlan_da]) and (lpkt[wlan_da] != curPkt[wlan_sa]):
                            if isDataPacketWithData(lpkt[wlan_fc_type],lpkt[wlan_fc_subtype]) and (lpkt[wlan_fc_tods]=="1"):
                                # Have to exclude retry packet
                                if (lpkt[wlan_bssid]== oldbssid) and (lpkt[wlan_fc_retry]=="0"):
                                    bLastDataUpLink = lpkt[frame_number]
                                    tLastDataUplink = lpkt[frame_time_relative]

                    # prevent duplicate
                    if bLastDataDownLink == 0:
                        if (lpkt[wlan_sa] != curPkt[wlan_sa]) and (lpkt[wlan_da] == curPkt[wlan_da]):
                            if isDataPacketWithData(lpkt[wlan_fc_type],lpkt[wlan_fc_subtype]) and (lpkt[wlan_fc_fromds]=="1"):
                                # Have to exclude retry packet
                                if (lpkt[wlan_bssid] == oldbssid) and (lpkt[wlan_fc_retry]=="0"):
                                    bLastDataDownLink = lpkt[frame_number]
                                    tLastDataDownlink = lpkt[frame_time_relative]

                    j = j - 1
                    # Check to give up
                    #if j == int(bAuth): #This doesn't help
                    if j == 1: # No more packet to check
                        # Should I stop here or a little bit further?
                        bGiveupFindingData = 2
                    elif (float(curPkt[frame_time_relative]) - float(lpkt[frame_time_relative]) > 1):
                        # too long, I dont want to search anymore
                        bGiveupFindingData = 2
                    elif (bLastDataUpLink != 0) and (bLastDataDownLink!= 0):
                        bGiveupFindingData = 1

                # Find the first uplink and last downlink to/from new ap
                j = int(iStartFrom) + 1
                bFirstDataUpLink = 0
                tFirstDataUplink = 0.0
                bFirstDataDownLink = 0
                tFirstDataDownLink = 0.0
                bGiveupFindingData = 0

                while bGiveupFindingData ==0:
                    lpkt = data_list[j]
                    # prevent update multiple times
                    if bFirstDataUpLink == 0:
                        #This is a data packet send from station to something other than bssid
                        if (lpkt[wlan_sa] == curPkt[wlan_da]) and (lpkt[wlan_da] != curPkt[wlan_sa]):
                            if isDataPacketWithData(lpkt[wlan_fc_type],lpkt[wlan_fc_subtype]) and (lpkt[wlan_fc_tods]=="1"):
                                # The packet should have the new bssid
                                # Have to exclude retry packet
                                if (lpkt[wlan_bssid]== curPkt[wlan_sa]) and (lpkt[wlan_fc_retry]=="0"):
                                    bFirstDataUpLink = lpkt[frame_number]
                                    tFirstDataUplink = lpkt[frame_time_relative]

                    # prevent duplicate
                    if bFirstDataDownLink == 0:
                        if (lpkt[wlan_sa] != curPkt[wlan_sa]) and (lpkt[wlan_da] == curPkt[wlan_da]):
                            if isDataPacketWithData(lpkt[wlan_fc_type],lpkt[wlan_fc_subtype]) and (lpkt[wlan_fc_fromds]=="1"):
                                # The packet should have the new bssid
                                if (lpkt[wlan_bssid]== curPkt[wlan_sa]) and (lpkt[wlan_fc_retry]=="0"):
                                    bFirstDataDownLink = lpkt[frame_number]
                                    tFirstDataDownlink = lpkt[frame_time_relative]

                    j = j + 1
                    # Check to give up
                    if j > len(data_list):
                        # No more data to search
                        bGiveupFindingData = 2
                    elif (float(lpkt[frame_time_relative]) - float(curPkt[frame_time_relative]) > 1):
                        # Should I stop here or go a little bit further?
                        bGiveupFindingData = 2
                    elif (bFirstDataUpLink != 0) and (bFirstDataDownLink!= 0):
                        bGiveupFindingData = 1

                # Store information
                if bGiveUpFindingAuth == 1:
                    #print "Look up bAuth = %s %s bAssocResonse = %s %s bEAPOL = %s %s " % (bAuth,tAuth,bASSOCResponse,tASSOCResponse,bLastEAPOL,tLastEAPOL)
                    # Calculate authentication time()
                    AUTHTime = 0.0
                    if (bLastEAPOL != 0):
                        AUTHTime = float(tLastEAPOL) - float(tAuth)
                    else:
                        AUTHTime = float(tASSOCResponse) - float(tAuth)

                    if (int(bLastDataUpLink) != 0) and (int(bFirstDataUpLink) != 0):
                        tDataUplink = float(tFirstDataUplink) - float(tLastDataUplink)
                        CountDataUplink+=1
                        tSumULData += float(tDataUplink)
                        if tMinULData > tDataUplink:
                            tMinULData = tDataUplink
                        if tMaxULData < tDataUplink:
                            tMaxULData = tDataUplink
                    else:
                        tDataUplink = 'N/A'
                        if int(bLastDataUpLink) == 0:
                            bLastDataUpLink = 'N/A'
                        if int(bFirstDataUpLink) == 0:
                            bFirstDataUpLink = 'N/A'

                    if (int(bLastDataDownLink) != 0) and (int(bFirstDataDownLink) != 0):
                        tDataDownlink = float(tFirstDataDownlink) - float(tLastDataDownlink)
                        CountDataDownlink+=1
                        tSumDLData += tDataDownlink
                        if tMinDLData > tDataDownlink:
                            tMinDLData = tDataDownlink
                        if tMaxDLData < tDataDownlink:
                            tMaxDLData = tDataDownlink
                    else:
                        tDataDownlink = 'N/A'
                        if int(bLastDataDownLink) == 0:
                            bLastDataDownLink = 'N/A'
                        if int(bFirstDataDownLink) == 0:
                            bFirstDataDownLink = 'N/A'

                    # Collect statistics
                    tSumAuth += AUTHTime
                    if tMinAuth > AUTHTime:
                        tMinAuth  = AUTHTime

                    if tMaxAuth < AUTHTime:
                        tMaxAuth  = AUTHTime

                    #Station,From BSSID,To BSSID,Last index,First index,Delay,Last index,First index,Delay,Auth from Station,Assoc Response from AP,Last EAPOL,Time\n")
                    RoamingOutPutText = "%s%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (RoamingOutPutText,curPkt[wlan_da],oldbssid,curPkt[wlan_sa],bLastDataUpLink,bFirstDataUpLink,tDataUplink ,bLastDataDownLink,bFirstDataDownLink,tDataDownlink ,bAuth,bASSOCResponse,bLastEAPOL,AUTHTime)
                    RoamingTimes+=1

        # In case this is a data packet
        if (curPkt[wlan_fc_type]==TypeData):
            if findkey(mydata,curPkt[wlan_sa]) == "":
                mydata[curPkt[wlan_sa]] = {}
                mydata[curPkt[wlan_sa]]['from'] = {}
                mydata[curPkt[wlan_sa]]['to'] = {}

                mydata[curPkt[wlan_sa]]['to'][curPkt[wlan_da]] = 1
            else:
                if findkey(mydata[curPkt[wlan_sa]]['to'],curPkt[wlan_da]) == "":
                    mydata[curPkt[wlan_sa]]['to'][curPkt[wlan_da]] = 1
                else:
                    mydata[curPkt[wlan_sa]]['to'][curPkt[wlan_da]] += 1

            if findkey(mydata,curPkt[wlan_da]) == "":
                mydata[curPkt[wlan_da]] = {}
                mydata[curPkt[wlan_da]]['from'] = {}
                mydata[curPkt[wlan_da]]['to'] = {}

                mydata[curPkt[wlan_da]]['from'][curPkt[wlan_sa]] = 1
            else:
                if findkey(mydata[curPkt[wlan_da]]['from'],curPkt[wlan_sa]) == "":
                    mydata[curPkt[wlan_da]]['from'][curPkt[wlan_sa]] = 1
                else:
                    mydata[curPkt[wlan_da]]['from'][curPkt[wlan_sa]] += 1

        # if packet to check
    # if good packet
    #print "Complete: %d / %d" % (i,len(data_list))
    ## keep update to user
    if (tm.time() - atime) > 2:
        print "Complete %d%%" % (int(float(i)/float(len(data_list))*100))
        atime = tm.time()

    i = i + 1
# Main loop
print "Done! %s roams found" % RoamingTimes
print "Making report file"

retfile = open('report.'+infile+'.csv', 'w')

retfile.write("AP/BSSID,,,,,,,,,,,,\n")
for abssid in uniqueBSSID:
    retfile.write(",%s,,,,,,,,,,,\n" % abssid)
retfile.write(",,,,,,,,,,,,\n")
retfile.write("Station,MAC address,Role,Partner,,,,,,,,,\n")
for amac in UniqueMAClist:
    # Look in mydata to decide the role of a station
    arole = "Unknown"
    maxcount = 0
    partner = ""
    # if this is a spectralink MAC
    if isSpectralink(amac):
        arole = "Spectralink handset"
        if findkey(mydata, amac) != "":
            # Many spectralinks send to amac, with many packet
            if (countSpectralinkkey(mydata[amac]['to'])!=0 ) and (countSpectralinkval(mydata[amac]['to'])>50 ):
                # No spectralink send to amac or there is some packet but not too many
                if (countSpectralinkkey(mydata[amac]['from'])==0 ) or (countSpectralinkval(mydata[amac]['from']) < 50):
                    # Could be SVP
                    arole = "Spectralink PRI"
            # amac send to many spectralink
            elif (countSpectralinkkey(mydata[amac]['from'])!=0 ) and (countSpectralinkval(mydata[amac]['from'])>500 ):
                if (countSpectralinkkey(mydata[amac]['to'])==0 ) or (countSpectralinkval(mydata[amac]['to']) < 50):
                    # Could be PRI
                    arole = "Spectralink SVP"

    elif isVocera(amac):
        arole = "Vocera handset"
        # Should have data
        if findkey(mydata, amac) != "":
            maxcount = 0
            partner = ""
            # Another vocera talk to this vocera
            if (countVocerakey(mydata[amac]['from'])!=0 ):
                for k,v in mydata[amac]['from'].iteritems():
                    if isVocera(k):
                        if int(v) > maxcount:
                            maxcount = int(v)
                            partner = k + '(F)'

            if (countVocerakey(mydata[amac]['to'])!=0 ):
                for k,v in mydata[amac]['to'].iteritems():
                    if isVocera(k):
                        if int(v) > maxcount:
                            maxcount = int(v)
                            partner = k + '(T)'

    else:
        if findkey(mydata, amac) != "":
            # A normal mac but spectralink talks to him and nothing else
            # should have any spectralink talk to
            if countSpectralinkkey(mydata[amac]['from']) > 0:
                # should receive from spectralink only
                if countSpectralinkkey(mydata[amac]['from']) == countkey(mydata[amac]['from']):
                    if (countkey(mydata[amac]['to']) == 0):
                        arole = "Syslog server"
                    else:
                        arole = "Syslog/TFTP server(not sure)"


            # Vocera server could talk to any station but he reply all packet from handsets to him
            elif (countVocerakey(mydata[amac]['from']) > 0) or (countVocerakey(mydata[amac]['to']) > 0):
                if countVoceraval(mydata[amac]['from']) == countVoceraval(mydata[amac]['to']):
                    arole = "Vocera server"
        else:
            #last chance to tell base on MAC address
            if re.search('00:10:1d:..:..:..', amac):
                arole = "Winbond Elec"
            elif re.search('00:oe:35:..:..:..', amac):
                arole = "Intel Corp"

    retfile.write(",%s,%s,%s,,,,,,,,,\n" % (amac,arole,partner))

retfile.write(",,,,,,,,,,,,\n")
retfile.write("Roaming,,,,,,,,,,,,\n")
retfile.write(",,,Uplink data,,,Downlink data,,,Assoc/Reassoc infor,,,\n")
retfile.write("Station,From BSSID,To BSSID,Up Last index,Up First index,Up Delay,Dn Last index,Dn First index,Dn Delay,Auth from Station,Assoc Response from AP,Last EAPOL,Time\n")
retfile.write(RoamingOutPutText)
retfile.write(",,,,,,,,,,,,\n")
retfile.write("SUMARY,,,,,,,,,,,,\n")
retfile.write(",Min,Max,Avg,,,,,,,,,\n")
# Check to prevent division by zero
if int(RoamingTimes) > 0:
    retfile.write("Authentication,%s,%s,%s,,,,,,,,,\n" % (tMinAuth,tMaxAuth,float(tSumAuth)/float(RoamingTimes)) )
else:
    retfile.write("Authentication,N/A,N/A,N/A,,,,,,,,,\n" )

if int(CountDataUplink) > 0:
    retfile.write("Uplink delay,%s,%s,%s,,,,,,,,,\n" % (tMinULData,tMaxULData,float(tSumULData)/float(CountDataUplink)) )
else:
    retfile.write("Uplink delay,N/A,N/A,N/A,,,,,,,,,\n" )

if int(CountDataDownlink) > 0:
    retfile.write("Downlink delay,%s,%s,%s,,,,,,,,,\n" % (tMinDLData,tMaxDLData,float(tSumDLData )/float(CountDataDownlink)) )
else:
    retfile.write("Downlink delay,N/A,N/A,N/A,,,,,,,,,\n" )


retfile.write(",,,,,,,,,,,,\n")
retfile.write("DATA FLOW SUMARY,,,,,,,,,,,,\n")
for k, v in mydata.iteritems():
    retfile.write(",,,,,,,,,,,,\n")
    retfile.write("%s,To,Count,,,,,,,,,,\n" % (k) )
    for kk, vv in v['to'].iteritems():
        retfile.write(",%s,%s,,,,,,,,,,\n" % (kk,vv) )
    retfile.write(",From,Count,,,,,,,,,,\n")
    for kk, vv in v['from'].iteritems():
        retfile.write(",%s,%s,,,,,,,,,,\n" % (kk,vv) )

retfile.close()
print "Done! Report is in %s" %('report.'+infile+'.csv')
