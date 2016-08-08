'''
Authentication/Accounting Servers table headers:
['name',
 'type']
'''

import logging
import time
import copy
from RuckusAutoTest.common import utils
from RuckusAutoTest.components.lib.zd import widgets_zd

#for tacacs plus server test
from RuckusAutoTest.components.lib.zd.guest_access_zd import get_server_list_can_be_selected
from RuckusAutoTest.components.lib.zd.wlan_zd import get_server_list_when_creat_web_auth_wlan,get_zeroit_auth_server_list
from RuckusAutoTest.components.lib.zd.hotspot_services_zd import get_hot_spot_auth_server_list

def verify_server_only_for_admin_auth(zd,server_list):
    list_g=get_server_list_can_be_selected(zd)
    logging.info('guest:%s'%list_g)
    list_w=get_server_list_when_creat_web_auth_wlan(zd)
    logging.info('wlan:%s'%list_w)
    list_z=get_zeroit_auth_server_list(zd)
    logging.info('zeroit:%s'%list_z)
    list_h=get_hot_spot_auth_server_list(zd)
    logging.info('hotspot:%s'%list_h)
    msg = ''
    for server in server_list:
        if server in list_g:
            msg+='server [%s] can be find in guest pass generation suth server,'%server
            logging.error(msg)
        if server in list_w:
            msg+='server [%s] can be find in wlan web auth server list,'%server
            logging.error(msg)
        if server in list_z:
            msg+='server [%s] can be find in zeroit server list,'%server
            logging.error(msg)
        if server in list_h:
            msg+='server [%s] can be find in hot spot server list suth server,'%server
            logging.error(msg)
    
    return msg


#-----------------------------------------------------------------------------
# ACCESS METHODS - Authentication/Accounting Servers
#-----------------------------------------------------------------------------
def create_server(zd, **kwargs):
    """
    Create an authentication/accounting server
    @param:
        zd: the reference to the Zone Director object
    @param:
        kwargs: keyword argument list
    """
    return _create_server(zd, **kwargs)


def create_server_2(zd, cfg, is_nav = True):
    """
    a simplified version of create_server
    . cfg: confiuration to create an aaa server
    . is_nav: This param is added to support config aaa_servers page on ZD
             template from FM. If is_nav = True, don't do navigate.
    """
    _cfg = copy.deepcopy(cfg)
    _cfg['is_nav'] = is_nav

    return _create_server(zd, **_cfg)


def edit_server(zd, name, new_cfg):
    '''
    '''
    _nav_to(zd)

    return _edit_server(zd, name, new_cfg)

#add by west.li
#del a server according to the name
def del_server(zd, name):
    '''
    '''
    _nav_to(zd)

    return _del_server(zd, name)

def get_auth_server_info(zd):
    '''
    return a dictionary {'name':'auth_type'}
    {
     'tacacs_plus':'TACPLUS Authenticating',
     'aa1':'RADIUS'
    }
    '''
    res={}
    server_list=get_auth_server_info_list(zd)
    for server in server_list:
        res[str(server['name'])]=str(server['type'])
    return res
    

def get_auth_server_info_list(zd, is_nav = True):
    '''
    '''
    return _get_auth_server_info_list(zd, is_nav)


def remove_all_servers(zd):
    '''
    '''
    return _remove_all_servers(zd, 2)


def get_server_cfg_list_by_names(zd, server_name_list, is_nav = True):
    if is_nav:
        _nav_to(zd)

    cfg_list = []
    for server_name in server_name_list:
        cfg = _get_server_cfg_by_name(zd, server_name)
        cfg_list.append(cfg)

    return cfg_list


def get_all_server_name_list(zd, is_nav = True):
    '''
    Output:
        a list of all aaa servers' name.
    '''
    if is_nav:
        _nav_to(zd)

    server_name_list = []
    server_info_list = get_auth_server_info_list(zd, is_nav = False)
    for i in range(len(server_info_list)):
        server_name = server_info_list[i]['name']
        server_name_list.append(server_name)

    return server_name_list


