'''
Created on 2011-3-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the ZD CLI roles' configuration in ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import roles


class CB_ZD_CLI_Verify_Roles_Cfg_In_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRoleCfgInGUI()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        #@author: Liang Aihua,@change: some params not exist,@since: 2014-11-19
        #for role_cfg in conf['role_cfg_list']:
        #    if role_cfg.has_key('allow_all_wlans') and role_cfg['allow_all_wlans'] == True:
        #        del role_cfg['specify_wlan_list']
        #    if role_cfg.has_key('allow_zd_admin') and role_cfg['allow_zd_admin'] == False:
        #        del role_cfg['zd_admin_mode']
            
        self.cli_cfg_list = conf['role_cfg_list']
        self.gui_info_list = self.carrierbag['zdgui_role_info_list']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyRoleCfgInGUI(self):
        logging.info("Verify the roles' configuration in ZD GUI.")
        try:
            cli_len = len(self.cli_cfg_list)
            gui_len = len(self.gui_info_list)
        
            if cli_len != gui_len:
                self.errmsg = 'The number of roles in cli_cfg_list [%s] is not the same as in gui_info_list [%s]' % (cli_len, gui_len)
                return
            
            for i in range(gui_len):
                for j in range(cli_len):
                    gui_info_dict = self.gui_info_list[i]
                    cli_cfg_dict = self.cli_cfg_list[j]
                    if cli_cfg_dict.get('new_role_name'):
                        cli_cfg_dict['role_name'] = cli_cfg_dict['new_role_name']
                        
                    if gui_info_dict['role_name'] == cli_cfg_dict['role_name']:
                        res, msg = roles.verify_cli_admin_cfg_in_gui(cli_cfg_dict, gui_info_dict)
                        if res:
                            break
                        else:
                            self.errmsg = msg
                            return
                        
                    elif j == cli_len - 1:
                        self.errmsg = 'The role [%s] exists in ZD GUI, but not in ZD CLI cfg' % self.gui_info_list[i]['role_name']
                        return
                    
            self.passmsg = "All roles' information shown in ZD GUI is the same as in ZD CLI cfg"
            
        except Exception, ex:
            self.errmsg = ex.message
