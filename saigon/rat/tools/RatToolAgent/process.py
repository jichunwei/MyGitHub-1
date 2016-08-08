'''
Simple process management.

Allows to launch, kill and see the status of a process independently
from the platform (at least on Win32 and Unix).

B{Classes}
  -  L{Process}         -- Abstract base class for a process.
  -  L{Win32Process}    -- a WIN32 process.

B{Usage}
    - Execute a cmd in a separate process: p = createProcess(cmd)
    - "Wrap" an existing process (pid): p = wrapProcess(pid)
'''

import os, sys, string, time

true, false = -1, 0

class ProcessError(Exception):
    ''' Exception raised by the process module.
    '''
    pass

#-----------------------------------------------------------------------------
class Process:
#-----------------------------------------------------------------------------
    ''' Abstract base class for a Process.
        => Derive specialized classes for each OS.
    '''
    MIN_LIFE_TIME = 1.0 # Minimum lifetime of a process in sec

    def __init__(self, cmd, pid, detached):
        ''' Runs the program C{cmd} in a new process or wraps the given
            process.

            NB: this base class constructor MUST be called by derived classes
            to initialize attributes.

            @param cmd:  The program command line (may be None).
            @param pid:  The process ID (in case of wrap)
            @param detached: (if creation) Whether the process will survive its
                            parent.

        '''
        self.cmd = cmd
        self.pid = pid
        self.detached = detached
        self.exitCode = None
        self.killed = false
        self.startedOn = time.time()    # N.S. if not launched by us

    def __repr__(self):
        exitCode = self.getExitCode()
        if exitCode is None:
            state = 'alive'
        else:
            state = 'ended, exit code=%d' % exitCode
        return '<%s pid=%d, %s>' % (self.__class__.__name__, self.pid, state)

    def getCmd(self):
        ''' Returns the command string executed by the process.
        '''
        return self.cmd

    def getPid(self):
        ''' Returns the PID of the process.
        '''
        return self.pid

    def killed(self):
        ''' Returns true if process was killed (via kill).
        '''
        return self.killed

    def isAlive(self):
        ''' Returns true if process is alive.
        '''
        return self.getExitCode() is None


    # Private:

    def _ensureMinLifeTime(self, minTime=None):
        ''' Sleeps until the process has lived at least C{minTime} sec.

            This is used to avoid killing the process too fast (this leads
            to strange result codes).
        '''
        if minTime is None:
            minTime = self.MIN_LIFE_TIME
        delta = time.time() - (self.startedOn + minTime)
        if delta < 0:
            time.sleep(-delta)



if sys.platform == 'win32':
    try:
        from win32process import CreateProcess, TerminateProcess, GetExitCodeProcess, STARTUPINFO
        import win32event, win32api, win32con, pywintypes
    except ImportError, e:
        raise ProcessError("Import error: %s. Have you installed the "
                    "Python win32 extensions ?" % e)
    class Win32Process(Process):
        ''' A Win32 process.
        '''

        def __init__(self, cmd=None, pid=0, detached=false):
            ''' Runs the program C{cmd} in a new process or wraps a process.

                If C{cmd} is specified (non empty), the command is executed in
                a new process. C{pid} is non significant.

                If C{cmd} is empty, wraps the existing process whose pid is
                given in C{pid}.

                @param cmd: The program command line (may be None).
                @param pid: The process ID (in case of wrap)
                @param detached: (if creation) Whether the process will survive
                        its parent. On Win32 processes are independent, so
                        so this simply means that parent and child must have
                        separate consoles to avoid killing the child when the
                        parent console is closed.
            '''
            if cmd:
                if detached:
                    createFlags =  win32con.CREATE_NEW_CONSOLE
                else:
                    createFlags = 0
                hp, ht, pid, tid = CreateProcess(None, cmd, None, None, 1,
                                                 createFlags,
                                                 None, None, STARTUPINFO())
            else:
                cmd = None
                assert pid
                try:
                    hp = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,
                                              0, pid)
                except pywintypes.error, e:
                    raise ProcessError("Can't get handle from pid=%s: %s" % (pid, e))

            self.handle = hp    # [PyHANDLE] Win32 process handle
            Process.__init__(self, cmd, pid, detached)

        def wait(self, timeout=None):
            ''' See class L{Process}.
            '''
            if timeout is not None:
                timeout = int(timeout * 1000)   # in ms
            else:
                timeout = win32event.INFINITE
            win32event.WaitForSingleObject(self.handle, timeout)
            return self.getExitCode()

        def kill(self):
            ''' See class L{Process}.
            '''
            if self.isAlive():
                self._ensureMinLifeTime()
                TerminateProcess(self.handle, -1)
                self.wait()     # ensure exit code known.
                self.killed = true
                self.getExitCode() # refresh attributes

        def getExitCode(self):
            ''' See class L{Process}.
            '''
            exitCode = GetExitCodeProcess(self.handle)
            if exitCode <>  259:    # (259 means alive, keep exitCode==None)
                self.exitCode = exitCode
            return self.exitCode


def createProcess(cmd, detached=false):
    ''' Runs the program C{cmd} in a new process.

        @param cmd:  The program command line.
        @param detached: (if creation) Whether the process will survive its
                        parent.
        @return: a Process object.
        @exception ProcessError: The program cannot be launched.
        @see: L{wrapProcess}
    '''
    import types
    if not isinstance(cmd, types.StringType) or not cmd:
        raise ProcessError('cmd should be a non empty string')
    if sys.platform == 'win32':
        f = Win32Process
    else:
        raise ProcessError('Only Win32 is supported.')

    return f(cmd, 0, detached)

def wrapProcess(pid):
    ''' Wraps an existing process.

        @param pid: The ID of the process to wrap.
        @return: a Process object.
        @exception ProcessError:
    '''
    if sys.platform == 'win32':
        f = Win32Process
    else:
        raise ProcessError('Only Win32 is supported.')

    return f(pid=pid)

def test():

    print 'Testing module "process"'
    if sys.platform == 'win32':
        cmd = 'zapd'

    p = createProcess(cmd)
    print p
    assert p.isAlive()
    p.kill(hard=false)
    print p
    assert not p.isAlive()

    p1 = createProcess(cmd, detached=true)
    p2 = wrapProcess(p1.getPid())
    print p2
    assert p2.isAlive()
    p2.kill(hard=true)
    print p2
    assert not p2.isAlive()
    print p1    # same as p2

    print '=> Tests passed.'
    return p

if __name__ == "__main__":
    p = test()