def get_all_server_cfg_list(zd, is_nav = True):
    '''
    Output:
        a list of all servers' cfg.
    '''
    if is_nav:
        _nav_to(zd)

    server_name_list = get_all_server_name_list(zd, is_nav = False)
    cfg_list = get_server_cfg_list_by_names(zd, server_name_list, is_nav = False)

    return cfg_list

def test_authentication_settings(zd,server,user,password,server_type='tacacs_plus',expected_result='success'):
    result_mapping={
                    'tacacs_plus':{'success':'Success! The user will be authenticated by "tacplus".',
                                   'fail':'Failed! Invalid username or password.',
                                   'unreachable':'Failed! Unable to connect.'},
                    
                    }
    expected_result=result_mapping[server_type][expected_result]
    _nav_to(zd)
    zd.s.select_option(locs['test_select_server'],server)
    zd.s.type_text(locs['test_user_name'],user)
    zd.s.type_text(locs['test_password'],password)
    zd.s.click_and_wait(locs['test_button'])
    timeout = 60
    result_got = False
    t0 = time.time()
    while not result_got:
        if time.time() - t0>timeout:
            logging.error('no test result got after %s seconds'%timeout)
            break
        result=str(zd.s.get_text(locs['test_result']))
        if result:
            logging.info('result [%s] get'%result)
            break
    
    if result==expected_result:
        return True
    else:
        logging.error("test result (%s) is not the same with expected (%s)"%(result,expected_result))
        return False

def verify_server_cfg_by_name(zd, server_name, cfg):
    _nav_to(zd)
    cfg_get=_get_server_cfg_by_name(zd, server_name)
    logging.info('configuration got:%s'%cfg_get)
    errmsg=''
    for key in cfg:
        if not key in cfg_get:
            logging.info('key %s not get in wlan cfg'%key)
        elif str(cfg[key])!=str(cfg_get[key]):
            errmsg+='info %s get(%s) not the same as expected(%s)'%(key,cfg_get[key],cfg[key])
    return errmsg
def verify_server_cfg_gui_set_get(set_server_cfg_list, get_server_cfg_list):
    '''
    Verify server cfg between gui set and get.
    Set:
    [{'cfg_name': 'AD without Global Catalog',
      'global_catalog': False,
      'server_addr': '2020:db8:1::249',
      'server_name': 'ad_server_1',
      'server_port': '389',
      'type': 'ad',
      'win_domain_name': 'domain.ruckuswireless.com'}]
    Get:
    [{'global_catalog': False,
      'server_addr': u'2020:db8:1::249',
      'server_name': u'ad_server_1',
      'server_port': u'389',
      'type': 'ad',
      'win_domain_name': u'domain.ruckuswireless.com'}]
    '''
    if type(set_server_cfg_list) != list:
        set_server_cfg_list = [set_server_cfg_list]
    if type(get_server_cfg_list) != list:
        get_server_cfg_list = [get_server_cfg_list]
        
    err_dict = {}
    if len(set_server_cfg_list) != len(get_server_cfg_list):
        err_dict['Count'] = "GUI set:%s, GUI get:%s" % (len(set_server_cfg_list), len(get_server_cfg_list))
    else:
        set_servers_dict = _convert_list_to_dict(set_server_cfg_list)
        get_servers_dict = _convert_list_to_dict(get_server_cfg_list)
        
        logging.debug("GUI set: %s" % set_servers_dict)
        logging.debug("GUI get: %s" % get_servers_dict)
        
        for server_name, set_server_cfg in set_servers_dict.items():
            get_server_cfg = get_servers_dict[server_name]
            res = _compare_server_cfg_gui_set_get(set_server_cfg, get_server_cfg)
            if res:
                err_dict[server_name] = res
                    
    return err_dict

