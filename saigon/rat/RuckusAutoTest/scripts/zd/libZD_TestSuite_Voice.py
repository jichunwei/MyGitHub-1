from libZD_TestSuite import *
from libZD_TestSuite import _getAtrVal
import subprocess

# for create tb ZD_Voice 
def getTestbed4(**kwargs):
    atrs = {"ApUseSym": True}
    atrs.update(kwargs)
    return getTestbed3(**atrs)

def getTestbed3(**kwargs):
    atrs = {'zd_ip_addr':'192.168.0.2', 
            'svr_ip_addr':'192.168.0.252', 
            'splk_gw_ip_addr': '192.168.0.10',
            'splk_svp_ip_addr': '192.168.0.20',
            'tbtype': 'ZD_Voice',
            'L3Switch': {},
            'shielding_box': {},
            'push_keypad_device': {},
            'shell_key':'',
            'zd_username':'admin',
            'zd_password':'admin',
            'splk_username':'admin',
            'splk_password':'admin'}
    atrs.update(kwargs)

    tb_name = atrs['name'] if atrs.has_key('name') \
              else raw_input("Your test bed name: ")

    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = atrs['location'] if atrs.has_key('location') \
                      else raw_input("Testbed location: ")
        tb_owner = atrs['owner'] if atrs.has_key('owner') else raw_input("Testbed owner: ")
        sta_ip_list = atrs['sta_ip_list'] if atrs.has_key('sta_ip_list') \
                      else raw_input("Station IP address list (separated by spaces): ").split() 
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            ap_sym_dict = getZoneDirectorAPsDict({'ip_addr': atrs['zd_ip_addr']})
            ap_mac_list = [ x['mac'] for x in ap_sym_dict.values() ]
        else:
            ap_mac_list = atrs['ap_mac_list'] if atrs.has_key('ap_mac_list') \
                          else raw_input("AP MAC address list (separated by spaces): ").split()
            
        super_ruca_id_list = getSuperRucaIdList()

        zd_conf = _getAtrVal('zd_conf', atrs,
                  { 'browser_type':'firefox'
                  , 'ip_addr': atrs['zd_ip_addr']
                  , 'username': atrs['zd_username']
                  , 'password': atrs['zd_password']
                  })
        shell_key = zd_conf['shell_key'] if zd_conf.has_key('shell_key') else raw_input("shell key:(!v54!)")
        if shell_key is None or shell_key is '':
            shell_key = '!v54!'
        zd_conf['shell_key'] = shell_key
        
        sta_conf = _getAtrVal('sta_conf', atrs, {})
        srv_conf = _getAtrVal('srv_conf', atrs,
                   { 'ip_addr': atrs['svr_ip_addr']
                   , 'user': 'lab'
                   , 'password': 'lab4man1'
                   , 'root_password': 'lab4man1'
                   })
        
        splk_srv_conf = _getAtrVal('splk_server', atrs,
                                   { 'enabled':True,  
                                     'gw_cfg':{ 'ip_addr':atrs['splk_gw_ip_addr'],
                                                'username':atrs['splk_username'],
                                                'password':atrs['splk_password']},
                                     'svp_cfg':{ 'ip_addr':atrs['splk_svp_ip_addr'],
                                                 'username':atrs['splk_username'],
                                                 'password':atrs['splk_password']}
                                    })

        tb_config = { "ZD": zd_conf
                    , "sta_conf": sta_conf
                    , "server": srv_conf
                    , "ap_mac_list": ap_mac_list
                    , "splk_server": splk_srv_conf
                    , "sta_ip_list": sta_ip_list
                    }
        if atrs.has_key('ApUseSym') and atrs['ApUseSym']:
            tb_config['ap_sym_dict'] = ap_sym_dict

        if atrs.has_key('L3Switch'):
            if not atrs['L3Switch']:
                atrs['L3Switch'] = { 'ip_addr': '192.168.0.253'
                                   , 'username': 'admin'
                                   , 'password': ''
                                   , 'enable_password': ''
                                   }
            tb_config['L3Switch'] = atrs['L3Switch']
            
        if super_ruca_id_list:
            tb_config['super_ruca_id'] = super_ruca_id_list
        if atrs.has_key('shielding_box') and not atrs['shielding_box']: 
            print "Please pick up AP in Box1"
            box1_ap_list = getActiveAp(ap_sym_dict) 
            print "Active AP : %s" % box1_ap_list
            print "Please pick up AP in Box2"
            box2_ap_list = getActiveAp(ap_sym_dict)
            print "Active AP : %s" % box2_ap_list
            box1_super_ruca_id = raw_input("input 3 super ruca id in box1 %s: " % super_ruca_id_list).split()
            box2_super_ruca_id = raw_input("input 3 super ruca id in box2 %s: " % super_ruca_id_list).split()
            atrs['shielding_box'] = {'box1': {'active_ap' : box1_ap_list,
			                               'super_ruca_id' : box1_super_ruca_id},
                                  'box2': {'active_ap' : box2_ap_list,
			                               'super_ruca_id' : box2_super_ruca_id}}
            tb_config['shielding_box'] = atrs['shielding_box']
            
        if atrs.has_key('push_keypad_device') and not atrs['push_keypad_device']:
            dev = atrs['push_keypad_device']['dev'] = raw_input("input the serial port number connect to the push keypad device(like COM1, COM2 ...): ")
            if dev: atrs['push_keypad_device']['baudrate'] = 9600
        tb_config['push_keypad_device'] = atrs['push_keypad_device']
        # ATTN: case sense for keywords
        for opt_key in ['Mesh', 'APConnMode', 'RoutingVLANs']:
            if atrs.has_key(opt_key):
                tb_config[opt_key] = atrs[opt_key]

        m = re.match(r'^([^@]+)@(|[^\s]+)', tb_owner)
        if not m:
            tb_owner = tb_owner + '@ruckuswireless.com'
        elif len(m.group(2)) < 1:
            tb_owner = m.group(1) + '@ruckuswireless.com'

        # Only ask the user for info to initiate testbed into
        # a mesh topology at the time of creating testbed.
        testbedInitToMesh(tb_config)

        testbed = { 'name':tb_name
                  , 'tbtype': TestbedType.objects.get(name=atrs['tbtype'])
                  , 'location':tb_location
                  , 'owner':tb_owner
                  , 'resultdist':tb_owner
                  , 'config':str(tb_config)
                  }

        tb = Testbed(**testbed)
        tb.save()
    return tb

