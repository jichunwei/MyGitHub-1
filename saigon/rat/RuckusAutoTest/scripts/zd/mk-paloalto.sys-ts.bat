@echo off

maketestbed.py name=paloalto.sys location=S3 owner=tntoan@s3solutions.com.vn sta_ip_list=['192.168.1.11','192.168.1.12']

ats_ZD_Palo_Alto_32WLANs.py name=paloalto.sys testsuite_name="32 Wlan - Basic" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_L2_ACL_With_Specific_APs.py name=paloalto.sys testsuite_name="L2 ACL" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_L3_L4_ACL_With_Specific_APs.py name=paloalto.sys testsuite_name="L3/L4 ACL" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_WISPr.py name=paloalto.sys testsuite_name="WISPr - ACL" targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_WISPr_ACL_Integration_With_Specific_APs.py name=paloalto.sys testsuite_name="WISPr ACL" targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_LDAP_Integration.py name=paloalto.sys testsuite_name="LDAP Integration" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_Accounting_With_Specific_APs.py name=paloalto.sys testsuite_name="ZD Accounting" targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_SNMP.py name=paloalto.sys testsuite_name="ZD SNMP" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_SNMP_With_Specific_APs.py name=paloalto.sys testsuite_name="ZD SNMP with Specific APs" targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_MAC_Authentication.py name=paloalto.sys testsuite_name="MAC Authentication" valid_sta=0 invalid_sta=1 interactive_mode=False

ats_ZD_Palo_Alto_MAC_Authentication_Encryption_Types.py name=paloalto.sys testsuite_name="MAC Authentication with Encryption Types" sta_id=0 interactive_mode=0

ats_ZD_Palo_Alto_MAC_Authentication_Integration_With_Specific_APs.py name=paloalto.sys testsuite_name="MAC Authentication Integration" targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_CustomizedGuestPassPrintout.py name=paloalto.sys testsuite_name="Customize Guest Pass Printout" sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_IPTV.py name=paloalto.sys targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_IPTV_Port_Matching_Filter.py name=paloalto.sys targetap=True sta_id=0 interactive_mode=False

ats_ZD_Palo_Alto_IPTV_Smartcast.py name=paloalto.sys targetap=True sta_id=0 interactive_mode=False



