"""
Description:
    all of SimAPs are embed into SimAP Servers, this module is used for starting up/shutdown those SimAPs,
    extract those SimAPs MAC Address or catch count of SimAPs from agents.  
usage:
    tea.py <simap_vm_controller key/value pair> ...
    
    where <simap_vm_controller key/value pair> are:
        shutdown     :   if True then try to shutdown all of SimAPs
        timeout      :   waiting for SimAPs.
    notes:
        if want to update more parameters, please modify vmcfg/mycfg from main function.        
Examples:
    tea.py simap_vm_controller te_root=u.zd.simap
    tea.py simap_vm_controller te_root=u.zd.simap shutdown=True
    tea.py simap_vm_controller te_root=u.zd.simap debug=True
    tea.py simap_vm_controller te_root=u.zd.simap timeout=100
"""
import re
import time
import logging

from RuckusAutoTest.components.LinuxPC import LinuxPC

class SimAPsAgent():
    
    def __init__(self):
        self.agent = None
        self.tcfg = dict(ipaddr='172.18.35.150',
                         zd_ip='192.168.0.2',
                         ap_start_mac='00:13:92:01:02:00',
                         ap_cnt=3,
                         based_line='saigon',
                         cfgonly=False,
                         user='lab',
                         passwd='lab4man1',
                         asRoot=False,
                         root_passwd='lab4man1',
                         debug=False,
                         init=False,
                         prompt=r"([^@]+)@(.+)\s*(~|[^#$]+)[#$] ",
                         rs_fname='result.txt',
                         shutdown_first=True,
                         timeout=5,
                         chk_time=1200,
                         work_dir='/sim_ap',
                         script_exc_dir='/sim_ap/sim-ap')  
        
    def touch_tcfg(self, conf):
        self.tcfg.update(conf)
        self.tcfg['ip_addr'] = self.tcfg['ipaddr']
        self.chk_time = self.tcfg['chk_time']
        
    def get_tcfg(self):
        return self.tcfg
            
    def connect_te(self):
        if self.agent is None :
            logging.info('[ConnectTo Agent.apvm] with [ipAddr %s] [user %s] [psw %s] [rpsw %s]' \
                % (self.tcfg['ipaddr'], self.tcfg['user'], self.tcfg['passwd'], self.tcfg['root_passwd']))        
            self.agent = LinuxPC(self.tcfg)
            self.agent.initialize(dologin=False)        
            self.agent.login(asRoot=False)
            self.agent.login_as_root()
            self.agent.do_cmd('cd /')
            self.agent.do_cmd('cd %s' % self.tcfg['work_dir'])
            logging.info(self.agent.do_cmd('pwd', timeout=30))
        
    def disconnect_te(self):
        try:
            logging.info("[DisconnectFrom Agent.APVM]")
            self.agent.close()
                        
        except Exception, e:
            print "** ERROR ** Cannot close APVM Server:\n%s" % e.message
            
            
    def startup_simaps(self):    
        cfg = dict(ap_cnt=10, ap_mode='zf2741', ap_start_mac='00:13:92:01:02:00', zd_ip='192.168.0.2')
        cfg.update(self.tcfg)
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        data = self.agent.do_cmd('sh run_ap.sh %s %d %s %s' % (cfg['ap_mode'], cfg['ap_cnt'], cfg['start_mac'], cfg['zd_ip']), 30)        
        return data
    
    def startup_single_simap(self):
        cfg = dict(ap_cnt=1, ap_mode=u'zf2925', ap_start_mac='00:13:92:01:02:00', zd_ip='192.168.0.2', rogue=0, tap_id=1)
        cfg.update(self.tcfg)
        self.agent.do_cmd('cd %s/script' % self.tcfg['script_exc_dir'], timeout=30)
        data = self.agent.do_cmd('sh gen_all_ap.sh %s %d %s zd_ip=%s tap_started_id=%d' % 
                                (str(cfg['ap_mode']), cfg['ap_cnt'], cfg['ap_start_mac'], cfg['zd_ip'], cfg['tap_id']), 30)
        return data
    
    def shutdown_simaps(self):
        logging.info('shutdown all of simulator APs')
        self.agent.do_cmd('cd %s' % self.tcfg['script_exc_dir'], timeout=30)
        data = self.agent.do_cmd('sh stop_ap.sh', timeout=30)
        startT = time.time()
        endT = time.time()
        while True:
            if endT - startT >= self.chk_time:
                logging.error("SimAPs haven't shutdown all, but time is out")
                
            else:
                actual_cnt = self.get_sim_ap_nums(timeout=10)
                if actual_cnt == 0:
                    logging.info("All of SimAPs at Server[%s] have shutdown" % self.tcfg['ipaddr'])
                    break
                
                else:
                    time.sleep(5)
                    endT = time.time()
                    
        self.agent.do_cmd('service network restart', timeout=30)
        logging.info(data)
        return data

    
    def get_sim_ap_nums(self, timeout=30):
        result = self.agent.do_cmd('ps aux | grep qemu | grep -v grep | wc -l', timeout=timeout)
        logging.info(result)
        hnd = re.search('(\d+)', result)
        logging.info('curret APs nums are %s' % hnd.group(0))
        return int(hnd.group(0))
    
    def get_simaps_nums_by_model(self, model='zf2942'):
        result = self.agent.do_cmd('ps aux | grep qemu | grep zf2942 | grep -v grep | wc -l', timeout=30)
        hnd = re.search('(\d+)[^\d]+(\d+)', result)    
        logging.info('curret APs nums are %s by model[%s]' % (hnd.group(2), model))
        return int(hnd.group(2))
    
    def get_simaps_maclist(self):
        """
        Fetch all of SimAP macaddrs against this ENV.
        """
