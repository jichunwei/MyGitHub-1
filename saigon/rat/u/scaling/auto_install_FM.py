'''
Created on Aug 11, 2010
updated Sep 13, 2010

@author: webber.lin

Purpose: To install FM new build automatically and 
         achieve database as tar.gz file for database restoring.

Needs: need to install a new package "pexpect-2.3.tar.gz"

1. Need to uninstall FM server first

2. create a folder and mount FM iso on it
2.1 create a folder under /tmp/
2.2 mount fm iso under this folder

3. Install FM server with pexpect package

4. Backup the database as tar file

5. Need to be root to run this automation


example:
need to copy FM iso and this script to /tmp
[root@localhost tmp]# python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso backup
[root@localhost tmp]# python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso restore
[root@localhost tmp]# python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso install
[root@localhost tmp]# python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso uninstall

'''


import os
import sys
import re
import pexpect
import time
import glob
import logging

#logging format
logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

#from RuckusAutoTest.common.Ratutils import send_mail
def goToOpt():
    try:
        os.chdir('/opt/FlexMaster')
        logging.info('Done: go to opt directory')
    except:
        logging.error('Failed: go to opt directory')
        
def uninstallFM():
    
    #no need to change dir
    logging.info("Start to uninstall FM Server")
    
    try:
        os.system("./shutdown.sh")
        logging.info("shutdown FM server")
        try:
            os.system("./uninstall.sh")
            logging.info("Uninstall successfully!")
        except:
            logging.error("cannot uninstall FM Server")
    except:
        logging.error("shutdown FM failed")
def _getIsoVersion(isoFileName):
    ''' Return Fm version and make it to be part of folder name
        example: FM_9.0.0.0.147.20100809_0001.iso
        version will be 147 and folderName will be iso147
    '''
    reg = re.compile(r"0.0.0.(?P<version>\d+).") 
    result = reg.search(isoFileName)
    return result.group('version')

def createTempDir(isoFileName):
    ''' create a directory under /tmp/ for mounting a FM iso '''
    version = _getIsoVersion(isoFileName)
    tmpDir='/tmp/iso%s' % version
    try:
        os.mkdir(tmpDir)
        logging.info(" %s is created" %tmpDir)
        
    except:
        pass
        logging.error(" %s is already existed on FM Server" % tmpDir)
    return tmpDir #return folder name and be able to use on removeDir function
def removeTempDir(dirName):
    try:
        os.rmdir(dirName)
    except:
        logging.error("%s directory cannot be removed")
    
def umountTempDir(dirName):
    try:
        os.system('umount -a %s' % dirName)
    except:
        logging.error("%s directory cannot be unmounted")
    
def mountIso(sourceIso):
    ''' 
        source iso = /tmp/xxxxx.iso -> need to be full path
        target folder = /tmp/isoXXX   
    '''
    reg = re.compile("/\w+(?P<iso>.*.iso)$")
    result = reg.search(sourceIso)
    iso = result.group('iso')
    tmp_dir = createTempDir(iso)
    logging.info( "Mount %s on %s" % (iso, tmp_dir))
    command='mount %s -o loop %s' % (sourceIso,tmp_dir)
    logging.info("command: %s" % command)
    try:
        os.system(command) #success returns 0
        logging.info(" Mount iso on %s successfully" % tmp_dir)
        return tmp_dir
    except:
        logging.error(" mount %s failed or iso is already mounted" % iso)
    
        

