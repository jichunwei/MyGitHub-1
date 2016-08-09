# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""HTTP client: simulate a web browser that is used to test Zone Director functionality"""

import os
import sys
import time
import re

import urllib
import urllib2
import socket
import tempfile
import urlparse

# Limit socket default timeout value so that some HTTP/HTTPS requests will not be blocked for long time
socket.setdefaulttimeout(180)
cookieProcessor = urllib2.HTTPCookieProcessor()
_opener = urllib2.build_opener(cookieProcessor)


class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def __init__(self):
        self.redirected_url = ""
        self.counter = 0

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
        elif 'uri' in headers:
            newurl = headers.getheaders('uri')[0]
        else:
            return
        self.redirected_url = urlparse.urljoin(req.get_full_url(), newurl)
        self.counter += 1

        res = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        res.status = code
        return res

    def http_error_301(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
        elif 'uri' in headers:
            newurl = headers.getheaders('uri')[0]
        else:
            return
        self.redirected_url = urlparse.urljoin(req.get_full_url(), newurl)
        self.counter += 1

        res = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        res.status = code
        return res


#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
#
# RAT client authentication functions
#
def perform_zd_web_auth(arg):
    """
    Try to navigate to a URL and expect that ZD redirects to the authentication web page.
    Then try to pass user credentials to authenticate the client
    Input:
    @param username/password: credentials to present to the ZD
    @param url: (optional) a URL to be used to trigger the Web authentication
    """

    _arg = {
        'target_url': 'http://www.example.net/',
        'login_url': 'https://%s/user/user_login_auth.jsp',
        'user_login_auth': {
            'username':'testuser',
            'password': 'testuser',
            'ok': "Log In",
         },
         'activate_url': 'https://%s/user/_allowuser.jsp'
    }
    _arg.update(arg)

    cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieProcessor)

    f = opener.open(_arg['target_url'])
    data = f.read()

    done_redir_auth_page = False
    done_auth_page = False
    done_everything = False
    retries = 10
    auth_status = dict(cnt = 0)

    while retries:
        if not done_redir_auth_page and _asked_to_redirect(data):
            # The redir page
            # Find the redirected address
            ip_match_obj = re.search("//([0-9\.]+)", f.geturl())
            if not ip_match_obj:
                raise Exception("Could not parse IP address in the URL %s" % f.geturl())

            ip_addr = ip_match_obj.group(1)
            # Open the redirected page
            f = opener.open("https://%s" % ip_addr)
            data = f.read()
            done_redir_auth_page = True

        elif data.find("Authenticating...") != -1:
            time.sleep(1)
            ip_match_obj = re.search("//([0-9\.]+)", f.geturl())
            if not ip_match_obj:
                raise Exception("Could not parse IP address in the URL %s" % f.geturl())
            ip_addr = ip_match_obj.group(1)

            # Pass the credentials to the ZD
            login_inf = urllib.urlencode(_arg['user_login_auth'])
            f = opener.open(_arg['login_url'] % ip_addr)
            data = f.read()

        elif data.find("Either your user name or password is incorrect") != -1:
            raise Exception("Invalid username or password given")

        elif _is_authentication_required_for_web_auth_user(data, auth_status):
            if done_auth_page:
                if auth_status['cnt'] < 3:
                    time.sleep(1)

                else:
                    raise Exception("WebAuth Failed: being asked to authenticate[%s %s] %d times" %
                                    (_arg['target_url']['username'], _arg['target_url']['password'],
                                     auth_status['cnt']))
            # The login page
            # Find the address of the ZD
            ip_match_obj = re.search("//([0-9\.]+)", f.geturl())
            if not ip_match_obj:
                raise Exception("Could not parse IP address in the URL %s" % f.geturl())
            ip_addr = ip_match_obj.group(1)

            # Pass the credentials to the ZD
            login_inf = urllib.urlencode(_arg['user_login_auth'])
            f = opener.open(_arg['login_url'] % ip_addr, login_inf)
            data = f.read()
            done_auth_page = True

        elif _is_authenticated_web_auth_user(data):
            # The authenticated page
            # Find the redirecturl cookie
            try:
                redir_url = [cookie for cookie in cookieProcessor.cookiejar
                             if cookie.name == 'redirecturl'][0].value

            except IndexError:
                raise Exception("'redirecturl' cookie was not found in the HTTP response")

            # Find the address of the ZD
            ip_match_obj = re.search("//([0-9\.]+)", f.geturl())
            if not ip_match_obj:
                raise Exception("Could not parse IP address in the URL %s" % f.geturl())

            ip_addr = ip_match_obj.group(1)
            # And activate the user
            try:
                opener.open(_arg['activate_url'] % ip_addr)

            except urllib2.URLError, error:
                if str(error).find("timed out") != -1:
                    pass

                else:
                    raise

            # Validate the redirecturl cookie
            if redir_url.find(_arg['target_url']) == -1:
                raise Exception("'redirecturl' cookie was not as expected (%s instead of %s)" % (redir_url, _arg['target_url']))

            done_everything = True

            break

        else:
            raise Exception("Unknown data pattern received")

        retries -= 1
    # End of while
    if not done_redir_auth_page:
        raise Exception("Redirect page not found")

    if not done_auth_page:
        raise Exception("Authentication page not found")

    if not done_everything:
        raise Exception("Could not finish the authentication, maybe because of incorrect credentials")


