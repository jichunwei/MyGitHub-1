@echo off
maketestbed.py name=odessa.sys location=S3 owner=tntoan@s3solutions.com.vn sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Odessa_L3LWAPP.py name=odessa.sys testsuite_name="L3LWAPP" targetap=True interactive_mode=False

addtestsuite_ZD_Odessa_AdminAuth.py name=odessa.sys testsuite_name="WebAuth" targetap=True interative_mode=False

addtestsuite_ZD_Odessa_AP_IP_Management.py name=odessa.sys testsuite_name="AP IP Management" targetap=True interactive_mode=False

