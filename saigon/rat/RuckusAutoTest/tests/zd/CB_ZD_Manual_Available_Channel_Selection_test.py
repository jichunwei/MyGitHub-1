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
from RuckusAutoTest.components.lib.zd import admin_backup_restore_zd as bk
from RuckusAutoTest.common import lib_Constant as constant


class CB_ZD_Manual_Available_Channel_Selection_test(Test):
    def config(self, conf):
        self._retrive_carrierbag()
        self._cfg_init_test_params(conf)
        if not self.test_type=='mesh_test':
            if self.ap_group_name != 'System Default':
                ap_group.clear_channel_selection_related_settings(self.zd, self.ap_group_name)
                    
            for ap in self.ap_list:
                ap_mac=self._get_ap_mac(ap)
                access_points_zd.disable_channel_selection_related_group_override(self.zd,ap_mac)
                if self.conf['ap_group']:
                    logging.info('add ap %s to apgroup %s'%(ap_mac,self.ap_group_name))
                    access_points_zd.set_ap_general_by_mac_addr(self.zd,ap_mac,ap_group=self.ap_group_name)
                    
        if not (self.test_type == 'mesh_test' or self.test_type == 'single_band_ap'):
            self._set_channlization()
            if not self.test_type == 'precedency':
                self.enable_all_channel()
        
        #just for mesh test, disable all sw port connect to aps except those connected to mesh ap and root ap
        if self.mesh_ap_mac and self.root_ap_mac:
            mesh_ap_port = self.sw.mac_to_interface(self.mesh_ap_mac)
            root_ap_port = self.sw.mac_to_interface(self.root_ap_mac)
            for port in self.ap_sw_port_list:
                if not(port==mesh_ap_port or port==root_ap_port):
                    self.sw.disable_interface(port)
            self.mesh_ap_port=mesh_ap_port
            self.event_msg = self.zd.messages['MSG_AP_lost_heartbeat'].replace('{ap}','AP[%s]'%self.mesh_ap_mac)


    def test(self):
        logging.info('ready to begin testing,test type is %s'%self.test_type)
        
        if self.test_type =='single_band_ap':
            self._single_band_ap_test()
        elif self.test_type == 'dule_band_ap':
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
        elif self.test_type == 'precedency':
            self._configuration_precedence_test()
        elif self.test_type == 'mesh_test':
            self._mesh_test()
        elif self.test_type == 'backup':
            self._backup_test()
        else :
            self.errmsg='test type %s not correct'%self.test_type
            
        if self.errmsg:
            return 'FAIL',self.errmsg  
        else:
            self._update_carrierbag()
            return ["PASS", self.passmsg]
    
    def cleanup(self):
        if self.mesh_ap_mac:
            logging.info('this test is for mesh test,enable all switch port connected to aps')
            for port in self.ap_sw_port_list:
                logging.info('enable switch port %s'%port)
                self.sw.enable_interface(port)
                
        for ap in self.ap_list:
            ap_mac=self._get_ap_mac(ap)
            if self.conf['ap_group']:
                logging.info('add ap %s to apgroup System Default'%ap_mac)
                access_points_zd.set_ap_general_by_mac_addr(self.zd,ap_mac,ap_group='System Default')

    def _cfg_init_test_params(self, conf):
        self.conf={'ap_group':''}
        self.conf.update(conf)
        if self.conf.has_key('test_type'):
            self.test_type=self.conf['test_type']
            
        self.ap_mac_list=self._get_aps_mac_list(self.ap_list)
        if not self.test_type=='mesh_test':
            #default ap group or new ap group
            if self.apg =='default':
                self.ap_group_name = 'System Default'
                self.set_para_group = 'System Default'
            else:
                self.ap_group_name = self.conf['ap_group']
                self.set_para_group=random.choice(['System Default',self.ap_group_name])
            
            logging.info('for this test,I will add ap to ap group %s'%(self.ap_group_name))
            
            if self.set_para_way == 'group':
                logging.info('set parameter from apgroup %s'%(self.set_para_group))
            else:
                logging.info('set parameter from aps %s'%self.ap_mac_list)
        
            
        self.zd = self.testbed.components['ZoneDirector']
        self.sw = self.testbed.components['L3Switch']
        self.mesh_ap_mac=self.conf.get('mesh_ap_mac')
        self.root_ap_mac=self.conf.get('root_ap_mac')
        self.passmsg = 'test %s manual available channel selection OK'%self.test_type
        self.errmsg=''
        
    
    def _retrive_carrierbag(self):
        if self.carrierbag.has_key('channel_selection_test_para'):
            self.test_para=self.carrierbag['channel_selection_test_para']
        
            self.test_type = self.test_para['test_type']
            self.ap_list = self.test_para['ap']
            logging.info('use ap %s to do test'%self._get_aps_mac_list(self.ap_list))
            
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
        self.ap_sw_port_list=self.carrierbag['ap_sw_port_list']
    def _update_carrierbag(self):
        if self.test_type == 'backup':
            self.carrierbag['restore_file_path'] = self.back_path
            self.carrierbag['backed_channel_info']={'ap':self.ap_list[0],
                                                    'ng_channel_list':self.backup_ng_channel_list,
                                                    'na_channel_list':self.backup_na_channel_list,
                                                    }
            
    def _single_band_ap_test(self):
        channel_list=self.ctry_para['channels-11bg']
        ap = self.ap_list[0]
        ap_group = self.set_para_group
        #verify the channel display is correct on ap page and ap group page
        if not self._verify_channel_display(ap,ap_group,channel_list,[],True):
            return
        #verify set channel can take effect
        model=self._get_ap_model(ap)
        if model.startswith('7'):
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
        self.zd.set_country_code(country_code = "", optimize=None, allow_indoor = False,set_country_code=False)
        logging.info('waiting aps reconnect after enable indoor ap')
        time.sleep(60)
        self._set_channlization()
        time.sleep(60)
        self.enable_all_channel()
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
            self.errmsg = 'verify na channel deploy from outdoor ap cli failed'
            return 
                
        res=self._verify_channel_deploy_to_ap('na',indoor_ap,na_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from indoor ap cli failed'
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
        
        
#        no_dfs_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,no_dfs_ap,
#                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
#                                           alow_indoor=self.allow_indoor,use_dfs=no_dfs_ap_use_dfs, only_centrino=only_centrino)
        dfs_channel_list = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,dfs_ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=dfs_ap_use_dfs, only_centrino=only_centrino)
        
        logging.info('verify the channel display is correct on ap page and ap group page when allow dfs channel')
        #verify the channel display is correct on ap page and ap group page when allow dfs channel
        logging.info('begin dfs ap channel list display verify')
        if not self._verify_channel_display(dfs_ap,ap_group,ng_channel_list,dfs_channel_list):
            return
