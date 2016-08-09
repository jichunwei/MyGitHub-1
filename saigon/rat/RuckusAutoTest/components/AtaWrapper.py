"""
This component is used for connect to Veriwave and control clients.
"""
import os, sys
import AtaTelnet as Atatelnet
from RuckusAutoTest.components.lib.ata import ata_lib
import pdb
from time import sleep
import time
from RuckusAutoTest.common import xml_dict_json as XDJ

ata_admin = "admin"
ata_user = "user"
fiveg_band = 5000
twog_band = 2400
## for scg wispr
#fiveg_channel = 153
## for third party AP
fiveg_channel = 36
twog_channel = 11
wifi_01 = "wifi_01"
wifi_02 = "wifi_02"
enet_01 = "enet_01"
enet_02 = "enet_02"
wifi_blade_01 = 9
wifi_port_01 = 4
enet_blade_01 = 2
enet_port_01 = 2
ata_IP = "172.18.120.23"
veriwave_IP = "172.18.110.31"
apSSID = "chris-test"
client_name = "cl_01"
clg_group_name = "clg_01"
client_count = 5
wifi_client_type = "802.11a/b/g/n"

# for encrytpion / authentication samples
#WPA
wifi_security_type = "WPA-PSK-AES"
wifi_security_passphrase = "password123"
#WEP
apWepSSID = "zauto-wep"
wifi_wep = "WEP-OPEN-128"
wifi_wep_passphrase = "1234567890abc0987654321def"
#802.1x 
apdot1xSSID = "zauto-8021x"
wifi_8021x = "WPA2-PEAP-MSCHAPv2"
user_ID = "ras.local.user"
user_password = "ras.local.user"
start_index = 1
#802.1x eap-sim sample crediental
# identity=1310410357548204@wlan.mnc410.mcc310.3gppnetwork.org  << error with ATA (need to be under 32 chars)
#createclient eap_sim01 zauto-8021x clientType=802.11a/b/g/n security=WPA2-SIM-AES 
#identity=1310410339288673 simCypherKey='7C09D7118E3C87A7 BD8C656E97AA29B5 EE0B8E00C828F19E' 
#simResponse='B1858F65 40953453 936197F6'
apdot1xSSID = "zauto-8021x"
wifi_8021x_eap_sim = "WPA2-SIM-AES"
eap_sim_user_ID = "1310410339288672"
simCypherKey="'7C09D7118E3C87A7 BD8C656E97AA29B5 EE0B8E00C828F19E'" 
simResponse="'B1858F65 40953453 936197F6'"

# for wispr
#createclient wc11 zauto-wispr webAuthAlgorithm=Dave19 webAuthURL=http://www.google.com
#controlclient wc11 DNSAdd www.google.com=74.125.239.49
#controlclient wc11 webAuthLogon ControllerIP=192.168.0.2 KeyPhrases='google' FormName='' FormInfo='username,text,user3;submit,static,ok;password,password,user3' Port=80
# for ZD
#apwisprSSID = "zauto-wispr"
#webAuth = "Dave19"

## for scg wispr
#apwisprSSID = "zauto-scg-wispr"
#webAuth = "wispr13"

## for scg third party ap
apwisprSSID = "MO-ARUBA-QQQQ"
webAuth = "third2"

# For different flow and flow group
server_name = "server_01"
flow_name = "flow01"
flow_group_name = "flow_g1"
flow_count = 10


