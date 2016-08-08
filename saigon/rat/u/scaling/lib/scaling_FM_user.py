'''
Created on Sep 3, 2010

@author: webber.lin
'''


import logging
import time
from RuckusAutoTest.components import create_fm_by_ip_addr
#from RuckusAutoTest.common.Ratutils import send_mail
from u.scaling.lib.syslog_client import syslog


def readUserPassw_from_a_file(filename=''):
    ''' 
        Get the username and password and return a dictionary. 
        
    The dictionary format is {username:password,}    
    '''
    import re
    f = open(filename,'r')
    line_dict={}
    comma=re.compile(',')
    #example:  'username:NA-21-1,password:na,' 
    try:
        for line in f:
            up=re.sub('username:|password:','',line)
            user=comma.split(up)[0]
            passw=comma.split(up)[1]
            line_dict[user]=passw
        f.close()
        return line_dict # the dictionary format is {username:password,}
    except:
        msg = 'Failed (read username or password from te_info txt file:%s)' % filename
        syslog(message=msg,host='172.17.19.201',skey='error',port=514,source_ip='')
        logging.error('read User/Name Password failed')

def create_multi_users(p_dict={},account_info={},ip_addr='',version='9'):

    '''
      this function returns a list of fm instance.
    '''
    keys=account_info.keys()
    keys.sort()
    fm_list=[]
    for key in keys:
        try:
            temp_fm=create_fm_by_ip_addr(username=key,password=account_info[key],ip_addr=ip_addr)
            fm_list.append(temp_fm)
            logging.info('User:%s is created on FM server(%s)' % (key,ip_addr))
        except:
            msg = 'Failed (create multiple users failed on user: %s)' % key
            syslog(message=msg,host='172.17.19.201',skey='error',port=514,source_ip='')
            logging.error('create FM by IP address failed with User name: %s' % key)
    p_dict['fm_list']=fm_list
    #return fm_list


    
def multi_user_log_in(fm_list):
    #update: 07/15/2010
    #Add: monitor fm user login and keep user staying on fm server.
    count=1
    
    for fm in fm_list:
        try:
            #fm.login()
            fm.stop()
            fm.start()
            logging.info("Account: %s" % fm.username)
        except Exception:
            msg = 'Failed (First time to Login FM server with user name:%s)' % fm.config['username']
            syslog(message=msg,host='172.17.19.201',skey='error',port=514,source_ip='')
            logging.error("Warning:FM user log in fail: %s" % fm.config['username'])
            time.sleep(20)
            try:
                #logging.error("Warning: %s cannot login and refresh Page" % fm.config['username'])
                #time.sleep(10)
                fm.s.refresh()
                fm.login()
            except Exception:
                msg = 'Failed (Second time Login FM server with user name:%s after waiting 20 seconds to refresh FM page)' % fm.config['username']
                syslog(message=msg,host='172.17.19.201',skey='error',port=514,source_ip='')
                logging.error("Warning: After refresh, %s still unable to login"% fm.config['username'])
            #logging.error("After refresh the page, now try to login (%s) again" % fm.config['username'])
            #send_mail("172.16.100.20", "Webber Lin<webber.lin@ruckuswireless.com>", "RAT <webber.lin@ruckuswireless.com>", "FM_MultiUser_login", "Something wrong!! %s" % fm.config['username'])
            continue   
        time.sleep(10)
        msg = "%d. FM user {{%s}} logged in" % (count,fm.config['username'])
        syslog(message=msg,host='172.17.19.201',port=514,source_ip='')
        logging.info("\t\t%d. FM user {{%s   }} log in" % (count,fm.config['username']))
        count=count+1

def multi_user_log_out(fm_list):
    count=1
    
    for fm in fm_list:
        try:
            fm.logout()
        except:
            msg = "Failed %d. FM user {{%s}} logged out" % (count,fm.config['username'])
            syslog(message=msg,host='172.17.19.201',skey='err',port=514,source_ip='')
            logging.error('\t\t%d. FM user {{%s  }} log out failed'% (count, fm.config['username']))
            try:
                time.sleep(10)
                fm.logout()
                msg = "%d. FM user {{%s}} logged out" % (count,fm.config['username'])
                syslog(message=msg,host='172.17.19.201',port=514,source_ip='')
            except:
                msg = "2nd Failed %d. FM user {{%s}} logged out" % (count,fm.config['username'])
                syslog(message=msg,host='172.17.19.201',skey='err',port=514,source_ip='')
                logging.error('\t\t%d. FM user {{%s  }} log out failed'% (count, fm.config['username']))
            continue
        time.sleep(10)
        msg = "%d. FM user {{%s}} logged out" % (count,fm.config['username'])
        syslog(message=msg,host='172.17.19.201',port=514,source_ip='')
        logging.info("\t\t%d. FM user {{%s   }} log out" % (count, fm.config['username']))
        count=count+1