#        logging.info('begin no dfs ap channel list display verify')
#        if not self._verify_channel_display(no_dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
#            return
        
        res=self._verify_channel_deploy_to_ap('ng',dfs_ap,ng_channel_list)
        if not res:
            self.errmsg = 'verify ng channel deploy from ap cli failed'
            return  
        
        res=self._verify_channel_deploy_to_ap('na',dfs_ap,dfs_channel_list)
        if not res:
            self.errmsg = 'verify na channel deploy from ap cli failed'
            return 
        
        logging.info('verify the channel display is correct on ap page and ap group page when not allow dfs channel')
        #verify the channel display is correct on ap page and ap group page when not allow dfs channel
        self.zd.set_country_code(country_code = "", optimize='compatibility', allow_indoor =None,set_country_code=False)
        logging.info('waiting aps reconnect after disable dfs channel')
        time.sleep(60)
        self._set_channlization()
        self.enable_all_channel()
        no_dfs_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,dfs_ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=False, only_centrino=False)
        
        logging.info('begin dfs ap channel list display verify')
        if not self._verify_channel_display(dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
            return
#        logging.info('begin no dfs ap channel list display verify')
#        if not self._verify_channel_display(no_dfs_ap,ap_group,ng_channel_list,no_dfs_channel_list):
#            return
        
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
        logging.info('channel with cband %s'%channel_list_with_cband)
        
        channel_list_without_cband = self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap,
                                            dfs_channel_list=self.ctry_para['dfs-channels-11a'],centrino_channel_list=self.ctry_para['centrino-channels-11a'],
                                           alow_indoor=self.allow_indoor,use_dfs=True, only_centrino=False, 
                                           cband_channel_list=self.ctry_para['cband-channels-11a'],use_cband=False)
        logging.info('channel without cband %s'%channel_list_without_cband)
        
        #enable cband channel and verify
        logging.info('begin cband channel enable test')
        self._cfg_cband_channel(ap)
        self.enable_all_channel()
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
        logging.info('begin cband channel disable test')
        self._cfg_cband_channel(ap,False)
        self.enable_all_channel()
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

    def _configuration_precedence_test(self):
        '''
        per ap config->ap group->default ap Group
        '''
        ap = self.ap_list[0]
        default_ap_group = 'System Default'
        new_ap_group = self.conf['ap_group']
        mac_addr=self._get_ap_mac(ap)
        ng_channel_list = self.ctry_para['channels-11bg']
        na_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap)
        
        #default ap group ng_channel_list[0],na_channel_list[0]
        #        ap group ng_channel_list[1],na_channel_list[1]
        #        ap       ng_channel_list[2],na_channel_list[2]
        
        #ng channel test
        #set default apgroup->apgroup->ap
        logging.info('begin testing ng channel setting')
        logging.info('setting in default apg')
        ap_group.set_channel_range(self.zd,default_ap_group,True,'ng',False,[1])
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[0]]):
            self.errmsg='default ap group ng channel setting setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        
        logging.info('setting in apg')
        ap_group.set_channel_range(self.zd,new_ap_group,True,'ng',False,[2])
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[1]]):
            self.errmsg='ap group ng channel setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        
        logging.info('setting in ap')
        access_points_zd.set_channel_range(self.zd, mac_addr,True,'ng',[3])
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[2]]):
            self.errmsg='ap ng channel setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        logging.info('test ng channel setting successfully,1 default apgroup,2 apgroup,3 ap')
        
        logging.info('begin testing na channel setting')
        #na channel test
        #set ap->apgroup->default apgroup
        
        logging.info('setting in ap')
        access_points_zd.set_channel_range(self.zd, mac_addr,True,'na',[3])
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[2]]):
            self.errmsg='ap na channel setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        
        logging.info('setting in apg')
        ap_group.set_channel_range(self.zd,new_ap_group,True,'na',False,[2])
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[2]]):
            self.errmsg='after set apgroup channel,ap na channel setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        
        logging.info('setting in default apg')
        ap_group.set_channel_range(self.zd,default_ap_group,True,'na',False,[1])
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[2]]):
            self.errmsg='after default ap group set na channel,ap setting can not deploy to ap'
            logging.error(self.errmsg)
            return
        
        logging.info('disable ap override,channel should the same as ap group')
        #disable ap override,channel should the same as ap group
        access_points_zd.set_channel_range(self.zd, mac_addr,False,'na')
        access_points_zd.set_channel_range(self.zd, mac_addr,False,'ng')
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[1]]):
            self.errmsg='ap group na channel setting can not deploy to ap after disable ap override'
            logging.error(self.errmsg)
            return
        
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[1]]):
            self.errmsg='ap group ng channel setting can not deploy to ap after disable ap override'
            logging.error(self.errmsg)
            return
        
        logging.info('move ap to default ap group,ap channel should the same as default ap group')
        #move ap to default ap group,ap channel should the same as default
        ap_group.move_aps_to_ap_group(self.zd, mac_addr, new_ap_group,default_ap_group)
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[0]]):
            self.errmsg='ap group na channel setting can not deploy to ap after move ap to default ap group'
            logging.error(self.errmsg)
            return
        
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[0]]):
            self.errmsg='ap group ng channel setting can not deploy to ap after move ap to default ap group'
            logging.error(self.errmsg)
            return
    
    
    def _mesh_test(self):
        #get country parameter
        self.ctry = self.zd.get_country_code()['label']
        logging.info('conutry code is %s'%self.ctry)
        self.ctry_para = self.carrierbag['country_para'][self.ctry]
        mesh_ap=self.testbed.mac_to_ap[self.mesh_ap_mac]
        root_ap=self.testbed.mac_to_ap[self.root_ap_mac]
        mesh_name=time.ctime().replace(':','_').replace(' ','_')+'channel_selection'
        ret,msg=self.zd.enable_mesh(mesh_name = mesh_name )
        if not ret:
            self.errmsg=msg
            logging.error(msg)
            return
        logging.info('sleep 1 minutes wait aps enable mesh')
        time.sleep(60)
        ng_channel_list = self.ctry_para['channels-11bg']
        na_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],'40',mesh_ap)
        
        #set mesh ap channel to ng_channel_list[2,3] and na_channel_list[2,3] 
        access_points_zd.set_channel_range(self.zd, self.mesh_ap_mac,True,'ng',[3,4])
        if not self._verify_channel_setting_in_ap(mesh_ap,'ng',[ng_channel_list[2],ng_channel_list[3]]):
            self.errmsg='mesh ap %s ng channel setting can not deploy to ap'%self.mesh_ap_mac
            logging.error(self.errmsg)
            return
        
        access_points_zd.set_channel_range(self.zd, self.mesh_ap_mac,True,'na',[3,4])
        if not self._verify_channel_setting_in_ap(mesh_ap,'na',[na_channel_list[2],na_channel_list[3]]):
            self.errmsg='mesh ap %s na channel setting can not deploy to ap'%self.mesh_ap_mac
            logging.error(self.errmsg)
            return
        
        #set root ap channel to ng_channel_list[0,1] and na_channel_list[0,1] 
        access_points_zd.set_channel_range(self.zd, self.root_ap_mac,True,'na',[1,2])
        if not self._verify_channel_setting_in_ap(root_ap,'na',[na_channel_list[0],na_channel_list[1]]):
            self.errmsg='root_ap %s na channel setting can not deploy to ap'%self.root_ap_mac
            logging.error(self.errmsg)
            return
        
        access_points_zd.set_channel_range(self.zd, self.root_ap_mac,True,'ng',[1,2])
        if not self._verify_channel_setting_in_ap(root_ap,'ng',[ng_channel_list[0],ng_channel_list[1]]):
            self.errmsg='root_ap %s ng channel setting can not deploy to ap'%self.root_ap_mac
            logging.error(self.errmsg)
            return
        
        #clear zd events
        self.zd.clear_all_events()
        #disable sw port connected to mesh ap and check events
        self.sw.disable_interface(self.mesh_ap_port)
        if not self._check_event_continuously(1200):
            self.errmsg = 'heart beat lose msg not fount after disconnect the mesh ap switch port'
            logging.error(self.errmsg)
            return 
        ap_info=self.zd.get_all_ap_info(self.mesh_ap_mac)
        if ap_info['status'].startswith('Connected'):
            self.errmsg = 'mesh ap is connected to zd after disable switch port'
            logging.error(self.errmsg)
            return 
        logging.info('heart beat lose message found and mesh dissconnect from zd')
        
        #enable switch port and verify the channel deployment
        self.sw.enable_interface(self.mesh_ap_port)
        if not self._wait_mesh_ap_connect(120):
            self.errmsg = 'mesh ap not connect after enable switch port 120 seconds'
            logging.error(self.errmsg)
            return 
        
        if not self._verify_channel_setting_in_ap(mesh_ap,'ng',[ng_channel_list[2],ng_channel_list[3]]):
            self.errmsg='mesh ap %s ng channel setting can not deploy to ap after reconnet'%self.mesh_ap_mac
            logging.error(self.errmsg)
            return
        
        if not self._verify_channel_setting_in_ap(mesh_ap,'na',[na_channel_list[2],na_channel_list[3]]):
            self.errmsg='mesh ap %s na channel setting can not deploy to ap after reconnet'%self.mesh_ap_mac
            logging.error(self.errmsg)
            return
        
        logging.info('ap channel deploy correct after reconnect')
    
    def _backup_test(self):
        ap=self.ap_list[0]
        ng_channel_list = self.ctry_para['channels-11bg']
        na_channel_list=self._get_ap_11a_desplayed_channel_list(self.ctry_para['channels-11a'],self.channlization,ap)
        ap_mac=self._get_ap_mac(ap)
        
        access_points_zd.set_channel_range(self.zd, ap_mac,True,'ng',[3,4])
        access_points_zd.set_channel_range(self.zd, ap_mac,True,'na',[3,4])
        
        path = self._backup()
        logging.info('config file is backup at %s'%path)
        
        if not self._verify_channel_setting_in_ap(ap,'ng',[ng_channel_list[2],ng_channel_list[3]]):
            self.errmsg='ap %s ng channel setting can not deploy to ap after backup'%ap_mac
            logging.error(self.errmsg)
            return
        
        if not self._verify_channel_setting_in_ap(ap,'na',[na_channel_list[2],na_channel_list[3]]):
            self.errmsg='ap %s na channel setting can not deploy to ap after backup'%ap_mac
            logging.error(self.errmsg)
            return
        logging.info('ap config is correct after backup')
        access_points_zd.set_channel_range(self.zd, ap_mac,False)
        access_points_zd.set_channel_range(self.zd, ap_mac,False)
        self.back_path=path
        self.backup_ng_channel_list=[ng_channel_list[2],ng_channel_list[3]]
        self.backup_na_channel_list=[na_channel_list[2],na_channel_list[3]]
        access_points_zd.disable_channel_selection_related_group_override(self.zd,ap_mac)
        
    def _backup(self):
        """
        """
        save_to = constant.save_to
        # Go to the Administer --> Backup
        file_path = bk.backup(self.zd, save_to = save_to)
            
        return file_path
    
    def _wait_mesh_ap_connect(self,timeout):
        t0=time.time()
        t1=time.time()
        connected=False
        while (t1-t0<timeout) and not(connected):
            ap_info=self.zd.get_all_ap_info(self.mesh_ap_mac)
            if ap_info['status'].startswith('Connected'):
                connected=True
        return connected
        
                
    def _check_event_continuously(self,timeout):
        t0=time.time()
        t1=time.time()
        event_fonud=False
        while (t1-t0<timeout) and not(event_fonud):
            event_fonud = self._check_event()
        return event_fonud
    
    def _check_event(self):
        # zj 2014-0126 ZF-7269  There is no "get_events_v91()" in ZoneDirctor.py
        #event_list=self.zd.get_events_v91()
        event_list=self.zd.get_events()  
        event_fonud=False
        for event in event_list:
            if str(self.event_msg) == str(event[3]):
                event_fonud=True
                break
        logging.info('event_fonud %s'%event_fonud)
        return event_fonud
        
    
    def _verify_channel_deploy_to_ap(self,radio,ap,channel_list):  
        if not channel_list:
            return True
        channel_idx_list = range(1,len(channel_list)+1)
        enabled_channel_idx_list=self._get_random_enable_channel_idx(channel_idx_list)
        logging.info('enable channel index list got %s'%enabled_channel_idx_list)   
        enable_channel_list=self._get_channel_list_from_channel_idx_list(enabled_channel_idx_list,channel_list)
        logging.info('enable channel list got %s'%enable_channel_list) 
        
        self._set_channel_range(ap,radio,enabled_channel_idx_list) 
        return self._verify_channel_setting_in_ap(ap,radio,enable_channel_list) 

    def _verify_channel_display(self,ap,ap_group,channel_list_2_4G,channel_list_5_0G=[],only_2_4G=False,initial=False):
        mac = self._get_ap_mac(ap)
        if ap in self.out_door_ap_list:
            out_door=True
            logging.info('ap is outdoor ap')
        else:
            out_door=False
            logging.info('ap is indoor ap')
        ap_model='zf'+self._get_ap_model(ap)
        ap_model=ap_model.lower()
        
        
        if self.set_para_way == 'group':
            res=self._verify_2_4G_apg_channel_display(ap_group,channel_list_2_4G)
            if not res:
                self.errmsg = 'verify apgroup page(%s) 2.4 G channel display failed'%ap_group
                return False
        else:
            res=self._verify_2_4G_ap_channel_display(ap,channel_list_2_4G)
            if not res:
                self.errmsg = 'verify ap page(%s) 2.4 G channel display failed'%mac
                return False
            
        if not only_2_4G:
            if not self.set_para_way == 'group':
                logging.info('begin ap page channel display verify')
                res=self._verify_5_0G_ap_channel_display(ap,channel_list_5_0G)
                if not res:
                    self.errmsg = 'verify ap page(%s) 5.0 G channel display failed'%mac
                    return False
            
            else:
                logging.info('begin ap group page channel display verify (%s)'%ap_group)
                res=self._verify_5_0G_apg_channel_display(ap_group,channel_list_5_0G,ap_model,out_door)
                if not res:
                    self.errmsg = 'verify apgroup page(%s) 5.0 G channel display failed'%ap_group
                    return False
        return True
            
    def _get_ap_model(self,ap):
        return ap.get_model_display().split()[1]
    
    def _get_ap_mac(self,ap):
        return ap.base_mac_addr    
    
    def _get_aps_mac_list(self,ap_list):
        res = []
        for ap in ap_list:
            res.append(ap.base_mac_addr)
        return res
    
    def _set_channlization(self):
