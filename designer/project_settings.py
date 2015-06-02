import os
import designer

from kivy.properties import ObjectProperty
from kivy.config import ConfigParser
from kivy.uix.settings import Settings, SettingTitle
from kivy.uix.label import Label
from kivy.uix.button import Button

PROJ_DESIGNER = '.designer'
PROJ_CONFIG = os.path.join(PROJ_DESIGNER, 'config.ini')


class ProjectSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing settings of project.
    '''

    proj_loader = ObjectProperty(None)
    '''Reference to :class:`desginer.project_loader.ProjectLoader`
    '''

    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def load_proj_settings(self):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser()
        file_path = os.path.join(self.proj_loader.proj_dir, PROJ_CONFIG)
        if not os.path.exists(file_path):
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            CONFIG_TEMPLATE = '''[proj_name]
name = Project

[arguments]
arg =

[env variables]
env =
'''
            f = open(file_path, 'w')
            f.write(CONFIG_TEMPLATE)
            f.close()

        self.config_parser.read(file_path)
        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]
        settings_dir = os.path.join(_dir, 'designer', 'settings')
        self.add_json_panel('Shell Environment',
                            self.config_parser,
                            os.path.join(settings_dir,
                                         'proj_settings_shell_env.json'))
        self.add_json_panel('Project Properties',
                            self.config_parser,
                            os.path.join(settings_dir,
                                         'proj_settings_proj_prop.json'))

    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(ProjectSettings, self).on_config_change(*args)
