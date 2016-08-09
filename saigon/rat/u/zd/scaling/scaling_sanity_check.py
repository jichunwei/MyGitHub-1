"""
Description: sanity check SIMAP Image and ZD Image which can deploy WLANs to Simulator AP or RuckusAP correctly, at the same time, 
system can wireless client can associate to RuckusAP with different WLANs, use WLANGroup to group WLAN and AP so that wireless
client can associate to correct AP with special WLAN.
   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director.
   2. Station can work correctly, and agent embed into station can access correctly.
   3. Lhotse server can work, which is used for fetching SIMAP Image or ZD Image.
   4. TFTP server can work, and install simage script has put into root folder of TFTP Server.
   5. SIMAP Server can work, we can invoke Simulator any time.

   Required components: 'ZoneDirector, Station'
   Result type: PASS/FAIL 
   Results: PASS: All the values on the wizard match with the corresponding ones in the dictionary of default values.
            FAIL: At least one value on the wizard is different from the corresponding one in the dictionary.      

   Messages: 
       - if the result is PASS, no message is shown. 
       - if the result is FAIL, an error message is shown.
   Test procedures:
       Config:
        +Initial parameters and download simage from Lhotse.
        +Start up SIMAPs from SIMAP Server by different AP models.
        +Verify all of SIMAPs can work correctly.
        +Remove all WLANs configuration from webui.
        +Retrieve all of APs include RuckusAP, SIMAP
       Test:                
        +Upgrade ZD firmware if need
        +Step by step configure WLAN and make sure this WLAN can perform to SIMAP and RuckusAP.
        +Configure WLAN group with WLAN, and take RuckusAP to associate this WLANGROUP, and then 
        take a wireless client to associate to this AP, make sure can work correctly.        
       Cleanup:
        +Remove all WLANs.
   How it was tested:
       1.  Change the a default value the test must return FAIL.
              
"""
import logging
import time
import re
import os

from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

from contrib.wlandemo import defaultWlanConfigParams as wlancfg
from contrib.download import image_resolver as imgres


from u.zd.scaling.lib import scaling_utils as utils
from u.zd.scaling.lib import scaling_zd_lib as lib
from u.zd.simap import simap_image_installer as installer
from u.zd.simap import simap_vm_controller as controller

def do_config(tcfg):
    _cfg = dict()
    _cfg['zd'] = utils.create_zd(**tcfg)
    _cfg['ap_username'] = _cfg['zd'].username
    _cfg['ap_password'] = _cfg['zd'].password
    
    sta_cfg = dict(sta_ip_addr='192.168.1.11')
    if tcfg.has_key('target_station'):
        sta_cfg['sta_ip_addr'] = tcfg['target_station']
        
    _cfg['station'] = utils.create_station(**sta_cfg)  
    select_client_and_check(_cfg['station'])
     
    logging.info("[Config]initialize environment")
    init_env(_cfg, tcfg)
    logging.info("[Config]finish enviroment initialization.")    
    logging.info("[Config]try to remove all of configuration from ZD")
    _cfg['zd'].remove_all_cfg()
    logging.info("[Config]remove all of configuration from ZD successuflly")        
    return _cfg

def do_test(cfg):
        logging.info('Begin to retrieve APs from webui')
        aps = lib.retrieve_aps(cfg['zd'])
        
        cfg['aps'] = aps
                 
        if cfg['do_zd_upgrade']:
            logging.info('Try to upgrade image of ZoneDirector to [%s]' % cfg['img_file_path'])
            lib.upgrade_sw(cfg['zd'], cfg['img_file_path'])
            logging.info('ZoneDirector image upgrade done.')
            logging.debug('Try to install SIMAP image')
            installer.main(**cfg['package_simap_cfg'])
            
            try:
                cfg['zd'].do_login()
            except:
                pass
                
        logging.info('Begin to verify All APs status and make sure all of the are connected')
        lib.verify_aps(cfg['zd'], aps, timeout=1200)
        logging.info('All of APs are connected.') 

