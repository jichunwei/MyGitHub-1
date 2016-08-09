'''
Created on Nov 11, 2014

@author: lz
'''
import os
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg():
    test_cfgs = []

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

#testcase 1 
    test_case_name = '[SRP calculates]'
    num = 0
    idx = '1.%s'
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))
    
    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'license_type':'random',
                       'file_name':'active_zd_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'active_zd_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'active_zd_increase_random.lic',
                       'zd_tag':'active_zd',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%s%sFailover the active ZD' %(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for new active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'license_type':'random',
                       'file_name':'active_zd_increase_random.lic'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for new active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'active_zd_increase_random.lic'},
                      test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the temp license to new active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'active_zd_increase_random.lic',
                       'zd_tag':'active_zd',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete the license on new active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%s%sFailover the active ZD' %(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete the license on previous active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, True))
#testcase 2
    num = 0
    idx = '2.%s'
    test_case_name = '[SRP MAX limitation]'

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli1',
                       'license_type':'over_half',
                       'file_name':'zd1_increase_over_half.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd1_increase_over_half.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd1_increase_over_half.lic',
                       'zd_tag':'zd1',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli2',
                       'license_type':'over_half',
                       'file_name':'zd2_increase_over_half.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd2_increase_over_half.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd2_increase_over_half.lic',
                       'zd_tag':'zd2',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete the license on active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%s%sFailover the active ZD' %(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete the license on new active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, True))
#testcase 3

    test_case_name = '[SRP holds within 60 days]'
    num = 0
    idx = '3.%s'

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,1,False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'standby_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Degraded'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Config_SR_Cluster_Timer'
    common_name = '%s%sConfigure cluster timer to let it expire fast' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Invalid'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'active_zd_cli'}, test_name, common_name, 2, True))

#testcase 4
    test_case_name = '[SRP rebulids with more licensed APs]'
    num = 0
    idx = '4.%s'
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'license_type':'random',
                       'file_name':'standby_zd_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'standby_zd_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'standby_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'standby_zd_increase_random.lic',
                       'zd_tag':'standby_zd',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, True))

#testcase 5
    test_case_name = '[SRP rebulids with less licensed APs - OK]'
    num = 0
    idx = '5.%s'

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli1',
                       'license_type':'random',
                       'file_name':'zd1_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd1_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd1_increase_random.lic',
                       'zd_tag':'zd1',}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli2',
                       'license_type':'random',
                       'file_name':'zd2_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd2_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd2_increase_random.lic',
                       'zd_tag':'zd2',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'standby_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all licenses on standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

#click ok or cancel when warning pops up.
#if ok, re-calculates

    num += 1
    test_name = 'CB_Answer_Smart_Redundancy_Pool_Choice'
    common_name = '%s%sEnable sr on standby zd and answer confirm on active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd','choice':'OK'},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Verify_APs_Info'
    common_name = '%s%sVerify all APs are connected' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1 after test'%(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2 after test'%(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

#testcase 6
    test_case_name = '[SRP rebulids with less licensed APs - Cancel]'
    num = 0
    idx = '6.%s'

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd2'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli1',
                       'license_type':'random',
                       'file_name':'zd1_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd1_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd1_increase_random.lic',
                       'zd_tag':'zd1',}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli2',
                       'license_type':'random',
                       'file_name':'zd2_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the license for zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd2_increase_random.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the license to zd2'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd2_increase_random.lic',
                       'zd_tag':'zd2',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,2,False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'standby_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all licenses on standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

#click ok or cancel when warning pops up.
#if cancel, peer zd's local sr status is disabled

    num += 1
    test_name = 'CB_Answer_Smart_Redundancy_Pool_Choice'
    common_name = '%s%sEnable sr on standby zd and answer confirm on active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd','choice':'Cancel'},test_name,common_name,2,False))

    test_name = 'CB_ZD_CLI_Verify_SR_Status' 
    common_name = '%s%sVerify sr local status is disabled on standby zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_info':{'local_status':'Disabled',
                                      'peer_status':'Disabled'}},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1 after test'%(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd2 after test'%(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

#testcase 7
    test_case_name = '[Temp license can not work with SR]'
    num = 0
    idx = '7.%s'

    num += 1
    test_name = 'CB_ZD_Delete_All_SR_License' 
    common_name = '%s%sDelete all license on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 1, False))

    num += 1
    test_name = 'CB_Server_Generate_SR_License' 
    common_name = '%s%sGenerate a temp license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'zdcli1',
                       'license_type':'temp',
                       'file_name':'zd1_temp.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_TE_Get_File_From_Linux' 
    common_name = '%s%sGet the temp license for zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'src_file_dir':'/home/lab/zd_sr_license',
                       'src_file_name':'zd1_temp.lic'},
                       test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Enable_SR_On_One_ZD' 
    common_name = '%s%sEnable SR on zd1'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the temp license to zd1 should fail'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd1_temp.lic',
                       'zd_tag':'zd1',
                       'negative':True}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%s%sDisable SR on zd1' %(test_case_name,idx%(num))
    test_cfgs.append(({'target_zd':'zdcli1'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Import_SR_License' 
    common_name = '%s%sImport the temp license to zd1 should succeed'%(test_case_name,idx%(num))
    test_cfgs.append(({'license_name':'zd1_temp.lic',
                       'zd_tag':'zd1',}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Enable_SR_On_One_ZD' 
    common_name = '%s%sEnable SR on zd1 should fail'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'zd1','negative':True}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%s%sSet ZD to factory to remove temp license' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd':'zd1'},test_name, common_name, 2, True))

#testcase 8

    test_case_name = '[SRP works after zd reboot]'
    num = 0
    idx = '8.%s'

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,1,False))

    num += 1
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%s%sReboot zd1 from zdcli'%(test_case_name,idx%(num))
    test_cfgs.append(( {'zd_tag':'zdcli1','timeout':10*60}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%s%sReboot zd2 from zdcli'%(test_case_name,idx%(num))
    test_cfgs.append(( {'zd_tag':'zdcli2','timeout':10*60}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))
    
#testcase 9

    test_case_name = '[SRP works after zd factory reset]'
    num = 0
    idx = '9.%s'

    num += 1
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s%sBoth ZD enable SR and ready to do test'%(test_case_name,idx%(num))
    test_cfgs.append(({},test_name,common_name,1,False))

    num += 1
    test_name = 'CB_ZD_Backup'
    save_to = os.path.join(os.path.expanduser('~'), r"Desktop" )
    common_name = '%s%sBackup the current configuration of active zd'%(test_case_name,idx%(num))
    test_cfgs.append(({'zd':'active_zd','save_to':save_to}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%s%s active zd set factory' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Restore'
    common_name = '%s%s restore active zd config' %(test_case_name,idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from active zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'active_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_SR_License_Info'
    common_name = '%s%sGet licensed AP number from standby zd' %(test_case_name,idx%(num))
    test_cfgs.append(({'zd_tag':'standby_zd'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in active ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Verify_SR_License'
    common_name = '%s%sVerify SRP in standby ZD CLI' %(test_case_name,idx%(num))
    test_cfgs.append(({'zdcli_tag':'standby_zd_cli',
                       'expect_status':'Normal'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s%sDisable Smart Redundancy on the two ZDs' %(test_case_name,idx%(num))
    test_cfgs.append(({},test_name, common_name, 2, True))

    return test_cfgs

def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs) 
    test_cfgs = define_test_cfg()

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Smart Redundancy License Pool"

    ts = testsuite.get_testsuite(ts_name, "Smart Redundancy License Pool" , combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1

            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)