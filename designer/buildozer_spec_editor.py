import os
import json
import designer

from kivy.properties import ObjectProperty, ConfigParser
from kivy.uix.settings import Settings, InterfaceWithSidebar, MenuSidebar,\
    ContentPanel, SettingsPanel


class SpecContentPanel(ContentPanel):
    pass


class SpecMenuSidebar(MenuSidebar):
    pass


class SpecEditorInterface(InterfaceWithSidebar):
    pass


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

    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(BuildozerSpecEditor, self).on_config_change(*args)

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

    #TODO on write check if value is '' and not exists, so ignore