#        zhlp.wgs.remove_wlan_groups(cfg['zd'])
#        zhlp.wlan.delete_all_wlans(cfg['zd'])        
        
        logging.info('Sanity check different wlans[%s]' % cfg['wlans'])
        errmsg = sanity_check_wlans(cfg['wlan_group_prefix'], cfg)
        
        if errmsg and errmsg.has_key('ERROR'):
            return ("FAIL", errmsg)
        
        passmsg = 'Sanity check successfully!SIMAP Version[%s], SIMAP models[%s], WLANs[%s]' \
        % (cfg['sim_version'], cfg['modelsExpr'], cfg['wlans'])
        
        return ("PASS", passmsg.strip())    

def do_clean_up(cfg):
    zhlp.wgs.remove_wlan_groups(cfg['zd'])
    zhlp.wlan.delete_all_wlans(cfg['zd'])    

def init_env(_cfg,tcfg):
        
        _cfg['do_zd_upgrade'] = False
        if tcfg.has_key('do_zd_upgrade'):
            _cfg['do_zd_upgrade'] = tcfg['do_zd_upgrade']
            
        wlans = tcfg['wlans']
        _cfg['wlans'] = wlans
        _cfg['wlan_group_prefix'] = 'scaling-sanity-check'
        
        if _cfg['do_zd_upgrade']:
                        
            _cfg['zd_build_stream'] = None
            if tcfg.has_key('zd_build_stream'):
                _cfg['zd_build_stream'] = tcfg['zd_build_stream']
        
            _cfg['zd_bno'] = None
            if tcfg.has_key('zd_bno'):
                _cfg['zd_bno'] = tcfg['zd_bno']
            
        tftpserver = None
        if tcfg.has_key('tftpserver'):
            tftpserver = tcfg['tftpserver']
                
        _cfg['sim_version'] = None
            
        _cfg['simap_build_stream'] = None
        if tcfg.has_key('simap_build_stream'):
            _cfg['simap_build_stream'] = tcfg['simap_build_stream']
            
        _cfg['simap_bno'] = None
        if tcfg.has_key('simap_bno'):
            _cfg['simap_bno'] = tcfg['simap_bno']
            
        _cfg['file_path'] = None
        if tcfg.has_key('file_path'):
            _cfg['file_path'] = tcfg['file_path']
        
        wlan_conf_list = []
        for wlan in wlans :
            wlan_conf_list.append(wlancfg.get_cfg(wlan))
        
        _cfg['wlan_conf_list'] = wlan_conf_list
            
        _cfg['check_status_timeout'] = 120   
        
        zd = _cfg['zd']
        zd_cli = restart_zd_cli( zd )
        _cfg['zd_cli'] = zd_cli
        
        logging.info("[Initial]try to shut down SIMAP Server")
        time.sleep(5)
        agent = controller.SimAPsAgent()
        _cfg['agent'] = agent
        
        _cfg['vm_ip_addr'] = '172.18.35.150'
        if tcfg.has_key('vm_ip_addr'):
            _cfg['vm_ip_addr'] = tcfg['vm_ip_addr']
            
        vmcfg = dict(ipaddr=_cfg['vm_ip_addr'], zd_ip=zd.ip_addr)
        
        agent.touch_tcfg(vmcfg)
        agent.connect_te()
        agent.shutdown_simaps()
         
        logging.info("[Initial]shut down SIMAP Server successfully")
        
                                
        logging.info('try to remove all of APs and wait for reconnect')
        zd.remove_approval_ap()
        
        logging.info('all of APs remove successfully')
        
        logging.info('waiting for all APs reconnected.')
        time.sleep(150)
        
