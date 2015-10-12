import re
import os
import sys
import inspect
import time
import functools
import shutil
import imp

from six import exec_

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.factory import Factory, FactoryException
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.sandbox import Sandbox
from kivy.clock import Clock

from designer.helper_functions import get_indentation, get_indent_str,\
    get_line_start_pos, get_kivy_designer_dir
from designer.proj_watcher import ProjectWatcher

PROJ_DESIGNER = '.designer'
KV_PROJ_FILE_NAME = os.path.join(PROJ_DESIGNER, 'kvproj')
PROJ_FILE_CONFIG = os.path.join(PROJ_DESIGNER, 'file_config.ini')
ignored_paths = ('.designer', '.buildozer', '.git', '__pycache__', 'bin', )


class Comment(object):
    '''Comment is an Abstract class for representing a commentary.
    '''
    def __init__(self, string, path, _file):
        super(Comment, self).__init__()
        self.string = string
        self.path = path
        self.kv_file = _file


class WidgetRule(object):
    '''WidgetRule is an Abstract class for representing a rule of Widget.
    '''
    def __init__(self, widget, parent):
        super(WidgetRule, self).__init__()
        self.name = widget
        self.parent = parent
        self.file = None
        self.kv_file = None
        self.module = None


class ClassRule(WidgetRule):
    '''ClassRule is a class for representing a class rule in kv
    '''
    def __init__(self, class_name):
        super(ClassRule, self).__init__(class_name, None)


class CustomWidgetRule(ClassRule):
    '''CustomWidgetRule is a class for representing a custom widgets rule in kv
    '''
    def __init__(self, class_name, kv_file, py_file):
        super(ClassRule, self).__init__(class_name, None)
        self.class_name = class_name
        self.kv_file = kv_file
        self.py_file = py_file


class RootRule(ClassRule):
    '''RootRule is a class for representing root rule in kv.
    '''
    def __init__(self, class_name, widget):
        super(RootRule, self).__init__(class_name)
        self.widget = widget


class ProjectLoaderException(Exception):
    pass


