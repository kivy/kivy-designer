import os
import os.path
import shutil
import sys
import designer

from distutils.spawn import find_executable
from pygments import styles

from kivy.properties import ObjectProperty
from kivy.config import ConfigParser
from kivy.uix.settings import Settings

from designer.helper_functions import get_kivy_designer_dir
from designer.uix.settings import SettingList

DESIGNER_CONFIG_FILE_NAME = 'config.ini'


# monkey backport! (https://github.com/kivy/kivy/pull/2288)
if not hasattr(ConfigParser, 'upgrade'):
    try:
        from ConfigParser import ConfigParser as PythonConfigParser
    except ImportError:
        from configparser import RawConfigParser as PythonConfigParser

    def upgrade(self, default_config_file):
        '''Upgrade the configuration based on a new default config file.
        '''
        pcp = PythonConfigParser()
        pcp.read(default_config_file)
        for section in pcp.sections():
            self.setdefaults(section, dict(pcp.items(section)))
        self.write()

    ConfigParser.upgrade = upgrade


class DesignerSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing settings of Kivy Designer.
    '''

    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def __init__(self, **kwargs):
        super(DesignerSettings, self).__init__(*kwargs)
        self.register_type('list', SettingList)

    def load_settings(self):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser(name='DesignerSettings')
        DESIGNER_CONFIG = os.path.join(get_kivy_designer_dir(),
                                       DESIGNER_CONFIG_FILE_NAME)

        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]

        DEFAULT_CONFIG = os.path.join(_dir, DESIGNER_CONFIG_FILE_NAME)
        if not os.path.exists(DESIGNER_CONFIG):
            shutil.copyfile(DEFAULT_CONFIG,
                            DESIGNER_CONFIG)

        self.config_parser.read(DESIGNER_CONFIG)
        self.config_parser.upgrade(DEFAULT_CONFIG)

        # creates a panel before insert it to update code input theme list
        panel = self.create_json_panel('Kivy Designer Settings',
                                        self.config_parser,
                            os.path.join(_dir, 'designer',
                                         'settings', 'designer_settings.json'))
        uid = panel.uid
        if self.interface is not None:
            self.interface.add_panel(panel, 'Kivy Designer Settings', uid)

        # loads available themes
        for child in panel.children:
            if child.id == 'code_input_theme_options':
                child.items = styles.get_all_styles()

        # tries to find python and buildozer path if it's not defined
        path = self.config_parser.getdefault(
            'global', 'python_shell_path', '')

        if path.strip() == '':
            self.config_parser.set('global', 'python_shell_path',
                                   sys.executable)
            self.config_parser.write()

        buildozer_path = self.config_parser.getdefault('buildozer',
                                                       'buildozer_path', '')

        if buildozer_path.strip() == '':
            buildozer_path = find_executable('buildozer')
            if buildozer_path:
                self.config_parser.set('buildozer',
                                       'buildozer_path',
                                        buildozer_path)
                self.config_parser.write()

        self.add_json_panel('Buildozer', self.config_parser,
                            os.path.join(_dir, 'designer', 'settings',
                                         'buildozer_settings.json'))
        self.add_json_panel('Hanga', self.config_parser,
                            os.path.join(_dir, 'designer', 'settings',
                                         'hanga_settings.json'))

    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(DesignerSettings, self).on_config_change(*args)
