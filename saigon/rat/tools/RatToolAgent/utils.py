import os
import time

from DialogHandler import BaseDialog, DialogManager
from RuckusAutoTest.common import lib_Constant as constant


def try_interval(timeout = 180, interval = 2):
    '''
    Simplify the re-trying actions in a definite interval
    A try_times() should be developed accordingly
    '''
    t, end_time = time.time(), time.time() + timeout
    while t < end_time:
        yield t
        time.sleep(interval)
        t = time.time()


def download_file_firefox(file_name = None):
    '''
    This function is to download file from FireFox browser to current user home
    directory.
    Note that: This function only works with FireFox
    '''
    # get user home directory
    file_path = os.path.join(constant.save_to, file_name)#Chico, 2015-8-13

    remove_file(file_path)
    # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
    dlg1 = BaseDialog(
        title = "Opening %s" % file_name, text = "", button_name = "",
        key_string = "{PAUSE 1}%{s}{PAUSE 0.5}{ENTER}"
    )
    dlg2 = BaseDialog(
        title = "Downloads", text = "", button_name = "", key_string = "%{F4}"
    )
    dlg_mgr = DialogManager()

    dlg_mgr.add_dialog(dlg1)
    dlg_mgr.add_dialog(dlg2)

    dlg_mgr.start()

    # Wait until the file is saved
    for i in try_interval(15, 2):
        if os.path.isfile(file_path): break

    # Regardless what has happened, stop the dialog handlers
    dlg_mgr.shutdown()
    time.sleep(2)
    if os.path.isfile(file_path):
        return file_path

    raise Exception("Unable to download and save the file to [%s]" % file_path)


def remove_file(file_path):
    '''
    This function is to remove a file if it exists
    '''
    if os.path.isfile(file_path):
        os.remove(file_path)

