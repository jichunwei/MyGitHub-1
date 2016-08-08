import time
import re

import paramiko

PARAMIKO_VERSIONS_OLD = ['1.7.3', '1.7.4', '1.7.5']


class sshclient:
    def __init__(self, ip_addr, port = 22, username = "", password = None):
        '''
        '''
        self.ip_addr = ip_addr
        self.port = port
        self.username = username
        self.password = password
        self.hostkey = None

        # gets the paramiko release's version installed
        ver = paramiko.__version__

        # Version 1.7.3 is the oldest one mentioned at its development website:
        # http://www.lag.net/paramiko/.
        #
        # Method self.init_old() can be used with any release, however from 1.7.6
        # going forward, the self.init() method is strongly recommended.
        #
        if not ver[:5] in PARAMIKO_VERSIONS_OLD:
            return self.init()

        return self.init_old()


    def init(self):
        '''
        This enhancement requires version 1.7.6 or later of paramiko or
        paramiko-on-pypi packages:
         - http://pypi.python.org/pypi/paramiko/1.7.6
         - http://pypi.python.org/pypi/paramiko-on-pypi/1.7.6
        '''
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(self.ip_addr, self.port, self.username, self.password)

        self.channel = self.client.invoke_shell()
        self.transport = self.client.get_transport()
        self.buffer = ""


    def init_old(self):
        '''
        '''
        self.transport = paramiko.Transport((self.ip_addr, self.port))
        self.transport.connect(username = self.username, password = self.password,
                               hostkey = self.hostkey)
        self.channel = self.transport.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()

        self.buffer = ""


    def __del__(self):
        '''
        '''
        try:
            self.channel.close()
            self.transport.close()

        except:
            pass


    def _read(self):
        '''
        '''
        try:
            i = 0
            while i < 4:
                if self.channel.recv_ready():
                    self.buffer += self.channel.recv(1024)

                else:
                    time.sleep(0.1)
                    i += 1

        except:
            self.__del__()


    def read_until(self, expected, timeout = 0):
        '''
        '''
        if not expected:
            return ""

        base_time = time.time()
        while True:
            self._read()
            x = self.buffer.partition(expected)
            if x[1]:
                self.buffer = x[2]
                return "%s%s" % (x[0], x[1])

            if time.time() - base_time > timeout:
                return ""


    def expect(self, plist, timeout = 10):
        '''
        '''
        polist = []
        if type(plist) == str:
            _plist = [plist]

        elif type(plist) == list:
            _plist = plist

        else:
            raise Exception("<plist> should be <str> or <list>")

        for p in _plist:
            polist.append(re.compile(p))

        idx, mobj, txt = (-1, None, "")

        base_time = time.time()
        while True:
            self._read()
            for po in polist:
                mobj = po.search(self.buffer)
                if mobj:
                    idx = polist.index(po)
                    txt = self.buffer[:mobj.end()]
                    self.buffer = self.buffer[mobj.end():]
                    return (idx, mobj, txt)

            if time.time() - base_time > timeout:
                break

        return (idx, mobj, txt)


    def write(self, data):
        '''
        '''
        self.channel.send(data)


    def close(self):
        '''
        '''
        self.__del__()


if __name__ == "__main__":
    zdcli = sshclient("192.168.0.2")
#    idx, mobj, txt = zdcli.expect(["Please login:"])
#    if idx == -1:
#        print "Didn't see the login prompt"
#        exit()
#    zdcli.write("admin\n")
#    idx, mobj, txt = zdcli.expect(["Password:"])
#    if idx == -1:
#        print "Didn't see the password prompt"
#        exit()
#    zdcli.write("admin\n")
#    idx, mobj, txt = zdcli.expect(["ruckus%"])
#    if idx == -1:
#        print "Didn't see the command prompt"
#        exit()
#    zdcli.write("wlaninfo -A\n")
#    idx, mobj, txt = zdcli.expect(["ruckus%"])
#    if idx == -1:
#        print "Didn't see the command prompt"
#        exit()
#    print txt

    txt = zdcli.read_until("Please login:")
    if not txt:
        print "Didn't see the login prompt"
        exit()
    zdcli.write("admin\n")
    txt = zdcli.read_until("Password:")
    if not txt:
        print "Didn't see the password prompt"
        exit()
    zdcli.write("admin\n")
    txt = zdcli.read_until("ruckus%")
    if not txt:
        print "Didn't see the command prompt"
        exit()
    zdcli.write("wlaninfo -A\n")
    txt = zdcli.read_until("ruckus%")
    if not txt:
        print "Didn't see the command prompt"
        exit()
    print txt

    zdcli.close()

