"""
This module supports to do an upgrade action on ZD by down load a build from server or use a file in HD

   tea.py zd_upgrade image_path=the-full-path-of-img-file-in-tar-gz-format
                    | [build_stream=the-build-stream-name][build_number=the-build-number]
                    | [server_user=the-user-name-use-to-access-lhotse-server][server_user_password=the-password-to-access-lhotse-server]
                    | [force_upgrade=True|False] [rm_data_files=True|False]
                    | [ip_addr=192.168.0.2] [username=admin] [password=admin]
                    | [debug=True|False]

   Parameters:
       image_path:             The file path of the SW image file (with format: build_no.tar.gz, ex: 46.tar.gz)
       build_stream:           The build stream name of ZD will be upgraded to
       build_number:           The build number to be upgarded
       server_user:            lhotse server user
       server_user_password:   lhotse server password
       force_upgrade:          Force to upgrade (True|False)
       rm_data_files:          Delete the image file after upgrade (True|False)
       ip_addr :               IP address of the Zone Director
       username/password:      ZD's login username/password
       debug:                  True|False (turn on|off the debug mode)

   Examples:
       tea.py zd_upgrade image_path=c://46.tar.gz
       tea.py zd_upgrade build_stream=ZD100_9.0.0.0_production build_no=46
"""

import time

from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common import lib_ruckus_build_access as build_access

def _download_build(build_stream, build_number):
    build_url = build_access.get_build_url(build_stream, build_number)

    if not build_url:
        errmsg = 'There is not any URL for the build %s.%s'
        errmsg = errmsg % (build_stream.split('_')[1], build_number)
        raise Exception(errmsg)
    
    return build_access.download_build(build_url)

def main(**kwargs):
    mycfg = {'debug': False}
    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin'}
    rescfg = {'image_path': '',
              'server_user': None,
              'server_user_password': None,
              'build_stream': '',
              'build_number': '',
              'force_upgrade': False,
              'rm_data_files': False,}

    for k, v in kwargs.items():
        if zdcfg.has_key(k):
            zdcfg[k] = v
        if mycfg.has_key(k):
            mycfg[k] = v
        if rescfg.has_key(k):
            rescfg[k] = v

    if mycfg['debug']: bugme.pdb.set_trace()
    
    #An Nguyen: If the image_path param is None, then download the build from server
    if not rescfg['image_path']:
        rescfg['image_path'] = _download_build(rescfg['build_stream'], 
                                               rescfg['build_number'])
    
    zd = create_zd_by_ip_addr(**zdcfg)

    start_time = time.time()
    try:
        zd.upgrade_sw(rescfg['image_path'], 
                      rescfg['force_upgrade'], 
                      rescfg['rm_data_files'])
    except Exception, e:
        return ('FAIL', '[RESTORE ERROR]: %s' % e.message)
    upgrade_time = time.time() - start_time

    zd.destroy()
    return ('PASS', 'It takes %s seconds to upgrade Zone Director successfully' 
            % upgrade_time)