def _compare_server_cfg_gui_set_get(set_server_cfg, get_server_cfg):
    gui_set_get_keys_mapping = {'ldap_admin_dn': 'admin_domain_name',
                                'ldap_admin_pwd': 'admin_password',
                                'ldap_search_base': 'win_domain_name',
                                'secondary_server_addr': 'backup_server_addr',
                                'secondary_server_port': 'backup_server_port',
                                'failover_retries': 'retry_count',
                                'primary_reconnect': 'retry_interval',
                                'primary_timeout': 'request_timeout',
                                }
    
    item_pop_from_set_cfg = ['admin_password', 'cfg_name', 'new_server_name', 
                             'radius_auth_secret', 'secondary_radius_auth_secret', 
                             'radius_acct_secret', 'secondary_acct_secret']
    
    new_set_server_cfg = {}
    new_set_server_cfg.update(set_server_cfg)
    
    for key, get_key in gui_set_get_keys_mapping.items():
        if new_set_server_cfg.has_key(key):
            new_set_server_cfg[get_key] = new_set_server_cfg.pop(key)
            
    for key in item_pop_from_set_cfg:
        if new_set_server_cfg.has_key(key):
            new_set_server_cfg.pop(key)
            
    err_dict = utils.compare_dict_key_value(new_set_server_cfg, get_server_cfg)
                                
    return err_dict
    
def _convert_list_to_dict(server_cfg_list):
    '''
    Convert server cfg list to dict, key is server name.
    '''
    servers_cfg_dict = {}
    
    for server_cfg in server_cfg_list:
        servers_cfg_dict[server_cfg['server_name']] = server_cfg
    
    return servers_cfg_dict


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locs = dict(
    aaa_tbl_loc = "//table[@id='%s']",
    aaa_tbl_nav_loc = "//table[@id='%s']/tfoot",
    aaa_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
    aaa_edit_btn = "//td[@class='action']/span[contains(@id,'edit-authsvr')]",
    aaa_clone_btn = "//td[@class='action']/span[contains(@id,'clone-authsvr')]",

    create_server_span = "//span[@id='new-authsvr']",
    show_more_button = "//input[@id='showmore-authsvr']",
    select_all_checkbox = "//input[@id='authsvr-sall']",
    delete_button = "//input[@id='del-authsvr']",
    ok_button = "//input[@id='ok-authsvr']",

    name_textbox = "//input[@id='name']",

    type_ad_radio = "//input[@id='type-ad']",
    type_ldap_server_radio = "//input[@id='type-ldap']",
    type_radius_auth_radio = "//input[@id='type-radius-auth']",
    type_radius_acct_radio = "//input[@id='type-radius-acct']",

    type_tacacs_plus_radio = "//input[@id='type-tacplus-auth']",
    radius_auth_method_pap_radio = "//input[@id='pap']",
    radius_auth_method_chap_radio = "//input[@id='chap']",

    server_ip_textbox = "//input[@id='pri-ip']",
    server_port_textbox = "//input[@id='pri-port']",

    ad_server_gc_enabled_checkbox = "//input[@id='ad-gc-enabled']",
    ad_server_searchbase_textbox = "//input[@id='ad-search-base']",
    ad_server_admin_dn_textbox = "//input[@id='ad-admin-dn']",
    ad_server_admin_pwd_textbox = "//input[@id='ad-admin-pwd']",
    ad_server_admin_pwd2_textbox = "//input[@id='ad-admin-pwd2']",

    ldap_server_searchbase_textbox = "//input[@id='ldap-search-base']",
    ldap_server_admin_dn_textbox = "//input[@id='ldap-admin-dn']",
    ldap_server_admin_pwd_textbox = "//input[@id='ldap-admin-pwd']",
    ldap_server_admin_pwd2_textbox = "//input[@id='ldap-admin-pwd2']",

    radius_secret_textbox = "//input[@id='pri-pwd']",
    radius_secret2_textbox = "//input[@id='pri-pwd2']",

    radius_backup_enabled_checkbox = "//input[@id='radius-backup-enabled']",
    server_sec_ip_textbox = "//input[@id='sec-ip']",
    server_sec_port_textbox = "//input[@id='sec-port']",
    radius_sec_secret_textbox = "//input[@id='sec-pwd']",
    radius_sec_secret2_textbox = "//input[@id='sec-pwd2']",

    radius_primary_timeout_textbox = "//input[@id='pri-timeout']",
    radius_failover_retries_textbox = "//input[@id='failover-retry']",
    radius_primary_reconnect_interval_textbox = "//input[@id='pri-retry-int']",

    #stan@20110111
    aaa_edit_button = r"//table[@id='%s']//tr/td[text()='%s']/../td[@class='action']/span[contains(@id,'edit-authsvr')]",
    aaa_search_txt = r"//table[@id='%s']/tfoot/tr[2]/td/span/input[1]",
    aaa_cancel_button = r"//input[@id='cancel-authsvr']",
    ldap_server_key_attribute_textbox = r"//input[@id='ldap-key']",
    ldap_server_search_filter_textbox = r"//input[@id='ldap-filter']",
    
    tacplus_service_textbox = "//input[@id='tac-service']",
    
    #test setting
    test_select_server="//select[@id='test-authsvr']",
    test_user_name="//input[@id='username-authtest']",
    test_password="//input[@id='password-authtest']",
    test_button="//input[@id='test-authsvrtest']",
    test_result="//span[@id='msg-authtest']",
)