def perfrom_zd_guest_auth(arg):
    """
    Try to navigate to a URL and expect that ZD redirects to the guest pass authentication page if required.
    Then expect to see the Terms Of Use page if required. Finally, expect that ZD will redirect to
    the original page or to a given URL
    @param guest_pass (True/False): use or don't use Guest Pass Authentication
    @param use_tou (True/False): show or don't show Terms Of Use
    @param redirect_url: the URL that ZD will redirect to after TOU is agreed
    @param original_url: (optional) the URL to be used to trigger the guest authentication
    """
    _arg = {
        'target_url': 'http://www.example.net/',
        'redirect_url': '',
        'guest_auth_cfg': {
            'guest_pass': '',
            'use_tou': False,
        },
        'guest_login_url': '%s/user/guest_login.jsp',
        'guest_login': {
            'key': '',
            'ok': 'Login',
         },
         'guest_tou_url': '%s/user/guest_tou.jsp',
         'guest_tou': {
            'ok': 'ok',
         },
        'activate_url': '%s/user/_allowguest.jsp',
        'msg_guestpass_is_invalid': 'This is an invalid Guest Pass',
        'msg_guestpass_welcome_page': 'Welcome to the Guest Access login page',
        'msg_guestpass_tou_review': 'Please review the terms of use',
    }
    _arg.update(arg)

    cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieProcessor)

    f = opener.open(_arg['target_url'])
    data = f.read()
    done_guest_pass_auth = False
    done_tou_agreement = False
    done_everything = False    
    retries = 20
    while retries:
        if data.find(_arg['msg_guestpass_is_invalid']) != -1:
            # The guest pass is invalid or has been expired
            raise Exception("Provided Guest Pass is invalid")

        elif data.find(_arg['msg_guestpass_welcome_page']) != -1:
            # Do the authentication by sending the pass to ZD
            # Look for the URL of ZD
            match_obj = re.search("([https]+://[0-9\.]+)", f.geturl())
            if not match_obj:
                raise Exception("Could not parse the URL %s" % f.geturl())

            zd_url = match_obj.group(1)

            # Use post method to send authentication info to the ZD
            keyinfo = urllib.urlencode(_arg['guest_login'])
            f = opener.open(_arg['guest_login_url'] % zd_url, keyinfo)
            data = f.read()
            done_guest_pass_auth = True

        elif data.find(_arg['msg_guestpass_tou_review']) != -1:
            # Look for the URL of ZD
            match_obj = re.search("([https]+://[0-9\.]+)", f.geturl())
            if not match_obj:
                raise Exception("Could not parse the URL %s" % f.geturl())

            zd_url = match_obj.group(1)

            # Use post method to send TOU agreement to the ZD            
            #okinfo = urllib.urlencode(_arg['guest_tou'])
            #Fixed by cwang@2012/11/8            
            okinfo = re.search('location.href = \"guest_tou\.jsp\?(.*);', data, re.M) 
            if okinfo:
                okinfo = okinfo.group(1)#9.6 Feature, one cookie per http request.
            else:
                okinfo = urllib.urlencode(_arg['guest_tou'])#Before 9.6 Feature.

            f = opener.open(_arg['guest_tou_url'] % zd_url, okinfo)
            data = f.read()
            f.close()
            done_tou_agreement = True

        elif _is_authenticated_guestaccess_user(data):
            # Activate the client
            # Find the redirecturl cookie
            try:
                redir_url = [cookie for cookie in cookieProcessor.cookiejar
                             if cookie.name == 'redirecturl'][0].value

            except IndexError:
                raise Exception("'redirecturl' cookie was not found in the HTTP response")

            # Look for ZD's URL
            match_obj = re.search("([https]+://[0-9\.]+)", f.geturl())
            if not match_obj:
                raise Exception("Could not parse the URL %s" % f.geturl())

            zd_url = match_obj.group(1)
            # Try to activate the guest user
            try:
                opener.open(_arg['activate_url'] % zd_url)

            except urllib2.URLError, error:
                if str(error).find("timed out") != -1:
                    pass

                else:
                    raise

            # Validate the redirect cookie
            if _arg['redirect_url']:
                if _arg['redirect_url'] != redir_url:
                    raise Exception("'redirecturl' cookie was not as expected (%s instead of %s)" %
                                    (redir_url, _arg['redirect_url']))
            else:
                if _arg['target_url'] != redir_url:
                    raise Exception("'redirecturl' cookie was not as expected (%s instead of %s)" %
                                    (redir_url, _arg['target_url']))

            done_everything = True

            break

        elif data.find("Redirecting") != -1:
            # Redirect to the original site or to a site specified by ZD
            # This kind of redirect is used without Guest Pass Auth or TOU
            # Look for ZD's URL
            match_obj = re.search("([https]+://[0-9\.]+)", f.geturl())
            if not match_obj:
                raise Exception("Could not parse the URL %s" % f.geturl())

            zd_url = match_obj.group(1)
            # Try to activate the guest user
            try:
                opener.open(_arg['activate_url'] % zd_url)

            except urllib2.URLError, error:
                if str(error).find("timed out") != -1:
                    pass

                else:
                    raise

            # Find the redirecturl cookie
            try:
                redir_url = [cookie for cookie in cookieProcessor.cookiejar
                             if cookie.name == 'redirecturl'][0].value

            except IndexError:
                raise Exception("'redirecturl' cookie was not found in the HTTP response")

            if _arg['redirect_url']:
                if redir_url.find(_arg['redirect_url']) == -1:
                    raise Exception("'redirecturl' cookie was not as expected (%s instead of %s)" %
                                    (redir_url, _arg['redirect_url']))
            else:
                if redir_url.find(_arg['target_url']) == -1:
                    raise Exception("'redirecturl' cookie was not as expected (%s instead of %s)" %
                                    (redir_url, _arg['target_url']))

            done_everything = True

            break

        else:
            raise Exception("Unknown data pattern received")

        retries -= -1
    # End of while

    if done_everything:
        done_guest_pass_auth = True
        done_tou_agreement = True

    if _arg['guest_auth_cfg']['guest_pass'] and not done_guest_pass_auth:
        raise Exception("The Guest Access login page was not found")

    if _arg['guest_auth_cfg']['use_tou'] and not done_tou_agreement:
        raise Exception("The Terms Of Use agreement page was not found")

    if not done_everything:
        raise Exception("Could not do the authentication, maybe because of incorrect credentials")


