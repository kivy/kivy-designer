import os
import shutil

from designer.utils.utils import ignore_proj_watcher
from kivy.garden.xpopup.file import XFileOpen, XFolder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


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

    lbl_error = ObjectProperty()
    '''An instance to Label to display errors.
       :data:`lbl_error` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_cancel', 'on_added', 'on_error')

    def __init__(self, project, **kwargs):
        super(AddFileDialog, self).__init__(**kwargs)
        self.project = project
        self._popup = None
        self._fbrowser = None

    def on_cancel(self):
        pass

    def on_added(self):
        pass

    def on_error(self):
        pass

    @ignore_proj_watcher
    def _perform_add_file(self):
        '''To copy file from its original path to new path
        '''

        if self.text_file.text == '':
            self.lbl_error.text = "Select the File"
            return

        target_folder = self.text_folder.text

        folder = os.path.join(self.project.path, target_folder)
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

            self.dispatch('on_added')

        except (OSError, IOError):
            self.dispatch('on_error')

    def _file_load(self, instance):
        '''To set the text of text_file, to the file selected.
        '''
        if instance.is_canceled():
            return

        self.text_file.text = instance.selection[0]

    def open_file_btn_pressed(self, *args):
        '''To load File Browser for selected file when 'Open File' is clicked
        '''

        def_path = os.path.expanduser('~')
        XFileOpen(title="Open File", on_dismiss=self._file_load, path=def_path)

    def _folder_load(self, instance):
        '''To set the text of text_folder, to the folder selected.
        '''

        if instance.is_canceled():
            return

        target_dir = os.path.relpath(instance.path, self.project.path)
        self.text_folder.text = target_dir

    def open_folder_btn_pressed(self, *args):
        '''To load File Browser for selected folder when 'Open Folder'
           is clicked
        '''

        XFolder(title="Open Folder", on_dismiss=self._folder_load,
                path=self.project.path, dirselect=True)
