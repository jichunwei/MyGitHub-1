'''
this module is used to download the file in 2 ZD and compare them
by west.li
'''

import logging
import time
import os
from RuckusAutoTest.components.lib.zdcli import download_file_from_zd_to_pc as downloadfile
from RuckusAutoTest.components.lib.zdcli import compare_xml_file_on_pc as com_pc_xml


#Constant definition
ADD_ACTION = "Add"
DEL_ACTION = "Del"
MOD_ACTION = "Mod"

#parameter:zdcli_source,zdcli_target-the two zdcli of the zd you want to compare file
#zdcli_source-the source side of the data sync,zdcli_target-the target side of the data sync
#dir_zd_source,dir_zd_target-the location of the file in ZD,source and target also means the data sync direction;
#action-Del,Add,Mod;
#dir_pc-where you put the download file in your pc;
#filename-name of the file you want to compare
#recursive- weather this function is recursive called,user need not to care about this
#return value True,False
def compare_file(zdcli_source,zdcli_target,dir_zd_source,dir_zd_target,filename,dir_pc,action,recursive=False):
    tftp_server={'addr':'192.168.0.10'}
    d_source, file=downloadfile.download_file(zdcli_source,dir_zd_source,filename,tftp_server['addr'],"source")
    d_target, file=downloadfile.download_file(zdcli_target,dir_zd_target,filename,tftp_server['addr'],"target")
    source_file_name="source-"+filename
    target_file_name="target-"+filename
    
    if((d_source==1)or(d_target==1)):
        raise Exception('download file failed[%s]'% filename)
    
    if(((d_source,d_target)==(0,2))or((d_source,d_target)==(2,0))):
        if action != 'Del':
            if d_target == 2:
                zd_ip = zdcli_target.ip_addr
            elif zdcli_target == 2:
                zd_ip = zdcli_source.ip_addr
            msg = 'action is not \'Del\' but zd[%s] have %s,another do not have,' % (zd_ip,filename)
            logging.info(msg)
            return False,msg
        else:
            if not recursive:
                return _only_one_zd_has_file_process(d_source,d_target,dir_pc,zdcli_source,zdcli_target,dir_zd_source,dir_zd_target,filename)
            else:
                return False,'%s is exist only in one ZD,and not the same with default configuration' %  filename
    
    if((d_source,d_target)==(2,2)):
        if (action == 'Del'):
            msg = 'action is \'Del\' and file [%s] not exist,OK,' % filename
            logging.info(msg)
            return True,msg
        else:
            msg = 'the user did not delete [%s],but it disappear,' % filename
            logging.error(msg)
            return False,msg
        
    if ((d_source,d_target)==(0,0)):
        logging.info('both ZD have file [%s],begin compare:' % filename)
        return com_pc_xml.compare_xml_file_on_pc(dir_pc,source_file_name,dir_pc,target_file_name,filename)
    
    raise Exception('download_file return wrong value : %d,%d' % (d_source,d_target))    
        

#step:
#1.check if the line number of the exist file more then 1
#2.if the line number>1 check if the file is the same to the default configuration
def _only_one_zd_has_file_process(source_result,target_result,dir_in_pc,source_zdcli,target_zdcli,source_zd_dir,target_zd_dir,filename):
    zd_default_cfg_dir = '//etc//airespider-default'
    source_filename = 'source-'+filename
    target_filename = 'target-'+filename   
    source_file_path = os.path.join(dir_in_pc,source_filename)
    target_file_path = os.path.join(dir_in_pc,target_filename)
    
    if (target_result == 0):
        path = target_file_path
        zdcli = target_zdcli
        zd_dir = target_zd_dir
    else:
        if (source_result == 0):
            path = source_file_path
            zdcli = source_zdcli
            zd_dir = source_zd_dir
        else:
            msg='wrong parameter when call _only_one_zd_has_file_process source_result:%d,target_result:%d,'%(source_result,target_result)
            return False,msg
        
    lenNum = len(open(path,'r').readlines())
    
    if lenNum>1:
        result,msg = compare_file(zdcli,zdcli,zd_dir,zd_default_cfg_dir,filename,dir_in_pc,'Mod',True)
        if result:
            return True,'%s is exist only in one zd,but it is the same with default config' % filename
        else:
            return False,'%s is exist only in one ZD,and not the same with default configuration' %  filename
    
    else:
        msg="one ZD don't has %s,and %s in another ZD has only 1 line," % (filename,filename)
        return True,msg

     
