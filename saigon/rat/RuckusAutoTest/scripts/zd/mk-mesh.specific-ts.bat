@echo off
maketestbed.py name=mesh.specific location=S3 owner=tntoan@s3solutions.com.vn sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Mesh_Configuration.py name=mesh.specific testsuite_name="Mesh Configuration" sta_id=0 interactive_mode=False

addtestsuite_ZD_Mesh_Forming.py name=mesh.specific testsuite_name="Mesh Forming" interactive_mode=False

addtestsuite_ZD_Mesh_Provisioning.py name=mesh.specific testsuite_name="Mesh Provisioning" sta_id=0 interactive_mode=False

addtestsuite_ZD_Mesh_UI.py name=mesh.specific testsuite_name="Mesh WebUI" interactive_mode=False