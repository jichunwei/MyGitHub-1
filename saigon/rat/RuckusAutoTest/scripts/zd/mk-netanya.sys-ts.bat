@echo off
maketestbed.py name=netanya.sys location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11','192.168.1.12']

addtestsuites_ZD_System_AP_Control.py name=netanya.sys testsuite_name="System - AP Control" interactive_mode=False

addtestsuites_ZD_System_Roles.py name=netanya.sys testsuite_name="System - Roles" station="(0,'g')" interactive_mode=False

addtestsuites_ZD_System_Services.py name=netanya.sys testsuite_name="System - Services" targetap=True interactive_mode=False

addtestsuites_ZD_System_Users.py name=netanya.sys testsuite_name="System - Users" interactive_mode=False

addtestsuite_Wlan_Option_8BSSIDs.py name=netanya.sys testsuite_name="WLAN Options - 8 BSSIDs" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_ACL.py name=netanya.sys testsuite_name="WLAN Options - ACL" interactive_mode=False

addtestsuite_ZD_Administration.py name=netanya.sys testsuite_name="ZD Administration" interactive_mode=False

addtestsuite_ZD_AP_Classification.py name=netanya.sys testsuite_name="QoS - SmartCast" targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Client_Isolation.py name=netanya.sys testsuite_name="WLAN Options - Wireless Client Isolation" sta_11g="(0,'g')" sta_11n="(1,'ng')" interactive_mode=False

addtestsuite_ZD_EncryptionTypes.py name=netanya.sys testsuite_name="Encryption Types - 11g" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_EncryptionTypes.py name=netanya.sys testsuite_name="Encryption Types - 11ng" station="(1,'ng')" interactive_mode=False

addtestsuite_ZD_EncryptionTypesWebAuth.py name=netanya.sys testsuite_name="Encryption Types - Web Auth" targetap=True  station="(0,'g')" interactive_mode=False

addtestsuite_ZD_GuestAccess.py name=netanya.sys testsuite_name="WLAN Types - Guest Access" targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_MapView.py name=netanya.sys testsuite_name="MAP View" max_size=2 interactive_mode=False

addtestsuite_ZD_RateLimit.py name=netanya.sys testsuite_name="WLAN Option - Rate Limiting" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_System.py name=netanya.sys testsutie_name="System - Basic" interactive_mode=False

addtestsuite_ZD_System_AuthServers.py name=netanya.sys testsuite_name="System - Authentication Servers" interactive_mode=False

addtestsuite_ZD_VLAN.py name=netanya.sys testsuite_name="VLAN configuration" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Zero_IT.py name=netanya.sys station="(0,'g')" interactive_mode=False

addtestsuite_ZD_ZeroIT_Misc.py name=netanya.sys testsuite_name="Zero-IT Activation - Misc" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_WLAN_Options_HideSSID.py name=netanya.sys targetap=True testsuite_name="VLAN Options - Hide SSID" station="(0,'g')" interactive_mode=False

addtestsuite_ZD_VLAN_GuestAccess.py name=netanya.sys testsuite_name="VLAN Configuration - Gueset Access" targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_VLAN_WebAuth.py name=netanya.sys testsuite_name="VLAN Configuration - WebAuth" targetap=True station="(0,'g')" interactive_mode=False
