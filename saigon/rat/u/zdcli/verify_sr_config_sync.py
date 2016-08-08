'''
Created on 2012-11-16
@author: West

Description:
download the xml file in the two zds and compare the configuration

procedure
1.enter zd shell, get configuration file list,compress these files to one .tar.gz file
2.get the file list need to be sync in the two zds
3.from the two zd list got in step 2, get 3 file list
    file list only in zd1
    file list only in zd2
    file list in both zds
4.download the .tar.gz file in the two zd, remove the file after download
5.decompress the .tar.gz file
6.compare the files in the two zds
7.if error happens in step 4,backup the configuration files
8.wait for a while and repeat 1-8
'''

import logging
import os
import shutil
import time
from tarfile import TarFile

from RuckusAutoTest.components import create_zd_shell_by_ip_addr
from RuckusAutoTest.components.lib.zdcli.compare_xml_file_on_pc_sr import compare_xml_file_on_pc as cmp_file
from RuckusAutoTest.common.lib_List import list_minus_list
from RuckusAutoTest.components.lib.zdcli.download_file_from_zd_by_shell import download_file

default_cfg = dict(zd_ip_addr1 = '192.168.0.2', 
                   username1 = 'admin', 
                   password1 = 'admin', 
                   shell_key1 = '!v54!',
                   protocol1='SSH',
                   
                   zd_ip_addr2 = '192.168.0.3',
                   username2 = 'admin', 
                   password2 = 'admin', 
                   shell_key2 = '!v54!',
                   protocol2='SSH',
                   
                   zd_dir='/etc/airespider/',
                   pc_dir='C:\\sr_sync\\xml_tar_file\\',
                   
                   zd1_tar_name = 'xml_file_1.tar.gz',
                   zd2_tar_name = 'xml_file_2.tar.gz',
                   zd1_file_dir = 'C:\\sr_sync\\zd1',
                   zd2_file_dir = 'C:\\sr_sync\\zd2',
                   backup_dir = 'C:\\sr_sync\\backup',
                   
                   wait_time=30,#minutes
                   pc_ip_addr = '192.168.0.10'
                   )

total_sync_file_list=['mgmtipacl-list.xml','mgmtipv6acl-list.xml','mesh-list.xml',
                       'acl-list.xml','policy-list.xml','policy6-list.xml',
                       'authsvr-list.xml','hotspot-list.xml','wlansvc-list.xml',
                       'wlangroup-list.xml','map-list.xml','apgroup-list.xml',
                       'ap-list.xml','dcert-list.xml','dpsk-list.xml',
                       'guest-list.xml','role-list.xml','user-list.xml']
part_sync_file_list=['system.xml']
all_file_need_check=total_sync_file_list+part_sync_file_list
    
def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    zd_shell1=create_zd_shell_by_ip_addr(
                                            ip_addr = _cfg['zd_ip_addr1'],
                                            username = _cfg['username1'],
                                            password = _cfg['password1'],
                                            shell_key = _cfg['shell_key1'],
                                            protocol = _cfg['protocol1']
                                        )
    
    zd_shell2=create_zd_shell_by_ip_addr(
                                            ip_addr = _cfg['zd_ip_addr2'],
                                            username = _cfg['username2'],
                                            password = _cfg['password2'],
                                            shell_key = _cfg['shell_key2'],
                                            protocol = _cfg['protocol2']
                                        )
    
    return (zd_shell1,zd_shell2)


def do_test(zd_shell1,zd_shell2):
    while True:
        #get configuration file list and and compress the files in one .tar.gz file
        xml_file_list_1 = _get_file_list_in_zd(zd_shell1,default_cfg['zd_dir'],default_cfg['zd1_tar_name'])
        xml_file_list_2 = _get_file_list_in_zd(zd_shell2,default_cfg['zd_dir'],default_cfg['zd2_tar_name'])
        
        list_1,list_2 = _get_file_list_need_check(xml_file_list_1,xml_file_list_2)
        
        only_zd1_list=list_minus_list(list_1,list_2) 
        only_zd2_list=list_minus_list(list_2,list_1)
        both_zd_list =list_minus_list(list_1,only_zd1_list)
        
        logging.info('there are %d files in both zds,they are %s'%(len(both_zd_list),both_zd_list))  
        logging.info('there are %d files only in zd1,they are %s'%(len(only_zd1_list),only_zd1_list)) 
        logging.info('there are %d files only in zd2,they are %s'%(len(only_zd2_list),only_zd2_list)) 
        
        #download the .tar.gz file from zds
        logging.info("begin download file from zd1...")
        if 0!=download_file(zd_shell1,default_cfg['zd1_tar_name'],ipaddr=default_cfg['pc_ip_addr']):
            msg = 'download file %s from zd failed'%default_cfg['zd1_tar_name']
            logging.error(msg)
            continue
        logging.info("begin download file from zd2...")
        if 0!=download_file(zd_shell2,default_cfg['zd2_tar_name'],ipaddr=default_cfg['pc_ip_addr']):
            msg = 'download file %s from zd failed'%default_cfg['zd2_tar_name']
            logging.error(msg)
            continue
        logging.info("get file from two zds successfully")
        
        logging.info('remove tar file in zds')
        if not _rm_file_in_zd(zd_shell1,default_cfg['zd1_tar_name']):
            logging.error('remove zd1 tar file failed')
        if not _rm_file_in_zd(zd_shell2,default_cfg['zd2_tar_name']):
            logging.error('remove zd2 tar file failed')
        logging.info('remove tar file in zds successfully')
        
        #decompress the .tar.gz files in the two zds
        logging.info("begin decompress .tar.gz file got from zd1")
        zd1_file=os.path.join(default_cfg['pc_dir'],default_cfg['zd1_tar_name'])
        zd2_file=os.path.join(default_cfg['pc_dir'],default_cfg['zd2_tar_name'])
        