tbl_id = dict(
    aaa_server = 'authsvr',
)

def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_AUTHENTICATION_SERVER)


def _set_server_cfg(zd, params):
    '''
    '''
    conf = {
        'server_addr': '', 'server_port': '', 'server_name': '',
        'win_domain_name': '', 'global_catalog': '','admin_domain_name': '', 'admin_password': '', 
        'ldap_search_base': '', 'ldap_admin_dn': '', 'ldap_admin_pwd': '',
        'ldap_key_attribute': '', 'ldap_search_filter': '',
        'radius_auth_secret': '', 'radius_acct_secret': '',
        'secondary_server_addr':'', 'secondary_server_port': '',
        'secondary_radius_auth_secret': '', 'secondary_acct_secret': '',
        'primary_timeout': '', 'failover_retries': '', 'primary_reconnect': '',
        'radius_auth_method': 'pap','tacacs_auth_secret':None,'tacacs_service':None,'server_type':''
    }
    conf.update(params)

    xpath_by_aaa_type = {
        'ad': locs['type_ad_radio'],
        'ldap': locs['type_ldap_server_radio'],
        'radius': locs['type_radius_auth_radio'],
        'rad_acct': locs['type_radius_acct_radio'],
        'tacacs_plus': locs['type_tacacs_plus_radio'],
    }
    if conf.get('server_type'):
        aaa_type = conf['server_type']
    else:
        if conf.get('win_domain_name'):
            aaa_type = "ad"
    
        elif conf.get('ldap_search_base'):
            aaa_type = "ldap"
    
        elif conf.get('radius_auth_secret'):
            aaa_type = "radius"
    
        elif conf.get('radius_acct_secret'):
            aaa_type = "rad_acct"
            
        elif conf.get('tacacs_service'):
            aaa_type = "tacacs_plus"

        else:
            raise Exception("No AAA type specified.")

    # Choose server type
    zd.s.click_and_wait(xpath_by_aaa_type[aaa_type])

    # configure backup radius server
    if conf['secondary_server_addr']:
        if not zd.s.is_checked(locs['radius_backup_enabled_checkbox']):
            zd.s.click_and_wait(locs['radius_backup_enabled_checkbox'], 2)

    # Enter detail information
    if conf['server_name']:
        zd.s.type_text(locs['name_textbox'], conf['server_name'])

    if conf['server_addr']:
        zd.s.type_text(locs['server_ip_textbox'], conf['server_addr'])



    if aaa_type == "ad":
        zd.s.type_text(locs['ad_server_searchbase_textbox'], conf['win_domain_name'])
        
        #Cherry-2012-02 Add set global category and admin domain name and password.
        if zd.s.is_element_present(locs['ad_server_gc_enabled_checkbox']):
            if conf['global_catalog']:
                if not zd.s.is_checked(locs['ad_server_gc_enabled_checkbox']):
                    zd.s.click_and_wait(locs['ad_server_gc_enabled_checkbox'], 2)
        
                zd.s.type_text(locs['ad_server_admin_dn_textbox'], conf['admin_domain_name'])            
                zd.s.type_text(locs['ad_server_admin_pwd_textbox'], conf['admin_password'])
                zd.s.type_text(locs['ad_server_admin_pwd2_textbox'], conf['admin_password'])
        
    if aaa_type == "ldap":
        ldap_search_base = conf['ldap_search_base']
        if not zd.s.is_element_present(locs['ldap_server_admin_dn_textbox']):
            ldap_search_base = "ou=users,%s" % conf['ldap_search_base']

        zd.s.type_text(locs['ldap_server_searchbase_textbox'], ldap_search_base)
        if zd.s.is_element_present(locs['ldap_server_admin_dn_textbox']):
            zd.s.type_text(locs['ldap_server_admin_dn_textbox'], conf['ldap_admin_dn'])
            zd.s.type_text(locs['ldap_server_admin_pwd_textbox'], conf['ldap_admin_pwd'])
            zd.s.type_text(locs['ldap_server_admin_pwd2_textbox'], conf['ldap_admin_pwd'])
            
        #Cherry-2012-02 Add set ldap search filter and key attribute.
        if zd.s.is_element_present(locs['ldap_server_key_attribute_textbox']):
            zd.s.type_text(locs['ldap_server_key_attribute_textbox'], conf['ldap_key_attribute'])
        if zd.s.is_element_present(locs['ldap_server_search_filter_textbox']):
            zd.s.type_text(locs['ldap_server_search_filter_textbox'], conf['ldap_search_filter'])

    if aaa_type == "radius":
        if conf['radius_auth_method'] == "chap" and zd.s.is_element_present(locs['radius_auth_method_chap_radio']):
            zd.s.click_and_wait(locs['radius_auth_method_chap_radio'])
        if conf['radius_auth_method'] == "pap" and zd.s.is_element_present(locs['radius_auth_method_pap_radio']):
            zd.s.click_and_wait(locs['radius_auth_method_pap_radio'])

        zd.s.type_text(locs['radius_secret_textbox'], conf['radius_auth_secret'])
        zd.s.type_text(locs['radius_secret2_textbox'], conf['radius_auth_secret'])

    if aaa_type == "rad_acct":
        zd.s.type_text(locs['radius_secret_textbox'], conf['radius_acct_secret'])
        zd.s.type_text(locs['radius_secret2_textbox'], conf['radius_acct_secret'])

    if aaa_type == "tacacs_plus":
        if conf['tacacs_auth_secret'] is not None:
            zd.s.type_text(locs['radius_secret_textbox'], conf['tacacs_auth_secret'])
            zd.s.type_text(locs['radius_secret2_textbox'], conf['tacacs_auth_secret'])
        if conf['tacacs_service'] is not None:
            zd.s.type_text(locs['tacplus_service_textbox'], conf['tacacs_service'])
    #Move set server port after check global category because when check it port will be set as 3268 by default.
    if conf['server_port']:
        zd.s.type_text(locs['server_port_textbox'], conf['server_port'])

    # configure radius backup server
    if conf['secondary_server_addr']:
        zd.s.type_text(locs['server_sec_ip_textbox'], conf['secondary_server_addr'])

        if conf['secondary_server_port']:
            zd.s.type_text(locs['server_sec_port_textbox'], conf['secondary_server_port'])

        shared_secret = ""
        if conf['radius_auth_secret']:
            shared_secret = conf['secondary_radius_auth_secret']

        elif conf['radius_acct_secret']:
            shared_secret = conf['secondary_acct_secret']

        if shared_secret:
            zd.s.type_text(locs['radius_sec_secret_textbox'], shared_secret)
            zd.s.type_text(locs['radius_sec_secret2_textbox'], shared_secret)

        if conf['primary_timeout']:
            zd.s.type_text(locs['radius_primary_timeout_textbox'], conf['primary_timeout'])

        if conf['failover_retries']:
            zd.s.type_text(locs['radius_failover_retries_textbox'], conf['failover_retries'])

        if conf['primary_reconnect']:
            zd.s.type_text(locs['radius_primary_reconnect_interval_textbox'], conf['primary_reconnect'])


    zd.s.click_and_wait(locs['ok_button'])

    return zd.s.get_alert(locs['aaa_cancel_button'])


