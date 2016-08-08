'''
Created on Dec 1, 2014

@author: chen.tao@odc-ruckuswireless.com

'''
import re
import random
import logging
from copy import deepcopy
from RuckusAutoTest.components.lib.zdcli import output_as_dict

CONFIG_VLAN_POOL = 'vlan-pool "%s"\n'
EDIT_VLAN_POOL = 'vlan-pool "%s"\n'
SET_VLAN_POOL_NAME = 'name "%s"\n'
SET_VLAN_POOL_DESC = 'description "%s"\n'
SET_VLAN_POOL_ADD_VLAN = "vlan add %s\n"
SET_VLAN_POOL_DEL_VLAN = "vlan del %s\n"
SET_VLAN_POOL_OPTION = "option %s\n"
DELETE_VLAN_POOL = 'no vlan-pool "%s"\n'
SHOW_VLAN_POOL_ALL = "show vlan-pool\n"

SAVE_CFG = "exit\n"

def get_vlan_pool_list(zdcli):
    '''      
    
    '''
    output = show_all_vlan_pool(zdcli)
    vlan_pool_list = parse_vlan_pool_info(output)
    return vlan_pool_list

def get_vlan_pool_num(zdcli):
    '''
    Get the numbers of services rules.
    
    '''
    nums = len(get_vlan_pool_list(zdcli))
    return nums

def del_all_vlan_pool(zdcli):
    '''
    Remove all vlan pools.

    Return True, if remove it successfully.
    Return False, if remove if fail.   
    '''
    vlan_pool_list = get_vlan_pool_list(zdcli)
    res = True
    value = ''
    if len(vlan_pool_list) == 0:
        return (res,value)
    for vlan_pool in vlan_pool_list:
        (res, value) = del_vlan_pool(zdcli, vlan_pool)
        if res == False:
            break
    return (res,value)   

def show_all_vlan_pool(zdcli):
    '''      
    ruckus(config)# sh vlan-pool
    VLAN Pool:
      ID:
        1:
          Name = aaa
          Description = sfdsdf
          Option = 2
          VLANSET = 1-10,19

        2:
          Name = 123
          Description =
          Option = 1
          VLANSET = 1


    ruckus(config)#  
    
    '''
    cmd_block = SHOW_VLAN_POOL_ALL
    logging.info( "=======show vlan pool=========")
    res = zdcli.do_show(cmd_block, go_to_cfg = True, timeout = 20)
    logging.info('show vlan pool result:\n%s' % res[0])
    return res[0]

def parse_vlan_pool_info(output):
    '''
    output:
    
    [{'Description': 'sfdsdf', 'Name': 'aaa', 'Option': '2', 'VLANSET': '1-10,19'},
     {'Description': '', 'Name': '123', 'Option': '1', 'VLANSET': '1'}]
    
    '''
    vlan_pool_list = []
    res = output_as_dict.parse(output)
    if not res.get('VLAN Pool'):
        return vlan_pool_list
    else:
        vlan_pool_list += res['VLAN Pool']['ID'].values()
        #raise "VLAN pool info not found."
    
    return vlan_pool_list
    
