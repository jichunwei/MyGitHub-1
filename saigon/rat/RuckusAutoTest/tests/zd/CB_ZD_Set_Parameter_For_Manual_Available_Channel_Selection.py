# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
set parameter used by Manual Available Channel Selection cases
put them in carrierbag
"""

import logging
import random
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli.shellmode import get_single_dule_band_aps_list
from RuckusAutoTest.components.lib.zdcli.get_default_parameters import parse_country_list,get_outdoor_models_list 

class CB_ZD_Set_Parameter_For_Manual_Available_Channel_Selection(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        country_para=parse_country_list(self.zdcli,self.tftp_dir)
        outdoor_model_list=get_outdoor_models_list(self.zdcli)
        
        if country_para.has_key("United States"):
            us="United States"
        else:
            us="United states"
        if country_para.has_key("United Kingdom"):
            uk="United Kingdom"
        else:
            uk="United kingdom"
        
        #get single band and dule band ap list
        single_band_ap_list,dule_band_ap_list=get_single_dule_band_aps_list(self.ap_list)
        logging.info('single_band_ap_list is %s'%self._get_ap_list_mac(single_band_ap_list))
        logging.info('dule_band_ap_list is %s'%self._get_ap_list_mac(dule_band_ap_list))
        
        #get out door ap list
        out_door_ap_list=[]
        for model in self.model_to_ap_list:
            if model in outdoor_model_list:
                out_door_ap_list.extend(self.model_to_ap_list[model])
        logging.info('out_door_ap_list is %s'%self._get_ap_list_mac(out_door_ap_list))
        self.out_door_ap_list=out_door_ap_list
        
        dule_band_include_out_door_ap_list = copy.copy(dule_band_ap_list)
        
        for ap in dule_band_ap_list:
            if ap in out_door_ap_list:
                dule_band_ap_list.remove(ap)
        logging.info('after delete out door aps,dule_band_ap_list is %s'%self._get_ap_list_mac(dule_band_ap_list))   
             
        #get in door ap list
        in_door_ap_list=[]
        for ap in dule_band_ap_list:
            if ap not in out_door_ap_list:
                in_door_ap_list.append(ap)
        logging.info('in_door_ap_list is %s'%self._get_ap_list_mac(in_door_ap_list))

        #get US permitted dfs channel ap list
        US_dfs_ap_list=[]
        for model in self.model_to_ap_list:
            if model in country_para[us]['allow-dfs-models']:
                US_dfs_ap_list.extend(self.model_to_ap_list[model])
        logging.info('US_dfs_ap_list is %s'%self._get_ap_list_mac(US_dfs_ap_list) )
                
        #get US not permitted dfs channel ap list
        US_not_dfs_ap_list=[]
        for ap in dule_band_include_out_door_ap_list:
            if ap not in US_dfs_ap_list:
                US_not_dfs_ap_list.append(ap)
        logging.info('US_not_dfs_ap_list is %s'%self._get_ap_list_mac(US_not_dfs_ap_list))
                
        channlization_list=['20','40']
        apg_list=['default','new']
        US_channel_optimization_list = ['Interoperability','Performance']
        sigle_band_test_country_chois=['dule_band_country','only_2_4_G_country']
        
        set_para_way_list=['group','ap']
        
        #set single band ap test parameters
        logging.info('begin setting single band ap test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        self.useful_ctry_list=[]
        self.useful_ctry_list.append(us)
        self.useful_ctry_list.append(uk)
        ctry=random.choice(country_para[random.choice(sigle_band_test_country_chois)])
        self.useful_ctry_list.append(ctry)
        ap=random.choice(single_band_ap_list)
        set_para_way = random.choice(set_para_way_list)
        self.single_band_ap_test_para={'test_type':'single_band_ap',
                                       'channlization':channlization,
                                       'apg':apg,
                                       'ctry':ctry,
                                       'ap':[ap],
                                       'set_para_way':set_para_way
                                       }
    
        #set dule band ap test parameters
        logging.info('begin setting dule band ap test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        ap=random.choice(dule_band_ap_list)
        ctry=random.choice(country_para['dule_band_country'])
        self.useful_ctry_list.append(ctry)
        set_para_way = random.choice(set_para_way_list)
        self.dule_band_ap_test_para={'test_type':'dule_band_ap',
                                     'channlization':channlization,
                                       'apg':apg,
                                       'ctry':ctry,
                                       'ap':[ap],
                                       'set_para_way':set_para_way
                                       }
        
        self.precedency_para= copy.deepcopy(self.dule_band_ap_test_para)
        self.precedency_para['test_type']='precedency'
        self.precedency_para['ctry']=us
        self.backup_para = copy.deepcopy(self.precedency_para)
        self.backup_para['test_type']='backup'
        
        
        #set out door ap test parameters
        logging.info('begin setting outdoor ap test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        outdoor_ap=random.choice(out_door_ap_list)
        indoor_ap=random.choice(in_door_ap_list)
        ctry=us
        while (ctry in country_para['dfs_channel_country']) or (ctry in country_para['cband_channel_country']):
            ctry_list_key=random.choice(['American_country','European_country','Other_country'])
            ctry=random.choice(country_para[ctry_list_key])
        set_para_way = random.choice(set_para_way_list)
        self.outdoor_ap_test_para={'test_type':'outdoor_ap',
                                   'channlization':channlization,
                                   'apg':apg,
                                   'ctry':ctry,
                                   'ap':[outdoor_ap,indoor_ap],
                                    'set_para_way':set_para_way
                                   }
        self.useful_ctry_list.append(ctry)
        
        #set US dfs channel test parameters
        logging.info('begin setting US dfs channel test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        channel_optimization=random.choice(US_channel_optimization_list)
        dfs_ap=random.choice(US_dfs_ap_list)
        not_dfs_ap=random.choice(US_not_dfs_ap_list)
        set_para_way = random.choice(set_para_way_list)
        self.US_dfs_channel_test_para={'test_type':'US_dfs_channel',
                                       'channlization':channlization,
                                       'apg':apg,
                                       'channel_optimization':channel_optimization,
                                       'ctry':us,
                                       'ap':[dfs_ap,not_dfs_ap],
                                       'set_para_way':set_para_way,
                                       'allow_indoor_channel':random.choice([False,True])
                                       }
        
        #set dfs channel test parameters
        logging.info('begin setting dfs channel test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        ap=random.choice(dule_band_ap_list)
        ctry=us
        while ctry==us:
            ctry=random.choice(country_para['dfs_channel_country'])
        set_para_way = random.choice(set_para_way_list)
        self.dfs_channel_test_para={'test_type':'dfs_channel',
                                   'channlization':channlization,
                                   'apg':apg,
                                   'ctry':ctry,
                                   'ap':[ap],
                                   'set_para_way':set_para_way,
                                   'allow_indoor_channel':random.choice([False,True])
                                   }
        self.useful_ctry_list.append(ctry)
        
        #set cband channel test parameters
        logging.info('begin setting cband channel test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        ap=random.choice(out_door_ap_list)
        ctry=uk
        while ctry==uk:
            ctry=random.choice(country_para['cband_channel_country'])
        self.useful_ctry_list.append(ctry)
        set_para_way = random.choice(set_para_way_list)
        self.cband_channel_test_para={'test_type':'cband_channel',
                                   'channlization':channlization,
                                   'apg':apg,
                                   'ctry':ctry,
                                   'ap':[ap],
                                   'set_para_way':set_para_way,
                                   'allow_indoor_channel':random.choice([False,True])
                                   }
        
        #set uk cband channel test parameters
        logging.info('begin setting uk cband channel test parameters')
        channlization=random.choice(channlization_list)
        apg=random.choice(apg_list)
        ap=random.choice(out_door_ap_list)
        set_para_way = random.choice(set_para_way_list)
        self.uk_cband_channel_test_para={'test_type':'uk_cband_channel',
                                   'channlization':channlization,
                                   'apg':apg,
                                   'ctry':uk,
                                   'ap':[ap],
                                   'set_para_way':set_para_way,
                                   'allow_indoor_channel':random.choice([False,True])
                                   }
        
        logging.info('ready to save test parameters in carrierbag')
        self.country_para={}
        for k in country_para:
            if k in self.useful_ctry_list:
                self.country_para[k]=country_para[k]
                
        self._update_carrier_bag()     
        logging.info(self.passmsg)
        #set outdoor ap test parameter       
        return ["PASS", self.passmsg]

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'tftp_dir':'D:\\sr_sync\\xml_tar_file'}
        self.conf.update(conf)
        self.tftp_dir=self.conf['tftp_dir']
        self.errmsg = ''
        self.passmsg = 'set parameters successfully'
        
        self.single_band_ap_test_para={}
        self.dule_band_ap_test_para={}
        self.outdoor_ap_test_para={}
        self.US_dfs_channel_test_para={}
        self.dfs_channel_test_para={}
        self.cband_channel_test_para={}
        
        self.ap_list = self.testbed.components['AP']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.ap_mac_list=self.testbed.get_aps_mac_list() 
        self.model_to_mac_list = self.testbed.model_to_mac_list
        self.mac_to_ap=self.testbed.mac_to_ap
        self.model_to_ap_list = {}
        for model in self.model_to_mac_list:
            self.model_to_ap_list[model]=[]
            for mac in self.model_to_mac_list[model]:
                self.model_to_ap_list[model].append(self.mac_to_ap[mac])
        self.sw=self.testbed.components['L3Switch']
        self.ap_sw_port_list=[]
        for mac in self.ap_mac_list:
            self.ap_sw_port_list.append(self.sw.mac_to_interface(mac))
        
    def _update_carrier_bag(self):
        self.carrierbag['test_para']={}
        self.carrierbag['test_para']['single_band_ap_test_para'] =self.single_band_ap_test_para
        self.carrierbag['test_para']['dule_band_ap_test_para']   =self.dule_band_ap_test_para
        self.carrierbag['test_para']['outdoor_ap_test_para']     =self.outdoor_ap_test_para
        self.carrierbag['test_para']['US_dfs_channel_test_para'] =self.US_dfs_channel_test_para
        self.carrierbag['test_para']['dfs_channel_test_para']    =self.dfs_channel_test_para
        self.carrierbag['test_para']['cband_channel_test_para']  =self.cband_channel_test_para
        self.carrierbag['test_para']['uk_cband_channel_test_para']  =self.uk_cband_channel_test_para
        self.carrierbag['test_para']['precedency_para']  =self.precedency_para
        self.carrierbag['test_para']['backup_para']  =self.backup_para
        self.carrierbag['country_para']  =self.country_para
        self.carrierbag['out_door_ap_list']  =self.out_door_ap_list
        self.carrierbag['ap_sw_port_list']  =self.ap_sw_port_list
           
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['single_band_ap_test_para']['ap'])
        logging.info('single_band_ap %s'%mac_list)
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['dule_band_ap_test_para']['ap'])
        logging.info('dule_band_ap %s'%mac_list)
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['outdoor_ap_test_para']['ap'])
        logging.info('outdoor_ap %s'%mac_list)
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['US_dfs_channel_test_para']['ap'])
        logging.info('US_dfs_channel %s'%mac_list)
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['dfs_channel_test_para']['ap'])
        logging.info('dfs_channel %s'%mac_list)
        mac_list=self._get_ap_list_mac(self.carrierbag['test_para']['cband_channel_test_para']['ap'])
        logging.info('cband_channel %s'%mac_list)
        
        
    def _get_ap_list_mac(self,ap_list):
        mac_list=[]
        for ap in ap_list:
            for mac in self.mac_to_ap:
                if self.mac_to_ap[mac]==ap:
                    mac_list.append(mac)
                    break
        return mac_list