def showApSymListByShieldingBox(ap_sym_dict, shielding_box_dict):
    for box in sorted(shielding_box_dict.keys()):
        print "APs in %s" % box
        for k in shielding_box_dict[box]['active_ap']:
            print "   %s : mac=%s; status=%s" % (k, ap_sym_dict[k]['mac'], ap_sym_dict[k]['status'])

def getActiveApByShieldingBox(ap_sym_dict, shielding_box_dict):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter 2 symbolic APs on different shielding box from above list, separated by space (enter all for all APs): """
    while (True):
        showApSymListByShieldingBox(ap_sym_dict, shielding_box_dict)
        active_ap_list = raw_input(select_tips).split()
        if not active_ap_list: continue
        if re.match(r'^all$', active_ap_list[0], re.M):
            return sorted(ap_sym_dict.keys())
        if _list_in_dict(active_ap_list, ap_sym_dict):
            return active_ap_list
                    
def getSuperRucaIdList():
    cmdline='rac -d'
    output = subprocess.Popen(cmdline,  stdout=subprocess.PIPE).communicate()[0]
    rdata = output.split('\r\n')
    pattern = r"Device\s*(\d+)"
    id_list = []
    for line in rdata:
        m = re.match(pattern, line)
        if m:
            id_list.append(str(m.group(1)))
    return id_list

def _getAtrVal(name, atrs, default):
    val = atrs[name] if atrs.has_key(name) else default
    return val

def _list_in_dict(_list, _dict):
    for _l in _list:
        if not _dict.has_key(_l):
            return False
    return True
