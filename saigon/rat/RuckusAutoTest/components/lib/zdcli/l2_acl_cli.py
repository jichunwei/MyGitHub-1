'''
This module define the l2 ACL
Updated by cwang@2012-07-03
'''

import time
import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

SHOW_L2ACL_ALL = 'show l2acl all'
SHOW_L2ACL_NAME = 'show l2acl name "$name"'

CREATE_L2ACL = """
l2acl '$l2acl_name'
"""

SET_L2ACL_NAME ="""
l2acl '$l2acl_name'
    name '$new_name'
"""
SET_L2ACL_DESCRIPTION = """
l2acl '$l2acl_name'
    description $description
"""
SET_L2ACL_POLICY = """
l2acl '$l2acl_name'
    mode $mode
"""

SET_L2ACL_MAC = """
l2acl '$l2acl_name'
    add-mac $mac_addr
"""

REMOVE_L2ACL_MAC = """
l2acl '$l2acl_name'
    del-mac $mac_addr
"""

REMOVE_L2ACL = """
no l2acl '$l2acl_name'
"""


CONST_KEY = {'name': 'Name',
             'title':'L2/MAC ACL',
             'id':'ID',
             }

def show_l2acl_all(zdcli):
    cmd_block = SHOW_L2ACL_ALL
    logging.info("======show l2 ACL all==========")

    l2acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The l2 ACL result\n:%s',l2acl_result)
    l2acl_data = output.parse(l2acl_result)
    
#    logging.info('The l2 ACL dict result:\n%s',l2acl_data)
    return l2acl_data


def show_l2acl_name(zdcli,l2acl_name):
    cmd_block = Template(SHOW_L2ACL_NAME).substitute(dict(name = l2acl_name))
    
    logging.info( "=======show l2 ACL name=========")

    l2acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The l2 ACL result\n%s:' % l2acl_result)
    l2acl_data = output.parse(l2acl_result)
    
#    logging.info('The l2 ACL dict result:\n%s' % l2acl_data)
    return l2acl_data


def verify_l2acl_all(l2acl_data,acl_name_list,mac_list,acl_policy=True,msg = None):
    
    logging.info("Verify 'show l2acl all' in CLI and GUI are the same")
    rule_number = len(acl_name_list)
    if rule_number == 0:
        logging.info("When there is no ACL in GUI...")
        if l2acl_data[CONST_KEY['title']]['ID'].has_key('2'):
            logging.info("There is another ACL in CLI -- incorrect behaver")
            return False
        else:
            logging.info("There is only one default ACL in CLI -- incorrect behaver")
            return True
        
    else:
        logging.info("When there are another ACLs in GUI")
        for i in range(2,rule_number+2):
            j = str(i)
            if not l2acl_data[CONST_KEY['title']]['ID'].has_key(j):
                logging.info("There is no ACL in CLI -- incorrect behaver")
                return False
            
            if l2acl_data[CONST_KEY['title']]['ID'][j]['Name'] != acl_name_list[i-2]:
                logging.info("The ACL name in CLI is different in GUI")
                return False

            if l2acl_data[CONST_KEY['title']]['ID'][j]['Stations']['MAC Address'] != mac_list:
                logging.info("The MAC list in CLI is different in GUI")
                return False

            if l2acl_data[CONST_KEY['title']]['ID'][j]['Restriction'].keys()[0] == 'Allow only the stations listed below':
                if acl_policy == False:
                    logging.info("The policy in CLI is different from in GUI")
                    return False
            else:
                if acl_policy == True:
                    return False
                    logging.info("The policy in CLI is different from in GUI")
        
        logging.info("The CLI L2 ACL's name, MAC list and policy are the same as GUI")
        return True
            