class ProjectLoader(object):
    '''ProjectLoader class, used to load Project
    '''

    def __init__(self, proj_watcher):
        super(ProjectLoader, self).__init__()
        self._dir_list = []
        self.proj_watcher = proj_watcher
        self.class_rules = []
        self.root_rule = None
        self.new_project = None
        self.dict_file_type_and_path = {}
        self.kv_file_list = []
        self.kv_code_input = None
        self.tab_pannel = None
        self._root_rule = None
        self.file_list = []
        self.proj_dir = ""
        self._is_root_already_in_factory = False

    def update_file_list(self):
        '''
        Update and return the file_list object
        '''
        self.file_list = self._get_file_list(self.proj_dir)
        return self.file_list

    def _get_file_list(self, path):
        '''This function is recursively called for loading all py file files
           in the current directory.
        '''

        file_list = []
        for ignored in ignored_paths:
            if ignored in path:
                return []

        if os.path.isfile(path):
            path = os.path.dirname(path)

        sys.path.insert(0, path)
        self._dir_list.append(path)
        for _file in os.listdir(path):
            file_path = os.path.join(path, _file)
            if os.path.isdir(file_path):
                file_list += self._get_file_list(file_path)
            else:
                # Consider only kv, py and buildozer(spec) files
                if file_path[file_path.rfind('.'):] in [".py", ".spec"]:
                    if os.path.dirname(file_path) == self.proj_dir:
                        file_list.insert(0, file_path)
                    else:
                        file_list.append(file_path)

        return file_list

    def add_custom_widget(self, py_path):
        '''This function is used to add a custom widget given path to its
           py file.
        '''

        f = open(py_path, 'r')
        py_string = f.read()
        f.close()

        # Find path to kv. py file will have Builder.load_file('path/to/kv')
        _r = re.findall(r'Builder\.load_file\s*\(\s*.+\s*\)', py_string)
        if _r == []:
            raise ProjectLoaderException('Cannot find widget\'s kv file.')

        py_string = py_string.replace(_r[0], '')
        kv_path = _r[0][_r[0].find('(') + 1: _r[0].find(')')]
        py_string = py_string.replace(kv_path, '')
        kv_path = kv_path.replace("'", '').replace('"', '')

        f = open(kv_path, 'r')
        kv_string = f.read()
        f.close()

        # Remove all the 'app' lines
        for app_str in re.findall(r'.+app+.+', kv_string):
            kv_string = kv_string.replace(
                app_str,
                app_str[:get_indentation(app_str)] + '#' + app_str.lstrip())

        Builder.load_string(kv_string)

        sys.path.insert(0, os.path.dirname(kv_path))

        _to_check = []

        # Get all the class_rules
        for class_str in re.findall(r'<+([\w_]+)>', kv_string):
            if re.search(r'\bclass\s+%s+.+:' % class_str, py_string):
                module = imp.new_module('CustomWidget')
                exec_(py_string, module.__dict__)
                sys.modules['AppModule'] = module
                class_rule = CustomWidgetRule(class_str, kv_path, py_path)
                class_rule.file = py_path
                class_rule.module = module
                self.custom_widgets.append(class_rule)

    def get_root_str(self, kv_str=''):
        '''This function will get the root widgets rule from either kv_str
           or if it is empty string then from the kv file of root widget
        '''

        if kv_str == '':
            f = open(self.root_rule.kv_file, 'r')
            kv_str = f.read()
            f.close()

        # Find the start position of root_rule
        start_pos = kv_str.find(self.root_rule.name)
        if start_pos == -1:
            raise ProjectLoaderException(
                'Cannot find root rule in its file')

        # Get line for start_pos
        _line = 0
        _line_pos = 0
        _line_pos = kv_str.find('\n', _line_pos + 1)
        while _line_pos != -1 and _line_pos < start_pos:
            _line_pos = kv_str.find('\n', _line_pos + 1)
            _line += 1

        # Find the end position of root_rule, where indentation becomes 0
        # or file ends
        _line += 1
        lines = kv_str.splitlines()
        _total_lines = len(lines)
        while _line < _total_lines and (lines[_line].strip() == '' or
                                        get_indentation(lines[_line]) != 0):
            _line_pos = kv_str.find('\n', _line_pos + 1)
            _line += 1

        end_pos = _line_pos

        root_old_str = kv_str[start_pos: end_pos]

        for _rule in self.class_rules:
            if _rule.name == self.root_rule.name:
                root_old_str = "<" + root_old_str

        return root_old_str

    def get_full_str(self):
        '''This function will give the full string of all detected kv files.
        '''

        text = ''
        for _file in self.kv_file_list:
            f = open(_file, 'r')
            text += f.read() + '\n'
            f.close()

        return text

    def load_new_project(self, kv_path):
        '''To load a new project given by kv_path
        '''

        self.new_project = True
        self._load_project(kv_path)

    def load_project(self, kv_path):
        '''To load a project given by kv_path
        '''

        ret = self._load_project(kv_path)
        self.new_project = False
        # Add project_dir to watch
        self.proj_watcher.start_watching(self.proj_dir)
        return ret

    def _load_project(self, kv_path):
        '''Pivate function to load any project given by kv_path
        '''

        if os.path.isdir(kv_path):
            self.proj_dir = kv_path
        else:
            self.proj_dir = os.path.dirname(kv_path)

        parent_proj_dir = os.path.dirname(self.proj_dir)
        sys.path.insert(0, parent_proj_dir)

        self.class_rules = []
        all_files_loaded = True
        _file = None

        for _file in os.listdir(self.proj_dir):
            # Load each kv file in the directory
            _file = os.path.join(self.proj_dir, _file)
            if _file[_file.rfind('.'):] != '.kv':
                continue

            self.kv_file_list.append(_file)

            f = open(_file, 'r')
            kv_string = f.read()
            f.close()

            # Remove all the 'app' lines
            for app_str in re.findall(r'.+app+.+', kv_string):
                kv_string = kv_string.replace(
                    app_str,
                    app_str[:get_indentation(app_str)] +
                    '#' + app_str.lstrip())

            # Get all the class_rules
            for class_str in re.findall(r'<+([\w_]+)>', kv_string):
                class_rule = ClassRule(class_str)
                class_rule.kv_file = _file
                self.class_rules.append(class_rule)

            try:
                root_name = re.findall(r'^([\w\d_]+)\:', kv_string,
                                       re.MULTILINE)

                if root_name != []:
                    # It will occur when there is a root rule and it can't
                    # be loaded by Builder because the its file
                    # has been imported
                    root_name = root_name[0]
                    if not hasattr(Factory, root_name):
                        match = re.search(r'^([\w\d_]+)\:', kv_string,
                                          re.MULTILINE)
                        kv_string = kv_string[:match.start()] + \
                            '<' + root_name + '>:' + kv_string[match.end():]
                        self.root_rule = RootRule(root_name, None)
                        self.root_rule.kv_file = _file
                        self._root_rule = self.root_rule
                        self._is_root_already_in_factory = False

                    else:
                        self._is_root_already_in_factory = True
                else:
                    self._is_root_already_in_factory = False

                re_kv_event = r'(\s+on_\w+\s*:.+)|([\s\w\d]+:[\.\s\w]+\(.*\))'
                root_rule = Builder.load_string(re.sub(re_kv_event,
                                                       '', kv_string))
                if root_rule:
                    self.root_rule = RootRule(root_rule.__class__.__name__,
                                              root_rule)
                    self.root_rule.kv_file = _file
                    self._root_rule = self.root_rule

            except Exception as e:
                all_files_loaded = False

        if not all_files_loaded:
            raise ProjectLoaderException('Cannot load file "%s"' % (_file))

        if os.path.exists(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME)):
            projdir_mtime = os.path.getmtime(self.proj_dir)

            f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'r')
            proj_str = f.read()
            f.close()

            _file_is_valid = True
            # Checking if the file is valid
            if proj_str == '' or\
                    proj_str.count('<files>') != proj_str.count('</files>') or\
                    proj_str.count('<file>') != proj_str.count('</file>') or\
                    proj_str.count('<class>') != proj_str.count('</class>'):
                _file_is_valid = False

            if _file_is_valid:
                projdir_time = proj_str[
                    proj_str.find('<time>') + len('<time>'):
                    proj_str.find('</time>')]

                projdir_time = float(projdir_time.strip())

            if _file_is_valid and projdir_mtime <= projdir_time:
                # Project Directory folder hasn't been modified,
                # file list will remain same
                self.file_list = []
                un_modified_files = []
                start_pos = proj_str.find('<files>')
                end_pos = proj_str.find('</files>')
                if start_pos != -1 and end_pos != -1:
                    start_pos = proj_str.find('<file>', start_pos)
                    end_pos1 = proj_str.find('</file>', start_pos)
                    while start_pos < end_pos and start_pos != -1:
                        _file = proj_str[
                            start_pos + len('<file>'):end_pos1].strip()
                        self.file_list.append(_file)
                        if os.path.getmtime(_file) <= projdir_time:
                            un_modified_files.append(_file)

                        start_pos = proj_str.find('<file>', end_pos1)
                        end_pos1 = proj_str.find('</file>', start_pos)

                    for _file in self.file_list:
                        _dir = os.path.dirname(_file)
                        if _dir not in sys.path:
                            sys.path.insert(0, _dir)

                # Reload information for app
                start_pos = proj_str.find('<app>')
                end_pos = proj_str.find('</app>')
                if start_pos != -1 and end_pos != -1:
                    self._app_class = proj_str[
                        proj_str.find('<class>', start_pos) + len('<class>'):
                        proj_str.find('</class>', start_pos)].strip()
                    self._app_file = proj_str[
                        proj_str.find('<file>', start_pos) + len('<file>'):
                        proj_str.find('</file>', start_pos)].strip()
                    f = open(self._app_file, 'r')
                    self._app_module = self._import_module(f.read(),
                                                           self._app_file)
                    f.close()

                # Reload information for the files which haven't been modified
                start_pos = proj_str.find('<classes>')
                end_pos = proj_str.find('</classes>')

                if start_pos != -1 and end_pos != -1:
                    while start_pos < end_pos and start_pos != -1:
                        start_pos = proj_str.find('<class>', start_pos) +\
                            len('<class>')
                        end_pos1 = proj_str.find('</class>', start_pos)
                        _file = proj_str[
                            proj_str.find('<file>', start_pos) + len('<file>'):
                            proj_str.find('</file>', start_pos)].strip()

                        if _file in un_modified_files:
                            # If _file is un modified then assign it to
                            # class rule with _name
                            _name = proj_str[
                                proj_str.find('<name>', start_pos) +
                                len('<name>'):
                                proj_str.find('</name>', start_pos)].strip()

                            for _rule in self.class_rules:
                                if _name == _rule.name:
                                    _rule.file = _file
                                    f = open(_file, 'r')
                                    _rule.module = self._import_module(
                                        f.read(), _file, _fromlist=[_name])
                                    f.close()

                        start_pos = proj_str.find('<class>', start_pos)
                        end_pos1 = proj_str.find('</class>', start_pos)

        if self.file_list == []:
            self.file_list = self._get_file_list(self.proj_dir)

        # Get all files corresponding to each class
        self._get_class_files()

        # If root widget is not created but root class is known
        # then create widget
        if self.root_rule and not self.root_rule.widget and \
                self.root_rule.name:
            self.root_rule.widget = self.get_widget_of_class(
                self.root_rule.name)

        self.load_proj_config()

    def load_proj_config(self):
        '''To load project's config file. Project's config file is stored in
           .designer directory in project's directory.
        '''

        try:
            f = open(os.path.join(self.proj_dir, PROJ_FILE_CONFIG), 'r')
            s = f.read()
            f.close()

            start_pos = -1
            end_pos = -1

            start_pos = s.find('<file_type_and_dirs>\n')
            end_pos = s.find('</file_type_and_dirs>\n')

            if start_pos != -1 and end_pos != -1:
                for searchiter in re.finditer(r'<file_type=.+', s):
                    if searchiter.start() < start_pos:
                        continue

                    if searchiter.start() > end_pos:
                        break

                    found_str = searchiter.group(0)
                    file_type = found_str[found_str.find('"') + 1:
                                          found_str.find(
                                              '"', found_str.find('"') + 1)]
                    folder = found_str[
                        found_str.find('"', found_str.find('dir=') + 1) + 1:
                        found_str.rfind('"')]

                    self.dict_file_type_and_path[file_type] = folder

        except IOError:
            pass

    def save_proj_config(self):
        '''To save project's config file.
        '''

        string = '<file_type_and_dirs>\n'
        for file_type in self.dict_file_type_and_path.keys():
            string += '    <file_type="' + file_type + '"' + ' dir="' + \
                self.dict_file_type_and_path[file_type] + '">\n'
        string += '</file_type_and_dirs>\n'

        f = open(os.path.join(self.proj_dir, PROJ_FILE_CONFIG), 'w')
        f.write(string)
        f.close()

    def add_dir_for_file_type(self, file_type, folder):
        '''To add directory for specified file_type. More information in
           add_file.py
        '''

        self.dict_file_type_and_path[file_type] = folder
        self.save_proj_config()

    def perform_auto_save(self, *args):
        '''To perform auto save. Auto Save is done after every 5 min.
        '''

        if not self.root_rule:
            return

        auto_save_dir = os.path.join(self.proj_dir, '.designer')
        auto_save_dir = os.path.join(auto_save_dir, 'auto_save')

        if not os.path.exists(auto_save_dir):
            os.makedirs(auto_save_dir)

        else:
            shutil.rmtree(auto_save_dir)
            os.mkdir(auto_save_dir)

        for _file in os.listdir(self.proj_dir):
            if list(set(ignored_paths) & {_file}):
                continue
            old_file = os.path.join(self.proj_dir, _file)
            new_file = os.path.join(auto_save_dir, _file)
            if os.path.isdir(old_file):
                shutil.copytree(old_file, new_file)
            else:
                shutil.copy(old_file, new_file)

        root_rule_file = os.path.join(auto_save_dir,
                                      os.path.basename(self.root_rule.kv_file))
        f = open(root_rule_file, 'r')
        _file_str = f.read()
        f.close()

        text = self.kv_code_input.text

        root_str = self.get_root_str()
        f = open(root_rule_file, 'w')
        _file_str = _file_str.replace(root_str, text)
        f.write(_file_str)
        f.close()

        # For custom widgets copy py and kv file
        for widget in self.custom_widgets:
            custom_kv = os.path.join(auto_save_dir,
                                     os.path.basename(widget.kv_file))
            if not os.path.exists(custom_kv):
                shutil.copy(widget.kv_file, custom_kv)

            custom_py = os.path.join(auto_save_dir,
                                     os.path.basename(widget.py_file))
            if not os.path.exists(custom_py):
                shutil.copy(widget.py_file, custom_py)

    def save_project(self, proj_dir=''):
        '''To save project to proj_dir. If proj_dir is not empty string then
           project is saved to a new directory other than its
           current directory and otherwise it is saved to the
           current directory.
        '''

        # To stop ProjectWatcher from emitting event when project is saved
        self.proj_watcher.allow_event_dispatch = False
        proj_dir_changed = False

        if self.new_project:
            # Create dir and copy new_proj.kv and new_proj.py to new directory
            if not os.path.exists(proj_dir):
                os.mkdir(proj_dir)

            kivy_designer_dir = get_kivy_designer_dir()
            kivy_designer_new_proj_dir = os.path.join(kivy_designer_dir,
                                                      "new_proj")
            for _file in os.listdir(kivy_designer_new_proj_dir):
                old_file = os.path.join(kivy_designer_new_proj_dir, _file)
                new_file = os.path.join(proj_dir, _file)
                if os.path.isdir(old_file):
                    shutil.copytree(old_file, new_file)
                else:
                    shutil.copy(old_file, new_file)

            self.file_list = self._get_file_list(proj_dir)

            new_kv_file = os.path.join(proj_dir, "main.kv")
            new_py_file = os.path.join(proj_dir, "main.py")

            self.proj_dir = proj_dir
            if self.root_rule:
                self.root_rule.kv_file = new_kv_file
                self.root_rule.py_file = new_py_file

            if self.class_rules:
                self.class_rules[0].py_file = new_py_file
                self.class_rules[0].kv_file = new_kv_file

            self.new_project = False

        else:
            if proj_dir != '' and proj_dir != self.proj_dir:
                proj_dir_changed = True

                # Remove previous project directories from sys.path
                for _dir in self._dir_list:
                    try:
                        sys.path.remove(_dir)
                    except:
                        pass

                # if proj_dir and self.proj_dir differs then user wants to save
                # an already opened project to somewhere else
                # Copy all the files
                if not os.path.exists(proj_dir):
                    os.mkdir(proj_dir)

                for _file in os.listdir(self.proj_dir):
                    old_file = os.path.join(self.proj_dir, _file)
                    new_file = os.path.join(proj_dir, _file)
                    if os.path.isdir(old_file):
                        shutil.copytree(old_file, new_file)
                    else:
                        shutil.copy(old_file, new_file)

                self.file_list = self._get_file_list(proj_dir)

                # Change the path of all files in the class rules,
                # root rule and app
                relative_path = self._app_file[
                    self._app_file.find(self.proj_dir):]
                self._app_file = os.path.join(proj_dir, relative_path)

                f = open(self._app_file, 'r')
                s = f.read()
                f.close()

                self._import_module(s, self._app_file,
                                    _fromlist=[self._app_class])

                for _rule in self.class_rules:
                    relative_path = _rule.kv_file[
                        _rule.kv_file.find(self.proj_dir):]
                    _rule.kv_file = os.path.join(proj_dir, relative_path)

                    relative_path = _rule.file[_rule.file.find(self.proj_dir):]
                    _rule.file = os.path.join(proj_dir, relative_path)

                    f = open(_rule.file, 'r')
                    s = f.read()
                    f.close()
                    self._import_module(s, _rule.file, _fromlist=[_rule.name])

                relative_path = self.root_rule.kv_file[
                    self.root_rule.kv_file.find(self.proj_dir):]
                self.root_rule.kv_file = os.path.join(proj_dir, relative_path)

                relative_path = self.root_rule.file[
                    self.root_rule.file.find(self.proj_dir):]
                self.root_rule.file = os.path.join(proj_dir, relative_path)

                self.proj_dir = proj_dir

        # For custom widgets copy py and kv file to project directory
        for widget in self.custom_widgets:
            custom_kv = os.path.join(self.proj_dir,
                                     os.path.basename(widget.kv_file))
            if not os.path.exists(custom_kv):
                shutil.copy(widget.kv_file, custom_kv)

            custom_py = os.path.join(self.proj_dir,
                                     os.path.basename(widget.py_file))
            if not os.path.exists(custom_py):
                shutil.copy(widget.py_file, custom_py)

        # Saving all opened py files and also reimport them
        for _code_input in self.tab_pannel.list_py_code_inputs:
            path = os.path.join(self.proj_dir, _code_input.rel_file_path)
            f = open(path, 'w')
            f.write(_code_input.text)
            f.close()
            _from_list = []
            for rule in self.class_rules:
                if rule.file == path:
                    _from_list.append(rule.file)

            if not self.is_root_a_class_rule():
                if self.root_rule.file == path:
                    _from_list.append(self.root_rule.name)

            # Ignore all types that are not .py
            if path.endswith(".py"):
                self._import_module(_code_input.text, path,
                                    _fromlist=_from_list)

        # Save all class rules
        text = self.kv_code_input.text
        for _rule in self.class_rules:
            # Get the kv text from KVLangArea and write it to class rule's file
            f = open(_rule.kv_file, 'r')
            _file_str = f.read()
            f.close()

            old_str = self.get_class_str_from_text(_rule.name, _file_str)
            new_str = self.get_class_str_from_text(_rule.name, text)

            f = open(_rule.kv_file, 'w')
            _file_str = _file_str.replace(old_str, new_str)
            f.write(_file_str)
            f.close()

        # If root widget is not changed
        if self._root_rule.name == self.root_rule.name:
            # Save root widget's rule
            is_root_class = False
            for _rule in self.class_rules:
                if _rule.name == self.root_rule.name:
                    is_root_class = True
                    break

            if not is_root_class:
                f = open(self.root_rule.kv_file, 'r')
                _file_str = f.read()
                f.close()

                old_str = self.get_class_str_from_text(self.root_rule.name,
                                                       _file_str,
                                                       is_class=False)
                new_str = self.get_class_str_from_text(self.root_rule.name,
                                                       text, is_class=False)

                f = open(self.root_rule.kv_file, 'w')
                _file_str = _file_str.replace(old_str, new_str)
                f.write(_file_str)
                f.close()

        else:
            # If root widget is changed
            # Root Widget changes, there can be these cases:
            root_name = self.root_rule.name
            f = open(self._app_file, 'r')
            file_str = f.read()
            f.close()
            self._root_rule = self.root_rule

            if self.is_root_a_class_rule() and self._app_file:
                # Root Widget's class rule is a custom class
                # and its rule is class rule. So, it already have been saved
                # the string of App's build() function will be changed to
                # return new root widget's class

                if self._app_class != 'runTouchApp':
                    s = re.search(r'class\s+%s.+:' % self._app_class, file_str)
                    if s:
                        build_searchiter = None
                        for searchiter in re.finditer(
                                r'[ \ \t]+def\s+build\s*\(\s*self.+\s*:',
                                file_str):
                            if searchiter.start() > s.start():
                                build_searchiter = searchiter
                                break

                        if build_searchiter:
                            indent = get_indentation(build_searchiter.group(0))
                            file_str = file_str[:build_searchiter.end()] +\
                                '\n' + get_indent_str(2 * indent) + "return " +\
                                root_name + "()\n" + \
                                file_str[build_searchiter.end():]

                        else:
                            file_str = file_str[:s.end()] + \
                                "\n    def build(self):\n        return " + \
                                root_name + '()\n' + file_str[s.end():]

                else:
                    file_str = re.sub(r'runTouchApp\s*\(.+\)',
                                      'runTouchApp(' + root_name + '())',
                                      file_str)

                f = open(self._app_file, 'w')
                f.write(file_str)
                f.close()

            else:
                # Root Widget's rule is not a custom class
                # and its rule is root rule
                # Its kv_file should be of App's class name
                # and App's build() function should be cleared
                if not self.root_rule.kv_file:
                    s = self._app_class.replace('App', '').lower()
                    root_file = None
                    for _file in self.kv_file_list:
                        if os.path.basename(_file).find(s) == 0:
                            self.root_rule.kv_file = _file
                            break

                f = open(self.root_rule.kv_file, 'r')
                _file_str = f.read()
                f.close()

                new_str = self.get_class_str_from_text(self.root_rule.name,
                                                       text, False)

                f = open(self.root_rule.kv_file, 'a')
                f.write(new_str)
                f.close()

                if self._app_class != 'runTouchApp':
                    s = re.search(r'class\s+%s.+:' % self._app_class, file_str)
                    if s:
                        build_searchiter = None
                        for searchiter in re.finditer(
                                r'[ \ \t]+def\s+build\s*\(\s*self.+\s*:',
                                file_str):
                            if searchiter.start() > s.start():
                                build_searchiter = searchiter
                                break

                        if build_searchiter:
                            lines = file_str.splitlines()
                            total_lines = len(lines)
                            indent = get_indentation(build_searchiter.group(0))

                            _line = 0
                            _line_pos = -1
                            _line_pos = file_str.find('\n', _line_pos + 1)
                            while _line_pos <= build_searchiter.start():
                                _line_pos = file_str.find('\n', _line_pos + 1)
                                _line += 1

                            _line += 1

                            while _line < total_lines:
                                if lines[_line].strip() != '' and\
                                        get_indentation(lines[_line]) <= \
                                        indent:
                                    break

                                _line += 1

                            _line -= 1
                            end = get_line_start_pos(file_str, _line)
                            start = build_searchiter.start()
                            file_str = file_str.replace(file_str[start:end],
                                                        '    pass')

                            f = open(self._app_file, 'w')
                            f.write(file_str)
                            f.close()

        # Allow Project Watcher to emit events
        Clock.schedule_once(self._allow_proj_watcher_dispatch, 1)

    def get_class_str_from_text(self, class_name, _file_str, is_class=True):
        '''To return the full class rule of class_name from _file_str
        '''
        _file_str += '\n'
        start_pos = -1
        # Find the start position of class_name
        if is_class:
            start_pos = _file_str.find('<' + class_name + '>:')
        else:
            while True:
                start_pos = _file_str.find(class_name, start_pos + 1)
                if start_pos == 0 or not (_file_str[start_pos - 1].isalnum() and
                                          _file_str[start_pos - 1] != ''):
                    break

        _line = 0
        _line_pos = 0
        _line_pos = _file_str.find('\n', _line_pos + 1)
        while _line_pos != -1 and _line_pos < start_pos:
            _line_pos = _file_str.find('\n', _line_pos + 1)
            _line += 1

        # Find the end position of class_name, where indentation becomes 0
        # or file ends
        _line += 1
        lines = _file_str.splitlines()
        _total_lines = len(lines)

        hash_pos = 0
        while hash_pos == 0 and _line < _total_lines:
            hash_pos = lines[_line].find('#')
            if hash_pos == 0:
                _line_pos += 1 + len(lines[_line])
                _line += 1

        while _line < _total_lines and (lines[_line].strip() == '' or
                                        get_indentation(lines[_line]) != 0):
            _line_pos = _file_str.find('\n', _line_pos + 1)
            _line += 1
            hash_pos = 0
            while hash_pos == 0 and _line < _total_lines:
                hash_pos = lines[_line].find('#')
                if hash_pos == 0:
                    _line += 1

        end_pos = _line_pos

        old_str = _file_str[start_pos: end_pos]
        return old_str

    def _allow_proj_watcher_dispatch(self, *args):
        '''To start project_watcher to start watching self.proj_dir
        '''

        self.proj_watcher.allow_event_dispatch = True
        # self.proj_watcher.start_watching(self.proj_dir)

    def _app_in_string(self, s):
        '''To determine if there is an App class or runTouchApp
           defined/used in string s.
        '''

        if 'runTouchApp(' in s:
            self._app_class = 'runTouchApp'
            return True

        elif 'kivy.app' in s:
            for _class in re.findall(r'\bclass\b.+:', s):
                b_index1 = _class.find('(')
                b_index2 = _class.find(')')
                classes = _class[b_index1 + 1:b_index2]
                classes = re.sub(r'[\s]+', '', classes)
                classes = classes.split(',')
                if 'App' in classes:
                    self._app_class = _class[_class.find(' '):b_index1].strip()
                    return True

        return False

    def _get_class_files(self):
        '''To search through all detected class rules and find
           their python files and to search for app.
        '''
        if self._app_file is None:
            # Search for main.py
            for _file in self.file_list:
                if _file[_file.rfind('/') + 1:] == 'main.py':
                    f = open(_file, 'r')
                    s = f.read()
                    f.close()
                    if self._app_in_string(s):
                        self._app_module = self._import_module(s, _file)
                        self._app_file = _file

            # Search for a file with app in its name
            if not self._app_class:
                for _file in self.file_list:
                    if 'app' in _file[_file.rfind('/'):]:
                        f = open(_file, 'r')
                        s = f.read()
                        f.close()
                        if self._app_in_string(s):
                            self._app_module = self._import_module(s, _file)
                            self._app_file = _file

        to_find = []
        for _rule in self.class_rules:
            if _rule.file is None:
                to_find.append(_rule)

        if self.root_rule:
            to_find.append(self.root_rule)

        # If cannot find due to above methods, search every file
        for _file in self.file_list:
            if _file[_file.rfind('.') + 1:] == 'py':
                f = open(_file, 'r')
                s = f.read()
                f.close()
                if not self._app_file and self._app_in_string(s):
                    self._app_module = self._import_module(s, _file)
                    self._app_file = _file

                for _rule in to_find[:]:
                    if _rule.file:
                        continue

                    if re.search(r'\bclass\s*%s+.+:' % (_rule.name), s):
                        mod = self._import_module(s, _file,
                                                  _fromlist=[_rule.name])
                        if hasattr(mod, _rule.name):
                            _rule.file = _file
                            to_find.remove(_rule)
                            _rule.module = mod

        # Cannot Find App, So, use default runTouchApp
        if not self._app_file:
            self._app_class = 'runTouchApp'

        # Root Widget may be in Factory not in file
        if self.root_rule:
            if not self.root_rule.file and\
                    hasattr(Factory, self.root_rule.name):
                to_find.remove(self.root_rule)

        # to_find should be empty, if not some class's files are not detected
        if to_find != []:
            raise ProjectLoaderException(
                'Cannot find class files for all classes')

    def _import_module(self, s, _file, _fromlist=[]):
        module = None
        import_from_s = False
        _r = re.findall(r'Builder\.load_file\s*\(\s*.+\s*\)', s)
        if _r:
            s = s.replace(_r[0], '')
            import_from_s = True

        run_pos = s.rfind('().run()')

        i = None
        if run_pos != -1:
            run_pos -= 1
            while not s[run_pos].isspace():
                run_pos -= 1

            i = run_pos - 1
            while s[i] == ' ':
                i -= 1

        if i is not None and i == run_pos - 1 or _r != []:
            if i == run_pos - 1:
                s = s.replace('%s().run()' % self._app_class, '')

            if 'AppModule' in sys.modules:
                del sys.modules['AppModule']

            module = imp.new_module('AppModule')
            exec_(s, module.__dict__)
            sys.modules['AppModule'] = module
            return module

        module_name = _file[_file.rfind(os.sep) + 1:].replace('.py', '')
        if module_name in sys.modules:
            del sys.modules[module_name]

        module = __import__(module_name, fromlist=_fromlist)
        return module

    def cleanup(self, stop_watcher=True):
        '''To cleanup everything loaded by previous project.
        '''

        if stop_watcher:
            self.proj_watcher.stop()

        # Remove all class rules and root rules of previous project
        rules = []

        try:
            rules = Builder.match(self.root_rule.widget)
            for _rule in rules:
                for _tuple in Builder.rules[:]:
                    if _tuple[1] == _rule:
                        Builder.rules.remove(_tuple)
        except:
            pass

        for _tuple in Builder.rules[:]:
            for _rule in self.class_rules:
                if "<" + _rule.name + ">" == _tuple[1].name:
                    Builder.rules.remove(_tuple)

        if self.root_rule and not self._is_root_already_in_factory and\
                hasattr(Factory, self.root_rule.name):
            Factory.unregister(self.root_rule.name)

        self._app_file = None
        self._app_class = None
        self._app_module = None
        self._app = None
        # Remove previous project directories
        for _dir in self._dir_list:
            try:
                sys.path.remove(_dir)
            except:
                pass

        self.kv_file_list = []
        self.file_list = []
        self._dir_list = []
        self.class_rules = []
        self.list_comments = []
        self.custom_widgets = []
        self.dict_file_type_and_path = {}
        self.root_rule = None
        self._root_rule = None

    def get_app(self, reload_app=False):
        '''To get the applications app class instance
        '''

        if not self._app_file or not self._app_class or not self._app_module:
            return None

        if not reload_app and self._app:
            return self._app

        for name, obj in inspect.getmembers(self._app_module):
            if inspect.isclass(obj) and self._app_class == name:
                self._app = obj()
                return self._app

        # if still couldn't get app, although that shouldn't happen
        return None

    def reload_from_str(self, root_str):
        '''To reload from root_str
        '''

        rules = []
        # Cleaning root rules
        try:
            rules = Builder.match(self.root_rule.widget)
            for _rule in rules:
                for _tuple in Builder.rules[:]:
                    if _tuple[1] == _rule:
                        Builder.rules.remove(_tuple)
        except:
            pass

        # Cleaning class rules
        for _rule in self.class_rules:
            for rule in Builder.rules[:]:
                if rule[1].name == '<' + _rule.name + '>':
                    Builder.rules.remove(rule)
                    break

        root_widget = None
        # Remove all the 'app' lines
        root_str = re.sub(r'.+app+.+', '', root_str)

        root_widget = Builder.load_string(root_str)

        if not root_widget:
            root_widget = self.get_widget_of_class(self.root_rule.name)
            self.root_rule.widget = root_widget

        if not root_widget:
            root_name = root_str[:root_str.find('\n')]
            root_name = root_widget.replace(':', '').replace('<', '')
            root_name = root_widget.replace('>', '')
            root_widget = self.set_root_widget(root_name)

        return root_widget

    def is_root_a_class_rule(self):
        '''Returns True if root rule is a class rule
        '''

        for _rule in self.class_rules:
            if _rule.name == self.root_rule.name:
                return True

        return False

    def set_root_widget(self, root_name, widget=None):
        '''To set root_name as the root rule.
        '''

        root_widget = None
        if not widget:
            root_widget = self.get_widget_of_class(root_name)
        else:
            root_widget = widget

        self.root_rule = RootRule(root_name, root_widget)
        for _rule in self.class_rules:
            if _rule.name == root_name:
                self.root_rule.kv_file = _rule.kv_file
                self.root_rule.py_file = _rule.file
                break

        if not self._root_rule:
            self._root_rule = self.root_rule

        return root_widget

    def get_root_widget(self, new_root=False):
        '''To get the root widget of the current project.
        '''

        if not new_root and self.root_rule and self.root_rule.name != '':
            return self.root_rule.widget

        if self._app_file is None:
            return None

        f = open(self._app_file, 'r')
        s = f.read()
        f.close()

        current_app = App.get_running_app()
        app = self.get_app(reload_app=True)
        root_widget = None
        if app is not None:
            root_widget = app.build()
            if not root_widget:
                root_widget = app.root

        App._running_app = current_app

        if root_widget:
            self.root_rule = RootRule(root_widget.__class__.__name__,
                                      root_widget)
            for _rule in self.class_rules:
                if _rule.name == self.root_rule.name:
                    self.root_rule.kv_file = _rule.kv_file
                    self.root_rule.file = _rule.file
                    break

            if not self._root_rule:
                self._root_rule = self.root_rule

        if not self.root_rule.kv_file:
            raise ProjectLoaderException("Cannot find root widget's kv file")

        return root_widget

    def get_widget_of_class(self, class_name):
        '''To get instance of the class_name
        '''

        self.root = getattr(Factory, class_name)()
        return self.root

    def is_widget_custom(self, widget):
        for rule in self.class_rules:
            if rule.name == type(widget).__name__:
                return True

        return False

    def record(self):
        '''To record all the findings in ./designer/kvproj. These will
           be loaded again if project hasn't been modified
           outside Kivy Designer
        '''

        if not os.path.exists(os.path.join(
                self.proj_dir, os.path.dirname(KV_PROJ_FILE_NAME))):
            os.mkdir(os.path.join(self.proj_dir, ".designer"))

        f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'w')
        f.close()

        f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'w')
        proj_file_str = '<time>\n' + '    ' + str(time.time()) + '\n</time>\n'
        proj_file_str += '<files>\n'
        for _file in self.file_list:
            proj_file_str += '    <file>\n'
            proj_file_str += '        ' + _file
            proj_file_str += '\n    </file>\n'

        proj_file_str += '</files>\n'

        proj_file_str += '<classes>\n'
        for _rule in self.class_rules:
            proj_file_str += '    <class>\n'
            proj_file_str += '         <name>\n'
            proj_file_str += '             ' + _rule.name
            proj_file_str += '\n         </name>\n'
            proj_file_str += '         <file>\n'
            proj_file_str += '             ' + _rule.file
            proj_file_str += '\n         </file>\n'
            proj_file_str += '\n    </class>\n'

        proj_file_str += '</classes>\n'

        if self._app_class and self._app_file:
            proj_file_str += '<app>\n'
            proj_file_str += '    <class>\n'
            proj_file_str += '         ' + self._app_class
            proj_file_str += '\n    </class>\n'
            proj_file_str += '    <file>\n'
            proj_file_str += '         ' + self._app_file
            proj_file_str += '\n    </file>\n'
            proj_file_str += '</app>\n'

        f.write(proj_file_str)

        f.close()