#        wlan_conf_list = tcfg['wlan_conf_list']
        logging.info("[Initial]try to retrieve models of ruckus aps")
        _cfg['ruckus_aps'] = lib.resolve_verify_all_aps(zd)
        
               
        logging.info('begin to configure SIMAP firmware.')
        ruckusAPsModels = lib.retrieve_aps_models(zd)
        simapsModels = convert_models(ruckusAPsModels)
        modelsExpr = retrieve_models(simapsModels)
        logging.info("[Initial]the SIMAP's models are %s" % modelsExpr)
        
        #Download image of simulator from lhotse and set the image version to sim_verion attribute.
        logging.info("[Initial]try to download simulator image[buildstream=%s, bno=%s]" % (_cfg['simap_build_stream'], _cfg['simap_bno']))        
        download_simage(_cfg)
        
        sim_version = _cfg['sim_version']
        logging.info("[Initial]simap image is [%s] which has downloaded" % sim_version)
        
        package_simap_cfg = dict(shell_key="!v54!",
                                      ip_addr=zd.ip_addr,
                                      username=zd.username,
                                      password=zd.password,
                                      tftpserver=tftpserver,
                                      model="ss2942",
                                      version=sim_version,
                                      do_install_ap=True,
                                      do_upload_image=True,
                                      do_upload_script=True,
                                      do_remove_image=False,
                                      do_remove_script=False,
                                      )
        
        package_simap_cfg['model'] = modelsExpr
        _cfg['modelsExpr'] = modelsExpr
        _cfg['package_simap_cfg'] = package_simap_cfg
        
        logging.info('package_sim-cfg [%s]' % package_simap_cfg)
        installer.main(**package_simap_cfg)
        logging.info('SIMAP firmware configure successfully')
        
        bootup_simaps(agent, simapsModels)
        if not verify_simaps_from_vm(agent, len(ruckusAPsModels)):
            raise Exception('Some of SIMAPs haven\'t boot up correctly, please check.')
                
        logging.info('[Initial]begin verify RuckusAPs and SimAPs, make sure all of them are connected.')
        
        try:        
            zd.do_login()
        except:
            pass
        
        lib.verify_aps_by_models(zd, simapsModels)
        logging.info('[Initial]all of RuckusAPs and SimAPs are connected.') 

def bind_wlan_groups_to_ap(ap_mac, conf):    
    zhlp.ap.assign_to_default_wlan_group(conf['zd'], ap_mac)
    radios = zhlp.ap.get_supported_radio(conf['zd'], ap_mac)
    for radio in radios:
        zhlp.ap.assign_to_wlan_groups_by_radio(conf['zd'], ap_mac, conf['wlan_group_prefix'], radio, conf['wlan_group_prefix'])

def assign_client_to_wlan(wlan_conf, conf,check_status_timeout = 100):
#        import pdb
#        pdb.set_trace()
    target_station = conf['station']
    target_station.remove_all_wlan()
    time.sleep(10)    
#    tmethod.renew_wifi_ip_address(target_station, check_status_timeout)
    errmsg = tmethod.assoc_station_with_ssid(target_station, wlan_conf, check_status_timeout)
    
    if errmsg:
        errmsg = '[Connect failed]: %s' % errmsg
        logging.info(errmsg)
        
        return {"ERROR":errmsg}
                                
def go_through_aps_wlan(wlan_conf, aps, ap_username, ap_password):
        for index in range(len(aps)):
            active_ap = RuckusAP(dict(ip_addr = aps[index]['ip_addr'], username = ap_username, password = ap_password ))
            msg = tmethod.verify_wlan_on_aps(active_ap, wlan_conf['ssid'])            
            if not msg and msg != '':
                errmsg = msg
                return {"ERROR":errmsg}
            
        passmsg = 'all of aps can perform wlan[%s]' % wlan_conf['ssid']
        logging.info(passmsg)
        return {"PASS":passmsg}
                                        
def select_client_and_check(station, check_status_timeout = 100):
    # Find the target station object and remove all Wlan profiles        
    # Found the target station
    target_station = station

    logging.info("Remove all WLAN profiles on the target station %s" % target_station.get_ip_addr())
    target_station.remove_all_wlan()
    
#    target_station.removeAllWlan()

    logging.info("Make sure the target station %s disconnects from wireless network" % 
                 target_station.get_ip_addr())
    
    start_time = time.time()
    while True:
        if target_station.get_current_status() == "disconnected":
            break
        
        time.sleep(1)
        if time.time() - start_time > check_status_timeout:
            raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                            check_status_timeout)    
        
    if not target_station:
        raise Exception("Target station % s not found" % target_station)  
        