def _create_server(zd, **kwargs):
    '''
    @is_nav: to support config aaa_servers page on ZD template from FM. If
             is_nav = True, don't do navigate.
    '''
    params = {
        'server_addr': '', 'server_port': '', 'server_name': '',
        'win_domain_name': '', 'global_catalog': '','admin_domain_name': '', 'admin_password': '', 
        'ldap_search_base': '', 'ldap_admin_dn': '', 'ldap_admin_pwd': '',
        'ldap_key_attribute': '', 'ldap_search_filter': '',        
        'radius_auth_secret': '', 'radius_acct_secret': '',
        'secondary_server_addr':'', 'secondary_server_port': '',
        'secondary_radius_auth_secret': '', 'secondary_acct_secret': '',
        'primary_timeout': '', 'failover_retries': '', 'primary_reconnect': '',        
        'is_nav': True,
    }
    params.update(kwargs)
        
    if not params['server_name']:
        params['server_name'] = params['server_addr']

    if params.pop('is_nav'):
        _nav_to(zd)

    try:
        if zd.s.is_visible(locs['create_server_span']):
            zd.s.click_and_wait(locs['create_server_span'])

        else:
            raise Exception('The "Create New" button is disabled')

        msg = _set_server_cfg(zd, params)


    except Exception, e:
        logging.info("Catch the error when creating a server [%s]" % e.message)
        raise Exception(e.message)

    logging.info("The server [%s] has been created successfully" % params['server_name'])
    return msg


