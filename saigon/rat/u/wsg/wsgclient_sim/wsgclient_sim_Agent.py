"""
Author: Yung-Mu Chen <armor.chen@ruckuswireless.com>
Description:
    For scaling testing, 10k APs (wsg clients) are distributed into 10 VM servers. Each VM server has 1k APs.
    The wsgclient serial id can be assigned from 1 to 10000.
    Each VM server generates 1k APs including different IP ranges and mac address.
    All wsgclient-sim are embedded into VM Servers, this module is used for starting up/shutdown those wsg clients.  
usage:
    tea.py <wsgclient_sim_Agent key/value pair> ...
    
    where <wsgclient_sim_Agent key/value pair> are:
        shutdown     :   if True then try to shutdown all of wsgclients
        timeout      :   waiting for wsgclients.
        
    notes:
        
Examples:
    tea.py wsgclient_sim_Agent te_root=u.wsg.wsgclient_sim
    tea.py wsgclient_sim_Agent te_root=u.wsg.wsgclient_sim shutdown=True
    tea.py wsgclient_sim_Agent te_root=u.wsg.wsgclient_sim debug=True
    tea.py wsgclient_sim_Agent te_root=u.wsg.wsgclient_sim timeout=100
"""
import re
import time
import logging
import string

from RuckusAutoTest.components.LinuxPC import LinuxPC


class wsgclient_sim_Agent():
    
    def __init__(self):
        self.agent = None
        self.tcfg = dict(vm_ip_addr='172.17.16.50',
                         wsg_server_ip='192.168.2.2',
                         ap_start_ip='192.168.3.1',
                         ap_end_ip='192.168.3.10',
                         start_id=1,
                         end_id=10,
                         wsgclient_cnt=0,
                         wsg_server_url='https://127.0.0.1/wsg/ap',
                         user='lab',
                         passwd='lab4man1',
                         asRoot=False,
                         root_passwd='lab4man1',
                         debug=False,
                         init=False,
                         prompt=r"([^@]+)@(.+)\s*(~|[^#$]+)[#$] ",
                         rs_fname='result.txt',
                         shutdown_first=True,
                         timeout=30,
                         work_dir='/tmp/',
                         script_exc_dir='wsgclient-sim')
        self.tcfg['wsgclient_cnt']=self.tcfg['end_id']-self.tcfg['start_id']+1
        self.tcfg['ip_addr']=self.tcfg['vm_ip_addr']


    """
      Update Agent Information by configuration file (conf)
      After that, we use the following commands to control wsgclients

      --connect_vm : connect to a vm server
      --disconnect_vm : disconnect from a vm server
      --startup_wsgclients : lunch all wsgclient in the configuration file (mobile zone)
      --shutdown_wsgclients : terminate all wsgclient in the configuration file (mobile zone)
      --startup_wsgclients_by_range : start a range of wsgclient in the zone
      --shutdown_wsgclients_by_range : terminate a range of wsgclient in the zone
      
    """        
    def touch_tcfg(self, conf):
        self.tcfg.update(conf)

    def get_tcfg(self):
        return self.tcfg
            
    def connect_vm(self):
        if self.agent is None :
            logging.info('[ConnectTo WSGClient VM Server] with [ipAddr %s] [user %s] [psw %s] [rpsw %s]' \
                % (self.tcfg['vm_ip_addr'], self.tcfg['user'], self.tcfg['passwd'], self.tcfg['root_passwd']))        
            self.agent = LinuxPC(self.tcfg)
            self.agent.initialize(dologin=False)        
            self.agent.login(asRoot=False)
            self.agent.login_as_root()
            self.agent.do_cmd('cd /')
            self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
            logging.info(self.agent.do_cmd('pwd', timeout=30))
        
    def disconnect_vm(self):
        try:
            logging.info("[Disconnect From WSGClient VM Server]")
            self.agent.close()
                        
        except Exception, e:
            print "** ERROR ** Cannot close connection to WSGClient VM Server:\n%s" % e.message
            

    def startup_wsgclients(self):
        cfg = dict()
        cfg.update(self.tcfg)
        self.agent.do_cmd('cd /')
        self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        #data = self.agent.do_cmd('pwd')
        #print data
        data = self.agent.do_cmd('nohup python auto.py -i %s -s %d -e %d -v dev-ip -t Up -w On &' \
                                 % (cfg['ap_start_ip'], cfg['start_id'], cfg['end_id']), timeout=60)
        return data

    def shutdown_wsgclients(self):
        cfg = dict()
        cfg.update(self.tcfg)
        self.agent.do_cmd('cd /')
        self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        #data = self.agent.do_cmd('pwd')
        #print data
        data = self.agent.do_cmd('nohup python auto.py -s %d -e %d -v dev-ip -t Down &' \
                                 % (cfg['start_id'], cfg['end_id']), timeout=60)
        return data
            
    def startup_wsgclients_by_range(self, start_ip, start, end):    
        cfg = dict()
        cfg.update(self.tcfg)
        cfg['ap_start_ip']=start_ip
        cfg['start_id']=start
        cfg['end_id']=end
        self.agent.do_cmd('cd /')
        self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        #data = self.agent.do_cmd('pwd')
        #print data
        data = self.agent.do_cmd('nohup python auto.py -i %s -s %d -e %d -v dev-ip -t Up -w On &' \
                                 % (cfg['ap_start_ip'], cfg['start_id'], cfg['end_id']), timeout=60)
        return data
    
    def shutdown_wsgclients_by_range(self, start, end):
        cfg = dict()
        cfg.update(self.tcfg)
        cfg['start_id']=start
        cfg['end_id']=end
        self.agent.do_cmd('cd /')
        self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        #data = self.agent.do_cmd('pwd')
        #print data
        data = self.agent.do_cmd('nohup python auto.py -s %d -e %d -v dev-ip -t Down &' \
                                 % (cfg['start_id'], cfg['end_id']), timeout=60)
        return data

    def get_wsgclient_nums(self):
        self.agent.do_cmd('cd /')
        self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        result = self.agent.do_cmd('ps axuw | grep wsgclient | grep -v grep|wc -l', 5)
        logging.info(result)
        hnd = re.search('(\d+)', result)
        logging.info('curret APs nums are %s' % hnd.group(0))
        return int(hnd.group(0))        
        
    def halt_process(self, debug):
        if debug:
            import pdb
            pdb.set_trace()
            
