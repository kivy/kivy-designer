import os
import shutil

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty, \
    ConfigParser, ConfigParserProperty, partial, Clock
from kivy.uix.popup import Popup
import designer
from designer.confirmation_dialog import ConfirmationDialog


class Builder(EventDispatcher):
    '''Builder interface
    '''

    def __init__(self, profiler):
        self.profiler = profiler
        self.designer = self.profiler.designer
        self.designer_settings = self.designer.designer_settings
        self.proj_watcher = self.designer.project_watcher
        self.proj_settings = self.designer.proj_settings
        self.ui_creator = self.designer.ui_creator
        self.run_command = self.ui_creator.kivy_console.run_command
        self.can_run = False  # if the env if ok to run the project
        self.last_command = None  # last method executed.
        if not self.profiler.pro_mode:
            self.profiler.pro_mode = 'Debug'


class Buildozer(Builder):
    '''Class to handle Buildozer builder
    '''

    def __init__(self, profiler):
        super(Buildozer, self).__init__(profiler)
        self.buildozer_path = ''

    def _initialize(self):
        '''Try to get the buildozer path and check required variables
        If there is something wrong shows an alert.
        '''

        # first, check if buildozer is set
        self.buildozer_path = self.designer_settings.config_parser.getdefault(
            'buildozer',
            'buildozer_path',
            ''
        )

        if self.buildozer_path == '':
            self.profiler.dispatch('on_error', 'Buildozer Path not specified.'
                                '\n\nUpdate it on \'File\' -> \'Settings\'')
            self.can_run = False
            return

        envs = self.proj_settings.config_parser.getdefault(
            'env variables',
            'env',
            ''
        )

        for env in envs.split(' '):
            self.ui_creator.kivy_console.environment[
                env[:env.find('=')]] = env[env.find('=') + 1:]

        # check if buildozer.spec exists
        if not os.path.isfile(os.path.join(self.profiler.project_path,
                                           'buildozer.spec')):
            self._confirm_dlg = ConfirmationDialog(
                message='buildozer.spec not found.\n'
                            'Do you want to create it now?')
            self._popup = Popup(title='Buildozer', content=self._confirm_dlg,
                                size_hint=(None, None), size=('200pt', '150pt'),
                                auto_dismiss=False)
            self._confirm_dlg.bind(on_ok=self._perform_create_spec,
                                   on_cancel=self._popup.dismiss)
            self._popup.open()
            self.can_run = False
            return

        # TODO check if buildozer source.dir and main file exists

        self.can_run = True

    def _perform_create_spec(self, *args):
        '''Creates the default buildozer.spec file
        '''
        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]
        templates_dir = os.path.join(_dir, 'new_templates')
        shutil.copy(os.path.join(templates_dir, 'default.spec'),
                    os.path.join(self.profiler.project_path, 'buildozer.spec'))

        self.designer.designer_content.update_tree_view(
            self.designer.project_loader)
        self._popup.dismiss()
        self.last_command()

    def _create_command(self, extra):
        '''Generate the buildozer command
        '''
        self.proj_watcher.stop()
        self._initialize()
        self.ui_creator.tab_pannel.switch_to(
            self.ui_creator.tab_pannel.tab_list[2])

        cd = 'cd ' + self.profiler.project_path
        args = []
        args.append(self.buildozer_path)
        if self.profiler.pro_verbose:
            args.append('--verbose')
        args.append(self.profiler.pro_target.lower())  # android or ios
        args += extra

        return [cd, " ".join(args)]

    def build(self, *args):
        '''Build the Buildozer project.
        Will read the necessary information from the profile and build the app
        '''
        build_mode = self.profiler.pro_mode.lower()
        cmd = self._create_command([build_mode])
        if not self.can_run:
            self.last_command = self.build
            return
        self.run_command(cmd)

        self.profiler.dispatch('on_message', 'Building project...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_build)

    def rebuild(self, *args):
        '''Update project dependencies, and build it again
        '''
        self.clean()
        self.profiler.bind(on_clean=self._rebuild)

    def _rebuild(self, *args):
        '''Perform the project rebuild
        '''
        cmd = self._create_command(['update'])
        if not self.can_run:
            self.last_command = self.rebuild
            return
        self.run_command(cmd)

        self.profiler.dispatch('on_message',
                               'Updating project dependencies...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.build)

    def run(self, *args, **kwargs):
        '''Run the build command and then run the application on the device
        '''
        self.build()
        if not self.can_run:
            self.last_command = self.run
            return
        if not self.profiler.pro_install:
            self.profiler.bind(on_build=self.deploy)
        self.profiler.bind(on_deploy=self._run)

    def _run(self, *args):
        '''Perform the buildozer run
        '''
        cmds = ['run']
        if self.profiler.pro_debug and self.profiler.pro_target == 'Android':
            cmds.append('logcat')
        cmd = self._create_command(cmds)
        if not self.can_run:
            return
        self.run_command(cmd)

        self.profiler.dispatch('on_message', 'Running on device...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_run)

    def deploy(self, *args):
        '''Perform the buildozer deploy
        '''
        cmd = self._create_command(['deploy'])
        if not self.can_run:
            return
        self.run_command(cmd)

        self.profiler.dispatch('on_message', 'Installing on device...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_deploy)

    def clean(self, *args):
        '''Clean the project directory
        '''
        cmd = self._create_command(['clean'])
        if not self.can_run:
            self.last_command = self.clean
            return
        self.run_command(cmd)

        self.profiler.dispatch('on_message', 'Cleaning project...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_clean)

    def on_clean(self, *args):
        '''on_clean event handler
        '''
        self.ui_creator.kivy_console.unbind(on_command_list_done=self.on_clean)

        self.proj_watcher.start_watching(self.profiler.project_path)

        self.profiler.dispatch('on_message', 'Project clean', 5)
        self.profiler.dispatch('on_clean')

    def on_build(self, *args):
        '''on_build event handler
        '''
        self.ui_creator.kivy_console.unbind(on_command_list_done=self.on_build)

        self.proj_watcher.start_watching(self.profiler.project_path)

        self.profiler.dispatch('on_message', 'Build complete', 5)
        self.profiler.dispatch('on_build')

        if self.profiler.pro_install:
            self.deploy()

    def on_deploy(self, *args):
        '''on_build event handler
        '''
        self.ui_creator.kivy_console.unbind(on_command_list_done=self.on_deploy)

        self.proj_watcher.start_watching(self.profiler.project_path)

        self.profiler.dispatch('on_message', 'Installed on device', 5)
        self.profiler.dispatch('on_deploy')

    def on_stop(self, *args):
        '''on_stop event handler
        '''
        self.ui_creator.kivy_console.unbind(on_command_list_done=self.on_stop)

        self.profiler.dispatch('on_stop')

    def on_run(self, *args):
        '''on_run event handler
        '''
        self.ui_creator.kivy_console.unbind(on_command_list_done=self.on_run)

        self.proj_watcher.start_watching(self.profiler.project_path)

        self.profiler.dispatch('on_message', '', 1)
        self.profiler.dispatch('on_run')
        self.designer.ids.actn_btn_stop_proj.disabled = True


class Hanga(Builder):
    '''Class to handle Hanga builder
    '''

    def __init__(self, profiler):
        super(Hanga, self).__init__(profiler)


class Desktop(Builder):
    '''Class to handle Desktop builder
    '''

    def __init__(self, profiler):
        super(Desktop, self).__init__(profiler)
        self.python_path = ''
        self.args = ''
        # TODO check if buildozer source.dir and main file is set, if so
        # use this file

    def _get_python(self):
        '''Initialize python variables
        If there is something wrong shows an alert
        '''
        self.python_path = self.designer_settings.config_parser.getdefault(
            'global',
            'python_shell_path',
            ''
        )

        if self.python_path == '':
            self.profiler.dispatch('on_error', 'Python Shell Path not '
                                   'specified.'
                                   '\n\nUpdate it on \'File\' -> \'Settings\'')
            self.can_run = False
            return

        self.args = self.proj_settings.config_parser.getdefault(
            'arguments',
            'arg',
            ''
        )

        envs = self.proj_settings.config_parser.getdefault(
            'env variables',
            'env',
            ''
        )

        for env in envs.split(' '):
            self.ui_creator.kivy_console.environment[
                env[:env.find('=')]] = env[env.find('=') + 1:]

        self.can_run = True

    def _perform_kill_run(self, *args):
        '''Stop the running project/command and then run the project
        '''
        self._popup.dismiss()
        self.stop()
        Clock.schedule_once(self.run)

    def run(self, *args, **kwargs):
        '''Run the project using Python
        '''
        mod = kwargs.get('mod', '')
        data = kwargs.get('data', [])

        self._get_python()
        if not self.can_run:
            return

        py_main = os.path.join(self.profiler.project_path, 'main.py')

        if not os.path.isfile(py_main):
            self.profiler.dispatch('on_error', 'Cannot find main.py')
            return

        cmd = ''
        if mod == '':
            cmd = '%s %s %s' % (self.python_path, py_main, self.args)
        elif mod == 'screen':
            cmd = '%s %s -m screen:%s %s' % (self.python_path, py_main,
                                             data, self.args)
        else:
            cmd = '%s %s -m %s %s' % (self.python_path, py_main,
                                      mod, self.args)

        status = self.run_command(cmd)

        # popen busy
        if status is False:
            self._confirm_dlg = ConfirmationDialog(
                message="There is another command running.\n"
                        "Do you want to stop it to run your project?")
            self._popup = Popup(title='Kivy Designer',
                                content=self._confirm_dlg,
                                size_hint=(None, None),
                                size=('300pt', '150pt'),
                                auto_dismiss=False)
            self._confirm_dlg.bind(on_ok=self._perform_kill_run,
                                   on_cancel=self._popup.dismiss)
            self._popup.open()
            return

        self.ui_creator.tab_pannel.switch_to(
            self.ui_creator.tab_pannel.tab_list[2])

        self.profiler.dispatch('on_message', 'Running main.py...')
        self.profiler.dispatch('on_run')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_stop)

    def stop(self, *args):
        '''If there is a process running, it'll be stopped
        '''
        self.ui_creator.kivy_console.kill_process()
        self.profiler.dispatch('on_stop')
        self.profiler.dispatch('on_message', '', 1)

    def clean(self, *args):
        '''Remove .pyc files and __pycache__ folder
        '''
        # here it's necessary to stop the listener as long as the
        # python is managing files
        self.proj_watcher.stop()
        for _file in os.listdir(self.profiler.project_path):
            ext = _file.split('.')[-1]
            if ext == 'pyc':
                os.remove(os.path.join(self.profiler.project_path, _file))
        __pycache__ = os.path.join(self.profiler.project_path, '__pycache__')
        if os.path.exists(__pycache__):
            shutil.rmtree(__pycache__)

        self.proj_watcher.start_watching(self.profiler.project_path)
        self.profiler.dispatch('on_message', 'Project cleaned', 5)

    def build(self, *args):
        '''Compile all .py to .pyc
        '''
        self._get_python()
        if not self.can_run:
            return

        self.proj_watcher.stop()
        proj_path = self.profiler.project_path

        self.run_command(
                    '%s -m compileall -l %s' % (self.python_path, proj_path))

        self.ui_creator.tab_pannel.switch_to(
            self.ui_creator.tab_pannel.tab_list[2])

        self.profiler.dispatch('on_message', 'Building project...')
        self.ui_creator.kivy_console.bind(on_command_list_done=self.on_build)

    def rebuild(self, *args):
        '''Clean and build the project
        '''
        self.clean()
        self.build()

    def on_build(self, *args):
        '''on_build event handler
        '''
        self.proj_watcher.start_watching(self.profiler.project_path)
        self.profiler.dispatch('on_message', 'Build complete', 5)
        self.profiler.dispatch('on_build')

    def on_stop(self, *args):
        '''on_stop event handler
        '''
        self.profiler.dispatch('on_message', '', 1)
        self.profiler.dispatch('on_stop')


class Profiler(EventDispatcher):
    profile_path = StringProperty('')
    ''' Profile settings path
    :class:`~kivy.properties.StringProperty` and defaults to ''.
    '''

    project_path = StringProperty('')
    ''' Project path
    :class:`~kivy.properties.StringProperty` and defaults to ''.
    '''

    designer = ObjectProperty(None)
    '''Reference of :class:`~designer.app.Designer`.
       :data:`designer` is a :class:`~kivy.properties.ObjectProperty`
    '''

    profile_config = ObjectProperty(None)
    '''Reference to a ConfigParser with the profile settings
    :class:`~kivy.properties.ObjectProperty` and defaults to None.
    '''

    pro_name = ConfigParserProperty('', 'profile', 'name', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile name
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_builder = ConfigParserProperty('', 'profile', 'builder', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile builder
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_target = ConfigParserProperty('', 'profile', 'target', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile target
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_mode = ConfigParserProperty('', 'profile', 'mode', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile builder
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_install = ConfigParserProperty('', 'profile', 'install', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile install_on_device
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_debug = ConfigParserProperty('', 'profile', 'debug', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile debug mode
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    pro_verbose = ConfigParserProperty('', 'profile', 'verbose', 'profiler')
    '''Reference to a ConfigParser with the profile settings
    Get the profile verbose mode
    :class:`~kivy.properties.ConfigParserProperty`
    '''

    builder = ObjectProperty(None)
    '''Reference to the builder class. Can be Hanga, Buildozer or Desktop
    :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_run', 'on_stop', 'on_error', 'on_message', 'on_build',
                  'on_deploy', 'on_clean')

    def __init__(self, **kwargs):
        super(Profiler, self).__init__(**kwargs)
        self.profile_config = ConfigParser(name='profiler')

    def run(self, *args, **kwargs):
        '''Run project
        '''
        self.builder.run(*args, **kwargs)

    def stop(self):
        '''Stop project
        '''
        self.builder.stop()

    def clean(self):
        '''Clean project
        '''
        self.builder.clean()

    def build(self):
        '''Build project
        '''
        self.builder.build()

    def rebuild(self):
        '''Rebuild project
        '''
        self.builder.rebuild()

    def load_profile(self, prof_path, proj_path):
        '''Read the settings
        '''
        self.profile_path = prof_path
        self.project_path = proj_path

        self.profile_config.read(self.profile_path)

        if self.pro_target == 'Desktop':
            self.builder = Desktop(self)
        else:
            if self.pro_builder == 'Buildozer':
                self.builder = Buildozer(self)
            elif self.pro_builder == 'Hanga':
                # TODO implement hanga
                self.builder = Desktop(self)
                self.dispatch('on_error', 'Hanga Builder not yet implemented!\n'
                              'Using Desktop')
            else:
                self.builder = Desktop(self)

    def on_error(self, *args):
        '''on_error event handler
        '''
        pass

    def on_message(self, *args):
        '''on_message event handler
        '''
        pass

    def on_run(self, *args):
        '''on_run event handler
        '''
        pass

    def on_stop(self, *args):
        '''on_stop event handler
        '''
        pass

    def on_build(self, *args):
        '''on_build event handler
        '''
        pass

    def on_deploy(self, *args):
        '''on_deploy event handler
        '''
        pass

    def on_clean(self, *args):
        '''on_clean event handler
        '''
        pass
