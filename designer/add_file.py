import os
import shutil

from kivy.garden.filebrowser import FileBrowser
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup


class AddFileDialog(BoxLayout):
    '''AddFileDialog is a dialog for adding files to current project. It emits
       'on_added' event if file has been added successfully, 'on_error' if
       there has been some error in adding file and 'on_cancel' when user
       wishes to cancel the operation.
    '''

    text_file = ObjectProperty()
    '''An instance to TextInput showing file path to be added.
       :data:`text_file` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text_folder = ObjectProperty()
    '''An instance to TextInput showing folder where file has to be added.
       :data:`text_folder` is a :class:`~kivy.properties.ObjectProperty`
    '''

    always_check = ObjectProperty()
    '''An instance to :class:`~kivy.uix.checkbox.CheckBox`, which will
       determine whether same folder will be used for all files of
       same type or not.
       :data:`always_check` is a :class:`~kivy.properties.ObjectProperty`
    '''

    lbl_error = ObjectProperty()
    '''An instance to Label to display errors.
       :data:`lbl_error` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_cancel', 'on_added', 'on_error')

    def __init__(self, proj_loader, **kwargs):
        super(AddFileDialog, self).__init__(**kwargs)
        self.proj_loader = proj_loader

    def on_cancel(self):
        pass

    def on_added(self):
        pass

    def on_error(self):
        pass

    def _perform_add_file(self):
        '''To copy file from its original path to new path
        '''

        if self.text_file.text == '':
            self.lbl_error.text = "Select the File"
            return

        self.proj_loader.proj_watcher.stop()

        target_folder = "" if self.text_folder.text == "." \
                                        else self.text_folder.text

        folder = os.path.join(self.proj_loader.proj_dir, target_folder)
        if not os.path.exists(folder):
            os.mkdir(folder)

        if os.path.exists(os.path.join(folder,
                                       os.path.basename(self.text_file.text))):
            self.lbl_error.text = "There is a file with the same name!"
            return

        try:
            shutil.copy(self.text_file.text,
                        os.path.join(folder,
                                     os.path.basename(self.text_file.text)))

            if self.always_check.active:
                self.proj_loader.add_dir_for_file_type(
                    self.text_file.text[self.text_file.text.rfind('.') + 1:],
                    target_folder)
            self.proj_loader.proj_watcher.start_watching(
                self.proj_loader.proj_dir)
            self.dispatch('on_added')

        except (OSError, IOError):
            self.dispatch('on_error')

    def update_from_file(self, *args):
        '''To determine the folder associated with current file type.
        '''

        curr_type = self.text_file.text
        curr_type = curr_type[curr_type.find('.') + 1:]
        if curr_type == '':
            return

        try:
            folder = self.proj_loader.dict_file_type_and_path[curr_type]
            self.text_folder.text = folder
            self.always_check.active = True

        except KeyError:
            pass

    def _cancel_popup(self, *args):
        '''To dismiss popup when cancel is pressed.
        '''

        self._popup.dismiss()

    def _file_load(self, instance):
        '''To set the text of text_file, to the file selected.
        '''

        self._popup.dismiss()
        if instance.selection != []:
            self.text_file.text = instance.selection[0]

    def open_file_btn_pressed(self, *args):
        '''To load File Browser for selected file when 'Open File' is clicked
        '''

        self._fbrowser = FileBrowser(select_string='Open')
        self._fbrowser.bind(on_success=self._file_load,
                            on_canceled=self._cancel_popup)

        self._popup = Popup(title='Open File', content=self._fbrowser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)

        self._popup.open()

    def _folder_load(self, instance):
        '''To set the text of text_folder, to the folder selected.
        '''

        if hasattr(self, '_popup'):
            self._popup.dismiss()

        if instance.ids.tabbed_browser.current_tab.text == 'List View':
            proj_dir = instance.ids.list_view.path
        else:
            proj_dir = instance.ids.icon_view.path

        proj_dir = os.path.join(proj_dir, instance.filename)

        target_dir = self.proj_loader.proj_dir

        if os.path.isdir(proj_dir):
            target_dir = os.path.relpath(proj_dir, self.proj_loader.proj_dir)
        elif os.path.isfile(proj_dir):
            proj_dir = os.path.dirname(proj_dir)
            target_dir = os.path.relpath(proj_dir, self.proj_loader.proj_dir)

        self.text_folder.text = target_dir

    def open_folder_btn_pressed(self, *args):
        '''To load File Browser for selected folder when 'Open Folder'
           is clicked
        '''

        self._fbrowser = FileBrowser(select_string='Open Folder')
        self._fbrowser.ids.list_view.path = self.proj_loader.proj_dir
        self._fbrowser.bind(on_success=self._folder_load,
                            on_canceled=self._cancel_popup)

        self._popup = Popup(title='Open Folder', content=self._fbrowser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)

        self._popup.open()
