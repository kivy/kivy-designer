import kivy
import re
import os, sys, inspect
import time
import functools
import shutil
import imp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.sandbox import Sandbox
from kivy.clock import Clock

from designer.helper_functions import get_indentation, get_indent_str
from designer.proj_watcher import ProjectWatcher

KV_PROJ_FILE_NAME = '.designer/kvproj'

class Comment(object):
    
    def __init__(self, string, path, _file):
        super(Comment, self).__init__()
        self.string = string
        self.path = path
        self.kv_file = _file

class WidgetRule(object):
    
    def __init__(self, widget, parent):
        super(WidgetRule, self).__init__()
        self.name = widget
        self.parent = parent
        self.file = None
        self.kv_file = None
        self.module = None


class ClassRule(WidgetRule):
    
    def __init__(self, class_name):
        super(ClassRule, self).__init__(class_name, None)


class CustomWidgetRule(ClassRule):

    def __init__(self, class_name, kv_file, py_file):
        super(ClassRule, self).__init__(class_name, None)
        self.class_name = class_name
        self.kv_file = kv_file
        self.py_file = py_file


class RootRule(ClassRule):
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

    def _get_file_list(self, path):
        file_list = []
        sys.path.insert(0, path)
        self._dir_list.append(path)
        for _file in os.listdir(path):
            file_path = os.path.join(path, _file)
            if os.path.isdir(file_path):
                file_list += self._get_file_list(file_path)
            else:
                #Consider only py files
                if file_path[file_path.rfind('.'):] == '.py':
                    if os.path.dirname(file_path) == self.proj_dir:
                        file_list.insert(0, file_path)
                    else:
                        file_list.append(file_path)

        return file_list
    
    def add_custom_widget(self, py_path):
        f = open(py_path, 'r')
        py_string = f.read()
        f.close()
        
        #Find path to kv. py file will have Builder.load_file('path/to/kv')
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

        #Remove all the 'app' lines
        for app_str in re.findall(r'.+app+.+', kv_string):
            kv_string = kv_string.replace(app_str, 
                                          app_str[:get_indentation(app_str)]\
                                          + '#' + app_str.lstrip())

        Builder.load_string(kv_string)
        
        sys.path.insert(0, os.path.dirname(kv_path))
        
        _to_check = []

        #Get all the class_rules
        for class_str in re.findall(r'<+([\w_]+)>', kv_string):
            if re.search(r'\bclass\s+%s+.+:'%class_str, py_string):
                module = imp.new_module('CustomWidget')
                exec py_string in module.__dict__
                sys.modules['AppModule'] = module
                class_rule = CustomWidgetRule(class_str, kv_path, py_path)
                class_rule.file = py_path
                class_rule.module = module
                self.custom_widgets.append(class_rule)
    
    def get_root_str(self):
        f = open(self.root_rule.kv_file, 'r')
        kv_str = f.read()
        f.close()

        #Find the start position of root_rule
        start_pos = kv_str.find(self.root_rule.name)
        if start_pos == -1:
            raise ProjectLoaderException(
                'Cannot find root rule in its file')

        #Get line for start_pos
        _line = 0
        _line_pos = 0
        _line_pos = kv_str.find('\n', _line_pos + 1)
        while _line_pos != -1 and _line_pos < start_pos:
            _line_pos = kv_str.find('\n', _line_pos + 1)
            _line += 1

        #Find the end position of root_rule, where indentation becomes 0
        #or file ends
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
    
    def load_new_project(self, kv_path):
        self.new_project = True
        self._load_project(kv_path)
    
    def load_project(self, kv_path):
        ret = self._load_project(kv_path)
        self.new_project = False
        if ret:
            #Add project_dir to watch
            self.proj_watcher.start_watching(self.proj_dir)

        return ret

    def _load_project(self, kv_path):
        try:
            self.cleanup()
            
            if os.path.isdir(kv_path):
                self.proj_dir = kv_path
            else:
                self.proj_dir = os.path.dirname(kv_path)

            parent_proj_dir = os.path.dirname(self.proj_dir)
            sys.path.insert(0, parent_proj_dir)

            self.class_rules = []

            for _file in os.listdir(self.proj_dir):
                #Load each kv file in the directory
                _file = os.path.join(self.proj_dir, _file)
                if _file[_file.rfind('.'):] != '.kv':
                    continue

                f = open(_file, 'r')
                kv_string = f.read()
                f.close()
        
                #Remove all the 'app' lines
                for app_str in re.findall(r'.+app+.+', kv_string):
                    kv_string = kv_string.replace(app_str, 
                                                  app_str[:get_indentation(app_str)]
                                                  + '#' + app_str.lstrip())
                
                root_rule = Builder.load_string(kv_string)
                self.root_rule = None
                if root_rule:
                    self.root_rule = RootRule(root_rule.__class__.__name__, root_rule)

                #Get all the class_rules
                for class_str in re.findall(r'<+([\w_]+)>', kv_string):
                    class_rule = ClassRule(class_str)
                    class_rule.kv_file = _file
                    self.class_rules.append(class_rule)

            if os.path.exists(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME)):
                projdir_mtime = os.path.getmtime(self.proj_dir)

                f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'r')
                proj_str = f.read()
                f.close()

                projdir_time = proj_str[proj_str.find('<time>') + len('<time>'): 
                                        proj_str.find('</time>')]

                projdir_time = float(projdir_time.strip())
                if projdir_mtime <= projdir_time:
                    #Project Directory folder hasn't been modified,
                    #file list will remain same
                    self.file_list = []
                    un_modified_files = []
                    start_pos = proj_str.find('<files>')
                    end_pos = proj_str.find('</files>')
                    if start_pos != -1 and end_pos != -1:
                        start_pos = proj_str.find('<file>', start_pos)
                        end_pos1 = proj_str.find('</file>', start_pos)
                        while start_pos < end_pos and start_pos != -1:
                            _file = proj_str[start_pos + len('<file>'):end_pos1].strip()
                            self.file_list.append(_file)
                            if os.path.getmtime(_file) <= projdir_time:
                                un_modified_files.append(_file)
                            
                            start_pos = proj_str.find('<file>', end_pos1)
                            end_pos1 = proj_str.find('</file>', start_pos)
                        
                        for _file in self.file_list:
                            _dir = os.path.dirname(_file)
                            if _dir not in sys.path:
                                sys.path.insert(0, _dir)
                    
                    #Reload information for app
                    start_pos = proj_str.find('<app>')
                    end_pos = proj_str.find('</app>')
                    if start_pos != -1 and end_pos != -1:
                        self._app_class = proj_str[proj_str.find('<class>', start_pos)+len('<class>'):
                                                   proj_str.find('</class>', start_pos)].strip()
                        self._app_file = proj_str[proj_str.find('<file>', start_pos)+len('<file>'):
                                                   proj_str.find('</file>', start_pos)].strip()
                        f = open(self._app_file, 'r')
                        self._app_module = self._import_module(f.read(),
                                                           self._app_file)
                        f.close()

                    #Reload information for the files which haven't been modified
                    start_pos = proj_str.find('<classes>')
                    end_pos = proj_str.find('</classes>')

                    if start_pos != -1 and end_pos != -1:
                        while start_pos < end_pos and start_pos != -1:
                            start_pos = proj_str.find('<class>', start_pos) + len('<class>')
                            end_pos1 = proj_str.find('</class>', start_pos)
                            _file = proj_str[proj_str.find('<file>', start_pos) + len('<file>')
                                             :proj_str.find('</file>', start_pos)].strip()

                            if _file in un_modified_files:
                                #If _file is un modified then assign it to 
                                #class rule with _name
                                _name = proj_str[proj_str.find('<name>', start_pos) + len('<name>')
                                             :proj_str.find('</name>', start_pos)].strip()
                                
                                for _rule in self.class_rules:
                                    if _name == _rule.name:
                                        _rule.file = _file
                                        f = open(_file, 'r')
                                        _rule.module = self._import_module(f.read(),
                                                                           _file,
                                                                           _fromlist=[_name])
                                        f.close()
                                
                            start_pos = proj_str.find('<class>', start_pos)
                            end_pos1 = proj_str.find('</class>', start_pos)

            if self.file_list == []:
                 self.file_list = self._get_file_list(self.proj_dir)

            #Get all files corresponding to each class
            self._get_class_files()

            return True

        except:
            return False

    def save_project(self, proj_dir = ''):
        #To block ProjectWatcher from emitting event when project is saved
        self.proj_watcher.can_dispatch = False

        if self.new_project:
            #Create dir and copy new_proj.kv and new_proj.py to new directory
            if not os.path.exists(proj_dir):
                os.mkdir(proj_dir)
            
            kivy_designer_dir = os.path.join(os.path.expanduser('~'),
                                             '.kivy-designer')
            kivy_designer_new_proj_dir = os.path.join(kivy_designer_dir,
                                                      "new_proj")
            
            new_kv_file = os.path.join(proj_dir, "main.kv")
            old_kv_file = os.path.join(kivy_designer_new_proj_dir, "main.kv")
            shutil.copy(old_kv_file, new_kv_file)
            
            new_py_file = os.path.join(proj_dir, "main.py")
            old_py_file = os.path.join(kivy_designer_new_proj_dir, "main.py")
            shutil.copy(old_py_file, new_py_file)
            
            self.proj_dir = proj_dir
            if self.root_rule:
                self.root_rule.kv_file = new_kv_file
                self.root_rule.py_file = new_py_file

            if self.class_rules:
                self.class_rules[0].py_file = new_py_file
                self.class_rules[0].kv_file = new_kv_file
            
            self.new_project = False

        #For custom widgets copy py and kv file to project directory
        for widget in self.custom_widgets:
            custom_kv = os.path.join(self.proj_dir, 
                                     os.path.basename(self.kv_file))
            if not os.path.exists(custom_kv):
                shutil.copy(self.kv_file, custom_kv)
            
            custom_py = os.path.join(self.proj_dir, 
                                     os.path.basename(self.py_file))
            if not os.path.exists(custom_py):
                shutil.copy(self.py_file, custom_py)
        
        #Get the kv text from KVLangArea and write it to root rule's file
        root_str = self.get_root_str()
        f = open(self.root_rule.kv_file, 'r')
        _file_str = f.read()
        f.close()

        f = open(self.root_rule.kv_file, 'w')
        _file_str = _file_str.replace(root_str, App.get_running_app().root.kv_code_input.text)
        f.write(_file_str)
        f.close()
        
        #Allow Project Watcher to emit events
        Clock.schedule_once(self._allow_proj_watcher_dispatch, 1)
    
    def _allow_proj_watcher_dispatch(self, *args):
        self.proj_watcher.can_dispatch = True

    def _app_in_string(self, s):
        if 'runTouchApp' in s:
            self._app_class = 'runTouchApp'
            return True

        elif 'kivy.app' in s:
            for _class in re.findall(r'\bclass\b.+:', s):
                b_index1 = _class.find('(')
                b_index2 = _class.find(')')
                if _class[b_index1+1:b_index2].strip() == 'App':
                    self._app_class = _class[_class.find(' '):b_index1].strip()
                    return True

        return False

    def _get_class_files(self):
        if self._app_file == None:
            #Search for main.py
            for _file in self.file_list:
                if _file[_file.rfind('/')+1:] == 'main.py':
                    f = open(_file, 'r')
                    s = f.read()
                    f.close()
                    if self._app_in_string(s):
                        self._app_module = self._import_module(s, _file)
                        self._app_file = _file
            
            #Search for a file with app in its name
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
            if _rule.file == None:
                to_find.append(_rule)

        if self.root_rule:
            to_find.append(self.root_rule)

        #If cannot find due to above methods, search every file
        for _file in self.file_list:
            f = open(_file, 'r')
            s = f.read()
            f.close()
            if not self._app_file and self._app_in_string(s):
                self._app_module = self._import_module(s, _file)
                self._app_file = _file

            for _rule in to_find[:]:
                if _rule.file != None:
                    continue

                if re.search(r'\bclass\s*%s+.+:'%(_rule.name), s):
                    mod = self._import_module(s, _file, _fromlist=[_rule.name])
                    if hasattr(mod, _rule.name):
                        _rule.file = _file
                        to_find.remove(_rule)
                        _rule.module = mod

        #Cannot Find App, So, use default runTouchApp
        if not self._app_file:
            self._app_class = 'runTouchApp'

        #Root Widget may be in Factory not in file
        if self.root_rule:
            if hasattr(Factory, self.root_rule.name):
                to_find.remove(self.root_rule)

        #to_find should be empty, if not some class's files are not detected
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
        if run_pos != -1:
            run_pos -= 1
            while s[run_pos] != ' ':
                run_pos -= 1

            i = run_pos - 1
            while s[i] == ' ':
                i -= 1

        if i == run_pos - 1 or _r != []:
            if i == run_pos -1:
                s = s.replace('%s().run()'%self._app_class, '')

            module = imp.new_module('AppModule')
            exec s in module.__dict__
            sys.modules['AppModule'] = module
            return module

        module = __import__(
                _file[_file.rfind('/')+1:].replace('.py',''),
                fromlist=_fromlist)

        return module

    def cleanup(self):
        self.proj_watcher.stop_current_watching()
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
    
        if self.root_rule and hasattr(Factory, self.root_rule.name):
            Factory.unregister(self.root_rule.name)

        self._app_file = None
        self._app_class = None
        self._app_module = None
        self._app = None

        for _dir in self._dir_list:
            try:
                sys.path.remove(_dir)
            except:
                pass

        self.file_list = []
        self._dir_list = []
        self.class_rules = []
        self.list_comments = []
        self.custom_widgets = []

    def get_app(self):
        if not self._app_file or not self._app_class or not self._app_module:
            return None
        
        if self._app:
            return self._app
        
        for name, obj in inspect.getmembers(self._app_module):
            if inspect.isclass(obj) and self._app_class == name:
                self._app = obj()
                return self._app
        
        #if still couldn't get app, although that shouldn't happen
        return None
    
    def reload_root_widget_from_str(self, string):
        rules = []

        try:
            rules = Builder.match(self.root_rule.widget)
            for _rule in rules:
                for _tuple in Builder.rules[:]:
                    if _tuple[1] == _rule:
                        Builder.rules.remove(_tuple)
        except:
            pass
        
        if hasattr(Factory, self.root_rule.name):
            Factory.unregister(self.root_rule.name)
        
        root_widget = None
        #Remove all the 'app' lines
        for app_str in re.findall(r'.+app+.+', string):
            string = string.replace(app_str, 
                                    app_str[:get_indentation(app_str)]\
                                    + '#' + app_str.lstrip())
    
        root_widget = Builder.load_string(string)
        if not root_widget:
            root_widget = self.get_root_widget()
        
        if not root_widget:
            root_name = string[:string.find('\n')]
            root_name = root_widget.replace(':', '').replace('<','')
            root_name = root_widget.replace('>', '')
            root_widget = self.set_root_widget(root_name)           

        return root_widget
    
    def set_root_widget(self, root_name):
        root_widget = self.get_widget_of_class(root_name)
        self.root_rule = RootRule(root_name, root_widget)
        for _rule in self.class_rules:
            if _rule.name == root_name:
                self.root_rule.kv_file = _rule.kv_file
                self.root_rule.py_file = _rule.py_file
                break
        
        return root_widget
        
    def get_root_widget(self):
        if self._app_file == None:
            return None

        f = open(self._app_file, 'r')
        s = f.read()
        f.close()

        current_app = App.get_running_app()
        app = self.get_app()
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

        return root_widget
        
    def get_widget_of_class(self, class_name):
        self.root = getattr(Factory, class_name)()
        return self.root
    
    def record(self):
        if not os.path.exists(os.path.join(self.proj_dir, os.path.dirname(KV_PROJ_FILE_NAME))):
            os.mkdir(os.path.join(self.proj_dir, ".designer"))

        f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'w')
        f.close()
        
        f = open(os.path.join(self.proj_dir, KV_PROJ_FILE_NAME), 'w')
        proj_file_str = '<time>\n' + '    ' + str(time.time()) + '\n</time>\n'
        proj_file_str += '<files>\n'
        for _file in self.file_list:
            proj_file_str += '    <file>\n'
            proj_file_str += '        '+_file
            proj_file_str += '\n    </file>\n'

        proj_file_str += '</files>\n'
        
        proj_file_str += '<classes>\n'
        for _rule in self.class_rules:
            proj_file_str += '    <class>\n'
            proj_file_str += '         <name>\n'
            proj_file_str += '             '+_rule.name
            proj_file_str += '\n         </name>\n'
            proj_file_str += '         <file>\n'
            proj_file_str += '             '+_rule.file
            proj_file_str += '\n         </file>\n'
            proj_file_str += '\n    </class>\n'

        proj_file_str += '</classes>\n'
        
        if self._app_class and self._app_file:
            proj_file_str += '<app>\n'
            proj_file_str += '    <class>\n'
            proj_file_str += '         '+self._app_class
            proj_file_str += '\n    </class>\n'
            proj_file_str += '    <file>\n'
            proj_file_str += '         '+self._app_file
            proj_file_str += '\n    </file>\n'
            proj_file_str += '</app>\n'
        
        f.write(proj_file_str)

        f.close()
        
