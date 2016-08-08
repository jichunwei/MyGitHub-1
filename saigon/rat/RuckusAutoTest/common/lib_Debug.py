__author__ = "TechinAlexKang"
__date__ = "$Oct 25, 2008 10:33:00 AM$"

"""
Import me in the module you want to step through.
On the directory you launch your main program, touch the file name
to bring up Python Debugger.

File RAT_TRACE_IGNORE overwrite others.
The default file to trigger debugging is RAT_TRACE_ON.
You can provide a specific name in your own program/module/script
to step through your program.

Example:
    # step into debug right before rat call test case's test() method
    import lib_Debug as bugme
    ...
    bugme.do_trace()
    ...
    bugme.do_trace(bugme.RAT_TRACE_TEST_TEST)
    ...
    bugme.do_trace('TRACE_RAT_STATION')  # user defined filename

ATTENTION:

    To avoid accidentally delte rat.db; the file names of break points
    are changed. They are now all begin with TRACE_RAT, not RAT_TRACE.

    RAT_TRACE_ON -> TRACE_RAT_ON

    The symbolic names are still begin with RAT_TRACE to indicate the
    original of the project this application is running under.
"""

# predefined filename recognized by rat framework RunTest mechanism

# global breaking point
RAT_TRACE_IGNORE = 'TRACE_RAT_IGNORE'   # if exist, NO step into debug mode
RAT_TRACE_ON = 'TRACE_RAT_ON'           # if exist, STEP into debug mode

# breakpoint before executing test case
RAT_TRACE_RUNTEST = 'TRACE_RAT_RUNTEST'             # debug RunTest()
RAT_TRACE_TEST_CONFIG = 'TRACE_RAT_TEST_CONFIG'     # debug testobj.config()
RAT_TRACE_TEST_TEST = 'TRACE_RAT_TEST_TEST'         # debug testobj.test()
RAT_TRACE_TEST_CLEANUP = 'TRACE_RAT_TEST_CLEANUP'   # debug testobj.cleanup()

# after event breakpoint if test is ERROR, PASS, FAIL
RAT_TRACE_ON_ERROR = 'TRACE_RAT_ON_ERROR'   # debug error'd test
RAT_TRACE_ON_PASS = 'TRACE_RAT_ON_PASS'     # debug passed test
RAT_TRACE_ON_FAIL = 'TRACE_RAT_ON_FAIL'     # debug failed test

import os
import pdb

def do_trace(trace_on_file = ''):
    # RAT_TRACE_IGNORE overpower every debug attempt
    if os.path.exists(RAT_TRACE_IGNORE): return
    # default initate TRACE if RAT_TRACE_ON exist
    if os.path.exists(RAT_TRACE_ON) or (trace_on_file and os.path.exists(trace_on_file)):
        pdb.set_trace()

# trigger the breakpoint only when trace_on_file exists
def do_trace_on(trace_on_file):
    # RAT_TRACE_IGNORE overpower every debug attempt
    if os.path.exists(RAT_TRACE_IGNORE): return
    if trace_on_file and os.path.exists(trace_on_file):
        pdb.set_trace()