def download_zero_it(activate_url, username, password):
    """
    Download the Zero IT tool from Zone Director by accessing the given URL and using given credentials
    @param activate_url: Activation URL on Zone Director
    @param username: Username to pass authentication
    @param password: Password to pass authentication
    @return: The full path to the downloaded file
    """
    cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieProcessor)

    headers = [('Accept-Language', 'en-us,en;q=0.5'), ('Accept-Encoding', 'gzip,deflate'), ('Keep-Alive', '300'),
               ('Accept', 'text/html, application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
               ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'), ('Connection', 'keep-alive')]
    win_ver_major, win_ver_minor, win_ver_build, win_ver_platform, win_ver_text = sys.getwindowsversion()
    user_agent_hdr = ('User-Agent',
                      'Mozilla/5.0 (Windows; U; Windows NT %s.%s; en-US; rv:1.9) Gecko/2008042905 Firefox/3.0' %
                      (win_ver_major, win_ver_minor))
    headers.append(user_agent_hdr)
    opener.addheaders = headers

    # Find the address of the ZD
    # Add pattern for ipv6.
    ptns = ["//([0-9\.]+)", "//(\[[0-9a-zA-Z:]+\])"]
    is_match = False
    for ptn in ptns:
        ip_match_obj = re.search(ptn, activate_url)
        if ip_match_obj:
            is_match = True
            zd_ip_addr = ip_match_obj.group(1)
            break
                
    if not is_match:
        raise Exception("Could not parse IP address in the URL %s" % activate_url)

    f = opener.open(activate_url)
    data = f.read()

    while True:
        if data.find("Either your user name or password is incorrect") != -1:
            raise Exception("Invalid username or password given")

        elif data.find("WLAN Connection Activation") != -1:
            # The WLAN Connection Activation page
            # Pass the credentials to the ZD
            login_inf = urllib.urlencode(dict(username = username, password = password, ok = "Login"))
            f = opener.open("https://%s/user/user_login_prov.jsp" % zd_ip_addr, login_inf)
            data = f.read()

        #elif data.find("Corporate WLAN Configuration") != -1:
        #@author: lipingping, to adatper zero-it download page behavior change; @bug:ZF-9883
        elif data.find("Secure WLAN Configuration") != -1: 
            # The authentication has been done
            # Now move to the Corporate WLAN Configuration page
            # Try to download the prov.exe file
            f = opener.open("https://%s/user/download.jsp" % zd_ip_addr)
            data = f.read()
            
            #@author: anzuo, ZF-4818 & ZF-5119
            if f.headers.dict.has_key('content-length'):
                if len(data) != int(f.headers.dict['content-length']):
                    raise Exception("The prov.exe file was not downloaded properly: got only %d bytes instead of %d" %
                                    (len(data), int(f.headers.dict['content-length'])))
            # Save data to a file
            fd, path = tempfile.mkstemp(suffix = ".exe")
            os.write(fd, data)
            os.close(fd)
            return path
        else:
            raise Exception("Unkown data received")


def download_speedflex(speedflex_url):
    """
    Download the SpeedFlex tool from Zone Director by accessing the given URL
    @param speedflex_url: Activation URL on Zone Director
    @return: The full path to the downloaded file
    """
    cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieProcessor)

    headers = [('Accept-Language', 'en-us,en;q=0.5'), ('Accept-Encoding', 'gzip,deflate'), ('Keep-Alive', '300'),
               ('Accept', 'text/html, application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
               ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'), ('Connection', 'keep-alive')]
    win_ver_major, win_ver_minor, win_ver_build, win_ver_platform, win_ver_text = sys.getwindowsversion()
    user_agent_hdr = ('User-Agent',
                      'Mozilla/5.0 (Windows; U; Windows NT %s.%s; en-US; rv:1.9) Gecko/2008042905 Firefox/3.0' %
                      (win_ver_major, win_ver_minor))
    headers.append(user_agent_hdr)
    opener.addheaders = headers

    f = opener.open(speedflex_url)
    data = f.read()
    if len(data) != int(f.headers.dict['content-length']):
        raise Exception("The speedflex.exe file was not downloaded properly: got only %d bytes instead of %d" %
                        (len(data), int(f.headers.dict['content-length'])))
    # Save data to a file
    fd, path = tempfile.mkstemp(suffix = ".exe")
    os.write(fd, data)
    os.close(fd)
    return path


def login_ap_web_ui(username, password, ip_addr):
    """
    Login to the AP or adapter via WebUI
    @param username/password: account to login
    @param ip_addr: an ip address of AP or adapter to be used to creat a URL
    """
    try:
        logout_ap_web_ui(ip_addr)
    except:
        pass

    url = "https://%s" % ip_addr
    f = _opener.open(url)
    data = f.read()

    login_ok = False
    while True:
        if data.find("Ruckus Wireless Admin") != -1 and data.find("Username:") != -1 and data.find("Password:") != -1:
            login_info = urllib.urlencode(dict(login_username = username, password = password))
            f = _opener.open("%s/forms/doLogin" % url, login_info)
            f = _opener.open("%s/top.asp" % url)
            data = f.read()
        elif data.find("Logout") != -1:
            login_ok = True
            break
        else:
            raise Exception("Unknown data pattern received")

    if not login_ok:
        raise Exception("Cound not login, maybe incorrect username/password")


def logout_ap_web_ui(ip_addr):
    """
    Logout from AP WebUI
    @param ipaddr: ip address of the AP
    """
    url = "https://%s/forms/doLogout" % ip_addr
    f = _opener.open(url)
    data = f.read()
    if data.find("Username:") == -1 and data.find("Password:") == -1:
        raise Exception("Could not logout - Unknown pattern data received")


def get_ap_wireless_status(ip_addr):
    """
    This function verifies if the wireless has video network or data network or both of them.
    @param ip_addr: ip address of the AP
    """
    # Navigate to Status/Wireless page
    wl_href = "https://%s/sWireless.asp?subp=common" % ip_addr
    f = _opener.open(wl_href)
    data = f.read()

    found_video = False
    found_data = False
    if data.find("Status :: Wireless") != -1:
        if data.find("Video WLAN") != -1:
            found_video = True
        if data.find("Data WLAN") != -1:
            found_data = True
    else:
        raise Exception("Unknown pattern data received")

    return {'video_status':found_video, 'data_status':found_data}


def verify_station_mgmt(ap_ip_addr, aid, sta_mac_addr):
    """
    This function verifies information of station and information of STA-Management
    @param ap_ip_addr: IP address of the AP
    @param aid: AID value of the adapter shown on the AP CLI
    @param sta_mac_addr: MAC address of the adapter
    """
    sta_existed = False
    sta_mgmt = False
    video_wlan_href = "https://%s/sWireless.asp?subp=wlan0" % ap_ip_addr
    sta_port = 25400 + int(aid)
    sta_mgmt_href = "http://%s:%d" % (ap_ip_addr, sta_port)

    f = _opener.open(video_wlan_href)
    data = f.read()
    if data.find(sta_mac_addr.lower()) != -1 or data.find(sta_mac_addr.upper()) != -1:
        sta_existed = True
    if data.find(sta_mgmt_href) != -1 and data.find("STA WebServer") != -1:
        sta_mgmt = True

    return {'sta_existed':sta_existed, 'sta_mgmt_enable': sta_mgmt}


def login_ad_web_ui(ap_ip_addr, aid):
    """
    Login to AD WebUI
    """
    sta_port = 25400 + int(aid)
    url = "http://%s:%d" % (ap_ip_addr, sta_port)

    try:
        f = _opener.open(url)
        data = f.read()
        if data.find("Ruckus Wireless Admin") == -1:
            raise Exception("Unknown pattern data received")
    except urllib2.URLError, error:
        if str(error).find("timed out") != -1: pass
        elif str(error).find("Connection refused") != -1:
            raise Exception(error)
        else:
            raise
    except Exception, e:
        raise Exception(e.message)


def hotspot_auth(arg):
    '''
    '''
    _arg = {
        'original_url': 'http://172.16.10.252/',
        'redirect_url': '',
        'user_login_auth': {
            'username': 'local.username',
            'password': 'local.password',
         },
         'pattern_login_page': r"<form action=.?(?P<url>[https]+://[0-9\.]+:[0-9]+)(?P<path>/login).?>",
         'pattern_redirect_url': r"window.location.href=[\'\"](.*)[\'\"];", # use [\'\"] to cover the quote ' and "
         'pattern_redirect_auth': r"img.src = .?(/_allowuser.jsp.*)[\'\"];",
         'expected_data': 'It works!',
    }
    _arg.update(arg)
    login_page_re = re.compile(_arg['pattern_login_page'])
    redirect_url_re = re.compile(_arg['pattern_redirect_url'])
    redirect_auth_re = re.compile(_arg['pattern_redirect_auth'])

    done_login_page = False
    done_auth = False

    data = _opener.open(_arg['original_url']).read()

    retries = 10
    while retries:
        if _arg['expected_data'] in data:
            done_auth = True
            break

        elif not done_login_page:
            matcher = login_page_re.search(data, re.MULTILINE)
            if not matcher:
                pass

            # This is the login page, proceed to enter username, password
            result = matcher.groupdict()
            login_inf = urllib.urlencode(
                {'username': _arg['user_login_auth']['username'],
                 'password': _arg['user_login_auth']['password']}
            )

            data = _opener.open("%s/%s?%s" % (result['url'], result['path'], login_inf)).read()

            done_login_page = True

        elif done_login_page and not done_auth:
            '''
            '''
            m_auth_url = redirect_auth_re.search(data, re.MULTILINE)
            m_redirect_url = redirect_url_re.search(data, re.MULTILINE)

            matchers = []
            if m_auth_url:
                matchers.append(m_auth_url)

            if m_redirect_url:
                matchers.append(m_redirect_url)

            if not matchers:
                pass

            for m in matchers:
                if m.group(1).startswith('http'):
                    url = m.group(1)

                else:
                    url = "%s/%s" % (result['url'], m.group(1))

                data = _opener.open(url).read()

        else:
            raise Exception("Unknown data pattern received")

        retries -= 1
    # End of while

    if not done_auth:
        raise Exception("Unable to do Hotspot authentication")


def hotspot_deauth(logout_url):
    cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieProcessor)

    href_re = re.compile("href=[\"\'](.*)[\"\']")
    redirect_url_re = re.compile("window.location.href=[\"\'](.*)[\"\'];")
    settimeout_re = re.compile("setTimeout\(redirect_to_login_page\(\), ([0-9]+)\);")
    login_page_re = re.compile("<form action=[\"\']([https]+)://([0-9\.]+):([0-9]+)/(.*)[\"\']>")

    f = opener.open(logout_url)
    data = f.read()
    m = href_re.search(data, re.M)
    if not m:
        raise Exception("Unable to retrieve the UAM logout URL")

    f = opener.open(m.group(1))
    data = f.read()
    m = redirect_url_re.search(data, re.M)
    if not m:
        raise Exception("Not found the redirect Java script or the ZD didn't redirect the Web pages properly")
    redirect_url = m.group(1)
    m = settimeout_re.search(data, re.M)
    if not m:
        raise Exception("Not found the ONLOAD event handler or the ZD didn't redirect the Web pages properly")

    time.sleep(int(m.group(1)) / 1000.0)

    f = opener.open(redirect_url)
    data = f.read()
    m = login_page_re.search(data, re.M)
    if not m:
        raise Exception("Not found the login page or the ZD didn't redirect the Web pages properly")


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
#
# validation methods
#
def _asked_to_redirect(data):
    if data.find("location.href='https://' + location.host + '/';") != -1:
        return True

    # PaloAlto
    if data.find("location.href='https://' + ip + '/';") != -1:
        return True

    # PaloAlto MR1 and QingDao
    if re.search(r"target=getCookie\('redirecturl'\)\;", data, re.M):
        if re.search(r"location.href\s*=\s*target\s*;", data, re.M):
            return True

    return False


def _is_authenticated_web_auth_user(data):
    
    if re.search(r"You are su(c+)essfully authenticated as a wireless network user", data, re.I):
        return True

    if re.search(r"Authenticated", data, re.I) and re.search(r"Please wait for a few seconds...", data, re.I):
        return True

    return False


def _is_authenticated_guestaccess_user(data):
    if re.search(r"You are su(c+)essfully authenticated", data, re.I):
        return True

    return False


def _is_authentication_required_for_web_auth_user(data, auth_status):
    if not auth_status.has_key('cnt'): auth_status['cnt'] = 0

    if data.find("Authentication Required for Wireless Access") >= 0:
        auth_status['cnt'] += 1
        return True

    return False



if __name__ == "__main__":
    func_dispatcher = {'zd_web_auth': perform_zd_web_auth,
                       'guest_auth': perfrom_zd_guest_auth,
                       'download_zero_it': download_zero_it,
                       'download_speedflex': download_speedflex,
                       'wispr_auth': hotspot_auth,
                       'wispr_deauth': hotspot_deauth,
                       'login_ap': login_ap_web_ui,
                       'logout_ap': logout_ap_web_ui,
                       'get_ap_wireless_status': get_ap_wireless_status,
                       'verify_station_mgmt': verify_station_mgmt,
                       'login_ad': login_ad_web_ui,
                       }
    try:
        if len(sys.argv) < 2:
            raise Exception("Not enough parameter")

        if sys.argv[1] not in func_dispatcher.keys():
            print "ERROR: Unknown command %s" % sys.argv[1]
            exit()

        if len(sys.argv) < 3:
            raise Exception("Not enough parameter to perform subcommand [%s]" % sys.argv[1])

        param = eval(sys.argv[2])

        # hack again
        if sys.argv[1] in ('zd_web_auth', 'guest_auth', 'wispr_auth'):
            res = func_dispatcher[sys.argv[1]](param)

        else:
            res = func_dispatcher[sys.argv[1]](**param)

        if res:
            print res

        else:
            print "DONE"

    except urllib2.URLError, error:
        print "ERROR: %s" % error

    except Exception, e:
        print "ERROR: %s" % e.message

