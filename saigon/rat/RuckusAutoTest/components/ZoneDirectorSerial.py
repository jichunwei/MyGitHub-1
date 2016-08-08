"""
Common class to access ZoneDirector through serial port.
Required 3rd party package is serial (pyserial-2.4.win32.exe)

Usage:
    python ZoneDirectorSerial.py port='COM2' read_size=1000
    python rat/components/ZoneDirectorSerial.py
"""

import re
import time
import sys
import serial

PROMPT = [re.compile(r" (login)\s*:\s+$", re.M | re.I),
   re.compile(r"^(Password)\s*:\s+$", re.M | re.I),
   re.compile(r"^(ruckus)%\s+$", re.M),
   ]

ATR = {'username': "admin", 'password': "admin", 'eol': "\r", 'read_size': 2046,
   'stdout': 1, 'debug': 0, 'timeout': 0.25, 'debuglevel': 0,
   'recv_pause': 0.25, 'pause': 2 , 'init': False}

SERIAL_DEFAULT = dict(port = 'COM1', baudrate = 115200, bytesize = 8, parity = 'N', stopbits = 1, xonxoff = 0, rtscts = 0)

class ZoneDirectorSerial2:

    def __init__(self, **attrs):
        self.conf = ATR.copy()
        self.conf.update(SERIAL_DEFAULT)
        self.conf.update(attrs)
        self.prompt_list = PROMPT[:]
        self.log_file = None
        if self.conf['init']: self.connect()

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass

    def connect(self, **attrs):
        self.conf.update(attrs)
        self.disconnect()
        self.ser = serial.Serial(self.conf['port']
                                , self.conf['baudrate']
                                , bytesize = self.conf['bytesize']
                                , parity = self.conf['parity']
                                , stopbits = self.conf['stopbits']
                                , timeout = self.conf['timeout']
                                , xonxoff = self.conf['xonxoff']
                                , rtscts = self.conf['rtscts'])
        self.login()

    def login(self):
        self.ser.write('\r')
        while True:
            (ecode, m, response) = self.recv()
            if m:
                self.prompt = m.group(1)
                if re.match('.*login', self.prompt, re.I):
                    self.send(self.conf['username'])
                elif re.match('.*password', self.prompt, re.I):
                    self.send(self.conf['password'])
                else:
                    return self.prompt
            else:
                time.sleep(2)
                self.ser.write('\r')

    def disconnect(self):
        try:
            self.ser.close()
        except:
            pass
        self.ser = None

    def add_prompt_list(self, plist):
        if type(plist) is str:
            self.prompt_list.append(re.compile(str))
        elif hasattr(plist, 'search'):
            self.prompt_list.append(plist)
        elif type(plist) is list:
            for p in plist:
                if type(p) is str:
                    self.prompt_list.append(re.compile(p))
                elif hasattr(p, 'search'):
                    self.prompt_list.append(p)

    def set_prompt_list(self, plist):
        self.prompt_list = []
        self.add_prompt_list(plist)

    def send(self, cmd):
        self.ser.write(cmd + '\r')
        self.ser.flush()

    def recv(self, **kwargs):
        atrs = dict(timeout = 60, prompt = None)
        atrs.update(kwargs)
        plist = self.prompt_list[:]
        if type(atrs['prompt']) is str:
            plist.append(re.compile(atrs['prompt']))
        elif hasattr(atrs['prompt'], 'search'):
            plist.append(atrs['prompt'])
        time_start = time.time() if atrs['timeout'] else None
        self.exp_output = ''
        while True:
            if not self.ser: raise 'Serial port is not opened'
            inbuf = self.ser.read(self.conf['read_size'])
            if inbuf and len(inbuf) > 0:
                if self.conf['stdout']: print inbuf,
                self.exp_output += inbuf
                for i in range(len(plist)):
                    m = plist[i].search(self.exp_output)
                    if m:
                        self.prompt = m.group(1)
                        return (i, m, self.exp_output)
            else:
                if time_start:
                    if (time.time() - time_start) > atrs['timeout']:
                        break
        return (-1, None, self.exp_output)

    def perform(self, cmd, **kwargs):
        atrs = dict(timeout = None, prompt = None)
        atrs.update(kwargs)
        self.send(cmd)
        self.last_perform = self.recv(**atrs)
        return self.last_perform[2]

    def goto_cli(self):
        data = self.perform('help')
        if re.search('!v54!', data): self.perform('!v54!')

    def goto_shell(self):
        data = self.perform('help')
        if not re.search('!v54!', data): self.perform('!v54!')

    def interactive(self):
        stdout = self.conf['stdout']
        self.conf['stdout'] = 1
        self.send('')
        self.recv()
        while True:
            print '(Q or X to exit): '
            cmd = raw_input('')
            if re.match(r'^(Q|X)', cmd):
                break
            self.send(cmd)
            self.recv()
        self.conf['stdout'] = stdout


class ZoneDirectorSerial(ZoneDirectorSerial2):
    '''
    '''

func_map = {
    'addpromptlist': 'add_prompt_list',
    'setpromptlist': 'set_prompt_list',
    'gotoCLI': 'goto_cli',
    'gotoShell': 'goto_shell',

}

for attr, attr2 in func_map.items():
    # dynamically attaches the new methods to ZoneDirector from ZoneDirectorSerial2
    # if they do not exist
    try:
        getattr(ZoneDirectorSerial, attr)
    except:
        setattr(ZoneDirectorSerial, attr, getattr(ZoneDirectorSerial, attr2))


if __name__ == "__main__":
    from RuckusAutoTest.common import lib_KwList

    _dict = lib_KwList.as_dict(sys.argv[1:])
    con = ZoneDirectorSerial2(**_dict)
    con.connect()
    con.interactive()