class AtaWrapper(object):
    def __init__(self, ip_addr = ata_IP, username = ata_admin):
        self.ip_addr = ip_addr
        self.username = username
        self.ata_tel = Atatelnet.AtaTelnet(ip_addr, "admin")
        self.ata_port = []
        self.ata_wifi_port = []
        self.ata_enet_port = []
        self.current_band = fiveg_band
        self.current_channel = fiveg_channel 
        self.bss_info = {}
    
    def connect(self):
        self.ata_tel.login()
        self.rc = self.ata_tel.list_all()
        print self.rc  
        
    def info(self):
        self.rc = self.ata_tel.list_all()
        print self.rc  

    def bind_vw_port(self, port_name = wifi_01, ip_addr = veriwave_IP, slot = 1, port = 1):
        #("bindport wifi_01 10.150.4.98 1 1")
        self.rc = self.ata_tel.perform("bindport %s %s %d %d" % (port_name, ip_addr, slot, port))
        self.ata_port.append(port_name)
        print self.rc

    def set_band_channel(self, port_name = wifi_01, band = fiveg_band, channel = fiveg_channel):  
        #("setchannel wifi_01 5000 161")
        self.current_band = band
        self.current_channel = channel
        self.rc = self.ata_tel.perform("setchannel %s %d %d" % (port_name, band, channel))
        print self.rc

    def scanbss(self, port_name = wifi_01):
        self.rc = ata_lib.get_ssid_info(self.ata_tel, port_name)
        print self.rc
        self.bss_info[self.current_channel] = self.rc
        return self.rc

    def get_bss_info(self):
        #pdb.set_trace()
        return(self.bss_info)

    # Dave, not complete, needs additional works
    def run_x_command(self,cmd):
        self.rc = self.ata_tel.perform('xmlrsps', ofmt='xml')
        return(self.rc)

    def run_command(self,cmd):
        self.rc = self.ata_tel.perform(cmd)
        return(self.rc)

    def find_ssid(self, port_name = wifi_01, ssid = apSSID):
        self.rc = ata_lib.get_ssid_info(self.ata_tel, port_name)
        print self.rc
        self.bss_info[self.current_channel] = self.rc
        #pdb.set_trace()
        return self.rc.get(apSSID)

    def create_client(self, clientname = client_name, ssid = apSSID, client_type = wifi_client_type, \
                                  security_type = wifi_security_type, passphrase = None,
                                  identity = None, password = None
                                  ):
        #"createClientGroup clg_01 100 apSSID clientType=802.11a/b/g/n security=WPA-PSK-AES networkKey=password123"
        cmd = "createClient %s %s" % (clientname, ssid)
        if client_type:
            cmd = "%s clientType=%s" % (cmd, client_type)
        
        if security_type:
            cmd = "%s security=%s" % (cmd, security_type)
        
        if passphrase:
            cmd = "%s networkKey=%s" % (cmd, passphrase)
        
        if identity:
            cmd = "%s identity=%s" % (cmd, identity)
        
        if password:
            cmd = "%s password=%s" % (cmd, password)
            
        print "CMD: %s" % cmd
        
        timeout = 10
        st = time.time()
        while time.time() - st < timeout:
            self.rc = self.ata_tel.perform(cmd, timeout=3)
            #{'associationStatus': 'ok_connecting'}
            if type(self.rc) is dict:
                if self.rc.has_key('associationStatus') and self.rc['associationStatus'] == 'ok_connecting':
                    return self.rc
        
        return {"associationStatus":'Unknown'}

    
    def get_client_info(self, clientname = client_name, detail = False):
        cmd = "getClientInfo %s" % clientname
        if detail:
            cmd = "%s %s" % (cmd, 'detail')
        
        self.rc = self.ata_tel.perform(cmd)
        return self.rc

    def destroy_client(self, clientname = client_name):
        self.rc = self.ata_tel.perform("destroyClient %s " % (clientname))
        print self.rc
        return self.rc
    
    
    def destroy_server(self, servername):
        self.rc = self.ata_tel.perform("destroyServer %s" % (servername))
        print self.rc
        return self.rc

    def create_client_group(self, group_name = clg_group_name, count = client_count, ssid = apSSID, client_type = wifi_client_type, \
                                  security_type = wifi_security_type, passphrase = wifi_security_passphrase):
        #"createClientGroup clg_01 100 apSSID clientType=802.11a/b/g/n security=WPA-PSK-AES networkKey=password123"
        #for WPA2
        #"createClientGroup clg_01 100 apSSID clientType=802.11a/b/g/n security=WPA2-PSK networkKey=password123"
        cmd = "createClientGroup %s %d %s" % (group_name, count, ssid)
        if client_type:
            cmd = "%s clientType=%s" % (cmd, client_type)
        
        if security_type:
            cmd = "%s security=%s" % (cmd, security_type)
        
        if passphrase:
            cmd = "%s networkKey=%s" % (cmd, passphrase)
        
        self.rc = self.ata_tel.perform(cmd)
        print self.rc
        return self.rc
    
    
    def get_client_group_info(self, clientgroupname = clg_group_name, detail=False):
        cmd = "getClientGroupInfo %s" % clientgroupname
        if detail:
            cmd = "%s %s" % (cmd, 'detail')
        
        self.rc = self.ata_tel.perform(cmd)
            
    
    def disassociate_client_group(self, groupname = clg_group_name):
        self.rc = self.ata_tel.perform("disassoicateClientGroup %s" % (groupname))
        print self.rc
        return self.rc

    def destroy_client_group(self, groupname = clg_group_name):
        self.rc = self.ata_tel.perform("destroyClientGroup %s " % (groupname))
        print self.rc
        return self.rc

    def create_8021x_client(self, clientname = client_name, ssid = apSSID, client_type = wifi_client_type, \
                                  security_type = wifi_8021x, identity = user_ID, passphrase = user_password):
        #createclient cr_1 zauto-8021x clientType=802.11a/b/g/n security=WPA2-PEAP-MSCHAPv2 identity=user1 password=user1
        self.rc = self.ata_tel.perform("createclient %s %s clientType=%s security=%s identity=%s password=%s" % \
                                        (clientname, ssid, client_type, security_type, identity, passphrase))
        print self.rc
        return self.rc

    def create_8021x_group(self, group_name = clg_group_name, count = client_count, ssid = apSSID, client_type = wifi_client_type, \
                                  security_type = wifi_8021x, identity = user_ID, passphrase = user_password, index = start_index):
        #createclient cr_1 zauto-8021x clientType=802.11a/b/g/n security=WPA2-PEAP-MSCHAPv2 identity=user1 password=user1
        self.rc = self.ata_tel.perform("createClientGroup %s %d %s clientType=%s security=%s identity=%s password=%s credentialStartIndex=%d" % \
                                        (group_name, count, ssid, client_type, security_type, identity, passphrase, index))
        print self.rc
        return self.rc

    def create_eapsim_client(self, clientname = client_name, ssid = apdot1xSSID, client_type = wifi_client_type, \
                                  security_type = wifi_8021x_eap_sim, identity = eap_sim_user_ID, \
                                  simKey = simCypherKey, simResp = simResponse):
        #createclient eap_sim01 zauto-8021x clientType=802.11a/b/g/n security=WPA2-SIM-AES 
        #identity=1310410339288673 simCypherKey='7C09D7118E3C87A7 BD8C656E97AA29B5 EE0B8E00C828F19E' 
        #simResponse='B1858F65 40953453 936197F6'
        self.rc = self.ata_tel.perform("createClient %s %s clientType=%s security=%s identity=%s simCypherKey=%s simResponse=%s" % \
                                        (clientname, ssid, client_type, security_type, identity, simKey, simResp))
        print self.rc
        return self.rc


    def create_wispr_client(self, clientname = client_name, ssid = apSSID, webAuthAlgorithm='Ruckus3K_std', webAuthURL='http://www.google.com',\
                                  fqdn='wwww.google.com', fqdn_ip_addr='74.125.239.49', ControllerIP='192.168.0.2',\
                                  KeyPhrases='google', FormName='loginForm', FormInfo='username,text,user3;submit,static,ok;password,password,user3',\
                                  http_port=80):

        self.rc = self.ata_tel.perform("createclient %s %s webAuthAlgorithm=%s webAuthURL=%s" % \
                                        (clientname, ssid, webAuthAlgorithm, webAuthURL))