def verify_l2acl_name(l2acl_data,acl_name,mac_list,acl_policy=True,msg = None):
    logging.info("Verify 'show l2acl name $name' in CLI and GUI are the same")
    ilist = l2acl_data[CONST_KEY['title']]['ID'].keys()
    i = ilist[0]
    if l2acl_data[CONST_KEY['title']]['ID'][i]['Name'] != acl_name:
        logging.info("The ACL name in CLI is different from in GUI")
        return False
    
    if l2acl_data[CONST_KEY['title']]['ID'][i]['Stations']['MAC Address'] != mac_list:
        logging.info("The ACL MAC list is different from in GUI")
        return False
    
    if l2acl_data[CONST_KEY['title']]['ID'][i]['Restriction'] == 'Allow only the stations listed below':
        if acl_policy == False:
            logging.info("The policy in CLI is different from in GUI")
            return False
        else:
            if acl_policy == True:
                logging.info("The policy in CLI is different from in GUI")
                return False
    logging.info("The CLI L2 ACL's name, MAC list and policy are the same as GUI")
    return True


def create_l2acl(zdcli,l2acl_conf_list):    
    for l2acl_conf in l2acl_conf_list:
        _create_l2acl(zdcli,l2acl_conf)


def delete_all_l2acls(zdcli):
    aclsinfo = show_l2acl_all(zdcli)
    acldata = aclsinfo[CONST_KEY['title']][CONST_KEY['id']]    
    for id, acl in acldata.items():       
        acl_name = acl[CONST_KEY['name']]
        if acl_name == 'System':
            continue
        
        delete_l2acl_by_name(zdcli, acl_name)

def delete_l2acl_by_name(zdcli, acl_name):
    _delete_l2acl(zdcli, acl_name)        


def _delete_l2acl(zdcli, acl_name):
    cmd = Template(REMOVE_L2ACL).substitute(dict(l2acl_name = acl_name))
    logging.info('[ZDCLI]Remove L2 ACL %s' % acl_name)  
    _do_excute_cmd(zdcli,cmd)
     
def _create_l2acl(zdcli,conf):
    _create_blank_l2acl(zdcli,conf)
    _rename_l2acl(zdcli,conf)
    _set_l2acl_description(zdcli,conf)
    _set_l2acl_policy(zdcli,conf)
    _add_mac_addr_to_l2acl(zdcli,conf)
    
def _create_blank_l2acl(zdcli,l2acl_conf):
    cmd = Template(CREATE_L2ACL).substitute(dict(l2acl_name = l2acl_conf['acl_name']))
    
    logging.info('[ZDCLI]Create L2 ACL %s' % l2acl_conf['acl_name'])  
    _do_excute_cmd(zdcli,cmd)
    
def _rename_l2acl(zdcli,l2acl_conf):
    if l2acl_conf.has_key('new_name'):
        if l2acl_conf['new_name']:
            cmd = Template(SET_L2ACL_NAME).substitute(dict(
                                                           l2acl_name = l2acl_conf['acl_name'],
                                                           new_name = l2acl_conf['new_name']
                                                           ))
            logging.info("[ZDCLI] Rename L2 ACL[%s] to [%s]" %(l2acl_conf['acl_name'],l2acl_conf['new_name']))
            _do_excute_cmd(zdcli,cmd)
        

def _set_l2acl_description(zdcli,conf):
    if conf.has_key('description') and conf['description']:
        cmd = Template(SET_L2ACL_DESCRIPTION).substitute(dict(l2acl_name = conf['acl_name'],
                                                              description = conf['description']
                                                              ))
        logging.info("[ZDCLI]: Set L2 ACL[%s] description:[%s]" %(conf['acl_name'],conf['description']))
        _do_excute_cmd(zdcli,cmd)

def _set_l2acl_policy(zdcli,conf):
    if conf.has_key('policy') and conf['policy']:
        cmd = Template(SET_L2ACL_POLICY).substitute(dict(l2acl_name = conf['acl_name'],
                                                         mode = conf['policy']
                                                         ))
        
        logging.info("[ZDCLI]: Set L2 ACL[%s] policy(mode):%s " %(conf['acl_name'],conf['policy']))
        _do_excute_cmd(zdcli,cmd)

