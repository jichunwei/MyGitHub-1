@echo off
maketestbed.py name=l2.mesh.fanout.tunnel location=S3 owner=tntoan@s3solutions.com.vn shell_key='!v54!' sta_ip_list=['192.168.1.11']

addtestsuite_ZD_Odessa_GuestAccess.py   name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_GuestAccess.py   name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - Guest Access" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=True targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False

addtestsuite_ZD_Odessa_WebAuth.py       name=l2.mesh.fanout.tunnel mode=l2 tunnel=True vlan=False targetap=True station="(0,'g')" testsuite_name="Mesh - Integration - WebAuth" interactive_mode=False