#        sleep(1)
        self.rc = self.ata_tel.perform("controlclient %s DNSAdd %s=%s" % \
                                        (clientname, fqdn, fqdn_ip_addr))
        sleep(1)
        self.rc = self.ata_tel.perform("controlclient %s webAuthLogon ControllerIP=%s KeyPhrases=%s FormName=%s FormInfo=%s Port=%s" % \
                                        (clientname, ControllerIP, KeyPhrases, FormName, FormInfo, http_port))
        print self.rc
        return self.rc

    def create_server(self, servername = server_name):
        #"createServer server_01        
        self.rc = self.ata_tel.perform("createServer %s " % (servername))
        print self.rc
        return self.rc
    
    
    def get_server_info(self, servername = server_name):
        cmd = "getServerInfo %s" % servername
        self.rc = self.ata_tel.perform(cmd)
        return self.rc

    def create_flow(self, flowname = flow_name, source = server_name, destin = client_name):
        #createFlow flow1 server_01 clg_01 type=FTP
        self.rc = self.ata_tel.perform("createFlow %s %s %s" % (flowname, source, destin))
        print self.rc
        return self.rc
    
    def start_flow(self, flowname = flow_name):
        self.rc = self.ata_tel.perform("startFlow %s" % flowname)
        print self.rc
        return self.rc
    
    def stop_flow(self, flowname = flow_name):
        self.rc = self.ata_tel.perform("stopFlow %s" % flowname)
        print self.rc
        return self.rc

    def get_flow_info(self, flowname = flow_name, detail=False):
        cmd = "getFlowInfo %s" % flowname
        if detail:
            cmd = cmd + " detail"
        
        self.rc = self.ata_tel.perform(cmd)
        
        print self.rc
        
        return self.rc
    
    def create_flow_group(self, flowname = flow_group_name, flowcount = flow_count, source = server_name, destin = client_name, flowtype="HTTP"):
        #createFlowGroup flowgroup count server_01 clg_01 type=FTP
        self.rc = self.ata_tel.perform("createFlowGroup %s %d %s %s type=%s " % (flowname, flowcount, source, destin, flowtype))
        print self.rc
        return self.rc

    def ping_client(self, clientname = client_name, destination = "8.8.8.8"):
        self.rc = self.ata_tel.perform("pingFrom %s %s count=2" % (clientname, destination))
        print self.rc
        return self.rc

    def destroy_flow(self, flowname = flow_name):
        #createFlow flow1 server_01 clg_01 type=FTP
        self.rc = self.ata_tel.perform("destroyFlow %s " % (flowname))
        print self.rc
        return self.rc

    def destroy_flow_group(self, flowname = flow_group_name):
        #createFlow flow1 server_01 clg_01 type=FTP
        self.rc = self.ata_tel.perform("destroyFlowGroup %s " % (flowname))
        print self.rc
        return self.rc

    def remove_ports(self, items = "ports"):
        self.rc = self.ata_tel.perform("purge %s" % (items))
        print self.rc
    
    

