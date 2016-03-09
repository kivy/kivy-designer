from functools import partial
from os.path import join

from designer.helper_functions import get_kd_dir
from kivy.adapters.listadapter import ListAdapter
from kivy.core.window import Keyboard, Window
from kivy.factory import Factory
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.listview import ListView


NEW_PROJECTS = {
    'FloatLayout': ('template_floatlayout_kv',
                    'template_floatlayout_py'),
    'BoxLayout': ('template_boxlayout_kv',
                  'template_boxlayout_py'),
    'ScreenManager': ('template_screen_manager_kv',
                      'template_screen_manager_py'),
    'ActionBar': ('template_actionbar_kv',
                  'template_actionbar_py'),
    'Carousel and ActionBar': ('template_actionbar_carousel_kv',
                               'template_actionbar_carousel_py'),
    'ScreenManager and ActionBar': ('template_screen_manager_actionbar_kv',
                                    'template_screen_manager_actionbar_py'),
    'TabbedPanel': ('template_tabbed_panel_kv',
                    'template_tabbed_panel_py'),
    'TextInput and ScrollView': ('template_textinput_scrollview_kv',
                                 'template_textinput_scrollview_py')}

NEW_TEMPLATES_DIR = 'new_templates'
NEW_TEMPLATE_IMAGE_PATH = join(NEW_TEMPLATES_DIR, 'images')


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
    '''Type of :class:`~kivy.uix.image.Image` to display image of selected
       new template.
       :data:`image` is a :class:`~kivy.properties.ObjectProperty`
    '''

    list_parent = ObjectProperty(None)
    '''Parent of listview.
       :data:`list_parent` is a :class:`~kivy.properties.ObjectProperty`
    '''

    prev_selection = NumericProperty(0)
    '''to memorize the previous selection.
       :attr:`prev_selection` is a :class:
       `~kivy.properties.NumericProperty`, defaults to (0).
    '''

    __events__ = ('on_select', 'on_cancel')

    def __init__(self, **kwargs):
        super(NewProjectDialog, self).__init__(**kwargs)
        item_strings = list(NEW_PROJECTS.keys())
        item_strings.sort()
        self.adapter = ListAdapter(cls=Factory.DesignerListItemButton,
                                   data=item_strings,
                                   selection_mode='single',
                                   allow_empty_selection=False)
        self.adapter.check_for_empty_selection = self.check_for_empty_selection
        self.adapter.bind(on_selection_change=self.on_adapter_selection_change)
        self.listview = ListView(adapter=self.adapter)
        self.listview.size_hint = (0.5, 1)
        self.listview.pos_hint = {'top': 1}
        self.list_parent.add_widget(self.listview, 1)
        self.on_adapter_selection_change(self.adapter)

    def on_parent(self, *args):
        if self.parent:
            Window.bind(on_key_down=self._on_keyboard_down)
        else:
            Window.unbind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, key, codepoint,
                          text, modifier, *args):
        '''To detect which key is pressed
        '''
        if modifier:
            return False
        key_str = Keyboard.keycode_to_string(Window._system_keyboard, key)
        if key_str == 'up':
            v = self.adapter.get_view(self.prev_selection - 1)
            if v is not None:
                self.adapter.handle_selection(v)
                return True
        if key_str == 'down':
            v = self.adapter.get_view(self.prev_selection + 1)
            if v is not None:
                self.adapter.handle_selection(v)
                return True
        if key_str == 'enter':
            self.dispatch('on_select')
            return True

    def check_for_empty_selection(self, *args):
        if not self.adapter.allow_empty_selection:
            if len(self.adapter.selection) == 0:
                # Select the first item if we have it.
                v = self.adapter.get_view(self.prev_selection)
                if v is not None:
                    self.adapter.handle_selection(v)

    def on_adapter_selection_change(self, adapter):
        '''Event handler for 'on_selection_change' event of adapter.
        '''
        name = adapter.selection[0].text.lower() + '.png'
        name = name.replace(' and ', '_')
        image_source = join(NEW_TEMPLATE_IMAGE_PATH, name)
        _dir = get_kd_dir()
        image_source = join(_dir, image_source)
        parent = self.image.parent
        parent.remove_widget(self.image)
        self.image = Image(source=image_source)
        parent.add_widget(self.image)
        self.prev_selection = adapter.data.index(adapter.selection[0].text)

    def on_touch_down(self, touch):
        '''Used to determine where touch is down and to detect double
           tap.
        '''
        if touch.is_double_tap:
            self.dispatch('on_select')
        return super(NewProjectDialog, self).on_touch_down(touch)

    def on_select(self, *args):
        '''Default Event Handler for 'on_select' event
        '''
        pass

    def on_cancel(self, *args):
        '''Default Event Handler for 'on_cancel' event
        '''
        pass

    def on_select_button(self, *args):
        '''Event Handler for 'on_release' of select button.
        '''
        self.select_button.bind(on_press=partial(self.dispatch, 'on_select'))

    def on_cancel_button(self, *args):
        '''Event Handler for 'on_release' of cancel button.
        '''
        self.cancel_button.bind(on_press=partial(self.dispatch, 'on_cancel'))