def initial_wsgclient_agents(**kwargs):
    """
        1. set up all of APs agents.
        2. start all of SimAPs.
    """
    cfg = {   
             'mobile_zone_LA' : {
                'vm_ip_addr' : '172.17.16.50',
                'ap_start_ip': '192.168.13.1',
                'ap_end_ip' : '192.168.3.100',
                'start_id' : 1,
                'end_id' : 10,
                'wsg_server_url' : 'https://127.0.0.1/wsg/ap'
             },
           }
    cfg.update(kwargs)
    
    wsgclient_vm_Agents = []
    for k, v in cfg.items():
        agent = wsgclient_sim_Agent()
        logging.info('Initial wsgclient Mobile Zone: [%s]' % k)
        agent.touch_tcfg(v)
        wsgclient_vm_Agents.append(agent)
    return wsgclient_vm_Agents

def update_keywords(s, d):
    for k, v in s.items():
        if d.has_key(k):
            d[k] = v
            
def touch_agents(wsgclient_vm_Agents):
    for mobile_zone in wsgclient_vm_Agents :
        mobile_zone.connect_vm()

def start_all_aps(wsgclient_vm_Agents):
    for mobile_zone in wsgclient_vm_Agents :
        mobile_zone.startup_wsgclients()

def close_all_aps(wsgclient_vm_Agents):
    for mobile_zone in wsgclient_vm_Agents: 
        mobile_zone.shutdown_wsgclients()

def destroy_agents(wsgclient_vm_Agents):
    for mobile_zone in wsgclient_vm_Agents :
        mobile_zone.shutdown_wsgclients()
        mobile_zone.disconnect_vm()
    wsgclient_vm_Agents = None

def run_agents(**kwargs):
    """
    provide for execution command facade of agents.
    """
    wsgclient_vm_Agents = initial_wsgclient_agents(**kwargs)
    touch_agents(wsgclient_vm_Agents)
    start_all_aps(wsgclient_vm_Agents)
    return wsgclient_vm_Agents 

def close_agents(wsgclient_vm_Agents):
    """
    provide for close command facade of agents.
    """
    destroy_agents(wsgclient_vm_Agents)

def usage():
    """
    usage:
        tea.py <simap_vm_controller key/value pair> ...
        
        where <simap_vm_controller key/value pair> are:
            shutdown     :   if True then try to shutdown all of SimAPs
            timeout      :   waiting for SimAPs.
        notes:        
    Examples:
        tea.py wsgclient_sim_Agent te_root=RuckusAutoTest.lib.wsg_simap
        tea.py wsgclient_sim_Agent te_root=u.zd.simap shutdown=True
        tea.py wsgclient_sim_Agent te_root=u.zd.simap debug=True
        tea.py wsgclient_sim_Agent te_root=u.zd.simap timeout=100
    """
    pass   

def main(**kwargs):
    mycfg = dict(timeout=60, debug=False, shutdown=False)
    vmcfg = {   
             'mobile_zone_DC' : {
                'ipaddr' : '172.17.16.50',
                'start_id' : 21,
                'end_id' : 30,
             },             
           }
    update_keywords(kwargs, vmcfg)
        
    update_keywords(kwargs, mycfg)
    
    if mycfg['debug']:
        import pdb
        pdb.set_trace()
    
    if mycfg['shutdown']:
        logging.info('try to shutdown all Mobile Zone.')
        wsgclient_vm_Agents = initial_wsgclient_agents(**vmcfg)
        touch_agents(wsgclient_vm_Agents)
        close_agents(wsgclient_vm_Agents)
        logging.info('-------finished-------')
        return []


    logging.info("checking the active wsgclients numbers from VM")    
    wsgclient_vm_Agents = run_agents(**vmcfg)
    startT = time.time()
    endT = time.time()
    logging.info('begin checking all of APs status after simulator server starting up.')
    expectedCount=0;
    for mobile_zone in wsgclient_vm_Agents:
        expectedCount += mobile_zone.get_tcfg()['wsgclient_cnt']

    logging.info('expectedCount : %d'% expectedCount)

    while endT - startT < mycfg['timeout']:
        flag = False
        actualCount=0

        # get process number
        # note: if mobile zones are distributed at the same server,
        #       using ps auxw will get totol number of processes in a server
        # Todo: developing a method to check # of clients
        for mobile_zone in wsgclient_vm_Agents:
            actualCount = mobile_zone.get_wsgclient_nums()
            #expectedCount = mobile_zone.get_tcfg()['wsgclient_cnt']            

        logging.info('actualCount : %d'% actualCount)

        if actualCount != expectedCount :
           logging.info('there are %d APs ready, %d APs not yet' % (actualCount, expectedCount - actualCount))
           flag = True
        #        break

        if not flag:
            logging.info('all of simulator APs are ready')
            break
        else:
            endT = time.time()
            time.sleep(5) 
    return wsgclient_vm_Agents

