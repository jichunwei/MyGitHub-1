import logging

from RuckusAutoTest.components.lib.mf import metro_maintenance as mfmain

#=============================================#
#     Public Methods
#=============================================#
def upgrade_fw_via_gui(mf_obj, upgrade_cfg, timeout = 360):
    '''
    Upgrade firmware via AP web UI, the procedures are:
    1. For manual upgrade:
        a. Updated setting in web UI and click "Perform upgrade"
        b. Wait for upgrading
        c. Reboot AP
    2. For auto upgrade:
        a. Updated setting in web UI and click "Save parameters only"
    '''
    errmsg = ''
    
    mf_obj.start(15)
    try:
        ui_up_cfg = upgrade_cfg         
        timeout = 1200
        ts, msg = mfmain.upgrade_fw(mf_obj, ui_up_cfg, timeout)
        
        logging.info(msg)
        
        # ts = 3, Got alert pop up: A firmware upgrade is unnecessary.  Please click "OK" to continue.
        if mfmain.UPGRADE_STATUS_UNNECESSARY == ts:
            errmsg = "No Upgrade. AP is running an expected image"
        elif mfmain.UPGRADE_STATUS_FAILED == ts or mfmain.UPGRADE_STATUS_TIMEOUT == ts:
            errmsg = msg
            
    except Exception, e:
        errmsg = ('Fail to upgrade to firmware version: %s. Error: %s' %
                     (upgrade_cfg['control'], e.__str__()))

        logging.warning(errmsg)

    mf_obj.stop()
    
    return errmsg

#=============================================#
#     Private Methods
#=============================================#