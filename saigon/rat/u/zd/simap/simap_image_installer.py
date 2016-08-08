"""
    Description:
      This case is used for install SIMAP image to ZoneDirector, you must setup your tfptserver against your ENV
      and put "install_apimg.sh", SIMAP image to tftpserver root folder.
    Usage:
    tea.py <simap_image_installer key/value pair> ...

    where <simap_image_installer key/value pair> are:
        ip_addr          :   ip address of ZoneDirector CLI
        username         :   username to login ZoneDirector CLI
        password         :   password to login ZoneDirector CLI
        shell_key        :   enter key when login super mode of ZoneDirector.
        tftpserver       :   ip address of tftp server
        model            :   AP mode 
        version          :   SimAP Image version
        do_install_ap    :   True then will perform create AP, according by AP model, version etc, default value: False.
        do_upload_image  :   True then will fetch the image file from tftp server, default value: False.
        do_upload_script :   True then will fetch the script file from tftp server, default value: False.
        do_remove_image  :   True then will remove image file from work_dir, default value: False.
        do_remove_script  :  True then will remove script file from work_dir, default value: False.
    Example:
    tea.py simap_image_installer te_root=u.zd.simap do_install_ap=True do_upload_image=True do_upload_script=True tftpserver=192.168.0.180 version=8.7.0.0.4 model="ss2942 ss7962"    
    tea.py simap_image_installer te_root=u.zd.simap do_install_ap=True version=8.7.0.0.4 model="zf2925 zf9999"
    tea.py simap_image_installer te_root=u.zd.simap do_upload_image=True tftpserver=192.168.0.180
    tea.py simap_image_installer te_root=u.zd.simap do_upload_script=True tftpserver=192.168.0.180
    notes:  
"""

import logging
import re
import time

from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

IMG_FILE = 'rcks_fw.bl7'
SCRIPT_FILE = 'install_apimg.sh'
WORK_DIR = '/tmp'
SHELL_KEY = '!v54!'
TFTP_SERVER = '192.168.0.180'

def restart_ac(zdcli):
    """
    """
    logging.info(zdcli.do_shell_cmd("/etc/ac_init.sh restart", timeout=60))
    
    
def install_simap(zdcli, version, models='zf2925 zf9999'):
    logging.info('begin install simap image[version=%s,models=%s]' % (version, models))
    logging.info((zdcli.do_shell_cmd('sh /usr/tool/%s %s/%s %s %s' % (SCRIPT_FILE, WORK_DIR, IMG_FILE, version, models), timeout=30)))
    
def upload_imge_file(zdcli):
    _upload(zdcli, WORK_DIR, IMG_FILE, TFTP_SERVER)
    if not check_file(zdcli, '%s/%s' % (WORK_DIR, IMG_FILE)):
        raise Exception("file[%s] hasn't found, upload failure" % IMG_FILE)
    logging.info('filesize is [%d]' % resolve_file_size(zdcli, '%s/%s' % (WORK_DIR, IMG_FILE)))
    
def remove_image_file(zdcli):
    _rmfile(zdcli, WORK_DIR, IMG_FILE)
    if check_file(zdcli, '%s/%s' % (WORK_DIR, IMG_FILE)):
        raise Exception("file[%s] has't removed correctly" % IMG_FILE)
        
def check_file(zdcli, filename='/tmp/rcks_fw.bl7'):
    existed = True
    res = zdcli.do_shell_cmd('ls -l %s' % filename, timeout=10)
    logging.info(res)
    expr = "^ls: %s: No such file or directory$" % filename
    m = re.match(expr, res)
    if m  : existed = False 
    return existed
    
def resolve_file_size(zdcli, filename='/tmp/rcks_fw.bl7'):
    
    try:
        
        res = zdcli.do_shell_cmd('ls -l %s' % filename, timeout=10)
        logging.info(res)
        expr = "^[-rwx]+[\s]+1[\s]+[\S]+[\s]+[\S]+[\s]+(\d+)[\s]+.*%s$" % filename
        m = re.match(expr, res)
        if m  :
            size = int(m.group(1))
            logging.info('size:%s' % size)
            if size <= 0 :
                raise Exception('The file[%s] is an empty file, please verify' % filename)
            return size
        
        raise Exception('Haven\'t found the file[%s], please verify your upload process' % filename)
    
    finally:
        pass
        
def _upload(zdcli, dir, filename, ipaddr, timeout=60, chmod=False):
    zdcli.do_cmd(SHELL_KEY)    
    zdcli.do_cmd('cd %s' % dir, timeout=10)    
    time.sleep(2)
    logging.info('pwd=[%s]' % zdcli.do_cmd('pwd', timeout=10))
    zdcli.do_cmd('tftp -g -r %s %s' % (filename, ipaddr), timeout=timeout)
    t0 = time.time()
    while True :
        res = zdcli.do_cmd('ls', timeout=10)
        if re.findall('%s' % filename, res) :
            logging.info('upload file %s successfully!' % filename)
            if chmod :
                zdcli.do_cmd('chmod 777 %s' % filename)
            break
        
        elif time.time() - t0 > 30 :
            raise Exception('upload file %s failure!' % filename)
        
        else:
            time.sleep(5)
            
    zdcli.re_login()

