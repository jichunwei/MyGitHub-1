"""
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


import logging
import copy
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict
from RuckusAutoTest.common import lib_Debug as bugme


#Command templates
GET_WLAN_GROUP_ALL= "show wlan-group all"
GET_WLAN_GROUP_BY_NAME= "show wlan-group name '$name'"

NAME_ERR_MSG = "The entry '$name' could not be found. Please check the spelling, and then try again."


def get_wlan_group_by_name(zdcli, name):
    """
    Output:
            a dictionary of the WLAN group information:
            {
             ...
            }
            none: the WLAN group does not exist.
            exception
    """
    cmd = Template(GET_WLAN_GROUP_BY_NAME).substitute(dict(name = name))
    name_err_msg = Template(NAME_ERR_MSG).substitute(dict(name = name))
    
    logging.info('Get information of WLAN group [%s] from ZD CLI by command [%s].' % (name, cmd))
    try:
        info = _get_wlan_group_info_as_dict(zdcli, cmd)
        
    except Exception, ex:
        if name_err_msg in ex.message:
            logging.info('The WLAN group [%s] does not exist in ZD CLI!' % name)
            return None
        else:
            raise Exception(ex.message)
    
    wlan_group = info.values()[0]
    logging.info('The information of WLAN group [%s] in ZD CLI is:\n%s.' % (name, pformat(wlan_group)))

    return wlan_group


def get_wlan_group_all(zdcli):
    """
    Output:
            a dictionary of all WLAN group information:
            {
             '1': {
                   'name':
                   'Description':
                   'VLAN Override': 
                   'WLAN Service':
                   },
             ...
            }
            exception
    """
    logging.info('Get all WLAN group information via ZD CLI by command [%s].' % GET_WLAN_GROUP_ALL)
    wlan_group = _get_wlan_group_info_as_dict(zdcli, GET_WLAN_GROUP_ALL)
    
    logging.info("All WLAN group information in ZD CLI is:\n%s." % pformat(wlan_group))
    
    return wlan_group


def verify_wlan_group_all(cli_wgs, gui_wgs):
    """
    This method is used to verify whether the information of all WLAN group shown in ZD CLI is the same as in ZD GUI.
    """
    logging.info('Verify all WLAN group information shown in ZD CLI.')
    
    cli_wgs_list =  cli_wgs.values()
    gui_wgs_list =  gui_wgs.values()
    
    cli_len = len(cli_wgs_list)
    gui_len = len(gui_wgs_list)

    if cli_len != gui_len:
        logging.info('The number of WLAN groups in ZD CLI [%s] is not the same as in ZD GUI [%s]!' % (cli_len, gui_len))
        return False
    
    for i in range(cli_len):
        for j in range(gui_len):
            if cli_wgs_list[i]['Name'] == gui_wgs_list[j]['name']:
                res = _verify_wlan_group_info(cli_wgs_list[i], gui_wgs_list[j])
                if not res:
                    logging.info('The information of WLAN group [%s] shown in ZD ZD GUI!' % cli_wgs_list[i]['Name'])
                    return False
                else:
                    break
                
            elif j == gui_len - 1:
                logging.info('The WLAN group [%s] exists in ZD CLI, but not in ZD GUI!' % cli_wgs_list[i]['Name'])
                return False
            
    logging.info('All WLAN group information shown in ZD CLI is the same as in ZD GUI!')
    return True
    

def verify_wlan_group(cli_wg, gui_wg):
    """
    This method is used to verify whether the information of a WLAN group shown in ZD CLI is the same as in ZD GUI.
    """
    logging.info('Verify the WLAN group information shown in ZD CLI.')
    
    if cli_wg == None:
        if gui_wg == None:
            logging.info('No WLAN group exists in ZD CLI or ZD GUI!')
            return True
        else:
            logging.info('The WLAN group [%s] exists in ZD GUI but not in ZD CLI!' % gui_wg['name'])
            return False
    else:
        if gui_wg == None:
            logging.info('The WLAN group [%s] exists in ZD CLI but not in ZD GUI!' % cli_wg['Name'])
            return False
        
    res = _verify_wlan_group_info(cli_wg, gui_wg)
    if res:
        logging.info('The information of WLAN group [%s] shown in ZD CLI is the same as in ZD GUI!' % cli_wg['Name'])
        return True
    
    else:
        logging.info('The information of WLAN group [%s] shown in ZD CLI is not the same as in ZD GUI!' % cli_wg['Name'])
        return False


def get_wlan_member_list(zdcli, wg_name):
    '''
    Output:
        a list of all wlan members in the wlan group.
    '''
    logging.info('Get the WLAN members of WLAN group [%s]' % wg_name)
    wlan_member_list = []
    wg_info = get_wlan_group_by_name(zdcli, wg_name)
    if wg_info == None:
        return None
    
    if wg_info.has_key('WLAN Service'):
        wlans = wg_info['WLAN Service'].keys()
        for w in wlans:
            wlan_name = wg_info['WLAN Service'][w]['NAME']
            wlan_member_list.append(wlan_name)
    
    return wlan_member_list


def get_all_wlan_group_name_list(zdcli):
    wg_info_dict = get_wlan_group_all(zdcli)
    wg_info_list = wg_info_dict.values()
    wg_name_list = []
    for i in range(len(wg_info_list)):
        wg_name = wg_info_list[i]['Name']
        wg_name_list.append(wg_name)
        
    return wg_name_list


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _get_wlan_group_info_as_dict(zdcli, cmd):
    data = zdcli.do_show(cmd)
    info = output_as_dict.parse(data)
    
    if not info.has_key('WLAN Group'):
        raise Exception(data)

    return info['WLAN Group']['ID']


def _verify_wlan_group_info(cli_wg, gui_wg):
    _cli_wg = _format_cli_info(cli_wg)
    _gui_wg = _format_gui_info(gui_wg)
    
    if _cli_wg == _gui_wg:
        return True
    else:
        for cli_wg_u in _cli_wg['WLAN Service'].keys():
            if 'tag' not in _cli_wg['WLAN Service'][cli_wg_u]['VLAN'].lower() and \
                'tag' in _gui_wg['WLAN Service'][cli_wg_u]['VLAN'].lower():
                #added by jluh 2013-11-05
                #in cli side the vlan value is {'VLAN': '302'}
                #but in gui side the vlan value is {'VLAN': u'302(Tag)'}
                #so split '(', and only get '302' to update the gui side's vlan value.
                #compare the both dict, it will be done.
                _gui_wg['WLAN Service'][cli_wg_u].update({'VLAN': _gui_wg['WLAN Service'][cli_wg_u]['VLAN'].split('(')[0]})
                
        if _cli_wg == _gui_wg:
            return True
        else:
            return False


def _format_gui_info(gui_wg):
    _info = {}
    
    _info['Description'] = gui_wg['description']
    _info['Name'] = gui_wg['name']
        
    if gui_wg['vlan_override']:
        _info['VLAN Override'] = {'Status': 'Enabled'}
    else:
        _info['VLAN Override'] = {'Status': 'Disabled'}

    if gui_wg['wlan_member']:
        _info['WLAN Service'] = copy.deepcopy(gui_wg['wlan_member'])
        wlans = _info['WLAN Service'].keys()
        
        if gui_wg['vlan_override']:
            for w in wlans:
                _info['WLAN Service'][w].pop('original_vlan')                
                vlan_override = _info['WLAN Service'][w].pop('vlan_override')
                
                if vlan_override == 'No Change':
                    _info['WLAN Service'][w]['VLAN'] = ''
                
                elif vlan_override == 'Untag':
                    _info['WLAN Service'][w]['VLAN'] = ''#Behavior Change after 9.3
                    #_info['WLAN Service'][w]['VLAN'] = '1(Untag)'
                
                elif vlan_override == 'Tag':
                    _info['WLAN Service'][w]['VLAN'] = '%s(Tag)' % _info['WLAN Service'][w].pop('tag_override')
                    
                else:
                    raise Exception("Unexpect Vlan Override settings")
        
        else:
            for w in wlans:
                _info['WLAN Service'][w]['VLAN'] = ''

    return _info


def _format_cli_info(cli_wg):
    _info = copy.deepcopy(cli_wg)
    
    #stan@20110118, feature update for 9.2
    if not _info.has_key('VLAN Override'):
        _info['VLAN Override'] = {'Status': 'Enabled'}
    
    if _info.has_key('WLAN Service'):
        wlan_dict = {}
        wlans = _info['WLAN Service'].keys()
        for w in wlans:
            #stan@20110118
#            ssid = _info['WLAN Service'][w].pop('SSID')
#            wlan_dict[ssid] = _info['WLAN Service'][w]
            wlan_name = _info['WLAN Service'][w].pop('NAME')
            wlan_dict[wlan_name] = _info['WLAN Service'][w]
            
        _info['WLAN Service'] = wlan_dict

    return _info
