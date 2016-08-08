@echo off
maketestbed.py name=l2.mesh.fanout location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Mesh_EncryptionTypes.py        name=l2.mesh.fanout testsuite_name="Mesh - Integration - Encryption"    targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_EncryptionTypesWebAuth.py name=l2.mesh.fanout testsuite_name="Mesh - Integration - WebAuth"       targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_GuestAccess.py            name=l2.mesh.fanout testsuite_name="Mesh - Integration - GuestAccess"   targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_RateLimit_v2.py           name=l2.mesh.fanout testsuite_name="Mesh - Integration - Rate Limiting" targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_VLAN.py                        name=l2.mesh.fanout testsuite_name="Mesh - Integration - VLANs"         station="(0,'g')" interactive_mode=False
