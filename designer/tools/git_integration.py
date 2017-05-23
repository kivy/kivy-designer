import os
import subprocess
import threading
from io import open

from designer.components.designer_content import DesignerCloseableTab
from designer.uix.action_items import (
    DesignerActionSubMenu,
    DesignerSubActionButton,
)
from designer.uix.input_dialog import InputDialog
from designer.uix.py_code_input import PyScrollView
from designer.uix.settings import SettingListContent
from designer.utils.utils import (
    FakeSettingList,
    get_current_project,
    get_designer,
    get_kd_dir,
    ignore_proj_watcher,
    show_alert,
    show_message,
)
from git import GitCommandError, RemoteProgress, Repo
from git.exc import InvalidGitRepositoryError
from kivy.core.window import Window
from kivy.properties import (
    BooleanProperty,
    Clock,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from pygments.lexers.diff import DiffLexer


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

    __events__ = ('on_branch', )

    def __init__(self, **kwargs):
        super(DesignerGit, self).__init__(**kwargs)
        self._update_menu()

    def load_repo(self, path):
        '''Load a git/non-git repo from path
        :param path: project path
        '''
        self.path = path
        try:
            self.repo = Repo(path)
            self.is_repo = True
            branch_name = self.repo.active_branch.name
            self.dispatch('on_branch', branch_name)

            if os.name == 'posix':
                script = os.path.join(get_kd_dir(),
                                      'tools', 'ssh-agent', 'ssh.sh')
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
        d = get_designer()
        loader = None
        if d:
            loader = get_current_project().path

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
            script = os.path.join(get_kd_dir(), 'tools', 'ssh-agent', 'ssh.bat')
            status_txt = os.path.join(get_kd_dir(), 'tools', 'ssh-agent',
                                      'ssh_status.txt')
            status = open(status_txt, 'r', encoding='utf-8').read()
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
            show_message('Git repo initialized', 5, 'info')
        except:
            show_alert('Git Init', 'Failted to initialize repo!')

    def do_commit(self, *args):
        '''Git commit
        '''
        d = get_designer()
        if d.popup:
            return False
        input_dlg = InputDialog('Commit message: ')
        d.popup = Popup(title='Git Commit', content=input_dlg,
                        size_hint=(None, None), size=('300pt', '150pt'),
                        auto_dismiss=False)
        input_dlg.bind(on_confirm=self._perform_do_commit,
                       on_cancel=d.close_popup)
        d.popup.open()
        return True

    @ignore_proj_watcher
    def _perform_do_commit(self, input, *args):
        '''Perform the git commit with data from InputDialog
        '''
        message = input.get_user_input()
        if self.repo.is_dirty():
            try:
                self.repo.git.commit('-am', message)
                show_message('Commit: ' + message, 5, 'info')
            except GitCommandError as e:
                show_alert('Git Commit', 'Failed to commit!\n' + str(e))
        else:
            show_alert('Git Commit', 'There is nothing to commit')

        get_designer().close_popup()

    @ignore_proj_watcher
    def do_add(self, *args):
        '''Git select files from a list to add
        '''
        d = get_designer()
        if d.popup:
            return False
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
        popup = Popup(
            content=content, title='Git - Add files', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_add,
                     on_cancel=d.close_popup)

        content.show_items()
        d.popup = popup
        popup.open()

    @ignore_proj_watcher
    def _perform_do_add(self, instance, selected_files, *args):
        '''Add the selected files to git index
        '''
        try:
            self.repo.index.add(selected_files)
            show_message('%d file(s) added to Git index' %
                         len(selected_files), 5, 'info')
            get_designer().close_popup()
        except GitCommandError as e:
            show_alert('Git Add', 'Failed to add files to Git!\n' + str(e))

    def do_branches(self, *args):
        '''Shows a list of git branches and allow to change the current one
        '''
        d = get_designer()
        if d.popup:
            return False
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
        popup = Popup(
            content=content, title='Git - Branches', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_branches,
                     on_cancel=d.close_popup)

        content.selected_items = [self.repo.active_branch.name]
        content.show_items()
        d.popup = popup
        popup.open()

    @ignore_proj_watcher
    def _perform_do_branches(self, instance, branches, *args):
        '''If the branch name exists, try to checkout. If a new name, create
        the branch and checkout.
        If the code has modification, shows an alert and stops
        '''
        get_designer().close_popup()

        if self.repo.is_dirty():
            show_alert('Git checkout',
                       'Please, commit your changes before '
                       'switch branches.')
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
            branch_name = self.repo.active_branch.name
            self.dispatch('on_branch', branch_name)
        except GitCommandError as e:
            show_alert('Git Branches', 'Failed to switch branch!\n' + str(e))

    def on_branch(self, *args):
        '''Dispatch the branch name
        '''
        pass

    def do_diff(self, *args):
        '''Open a CodeInput with git diff
        '''
        diff = self.repo.git.diff()
        if not diff:
            diff = 'Empty diff'

        d = get_designer()
        panel = d.designer_content.tab_pannel
        inputs = d.code_inputs

        # check if diff is visible on tabbed panel.
        # if so, update the text content
        for i, code_input in enumerate(panel.tab_list):
            if code_input == self.diff_code_input:
                panel.switch_to(panel.tab_list[len(panel.tab_list) - i - 2])
                code_input.content.code_input.text = diff
                return

        # if not displayed, create or add it to the screen
        if self.diff_code_input is None:
            panel_item = DesignerCloseableTab(title='Git diff')
            panel_item.bind(on_close=panel.on_close_tab)
            scroll = PyScrollView()
            _py_code_input = scroll.code_input
            _py_code_input.text = diff
            _py_code_input.path = ''
            _py_code_input.readonly = True
            _py_code_input.lexer = DiffLexer()
            _py_code_input.saved = True
            panel_item.content = scroll
            panel_item.rel_path = ''
            self.diff_code_input = panel_item
        else:
            self.diff_code_input.content.code_input.text = diff
        panel.add_widget(self.diff_code_input)
        panel.switch_to(panel.tab_list[0])

    def do_push(self, *args):
        '''Open a list of remotes to push repository data.
        If there is not remote, shows an alert
        '''
        d = get_designer()
        if d.popup:
            return False
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
        popup = Popup(
            content=content, title='Git - Push Remote', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_push,
                     on_cancel=d.close_popup)

        content.selected_items = [remotes[0]]
        content.show_items()
        d.popup = popup
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
                show_message('Git remote push completed!', 5, 'info')
            except GitCommandError as e:
                progress.label.text = 'Failed to push!\n' + str(e)
                show_message('Failed to push', 5, 'error')
            get_designer().close_popup()

        progress.start()
        threading.Thread(target=push).start()

    def do_pull(self, *args):
        '''Open a list of remotes to pull remote data.
        If there is not remote, shows an alert
        '''
        d = get_designer()
        if d.popup:
            return False
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
        popup = popup = Popup(
            content=content, title='Git - Pull Remote', size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._perform_do_pull,
                     on_cancel=d.close_popup)

        content.selected_items = [remotes[0]]
        content.show_items()
        d.popup = popup
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
            get_designer().close_popup()

        progress.start()
        threading.Thread(target=pull).start()
