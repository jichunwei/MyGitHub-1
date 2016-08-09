import time

def set_device_name(mf_obj,name):
    mf_obj.navigate_to(mf_obj.CONFIG_DEVICE,-1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['device_name'],name)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_home_username(mf_obj,name):
    mf_obj.navigate_to(mf_obj.CONFIG_DEVICE,-1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['home_username'],name)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_home_password(mf_obj,password):
    mf_obj.navigate_to(mf_obj.CONFIG_DEVICE,-1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['password'],password)
    mf_obj.s.type_text(mf_obj.info['home_confirm'],password)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_sp_username(mf_obj,name):
    mf_obj.navigate_to(mf_obj.CONFIG_DEVICE,-1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['sp_username'],name)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_sp_password(mf_obj,password):
    mf_obj.navigate_to(mf_obj.CONFIG_DEVICE,-1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['sp_password'],password)
    mf_obj.s.type_text(mf_obj.info['sp_confirm'],password)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def submit(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def restore_settings(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['restore'])

def set_ntp(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.CONFIG_INTERNET, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['ntp'],ip)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_gateway(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.CONFIG_INTERNET, -1, timeout = 20)
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['gateway0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['gateway1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['gateway2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['gateway3'],splitip[3])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_prim_dns(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.CONFIG_INTERNET, -1, timeout = 20)
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['dns0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['dns1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['dns2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['dns3'],splitip[3])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_2nd_dns(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.CONFIG_INTERNET, -1, timeout = 20)
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['nd_dns0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['nd_dns1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['nd_dns2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['nd_dns3'],splitip[3])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_ip_dhcp(mf_obj):
    mf_obj.navigate_to(mf_obj.CONFIG_INTERNET, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['dhcp'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_ip_static(mf_obj,ip,wan=True,mask='255.255.255.0'):
    """
    True: set WAN ip on Internet page
    False: set LAN ip on System page ; one of the interface has to be in route mode first
    """
    if wan:
        mf_obj.navigate_to( mf_obj.CONFIG_INTERNET,-1, timeout = 20)
        mf_obj.s.click_if_not_checked(mf_obj.info['static'])
    elif not wan:
        mf_obj.navigate_to(mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['static0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['static1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['static2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['static3'],splitip[3])
    splitmask = mask.split('.')
    mf_obj.s.type_text(mf_obj.info['mask0'],splitmask[0])
    mf_obj.s.type_text(mf_obj.info['mask1'],splitmask[1])
    mf_obj.s.type_text(mf_obj.info['mask2'],splitmask[2])
    mf_obj.s.type_text(mf_obj.info['mask3'],splitmask[3])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_flag(mf_obj,flag ='auto'):
    """
    auto, broadcast or unicast
    """
    mf_obj.navigate_to( mf_obj.CONFIG_INTERNET,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['dhcp'])
    if flag =='unicast':
        mf_obj.s.click_if_not_checked(mf_obj.info['unicast'])
    elif flag =='broadcast':
        mf_obj.s.click_if_not_checked(mf_obj.info['broadcast'])
    else:
        mf_obj.s.click_if_not_checked(mf_obj.info['auto'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_eth_mode(mf_obj,mode):
    """bridge or route mode"""
    mf_obj.navigate_to( mf_obj.CONFIG_SYSTEM ,-1, timeout = 20)
    if mode=="bridge":
        mf_obj.s.click_if_not_checked(mf_obj.info['bridge_eth'])
    elif mode=="route":
        mf_obj.s.click_if_not_checked(mf_obj.info['route_eth'])
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wlan1_mode(mf_obj,mode):
    """bridge or route mode"""
    mf_obj.navigate_to( mf_obj.CONFIG_SYSTEM ,-1, timeout = 20)
    if mode=="bridge":
        mf_obj.s.click_if_not_checked(mf_obj.info['bridge_wlan1'])
    elif mode=="route":
        mf_obj.s.click_if_not_checked(mf_obj.info['route_wlan1'])
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wlan2_mode(mf_obj,mode):
    """bridge or route mode"""
    mf_obj.navigate_to(mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    if mode=="bridge":
        mf_obj.s.click_if_not_checked(mf_obj.info['bridge_wlan2'])
    elif mode=="route":
        mf_obj.s.click_if_not_checked(mf_obj.info['route_wlan2'])
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wds_en(mf_obj):
    mf_obj.navigate_to( mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['wds_en'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wds_dis(mf_obj):
    mf_obj.navigate_to( mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['wds_dis'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_dhcp_server_en(mf_obj,start_ip,users = 249):
    """
    ip is in string format; 
    make sure one of the interfaces enables router mode
    """
    mf_obj.navigate_to(mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['dhcp_server_en'])
    splitip = start_ip.split('.')
    mf_obj.s.type_text(mf_obj.info['start0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['start1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['start2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['start3'],splitip[3])
    if (users >0 and users < 250):
        mf_obj.s.type_text(mf_obj.info['max_users'],users)
    else:
        raise Exception('Invalid number of clients')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_dhcp_server_dis(mf_obj):    
    """
    make sure one of the interfaces enables router mode
    """
    mf_obj.navigate_to( mf_obj.CONFIG_SYSTEM,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['dhcp_server_dis'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wireless_mode(mf_obj,value='bgn'):
    """ bg, bgn, b, g"""
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS,mf_obj.CONFIG_COMMON, timeout = 20)
    
    if (value=='bg'):
        mf_obj.s.select_value(mf_obj.info['WLANCommon_WModeCb'], '11b/g')
    elif(value=='bgn'):
        mf_obj.s.select_value(mf_obj.info['WLANCommon_WModeCb'], '11b/g/n')
    elif(value=='b'):
        mf_obj.s.select_value(mf_obj.info['WLANCommon_WModeCb'], '11b')
    elif(value=='g'):
        mf_obj.s.select_value(mf_obj.info['WLANCommon_WModeCb'], '11g')
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_country(mf_obj,name):
    """need to know the exact country code
    make sure the countrycode-fixed is set to NO on CPE"""

    mf_obj.navigate_to( mf_obj.CONFIG_WIRELESS,mf_obj.CONFIG_COMMON, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANCommon_CountryCodeCb'], name)
    if mf_obj.s.is_confirmation_present(3):
        mf_obj.s.get_confirmation()
    mf_obj.s.choose_ok_on_next_confirmation()
    time.sleep(3)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    

def set_antenna(mf_obj,mode='both'):
    """both, internal or external"""
    mf_obj.navigate_to( mf_obj.CONFIG_WIRELESS,mf_obj.CONFIG_COMMON, timeout = 20)
    if mode == 'internal':
        mf_obj.s.click_if_not_checked(mf_obj.info['internal'])
    elif mode == 'external':
        mf_obj.s.click_if_not_checked(mf_obj.info['external'])
    elif mode == 'both':
        mf_obj.s.click_if_not_checked(mf_obj.info['both'])
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_txpower(mf_obj,level=0):
    """ 0=full,1=half,2=fourth,3=eighth,4=min"""
    mf_obj.navigate_to( mf_obj.CONFIG_WIRELESS,mf_obj.CONFIG_COMMON, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['WLANCommon_EditCommonBtn'])
    if mf_obj.s.is_confirmation_present(3):
        mf_obj.s.get_confirmation()
    mf_obj.s.choose_ok_on_next_confirmation()
    if (level==0 or level==1 or level==2 or level==3 or level==4):
        mf_obj.s.select_value(mf_obj.info['WLANCommon_TxPowerCb'], level)
    else:
        raise Exception('Unregcognized txpower')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    time.sleep(8)
    mf_obj.s.safe_click(mf_obj.info['go_back'])#cpe will reconnect and request dhcp again
  

def set_protection_mode(mf_obj,mode='disable'):
    """
    disable, cts or both
    both: cts_rts
    """
    mf_obj.navigate_to( mf_obj.CONFIG_WIRELESS,mf_obj.CONFIG_COMMON, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['WLANCommon_EditCommonBtn'])
    if mf_obj.s.is_confirmation_present(3):
        mf_obj.s.get_confirmation()
    mf_obj.s.choose_ok_on_next_confirmation()
    if(mode == 'disable'):
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANCommon_ProtModeDisabledRd'])
    elif(mode == 'cts'):
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANCommon_ProtModeCTSRd'])
    elif(mode == 'both'):
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANCommon_ProtModeRTSCTSRd'])
    else:
        raise Exception('Unregcognized mode')
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    time.sleep(8)
    mf_obj.s.safe_click(mf_obj.info['go_back'])#cpe will reconnect and request dhcp again


def set_threshold(mf_obj,iface,range=2346):
    """
    iface = wan, wlan1 or wlan2
    rang = 255 - 2347
    """
    if iface == 'wan':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    elif iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['WLANDet_EditThresBtn'])
    if mf_obj.s.is_confirmation_present(3):
        mf_obj.s.get_confirmation()
    mf_obj.s.choose_ok_on_next_confirmation()
    
    if (range > 255 and range < 2347):
        mf_obj.s.type_text(mf_obj.info['WLANDet_WRTSCTSTxt'],range)
        time.sleep(3)
        mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    else:
        raise Exception('Out of range')
    time.sleep(8)
    mf_obj.s.safe_click(mf_obj.info['go_back'])#cpe will reconnect and request dhcp again

def set_dtim(mf_obj,iface,rate=1):
    """
    iface = wlan1 or wlan2
    """
    if iface=='wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface=='wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    
    mf_obj.s.safe_click(mf_obj.info['WLANDet_EditThresBtn'])
    if mf_obj.s.is_confirmation_present(3):
        mf_obj.s.get_confirmation()
    mf_obj.s.choose_ok_on_next_confirmation()
    
    if (rate > 0 and rate < 226):
        mf_obj.s.type_text(mf_obj.info['WLANDet_WDTIMTxt'],rate)
        mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    else:
        raise Exception('Out of range')
    time.sleep(8)
    mf_obj.s.safe_click(mf_obj.info['go_back'])#cpe will reconnect and request dhcp again
                       
                       
def set_ssid(mf_obj,ssid,iface):
    """iface = wan, wlan1 or wlan2"""
    if iface == 'wan':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    elif iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['WLANDet_WSSIDTxt'],ssid)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_preferred_ap(mf_obj,bssid):
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['bssid'],bssid)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_locked_dis(mf_obj):
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['preferred'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_locked_en(mf_obj):
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['locked'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def last_survey(mf_obj):
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['survey'])
    time.sleep(8)
    content = []
    content.append(mf_obj.s.get_htable_content(mf_obj.info['survey_tbl']))
    mf_obj.s.safe_click(mf_obj.info['go_back'])
    return content

def set_survey_ssid(mf_obj,ssid,bssid=''):
    """
    search by bssid : set ssid = ''
    search by ssid : set bssid = ''
    can also search by both bssid and ssid
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['rescan'])
    time.sleep(10)
    if bssid=='':
        link = "//a[contains(.,'%s')]" %(ssid)
    elif ssid =='':
        link = "//a[contains(.,'%s')]" %(bssid)
    else:
        link = "//a[contains(@href,'/cWireless.asp?subp=apcli0&ssid=%s&bssid=%s')]" %(ssid,bssid)
        print link
    mf_obj.s.safe_click(link)
    time.sleep(6)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_rescan(mf_obj):
    """return the scanned table"""
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['rescan'])
    time.sleep(8)
    content = []
    content.append(mf_obj.s.get_htable_content(mf_obj.info['survey_tbl']))
    mf_obj.s.safe_click(mf_obj.info['go_back'])
    return content


def set_encryption_open(mf_obj,iface):
    """iface = wan, wlan1 or wlan2"""
    if iface == 'wan':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    elif iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'], 0)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_encryption_wep(mf_obj,iface,key,**kwarg):
    """
    iface = wan, wlan1 or wlan2
    kwarg : auth='auto','open','shared'; type='hex'or'text'; bit=64 or 128,index=1,generate=False,phrase=''
    """
    if iface == 'wan':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    elif iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)

    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'],'wep')
    param = {}
    param = {'auth'   :'auto',
             'bit'    : 64,
             'type'   : 'hex',
             'index'  : 1,
             'generate' : False,
             'phrase' : ''
             }
    param.update(kwarg)
    if param['auth'] =='open':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WOpenRd'])
    elif param['auth'] =='shared':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WSharedKeyRd'])
    elif param['auth'] =='auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAutoRd'])
    else:
         raise Exception('Unregcognized auth mode')

    if param['bit'] == 64:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptLenCb'],5)
    elif param['bit'] == 128:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptLenCb'],13)
    else:
        raise Exception('Unregcognized key length')

    if param['type'] == 'hex':#10 and 26 characters
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WKeyEntryHexaRd'])
    elif param['type'] == 'text':#5 and 13 characters
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WKeyEntryAsciiRd'])
    else:
        raise Exception('Unregcognized key type')

    if param['index'] == 1:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],1)
    elif param['index'] == 2:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],2)
    elif param['index'] == 3:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],3)
    elif param['index'] == 4:
        mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],4)
    else:
        raise Exception('Unregcognized key index')

    if param['generate'] == False:
        mf_obj.s.type_text(mf_obj.info['WLANDet_WWEPKeyTxt'],key)
    elif param['generate'] == True:
        mf_obj.s.type_text(mf_obj.info['WLANDet_WWEPPassphraseTxt'],param['phrase'])
        mf_obj.s.safe_click(mf_obj.info['WLANDet_WGenPassphraseBtn'])
        if mf_obj.s.is_confirmation_present(5):
            mf_obj.s.get_confirmation()
        mf_obj.s.choose_ok_on_next_confirmation()
    else:
        raise Exception('Cannot generate key')
    time.sleep(3)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_encryption_psk(mf_obj,iface,passphrase,**kwarg):
    """
    iface = wan, wlan1 or wlan2
    kwarg : wpa='auto','wpa','wpa2'; cipher='auto','tkip' or 'aes'
    """
    if iface == 'wan':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    elif iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'], 'wpa')
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAuthPSKRd'])
    param = {}
    param = {'wpa'    : 'auto',
             'cipher' : 'auto',
             }
    param.update(kwarg)

    if param['wpa'] == 'wpa':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer1Rd'])
    elif param['wpa'] == 'wpa2':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer2Rd'])
    elif param['wpa'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVerAutoRd'])
    else:
        raise Exception('Unregcognized wpa version')

    if param['cipher']== 'tkip':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPATKIPRd'])
    elif param['cipher'] == 'aes':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAESRd'])
    elif param['cipher'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAutoRd'])
    else:
        raise Exception('Unregcognized cipher')

    mf_obj.s.type_text(mf_obj.info['WLANDet_WPSKPassphraseTxt'],passphrase)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_encryption_1x_client(mf_obj,user,password,**kwarg):
    """
    kwarg : wpa='auto','wpa','wpa2'; cipher='auto','tkip' or 'aes';
            identity='anonymous'; protocol='mschapv2','mschap','chap','pap'
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'], 'wpa')
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAuth802.1xRd'])
    param = {}
    param = {'wpa'      :'auto',
             'cipher'   :'auto',
             'protocol' : 'mschapv2',
             'identity' : 'anonymous',
             }
    param.update(kwarg)
    if param['wpa'] == 'wpa':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer1Rd'])
    elif param['wpa']== 'wpa2':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer2Rd'])
    elif param['wpa'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVerAutoRd'])
    else:
        raise Exception('Unregcognized wpa version')

    if param['cipher'] == 'tkip':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPATKIPRd'])
    elif param['cipher'] == 'aes':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAESRd'])
    elif param['cipher'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAutoRd'])
    else:
        raise Exception('Unregcognized cipher')

    if param['protocol'] == 'mschapv2':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'MSCHAPV2')
    elif param['protocol'] == 'mschap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'MSCHAP')
    elif param['protocol'] == 'chap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'CHAP')
    elif param['protocol'] == 'pap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'PAP')
    else:
        raise Exception('Unregcognized inner authentication')
    mf_obj.s.type_text(mf_obj.info['identity'],param['identity'])
    mf_obj.s.type_text(mf_obj.info['eap_username'],user)
    mf_obj.s.type_text(mf_obj.info['eap_password'],password)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_encryption_1x_server(mf_obj,iface,server,secret,**kwarg):
    """
    iface = wlan1 or wlan2
    kwarg : wpa='auto','wpa','wpa2'; cipher='auto','tkip' or 'aes';
            nas='cpe'; port=1812;
    """
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'], 'wpa')
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAuth802.1xRd'])
    param = {}
    param = {'wpa'   :'auto',
             'cipher': 'auto',
             'nas'   : 'cpe',
             'port'  : 1812,
             }
    param.update(kwarg)
    if param['wpa'] == 'wpa':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer1Rd'])
    elif param['wpa'] == 'wpa2':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer2Rd'])
    elif param['wpa'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVerAutoRd'])
    else:
        raise Exception('Unregcognized wpa version')

    if param['cipher'] == 'tkip':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPATKIPRd'])
    elif param['cipher'] == 'aes':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAESRd'])
    elif param['cipher'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAutoRd'])
    else:
        raise Exception('Unregcognized cipher')

    mf_obj.s.type_text(mf_obj.info['WLANDet_WRadiusTxt'],param['nas'])
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthPortTxt'],param['port'])
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthSecretTxt'],secret)
    splitip = server.split('.')
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthIP1Txt'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthIP2Txt'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthIP3Txt'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['WLANDet_WAuthIP4Txt'],splitip[3])

    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_encryption_wpa_auto(mf_obj,psk,user,password,**kwarg):
    """
    802.1x and WPA-PSK configuration at the same time
    kwarg : wpa='auto','wpa','wpa2'; cipher='auto','tkip' or 'aes';
            identity='anonymous'; protocol='mschapv2','mschap','chap','pap'
            nas='cpe'; port=1812; secret='mysecret'
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WAN, timeout = 20)
    mf_obj.s.select_value(mf_obj.info['WLANDet_WEncryptCb'], 'wpa')
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAuthAutoRd'])
    param = {}
    param = {'wpa'      :'auto',
             'cipher'   : 'auto',
             'protocol' : 'mschapv2',
             'identity' : 'anonymous',
             }
    param.update(kwarg)
    if param['wpa']== 'wpa':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer1Rd'])
    elif param['wpa'] == 'wpa2':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVer2Rd'])
    elif param['wpa'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAVerAutoRd'])
    else:
        raise Exception('Unregcognized wpa version')

    if param['cipher'] == 'tkip':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPATKIPRd'])
    elif param['cipher'] == 'aes':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAESRd'])
    elif param['cipher'] == 'auto':
        mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WWPAAutoRd'])
    else:
        raise Exception('Unregcognized cipher')

    if param['protocol'] == 'mschapv2':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'MSCHAPV2')
    elif param['protocol'] == 'mschap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'MSCHAP')
    elif param['protocol'] == 'chap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'CHAP')
    elif param['protocol'] == 'pap':
        mf_obj.s.select_value(mf_obj.info['inner_auth'],'PAP')
    else:
        raise Exception('Unregcognized inner authentication')
    mf_obj.s.type_text(mf_obj.info['identity'],param['identity'])
    mf_obj.s.type_text(mf_obj.info['eap_username'],user)
    mf_obj.s.type_text(mf_obj.info['eap_password'],password)
    mf_obj.s.type_text(mf_obj.info['WLANDet_WPSKPassphraseTxt'],psk)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_wireless_state_en(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAvailERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wireless_state_dis(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WAvailDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_broadcast_en(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WBroadcastERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_broadcast_dis(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['WLANDet_WBroadcastDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_isolation_en(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['isolation_en'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_isolation_dis(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface == 'wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_1, timeout = 20)
    elif iface == 'wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_WIRELESS, mf_obj.CONFIG_WLAN_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['isolation_dis'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_acl_dis(mf_obj,iface):
    """iface = wlan1 or wlan2"""
    if iface=='wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_1, timeout = 20)
    elif iface=='wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_2, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['acl_dis'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


#def set_acl_allow(mf_obj):
 #   mf_obj.s.check_if_not_checked(mf_obj.info['acl_allow'])

#def set_acl_deny(mf_obj):
 #   mf_obj.s.check_if_not_checked(mf_obj.info['acl_deny'])


def set_acl_add(mf_obj,mac,idx,iface,allow=True):
    """
    iface = wlan1 or wlan2
    idx : start with 0, add 1 for every entry added
    """
    if iface=='wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_1, timeout = 20)
    elif iface=='wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_2, timeout = 20)
    if allow:
        mf_obj.s.click_if_not_checked(mf_obj.info['acl_allow'])
    elif not allow:
        mf_obj.s.click_if_not_checked(mf_obj.info['acl_deny'])

    splitmac = mac.split(':')
    if(mf_obj.s.is_element_present(mf_obj.info['add'])):
        mf_obj.s.safe_click(mf_obj.info['add'])
        time.sleep(1)
        for i in range (0,6):
            mf_obj.s.type_text("//input[@id='macaddress_%s_%s']" %(i,idx),splitmac[i])
    #mf_obj.s.type_text("//input[@id='macaddress_0_%s']" %idx,splitmac[0])
    #mf_obj.s.type_text("//input[@id='macaddress_1_%s']" %idx,splitmac[1])
    #mf_obj.s.type_text("//input[@id='macaddress_2_%s']" %idx,splitmac[2])
    #mf_obj.s.type_text("//input[@id='macaddress_3_%s']" %idx,splitmac[3])
    #mf_obj.s.type_text("//input[@id='macaddress_4_%s']" %idx,splitmac[4])
    #mf_obj.s.type_text("//input[@id='macaddress_5_%s']" %idx,splitmac[5])
        mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_acl_delete(mf_obj,idx,iface,allow=True):
    """
    iface = wlan1 or wlan2
    idx : exact index of the entry when added
    """
    if iface=='wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_1, timeout = 20)
    elif iface=='wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_2, timeout = 20)
    if allow:
        mf_obj.s.click_if_not_checked(mf_obj.info['acl_allow'])
    elif not allow:
        mf_obj.s.click_if_not_checked(mf_obj.info['acl_deny'])

    if(mf_obj.s.is_element_present("//input[@id='abr_remove_%s']" %idx)):
        mf_obj.s.click_if_not_checked("//input[@id='abr_remove_%s']" %idx)
        mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])


def set_acl_cancel(mf_obj):
    "navigate to correct menu"
    if(mf_obj.s.is_element_present(mf_obj.info['cancel'])):
        mf_obj.s.safe_click(mf_obj.info['cancel'])


def show_acl_local_mac(mf_obj,iface): #WHAT DOES IT DO?
    """iface = wlan1 or wlan2"""
    if iface=='wlan1':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_1, timeout = 20)
    elif iface=='wlan2':
        mf_obj.navigate_to(mf_obj.CONFIG_ACCESS_CONTROLS, mf_obj.CONFIG_ACL_2, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['show_mac'])

def set_port_forward_en (mf_obj, name, startp, endp, protocol, srv_ip, srv_p, idx):
    mf_obj.navigate_to(mf_obj.CONFIG_PORT_FWD,-1)
    mf_obj.s.safe_click(mf_obj.info['add_acl'])
    mf_obj.s.type_text("//input[@name='rulename-%s']" %idx, name)
    mf_obj.s.type_text("//input[@name='port-start-%s']" %idx, startp)
    mf_obj.s.type_text("//input[@name='port-end-%s']" %idx,endp)
    mf_obj.s.select_value("//select[@id='protocol-%s']" %idx,protocol)
    mf_obj.s.type_text("//input[@name='ipaddress-%s']" %idx,srv_ip)
    mf_obj.s.type_text("//input[@name='targetport-%s']" %idx,srv_p)
    mf_obj.s.click_if_not_checked("//input[@id='enable-%s']" %idx)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_port_forward_dis(mf_obj, idx):
    mf_obj.navigate_to(mf_obj.CONFIG_PORT_FWD,-1)
    mf_obj.s.click_if_not_checked("//input[@id='disable-%s']" %idx)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_port_forward_del(mf_obj, idx):
    mf_obj.navigate_to(mf_obj.CONFIG_PORT_FWD,-1)
    mf_obj.s.click_if_not_checked("//input[@id='delete-%s']" %idx)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def set_wizard_open_wan(mf_obj,mode,ssid_wan,ssid_lan='',encryption_lan='open',idx_lan = 1,pwd_lan=''):
    """
    open-system on the WAN side, plus config encryption on lan sides
    mode='bridge' or 'route', encryption_lan='open','wep' or 'psk
    ssid_lan is mandatory in route mode
    pwd_lan is mandatory if configure wep or psk on the wireless LAN
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIZARD, -1, timeout = 20)
    if mode == 'bridge':
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_bridge'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='Open']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        mf_obj.s.safe_click(mf_obj.info['next']) #reboot
    elif (mode == 'route' , ssid_lan != ''):
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_route'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='Open']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        #configure wireless lan
        mf_obj.s.type_text(mf_obj.info['wizard_ssid'],ssid_lan)
        if encryption_lan=='open':
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_open'])
        elif (encryption_lan=='wep' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wep'])
            mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],idx_lan)
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        elif (encryption_lan=='psk' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wpa'])
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        else:
            raise Exception ('Encryption not supported')
        mf_obj.s.safe_click(mf_obj.info['next'])#finish
        time.sleep(6)
        mf_obj.s.safe_click(mf_obj.info['next']) #reboot
    else:
        raise Exception ('Missing or wrong arguments')


def set_wizard_wep_wan(mf_obj,mode,ssid_wan,pwd_wan,idx_wan=1,ssid_lan='',encryption_lan='open',idx_lan=1,pwd_lan=''):
    """
    WEP on the WAN side, plus config encryption on lan sides
    mode='bridge' or 'route', encryption_lan='open','wep' or 'psk
    ssid_lan is mandatory in route mode
    pwd_lan is mandatory if configure wep or psk on the wireless LAN
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIZARD, -1, timeout = 20)
    if mode == 'bridge':
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_bridge'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WEP']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WEP selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        key_index = "//select[@name='defkeyidx_%s']"%value
        mf_obj.s.select_value(key_index,idx_wan)
        passwd = "//input[@name='password_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot
    elif (mode == 'route' and ssid_lan != ''):
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_route'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WEP']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WEP selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        key_index = "//select[@name='defkeyidx_%s']"%value
        mf_obj.s.select_value(key_index,idx_wan)
        passwd = "//input[@name='password_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        #config wireless lan
        mf_obj.s.type_text(mf_obj.info['wizard_ssid'],ssid_lan)
        if encryption_lan=='open':
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_open'])
        elif (encryption_lan=='wep' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wep'])
            mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],idx_lan)
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        elif (encryption_lan=='psk' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wpa'])
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        else:
            raise Exception ('Encryption not supported')
        mf_obj.s.safe_click(mf_obj.info['next'])#finished
        time.sleep(6)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot
    else:
        raise Exception ('Missing or wrong arguments')


def set_wizard_psk_wan(mf_obj,mode,ssid_wan,pwd_wan,ssid_lan='',encryption_lan='open',idx_lan=1,pwd_lan=''):
    """
    PSK on the WAN side, plus config encryption on lan sides
    mode='bridge' or 'route', encryption_lan='open','wep' or 'psk
    ssid_lan is mandatory in route mode
    pwd_lan is mandatory if configure wep or psk on the wireless LAN
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIZARD, -1, timeout = 20)
    if mode == 'bridge':
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_bridge'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WPAPSK']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WPAPSK selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        passwd = "//input[@name='psk_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot
    elif (mode == 'route' and ssid_lan != ''):
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_route'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WPAPSK']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WPAPSK selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        passwd = "//input[@name='psk_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        #config wireless lan
        mf_obj.s.type_text(mf_obj.info['wizard_ssid'],ssid_lan)
        if encryption_lan=='open':
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_open'])
        elif (encryption_lan=='wep' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wep'])
            mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],idx_lan)
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        elif (encryption_lan=='psk' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wpa'])
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        else:
            raise Exception ('Encryption not supported')
        mf_obj.s.safe_click(mf_obj.info['next'])#finish button
        time.sleep(6)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot button
    else:
        raise Exception ('Missing or wrong arguments')


def set_wizard_1x_wan(mf_obj,mode,ssid_wan,usr,pwd_wan,eap='MSCHAPV2',id='anonymous',ssid_lan='',encryption_lan='open',idx_lan=1,pwd_lan=''):
    """
    .1x on the WAN side, plus config encryption on lan sides
    mode='bridge' or 'route', eap = 'PAP','CHAP','MSCHAP','MSCHAPV2'
    encryption_lan='open','wep' or 'psk'
    ssid_lan is mandatory in route mode
    pwd_lan is mandatory if configure wep or psk on the wireless LAN
    """
    mf_obj.navigate_to(mf_obj.CONFIG_WIZARD, -1, timeout = 20)
    if mode == 'bridge':
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_bridge'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WPA']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WPA selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        eap_mode = "//select[@id='eapprot_%s']"%value
        mf_obj.s.select_value(eap_mode,eap)
        identity = "//input[@name='ident_%s']"%value
        mf_obj.s.type_text(identity,id)
        name = "//input[@name='uname_%s']"%value
        mf_obj.s.type_text(name,usr)
        passwd = "//input[@name='password_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(6)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot
    elif (mode == 'route' and ssid_lan != ''):
        mf_obj.s.click_if_not_checked(mf_obj.info['wizard_route'])
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(8)
        ssid_scan = "//li[@class='WPA']//label[contains(text(),'%s')]" %ssid_wan
        time.sleep(2)
        mf_obj.s.click_and_wait(ssid_scan,2)
        select = "//li[@class='WPA selected']//input[@type='radio']"
        value = mf_obj.s.get_attr(select,'value')
        eap_mode = "//select[@id='eapprot_%s']"%value
        mf_obj.s.select_value(eap_mode,eap)
        identity = "//input[@name='ident_%s']"%value
        mf_obj.s.type_text(identity,id)
        name = "//input[@name='uname_%s']"%value
        mf_obj.s.type_text(name,usr)
        passwd = "//input[@name='password_%s']"%value
        mf_obj.s.type_text(passwd, pwd_wan)
        mf_obj.s.safe_click(mf_obj.info['next'])
        time.sleep(4)
        #config wireless lan
        mf_obj.s.type_text(mf_obj.info['wizard_ssid'],ssid_lan)
        if encryption_lan=='open':
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_open'])
        elif (encryption_lan=='wep' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wep'])
            mf_obj.s.select_value(mf_obj.info['WLANDet_WKeyIndexCb'],idx_lan)
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        elif (encryption_lan=='psk' and pwd_lan!=''):
            mf_obj.s.click_if_not_checked(mf_obj.info['wizard_wpa'])
            mf_obj.s.type_text(mf_obj.info['password'],pwd_lan)
        else:
            raise Exception ('Encryption not supported')
        mf_obj.s.safe_click(mf_obj.info['next'])#finish
        time.sleep(8)
        mf_obj.s.safe_click(mf_obj.info['next'])#reboot
    else:
        raise Exception ('Missing or wrong arguments')











