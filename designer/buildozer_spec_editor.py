import os
import json
import re
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
import webbrowser
import designer

from kivy.properties import ObjectProperty, ConfigParser, DictProperty, \
    ListProperty, StringProperty, BooleanProperty
from kivy.uix.settings import Settings, InterfaceWithSidebar, MenuSidebar,\
    ContentPanel, SettingsPanel, SettingOptions, SettingItem, SettingSpacer


class SpecContentPanel(ContentPanel):
    pass


class SpecMenuSidebar(MenuSidebar):
    pass


class SpecEditorInterface(InterfaceWithSidebar):

    def open_buildozer_docs(self, *args):
        webbrowser.open('http://buildozer.readthedocs.org')


class SpecSettingsPanel(SettingsPanel):

    def get_value(self, section, key):
        '''Return the value of the section/key from the :attr:`config`
        ConfigParser instance. This function is used by :class:`SettingItem` to
        get the value for a given section/key.

        If you don't want to use a ConfigParser instance, you might want to
        override this function.
        '''
        config = self.config
        if not config:
            return
        if config.has_option(section, key):
            return config.get(section, key)
        else:
            return ''

    def set_value(self, section, key, value):
        # some keys are not enabled by default on .spec. If the value is empty
        # and this key is not on .spec, so we don't need to save it
        if not value and not self.config.has_option(section, key):
            return False
        super(SpecSettingsPanel, self).set_value(section, key, value)