def cfg_vlan_pool(zdcli, vlan_pool_cfg):
    '''
    ruckus(config)# vlan-pool  abc
    The vlan pool entry 'abc' has been created.
    ruckus(config-vlanpool)# name 123
    The command was executed successfully. To save the changes, type 'end' or 'exit'.
    ruckus(config-vlanpool)# description test123
    The command was executed successfully. To save the changes, type 'end' or 'exit'.
    ruckus(config-vlanpool)# vlan add 1,2,3,4,5
    ruckus(config-vlanpool)# option 1
    The command was executed successfully. To save the changes, type 'end' or 'exit'.
    ruckus(config-vlanpool)# exit
    The vlan pool entry has saved successfully.
    Your changes have been saved.
    ruckus(config)#


    CONFIG_VLAN_POOL = "vlan-pool $name\n"
    EDIT_VLAN_POOL = "vlan-pool $name\n"
    SET_VLAN_POOL_NAME = "name $name\n"
    SET_VLAN_POOL_DESC = "description $description\n"
    SET_VLAN_POOL_ADD_VLAN = "vlan $vlan\n"
    SET_VLAN_POOL_OPTION = "option $option\n"

    '''
    if not vlan_pool_cfg.get('name'):
        return (False, 'No vlan pool name is given')
    else:
        name = vlan_pool_cfg['name']
        cmd_block = CONFIG_VLAN_POOL % name
    
    if vlan_pool_cfg.get('description'):
        cmd_block += SET_VLAN_POOL_DESC % vlan_pool_cfg['description']
    if not vlan_pool_cfg.get('vlan'):
        return (False, 'No vlan is given')
    else:
        cmd_block += SET_VLAN_POOL_ADD_VLAN % vlan_pool_cfg['vlan']
    if vlan_pool_cfg.get('option'):    
        cmd_block += SET_VLAN_POOL_OPTION % vlan_pool_cfg['option']
    else:
        cmd_block += SET_VLAN_POOL_OPTION % random.randint(1,3)
    cmd_block += SAVE_CFG
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'abort', print_out = True)
        return (False, 'vlan pool is not configured successfully.')
    else:
        return verify_vlan_pool(zdcli,vlan_pool_cfg)
    #return (True, 'vlan pool is configured successfully!')
    
def verify_vlan_pool(zdcli,vlan_pool_cfg):
    err_msg = ''
    vlan_pool_info = get_vlan_pool_by_name(zdcli,vlan_pool_cfg['name'])
    if not vlan_pool_info:
        return False,'vlan pool %s is not found.'%vlan_pool_cfg['name']
    try:
        vlan_pool_cfg['vlan'] = get_expected_vlan(vlan_pool_cfg['vlan'])
    except Exception,e:
        return False,e.message  
    if vlan_pool_info['Name'] != vlan_pool_cfg['name']:
        err_msg += 'name different, expected %s,actual %s'%(vlan_pool_cfg['name'],vlan_pool_info['Name'])
    if vlan_pool_info['VLANSET'] != vlan_pool_cfg['vlan']:
        err_msg += 'vlan different, expected %s,actual %s'%(vlan_pool_cfg['vlan'],vlan_pool_info['VLANSET'])
    if vlan_pool_cfg.get('description'):
        if vlan_pool_info['Description'] != vlan_pool_cfg['description']:
            err_msg += 'description different, expected %s,actual %s'%(vlan_pool_cfg['description'],vlan_pool_info['Description'])
    if vlan_pool_cfg.get('option'):
        if vlan_pool_info['Option'] != vlan_pool_cfg['option']:
            err_msg += 'option different, expected %s,actual %s'%(vlan_pool_cfg['option'],vlan_pool_info['Option'])
    if err_msg:
        logging.info(err_msg)
        return False,err_msg
    else:
        return True,'Verify vlan pool %s successfully!'%vlan_pool_cfg['name']

def del_vlan_pool(zdcli, vlan_pool_cfg):
    '''
    ruckus(config)# no vlan-pool 123
    The vlan pool '123' has been deleted.
    ruckus(config)#
    
    DELETE_VLAN_POOL = "no vlan-pool $name\n"
    '''
    if vlan_pool_cfg.get('name'):
        name = vlan_pool_cfg['name']
    else:
        name = vlan_pool_cfg['Name']
    cmd_block = DELETE_VLAN_POOL % name
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    if "The vlan pool '%s' has been deleted."%name not in res['no vlan-pool "%s"'%name][0]:
        return (False, 'vlan pool %s is not deleted.'%name)
    return (True, "vlan pool %s is deleted successfully!"%name)

