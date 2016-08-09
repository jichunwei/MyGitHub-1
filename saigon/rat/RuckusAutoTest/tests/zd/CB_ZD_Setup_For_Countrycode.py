
import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib
import time
import logging
import traceback

class CB_ZD_Setup_For_Countrycode(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        try:
            self._create_ap()
    
            ## self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.active_ap_symbolic_name)        
            ## self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.mac_addr)
            if self.active_ap:
                self.old_fixedctrycode = self.active_ap.get_fixed_country_code()
            else:
                raise Exception('Target AP %s not found' % self.mac_addr)
    
            logging.info("Get the AP %s \"Fixed Ctry Code\" status is \"Fixed Ctry Code: %s\" ." % (self.mac_addr, self.old_fixedctrycode))
            if self.old_fixedctrycode.lower() == "yes":
                self.active_ap.set_fixed_country_code(False)
                logging.info("Change the \"Fixed Ctry Code\" status of the AP %s from \"yes\" to \"no\" by AP Shell command \"rbd change\"." % self.mac_addr)
    
            radio_list = ['2.4', '5']
            for radio in radio_list:
                logging.info('begin ap %s(%s) radio %s test'%(self.mac_addr, self.ap_model, radio))
                self._set_ap_full_power(self.mac_addr, radio)
                logging.info("Have set ap 'radio %s tx-power full' "% radio)

        except Exception, e:
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag[self.ap_tag]['ap_ins'] = self.active_ap
        passmsg = "Create active AP [%s %s] successfully. \nCheck and setup \"Fixed Ctry Code\" to \"no\" successfully.\nSetup radio \"tx-power\" to \"full\" successfully." % (self.active_ap.get_ap_model(), self.active_ap.get_base_mac())
        return self.returnResult('PASS', passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap_symbolic_name = self.conf['active_ap']
        self.ap_tag = self.conf['ap_tag']
        
        self.active_ap = self.conf.get('active_ap')
        self.mac_addr = self.testbed.get_aps_sym_dict()[self.active_ap]['mac']

        self.ap_model = ''
        self.ap_model = self.testbed.get_aps_sym_dict()[self.active_ap]['model']

##        # Match the parse_country_matrix_xsl(filename, ap_model)
##        if not self.ap_model.lower().startswith('zf'):
##            self.ap_model = 'zf' + self.ap_model


        self.carrierbag[self.ap_tag] = dict()

    def _create_ap(self):
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.active_ap_symbolic_name)
        if not self.active_ap:
            self.errmsg = "Active AP [%s] not found in testbed." % self.active_ap_symbolic_name
            return

        #'ap_info':{'apgroup_name': name, 'apgroup_ipmode': grp_mode, 'ap_ipmode': ap_mode}
        if self.conf.has_key('ap_info'):
            apmac = self.active_ap.base_mac_addr
            info = self.conf['ap_info']
            
            if info.has_key('apgroup_name'):
                try:
                    ap_group.set_ap_group_ip_mode_by_name(self.zd, info['apgroup_name'], info['apgroup_ipmode'])
                except:
                    ap_group.create_ap_group(self.zd, info['apgroup_name'])
                    ap_group.set_ap_group_ip_mode_by_name(self.zd, info['apgroup_name'], info['apgroup_ipmode'])
            
                lib.zd.ap.set_ap_general_by_mac_addr(self.zd, apmac, ap_group=info['apgroup_name'])

            if info.has_key('ap_ipmode'):
                lib.zd.ap.set_ap_network_setting_by_mac(self.zd, apmac, info['ap_ipmode'])

            time0 = time.time()
            wait_time = 300
            while(True):
                current_time = time.time()
                if  (current_time-time0) >wait_time:
                    self.errmsg = "Active AP [%s] not connected in %s second after change IP mode and move AP group." % (self.active_ap_symbolic_name, wait_time)
                    return
                try:
                    ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, apmac)
                    if ap_info['state'].lower().startswith('connected'):
                        break
                except:
                    pass
    
                time.sleep(3)

    def _set_ap_full_power(self, mac_addr, radio):
        ## from RuckusAutoTest.components.lib.zdcli import configure_ap        
        ## configure_ap.set_ap_tx_power(self.zdcli,ap_info['mac'],radio)
        lib.zdcli.configure_ap.set_ap_tx_power(self.zdcli, mac_addr, radio)
        time.sleep(3)

