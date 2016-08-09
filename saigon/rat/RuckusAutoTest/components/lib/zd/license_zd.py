import logging
import time
import re

LOCATORS_CFG = dict(
    cur_license_text = "//p[@id='curlicense']",
    upload_license_filename = "//input[@id='filename-uploadlicense']",
    uploaded_license_text = "//span[@id='uploaded-uploadlicense']",
    perform_upload_license_button = "//input[@id='perform-uploadlicense']",
    error_upload_license_text = "//span[@id='error-uploadlicense']",
    delete_license_link = "//table[@id='license']//tr[td='%s']/td/span[text()='Delete']",
    license_detail_link = "//table[@id='license']//tr[td='%s']/td/span[text()='Detail']",
    first_license_delete_link = "//span[@id='license-delete-license-0']",
    license_info_row = "//table[@id='license']//tr[%s]/td[%s]",

    qa_hack_key_textbox = "//input[@id='key']",
    qa_hack_ok_button = "//input[@name='ok']",
    qa_hack_delete_temp_license_button = "//tr[th='Delete Temporary License']/td/input",
    qa_hack_time_ratio_listbox = "//select[@id='time-ratio']",
    qa_hack_apply_button = "//table//tr[th='License Check Speed Up']//input[@value='Apply']",
)

def import_license(zd, license_path):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)
        zd.s.type_text(l['upload_license_filename'], license_path, 2)

        t0 = time.time()
        while time.time() - t0 < 15:
            time.sleep(2)
            if zd.s.is_visible(l['uploaded_license_text']):
                break

        zd.s.choose_ok_on_next_confirmation()
        zd.s.click_and_wait(l['perform_upload_license_button'])
        if zd.s.is_confirmation_present(5):
            logging.info("Catch a confirmation message: %s" % zd.s.get_confirmation())

        time.sleep(2)
        if zd.s.is_visible(l['error_upload_license_text']):
            raise Exception(zd.s.get_text(l['error_upload_license_text']))

    except Exception, e:
        if zd.s.is_visible(l['error_upload_license_text']):
            raise Exception(zd.s.get_text(l['error_upload_license_text']))

        logging.info("Catch the error [%s]" % e.message)
        raise


def get_all_license(zd):
    l = LOCATORS_CFG
    license_info = {'feature': 1, 'order_number': 2, 'status': 3}
    license_list = []

    try:
        zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)

        tr_idx = 1
        while True:
            try:
                license = {}
                for key, td_idx in license_info.items():
                    license[key] = zd.s.get_text(l['license_info_row'] % (tr_idx, td_idx))

                if zd.s.is_element_present(l['license_detail_link'] % license['feature']):
                    zd.s.click_and_wait(l['license_detail_link'] % license['feature'])
                    license['detail'] = zd.s.get_alert()

                else:
                    license['detail'] = ''

            except Exception, e:
                if "not found" in e.message:
                    break

                else:
                    raise

            license_list.append(license)
            tr_idx += 1

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise

    return license_list


def remove_permanent_license(zd, license_feature):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)

        if zd.s.is_element_present(l['delete_license_link'] % license_feature):
            zd.s.click_and_wait(l['delete_license_link'] % license_feature)

        else:
            raise Exception("The license doesn't exist or it is not a permanent license")

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise


def remove_all_permanent_licenses(zd):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)

        while True:
            try:
                zd.s.click_and_wait(l['first_license_delete_link'])
                time.sleep(2)

            except Exception, e:
                if "not found" in e.message:
                    break

                raise

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise


def remove_temporary_license(zd, qa_hack_page = "/admin/admin_eng.jsp", qa_hack_key = "RST123!"):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
        zd.s.open(zd.url + qa_hack_page)
        zd.s.type_text(l['qa_hack_key_textbox'], qa_hack_key)
        zd.s.click_and_wait(l['qa_hack_ok_button'])

        zd.s.click_and_wait(l['qa_hack_delete_temp_license_button'])

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise

    #PHANNT@20100427: logout is needed to reset current_tab/current_menu
    zd.logout()


def set_expiration_ratio(zd, ratio, qa_hack_page = "/admin/admin_eng.jsp", qa_hack_key = "RST123!"):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
        zd.s.open(zd.url + qa_hack_page)
        zd.s.type_text(l['qa_hack_key_textbox'], qa_hack_key)
        zd.s.click_and_wait(l['qa_hack_ok_button'])

        zd.s.select_option(l['qa_hack_time_ratio_listbox'], "%s.*" % ratio)
        zd.s.click_and_wait(l['qa_hack_apply_button'])

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise

    #PHANNT@20100427: logout is needed to reset current_tab/current_menu
    zd.logout()


def get_current_license_capability(zd):
    l = LOCATORS_CFG

    try:
        zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)
        txt = zd.s.get_text(l['cur_license_text'])

    except Exception, e:
        logging.info("Catch the error [%s]" % e.message)
        raise

    mobj = re.search("which supports ([\d]+) APs and ([\d]+) clients", txt)
    if not mobj:
        raise Exception("The current license text shown on the ZD was not as expected: %s" % txt)

    return {'max_ap': mobj.group(1), 'max_client': mobj.group(2)}

