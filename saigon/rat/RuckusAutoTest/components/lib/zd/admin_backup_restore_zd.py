import logging
import re
import time
import traceback

from RuckusAutoTest.components.lib.zd import control_zd as control_zd

LOCATORS_ADMIN_BACKUP_RESTORE = {
    'administer_backup_span': "//span[@id='admin_backup']",

    'backup_button': "//input[@value='Back up']",

    'restore_file_location_textbox': "//input[@id='filename-restore']",
    'perform_restore_button': "//input[@id='perform-restore']",
    'cancel_restore_button': "//a[@id='cancel-restore']",
    'restore_everything_radio': "//input[@id='restore_errorinput_0']",
    'restore_everything_except_ip_radio': "//input[@id='restore_errorinput_1']",
    'restore_basic_config_radio': "//input[@id='restore_errorinput_2']",

    'error_restore_span': "//span[@id='error-restore']",
    'error_file_msg': 'The backup file that you selected is not a valid configuration file or it may be corrupted. Please select another backup file.',

    'restoring_span': "//div[@id='dialog_content']//h2",
    'restoring_msg': "Restoring...",

}

xlocs = LOCATORS_ADMIN_BACKUP_RESTORE

def backup(zd, save_to=None, retry=3):
    """
    """
    # Go to the Administer --> Backup
    zd.navigate_to(zd.ADMIN, zd.ADMIN_BACKUP)
    while retry:
        try:
            backup_button = xlocs['backup_button']
            file_path = control_zd.download_single_file(zd, backup_button, filename_re = '.+.bak', save_to=save_to)
            if file_path:
                break
            logging.debug('The current configuration of Zone Director is backup at %s' % file_path)
        except:
            logging.warning(traceback.format_exc())
        finally:
            retry = retry - 1

    if not file_path:
        raise Exception("Backup fail! the file is empty, please check.")

    return file_path


def restore(zd, **kwargs):
    """
    """
    conf = {'restore_file_path': '',
            'restore_type': 'restore_everything',
            'timeout': 120,
            'reboot_timeout': 120}
    conf.update(**kwargs)

    zd.navigate_to(zd.ADMIN, zd.ADMIN_BACKUP)

    logging.debug('Restore the Zone Director configuration from file %s' % conf['restore_file_path'])
    zd.s.type_text(xlocs['restore_file_location_textbox'], conf['restore_file_path'])

    start_time = time.time()
    while True:
        loading_time = time.time() - start_time
        if zd.s.is_element_present(xlocs['perform_restore_button']):
            break

        if zd.s.is_element_present(xlocs['error_restore_span']):
            errmsg = zd.s.get_text(xlocs['error_restore_span'])
            if errmsg == xlocs['error_file_msg']:
                raise Exception(errmsg)

        if loading_time > conf['timeout']:
            errmsg = 'Zone Director could not load the file %s to restore after %s seconds'
            errmsg = errmsg % (conf['restore_file_path'], loading_time)
            raise Exception(errmsg)


    restore_type_radio = xlocs[conf['restore_type'] + '_radio']
    if zd.s.is_element_present(restore_type_radio):
        zd.s.click_and_wait(restore_type_radio)

    else:
        raise Exception('The restore type "%s" does not exist' % conf['restore_type'].replace('_', ' '))

    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xlocs['perform_restore_button'])

    # confirm the message
    if zd.s.is_confirmation_present(5):
        zd.s.get_confirmation()

    if zd.s.is_element_present(xlocs['restoring_span']):
        process_msg = zd.s.get_text(xlocs['restoring_span'])
        if process_msg != xlocs['restoring_msg']:
            raise Exception('[Restoring Error] The process should be "%s" instead of "%s"'
                            % (xlocs['restoring_msg'], process_msg))

    else:
        raise Exception('[Restoring error] The restore action does not form')

    logging.debug('Zone Director is restoring. Wait for it ups')
    start_reboot_time = time.time()
    while True:
        waiting_time = time.time() - start_reboot_time
        # ZoneDirector is being restored to a previously archived configuration.
        # Please wait one minute before reconnecting to <zd_ip>
        time.sleep(60)
        try:
            zd.do_login()
            break

        except:
            if waiting_time > conf['reboot_timeout']:
                raise Exception('Could not login again to Zone Director after %s seconds' % waiting_time)

    logging.debug('The restore process worked successfully')