def installFM(sourceIso):
    ''' 
        install FM:
        1. go to /tmp/xxx/
    '''
    #import pdb
    #pdb.set_trace()
    #no need to shutdown fm
    
    tmpDir = mountIso(sourceIso)
    #tmpDir = '/tmp/iso126'
    fout = file('/tmp/mylog.txt','w')
    
    try:
        os.chdir(str(tmpDir)) # tmpDir = /tmp/isoXXX
        logging.info('Done: change to directory %s' % str(tmpDir))
    except:
        logging.error('Failed: change directory: %s' % str(tmpDir))
    
    try:
        logging.info('Steps: There are 15 steps to install FM server')
        logging.info('FM installation will be started in 5 seconds')
        time.sleep(5)
        process=pexpect.spawn('./install.sh')
        process.logfile = sys.stdout
        try:
            process.expect('FlexMaster]:',timeout=30)
            process.send('\n')
            logging.info('1. done: %s' % process.after)
        except:
            logging.info('1. failed: %s' % process.after)
        try:
            process.expect('.com',timeout=10)
            process.sendline('ruckus.com')
            logging.info('2. done: %s ruckus.com' % process.after)
        except:
            logging.error('2. failed: %s ruckus.com' % process.after)
        try:
            process.expect('[pP]assword:')
            process.sendline('admin')
            logging.info( '3. done: %s admin' % process.after)
        except:
            logging.error('3. failed: %s admin' % process.after)
        try:
            process.expect('[pP]assword:')
            process.sendline('admin')
            logging.info( '4. done: %s admin' % process.after)
        except:
            logging.error('4. failed: %s admin' % process.after)
        try:
            process.expect('[pP]assword:')
            process.sendline('admin')
            logging.info('5. done: %s admin' % process.after)
        except:
            logging.error('5. failed: %s admin' % process.after)
        try:
            process.expect('[pP]assword:')
            process.sendline('admin')
            logging.info('6. done: %s admin' % process.after)
        except:
            logging.error('6. failed: %s admin' % process.after)
        try:
            process.expect('443]:')
            process.send('\n')
            logging.info('7. done: %s Enter' % process.after)
        except:
            logging.error('7. failed: %s ' % process.after)
        try:
            process.expect('host:')
            process.send('\n')
            logging.info('8.done: %s Enter' % process.after)
        except:
            logging.error('8. failed: %s ' % process.after)
        try:
            process.expect('25]')
            process.send('\n')
            logging.info('9. done: %s Enter' % process.after)
        except:
            logging.error('9. failed: %s ' % process.after)
        try:
            process.expect('to:')
            process.send('\n') # type in email
            logging.info('10. done: %s Enter' % process.after)
        except:
            logging.error('. failed: %s ' % process.after)
        try:
            process.expect('continue...',timeout=3)
            process.send('\n')
            logging.info('11. done: "%s Enter' % process.after)
        except:
            logging.error('11. failed: %s ' % process.after)
        try:
            process.expect('More--',timeout=50)
            logging.info('12.1 done: skip license check, so press q')
            process.send('q')
            logging.info('12.2 done: %s q' % (process.after) )
        except:
            logging.error('12. failed: %s ' % process.after)
        try:
            process.expect('no]',timeout=20)
            process.sendline('y')
            logging.info('13. done: %s y' % process.after)
            
        except:
            logging.error('13. failed: %s ' % process.after)
        
        
        
        try:
            #process.interact('')
            process.expect(pexpect.EOF, timeout=None)
            process.sendline('')
            logging.debug("Monitor: %s" % process.before)
            logging.debug("IsAlive: %s" % process.isalive())
        
            #this is taking long time to be completed
            #FM server takes long time to complete installation
            #after installation, it will automatically backup database.
            
            logging.info("14.Wait 10 minutes til FM server ")
            #time.sleep(600) # wait until FM server Ready!
            
            process.logfile = sys.stdout
            process.close()
            logging.info("14. FM server installation is finished and successfully")
            time.sleep(35)
            logging.info("15. FM server is up and running!!")
        except:
            logging.debug("Monitor: %s" % process.before)
            logging.error('Failed: unable to wait until FM up and running')
                
        #process.send('\n')       
        
        
#        index = process.expect(['FlexMaster]:',\
#                            '.com ):',\
#                            'Password:',\
#                            'password:',\
#                            'Https port[443]:',\
#                            'SMTP host:',\
#                            'SMTP port[25]',\
#                            'Mail to:',\
#                            'continue...',\
#                            'More--',\
#                            '[yes or no]'],timeout=30)
#        if index in [0,4,5,6,8]:
#            print "[info]Press Enter"
#            process.send('\n')# "Enter and keep default /opt/FlexMaster"
#            print process.after
#        elif index == 1:
#            print "[info]Type in domain name: ruckus.com"
#            process.sendline('ruckus.com') #domain name
#            print process.after
#        elif index == [2,3]:
#            print "[info]PassWrod: admin"
#            process.sendline('admin') #password
#            print process.after
#        elif index == 7:
#            print "[infor]Email:xxx@email.com"
#            process.sendline(email) # type in email
#            print process.after
#        elif index == 9:
#            print "[info]skip license check, so press q"
#            process.send('q')
#            print process.after
#        elif index == 10:
#            print "[info] Accept License"
#            process.sendline('yes')
#            print process.after
#        print "[info] FM server install successfully"
#        process.logfile = fout
    except:
        logging.error("FM auto-install failed due to Pexpect EOF")
        process.close()
           
     
def shutdownFM():
    _shutdownFM()
    
def startUpFM():
    _startUpFM()
def restartFM():
    _restartFM()
    
def _shutdownFM():
    ''' this function need to be worked before trigger handleFMDB function'''
    dir = '/opt/FlexMaster'
    try:
        os.chdir(dir)
        logging.info('Done: change current directory to %s' % dir)
        try:
            os.system('./shutdown.sh')
            logging.info('Done: ./shutdown.sh')
        except:
            logging.error('Failed: ./shutdown.sh')
    except:
        logging.error('Failed: switch to directory: %s' % dir)
    

def _startUpFM():
    ''' this function need to be worked before trigger handleFMDB function'''
    dir = '/opt/FlexMaster'
    try:
        os.chdir(dir)
        logging.info('Done: change current directory to %s' % dir)
        try:
            os.system('./startup.sh')
            logging.info('Done: ./startup.sh')
        except:
            logging.error('Failed: ./startup.sh')
            logging.info('Try to shutdown FM server and restart FM .....')
            _shutdownFM()
            _restartFM()
    except:
        logging.error('Failed: start up FM server')
        
