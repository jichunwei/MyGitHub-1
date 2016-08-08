'''
Created on Jan 13, 2011

purpose:

This tea program is modified from a batch file to remotely copy files

from one test engine to others.

1. able to copy whole CLxxxxx folder to others

2. able to move FM user information under te_information

@author: webber.lin
'''



import logging
import time, subprocess, pdb

def _create_scale_list(prefix='Scale-',start=8,end=27):
    ''' 
    this function is to crate a scale test engine list.
    OUTPUT:
    ['Scale-08', 'Scale-09', 'Scale-10', 'Scale-11', 
    'Scale-12', 'Scale-13', 'Scale-14', 'Scale-15', 
    'Scale-16', 'Scale-17', 'Scale-18', 'Scale-19',
     'Scale-20', 'Scale-21', 'Scale-22', 'Scale-23',
      'Scale-24', 'Scale-25', 'Scale-26', 'Scale-27']
    '''
    return ['%s%02d' % (prefix,i) for i in range(start,end+1)]

def _create_target_folder(target,folder='saigon_CL63699'):
    ''' 
        this function only support folders under FM_saigon
        example: target = 'Scale-08'
                 folder = 'saigon_CL63699'
        OUTPUT: '\\\\Scale-08\\FM_saigon\\saigon_CL63699\\'
    '''
    return '\\\\%s\\FM_saigon\\%s\\' % (target,folder)

def _create_cmd_pack_list(folder='saigon_CL63699',prefix='Scale-',start=8,end=27):
    '''
    this function is to crate a command pack list to be executed on test engines
    OUTPUT:
    this function will create a list of list as below:
    [[],[],....,['rcp', '-r', '\\\\Scale-01\\FM_saigon\\saigon_CL63699\\*', 
    '\\\\Scale-27\\FM_saigon\\saigon_CL63699\\']]
    '''
    #return ['%s' % _create_target_folder(target=i) for i in _create_scale_list()]
    cmd_pack_list =[]
    for i in _create_scale_list():
        cmd_pack=['rcp','-r',r'\\Scale-01\FM_saigon\saigon_CL63699\*',]
        temp = cmd_pack
        temp.append(_create_target_folder(target=i))
        cmd_pack_list.append(temp)
    return cmd_pack_list
    
def execute_cmd_on_TE(cmd_pack_list = _create_cmd_pack_list()):
    for cmd_pack in cmd_pack_list:
        subprocess.call(cmd_pack)

def do_config(cfg):
    program_config = dict(
                          cmd_pack_list= _create_cmd_pack_list(),
    )
    program_config.update(cfg)
    logging.info("----------------------------------------------------")
    execute_cmd_on_TE(program_config['cmd_pack_list'])
    logging.info("----------------------------------------------------")
    
    return program_config


def do_test(cfg):
    
    #lib.fm.user.add(cfg['fm'], cfg['usr_cfg']) #single user example
    program_config = dict(
        
    )
    program_config.update(cfg)
    pass
    
def do_clean_up(cfg):
    pass

def main(**kwa):
    default_cfg = dict(
        delete_user='no',fm_ip_addr='192.168.30.252',fm_version='9',view_name = 'ruckus_view', te_id='1',fm_list=[]
    )
    logging.info("start tea program")    
    default_cfg.update(kwa)
    tcfg = do_config(kwa)
    do_test(tcfg)
    do_clean_up(tcfg)
    
