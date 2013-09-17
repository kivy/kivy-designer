from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.properties import ObjectProperty
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.image import Image

import os
from functools import partial

NEW_PROJECTS = {'FloatLayout': ('template_floatlayout_kv', 'template_floatlayout_py'),
    'BoxLayout': ('template_boxlayout_kv', 'template_boxlayout_py'),
    'ScreenManager': ('template_screen_manager_kv', 'template_screen_manager_py'),
    'ActionBar': ('template_actionbar_kv', 'template_actionbar_py'),
    'Carousel and ActionBar': ('template_actionbar_carousel_kv', 'template_actionbar_carousel_py'),
    'ScreenManager and ActionBar': ('template_screen_manager_actionbar_kv', 'template_screen_manager_actionbar_py'),
    'TabbedPanel': ('template_tabbed_panel_kv', 'template_tabbed_panel_py'),
    'TextInput and ScrollView': ('template_textinput_scrollview_kv', 'template_textinput_scrollview_py')
    }

NEW_TEMPLATES_DIR = 'new_templates'
NEW_TEMPLATE_IMAGE_PATH = os.path.join(NEW_TEMPLATES_DIR, 'images')

class NewProjectDialog(BoxLayout):

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
    
    image = ObjectProperty(None)
    '''
    '''
    
    list_parent = ObjectProperty(None)
    
    __events__=('on_select', 'on_cancel')

    def __init__(self, **kwargs):
        super(NewProjectDialog, self).__init__(**kwargs)
        item_strings = NEW_PROJECTS.keys()
        self.adapter = ListAdapter(cls=ListItemButton, data=item_strings, 
                              selection_mode='single',
                              allow_empty_selection=False)
        self.adapter.bind(on_selection_change=self.on_adapter_selection_change)
        self.listview = ListView(adapter=self.adapter)
        self.listview.size_hint = (0.5, 0.5)
        self.listview.pos_hint = {'top': 1}
        self.list_parent.add_widget(self.listview, 1)
        self.on_adapter_selection_change(self.adapter)

    def on_adapter_selection_change(self, adapter):
        name = adapter.selection[0].text.lower()+'.png'
        name = name.replace(' and ', '_')
        image_source = os.path.join(NEW_TEMPLATE_IMAGE_PATH, name)
        image_source = os.path.join(os.getcwd(), image_source)
        parent = self.image.parent
        parent.remove_widget(self.image)
        self.image = Image(source=image_source)
        parent.add_widget(self.image)
    
    def on_select(self, *args):
        pass
    
    def on_cancel(self, *args):
        pass
    
    def on_select_button(self, *args):
        self.select_button.bind(on_press=partial(self.dispatch, 'on_select'))
    
    def on_cancel_button(self, *args):
        self.cancel_button.bind(on_press=partial(self.dispatch, 'on_cancel'))