def _restartFM():
    ''' this function need to be worked before trigger handleFMDB function'''
    dir = '/opt/FlexMaster'
    try:
        os.chdir(dir)
        logging.info('Done: change current directory to %s' % dir)
        try:
            os.system('./restart.sh')
            logging.info('Done: ./restart.sh')
        except:
            logging.error('Failed: ./restart.sh')          
    except:
        logging.error('Failed: change to %s' % dir)            

           
def handleFMDB(fileName='',handle='b'):
    ''' Before backup/restore FM database, it needs to be shutdown
        ex: handleFMDB(fileName,handle='b') backup FMDB
            handleFMDB(fileName,handle='r') restore FMDB
    '''
    _shutdownFM()
    
    # go to database directory
    dir = glob.glob('/opt/FlexMaster/3rdparty/mysql/m*')
    
    try:
        os.chdir(glob.glob('/opt/FlexMaster/3rdparty/mysql/m*')[0])#mysql version might be different on different FM server
        logging.debug("Monitor: %s" % os.getcwd())
        time.sleep(5)
        if handle == 'r': #restore
            logging.debug('Restore FM database in 5 seconds')
            time.sleep(5)
            restoreFMDB()
        else: #backup
            logging.debug('Backup FM database in 5 seconds')
            time.sleep(5)
            backupFMDB(fileName)
        logging.info('------------------------------------------------')
        logging.info('-        wait for 30 second to restart FM      -')
        logging.info('------------------------------------------------')
        _startUpFM()
        time.sleep(30)
        logging.info('Done:FM Server is running now')
    except:
        logging.error('Failed: change current directory to %s' % dir)
        
       
def restoreFMDB():
    ''' restore FM database '''
    #no need to shutdownFM()z
    #no need to chdir()
    #restore the tar.gz file to /opt/FlexMaster/3rdparty/mysql/m*
    
    #this line might need to be enhanced to be more clear!
    tar = 'tar -zxvf /tmp/FM*.tar.gz'
    
    try:
        os.system(tar)
        logging.info("Done: Untar FM Database Successfully")
        logging.info('Done: Restore FM datebase')
    except:
        logging.error("Failed: Untar FM Database")
          
 
def backupFMDB(fileName):
    #no need to change current working directory
    #no need filename
    #no need to shutdown fm
    ISOTIMEFORMAT= '%Y-%m-%d'
    #filename:
    tar = 'tar -zcvf %s%s.tar.gz data' % (fileName,time.strftime(ISOTIMEFORMAT, time.localtime(time.time())))
    
    try:
        logging.info('Command: %s' % tar)
        os.system(tar)
        logging.info("Backup FM Database Successfully")
        try:
            os.system('mv *.tar.gz /tmp') #copy it to /tmp
            logging.info("Done: Move tar.gz file to /tmp")
        except:
            logging.error("Failed: Move tar.gz file to /tmp")
    except:
        logging.error("Failed: Backup FM Database")
        
        
def do_test(cfg):
    ''' Main Function to run FM server installation'''
    install_config = dict(
                          email = 'autotest@ruckuswireless.com',\
                          iso = 'FM_9.0.0.0.126.20100719_0004.iso',\
                          handle = 'b',\
                          option ='')
    
    install_config.update(cfg)
    #Need an enhancement here
    tar_file = '%s_backup' % install_config['iso'] 
    logging.info( "[info] Option: %s " % install_config['option'])
    
    if install_config['option'] == 'backup':
        handleFMDB(tar_file,install_config['handle'])
        
    elif install_config['option'] == 'restore':
        handleFMDB(tar_file,handle='r')
        
    elif install_config['option'] == 'uninstall':
        try:
            goToOpt()
            uninstallFM()
        except:
            logging.error('Failed: no need to uninstall in do_test()')
            
    elif install_config['option'] == 'install':
        #Before install FM server, need to uninstall FM server first
        print "iso(install_config['iso']): %s" % install_config['iso']
        
        source_iso_full_path="/tmp/%s" % (install_config['iso'])
        print "tmp_dir = %s" % source_iso_full_path
        try:
            installFM(source_iso_full_path)
            logging.info("Monitor: Wait 3 minutes until AP/ZD connects to FM server")
            time.sleep(180) # wait 3 minutes
            logging.info("Done: FM server installation")
            logging.info("Please verify AP/ZD connection")
            
        except:
            logging.error("Failed: FM server installation")
                  
    else:
        print "[Error] what do you want to do?"
    
def usage(): 
    #needs to upgrade to the one tea program has.
    logging.info(' python auto_install_FM.py xxx.iso [uninstall/install/restore/backup]')
    
if __name__ == '__main__':
    cfg={}
    if len(sys.argv) < 2:
        usage()
        exit(1)
    cfg['iso'] = sys.argv[1]
    
    cfg['option'] = sys.argv[2]
       
    do_test(cfg)
    #send_mail("172.16.100.20", "webber.lin@ruckuswireless.com", "RAT <rat@ruckuswireless.com>", "auto_install is completed", "Please verify by typing ps -aux |grep java")
    #send_mail(mail_server_ip, to_addr_list, from_addr, subject, body, attachment_list = [], html_txt = ""):