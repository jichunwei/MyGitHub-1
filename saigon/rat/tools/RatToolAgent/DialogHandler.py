import threading
import time

from pywinauto import application
from pywinauto import handleprops
from pywinauto import controls

class BaseDialog:
    """
    This class defines a general dialog that can be identified by a title,
    may be a static text inside it, and can be handled by clicking
    a specified button, or at a specified coordinate.

    All available variables for Windows finding that can be set to
    BaseDialog's instances are as follows:
        * class_name
        *     Windows with this window class
        * class_name_re
        *     Windows whose class match this regular expression
        * parent
        *     Windows that are children of this
        * process
        *     Windows running in this process
        * title
        *     Windows with this Text
        * title_re
        *     Windows whose Text match this regular expression
        * top_level_only
        *     Top level windows only (default=True)
        * visible_only
        *     Visible windows only (default=True)
        * enabled_only
        *     Enabled windows only (default=True)
        * best_match
        *     Windows with a title similar to this
        * handle
        *     The handle of the window to return
        * ctrl_index
        *     The index of the child window to return
        * active_only
        *     Active windows only (default=False)
    """

    def __init__(self, title, text, button_name, key_string = "", coords = []):
        """ The class's constructor

        Input:
        - title: the title of the dialog
        - text: a text that appears inside the dialog
        - button_name: name of the button inside the dialog that the handle() function clicks on
        - key_string: string of key that is sent to the dialog to close it
        - coords: list of coordinates that the dialog will click at to close it
        """
        self._class_name = None
        self._class_name_re = None
        self._parent = None
        self._process = None
        self._title = None
        self._title_re = None
        self._top_level_only = True
        self._visible_only = True
        self._enabled_only = True
        self._best_match = None
        self._handle = None
        self._ctrl_index = None
        self._predicate_func = None
        self._active_only = False

        self.set_title(title)
        self.set_static_text(text)
        self.set_button_name(button_name)
        self.set_key_string(key_string)
        self.set_coords_list(coords)


    def get_static_text(self):
        return self._static_text


    def get_button_name(self):
        return self._button_name


    def get_key_string(self):
        return self._key_string


    def get_coords_list(self):
        return self._coords_list


    def get_class_name(self):
        return self._class_name


    def get_class_name_re(self):
        return self._class_name_re


    def get_parent(self):
        return self._parent


    def get_process(self):
        return self._process


    def get_title(self):
        return self._title


    def get_title_re(self):
        return self._title_re


    def get_top_level_only(self):
        return self._top_level_only


    def get_visible_only(self):
        return self._visible_only


    def get_enabled_only(self):
        return self._enabled_only


    def get_best_match(self):
        return self._best_match


    def get_handle(self):
        return self._handle


    def get_ctrl_index(self):
        return self._ctrl_index


    def get_predicate_func(self):
        return self._predicate_func


    def get_active_only(self):
        return self._active_only


    def set_static_text(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: part of the static text inside the dialog to look for
        """
        self._static_text = value


    def set_button_name(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: name of the button inside the dialog that the handle() function clicks on
        """
        self._button_name = value


    def set_key_string(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: string of key that is sent to the dialog to close it
        """
        self._key_string = value


    def set_coords_list(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: list of coordinates that the dialog will click at to close it
        """
        self._coords_list = value


    def set_class_name(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows with this window class
        """
        self._class_name = value


    def set_class_name_re(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows whose class match this regular expression
        """
        self._class_name_re = value


    def set_parent(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows that are children of this
        """
        self._parent = value


    def set_process(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows running in this process
        """
        self._process = value


    def set_title(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows with this Text
        """
        self._title = value


    def set_title_re(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows whose Text match this regular expression
        """
        self._title_re = value


    def set_top_level_only(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Top level windows only (default = True)
        """
        self._top_level_only = value


    def set_visible_only(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Visible windows only (default = True)
        """
        self._visible_only = value


    def set_enabled_only(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Enabled windows only (default = True)
        """
        self._enabled_only = value


    def set_best_match(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Windows with a title similar to this
        """
        self._best_match = value


    def set_handle(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: The handle of the window to return
        """
        self._handle = value


    def set_ctrl_index(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: The index of the child window to return
        """
        self._ctrl_index = value


    def set_predicate_func(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: part of the static text inside the dialog to look for
        """
        self._predicate_func = value


    def set_active_only(self, value):
        """
        * Sets the criterion to pass into the find_windows's params
        *
        * param:
        *     - value: Active windows only (default = False)
        """
        self._active_only = value


    def handle(self):
        """ Find the dialog with the specified title and text.

        Then click at the specified button or send the key string to it to close it.
        """
        # Check if the dialog with the specified text exists or not
        dlg_handle_list = application.findwindows.find_windows(
            self._class_name, self._class_name_re,
            self._parent, self._process,
            self._title, self._title_re,
            self._top_level_only, self._visible_only, self._enabled_only,
            self._best_match, self._handle, self._ctrl_index,
            self._predicate_func, self._active_only
        )

        if (len(dlg_handle_list) == 0):
            return False

        # Yes, get the handle of it
        handle_id = dlg_handle_list[0]

        # Verify if it is a real dialog
        if not(handleprops.iswindow(handle_id)):
            return False

        # Get the handles of the controls
        hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
        child_ctrls_list = hwnd.Children()

        # Verify the text inside if required
        if len(self._static_text) > 0:
            # Access all the child controls of the dialog
            # and verify the text
            found = False
            for child_obj in child_ctrls_list:
                if child_obj.Class() == "Static" and self._static_text in child_obj.WindowText():
                    found = True
                    break

            if not found:
                return False

        # The dialog is found
        # set the instance's properties
        self._set_properties(handle_id)

        # Now try to close it by clicking on a button
        if len(self._button_name) > 0:
            for child_obj in child_ctrls_list:
                if child_obj.Class() == "Button" and self._button_name == child_obj.WindowText():
                    child_obj.Click()
                    return True

        # Send the key string to the dialog
        if self._key_string:
            hwnd.TypeKeys(self._key_string)
            return True

        # Or click on the sequence of coordinates if required
        if len(self._coords_list):
            for coords in self._coords_list:
                hwnd.ClickInput(coords = coords)

        # Try to click on the X button at the top-right corner as the last resort
        hwnd.Close()

        # Unable to handle the dialog
        return False


    def _set_properties(self, handle_id):
        """
        * set the instance's properties
        """
        self.set_title(handleprops.text(handle_id))

        # if needed, specify other properties to set
        #


class StandardDialog(BaseDialog):
    """ This class implements the class that handles Windows standard Save As/Choose file dialogs
    """
    # Dialog types
    IE_SAVE_AS_DLG = 1
    IE_CHOOSE_FILE_DLG = 2
    FF_SAVE_FILE_DLG = 3

    def __init__(self, dialog_type, file_path):
        if (dialog_type == self.IE_SAVE_AS_DLG):
            BaseDialog.__init__(self, title = "Save As", text = "",
                                button_name = "&Save", key_string = "")

        elif (dialog_type == self.IE_CHOOSE_FILE_DLG):
            BaseDialog.__init__(self, title = "Choose file", text = "",
                                button_name = "&Open", key_string = "")

        elif dialog_type == self.FF_SAVE_FILE_DLG:
            BaseDialog.__init__(self, title = "Enter name of file to save to...", text = "",
                                button_name = "&Save", key_string = "")

        self.file_path = file_path


    def handle(self):
        """ Find the dialog with the specified title and text.
        Then click at the specified button or send the key string to it to close it.
        """

        # Check if the dialog with the specified text exists or not
        dlg_handle_list = application.findwindows.find_windows(
            self._class_name, self._class_name_re,
            self._parent, self._process,
            self._title, self._title_re,
            self._top_level_only, self._visible_only, self._enabled_only,
            self._best_match, self._handle, self._ctrl_index,
            self._predicate_func, self._active_only
        )

        if (len(dlg_handle_list) == 0):
            return False

        # Yes, get the handle of it
        handle_id = dlg_handle_list[0]

        # Verify if it is a real dialog
        if not(handleprops.iswindow(handle_id)):
            return False

        # Get the handles of the controls
        hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
        child_ctrls_list = hwnd.Children()

        # The dialog is found
        # Now enter the file name to the textbox
        button_ok = False
        for child_obj in child_ctrls_list:
            if child_obj.Class() == "Edit" and child_obj.ControlID() == 1148:
                child_obj.SetText(self.file_path)
                button_ok = True

        if button_ok:
            for child_obj in child_ctrls_list:
                if child_obj.Class() == "Button" and self._button_name == child_obj.WindowText():
                    child_obj.Click()
                    return True

        # Unable to handle the dialog
        return False


class DialogManager(threading.Thread):
    """ This class implements a thread that monitors the dialogs of the class BaseDialog
    and calls their method handle() to close them at predefined interval
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.dlg_list = []
        self.btn_shutdown = False

    def run(self):
        """ The main function that implements the thread's logic
        """
        while not self.btn_shutdown:
            for dlg_obj in self.dlg_list:
                dlg_obj.handle()
            time.sleep(2)

    def shutdown(self):
        """ Shut down the dialog manager
        """
        self.btn_shutdown = True

    def add_dialog(self, dialog):
        """ Add a dialog of class "BaseDialog" to the dialog manager
        """
        self.dlg_list.append(dialog)


if __name__ == "__main__":
    import os

#    dlg1 = BaseDialog("Security Alert", "You are about to view pages over a secure", "OK")
#    dlg2 = BaseDialog("Security Alert", "The security certificate was issued by a company", "&Yes")

    # These dialogs object handle the dialogs that appear after Backup button is clicked
#    dlg3 = BaseDialog("File Download", "Do you want to save this file?", "&Save")
#    dlg4 = ieStandardDialog(ieStandardDialog.SAVE_AS_DLG, r"c:\mynewfile.tgz")
#    dlg5 = BaseDialog("Download complete", "", "Close")

    ### Below is an example to save generated DPSK file. ###

    # specify a custom filename
    filename = 'test-generated-dpsk.csv'
    # user's desktop location to save file in
    file_path = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % filename)
    # Remove the specified if it is exists
    if os.path.isfile(file_path):
        os.remove(file_path)

    dlg_mgr = DialogManager()

    # navigate to the Save to Disk option
    dlg1 = BaseDialog(title = None, text = "", button_name = "", key_string = "{PAUSE 3} %s {PAUSE 1} {ENTER}")
    # set the dialog title which matches this regex
    dlg1.set_title_re("Opening batch_dpsk_\d{6}_\d{2}_\d{2}.csv")

    # save as a custom filename instead of the default one
    dlg3 = StandardDialog(StandardDialog.FF_SAVE_FILE_DLG, file_path)

    # close the Downloads dialog
    dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "", key_string = "{PAUSE 3} %{F4}")

    # add the above dialogs to the dialog manager and then start it
    dlg_mgr.add_dialog(dlg1)
    dlg_mgr.add_dialog(dlg3)
    dlg_mgr.add_dialog(dlg2)
    dlg_mgr.start()

    time.sleep(30)

    dlg_mgr.shutdown()

