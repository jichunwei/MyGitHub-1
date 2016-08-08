'''
this module is used to download file in ZD to pc by zd shell
by west.li
'''

import logging
import time

'''
return value:0-success 1-file exist but download failed 2-the file not exist
'''


def download_file(zdshell,filename,dir='/etc/airespider/',ipaddr='192.168.0.10',timeout=60):
    

    #1.enter the specified folder
    zdshell.do_cmd('cd %s' % dir, timeout=10)   
    time.sleep(2)
    logging.info('current path is [%s]' % zdshell.do_cmd('pwd', timeout=10))
    
    #3.put the copied file to tftp server
    res = zdshell.do_cmd('tftp -p -r %s %s' % (filename, ipaddr), timeout=timeout)
    if res.find('timeout') >= 0 or res.find('error') >= 0:
        logging.info('%s put to tftp server failed!' % filename)
        return 1
    elif res.find('No such file or directory') >= 0 :
        logging.info('%s not found in the dir %s!' %(filename,dir))
        #4.remove the copied file 
        return 2
    
    #4.remove the copied file 
    logging.info('%s is put to tftp successfully!' % filename)
    return 0


