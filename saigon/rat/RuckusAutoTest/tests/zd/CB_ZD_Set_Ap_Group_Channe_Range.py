# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
set parameter used by Manual Available Channel Selection cases
put them in carrierbag
"""

import logging
import random
import copy
import time

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components.lib.zd import access_points_zd
from RuckusAutoTest.components.lib.apcli import radiogroup
from RuckusAutoTest.common import lib_List


class CB_ZD_Set_Ap_Group_Channe_Range(Test):
    def config(self, conf):
        self._retrive_carrierbag()
        self._cfg_init_test_params(conf)
        
        if self.ap_group_name != 'System Default':
            ap_group.clear_channel_selection_related_settings(self.zd, self.ap_group_name)
            
        for ap in self.ap_list:
            ap_mac=self._get_ap_mac(ap)
            access_points_zd.disable_channel_selection_related_group_override(self.zd,ap_mac)
            access_points_zd.set_ap_general_by_mac_addr(self.zd,ap_mac,ap_group=self.ap_group_name)
        
        self._set_channlization()
        
        
    def test(self):
        if self.test_type =='single_band_ap':
            self._single_band_ap_test()
        elif self.test_type == 'dule_band_country':
            self._dule_band_ap_test()
        elif self.test_type == 'outdoor_ap':
            self._out_door_ap_test()
        elif self.test_type == 'US_dfs_channel':
            self._us_dfs_channel_test()
        elif self.test_type == 'dfs_channel':
            self._dfs_channel_test()
        elif self.test_type == 'cband_channel':
            self._cband_channel_test()
        elif self.test_type == 'uk_cband_channel':
            self._cband_channel_test()
        else :
            self.errmsg='test type %s not correct'%self.test_type
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'ap_group':''}
        self.conf.update(conf)
        
        #default ap group or new ap group
        if self.apg =='default':
            self.ap_group_name = 'System Default'
            self.set_para_group = 'System Default'
        else:
            self.ap_group_name = self.conf['ap_group']
            self.set_para_group=random.choice['System Default',self.ap_group_name]
        
        logging.info('for this test,I will add ap to ap group %s,and set parameter from apgroup %s'
                     %(self.ap_group_name,self.set_para_group))
        
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = 'test %s manual available channel selection OK'%self.test_type
        self.errmsg=''
        
    
    def _retrive_carrierbag(self):
        self.test_para=self.carrierbag['channel_selection_test_para']
        
        self.test_type = self.test_para['test_type']
        self.ap_list = self.test_para['ap']
        logging.info('use ap %s to do test'%self.ap_list)
        self.apg = self.test_para['apg']
        self.ctry = self.test_para['ctry']
        self.set_para_way = self.test_para['set_para_way']
        self.channlization = self.test_para['channlization']
        
        if self.test_para.has_key('channel_optimization'):
            self.channel_optimization = self.test_para['channel_optimization']
        if self.test_para.has_key('allow_indoor_channel'):
            self.allow_indoor = self.test_para['allow_indoor_channel']
        
        self.ctry_para = self.carrierbag['country_para'][self.ctry]
        self.out_door_ap_list=self.carrierbag['out_door_ap_list']

    def _single_band_ap_test(self):
        channel_list=self.ctry_para['channels-11bg']
        ap = self.ap_list[0]
        ap_group = self.set_para_group
        #verify the channel display is correct on ap page and ap group page
        if not self._verify_channel_display(ap,ap_group,channel_list,[],True):
            return
        #verify set channel can take effect
        model=self._get_ap_model(ap)
        if model.startwith('7'):
            radio = 'ng'
        else:
            radio = 'bg'
        res=self._verify_channel_deploy_to_ap(radio,ap,channel_list)
        if not res:
            self.errmsg = 'verify channel deploy from ap cli failed'
            return    
    
    def _dule_band_ap_test(self):
        #not out door ap
        
        ap = self.ap_list[0]
        ap_group = self.set_para_group
        ng_channel_list = self.ctry_para['channels-11bg']
        na_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap)
        
        #verify the channel display is correct on ap page and ap group page
        if not self._verify_channel_display(ap,ap_group,ng_channel_list,na_channel_list):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',ap,na_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return  
        
    def _out_door_ap_test(self):
        outdoor_ap,indoor_ap= self.ap_list
        ap_group = self.set_para_group
        ng_channel_list = self.ctry_para['channels-11bg']
        na_channel_list = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,indoor_ap)
        na_outdoor_channel_list = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,outdoor_ap,alow_indoor=False)
        
        #verify the channel display is correct on ap page and ap group page when allow indoor channel enable
        if not self._verify_channel_display(outdoor_ap,ap_group,ng_channel_list,na_channel_list):
            return
        if not self._verify_channel_display(indoor_ap,ap_group,ng_channel_list,na_channel_list):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',outdoor_ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',outdoor_ap,na_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
        
        #verify the channel display is correct on ap page and ap group page when not allow indoor channel disabled
        self.zd.set_country_code(country_code = "", optimize=None, allow_indoor =True,set_country_code=False)
        logging.info('waiting aps reconnect after enable indoor ap')
        time.sleep(60)
        if not self._verify_channel_display(outdoor_ap,ap_group,ng_channel_list,na_channel_list):
            return
        if not self._verify_channel_display(indoor_ap,ap_group,ng_channel_list,na_channel_list):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',outdoor_ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',outdoor_ap,na_outdoor_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
                
        res=self._verify_channel_deploy_to_ap('na',indoor_ap,na_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
                
    def _us_dfs_channel_test(self):
        #at first allow dfs should be opened
        dfs_ap,no_dfs_ap=self.ap_list
        ap_group = self.set_para_group
        
        ng_channel_list = self.ctry_para['channels-11bg']
        dfs_ap_use_dfs=True
        no_dfs_ap_use_dfs=False
        only_centrino=False
        if self.channel_optimization == 'Interoperability':
            only_centrino=True

        no_dfs_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,no_dfs_ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=no_dfs_ap_use_dfs, only_centrino=only_centrino)
        dfs_channel_list = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,dfs_ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=dfs_ap_use_dfs, only_centrino=only_centrino)
        
        #verify the channel display is correct on ap page and ap group page when allow dfs channel
        if not self._verify_channel_display(dfs_ap,ap_group,ng_channel_list,dfs_channel_list):
            return
        if not self._verify_channel_display(no_dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',dfs_ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',dfs_ap,dfs_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
        #verify the channel display is correct on ap page and ap group page when not allow dfs channel
        self.zd.set_country_code(country_code = "", optimize='compatibility', allow_indoor =None,set_country_code=False)
        logging.info('waiting aps reconnect after disable dfs channel')
        time.sleep(60)
        no_dfs_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,no_dfs_ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=False, only_centrino=False)
        if not self._verify_channel_display(dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
            return
        if not self._verify_channel_display(no_dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',dfs_ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',dfs_ap,no_dfs_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
    def _dfs_channel_test(self):
        self._dule_band_ap_test()
    
    def _cband_channel_test(self):
        ap=self.ap_list[0]
        ap_group = self.set_para_group
        ng_channel_list = self.ctry_para['channels-11bg']
        channel_list_with_cband=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=True, only_centrino=False, 
                                           cband_channel_list=self.ctry_para['cband-channels-11a'],use_cband=True)
        
        channel_list_without_cband = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=True, only_centrino=False, 
                                           cband_channel_list=self.ctry_para['cband-channels-11a'],use_cband=False)
        
        #enable cband channel and verify
        self._cfg_cband_channel(ap)
        if not self._verify_channel_display(ap,ap_group,ng_channel_list,channel_list_with_cband):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',ap,channel_list_with_cband)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
        #disable cband channel and verify
        self._cfg_cband_channel(ap,False)
        if not self._verify_channel_display(ap,ap_group,ng_channel_list,channel_list_without_cband):
            return
        
        res=self._verify_channel_deploy_to_ap('ng',ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',ap,channel_list_without_cband)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
    def _verify_channel_deploy_to_ap(self,radio,ap,channel_list):  
        channel_idx_list = range(1,len(channel_list)+1)
        enabled_channel_idx_list=self._get_random_enable_channel_idx(channel_idx_list)
        logging.info('enable channel index list got %s'%enabled_channel_idx_list)   
        enable_channel_list=self._get_channel_list_from_channel_idx_list(enabled_channel_idx_list,channel_list)
        logging.info('enable channel list got %s'%enable_channel_list) 
        
        self._set_channel_range(ap,radio,enabled_channel_idx_list) 
        return self._verify_channel_setting_in_ap(ap,radio,enable_channel_list) 

    def _verify_channel_display(self,ap,ap_group,channel_list_2_4G,channel_list_5_0G=[],only_2_4G=False,initial=True):
        mac = self._get_ap_mac(ap)
        if ap in self.out_door_ap_list:
            out_door=True
        else:
            out_door=False
        ap_model='zf'+self._get_ap_model(ap)
        res=self._verify_2_4G_ap_channel_display(ap,channel_list_2_4G)
        if not res:
            self.errmsg = 'verify ap page(%s) 2.4 G channel display failed'%mac
            return False
        
        if initial or self.set_para_way == 'group':
            res=self._verify_2_4G_apg_channel_display(ap_group,channel_list_2_4G)
            if not res:
                self.errmsg = 'verify apgroup page(%s) 2.4 G channel display failed'%ap_group
                return False
        
        if not only_2_4G:
            res=self._verify_5_0G_ap_channel_display(ap,channel_list_5_0G)
            if not res:
                self.errmsg = 'verify ap page(%s) 5.0 G channel display failed'%mac
                return False
            if initial or self.set_para_way == 'group':
                res=self._verify_5_0G_apg_channel_display(ap_group,channel_list_5_0G,ap_model,out_door)
                if not res:
                    self.errmsg = 'verify apgroup page(%s) 5.0 G channel display failed'%ap_group
                    return False
        return True
            
    def _get_ap_model(self,ap):
        return ap.get_model_display().split()[1]
    
    def _get_ap_mac(self,ap):
        return ap.base_mac_addr
    
    def _set_channlization(self):
        if self.set_para_way == 'group':
            logging.info('set channlization %s from apgroup %s'%(self.channlization,self.set_para_group))
            ap_group.set_channelization(self.zd, self.set_para_group, self.channlization)
        else:
            for ap in self.ap_list:
                mac_addr=self._get_ap_mac(ap)
                logging.info('set channlization %s from ap %s'%(self.channlization,mac_addr))
                access_points_zd.set_channelization(self.zd, mac_addr,self.channlization)
    
    def _get_random_enable_channel_idx(self,channel_idx_list):#parameter is channel list or channel index list
        '''
        in channel_list or channel index list(depands on the parameter you give),
        chose 1~len(channel_list) channel to enable
        '''
        number = random.choice(range(1,len(channel_idx_list)+1))
        return self._get_random_members_from_list(channel_idx_list,number)
    

    def _set_channel_range(self,ap,radio,channel_idx_list):
        if self.set_para_way == 'group':
            if radio == 'bg':
                radio='ng'
            if ap in self.out_door_ap_list:
                out_door=True
            else:
                out_door=False
            logging.info('set channel range %s from apgroup %s'%(channel_idx_list,self.set_para_group))
            ap_group.set_channel_range(self.zd, self.set_para_group,True,radio,out_door,channel_idx_list)
        else:
            mac_addr= self._get_ap_mac(ap)
            logging.info('set channel range %s from ap %s'%(channel_idx_list,mac_addr))
            access_points_zd.set_channel_range(self.zd, mac_addr,True,radio,channel_idx_list)

    def _cfg_cband_channel(self,ap,enable=True):
        mac_addr = self._get_ap_mac(ap)
        ap_model = self._get_ap_model(ap)
        if self.set_para_way == 'group':
            logging.info('configure cband channel %s from apgroup %s'%(enable,self.set_para_group))
            ap_group.cfg_5_8G_channel(self.zd,self.set_para_group,ap_model,override=True,enable=enable)
        else:
            logging.info('configure cband channel %s from ap %s'%(enable,mac_addr))
            access_points_zd.config_5_8G_channel(self.zd,mac_addr,override=True,enable=enable)

    def _verify_2_4G_ap_channel_display(self,ap,channel_list):
        model=self._get_ap_model(ap)
        if model.startwith('7'):
            radio = 'ng'
        else:
            radio = 'bg'
        mac_addr= self._get_ap_mac(ap)
        return access_points_zd.verify_channel_range(self.zd, mac_addr,channel_list, radio)
    
    def _verify_5_0G_ap_channel_display(self,ap,channel_list):
        radio = 'na'
        mac_addr= self._get_ap_mac(ap)
        return access_points_zd.verify_channel_range(self.zd, mac_addr,channel_list, radio)
    
            
    def _verify_2_4G_apg_channel_display(self,ap_group,channel_list):
        radio = 'ng'
        return ap_group.verify_channel_range(self.zd, ap_group, channel_list,'', radio)
    
    
    def _verify_5_0G_apg_channel_display(self,ap_group,channel_list,ap_model,outdoor):
        radio = 'na'
        return ap_group.verify_channel_range(self.zd, ap_group, channel_list,ap_model, radio,outdoor)

    def _verify_channel_setting_in_ap(self,ap,radio,channel_list):
        if radio=='bg' or radio=='ng':
            wifi_if='wifi0'
        else:    
            wifi_if='wifi1'
        return radiogroup.verify_available_channel_list(ap,channel_list,wifi_if)
    
    def _get_random_members_from_list(self,source_list,get_number):
        '''
        from source_list random get a number of members and put them in the result
        for example:
        source_list = [1,2,3,4,5,]  get_number =2
        return [1,2] or [1,4] or [2,5] and so on
        '''
        list1=copy.copy(source_list)
        res = []
        for i in range(1,get_number+1):
            random_member=random.choice(list1)
            list1.remove(random_member)
            res.append(random_member)
            res.sort()
        return res
    
    def _get_channel_list_from_channel_idx_list(self,channel_idx_list,channel_list):
        res = []
        for idx in channel_idx_list:
            res.append(channel_list[idx])
        return res
    
    def _get_ap_11a_desplayed_channel_list(self,channel_list_11a,Channelization,ap,dfs_channel_list=[],centrino_channel_list=[],
                                           alow_indoor=True,use_dfs=True, only_centrino=False, cband_channel_list=[],use_cband=False):
        if ap in self.out_door_ap_list:
            out_door=True
        else:
            out_door=False
        res=[]
        paired=1
        for channel in channel_list_11a:
            if(use_dfs or (not(channel in dfs_channel_list))):
                if ((not only_centrino) or (channel in centrino_channel_list)):
                    if not((Channelization=='40') and paired and (not((channel+4) in channel_list_11a))):
                        if (not out_door) or alow_indoor or (channel in self.ctry_para['out_door_channel']):
                            res.append(channel)
        
        if use_cband and cband_channel_list:
            for channel in cband_channel_list:
                if (use_dfs or (not(channel in dfs_channel_list))):
                    if not((Channelization=='40') and (not((channel+4) in cband_channel_list))):
                        res.append(channel)
                        
        return res

    
    def _get_apg_11a_desplayed_channel_list(self,channel_list_11a,Channelization,out_door,dfs_channel_list=[],centrino_channel_list=[],
                                           alow_indoor=True,use_dfs=True, only_centrino=False, cband_channel_list=[],use_cband=False):
        res=[]
        paired=1
        for channel in channel_list_11a:
            if(use_dfs or (not(channel in dfs_channel_list))):
                if ((not only_centrino) or (channel in centrino_channel_list)):
                    if not((Channelization=='40') and paired and (not((channel+4) in channel_list_11a))):
                        if (not out_door) or alow_indoor or (channel in self.ctry_para['out_door_channel']):
                            res.append(channel)
        
        if use_cband and cband_channel_list:
            for channel in cband_channel_list:
                if (use_dfs or (not(channel in dfs_channel_list))):
                    if not((Channelization=='40') and (not((channel+4) in cband_channel_list))):
                        res.append(channel)
                        
        return res            
    