if __name__ == "__main__":
    # always initialize and then connect 
    myata = AtaWrapper(ata_IP, ata_admin)
    myata.connect()
#    myata.remove_ports()
#    #i.e., bindport wifi_01 10.150.4.98 1 1
#    #i.e., bindport enet_01 10.150.4.98 2 1
#    myata.bind_vw_port(wifi_01, veriwave_IP, wifi_blade_01, wifi_port_01)
#    myata.bind_vw_port(enet_01, veriwave_IP, enet_blade_01, enet_port_01)
#    myata.info()
#    myata.set_band_channel(wifi_01, fiveg_band, fiveg_channel)
#    myata.scanbss(wifi_01)
#    print myata.find_ssid(wifi_01, apwisprSSID) != None
#    # Only proceed if desired ssid is found 
#    # sample code for scanning all 2.4GHz channel for bss
#    #for i in range(1, 12):
#    #    myata.set_band_channel(wifi_01, twog_band, i)
#    #    myata.scanbss(wifi_01)
#
#    #myata.get_bss_info()
#    pdb.set_trace()
    ssid = 'chris-test'
#    if myata.find_ssid(wifi_01, ssid) == None:
    myata.create_client_group('g3', 5, ssid, client_type=wifi_client_type, security_type = None, passphrase=None)
    # dave need to fix 
