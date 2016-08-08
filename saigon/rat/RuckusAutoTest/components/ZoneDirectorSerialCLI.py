# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
ZoneDirectorSerialCLI controls ZoneDirector via Console Port.

Examples:

    from ratenv import *
    from RuckusAutoTest.components.ZoneDirectorSerialCLI import ZoneDirectorSerialCLI2
    dd = dict(port='COM1', username='admin', password='admin')
    zds = ZoneDirectorSerialCLI2(dd)
    zds.connect()


"""
import time
import logging

from RuckusAutoTest.components.ZoneDirectorSerial import ZoneDirectorSerial2

class ZoneDirectorSerialCLI2(ZoneDirectorSerial2):

    def __init__(self, config):
        """
        Connect to the Ruckus ZD through its serial port (COM port, default COM1).
        All subsequent CLI operations will be subject to the specified default timeout.
        If log file is specified then CLI output will be logged to the specified file.
        """
        conf = dict(init = True)
        conf.update(config)
        ZoneDirectorSerial2.__init__(self, **conf)
        # you need to call initialize() if init is False

    def __del__(self):
        self.disconnect()

    def log(self, txt):
        """
        Log specified text if a log file is configured
        """

        if self.log_file:
            stime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            self.log_file.write("\r%s\r%s" % (stime, txt))

    def initialize(self):
        self.conf['init'] = True
        self.connect()

    def do_cmd(self, cmd, **atrs):
        # CLI commands are availabe in Shell environment
        # self.goto_cli()
        result = self.perform(cmd, **atrs)
        return result

    def do_shell_cmd(self, cmd, **atrs):
        self.goto_shell()
        result = self.perform(cmd, **atrs)
        # CLI commands are availabe in Shell environment
        # self.goto_cli()
        return result

    # example:
    #
    #   data = zds.do_cmd_block("show ap\nshow system")
    #   for x in data:
    #       print "Command: %s\nReply: %s" % (x[0], x[1])
    #
    def do_cmd_block(self, cmd_block, **atrs):
        # self.goto_cli()
        results = self._do_cmds(cmd_block, **atrs)
        return results

    # example:
    #
    #   data = zds.do_shell_cmd_block("ifconfig br0\napmgrinfo -a")
    #
    def do_shell_cmd_block(self, cmd_block, **atrs):
        self.goto_shell()
        results = self._do_cmds(cmd_block, **atrs)
        # self.goto_cli()
        return results

    def _do_cmds(self, cmd_block, **atrs):
        results = []
        for cmd in cmd_block.split('\n'):
            result = self.perform(cmd, **atrs)
            results.append([cmd, result])
        return results

class ZoneDirectorSerialCLI(ZoneDirectorSerialCLI2):
    '''
    '''

func_map = {
    'doCmd': 'do_cmd',
    'doShellCmd': 'do_shell_cmd',
    'doCmdBlock': 'do_cmd_block',
    'doShellCmdBlock': 'do_shell_cmd_block',

}

for attr, attr2 in func_map.items():
    # dynamically attaches the new methods to ZoneDirector from ZoneDirectorSerialCLI2
    # if they do not exist
    try:
        getattr(ZoneDirectorSerialCLI, attr)
    except:
        setattr(ZoneDirectorSerialCLI, attr, getattr(ZoneDirectorSerialCLI, attr2))