def cfg_vlan_pools(zdcli,vlan_pool_cfg_list):
    import pdb
    pdb.set_trace()
    fail_num = 0
    for vlan_pool_cfg in vlan_pool_cfg_list:
        res,value = cfg_vlan_pool(zdcli,vlan_pool_cfg)
        if not res:
            fail_num += 1
            msg = 'Configuring vlan pool failed, err info is:%s'%value
            logging.info(msg)

    if fail_num:
        errmsg = '%s vlan pools are not configured successfully.'%fail_num
        logging.info(errmsg)
        return False,errmsg
    else:
        return True, 'All vlan pools are configured successfully!'
    
def cfg_specified_num_of_vlan_pools(zdcli,num):
    vlan_list = range(0,4095)#invalid from 0 to 4094
    try:
        for i in range(0,num):
            name = 'vlan_pool_test_%s'%(i+1)
            description = 'vlan pool test %s'%(i+1)
            vlan = random.sample(vlan_list,16)
            vlan = [str(x) for x in vlan]
            vlan = ','.join(vlan)
            option = str(random.randint(1,3))
            vlan_pool_cfg = dict(name=name,description=description,vlan=vlan,option=option)
            res, value = cfg_vlan_pool(zdcli,vlan_pool_cfg)
            if not res:
                return False,value         
    except Exception,e:
        return False,e.message
    return True,'All vlan pools are created successfully!'
        
def get_vlan_pool_by_name(zdcli,name):        
    vlan_pool_list = get_vlan_pool_list(zdcli)
    for vlan_pool in vlan_pool_list:
        if vlan_pool['Name'] == name:
            return vlan_pool
    return {}

def get_expected_vlan(vlan_str):
    
    '''
    translate all vlan formats
    to 1-9,11,13-15,18
    for example, input is [100,1,3,'5-8','400-398',299,123]
    output is: '1,3,5-8,100,123,299,398-400'
    '''
    tmp_list = parse_vlan_list(vlan_str)
#    pattern_vlan_range = '(\d+)-(\d+)'
#    pattern_vlan_single = '(\d+)'
#    tmp_list = []
#    vlan_list = vlan_list.split(',')
#    for vlan in vlan_list:
#        
#        m = re.search(pattern_vlan_range,str(vlan))
#        if m:
#            start_vlan = int(m.group(1))
#            end_vlan = int(m.group(2))
#            if start_vlan > end_vlan:
#                tmp_list += range(int(end_vlan),int(start_vlan)+1)
#            elif start_vlan == end_vlan:
#                tmp_list.append(int(start_vlan))
#            else:
#                tmp_list += range(int(start_vlan),int(end_vlan)+1)
#        else:
#            n = re.search(pattern_vlan_single,str(vlan))
#            if n:
#                tmp_list.append(int(n.group(1)))
#            else:
#                raise Exception('VLAN format error:%s'%vlan)
#    if not tmp_list:
#        raise Exception('No vlan is given')
    tmp_list.sort()
    tmp = tmp_list[0]
    tmp_str = str(tmp)
    flag=False
    for vlan in tmp_list:
        if vlan == tmp:
            continue
        elif vlan - 1 == tmp and vlan == tmp_list[-1]:
            tmp_str += ('-'+str(vlan))
        elif vlan - 1 == tmp:
            flag = True
            tmp = vlan
        elif flag:
            tmp_str += ('-'+str(tmp)+','+str(vlan))
            tmp = vlan
            flag = False
        else:
            tmp_str += (','+str(vlan))
            tmp = vlan
            
    return tmp_str
          
