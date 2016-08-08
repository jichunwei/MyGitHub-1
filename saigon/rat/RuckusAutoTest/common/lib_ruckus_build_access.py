"""
@author: An Nguyen
@contact: an.nguyen@ruckuswireless.com
@since: 13 July, 2010
@copyright: Ruckus Wireless Inc,.

Description:
    This library support user to access server to get the SW image of Ruckus devices.
"""

import logging
import urllib2, urllib
from urlparse import urlparse

from RuckusAutoTest import BeautifulSoup
#
# To handle cookie, please refer to: http://wwwsearch.sourceforge.net/ClientCookie/
#

def get_auth_user(username, password):
    import os
    if username == None and password == None:
        if os.environ.has_key('BUILDSERVER_RAT_USER'):
            return os.environ['BUILDSERVER_RAT_USER'].split()[0:2]
        else:
            return ['qaauto@video54.local', 'QaAuto!880']
    return [username, password]

def get_auth_page(theurl, username = None, password = None):
    (username, password) = get_auth_user(username, password)
    logging.info("Get build info from url[%s]" % theurl)

    # this creates a password manager
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # because we have put None at the start it will always
    # use this username/password combination for  urls
    # for which `theurl` is a super-url
    passman.add_password(None, theurl, username, password)

    # create the AuthHandler
    authhandler = urllib2.HTTPBasicAuthHandler(passman)

    opener = urllib2.build_opener(authhandler)

    # All calls to urllib2.urlopen will now use our handler
    # Make sure not to include the protocol in with the URL, or
    # HTTPPasswordMgrWithDefaultRealm will be very confused.
    # You must (of course) use it when fetching the page though.
    urllib2.install_opener(opener)

    # authentication is now handled automatically for us
    pagehandle = urllib2.urlopen(theurl)
    thepage = pagehandle.read()
    return thepage

def urlretrieve_auth_file(theurl, filename,username=None,password=None):
    (username,password) = get_auth_user(username,password)
    class OpenerWithAuth(urllib.FancyURLopener):
        def prompt_user_passwd(self, host, realm):
            return username, password
    return OpenerWithAuth().retrieve(theurl,filename)

def get_build_url(build_stream, build_number):
    """
    Return the URL of the expected build 
    """
    server_url_map = {'server':{'lhotse': 'http://lhotse/cgi-bin/build_info.pl?filename=www_%s',
                                'k2': 'http://k2.video54.local/cgi-bin/build_info.pl?filename=www_%s',
                                },
                      'ZD3000':{'latest_k2_build': '7'},
                      'ZD1000':{'latest_k2_build': '7'},
                      }
    
    build_stream_info = build_stream.split('_')
    device_type = build_stream_info[0]
    stream = build_stream_info[1].split('.')[0]
    
    if device_type not in server_url_map.keys():
        errmsg =  'The device type is not recored on the server_url_map. Please check it!'
        raise Exception(errmsg)
    
    if stream == 'mainline' or stream > server_url_map[device_type]['latest_k2_build']:
        url = server_url_map['server']['lhotse'] % build_stream
    else:
        url = server_url_map['server']['k2'] % build_stream  
        
    try:
        _webpage_str = get_auth_page(url)
        soup = BeautifulSoup.BeautifulSoup("".join(_webpage_str))
    except Exception, e:
        logging.debug(e.message)
        raise 'The build stream is not existed or the connection is down'
    cols_map = {'number': 0,
                'url': 12}
    buildtable = soup('table')[1]

    for row in buildtable('tr')[1:]:
        build_url = ''
        if row('td')[cols_map['number']].contents[0].strip() == str(build_number):
            try:  # special case for URL column
                build_url = row('td')[cols_map['url']].contents[0]['href']     
                break
            except:
                pass  # no URL; failed build;
            
    return build_url

def download_build(build_url, file_name = ''):
    """
    Download the target build from server base on the build url.
    """
    if not file_name:
        file_name = build_url.split('/')[-1]
    logging.info('Please wait for downloading the image. It takes several minutes')
    fname, h = urlretrieve_auth_file(build_url, file_name)
    return fname