#    if( myata.find_ssid(wifi_01, apwisprSSID) == None ):
#        myata.create_client("wep_01", apWepSSID, wifi_client_type, \
#                                  wifi_wep, wifi_wep_passphrase)
#        myata.create_client("wpa_01", apSSID, wifi_client_type, \
#                                  wifi_security_type, wifi_security_passphrase)
#        myata.create_8021x_client("dot1x_01", apdot1xSSID, wifi_client_type, \
#                                  wifi_8021x, user_ID, user_password)
#        myata.create_8021x_group("dot1x_01_gp", client_count, apdot1xSSID, wifi_client_type, \
#                                  wifi_8021x, user_ID, user_password, start_index)
#        myata.create_client_group(clg_group_name, client_count, apSSID, wifi_client_type, \
#                                  wifi_security_type, wifi_security_passphrase)
#        myata.create_eapsim_client("eapsim_01", apdot1xSSID, wifi_client_type, \
#                                  wifi_8021x_eap_sim, eap_sim_user_ID, \
#                                  simCypherKey, simResponse)
#        myata.create_eapsim_client("eapsim_02", apdot1xSSID, wifi_client_type, \
#                                  wifi_8021x_eap_sim, eap_sim_user_ID, \
#                                  simCypherKey, simResponse)
#        for i in range(client_count):
#            sleep(1)
#            wispr_name = "wispr_%d" % (i) 
##           For ZD only            
##            myata.create_wispr_client(wispr_name, apwisprSSID, "Dave19", "http://www.google.com", \
##                                      'www.google.com', '74.125.239.49', '192.168.0.2','google', \
##                                      '', 'username,text,user3;submit,static,ok;password,password,user3',80)
### for third party AP
#            myata.create_wispr_client(wispr_name, apwisprSSID, webAuth, "http://www.google.com", \
#                                      'www.google.com', '74.125.239.49', '10.0.21.170','yahoo', \
#                                      'loginForm', 'UE-Username,steve,steve',80)
##            myata.create_wispr_client(wispr_name, apwisprSSID, webAuth, "http://www.google.com", \
##                                      'www.google.com', '74.125.239.49', '10.0.21.170','yahoo', \
##                                      'loginForm', 'UE-Username,testing,testing',80)
#        
#
#        # ICMP Flow specific for wispr
#        pdb.set_trace()
#        for n in range(2):
#            for j in range(client_count):
#                wispr_name = "wispr_%d" % (j) 
#                print "pingFrom %s 8.8.8.8\n" % (wispr_name)
#                rc = myata.ping_client(wispr_name, "8.8.8.8")
#                print rc

#        myata.create_server(server_name)
#        myata.create_flow(flow_name, server_name, "eapsim_01")
#        myata.create_flow("new_flow1", server_name, "eapsim_01", "FTP")
#        myata.create_flow_group("eapsim_g1", flow_count, server_name, "eapsim_01", "FTP")
#        myata.destroy_client("wep_01")
#        myata.destroy_client("wpa_01")
#        myata.destroy_client("dot1x_01")
#        myata.destroy_client("eapsim_01")
#        myata.destroy_client_group(clg_group_name)
        
#    dic1 = {}
#    myata = Atatelnet.AtaTelnet("10.150.4.97", "admin")
#    myata.login()
#    myata.list_all()
#    rc = myata.perform("purge ports")
#    print rc
#    rc = myata.perform("bindport wifi_01 10.150.4.98 1 1")
#    print rc
#    rc = myata.perform("bindport enet_01 10.150.4.98 2 1")
#    print rc
#    dic1 = myata.list_all()
#    print dic1
#    myata.perform("setchannel wifi_01 5000 161")
#    dic1 = ata_lib.get_ssid_info(myata, "wifi_01")
#    print dic1
#    if (dic1.get(apSSID) != None):
#        print "Found %s " % apSSID
#        rc = myata.perform("createClientGroup clg_01 100 %s clientType=802.11a/b/g/n security=WPA-PSK-AES networkKey=password123" % apSSID)
#        print rc
#        myata.perform("createserver server_01")
#        print rc
#        rc = myata.perform("createFlowGroup s_to_c 100 server_01 clg_01")
#        print rc
#        print "Trying getFlowGroupInfo s_to_c"
#        dic2 = {}
#        dic2 = myata.perform("getFlowGroupInfo s_to_c")
#        while dic2.get("admin ready") != None:
#            print "sleeping  "
#            sleep(1)
#            dic2 = myata.perform("getFlowGroupInfo s_to_c")
#        while(int(dic2['flowGroupStats']['RXFlowIPOctets']) == 0):
#            print "sleeping  "
#            sleep(1)
#            dic2 = myata.perform("getFlowGroupInfo s_to_c")
#        print dic2.keys()
#        print dic2.values()
#        pdb.set_trace()
