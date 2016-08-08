#[tl]
server_url = 'http://qa-tms.tw.video54.local/testlink/lib/api22/xmlrpc.php'
project_name = 'Zone Director'
build_no = '9.5.0.0.156'
dev_key =  '038812301d663e2712bbbbd3cd28ffa6'
plan_name = 'ZD Real life Automation'

#[cf]
mail_server = '172.16.110.5'
mail_to = ['an.nguyen@ruckuswireless.com']

#[tc]
testcases = {'Get all APs Info': 'u.zd.get_all_ap_cfg',
             'Get all WLAN Groups': 'u.zd.get_all_wlan_group'}

interval = 60