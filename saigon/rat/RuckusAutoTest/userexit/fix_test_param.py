# You need to define a function
#
#   named fix_test_param with 2 args.
#
#   The 1st arg is the testrun object, and
#   the 2nd arg is a dictionary of testrun.test_param
#
# def fix_test_param(testrun, test_param)
# 
# ================================================================
# Here is a sample function to overwrite L2 test cases that 
# need to authenticate with AD
#
import logging

def sample_fix_test_param(testrun, _tp):
    if _tp.has_key('ip') and _tp['ip'] == '172.26.0.252':
        _tp['ip'] = '172.126.0.252'
    if _tp.has_key('auth_type') and _tp['auth_type'] == 'ad':
        if _tp.has_key('auth_srv_info') and _tp['auth_srv_info'].startswith('example'):
            _tp['auth_srv_info'] = 'rat.ruckuswireless.com'
    return 0

AD_SERVER_DOMAIN = 'rat.ruckuswireless.com'
def b7_1_52_MR1_fix_test_param(testrun, _tp):
    if not testrun or not hasattr(testrun, 'id'): return 0
    fixcnt = 0
    fixcnt += l2tunnel_fix_test_param(testrun, _tp)
    return fixcnt

def l2tunnel_fix_test_param(testrun, _tp):    
    fixcnt = 0
    if _tp.has_key('auth_type') and _tp['auth_type'] == 'ad':
        if _tp.has_key('auth_srv_info') and _tp['auth_srv_info'].startswith('example'):
            logging.debug( "[USEREXIT] TrID #%d changes auth_srv_info ['%s' -> '%s']"
                         % (testrun.id, _tp['auth_srv_info'], AD_SERVER_DOMAIN))
            _tp['auth_srv_info'] = AD_SERVER_DOMAIN
            fixcnt += 1

    if _tp.has_key('wlan_cfg'):
        wlan_cfg =_tp['wlan_cfg']
        if wlan_cfg.has_key('ad_domain') and wlan_cfg['ad_domain'].startswith('example'):
            logging.debug( "[USEREXIT] TrID #%d changes wlan_cfg['ad_domain'] ['%s' -> '%s']"
                         % (testrun.id, wlan_cfg['ad_domain'], AD_SERVER_DOMAIN))
            wlan_cfg['ad_domain'] = AD_SERVER_DOMAIN
            fixcnt += 1

    return fixcnt

