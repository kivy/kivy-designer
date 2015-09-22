import threading
from git.exc import InvalidGitRepositoryError
from kivy._event import EventDispatcher
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty, \
    Clock, ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import os
from pygments.lexers.diff import DiffLexer
import designer
from designer.designer_content import DesignerTabbedPanelItem
from designer.helper_functions import ignore_proj_watcher, show_alert, \
    show_message, get_designer
from designer.input_dialog import InputDialog
from designer.uix.designer_action_items import DesignerActionSubMenu, \
        DesignerSubActionButton
from git import Repo, RemoteProgress, GitCommandError
from designer.uix.py_code_input import PyScrollView
from designer.uix.settings import SettingListContent
from kivy.app import App
import subprocess


class FakeSettingList(EventDispatcher):
    '''Fake Kivy Setting to use SettingList
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

    group = StringProperty(None)
    '''CheckBox group name. If the CheckBox is in a Group,
    it becomes a Radio button.
    :attr:`group` is a :class:`~kivy.properties.StringProperty` and
    defaults to ''
    '''

    desc = StringProperty(None, allownone=True)
    '''Description of the setting, rendered on the line below the title.

    :attr:`desc` is a :class:`~kivy.properties.StringProperty` and defaults to
    None.
    '''


class GitRemoteProgress(RemoteProgress):

    label = None
    text = ''

    def __init__(self):
        super(GitRemoteProgress, self).__init__()
        self.label = Label(text='')
        self.label.padding = [10, 10]

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.text = 'Progress: %.2f (%d of %d)\n%s' % (
            cur_count / (max_count or 100.0),
            cur_count,
            (max_count or 100),
            message.replace(',', '').strip()
        )

    def update_text(self, *args):
        '''Update the label text
        '''
        if self.text:
            self.label.text = self.text

    def start(self):
        '''Start the label updating in a separated thread
        '''
        Clock.schedule_interval(self.update_text, 0.2)

    def stop(self):
        '''Start the label updating in a separated thread
        '''
        Clock.unschedule(self.update_text)


class DesignerGit(DesignerActionSubMenu):

    is_repo = BooleanProperty(False)
    '''Indicates if it's representing a valid git repository
    :data:`is_repo` is a :class:`~kivy.properties.BooleanProperty`, defaults
       to False.
    '''

    path = StringProperty('')
    '''Project path
        :data:`path` is a :class:`~kivy.properties.StringProperty`,
        defaults to ''.
    '''

    repo = ObjectProperty(None)
    '''Instance of Git repository.
        :data:`repo` is a :class:`~kivy.properties.ObjectProperty`, defaults
       to None.
    '''

    diff_code_input = ObjectProperty(None)
    '''Instance of PyCodeInput with Git diff
    :data:`diff_code_input` is a :class:`~kivy.properties.ObjectProperty`,
        defaults to None.
    '''

    def __init__(self, **kwargs):
        super(DesignerGit, self).__init__(**kwargs)
        self._update_menu()

    def load_repo(self, path):
        '''Load a git/non-git repo from path
        '''
        self.path = path
        try:
            self.repo = Repo(path)
            self.is_repo = True

            _dir = os.path.dirname(designer.__file__)
            _dir = os.path.split(_dir)[0]
            if os.name == 'posix':
                script = os.path.join(_dir, 'tools', 'ssh-agent', 'ssh.sh')
                self.repo.git.update_environment(GIT_SSH_COMMAND=script)
        except InvalidGitRepositoryError:
            self.is_repo = False
        self._update_menu()

    def _update_menu(self, *args):
        '''Update the Git ActionSubMenu content.
        If a valid repo is open, git tools will be available.
        Is not a git repo, git init is available.
        '''
        self.remove_children()
        designer = App.get_running_app().root
        loader = None
        if designer:
            loader = designer.project_watcher._project_dir

        if loader:
            self.disabled = False
            if self.is_repo:
                btn_commit = DesignerSubActionButton(text='Commit')
                btn_commit.bind(on_press=self.do_commit)

                btn_add = DesignerSubActionButton(text='Add...')
                btn_add.bind(on_press=self.do_add)

                btn_branches = DesignerSubActionButton(text='Branches...')
                btn_branches.bind(on_press=self.do_branches)

                btn_diff = DesignerSubActionButton(text='Diff')
                btn_diff.bind(on_press=self.do_diff)

                btn_push = DesignerSubActionButton(text='Push')
                btn_push.bind(on_press=self.do_push)

                btn_pull = DesignerSubActionButton(text='Pull')
                btn_pull.bind(on_press=self.do_pull)

                self.add_widget(btn_commit)
                self.add_widget(btn_add)
                self.add_widget(btn_branches)
                self.add_widget(btn_diff)
                self.add_widget(btn_push)
                self.add_widget(btn_pull)
            else:
                btn_init = DesignerSubActionButton(text='Init repo')
                btn_init.bind(on_press=self.do_init)
                self.add_widget(btn_init)
            self._add_widget()
        else:
            self.disabled = True

    def validate_remote(self):
        '''Validates Git remote auth. If system if posix, returns True.
        If on NT, reads tools/ssh-agent/ssh_status.txt, if equals 1,
        returns True else runs the tools/ssh-agent/ssh.bat and returns False
        '''
        if os.name == 'nt':
            _dir = os.path.dirname(designer.__file__)
            _dir = os.path.split(_dir)[0]
            script = os.path.join(_dir, 'tools', 'ssh-agent', 'ssh.bat')
            status_txt = os.path.join(_dir, 'tools', 'ssh-agent',
                                                        'ssh_status.txt')
            status = open(status_txt, 'r').read()
            status = status.strip()
            if status == '1':
                return True
            else:
                subprocess.call(script, shell=True)
                return False
        else:
            return True

    @ignore_proj_watcher
    def do_init(self, *args):
        '''Git init
        '''
        try:
            self.repo = Repo.init(self.path, mkdir=False)
            self.repo.index.commit('Init commit')
            self.is_repo = True
            self._update_menu()
            show_message('Git repo initialized', 5)
        except:
            show_alert('Git Init', 'Failted to initialize repo!')

    def do_commit(self, *args):
        '''Git commit
        '''
        input = InputDialog('Commit message: ')
        self._popup = Popup(title='Git Commit', content=input,
                            size_hint=(None, None), size=('300pt', '150pt'),
                            auto_dismiss=False)
        input.bind(on_confirm=self._perform_do_commit,
                   on_cancel=self._popup.dismiss)
        self._popup.open()

    @ignore_proj_watcher
    def _perform_do_commit(self, input, *args):
        '''Perform the git commit with data from InputDialog
        '''
        message = input.get_user_input()
        if self.repo.is_dirty():
            try:
                self.repo.git.commit('-am', message)
                show_message('Commit: ' + message, 5)
            except GitCommandError as e:
                show_alert('Git Commit', 'Failed to commit!\n' + str(e))
        else:
            show_alert('Git Commit', 'There is nothing to commit')
        self._popup.dismiss()

    @ignore_proj_watcher
    def do_add(self, *args):
        '''Git select files from a list to add
        '''
        files = self.repo.untracked_files
        if not files:
            show_alert('Git Add', 'All files are already indexed by Git')
            return

        # create the popup
        fake_setting = FakeSettingList()
        fake_setting.allow_custom = False
        fake_setting.items = files
        fake_setting.desc = 'Select files to add to Git index'

        content = SettingListContent(setting=fake_setting)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self._popup = popup = Popup(
            content=content, title='Git - Add files', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_add,
                     on_cancel=self._popup.dismiss)

        content.show_items()
        popup.open()

    @ignore_proj_watcher
    def _perform_do_add(self, instance, selected_files, *args):
        '''Add the selected files to git index
        '''
        try:
            self.repo.index.add(selected_files)
            show_message('%d file(s) added to Git index' %
                         len(selected_files), 5)
            self._popup.dismiss()
        except GitCommandError as e:
            show_alert('Git Add', 'Failed to add files to Git!\n' + str(e))

    def do_branches(self, *args):
        '''Shows a list of git branches and allow to change the current one
        '''
        branches = []
        for b in self.repo.heads:
            branches.append(b.name)

        # create the popup
        fake_setting = FakeSettingList()
        fake_setting.allow_custom = True
        fake_setting.items = branches
        fake_setting.desc = 'Checkout to the selected branch. \n' \
                'You can type a name to create a new branch'
        fake_setting.group = 'git_branch'

        content = SettingListContent(setting=fake_setting)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self._popup = popup = Popup(
            content=content, title='Git - Branches', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_branches,
                     on_cancel=self._popup.dismiss)

        content.selected_items = [self.repo.active_branch.name]
        content.show_items()

        popup.open()

    @ignore_proj_watcher
    def _perform_do_branches(self, instance, branches, *args):
        '''If the branch name exists, try to checkout. If a new name, create
        the branch and checkout.
        If the code has modification, shows an alert and stops
        '''
        self._popup.dismiss()

        if self.repo.is_dirty():
            show_alert('Git checkout', 'Please, commit your changes before '
                                                    + 'switch branches.')
            return

        if not branches:
            return

        branch = branches[0]
        try:
            if branch in self.repo.heads:
                self.repo.heads[branch].checkout()
            else:
                self.repo.create_head(branch)
                self.repo.heads[branch].checkout()
        except GitCommandError as e:
            show_alert('Git Branches', 'Failed to switch branch!\n' + str(e))

    def do_diff(self, *args):
        '''Open a CodeInput with git diff
        '''
        diff = self.repo.git.diff()

        designer = get_designer()
        designer_content = designer.designer_content
        tabs = designer_content.tab_pannel

        # check if diff is visible on tabbed panel.
        # if so, update the text content
        for i, code_input in enumerate(tabs.list_py_code_inputs):
            if code_input == self.diff_code_input:
                tabs.switch_to(tabs.tab_list[len(tabs.tab_list) - i - 2])
                code_input.text = diff
                return

        # if not displayed, create or add it to the screen
        if self.diff_code_input is None:
            panel_item = DesignerTabbedPanelItem(text='Git diff')
            scroll = PyScrollView()
            _py_code_input = scroll.code_input
            _py_code_input.rel_file_path = 'designer.DesigerGit.diff_code_input'
            _py_code_input.text = diff
            _py_code_input.readonly = True
            _py_code_input.lexer = DiffLexer()
            tabs.list_py_code_inputs.append(_py_code_input)
            panel_item.content = scroll
            self.diff_code_input = panel_item
        else:
            self.diff_code_input.content.code_input.text = diff
        tabs.add_widget(self.diff_code_input)
        tabs.switch_to(tabs.tab_list[0])

    def do_push(self, *args):
        '''Open a list of remotes to push repository data.
        If there is not remote, shows an alert
        '''
        if not self.validate_remote():
            show_alert('Git - Remote Authentication',
                'To use Git remote you need to enter your ssh password')
            return
        remotes = []
        for r in self.repo.remotes:
            remotes.append(r.name)
        if not remotes:
            show_alert('Git Push Remote', 'There is no git remote configured!')
            return

        # create the popup
        fake_setting = FakeSettingList()
        fake_setting.allow_custom = False
        fake_setting.items = remotes
        fake_setting.desc = 'Push data to the selected remote'
        fake_setting.group = 'git_remote'

        content = SettingListContent(setting=fake_setting)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self._popup = popup = Popup(
            content=content, title='Git - Push Remote', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_push,
                     on_cancel=self._popup.dismiss)

        content.selected_items = [remotes[0]]
        content.show_items()

        popup.open()

    def _perform_do_push(self, instance, remotes, *args):
        '''Try to perform a push
        '''
        remote = remotes[0]
        remote_repo = self.repo.remotes[remote]
        progress = GitRemoteProgress()

        status = Popup(title='Git push progress',
                            content=progress.label,
                            size_hint=(None, None),
                            size=(500, 200))
        status.open()

        @ignore_proj_watcher
        def push(*args):
            '''Do a push in a separated thread
            '''
            try:
                remote_repo.push(self.repo.active_branch.name,
                                 progress=progress)

                def set_progress_done(*args):
                    progress.label.text = 'Completed!'

                Clock.schedule_once(set_progress_done, 1)
                progress.stop()
                show_message('Git remote push completed!', 5)
            except GitCommandError as e:
                progress.label.text = 'Failed to push!\n' + str(e)
            self._popup.dismiss()

        progress.start()
        threading.Thread(target=push).start()

    def do_pull(self, *args):
        '''Open a list of remotes to pull remote data.
        If there is not remote, shows an alert
        '''
        if not self.validate_remote():
            show_alert('Git - Remote Authentication',
                'To use Git remote you need to enter your ssh password')
            return
        remotes = []
        for r in self.repo.remotes:
            remotes.append(r.name)
        if not remotes:
            show_alert('Git Pull Remote', 'There is no git remote configured!')
            return

        # create the popup
        fake_setting = FakeSettingList()
        fake_setting.allow_custom = False
        fake_setting.items = remotes
        fake_setting.desc = 'Pull data from the selected remote'
        fake_setting.group = 'git_remote'

        content = SettingListContent(setting=fake_setting)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self._popup = popup = Popup(
            content=content, title='Git - Pull Remote', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_pull,
                     on_cancel=self._popup.dismiss)

        content.selected_items = [remotes[0]]
        content.show_items()

        popup.open()

    def _perform_do_pull(self, instance, remotes, *args):
        '''Try to perform a pull
        '''
        remote = remotes[0]
        remote_repo = self.repo.remotes[remote]
        progress = GitRemoteProgress()

        status = Popup(title='Git pull progress',
                            content=progress.label,
                            size_hint=(None, None),
                            size=(500, 200))
        status.open()

        @ignore_proj_watcher
        def pull(*args):
            '''Do a pull in a separated thread
            '''
            try:
                remote_repo.pull(progress=progress)

                def set_progress_done(*args):
                    progress.label.text = 'Completed!'

                Clock.schedule_once(set_progress_done, 1)
                progress.stop()
                show_message('Git remote pull completed!', 5)
            except GitCommandError as e:
                progress.label.text = 'Failed to pull!\n' + str(e)
            self._popup.dismiss()

        progress.start()
        threading.Thread(target=pull).start()