#        import pdb
#        pdb.set_trace()
        _decompress_file(zd1_file,list_1,default_cfg['zd1_file_dir'])
        _decompress_file(zd2_file,list_2,default_cfg['zd2_file_dir'])
        
        #begin compare the files one by one
        err_msg=''
        logging.info('begin check the files only in zd1')
        for file_name in only_zd1_list:
            res,msg=_only_one_zd_has_file_process(default_cfg['zd1_file_dir'],file_name,'zd1')
            logging.info(msg)
            if not res:
                err_msg += msg
        if err_msg:
            err_msg+='\n'
                
        logging.info('begin check the files only in zd2')
        for file_name in only_zd2_list:
            res,msg=_only_one_zd_has_file_process(default_cfg['zd2_file_dir'],file_name,'zd2')
            logging.info(msg)
            if not res:
                err_msg += msg
        if err_msg:
            err_msg+='\n'
    
        logging.info('begin compare the files exist in both zds')
        for file_name in both_zd_list:
            logging.info('begin compare the file %s'%file_name)
            res,msg=cmp_file(default_cfg['zd1_file_dir'],default_cfg['zd2_file_dir'],file_name)
            logging.info(msg)
            if not res:
                err_msg += msg
        
        if err_msg:
            logging.error("error occur when compare configuration in two zds")
            logging.error(err_msg)
            dirs=[default_cfg['zd1_file_dir'],default_cfg['zd2_file_dir']]
            res = _backup_dirs(dirs)
            logging.error('the configuration files was backup at [%s],please check'%res)
        else:
            logging.info('sr sync check successfully')

        logging.info('wait %s minutes and continue'%default_cfg['wait_time'])    
        _wait(default_cfg['wait_time']*60)
        
    return ("PASS", "this procedure will always run,and will not return ")

def do_clean_up():
    pass

def _get_file_list_in_zd(zd_shell,dir,tar_file_name):
    zd_shell.do_cmd('cd %s'%dir)
    cmd = "ls |grep 'xml' |grep -v '.bak.'" 
    res = zd_shell.do_cmd(cmd)
    res = res.strip()
    xml_file_list = res.split()
    cmd = "tar -cvzf ./%s ./*.xml"%tar_file_name
    zd_shell.do_cmd(cmd)
    return xml_file_list
        
        
def _get_file_list_need_check(file_list1,file_list2):
    
    logging.info('file in first zd:%s'%file_list1)
    logging.info('file in second zd:%s'%file_list2)
    
    logging.info('begin to get file list need check in first zd')
    not_check_file_list=list_minus_list(file_list1,all_file_need_check)
    logging.info('get file list not need to check %s'%not_check_file_list)
    check_file_list1=list_minus_list(file_list1,not_check_file_list)
    logging.info('get file list need to check in first zd %s'%check_file_list1)
    
    logging.info('begin to get file list need check in second zd')
    not_check_file_list=list_minus_list(file_list2,all_file_need_check)
    logging.info('get file list not need to check %s'%not_check_file_list)
    check_file_list2=list_minus_list(file_list2,not_check_file_list)
    logging.info('get file list need to check in second zd %s'%check_file_list2)
    
    return check_file_list1,check_file_list2


def _rm_file_in_zd(zd_shell,file_name,dir=''):
    if dir:
        zd_shell.do_cmd('cd %s'%dir)
    cmd = "rm %s"%file_name 
    zd_shell.do_cmd(cmd)
    res=zd_shell.do_cmd('ls')
    if file_name in res:
        logging.info('file remove failed')
        return False
    return True
    

def _decompress_file(file_name,target_file_list,target_dir):
    tar_file = TarFile.open(file_name, 'r:gz')
    for file in target_file_list:
        name='./'+file
        tar_file.extract(name,target_dir)

 
def _only_one_zd_has_file_process(dir_in_pc,filename,zd):
     
    file_path = os.path.join(dir_in_pc,filename)
    lenNum = len(open(file_path,'r').readlines())
    
    if lenNum>1:
        return False,'%s has file and more than 1 line,but other zd no this file %s'%(zd,filename)
    else:
        return True,''

def _backup_dirs(src_dirs):
    target_dir=time.ctime().replace(' ','_').replace(':','_')
    target_path = os.path.join(default_cfg['backup_dir'],target_dir)
    os.mkdir(target_path)
    for src_dir in src_dirs:
        str=src_dir.split('\\')
        if str[-1]:
            name = str[-1]
        else:
            name = str[-2]
       
        target_whole_path = os.path.join(target_path,name)
        shutil.copytree (src_dir, target_whole_path)
    
    return target_path

def _wait(wait_time):
    t0=time.time()
    t=time.time()
    while t-t0<wait_time:
        past_time = t-t0
        left_time = wait_time-past_time
        logging.info('have wait %s seconds,%s seconds(about %s minutes) left' % (past_time,left_time,left_time/60))
        time.sleep(60)
        t=time.time()
    logging.info('have wait %s seconds'%wait_time)
    
def main(**kwargs):
    shell1,shell2 = do_config(kwargs)
    res = None  
    try:
        res = do_test(shell1,shell2)
    finally:
        do_clean_up()
    return res

