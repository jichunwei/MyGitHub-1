@echo off

maketestbed.py name=qingdao.mesh.wlangroup location=S3 owner=tntoan@s3solutions.com.vn sta_ip_list=['192.168.1.11','192.168.1.12']

ats_ZD_Mesh_EncryptionTypes_WlanGroups.py name=qingdao.mesh.wlangroup testsuite_name = "Mesh - WlanGroup - EncryptionType" targetap=True sta_11ng=0 sta_11na=1 interactive_mode=False

ats_ZD_Mesh_EncryptionTypesWebAuth_WlanGroups.py name=qingdao.mesh.wlangroup testsuite_name="Mesh - WlanGroup - WebAuth" targetap=True sta_11ng=0 sta_11na=1 interactive_mode=False

ats_ZD_Mesh_VLAN_Integration_WlanGroups.py name=qingdao.mesh.wlangroup testsuite_name="Mesh - WlanGroup - VLANs" targetap=True sta_11ng=0 sta_11na=1 interactive_mode=False

ats_ZD_Mesh_RateLimit_WlanGroups.py name=qingdao.mesh.wlangroup testsuite_name="Mesh - WlanGroup - Rate Limiting" targetap=True sta_11ng=0 sta_11na=1 interactive_mode=False
