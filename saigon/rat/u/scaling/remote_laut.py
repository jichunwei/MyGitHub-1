'''

Date: 07/09/2010
Script: remote_laut
Purpose: telnet to laut server and execute tea program remotely
Engineer: Webber Lin

MEMO: This script is for access scaling FM server only.
      Please refer to the test_engine_list
Example: 
     python remote_laut.py 8 27
'''

###
#import modules
###

import telnetlib
import pdb,sys
import time
#from RuckusAutoTest.common.Ratutils import send_mail


#test_engine list
# User is able to modify the amounts of test engine need to be operated. 
#TE_LIST=[3,4]# if test engine 3 and 4 not available to be launched
#TE_LIST=[1,2,3,4,5,6,7] # run all test engines
TE_LIST=[]

#pdb.set_trace()
# run all test engines
###
# Variable, Constants
###

PORT = '10880'

def createTE_LIST(start,end):
    ''' this function is to create a test engine list, and test engine inside
        this list won't be launched '''
    list=[]
    if start > 0 and end >= 0 and end <= 28:
        for i in range(start,end):
            list.append(i)
    return list

def createTEIPlist(te_list=range(61,81),prefix='172.17.19.2',not_available_te=[]):
    ''' this function is to generate test engine ip address'''
    host_dict={}
    #hosts=[]
    for i in te_list:
        if i not in not_available_te:
            if i <= 9:
                i='0%s' % i
            #host = "172.17.19.2%s" % i
            host = '%s%s' % (prefix,i)
            #hosts.append(host)
            host_dict[i]=host
            #print "host (%s) is appended to HOSTS list" % host
    return host_dict

def teaCommand2Send(te_module,**kwargs):
    ''' flexible for tea program arguments for remote_laut phase II'''
    tcfg = dict()
    tcfg.update(kwargs)
    command='tea.py'
    for i in tcfg.keys():
        command= command + ' %s=%s' %(i,tcfg[i])
        #debug
        #print command
    return command
    
def connectTE_and_runTea(hosts_dict,duration,version,fm_ip='192.168.1.101'):
    ''' 
        telnet to test engines and send tea program to be launched on test engine
        version = 9 (might be removed soon)
        fm_ip = '192.168.1.11'
        duration = 3
    '''
    te_obj=[]
    
    for host in hosts_dict.keys():
        try:
            try:
                print "[info] host id: %s" % host
                tn = telnetlib.Telnet(hosts_dict[host],int(PORT))
                # debug
                # laut.py server must be running on the test engine
                print " [info] host:%s, telnet obj: %s" % (hosts_dict[host],tn)
                #comments:
                #date:07/09/2010
                #Engineer: Webber Lin
                #This portion could be enhanced to extract command out
                #import pdb; pdb.set_trace()
                tn.read_until("Command#")
                time.sleep(3)
                tn.write("tea u.scaling.multi_user_log_in %s %d %d %d\n" % (fm_ip,version,int(host),int(duration)))
                #tn.write("\n")
                print "[info] tea u.scaling.multi_user_log_in %s %d %d %d\n" % (fm_ip,version,int(host),int(duration))
                te_obj.append(tn)
                print "[info] Test Engine IP: %s" % hosts_dict[host]
                print "[info] %s " % tn.read_very_eager()
                #tn.write("exit\n")
            except:
                print "[error] Test Engine IP: %s" % hosts_dict[host]
                print "[error] telnet sub-commands error"                
        except:
            print "[error] Test Engine IP: %s" % hosts_dict[host]
            print "[error] Fail to create telnet connection"
    #debug
    #print te_obj
    return te_obj

def usage():
    print "Command Format: python remote_laut.py [TE_start] [TE_end]"
    print 'Example: python remote_laut.py 8 27'

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        exit(1)
    te_start=int(sys.argv[1])
    te_end=int(sys.argv[2])   
    try:
        #TE_LIST is the list to store "unavailable" test engines
        #Default: te_1 to te_7 is for automation development only
        TE_LIST=createTE_LIST(1,8)
        list = range(te_start,te_end+1)
        if len(TE_LIST) != 0:
            # all test engines will be started!
            for i in TE_LIST: # put TEs that you want to verify
                if i in list:
                    list.remove(i)
                    print "TEST Engine : %s  will not be started" % i
        hosts = createTEIPlist(te_list=list)
        print " started TEST Engine: %s" % hosts
        try:
            te_list = connectTE_and_runTea(hosts_dict = hosts,duration=3,version=9,fm_ip='192.168.1.101')
            print "[info] TEA command sent!!"
        except:
            print "[error] TEA cmd failed!!"
    except:
        print "[error] TEA command sent failed!!"
    #finally:
        #pass
        #send_mail("172.16.100.20", "Webber Lin<webber.lin@ruckuswireless.com>", "RAT <webber.lin@ruckuswireless.com>", "auto_install is completed", "Please verify by typing ps -aux |grep java")
        #print "work successfully"
    #send_mail(mail_server_ip, to_addr_list, from_addr, subject, body, attachment_list = [], html_txt = ""):
