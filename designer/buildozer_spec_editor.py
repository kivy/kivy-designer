import os
import json
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
import webbrowser
import designer

from kivy.properties import ObjectProperty, ConfigParser, DictProperty
from kivy.uix.settings import Settings, InterfaceWithSidebar, MenuSidebar,\
    ContentPanel, SettingsPanel, SettingOptions, SettingItem, SettingSpacer


class SpecContentPanel(ContentPanel):
    pass


class SpecMenuSidebar(MenuSidebar):
    pass


class SpecEditorInterface(InterfaceWithSidebar):

    def open_buildozer_docs(self, *args):
        webbrowser.open('http://buildozer.readthedocs.org')


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
    to [].
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
        if not value and not self.config.has_option(section, key):
            return False
        super(SpecSettingsPanel, self).set_value(section, key, value)


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