def _edit_server(zd, name, new_cfg):
    '''
    '''
    widgets_zd._fill_search_txt(
        zd.s, locs['aaa_tbl_filter_txt'] % tbl_id['aaa_server'], name
    )

    if zd.s.is_element_present(locs['aaa_edit_btn']):
        zd.s.click_and_wait(locs['aaa_edit_btn'])

        try:
            msg = _set_server_cfg(zd, new_cfg)
            logging.info("The AAA server [%s] was edited successfully" % name)

        except:
            logging.info("The AAA server [%s] could not be edited" % name)
            raise

    else:
        raise Exception("The AAA server [%s] does not exist" % name)
    
    return msg
    
#add by west.li
#del a server according to the name
def _del_server(zd, name):
    '''
    '''
    _nav_to(zd)
    
    widgets_zd._fill_search_txt(
        zd.s, locs['aaa_tbl_filter_txt'] % tbl_id['aaa_server'], name
    )

    zd.s.click_and_wait(locs['select_all_checkbox'])

    if not zd.s.is_element_disabled(locs['delete_button'], timeout = 0.2,
                                    disabled_xpath = "[@disabled]"):
        zd.s.click_and_wait(locs['delete_button'])

    else:
        raise Exception("The AAA server [%s] does not exist" % name)


def _get_auth_server_info_list(zd, is_nav):
    '''
    '''
    if is_nav:
        _nav_to(zd)

    return widgets_zd.get_tbl_rows(
        zd.s, locs['aaa_tbl_loc'] % tbl_id['aaa_server'],
        locs['aaa_tbl_loc'] % tbl_id['aaa_server']
    )


def _remove_all_servers(zd, pause = 2):
    '''
    '''
    _nav_to(zd)

    while True:
        zd.s.click_and_wait(locs['select_all_checkbox'])
        time.sleep(2)
        if not zd.s.is_element_disabled(locs['delete_button'], timeout = 0.2,
                                        disabled_xpath = "[@disabled]"):
            zd.s.click_and_wait(locs['delete_button'])
            time.sleep(pause)

        else:
            break


