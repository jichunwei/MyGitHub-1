
import time

def telnet_enable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT,-1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_TelnetERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def telnet_disable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_TelnetDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def ssh_enable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_SSHERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def ssh_disable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_SSHDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def http_enable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_HTTPERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def http_disable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_HTTPDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def https_enable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_HTTPSERd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def https_disable(mf_obj):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['Management_HTTPSDRd'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def telnet_port(mf_obj,port='23'):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['Management_TelnetPort'], port)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def ssh_port(mf_obj,port='22'):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['Management_SSHPort'], port)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def http_port(mf_obj,port='80'):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['Management_HTTPPort'], port)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def https_port(mf_obj,port='443'):
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['Management_HTTPSPort'], port)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def save_mgmt(mf_obj):
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def allow_mgmt(mf_obj): #if allowed, remote machine can access CPE
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['allow_mgmt'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def not_allow_mgmt(mf_obj):
    """
    if set not allowed, the CPE will not response to any connection,
    factory default is needed
    """
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_checked(mf_obj.info['allow_mgmt'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def limit_mgmt(mf_obj,listofip={}):
    """
    dictionary has to be in this format:
    dict(ip1='192.168.0.10',ip2='192.168.0.20',mask1='255.0.0.0',mask2='255.0.0.0')
    """
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['limit_mgmt'])
    iplist = dict (ip1 = '0.0.0.0',
                   ip2 = '0.0.0.0',
                   ip3 = '0.0.0.0',
                   ip4 = '0.0.0.0',
                   mask1 = '255.255.255.0',
                   mask2 = '255.255.255.0',
                   mask3 = '255.255.255.0',
                   mask4 = '255.255.255.0'
                   )
    iplist.update(listofip) #updating info from passing parameters
    a = 1
    for k in range (1,5): #go through the ip string inside dictionary, split it
        ipaddr = iplist['ip%s'%k].split('.')
        ipmask = iplist['mask%s'%k].split('.')
        for x in range(0,4):# go through the splited ip part from above and insert it
            #mf_obj.s.type_text(mf_obj.info['ip%sentry%s'%(a,x)],ipaddr[x])
            mf_obj.s.type_text("//input[@id='entry%sipaddress%s']"%(a,x),ipaddr[x])
            #mf_obj.s.type_text(mf_obj.info['mask%sentry%s'%(a,x)],ipmask[x])
            mf_obj.s.type_text("//input[@id='entry%smask%s']"%(a,x),ipmask[x])
        a = a + 1
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def not_limit_mgmt(mf_obj): # any ip will be able to access CPE
    mf_obj.navigate_to(mf_obj.ADMIN_MGMT, -1, timeout = 20)
    mf_obj.s.click_if_checked(mf_obj.info['limit_mgmt'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def restore(mf_obj):
    """remember to navigate to the correct menu"""
    mf_obj.s.safe_click(mf_obj.info['restore'])

def submit(mf_obj):
    """remember to navigate to the correct menu"""
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def ping(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.ADMIN_DIAGS, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['ping'], ip)
    mf_obj.s.safe_click(mf_obj.info['ping_button'])
    time.sleep(20)
    output = mf_obj.s.get_text(mf_obj.info['ping_output'])
    return output

def traceroute(mf_obj,ip):
    """ip is in string format"""
    mf_obj.navigate_to(mf_obj.ADMIN_DIAGS, -1, timeout = 20)
    mf_obj.s.type_text(mf_obj.info['trace'],ip)
    mf_obj.s.safe_click(mf_obj.info['trace_button'])
    time.sleep(30)
    output = mf_obj.s.get_text(mf_obj.info['trace_output'])
    return output


def admin_log_en(mf_obj, ip, port='514'):
    """
    ip is in string format
    sends log message to remote syslog
    """
    mf_obj.navigate_to(mf_obj.ADMIN_LOG, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['log_y'])
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['host0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['host1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['host2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['host3'],splitip[3])
    mf_obj.s.type_text(mf_obj.info['host_port'],port)
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])#save info


def admin_log_dis(mf_obj):
    """disable remote syslog"""
    mf_obj.navigate_to(mf_obj.ADMIN_LOG, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['log_n'])
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])#save info

def refresh(mf_obj):
    """remember to navigate to the correct menu"""
    mf_obj.s.safe_click(mf_obj.info['refresh'])


def admin_log(mf_obj):
    """return syslog messages"""
    mf_obj.navigate_to(mf_obj.ADMIN_LOG, -1, timeout = 20)
    output = mf_obj.s.get_text(mf_obj.info['admin_output'])
    return output
