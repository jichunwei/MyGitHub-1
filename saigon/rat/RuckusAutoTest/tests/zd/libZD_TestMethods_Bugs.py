import logging
import time

from RuckusAutoTest.common import sshclient
from RuckusAutoTest.common.Ratutils import ping

ZD_PROMPTS = ['Please login: ', 'Password: ', 'ruckus% ', 'ruckus# ']

# return ZD ssclient instance if login; otherwise is False (or None)
def login_zd(hostname, username = 'admin', password = 'admin', timeout = 60):
    myzd = sshclient.sshclient(hostname)
    noresp_cnt = 0
    login_cnt = 0
    cut_time = time.time()
    while time.time() - cut_time < timeout:
        (mid, mobj, resp) = myzd.expect(ZD_PROMPTS)
        if mid < 0:
            if noresp_cnt > 2:
                myzd.close()
                return False
            noresp_cnt += 1
            continue
        if mid == 0:
            print "[DEBUG SSH] username: %s" % username
            myzd.write(username + '\n')
            login_cnt += 1
            if login_cnt > 3:
                myzd.close()
                return False
        elif mid == 1:
            print "[DEBUG SSH] password: %s" % password
            myzd.write(password + '\n')
        elif mid > 1:
            print "[DEBUG SSH] login banner: %s" % resp
            return myzd 
        myzd.buffer = ''
        time.sleep(3)
    return False

# ZD.set_admin_cfg(self, conf)
# conf = dict(
#   auth_method=['local', 'external']
#   auth_server='radis.4.admin'
#   fallback_local=[True, False]
#   admin_name="string"
#   admin_pass1="password"
#   admin_pass2="confirm password"
#   )
def set_auth_info_local(zd, username = 'admin', password = 'admin', auth_serv = '', fallback_local = True):
    logging.info('[BUGID 8806] set ZoneDirector adminUser[%s %s] using local auth.' % (username, password))
    zd.do_login()
    zd.set_admin_cfg(dict(auth_method = 'local',
                                           admin_name = username,
                                           admin_pass1 = password,
                                           admin_pass2 = password,
                                           fallback_local = fallback_local,
                                           auth_serv = auth_serv))
    zd.password = password

def set_auth_info_external(zd, auth_server, username = 'admin', password = 'ruckus'):
    logging.info('[BUGID 8806] set ZoneDirector adminUser[%s %s] using External AuthServ[%s].' % (username, password, auth_server))
    zd.do_login()
    if username and password:
        zd.set_admin_cfg(dict(auth_method = 'external',
                                               auth_server = auth_server,
                                               admin_name = username,
                                               admin_pass1 = password,
                                               admin_pass2 = password))
        zd.password = password
    else:
        # this is how bug 8806 bug occur
        zd.set_admin_cfg(dict(auth_method = 'external',
                                               auth_server = auth_server))

# ap0, ap1 = restart_zd(zd, True)
def restart_zd(zd, chkApInfo = False, z_pause4Confirmation = 2, z_pause4ZDRestart = 60):
    if chkApInfo:
        apinfo_0 = zd.get_all_ap_info()
    xloc_restart = r"//input[@value='Restart']" 
    zd.do_login()
    zd.navigate_to(zd.ADMIN, zd.ADMIN_RESTART)
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc_restart)
    time.sleep(z_pause4Confirmation)
    if zd.s.is_confirmation_present(5):
        zd.s.get_confirmation()
    time.sleep(z_pause4ZDRestart)
    wait_for_zd_come_up(zd, 'restart', 180)
    zd.do_login()
    if chkApInfo:
        return wait_for_ap_registered(zd, apinfo_0)
    return (None, None)

def wait_for_ap_registered(zd, apinfo_0, zPause = 15, timeout = 360):
    ap_dict_0 = ap_list_as_dict(apinfo_0)
    end_time = time.time() + timeout
    while time.time() < end_time:
        time.sleep(zPause)
        apinfo_1 = zd.get_all_ap_info()
        neq = 0
        for ap in apinfo_1:
            if ap['status'] != ap_dict_0[ap['mac']]['status']:
                neq += 1
        if not neq:
            return (apinfo_0, apinfo_1)
    return None

def ap_list_as_dict(aplist):
    ap_dict = {}
    for ap in aplist:
        ap_dict[ap['mac']] = ap
    return ap_dict

# call me immediately after set_factory_default/Restart ZD
def wait_for_zd_come_up(zd, actType = 'restart', timeout = 420, pauseAfterComeUp = 20):
    logging.info("The ZoneDirector [%s] is %s. Please wait..." % (zd.ip_addr, actType))
    # Keeping pinging to the Zone Director until it has been restarted successfully
    time_out = timeout
    start_time = time.time()
    while True:
        if (time.time() - start_time) > time_out:
            raise Exception("Error: Timeout - ZoneDirector does not %s." % actType)
        res = ping(zd.ip_addr)
        if res.find("Timeout") != -1:
            break
        time.sleep(2)
    logging.info("The ZoneDirector is %s. Please wait..." % (actType))
    while True:
        if (time.time() - start_time) > time_out:
            raise Exception("Error: Timeout - ZoneDirector does not come up.")
        res = ping(zd.ip_addr)
        if res.find("Timeout") == -1:
            break
    time.sleep(pauseAfterComeUp)

