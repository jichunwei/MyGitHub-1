# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
FtpClient class is used to ftp get_from/put_to Ftp Server.

Examples:

    import FtpClient
    from pprint import pprint
    ftpc = FtpClient.FtpClient(dict(ip_addr='172.17.18.121', username='zdvm', password='tdcitms'))
    pprint(ftpc, indent=3)

    data1 = ftpc.get_file('/vmware/startzd.sh', '/datax/startzd.sh', return_data=True)
    data2 = ftpc.get_file('/vmware/stopzd.sh', '/datax/stopzd.sh', return_data=True)
    data3 = ftpc.get_file('/vmware/result.txt', '/datax/result1.json', return_data=True)

    pdata = ftp.get_json_file('/vmware/result.txt', '/datax/result2.json')
    pprint(pdata, indent=3)

"""
import os
import logging
import ftplib
import simplejson as json

class FtpClient():

    def __init__(self, config):
        """
        initialize the default information used to connect to FTP server.
        """
        self.conf = dict(ip_addr = '192.168.0.20',
                         username = 'anonymous',
                         password = '',
                         rootpath = '',
                         init = True,
                         rd_blocksize = 2048,
                         debug = 0,
                        )
        self.conf.update(config)
        if self.conf['init']: self.initialize()

    def initialize(self):
        pass

    def get_json_file(self, remote_file, local_file = '', **kwargs):
        self.get_file(remote_file, local_file, **kwargs)
        lfd = open(local_file, 'r')
        jdata = lfd.read()
        lfd.close()
        pdata = json.loads(jdata)
        return pdata

    def get_file(self, remote_file, local_file = '', **kwargs):
        cfg = {'ip_addr': self.conf['ip_addr'],
               'username': self.conf['username'],
               'password': self.conf['password'],
               }
        cfg.update(kwargs)
        ftp = ftplib.FTP(cfg['ip_addr'])
        ftp.login(cfg['username'], cfg['password'])
        self._retrieve_file(ftp, remote_file, local_file)

    def _retrieve_file(self, ftp, remote_file, local_file):
        lfd = open(local_file, 'wb')
        ftp.retrbinary('RETR %s' % remote_file, lfd.write)
        lfd.close()

    def put_file(self, local_file, remote_file = '', **kwargs):
        cfg = {'ip_addr': self.conf['ip_addr'],
               'username': self.conf['username'],
               'password': self.conf['passwrod'],
               'bksize': self.conf['rd_blocksize']}
        cfg.update(kwargs)
        raise Exception('Not implemented yet!')