def edit_vlan_pool(zdcli, vlan_pool_cfg):
    vlan_pool_info = get_vlan_pool_by_name(zdcli,vlan_pool_cfg['name'])
    if not vlan_pool_info:
        return False,'vlan pool %s is not found.'%vlan_pool_cfg['name']
    
    cmd_block = CONFIG_VLAN_POOL % vlan_pool_cfg['name']

    if vlan_pool_cfg.get('new_name'):
        cmd_block += SET_VLAN_POOL_NAME % vlan_pool_cfg['new_name']

    if vlan_pool_cfg.get('new_description'):
        cmd_block += SET_VLAN_POOL_DESC % vlan_pool_cfg['new_description']

    if vlan_pool_cfg.get('new_option'):    
        cmd_block += SET_VLAN_POOL_OPTION % vlan_pool_cfg['new_option']
        
    if vlan_pool_cfg.get('del_vlan'):
        if vlan_pool_cfg['del_vlan'] == 'all':
            cmd_block += SET_VLAN_POOL_DEL_VLAN % deepcopy(vlan_pool_info)['VLANSET']
        else:
            cmd_block += SET_VLAN_POOL_DEL_VLAN % vlan_pool_cfg['del_vlan']

    if vlan_pool_cfg.get('add_vlan'):    
        cmd_block += SET_VLAN_POOL_ADD_VLAN % vlan_pool_cfg['add_vlan']

    cmd_block += SAVE_CFG
    
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'abort', print_out = True)
        return (False, 'vlan pool is not edited successfully.')
    else:
        new_vlan_pool_cfg = {}
        new_vlan_pool_cfg['name'] = vlan_pool_cfg['name']
        if vlan_pool_cfg.get('new_name'):
            new_vlan_pool_cfg['name'] = vlan_pool_cfg['new_name']

        if vlan_pool_cfg.get('add_vlan'):
            add_vlan_list = parse_vlan_list(vlan_pool_cfg['add_vlan'])
        else:
            add_vlan_list = []
            
        if vlan_pool_cfg.get('del_vlan'):
            if vlan_pool_cfg['del_vlan'] == 'all':
                del_vlan_list = parse_vlan_list(deepcopy(vlan_pool_info)['VLANSET'])
            else:
                del_vlan_list = parse_vlan_list(vlan_pool_cfg['del_vlan'])
        else:
            del_vlan_list = []

        vlan_list = parse_vlan_list(deepcopy(vlan_pool_info['VLANSET']))

        new_vlan_pool_cfg['vlan'] = get_expect_vlan_after_edit(zdcli,vlan_list,add_vlan_list,del_vlan_list)

        if vlan_pool_cfg.get('new_description'):
            new_vlan_pool_cfg['description'] = vlan_pool_cfg['new_description']

        if vlan_pool_cfg.get('new_option'):    
            new_vlan_pool_cfg['option'] = vlan_pool_cfg['new_option']

        return verify_vlan_pool(zdcli,new_vlan_pool_cfg)

def get_expect_vlan_after_edit(zdcli,vlan_list,add_vlan_list,del_vlan_list):
    if del_vlan_list:
        for vlan in del_vlan_list:
            vlan_list.remove(vlan)

    if add_vlan_list:
        for vlan in add_vlan_list:
            vlan_list.append(vlan)

    vlan_list_length = len(vlan_list)
    for i in range(0,vlan_list_length):
        vlan_list[i] = str(vlan_list[i])

    return ','.join(vlan_list)
        
def parse_vlan_list(vlan_str):  

    pattern_vlan_range = '(\d+)-(\d+)'
    pattern_vlan_single = '(\d+)'
    tmp_list = []
        
    vlan_list = vlan_str.split(',')
    for vlan in vlan_list:
        
        m = re.search(pattern_vlan_range,str(vlan))
        if m:
            start_vlan = int(m.group(1))
            end_vlan = int(m.group(2))
            if start_vlan > end_vlan:
                tmp_list += range(end_vlan,start_vlan+1)
            elif start_vlan == end_vlan:
                tmp_list.append(start_vlan)
            else:
                tmp_list += range(start_vlan,end_vlan+1)
        else:
            n = re.search(pattern_vlan_single,str(vlan))
            if n:
                tmp_list.append(int(n.group(1)))
            else:
                raise Exception('VLAN format error:%s'%vlan)
    if not tmp_list:
        raise Exception('No vlan in vlan pool.')

    return tmp_list 