import time
import os
import logging
import re

from RuckusAutoTest.common.DialogHandler import (
    DialogManager, BaseDialog,
)
from RuckusAutoTest.common import lib_Constant as constant

ADMIN_RESTART_LOCATORS = dict(
    # Administrator page
    restart_button = "//input[@id='restart']",

    restarting_span = "//div[@id='dialog_content']//h2",
    restarting_msg = "Restarting...",
)

xlocs = ADMIN_RESTART_LOCATORS


def reboot_zd(zd, **kwargs):
    conf = {'restart_timeout': 360}
    conf.update(**kwargs)

    logging.info("Rebooting Zone Director")

    # navigate to the Administer page, then the Restart section
    # click Start and wait for confirmation
    zd.navigate_to(zd.ADMIN, zd.ADMIN_RESTART)
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xlocs['restart_button'], 2)

    # confirm the message
    if zd.s.is_confirmation_present(5):
        zd.s.get_confirmation()

    if zd.s.is_element_present(xlocs['restarting_span'], 2):
        process_msg = zd.s.get_text(xlocs['restarting_span'])
        if process_msg != xlocs['restarting_msg']:
            raise Exception('[Restarting Error] The process should be "%s" instead of "%s"'
                            % (xlocs['restarting_msg'], process_msg))

    else:
        raise Exception('[Restarting error] The restore action does not form')

    start_reboot_time = time.time()
    while True:
        waiting_time = time.time() - start_reboot_time
        time.sleep(30)
        try:
            zd.do_login()
            logging.info('log in zd after zd reboot %s seconds'%waiting_time)
            break

        except:
            if waiting_time > conf['restart_timeout']:
                raise Exception('Could not login again to Zone Director after %s seconds' % waiting_time)


def download_single_file(zd, loc, filename = None, filename_re = None, pause = 30, save_to=None):
    try:
        # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
        time.sleep(2)
        dlg_mgr = DialogManager()
        #attention@author: chico@change: change pause from 3 seconds to 6 seconds, sometime PC lags will enlarge the echo time
        dlg1 = BaseDialog(title = None, text = "", button_name = "", key_string = "{PAUSE 3} %s {PAUSE 1} {ENTER}") 
        #attention@author: chico@change: change pause from 3 seconds to 6 seconds, sometime PC lags will enlarge the echo time
        dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "OK", key_string = "{PAUSE 3} %{F4}")

        dlg_mgr.add_dialog(dlg1)
        dlg_mgr.add_dialog(dlg2)

        if filename is not None:
            # Make the path to the file, which is supposed to be saved on the Desktop of the current logged in user
            if not save_to:
                file_path = os.path.join(constant.save_to, r"%s" % filename)
            else:
                file_path = os.path.join(save_to, filename)

            # Remove it if it is existing
            if os.path.isfile(file_path):
                os.remove(file_path)

        elif filename_re is not None:
            dlg1.set_title_re("Opening %s" % filename_re)
        
        dlg_mgr.start()
        time.sleep(10)
        
        zd.s.click_and_wait(loc)
        time.sleep(pause)

        if filename_re is not None:
            m = re.search("Opening (%s)" % filename_re, dlg1.get_title())
            if m: filename = m.groups()
            if type(filename) is tuple:
                filename = filename[0]
            if not save_to:
                file_path = os.path.join(constant.save_to, r"%s" % filename)
            else:
                file_path = os.path.join(save_to, filename)
            #chen.tao 2015-01-06, to resolve the download path problem
            #if it is downloaded to another folder, then copy to the target folder
            try:
                if not os.path.isfile(file_path):
                    import shutil
                    file_path_desktop = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % filename)
                    shutil.copy(file_path_desktop,file_path) 
            except:
                pass

        # Wait until the file is saved
        t0 = time.time()
        while time.time() - t0 < pause:
            if os.path.isfile(file_path): break

        if os.path.isfile(file_path):
            return file_path

    except:
        raise

    finally:
        # Regardless what has happened, stop the dialog handlers
        time.sleep(5)
        dlg_mgr.shutdown()
        time.sleep(2)