#        import pdb
#        pdb.set_trace()
        t0 = time.time()
        exp_cnt = self.tcfg['ap_cnt']
        while True :
            act_cnt = self.get_sim_ap_nums()
            if exp_cnt == act_cnt : break
            if time.time() - t0 < self.chk_time :
                time.sleep(5)
            else:
                raise Exception('expected APs :[%s], actual APs :[%s]' % (exp_cnt, act_cnt))
                         
        result = self.agent.do_cmd('ps aux | grep qemu | grep -v grep', timeout=30)
        pattern = 'macaddr=([\da-fA-F:]{17})'
        return re.findall(pattern, result)
        
    def halt_process(self, debug):
        if debug:
            import pdb
            pdb.set_trace()
            
def initial_agents(**kwargs):
    """
        1. set up all of APs agents.
        2. start all of SimAPs.
    """
    cfg = {   
             'apvm_01' : {
                'ipaddr' : '172.18.35.150',
                'ap_start_mac' : '00:13:92:01:02:00',
                'ap_cnt' : 2,
                'ap_mode':'ss2942',
             },
           }
    cfg.update(kwargs)
    
    apvmAgents = []
    for k, v in cfg.items():
        agent = SimAPsAgent()
        logging.info('Initial SimAP Server: [%s]' % k)
        agent.touch_tcfg(v)
        apvmAgents.append(agent)
    return apvmAgents

def update_keywords(s, d):
    for k, v in s.items():
        if d.has_key(k):
            d[k] = v
            
def touch_agents(apvmAgents):
    for apvm in apvmAgents :
        apvm.connect_te()

def start_all_aps(apvmAgents):
    for apvm in apvmAgents :
        apvm.startup_simaps()

def close_all_aps(apvmAgents):
    for apvm in apvmAgents: 
        apvm.shutdown_simaps()

def destroy_agents(apvmAgents):
    for vm in apvmAgents :
        vm.shutdown_simaps()
        vm.disconnect_te()
    apvmAgents = None
    
def get_all_aps_macs(apvmAgents):
    macMap = {}
    for vm in apvmAgents :
        list = vm.get_simaps_maclist()
        logging.info('vm.ipaddr=%s,mac list: %s' % (vm.get_tcfg()['ipaddr'], list))
        macMap[vm.get_tcfg()['ipaddr']] = list
    return macMap

def run_agents(**kwargs):
    """
    provide for execution command facade of agents.
    """
    apvmAgents = initial_agents(**kwargs)
    touch_agents(apvmAgents)
    start_all_aps(apvmAgents)
    return apvmAgents 

def close_agents(apvmAgents):
    """
    provide for close command facade of agents.
    """
    destroy_agents(apvmAgents)

def usage():
    """
    usage:
        tea.py <simap_vm_controller key/value pair> ...
        
        where <simap_vm_controller key/value pair> are:
            shutdown     :   if True then try to shutdown all of SimAPs
            timeout      :   waiting for SimAPs.
        notes:        
    Examples:
        tea.py simap_vm_controller te_root=u.zd.simap
        tea.py simap_vm_controller te_root=u.zd.simap shutdown=True
        tea.py simap_vm_controller te_root=u.zd.simap debug=True
        tea.py simap_vm_controller te_root=u.zd.simap timeout=100
    """
    pass   

def main(**kwargs):
    mycfg = dict(timeout=60, debug=False, shutdown=False)
    vmcfg = {   
             'apvm_01' : {
                'ipaddr' : '172.18.35.255',
                'ap_start_mac' : '00:13:92:01:02:00',
                'ap_cnt' : 50,
                'ap_mode':'ss2942',
             },
             'apvm_02' : {
                'ipaddr' : '172.18.35.256',
                'ap_start_mac' : '00:13:93:01:02:00',
                'ap_cnt' : 50,
                'ap_mode':'ss2942',
             },             
           }
    update_keywords(kwargs, vmcfg)
        
    update_keywords(kwargs, mycfg)
    
    if mycfg['debug']:
        import pdb
        pdb.set_trace()
    
    if mycfg['shutdown']:
        logging.info('try to shutdown all of SimAP mockers.')
        apvmAgents = initial_agents(**vmcfg)
        touch_agents(apvmAgents)
        close_agents(apvmAgents)
        logging.info('-------finished-------')
        return []


    logging.info("checking the active APs numbers from VM")    
    apvmAgents = run_agents(**vmcfg)
    startT = time.time()
    endT = time.time()
    logging.info('begin checking all of APs status after simulator server starting up.')
    while endT - startT < mycfg['timeout']:
        flag = False        
        for apvm in apvmAgents:
            actualCount = apvm.get_sim_ap_nums()
            expectedCount = apvm.get_tcfg()['ap_cnt']            
            if actualCount < expectedCount :
                logging.info('there are %d APs ready, %d APs not yet' % (actualCount, expectedCount - actualCount))
                flag = True
                break
        if not flag:
            logging.info('all of simulator APs are ready')
            break
        else:
            endT = time.time()
            time.sleep(5) 
    return apvmAgents