def _rmfile(zdcli, dir, filename, timeout=60):
    zdcli.do_cmd(SHELL_KEY)
    zdcli.do_cmd('cd %s' % dir, timeout=10)
    time.sleep(2)
    logging.info('pwd=[%s]' % zdcli.do_cmd('pwd', timeout=10))
    zdcli.do_cmd('rm -r %s' % filename, timeout=timeout)
    res = zdcli.do_cmd('ls', timeout=10)
    if not re.findall('%s' % filename, res) :
        logging.info('remove file %s successfully!' % filename)
        
    else:
        logging.warn('remove file %s failure!' % filename)

    zdcli.re_login()
    
def update_keywords(s, d):
    for k, v in s.items():
        if d.has_key(k):
            d[k] = v            
        
def create_zd_cli(**kwargs):
    #configuration to ZoneDirector
    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin',
             'shell_key':'!v54!'}
    update_keywords(kwargs, zdcfg)
    
    return ZoneDirectorCLI(zdcfg)

def install_facade(zdcli, **kwargs):
    
    global SHELL_KEY, TFTP_SERVER
    if kwargs.has_key('shell_key'):
        SHELL_KEY = kwargs['shell_key']
        
    if kwargs.has_key('tftpserver'):
        TFTP_SERVER = kwargs['tftpserver']
        
    if check_file(zdcli, filename='%s/%s' % (WORK_DIR, IMG_FILE)):        
        install_simap(zdcli, kwargs['version'], kwargs['model'])
        restart_ac(zdcli)
        
    else:
        raise Exception("image file[%s] has found in the %s folder" % (IMG_FILE, WORK_DIR))


def install(zdcli, **kwargs):
    global SHELL_KEY, TFTP_SERVER
    mycfg = dict(shell_key="!v54!",
                  tftpserver='192.168.0.180',
                  model="ss2942",
                  version='8.7.0.0.4',
                  do_install_ap=False,
                  do_upload_image=False,
                  do_upload_script=False,
                  do_remove_image=False,
                  do_remove_script=False,
                  debug=False
                )
    mycfg.update(kwargs)  
    SHELL_KEY = zdcli.conf['shell_key']
    mycfg['shell_key'] = SHELL_KEY
    TFTP_SERVER = mycfg['tftpserver']
    
    if mycfg['do_upload_image']:
        upload_imge_file(zdcli)
                
    if mycfg['do_install_ap']:
        install_facade(zdcli, **mycfg)
        
    if mycfg['do_remove_image']:
        remove_image_file(zdcli)
        

def usage(zdcli, **kwargs):
    """
    Usage:
    tea.py <simap_image_installer key/value pair> ...
    
    where <simap_image_installer key/value pair> are:
        ip_addr          :   ip address of ZoneDirector CLI
        username         :   username to login ZoneDirector CLI
        password         :   password to login ZoneDirector CLI
        shell_key        :   enter key when login super mode of ZoneDirector.
        tftpserver       :   ip address of tftp server
        model            :   AP mode 
        version          :   SimAP Image version
        do_install_ap    :   True then will perform create AP, according by AP model, version etc, default value: False.
        do_upload_image  :   True then will fetch the image file from tftp server, default value: False.
        do_upload_script :   True then will fetch the script file from tftp server, default value: False.
        do_remove_image  :   True then will remove image file from work_dir, default value: False.
        do_remove_script  :  True then will remove script file from work_dir, default value: False.
    Example:
    tea.py simap_image_installer te_root=u.zd.simap do_install_ap=True do_upload_image=True do_upload_script=True tftpserver=192.168.0.180 version=8.7.0.0.4 model="ss2942"    
    tea.py simap_image_installer te_root=u.zd.simap do_install_ap=True version=8.7.0.0.4 model="zf2925 zf9999"
    tea.py simap_image_installer te_root=u.zd.simap do_upload_image=True tftpserver=192.168.0.180
    tea.py simap_image_installer te_root=u.zd.simap do_upload_script=True tftpserver=192.168.0.180
    notes:  
        
    """
def main(**kwargs):
    mycfg = dict(shell_key="!v54!",
                  tftpserver='192.168.0.180',
                  model="ss2942",
                  version='8.7.0.0.4',
                  do_install_ap=False,
                  do_upload_image=False,
                  do_upload_script=False,
                  do_remove_image=False,
                  do_remove_script=False,
                  debug=False
                )
    mycfg.update(kwargs)
    
    if mycfg['debug']:
        import pdb
        pdb.set_trace()
        
    global SHELL_KEY, TFTP_SERVER
    
    SHELL_KEY = mycfg['shell_key']
    TFTP_SERVER = mycfg['tftpserver']
    
    zdcli = create_zd_cli(**mycfg)
    if mycfg['do_upload_image']:
        upload_imge_file(zdcli)
                
    if mycfg['do_install_ap']:
        install_facade(zdcli, **mycfg)
        
    if mycfg['do_remove_image']:
        remove_image_file(zdcli)
                
    zdcli.__del__()
