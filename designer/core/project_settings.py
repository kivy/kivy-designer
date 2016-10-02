import os

from designer.utils.utils import get_kd_data_dir, ignore_proj_watcher
from kivy.config import ConfigParser
from kivy.properties import ObjectProperty
from kivy.uix.settings import Settings


PROJ_DESIGNER = '.designer'
PROJ_CONFIG = os.path.join(PROJ_DESIGNER, 'config.ini')


class ProjectSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing settings of project.
    '''

    project = ObjectProperty(None)
    '''Reference to :class:`desginer.project_manager.Project`
    '''

    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def load_proj_settings(self):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser()
        file_path = os.path.join(self.project.path, PROJ_CONFIG)
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

        settings_dir = os.path.join(get_kd_data_dir(), 'settings')
        self.add_json_panel('Shell Environment',
                            self.config_parser,
                            os.path.join(settings_dir,
                                         'proj_settings_shell_env.json'))
        self.add_json_panel('Project Properties',
                            self.config_parser,
                            os.path.join(settings_dir,
                                         'proj_settings_proj_prop.json'))

    @ignore_proj_watcher
    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(ProjectSettings, self).on_config_change(*args)