def go_through_ruckus_aps_wlan(zd, wlan_conf, cfg):
    ruckus_aps = cfg['ruckus_aps']
    for index in range(len(ruckus_aps)):
        ap_mac = ruckus_aps[index]['mac']
        bind_wlan_groups_to_ap(ap_mac, cfg)
        errmsg = verify_wlan_aps_beyond_bind_ap(ap_mac, wlan_conf, cfg)
        if errmsg and errmsg.has_key("ERROR"):
            return errmsg
        
        errmsg = assign_client_to_wlan(wlan_conf, cfg)
        
        if errmsg and errmsg.has_key("ERROR"):
            return errmsg
                
        zhlp.ap.default_wlan_groups_by_mac_addr(zd, ap_mac)
        
def verify_wlan_aps_beyond_bind_ap(ap_mac, wlan_conf, cfg):
    aps = cfg['aps']
    ap_username = cfg['ap_username']
    ap_password = cfg['ap_password']
    
    for index in range(len(aps)):
        active_ap = RuckusAP(dict(ip_addr=aps[index]['ip_addr'], username=ap_username, password=ap_password))        
        msg = tmethod.verify_wlan_on_aps(active_ap, wlan_conf['ssid'])
#            import pdb
#            pdb.set_trace()
        if ap_mac == aps[index]['mac'] and msg and msg != '':            
            return {"ERROR":msg}
        
        elif ap_mac != aps[index]['mac'] and not msg:            
            return {"ERROR":'AP[%s] should not been contained' % ap_mac}
        
    passmsg = 'All the wlans can perform successfully'        
    return {"PASS":passmsg}                               

def sanity_check_wlans(wlan_group, cfg):
    
        for wlan_conf in cfg['wlan_conf_list']:
            logging.info('[WLANsCheck]try to create WLAN[%s], WLANGroup[%s]' % (wlan_conf, wlan_group))
            create_wlan_and_wgs(cfg['zd'], wlan_conf, wlan_group)
            logging.info('[WLANsCheck]WLAN[%s], WLANGroup[%s] are created successfully' % (wlan_conf, wlan_group))
            
            logging.info('[WLANsCheck]try to verify status of WLAN[%s] against APs' % wlan_conf)                                    
            errmsg = go_through_aps_wlan(wlan_conf,cfg['aps'], cfg['ap_username'], cfg['ap_password'])
            if errmsg and errmsg.has_key("ERROR"):
                return errmsg
            
            logging.info('[WLANsCheck]try to verify status of WLAN[%s] against RuckusAPs and WirelessClient' % wlan_conf)
            errmsg = go_through_ruckus_aps_wlan(cfg['zd'], wlan_conf, cfg) 
            if errmsg and errmsg.has_key('ERROR'):
                return errmsg   
                    
            zhlp.wgs.remove_wlan_groups(cfg['zd'])
            zhlp.wlan.delete_all_wlans(cfg['zd'])
            
        return {"PASS":""}
                      
def create_wlan_and_wgs(zd, wlan_conf, wlan_group):
    zhlp.wlan.create_wlan(zd, wlan_conf)
    wlan_name = wlan_conf['ssid']
    zhlp.wgs.create_wlan_group(zd, wlan_group, wlan_name)
    zhlp.wgs.uncheck_default_wlan_member(zd, wlan_name)
        
def convert_models( models=['zf2942']):
    expectModels = []
    for index in range(len(models)):
        if models[index] and models[index].index('zf') == 0:
            expectModels.append(models[index].replace('zf', 'ss'))
            
    return expectModels 

def retrieve_models(models=['ss2942']):
    modelsStr = ""
    for model in models:
        if modelsStr == "":
            modelsStr = model
            
        else:
            modelsStr = modelsStr + " " + model
            
    return str(modelsStr)

def download_simage(conf):
    """
    download simulator image from lhotse
    """
    fname = imgres.download_build(conf['simap_build_stream'], conf['simap_bno'])
    img_filename = imgres.get_image(fname, filetype=".+\.Bl7$")
    expr = '^SIM-AP_([\d\.]+)\.Bl7$'
    res = re.match(expr, img_filename, re.I)
    
    if res:
        #bug in saigon
        v = res.group(1)
        conf['sim_version'] = v.replace("0", "9", 1)