def _add_mac_addr_to_l2acl(zdcli,conf):
    if conf.has_key('mac_entries') and conf['mac_entries']:
        mac_list = conf['mac_entries']
        SET_L2ACL_MAC = """l2acl '$l2acl_name'\r%s"""
        mac_cmd = ""
        for mac in mac_list:
            mac_cmd += "add-mac %s\r" % mac         
        SET_L2ACL_MAC = SET_L2ACL_MAC % mac_cmd
        cmd = Template(SET_L2ACL_MAC).substitute(l2acl_name = conf['acl_name'])        
        logging.info("[ZDCLI]: Add MAC address[%s] to L2 ACL" %(conf['acl_name']))
        _do_excute_cmd(zdcli,cmd)
            
def _remove_mac_addr_from_l2acl(zdcli,acl_name,mac):
    cmd = Template(REMOVE_L2ACL_MAC).substitute(l2acl_name = acl_name,
                                                mac_addr= mac)
    
    logging.info('[ZDCLI]: Remove MAC Address[%s] from L2ACL[%s]' %(mac,acl_name))
    _do_excute_cmd(zdcli,cmd)
    
    
def _do_excute_cmd(zdcli,cmd):
    try:
        time.sleep(1)
        logging.info("CLI is: %s" %cmd)
        zdcli.do_cfg(cmd)
        time.sleep(2)
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)
    
    
def _verify_l2acl_cliset_cliget(cli_set,cli_get):
    
    id = cli_get[CONST_KEY['title']]['ID'].keys()[0]
    
    cli_get_dict = cli_get[CONST_KEY['title']]['ID'][id]
    
    if cli_get_dict['Name'] != cli_set['acl_name']:
        return("FAIL, Get L2 ACL name:[%s],expect: [%s]" %(cli_get_dict['Name'],cli_set['acl_name']))
    
    if cli_get_dict['Description'] != cli_set['description']:
        return("FAIL, Get L2 ACL Description:[%s],expect[%s]" % (cli_get_dict['Description'],cli_set['description']))
    
    if type(cli_get_dict['Stations']['MAC Address'])is list:
        for acl_mac_list in cli_get_dict['Stations']['MAC Address']:
            if acl_mac_list not in cli_set['mac_entries']:
    #if cli_get_dict['Stations']['MAC Address'] != cli_set['mac_entries']:
                return("FAIL, Get L2 ACL MAC entries:[%s], expect[%s]" % (acl_mac_list,cli_set['mac_entries']))
    else:
        if cli_get_dict['Stations']['MAC Address'] not in cli_set['mac_entries']:
            return("FAIL, Get L2 ACL MAC entries:[%s], expect[%s]" % (cli_get_dict['Stations']['MAC Address'],cli_set['mac_entries']))
    
    if cli_get_dict['Restriction'].startswith('Allow'):
        if cli_set['policy'] !='allow':
            return("FAIL, Get L2 ACL Description :[%s], expect['allow']" %cli_get_dict['Restriction'].keys()[0])
            
    elif cli_get_dict['Restriction'].startswith('Deny'):
        if cli_set['policy'] !='deny':
            return("FAIL, Get L2 ACL Policy(Mode) :[%s],expect['deny']" % cli_get_dict['Restriction'].keys()[0])
    
def _verify_l2acl_cliset_guiget(cli_set,gui_get):
    '''
    cli_set = {'policy': 'deny', 
                'description': 'yIKsoHl9cvxzIL', 
                'acl_name': 'uCSetwxu3sXsagHcnCHh', 
                'mac_entries': ['00:00:00:00:00:01', '00:00:00:00:00:02']
                }
    
    guiset = {'acl_name': 'louis',
 'mac_entries': [u'00:01:02:03:04:05',
                 u'00:01:02:03:04:06',
                 u'00:01:02:03:04:04'],
 'policy': 'allow-all'}
        
        '''    
    for key in gui_get.keys():
        if cli_set[key] == 'deny':
            cli_set[key] ='deny-all'
        if cli_set[key] =='allow':
            cli_set[key] = 'allow-all'
        if cli_set[key] != gui_get[key]:
            return('FAIL, CLI Set[%s:%s] are different GUI Get[%s:%s]' %(key,cli_set[key],key,gui_get[key])) 