def _get_server_cfg_by_name(zd, server_name):
    '''
    Output:
        a dict of the aaa server cfg.
        cfg = {'server_name': '', 'type': '', 'global_catalog': True/False, 'backup': True/False,
               'server_addr': '', 'server_port': '', 'win_domain_name': '', 'admin_domain_name': '',
               'ldap_key_attribute': '', 'ldap_search_filter': '', 'backup_server_addr': '', 'backup_server_port': '',
               request_timeout': '', 'retry_count': '', 'retry_interval': '', 'radius_auth_method':'',
               }
    '''
    logging.info('Get the cfg of AAA server[%s] in ZD GUI' % server_name)
    cfg = dict()

    _set_search_box(zd.s, locs['aaa_search_txt'] % tbl_id['aaa_server'], server_name)
    aaa_edit_button = locs['aaa_edit_button'] % (tbl_id['aaa_server'], server_name)
    if zd.s.is_visible(aaa_edit_button):
        zd.s.click_and_wait(aaa_edit_button)

    else:
        _set_search_box(zd.s, locs['aaa_search_txt'] % tbl_id['aaa_server'], '')
        logging.info('Not found the AAA server[%s] in ZD GUI' % server_name)
        return cfg

    cfg['server_name'] = zd.s.get_value(locs['name_textbox'])
    cfg['server_addr'] = zd.s.get_value(locs['server_ip_textbox'])
    cfg['server_port'] = zd.s.get_value(locs['server_port_textbox'])

    if zd.s.is_checked(locs['type_ad_radio']):
        cfg['type'] = 'ad'
        cfg['win_domain_name'] = zd.s.get_value(locs['ad_server_searchbase_textbox'])
        if zd.s.is_checked(locs['ad_server_gc_enabled_checkbox']):
            cfg['global_catalog'] = True
            cfg['admin_domain_name'] = zd.s.get_value(locs['ad_server_admin_dn_textbox'])

        else:
            cfg['global_catalog'] = False

    elif zd.s.is_checked(locs['type_ldap_server_radio']):
        cfg['type'] = 'ldap'
        cfg['win_domain_name'] = zd.s.get_value(locs['ldap_server_searchbase_textbox'])
        if zd.s.is_element_present(locs['ldap_server_admin_dn_textbox']):
            cfg['admin_domain_name'] = zd.s.get_value(locs['ldap_server_admin_dn_textbox'])

        if zd.s.is_element_present(locs['ldap_server_key_attribute_textbox']):
            cfg['ldap_key_attribute'] = zd.s.get_value(locs['ldap_server_key_attribute_textbox'])

        if zd.s.is_element_present(locs['ldap_server_search_filter_textbox']):
            cfg['ldap_search_filter'] = zd.s.get_value(locs['ldap_server_search_filter_textbox'])

    elif zd.s.is_checked(locs['type_radius_auth_radio']):
        cfg['type'] = 'radius-auth'

        if zd.s.is_checked(locs['radius_auth_method_chap_radio']):
            cfg['radius_auth_method'] = 'chap'
        else:
            cfg['radius_auth_method'] = 'pap'

    elif zd.s.is_checked(locs['type_radius_acct_radio']):
        cfg['type'] = 'radius-acct'

    elif zd.s.is_checked(locs['type_tacacs_plus_radio']):
        cfg['type'] = 'tacacs_plus'

    else:
        raise Exception('No type checked')

    if cfg['type'] == 'radius-auth' or cfg['type'] == 'radius-acct':
        if zd.s.is_checked(locs['radius_backup_enabled_checkbox']):
            cfg['backup'] = True
            cfg['backup_server_addr'] = zd.s.get_value(locs['server_sec_ip_textbox'])
            cfg['backup_server_port'] = zd.s.get_value(locs['server_sec_port_textbox'])
            cfg['request_timeout'] = zd.s.get_value(locs['radius_primary_timeout_textbox'])
            cfg['retry_count'] = zd.s.get_value(locs['radius_failover_retries_textbox'])
            cfg['retry_interval'] = zd.s.get_value(locs['radius_primary_reconnect_interval_textbox'])

        else:
            cfg['backup'] = False
            
    elif cfg['type'] == 'tacacs_plus':
        cfg['tacacs_service']=zd.s.get_value(locs['tacplus_service_textbox'])

    zd.s.click_and_wait(locs['aaa_cancel_button'])
    _set_search_box(zd.s, locs['aaa_search_txt'] % tbl_id['aaa_server'], '')
    logging.info('The cfg of AAA server[%s] in ZD GUI is:\n%s' % (server_name, cfg))

    return cfg


def _set_search_box(s, loc, v):
    s.type_text(loc, v)
    ENTER_CODE = u'\013'
    s.key_down(loc, ENTER_CODE)
    time.sleep(2)