#            self.package_simap_cfg['version'] = self.sim_version
    else:
        errmsg = 'Haven\'t catched simap image from version server.'
        return {"ERROR":errmsg}
        
    if conf['file_path']:
        imgres.mv_file(img_filename, conf['file_path'], tname="rcks_fw.bl7")
        
def download_zdimage(conf):
    """
    download zd3k image from lhotse
    """
    fname = imgres.download_build(conf['zd_build_stream'], conf['zd_bno'])
    img_filename = imgres.get_image(fname, filetype="^zd3k_(\d+.){5}ap_(\d+.){5}img$")
    
    img_filename = escape(os.path.realpath(img_filename))
    logging.info("zd image file[%s]" % img_filename)
    conf['img_file_path'] = img_filename  
        
def verify_simaps_from_vm(agent, expect_cnt, timeout=90):
    startT = time.time()
    while True:
        if time.time() - startT < timeout :
            cnt = agent.get_sim_ap_nums()
            if cnt != expect_cnt:
                logging.info('[%d] SimAPs have started, waiting for another[%d]' % (cnt, expect_cnt - cnt))
                time.sleep(5)
                
            else:
                
                return True
    return False   
    
def bootup_simaps(agent, models):
    simcfg = {   
            'ap_start_mac' : '00:13:92:03:02:00',
            'ap_cnt' : 1,
            'ap_mode':'zf9999',
           }   
    for index in range(len(models)):
        simcfg['ap_mode'] = models[index]
        macID = '00'
        macID = convert_hex(index + 1)
        simcfg['ap_start_mac'] = '00:13:92:03:02:%s' % macID
        simcfg['ap_cnt'] = 1
        simcfg['rogue'] = 0
        simcfg['tap_id'] = index + 1
        
        agent.touch_tcfg(simcfg)
        agent.startup_single_simap()       
        
def convert_hex(index):
    if index < 15 :
        return hex(index).replace('0x', '0').upper()
    
    elif index < 256 :
        return hex(index).replace('0x', '').upper()
    
    raise Exception('out of range [0,255]')     
    
def restart_zd_cli(zd):
    zdcli = ZoneDirectorCLI({'ipaddr':  zd.ip_addr,
                                  'username': zd.username,
                                  'password': zd.password,})
    return zdcli
       
def escape(file_path):
    expr = "[/|\\^\\\\]"
    return re.sub(expr, "\\\\", file_path) 

def usage():
    """
        Description:
            sanity check scaling in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
        Prerequisites:
          1) TFTP server is runing at your ENV,  
          image exist at TFTP server root folder
          2) All of SimAPs are running at your ENV and all of them are connected. 
        usage:
            tea.py <scaling_zd_restart key/value pair> ...
            
            where <scaling_zd_restart key/value pair> are:
              do_zd_upgrade      :     'Do zd upgrade action'
              zd_build_stream    :     'build stream of ZoneDirector'
              zd_bno             :     'build no of ZoneDirector'
              simap_build_stream :     'build stream of SIMAP'
              simap_bno          :     'build no of SIMAP'
              vm_ip_addr         :     'IP address of SIMAP Server'
              file_path          :     'The file path of tftp server respo.'
              target_station     :     'IP address of target station.'
            notes:
        Examples:                        
            tea.py scaling_sanity_check te_root=u.zd.scaling
    """
         
def main(**kwa):
    mycfg = {'do_zd_upgrade':False,
             'wlans':['psk-wpa-tkip',
                      'share-wep128',
                      'share-wep64',
                      'open-wep64',
                      'open-none',
                      'open-wep128',
                      'psk-wpa-aes',],
              'zd_build_stream':'',
              'zd_bno':'',
              'simap_build_stream':'SIM-AP_mainline',
              'simap_bno':'43',
              'vm_ip_addr':'172.18.35.150',
              'file_path':'d:\\',
              'tftpserver':'192.168.0.20',
              'timeout':'1200',
              'target_station':'192.168.1.21',                                         
             }
    
    mycfg.update(kwa)
    tcfg = do_config(mycfg)
    try:        
        res = do_test(tcfg)
        do_clean_up(tcfg)
    finally:
        if tcfg['zd']:
            tcfg['zd'].s.shut_down_selenium_server()
    
    return res