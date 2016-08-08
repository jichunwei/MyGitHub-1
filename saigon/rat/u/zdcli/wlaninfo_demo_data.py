_ap_cfg_info = """
  ether MAC = 00:27:41:01:08:b0; DHCP IP Addr = 192.168.4.217
  Tunnel Mode = LWAPP Layer 2; last disconnect = Thu Jan  1 00:00:00 1970
  Netmask = 0.0.0.0; Gateway = 0.0.0.0
  DNS1 = 0.0.0.0; DNS2 = 0.0.0.0
  Management VLAN: Status = disabled; ID = 0
  Mesh:
     Enabled = true;   Mode= Auto;  ACL= no
     ACL Entries = 0
  Ether MAC = 00:27:41:01:08:b0; Auth Mode = PSK; Approved = True
  Version= 8.6.0.0.3
  State=PSK key installed ; Description = PSK ruckuswireless way!
  Country=US
  Qos Heuristic:
    Octet During: voip=600; video=50000; data=0; background=0
    Octet Between: voip=1000; video=500000
      data=0; background=0
    mix=5000; max=15000
  TOS:
    Classification:
      Voice=0xE0,0xC0,0xB8; Video=0xA0,0x80
      Data=0x0; Background=0x0
    marking:
      VoIP=0x0; Video=0xA0
      date: start=2010-02-25 8:30:33; end = 2010-02-25 15:30:33
      Data=0x0; Background=0x0
  Num Radios = 0"""

_mocked_ap_info = """
AP: mac=00:22:7f:24:a9:00; IP Addr = 192.168.0.125
  Netmask = 255.255.255.0; Gateway = 192.168.0.253
  DNS1 = 0.0.0.0; DNS2 = 0.0.0.0
  Management VLAN ID = 0
  Model = zf2741 ; Tunnel Mode = LWAPP Layer 2
  SW Version=8.6.0.0.58
  State = Operational; ref_cnt = 2; cfg_queue=0;  Connected since:Thu Feb 18 02:14:44 2010
  Classification status= enabled
  Tx Failure Threshold= 50
  TOS Classification:       Voice= 0XE0 0XC0 0XB8 ;  Video= 0XA0 0X80 ;  Data= 0X00 ;  Background= 0X00
  Dot1p Classification:    Voice= 0X06 0X07 ;  Video= 0X04 0X05 ;  Data= 0X00  ; Background= 0X00
  [Heuristic]: AP's method to control traffic flow.
    Classifier                         VoIP      Video      Data      Background
    ------------------------------     -------   ---------  -------   ----------
    Octet Count During Classify        600       50000      0         0
    Octet Count BetweenClassify        10000     500000     0         0
    Min/Max Avg Packet Length          70/400    1000/1518  0/0       0/0
    Min/Max Avg Inter Packet Gap       15/275    0/65       0/0      0/0
  mesh: enabled=Y; mesh_node_type=Auto; mesh_role=RAP; mesh do acl=N
  ACL: entries = 1
    mac= 00:1d:2e:16:3a:c0
    token=abc,
  Country=US
  Num of Radios = 1
  Radio: id= 0; type=11b/g; channel=1 ; Auto enabled = Yes
  Num of clients =0
  wlangroup: id=1
    Channel=0 (Auto); TX power=auto|full; antenna = Auto; env=000000
    Key table size=112 ; Used key entries=3
    80211.h=No; Mix mode=0; DTIM period=1
    Beacon interval=100; Occupancy limit=100
    CFP period =1; CFP max duration=100; max clients=100;    wmm uapsd=enabled
    tx_mcast    =                    0 ;  rx_mcast   =          45095372663
    tx_frag     =              1805380 ;  rx_frag    =              1793798
    tx_bytes    =             28322500 ;  rx_bytes   =             28134022
    tx_fail     =                11972 ;  tx_retry   =                13640
    tx_mul_retry=                    0 ;  rx_dup     =                    0
    good rts    =                    0 ;  failed rts =                    0
    failed ack  =                    0 ;  fcs err    =                    0
    decrypt err =               114240
    curr avg rssi    = 0 (count=0)
    Number of VAP = 1
    VAP: mac= 00:27:41:01:01:f2; id = 254 ;wlan id = 0 ;vlan id = 0 ;num_sta/num_roaming_sta = 0/0 ;num_ht_sta = 0
      state = Running ;ref_cnt = 2
      AP: mac = 00:27:41:01:01:f0; ip=192.168.4.199; radio_id = 0 ; vap index = 0
"""

