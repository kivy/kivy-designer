import os
import json
import tempfile
import webbrowser
import designer

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ConfigParser, StringProperty
from kivy.uix.settings import Settings, InterfaceWithSidebar, MenuSidebar,\
    ContentPanel, SettingsPanel
from designer.uix.settings import SettingList, SettingDict

from pygments.lexers.configs import IniLexer


class SpecContentPanel(ContentPanel):

    def on_current_uid(self, *args):
        result = super(SpecContentPanel, self).on_current_uid(*args)
        if isinstance(self.current_panel, SpecCodeInput):
            self.current_panel.load_spec()
        return result


class SpecMenuSidebar(MenuSidebar):

    def on_selected_uid(self, *args):
        '''(internal) unselects any currently selected menu buttons, unless
        they represent the current panel.

        '''
        for button in self.buttons_layout.children:
            button.selected = button.uid == self.selected_uid


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


class SpecCodeInput(BoxLayout):

    text_input = ObjectProperty(None)
    '''CodeInput with buildozer.spec text.
     Instance of :class:`kivy.config.ObjectProperty` and defaults to None
    '''

    lbl_error = ObjectProperty(None)
    '''(internal) Label to display errors.
     Instance of :class:`kivy.config.ObjectProperty` and defaults to None
    '''

    spec_path = StringProperty('')
    '''buildozer.spec path.
    Instance of :class:`kivy.config.StringProperty` and defaults to ''
    '''

    __events__ = ('on_change', )

    def __init__(self, **kwargs):
        super(SpecCodeInput, self).__init__(**kwargs)
        self.text_input.lexer = IniLexer()

    def load_spec(self, *args):
        '''Read the buildozer.spec and update the CodeInput
        '''
        self.lbl_error.color = [0, 0, 0, 0]
        self.text_input.text = open(self.spec_path, 'r').read()

    def _save_spec(self, *args):
        '''Try to save the spec file. If there is a error, show the label.
        If not, save the file and dispatch on_change
        '''
        designer = App.get_running_app().root
        designer.project_watcher.stop()
        f = tempfile.NamedTemporaryFile()
        f.write(self.text_input.text)
        try:
            cfg = ConfigParser()
            cfg.read(f.name)
        except Exception:
            self.lbl_error.color = [1, 0, 0, 1]
        else:
            spec = open(self.spec_path, 'w')
            spec.write(self.text_input.text)
            spec.close()
            self.dispatch('on_change')
        f.close()
        designer.project_watcher.start_watching(
                                            designer.project_loader.proj_dir)

    def on_change(self, *args):
        '''Event handler to dispatch a .spec modification
        '''
        pass


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
        self.register_type('dict', SettingDict)
        self.register_type('list', SettingList)
        self.SPEC_PATH = ''
        self.proj_dir = ''
        self.config_parser = ConfigParser.get_configparser("buildozer_spec")
        if self.config_parser is None:
            self.config_parser = ConfigParser(name="buildozer_spec")

    def load_settings(self, proj_dir):
        '''This function loads project settings
        '''
        self.interface.menu.buttons_layout.clear_widgets()
        self.proj_dir = proj_dir
        self.SPEC_PATH = os.path.join(proj_dir, 'buildozer.spec')

        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]

        self.config_parser.read(self.SPEC_PATH)
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

        raw_spec = SpecCodeInput(spec_path=self.SPEC_PATH)
        raw_spec.bind(on_change=self.on_spec_changed)
        self.interface.add_panel(raw_spec, "buildozer.spec", raw_spec.uid)

        menu = self.interface.menu
        menu.selected_uid = menu.buttons_layout.children[-1].uid

    def on_spec_changed(self, *args):
        self.load_settings(self.proj_dir)

        # force to show the last panel
        menu = self.interface.menu
        menu.selected_uid = menu.buttons_layout.children[0].uid

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

    def on_config_change(self, *args):
        designer = App.get_running_app().root
        designer.project_watcher.stop()

        self.config_parser.write()
        super(BuildozerSpecEditor, self).on_config_change(*args)
        designer.project_watcher.start_watching(
                                            designer.project_loader.proj_dir)
