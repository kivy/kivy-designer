import ast
import imp
import inspect
import os
import re
import sys

from designer.utils.utils import (
    get_app_widget,
    get_designer,
    show_error_console,
    show_message,
)
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    Clock,
    DictProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.widget import Widget
from six import exec_
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer
from io import open


IGNORED_PATHS = ('/.designer', '/.buildozer', '/.git', '/bin',)
IGNORED_EXTS = ('.pyc',)
KV_EVENT_RE = r'(\s+on_\w+\s*:.+)|(^[\s\w\d]+:[\.]+[\s\w]+\(.*)'
KV_ROOT_WIDGET = r'^([\w\d_]+)\:'
KV_APP_WIDGET = r'^<([\w\d_@]+)>\:'


class ProjectEventHandler(RegexMatchingEventHandler):
    def __init__(self, project_watcher):
        super(ProjectEventHandler, self).__init__()
        self.project_watcher = project_watcher

    def on_any_event(self, event):
        if self.project_watcher:
            self.project_watcher.on_any_event(event)


class ProjectWatcher(EventDispatcher):
    '''ProjectWatcher is responsible for watching any changes in
       project directory. It will call self._callback whenever there
       are any changes. It can currently handle only one directory at
       a time.
    '''

    _active = BooleanProperty(True)
    '''Indicates if the watchdog can dispatch events
       :data:`active` is a :class:`~kivy.properties.BooleanProperty`
    '''

    _path = StringProperty('')
    '''Project folder
       :data:`path` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_project_modified',)

    def __init__(self, **kw):
        super(ProjectWatcher, self).__init__(**kw)

        self._observer = None
        self._handler = None
        self._watcher = None

    def start_watching(self, path):
        '''To start watching project_dir.
        '''
        self._path = path
        self._observer = Observer()
        self._handler = ProjectEventHandler(project_watcher=self)
        self._watcher = self._observer.schedule(
            self._handler, path,
            recursive=True)
        self._observer.start()

    def on_project_modified(self, *args):
        pass

    def stop_watching(self):
        '''To stop watching currently watched directory. This will also call
           join() on the thread created by Observer.
        '''

        if self._observer:
            self._observer.unschedule_all()
            self._observer.stop()
            self._observer.join()

        self._observer = None

    def pause_watching(self):
        '''Pauses the watcher
        '''
        self._active = False

    def resume_watching(self, delay=1):
        '''Resume the watcher
        :param delay: seconds to start the watching
        '''
        Clock.schedule_once(self._resume_watching, delay)

    def _resume_watching(self, *args):
        if self._observer:
            self._observer.event_queue.queue.clear()
        self._active = True

    def on_any_event(self, event):
        if self._active:
            # filter events
            path = event.src_path.replace(self._path, '')
            if not path:
                return
            if '__pycache__' in path:
                return
            for ign in IGNORED_PATHS:
                if path.startswith(ign):
                    return
            for ext in IGNORED_EXTS:
                if event.src_path.endswith(ext):
                    return

            self.dispatch('on_project_modified', event)


class CallWrapper(ast.NodeTransformer):
    def visit_Expr(self, node):
        if node.col_offset == 0:
            return None
        return node


class AppWidget(EventDispatcher):
    name = StringProperty('')
    '''Root Widget name.
       :data:`name` is a :class:`~kivy.properties.StringProperty` and
       defaults to ''
    '''

    kv_path = StringProperty('')
    '''RootWidget associated kv file path.
       :data:`kv_path` is a :class:`~kivy.properties.StringProperty` and
       default to ''
    '''

    py_path = StringProperty('')
    '''RootWidget associated py file path.
       :data:`py_path` is a :class:`~kivy.properties.StringProperty` and
       default to ''
    '''

    is_root = BooleanProperty(False)
    '''Indicates if this widget is a root/default kivy widget or not
        :data:`is_root` is a :class:`~kivy.properties.BooleanProperty` and
        defaults to False
    '''

    instance = ObjectProperty(None)
    '''If the widget is root, it has a instance returned by Builder.load_string
    If not is root, instance is None
    data:`instance` is a :class:`~kivy.properties.ObjectProperty` and
        defaults to None
    '''

    is_dynamic = BooleanProperty(False)
    '''Indicates if this widget is a dynamic widget or not
        :data:`is_dynamic` is a :class:`~kivy.properties.BooleanProperty` and
        defaults to False
    '''

    module_name = StringProperty('')
    '''ModuleName used in the class import
       :data:`module_name` is a :class:`~kivy.properties.StringProperty` and
       default to ''
    '''


class Project(EventDispatcher):
    path = StringProperty('')
    '''Project path.
       :data:`path` is a :class:`~kivy.properties.StringProperty`
    '''

    saved = BooleanProperty(True)
    '''Indicates if the project was saved. The project is seted as saved when
        oppened
       :data:`saved` is a :class:`~kivy.properties.BooleanProperty`
    '''

    new_project = BooleanProperty(False)
    '''Indicates if it's a new project.
       :data:`new_project` is a :class:`~kivy.properties.BooleanProperty`
    '''

    file_list = ListProperty([])
    '''List of files in the project folder.
        :data:`file_list` is a :class:`~kivy.properties.ListProperty`
    '''

    kv_list = ListProperty([])
    '''List of kv files in the project folder.
        :data:`kv_list` is a :class:`~kivy.properties.ListProperty`
    '''

    py_list = ListProperty([])
    '''List of py files in the project folder.
        :data:`kv_list` is a :class:`~kivy.properties.ListProperty`
    '''

    app_widgets = DictProperty({})
    '''List of :class:`~designer.core.project_manager.AppWidget`.
    :data:`app_widgets` is a :class:`~kivy.properties.DictProperty`
    '''

    def __init__(self, **kw):
        super(Project, self).__init__(**kw)
        self._errors = []  # exception messages

    def open(self):
        '''Opens then project
        '''
        self.saved = True
        self.get_files()
        self.parse()

    def get_files(self, path=None, force_reload=True):
        '''Gets a list of files in the project folder. If force_reload is True,
        will gets the list from hard drive. Otherwiser will return the last
        file_list
        '''
        if path is None:
            path = self.path

        if not force_reload:
            return self.file_list

        file_list = []
        for ignored in IGNORED_PATHS:
            if ignored in path:
                return []

        for _file in os.listdir(path):
            file_path = os.path.join(path, _file)
            if os.path.isdir(file_path):
                file_list += self.get_files(file_path)
            else:
                if file_path[file_path.rfind('.'):] not in IGNORED_EXTS:
                    if os.path.dirname(file_path) == self.path:
                        file_list.insert(0, file_path)
                    else:
                        file_list.append(file_path)

        self.file_list = file_list
        return file_list

    def parse(self, reload_files=False):
        '''Parse project files to analyse python and kv files
        '''

        if reload_files:
            self.get_files()

        # reset caches
        self.kv_list = []
        self.py_list = []
        self.app_widgets = {}
        self._errors = []

        # find kv and python files
        for _file in self.file_list:
            # in the first step, loads only kv files
            ext = _file[_file.rfind('.'):]
            if ext == '.kv':
                self.kv_list.append(_file)
            elif ext == '.py' or ext == '.py2' or ext == '.py3':
                self.py_list.append(_file)

        # find and load classes
        for py in self.py_list:
            self.parse_py(py)
        # find and load root widgets
        for kv in self.kv_list:
            src = open(kv, 'r', encoding='utf-8').read()
            # removes events
            src = re.sub(KV_EVENT_RE, '', src, flags=re.MULTILINE)
            self.parse_kv(src, kv)

        self.show_errors()

    def show_errors(self, *args):
        '''Pop errors got in the last operations and display it on
        Error Console
        '''
        errors = list(self._errors)
        show_error_console('')
        if len(errors):
            show_message(
                'Errors found while parsing the project. Check Error Console',
                5, 'error'
            )
        for er in range(0, len(errors)):
            show_error_console('\n\nError: %d\n' % (er + 1), append=True)
            show_error_console(errors[er], append=True)
            self._errors.remove(errors[er])

    def _clean_old_kv(self, path):
        '''
        Removes widgets and rules already processed to this file
        :param path: file path - the same that in app_widgets
        '''
        for key in dict(self.app_widgets):
            wd = self.app_widgets[key]
            if path != wd.kv_path:
                continue
            wdg = get_app_widget(wd)
            if wdg is None:
                p = get_designer().ui_creator.playground
                if p.root_name == wd.name:
                    wdg = p._last_root
                if not wdg:
                    continue
            if wd.is_dynamic:
                del self.app_widgets[key]

            rules = Builder.match(wdg)

            # Cleaning widget rules
            for _rule in rules:
                for _tuple in Builder.rules[:]:
                    if _tuple[1] == _rule:
                        Builder.rules.remove(_tuple)
                        if wd.is_dynamic:
                            Factory.unregister(wd.name.split('@')[0])

            # Cleaning class rules
            for rule in Builder.rules[:]:
                if rule[1].name == '<' + wd.name + '>':
                    Builder.rules.remove(rule)
                    break

    def parse_kv(self, src, path):
        '''
        Parses a KV file with Builder.load_string. Identify root widgets and
        add them to self.root_widgets dict
        :param path: path of the kv file
        :param src: kv string
        :return boolean indicating if succeed in parsing the file
        '''
        self._clean_old_kv(path)
        root = None
        try:
            root = Builder.load_string(src, filename=os.path.basename(path))
        except Exception as e:
            self._errors.append(str(e))
            d = get_designer()
            d.ui_creator.kv_code_input.have_error = True
            return False
        # first, if a root widget was found, maps it
        if root:
            root_widgets = re.findall(KV_ROOT_WIDGET, src, re.MULTILINE)
            root_name = type(root).__name__
            for r in root_widgets:
                if r != root_name:
                    continue
                if r in self.app_widgets:
                    wdg = self.app_widgets[r]
                else:
                    wdg = AppWidget()
                wdg.name = r
                if path:
                    wdg.kv_path = path
                wdg.is_root = True
                wdg.instance = root
                if wdg not in self.app_widgets:
                    self.app_widgets[r] = wdg

        # now, get all custom widgets
        app_widgets = re.findall(KV_APP_WIDGET, src, re.MULTILINE)
        for a in app_widgets:
            wdg = self.app_widgets[a] if a in self.app_widgets else AppWidget()
            wdg.name = a
            if path:
                wdg.kv_path = path
            wdg.is_dynamic = '@' in a
            # dynamic widgets are not preloaded by py files
            if wdg not in self.app_widgets:
                self.app_widgets[a] = wdg

        return True

    def parse_py(self, path):
        '''Parses a Python file and load it.
        '''

        rel_path = path.replace(self.path, '')

        # creates a name to the import based in the file name and its path
        module_name = 'KDImport' + ''.join([x.replace('.py', '').capitalize()
                                            for x in rel_path.split('/')])

        # remove method calls to do a safe import
        src = open(path, 'r', encoding='utf-8').read()
        try:
            p = ast.parse(src, os.path.basename(path))
        except SyntaxError as e:
            self._errors.append(str(e))
            return False
        p = CallWrapper().visit(p)
        p = ast.fix_missing_locations(p)

        # if module is already loaded, removes it
        if module_name in sys.modules:
            del sys.modules[module_name]

        # imports the new python
        module = imp.new_module(module_name)

        try:
            exec_(compile(p, os.path.basename(path), 'exec'), module.__dict__)
        except Exception as e:
            self._errors.append(str(e))
            return False
        sys.modules[module_name] = module

        # find classes and possible widgets
        classes = inspect.getmembers(
            sys.modules[module_name],
            lambda member:
            inspect.isclass(member) and member.__module__ == module_name
        )

        if classes:
            self.load_widgets(path, classes, module_name)

        return True

    def load_widgets(self, path, classes, module_name):
        '''
        Analyze classes and loads Widgets from an array
        :param classes: array with classes to be analyzed
        :return: self.root_widgets
        '''
        for klass_name, klass in classes:
            if issubclass(klass, Widget):
                # updates root_widget dict
                if klass_name in self.app_widgets:
                    # if already exists, update only the path
                    self.app_widgets[klass_name].py_path = path
                else:
                    # otherwise create a new widget representation
                    r = AppWidget()
                    r.py_path = path
                    r.name = klass_name
                    r.module_name = module_name
                    self.app_widgets[klass_name] = r

        return self.app_widgets

    def save(self, code_inputs=None, *args):
        '''Get all KD Code input and save the content
        :param code_inputs list of files to save. If None, get all open files
        '''
        if not code_inputs:
            d = get_designer()
            code_inputs = d.code_inputs

        try:
            for code in code_inputs:
                fname = code.path
                if not fname:
                    continue
                content = code.text
                open(fname, 'w', encoding='utf-8').write(content)
                code.saved = True
        except IOError as e:
            return False

        self.saved = True
        self.new_project = False
        return True


class ProjectManager(EventDispatcher):
    current_project = ObjectProperty(None)
    '''An instance of the current project.
       :data:`current_project` is a :class:`~kivy.properties.ObjectProperty`
    '''

    projects = DictProperty(None)
    '''A map of opened projects
       :data:`projects` is a :class:`~kivy.properties.DictProperty`
    '''

    project_manager = BooleanProperty(True)
    '''Auto save the project
        :data:`project_manager` is a :class:`~kivy.properties.BooleanProperty`
    '''

    def __init__(self, **kwargs):
        super(ProjectManager, self).__init__(**kwargs)
        self.current_project = Project()

    def open_project(self, path):
        '''Opens a Python project by path, and returns the Project instance
        '''
        if os.path.isfile(path):
            path = os.path.dirname(path)

        if path in self.projects:
            self.current_project = self.projects[path]
            self.current_project.open()
            return self.current_project

        p = Project(path=path)
        p.open()
        self.projects[path] = p
        self.current_project = p
        return self.projects[path]

    def close_current_project(self):
        '''Closes a project, setting saved as True and new_project as False,
        and removing it from current_project
        :param project: instance of pro
        '''
        self.current_project.saved = True
        self.current_project.new_project = False
        self.current_project = Project()
