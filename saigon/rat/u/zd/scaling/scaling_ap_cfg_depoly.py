"""
    Description:
        Verify WLANs/ACL can deploy correctly to APs[RuckusAP | SIMAP]
    Prerequisites:
        1) All of SimAPs are running at your ENV and all of them are connected.
    Steps:
        +Remove All WLANs from ZD.
        +Pick up WLANs and deploy them to all of APs.
        +Verify all of WLANs can deploy successfully.         
    Usage:
        tea.py <scaling_wlans_depoly key/value pair> ...
        
        where <scaling_wlans_depoly key/value pair> are:
          chk_gui           :     'True then will verify from ZoneDirector GUI'
          debug             :     'True then will enter debugging mode'
        notes:
        All of SimAP Servers configuration, please reference scaling_config.py
    Examples:        
        tea.py scaling_wlans_depoly te_root=u.zd.scaling chk_gui=True debug=True        

"""
from u.zd.scaling.lib import scaling_utils as utils
from u.zd.scaling.lib import scaling_zd_lib as lib

def do_config(tcfg):
    _cfg = dict()
    _cfg['zd'] = utils.create_zd(**tcfg)
    
    return _cfg

def do_test(cfg):
    pass

def do_clean_up(cfg):
    pass

def deploy_wlans(num_of_wlans):
    pass

def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res