class SpecSettingDict(SettingItem):
    '''Implementation of an option list on top of a :class:`SettingItem`.
    Based on SettingOptions, but implemented to use DictProperty.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    list of options from which the user can select.
    '''

    options = DictProperty({})
    '''Dict with keys to be saved and visible values to the user

    :attr:`options` is a :class:`~kivy.properties.DictProperty` and defaults
    to {}.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _set_option(self, instance):
        self.value = instance.key
        self.popup.dismiss()

    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        popup.height = len(self.options) * dp(55) + dp(150)

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for key in self.options:
            state = 'down' if key == self.value else 'normal'
            btn = ToggleButton(text=self.options[key], state=state, group=uid)
            btn.key = key
            btn.bind(on_release=self._set_option)
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()


class SettingListCheckItem(BoxLayout):
    '''Widget with a check button and a label to display each item of list
    '''
    item_text = StringProperty('')
    '''Item text. :attr:`item_text` is a
    :class:`~kivy.properties.ObjectProperty` and defaults to ''
    '''

    active = BooleanProperty(False)
    '''Alias to the checkbox active state.
    :attr:`checked` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False
    '''

    def __init__(self, **kwargs):
        super(SettingListCheckItem, self).__init__(**kwargs)

    def on_active(self, instance, *args):
        '''Callback to update the active value
        '''
        self.active = instance.active


class SettingListContent(BoxLayout):
    '''Widget to display SettingList
    '''
    setting = ObjectProperty(None)
    '''(internal) Reference to the setting SpecSettingList.
    :attr:`setting` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    custom_item_layout = ObjectProperty(None)
    '''(internal) Widget that allows enter a custom item to the list.
    :attr:`custom_item` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    txt_custom_item = ObjectProperty(None)
    '''(internal) TextInput with the custom item name.
    :attr:`txt_custom_item` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    item_list = ObjectProperty(None)
    '''(internal) Widget that shows all items in a list.
    :attr:`item_list` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    selected_items = ListProperty([])
    '''List of selected items names. Updated only after clicking on Apply button
    :attr:`selected_item` is a :class:`~kivy.properties.ListProperty` and
    defaults to []
    '''

    __events__ = ('on_apply', 'on_cancel', )

    def __init__(self, **kwargs):
        super(SettingListContent, self).__init__(**kwargs)
        if not self.setting.allow_custom:
            self.remove_widget(self.custom_item_layout)
        self.input_filter_pattern = re.compile(r'[^\w\s\.\-]')

    def show_items(self, *args):
        '''Update the list of items
        '''
        self.clear_items()
        self.setting.items.sort()
        for item in self.setting.items:
            i = SettingListCheckItem(item_text=item)
            if item in self.selected_items:
                i.active = True
            self.item_list.add_widget(i)

    def clear_items(self, *args):
        '''Remove all items from the item_list
        '''
        self.item_list.clear_widgets()

    def on_apply_pressed(self, *args):
        '''Event handler to Apply button.
        Get selected items and update the selected_items.
        '''
        self.update_selected_list()
        self.dispatch('on_apply', self.selected_items)

    def update_selected_list(self, *args):
        '''Update selected_items with the selected items
        '''
        self.selected_items = []
        for child in self.item_list.children:
            if child.active:
                self.selected_items.append(str(child.item_text))

    def input_filter(self, text, *args):
        '''Filter the custom item name. Replaces [^\w\s\.\-] with ''
        '''
        pattern = self.input_filter_pattern
        return re.sub(pattern, '', text)

    def add_custom_item(self, *args):
        '''Add a custom item to the list
        '''
        txt = self.txt_custom_item.text.strip()
        self.txt_custom_item.text = ''
        if txt and txt not in self.setting.items:
            self.setting.items.append(txt)
        self.update_selected_list()
        self.show_items()

    def on_cancel(self, *args):
        '''Event handler to Cancel button.
        '''
        pass

    def on_apply(self, *args):
        '''Event handler to Apply button
        '''
        pass


class SpecSettingList(SettingItem):
    '''Implementation of an multi selection list on top of :class:`SettingItem`.
    '''

    items = ListProperty([])
    '''List with default visible items
    :attr:`items` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    allow_custom = BooleanProperty(False)
    '''Allow/disallow a custom item to the list
    :attr:`allow_custom` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _create_popup(self, instance):
        # create the popup
        content = SettingListContent(setting=self)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._set_values, on_cancel=self.popup.dismiss)
        selected_items = self.value.split(',')
        # update the item list with custom values
        for item in selected_items:
            if not item in self.items:
                self.items.append(item)
        # list of items saved in the property
        content.selected_items = selected_items

        content.show_items()
        popup.open()

    def _set_values(self, *args):
        '''Read items and save them
        '''
        selected_items = args[1]
        self.value = ','.join(selected_items)
        self.popup.dismiss()


class BuildozerSpecEditor(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       the UI editor of buildozer spec
    '''

    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def __init__(self, **kwargs):
        super(BuildozerSpecEditor, self).__init__(**kwargs)
        self.register_type('dict', SpecSettingDict)
        self.register_type('list', SpecSettingList)

    def load_settings(self, proj_dir):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser(name="buildozer_spec")
        SPEC_PATH = os.path.join(proj_dir, 'buildozer.spec')

        if not os.path.isfile(SPEC_PATH):
            pass
            # TODO show an alert from helper_functions after merge first PR

        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]

        self.config_parser.read(SPEC_PATH)
        self.add_json_panel('Application', self.config_parser,
                            os.path.join(_dir, 'designer',
                            'settings', 'buildozer_spec_app.json'))
        self.add_json_panel('Android', self.config_parser,
                            os.path.join(_dir, 'designer',
                            'settings', 'buildozer_spec_android.json'))
        self.add_json_panel('iOS', self.config_parser,
                            os.path.join(_dir, 'designer',
                            'settings', 'buildozer_spec_ios.json'))
        self.add_json_panel('Buildozer', self.config_parser,
                            os.path.join(_dir, 'designer',
                            'settings', 'buildozer_spec_buildozer.json'))

    def create_json_panel(self, title, config, filename=None, data=None):
        '''Override the original method to use the custom SpecSettingsPanel
        '''
        if filename is None and data is None:
            raise Exception('You must specify either the filename or data')
        if filename is not None:
            with open(filename, 'r') as fd:
                data = json.loads(fd.read())
        else:
            data = json.loads(data)
        if type(data) != list:
            raise ValueError('The first element must be a list')
        panel = SpecSettingsPanel(title=title, settings=self, config=config)

        for setting in data:
            # determine the type and the class to use
            if not 'type' in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                str_settings[str(key)] = item

            instance = cls(panel=panel, **str_settings)

            # instance created, add to the panel
            panel.add_widget(instance)

        return panel
