@echo off
REM l2.mesh.fanout test bed
maketestbed.py name=l2.mesh.fanout location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Mesh_EncryptionTypes.py        name=l2.mesh.fanout testsuite_name="Mesh - Integration - Encryption"    targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_EncryptionTypesWebAuth.py name=l2.mesh.fanout testsuite_name="Mesh - Integration - WebAuth"       targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_GuestAccess.py            name=l2.mesh.fanout testsuite_name="Mesh - Integration - GuestAccess"   targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_Mesh_RateLimit_v2.py           name=l2.mesh.fanout testsuite_name="Mesh - Integration - Rate Limiting" targetap=True station="(0,'g')" interactive_mode=False

addtestsuite_ZD_VLAN.py                        name=l2.mesh.fanout testsuite_name="Mesh - Integration - VLANs"         station="(0,'g')" interactive_mode=False

REM l2.mesh.fanout.tunnel test bed

maketestbed.py name=l2.mesh.fanout.tunnel location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Odessa_GuestAccess.py   name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_GuestAccess.py   name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False

REM l3.mesh.fanout.tunnel test bed
maketestbed.py name=l3.mesh.fanout.tunnel location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Odessa_GuestAccess.py   name=l3.mesh.fanout.tunnel mode=l3 tunnel=False vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_GuestAccess.py   name=l3.mesh.fanout.tunnel mode=l3 tunnel=False vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l3.mesh.fanout.tunnel mode=l3 tunnel=False vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l3.mesh.fanout.tunnel mode=l3 tunnel=False vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False
