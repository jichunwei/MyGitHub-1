'''
this module is used to rename the file in a ZD ,and download the renamed file in ZD to pc
by west.li
'''

import logging
import time
import os


#1.enter the specified folder
#2.copy the file which you want to download and add a prefix(source or target specified in zd_type) in the file name
#3.put the copied file to tftp server
#4.remove the copied file 
#5.return value:0-success 1-file exist but download failed 2-the file not exist
#parameters:zd_type- 'source' or 'target',if you don't care the data sync direction,you can give any character 

TYPE_SOURCE_ZD  = "source"
TYPE_TARGET_ZD = "target"
def download_file(zdcli,dir,filename,ipaddr,zd_type,timeout=60):
    
    cnt = 5
    while cnt:
        try:      
            zdcli.do_cmd(zdcli.login_shell_key)
            break
        except Exception, e:
            logging.debug('download file do cmd error [%s],login again' %e.message)
            zdcli.login()
        cnt-=1
        time.sleep(5)
        if not cnt:
            raise e

    filelist = []
    if type(filename) is not list:
        filelist.append(filename)
    else:
        filelist = filename
    
    for file in filelist:
        #1.enter the specified folder
        zdcli.do_cmd('cd %s' % dir, timeout=10)   
        time.sleep(2)
#        logging.info('current path is [%s]' % zdcli.do_cmd('pwd', timeout=10))
        
        #2.copy the file which you want to download and add a prefix(source or target) in the file name
        cpfilename=zd_type+'-'+file
        res = zdcli.do_cmd('cp %s /tmp/%s' % (file,cpfilename)) 
        if res.find('No such file or directory') >= 0:
            logging.info('%s not exist in the director!' % file)
            zdcli.re_login()
            return 2, file
        
        #3.put the copied file to tftp server
        zdcli.do_cmd('cd /tmp', timeout=10)
        res = zdcli.do_cmd('tftp -p -r %s %s' % (cpfilename, ipaddr), timeout=timeout)
        if res.find('timeout') >= 0 or res.find('error') >= 0:
            logging.info('%s put to tftp server failed!' % file)
            #4.remove the copied file 
            zdcli.do_cmd('rm %s' % cpfilename)
            zdcli.re_login()
            return 1, file
        
        #4.remove the copied file 
        logging.info('%s is put to tftp successfully!' % file)
        zdcli.do_cmd('rm %s' % cpfilename)
    
    zdcli.re_login()
    return 0, filelist