#        if str(self.channlization)=='20':
#            import pdb
#            pdb.set_trace()
        
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
   
    def enable_all_channel(self):
        if self.test_type =='single_band_ap':
            radio_list = ['bg']
        else:
            radio_list = ['ng','na']
        for ap in self.ap_list:
            for radio in radio_list:
                self._enable_all_channel(ap,radio)
            
    def _enable_all_channel(self,ap,radio):
        if self.set_para_way == 'group':
            if radio == 'bg':
                radio='ng'
            if ap in self.out_door_ap_list:
                out_door=True
            else:
                out_door=False
            logging.info('enable all channel from apgroup %s'%(self.set_para_group))
            ap_group.enable_all_channel(self.zd, self.set_para_group)
        else:
            mac_addr= self._get_ap_mac(ap)
            logging.info('enable all channel from ap %s'%(mac_addr))
            access_points_zd.enable_all_channel(self.zd, mac_addr,radio)

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
        ap_model = ('zf'+self._get_ap_model(ap)).lower()
        if self.set_para_way == 'group':
            logging.info('configure cband channel %s from apgroup %s'%(enable,self.set_para_group))
            ap_group.cfg_5_8G_channel(self.zd,self.set_para_group,ap_model,override=True,enable=enable)
        else:
            logging.info('configure cband channel %s from ap %s'%(enable,mac_addr))
            access_points_zd.config_5_8G_channel(self.zd,mac_addr,override=True,enable=enable)

    def _verify_2_4G_ap_channel_display(self,ap,channel_list):
        model=self._get_ap_model(ap)
        if model.startswith('7'):
            radio = 'ng'
        else:
            radio = 'bg'
        mac_addr= self._get_ap_mac(ap)
        return access_points_zd.verify_channel_range(self.zd, mac_addr,channel_list, radio)
    
    def _verify_5_0G_ap_channel_display(self,ap,channel_list):
        radio = 'na'
        mac_addr= self._get_ap_mac(ap)
        return access_points_zd.verify_channel_range(self.zd, mac_addr,channel_list, radio)
    
            
    def _verify_2_4G_apg_channel_display(self,apg,channel_list):
        radio = 'ng'
        return ap_group.verify_channel_range(self.zd, apg, channel_list,'', radio)
    
    
    def _verify_5_0G_apg_channel_display(self,apg,channel_list,ap_model,outdoor):
        radio = 'na'
        return ap_group.verify_channel_range(self.zd, apg, channel_list,ap_model, radio,outdoor)

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
            res.append(channel_list[idx-1])
        return res
    
    def _get_ap_11a_desplayed_channel_list(self,channel_list_11a,Channelization,ap,dfs_channel_list=[],centrino_channel_list=[],
                                           alow_indoor=True,use_dfs=True, only_centrino=False, cband_channel_list=[],use_cband=False):

        if ap in self.out_door_ap_list:
            out_door=True
            logging.info('ap is a outdoor ap')
        else:
            out_door=False
            logging.info('ap is a indoor ap')
        res=[]
        paired=1
        for channel in channel_list_11a:
            if(use_dfs or (not(channel in dfs_channel_list))):
                if ((not only_centrino) or (channel in centrino_channel_list)):
                    if not((Channelization=='40') and paired and (not((channel+4) in channel_list_11a))):
                        if (not out_door) or alow_indoor or (channel in self.ctry_para['out_door_channel']):
                            res.append(channel)
                        if paired:
                            paired = 0
                        else:
                            paired = 1
        
        if use_cband and cband_channel_list:
            for channel in cband_channel_list:
                if (use_dfs or (not(channel in dfs_channel_list))):
                    if not((Channelization=='40') and (not((channel+4) in cband_channel_list))):
                        res.append(channel)
        logging.info('the ap channel get %s'%res)
                        
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
                        if paired:
                            paired = 0
                        else:
                            paired = 1
        
        if use_cband and cband_channel_list:
            for channel in cband_channel_list:
                if (use_dfs or (not(channel in dfs_channel_list))):
                    if not((Channelization=='40') and (not((channel+4) in cband_channel_list))):
                        res.append(channel)
                        
        return res            
    