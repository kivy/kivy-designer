import os
from functools import partial

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.properties import ObjectProperty, NumericProperty
from kivy.adapters.listadapter import ListAdapter

from designer.helper_functions import get_kivy_designer_dir

RECENT_FILES_NAME = 'recent_files'


class RecentManager(object):
    '''RecentManager is responsible for retrieving/storing the list of recently
       opened/saved projects.
    '''

    def __init__(self):
        super(RecentManager, self).__init__()
        self.list_files = []
        self.max_recent_files = 5
        self.load_files()

    def add_file(self, _file):
        '''To add file to RecentManager.
        '''

        _file_index = 0
        try:
            _file_index = self.list_files.index(_file)
        except:
            _file_index = -1

        if _file_index != -1:
            # If _file is already present in list_files, then move it to 0 index
            self.list_files.remove(_file)

        self.list_files.insert(0, _file)

        # Recent files should not be greater than max_recent_files
        while len(self.list_files) > self.max_recent_files:
            self.list_files.pop()

        self.store_files()

    def store_files(self):
        '''To store the list of files on disk.
        '''

        _string = ''
        for _file in self.list_files:
            _string += _file + '\n'

        recent_file_path = os.path.join(get_kivy_designer_dir(),
                                        RECENT_FILES_NAME)
        f = open(recent_file_path, 'w')
        f.write(_string)
        f.close()

    def load_files(self):
        '''To load the list of files from disk
        '''

        recent_file_path = os.path.join(get_kivy_designer_dir(),
                                        RECENT_FILES_NAME)

        if not os.path.exists(recent_file_path):
            return

        f = open(recent_file_path, 'r')
        _file = f.readline()

        while _file != '':
            file_path = _file.strip()
            if os.path.exists(file_path):
                self.list_files.append(file_path)

            _file = f.readline()

        f.close()


class RecentItemButton(ListItemButton):
    pass


class RecentDialog(BoxLayout):
    '''RecentDialog shows the list of recent files retrieved from RecentManager
       It emits, 'on_select' event when a file is selected and select_button is
       clicked and 'on_cancel' when cancel_button is pressed.
    '''

    listview = ObjectProperty(None)
    ''':class:`~kivy.uix.listview.ListView` used for showing file paths.
       :data:`listview` is a :class:`~kivy.properties.ObjectProperty`
    '''

    select_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` used to select the list item.
       :data:`select_button` is a :class:`~kivy.properties.ObjectProperty`
    '''

    cancel_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` to cancel the dialog.
       :data:`cancel_button` is a :class:`~kivy.properties.ObjectProperty`
    '''

    adapter = ObjectProperty(None)
    ''':class:`~kivy.uix.listview.ListAdapter` used for selecting files.
       :data:`adapter` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_select', 'on_cancel')

    def __init__(self, file_list, **kwargs):
        super(RecentDialog, self).__init__(**kwargs)
        self.item_strings = file_list
        self.list_items = RecentItemButton

        self.adapter = ListAdapter(cls=self.list_items, data=self.item_strings,
                              selection_mode='single',
                              allow_empty_selection=False)

        self.listview.adapter = self.adapter

    def get_selected_project(self, *args):
        '''
        Get the path of the selected project
        '''
        return self.adapter.selection[0].text

    def on_select_button(self, *args):
        '''Event handler for 'on_release' event of select_button.
        '''
        self.select_button.bind(on_press=partial(self.dispatch, 'on_select'))

    def on_cancel_button(self, *args):
        '''Event handler for 'on_release' event of cancel_button.
        '''
        self.cancel_button.bind(on_press=partial(self.dispatch, 'on_cancel'))

    def on_select(self, *args):
        '''Default event handler for 'on_select' event.
        '''
        pass

    def on_cancel(self, *args):
        '''Default event handler for 'on_cancel' event.
        '''
        pass
