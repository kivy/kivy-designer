import re

from kivy.uix.codeinput import CodeInput
from kivy.properties import BooleanProperty, StringProperty,\
    NumericProperty, OptionProperty, ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelContent, \
    TabbedPanel, TabbedPanelHeader

from designer.helper_functions import get_indent_str, get_line_end_pos,\
    get_line_start_pos, get_indent_level, get_indentation
from designer.uix.designer_code_input import DesignerCodeInput


class KVLangAreaScroll(ScrollView):
    '''KVLangAreaScroll used as a :class:`~kivy.scrollview.ScrollView`
       for adding :class:`~designer.uix.kv_lang_area.KVLangArea`.
    '''

    kv_lang_area = ObjectProperty(None)
    '''(internal) Reference to the
        :class:`~designer.uix.kv_lang_area.KVLangArea`.
       :data:`kv_lang_area` is a :class:`~kivy.properties.ObjectProperty`
    '''

    line_number = ObjectProperty(None)
    '''(internal) Text Input to display line numbers
       :data:`line_number` is a :class:`~kivy.properties.ObjectProperty`
    '''

    show_line_number = BooleanProperty(True)
    '''Display line number on left
       :data:`show_line_number` is a :class:`~kivy.properties.BooleanProperty`
       and defaults to True
    '''

    def __init__(self, **kwargs):
        super(KVLangAreaScroll, self).__init__(**kwargs)

        self._max_num_of_lines = 0
        # identify if the line number binding is already running
        self._line_number_handled = False

    def on_width(self, *args):
        if not self._line_number_handled:
            if self.show_line_number:
                self.kv_lang_area.bind(_lines=self.on_lines_changed)
            else:
                self.line_number.parent.remove_widget(self.line_number)
            self._line_number_handled = True

    def on_lines_changed(self, *args):
        '''Event handler that listen the line modifications to update
        line_number
        '''
        n = len(self.kv_lang_area._lines)
        if n > self._max_num_of_lines:
            self.update_line_number(self._max_num_of_lines, n)

    def update_line_number(self, old, new):
        '''Analyze the difference between old and new number of lines
        to update the text input
        '''
        self._max_num_of_lines = new
        self.line_number.text += \
                    '\n'.join([str(i) for i in range(old + 1, new + 1)]) + '\n'
        self.line_number.width = self.line_number._label_cached.get_extents(
            str(self._max_num_of_lines))[0] + (self.line_number.padding[0] * 2)
        # not removing lines, as long as extra lines will not be visible


class KVLangArea(DesignerCodeInput):
    '''KVLangArea is the CodeInput for editing kv lang. It emits on_show_edit
       event, when clicked.
    '''

    have_error = BooleanProperty(False)
    '''This property specifies whether KVLangArea has encountered an error
       in reload in the edited text by user or not.
       :data:`can_place` is a :class:`~kivy.properties.BooleanProperty`
    '''

    _reload = BooleanProperty(False)
    '''Specifies whether to reload kv or not.
       :data:`_reload` is a :class:`~kivy.properties.BooleanProperty`
    '''

    reload_kv = BooleanProperty(True)

    playground = ObjectProperty()
    '''Reference to :class:`~designer.playground.Playground`
       :data:`playground` is a :class:`~kivy.properties.ObjectProperty`
    '''

    project_loader = ObjectProperty()
    '''Reference to :class:`~designer.project_loader.ProjectLoader`
       :data:`project_loader` is a :class:`~kivy.properties.ObjectProperty`
    '''
    statusbar = ObjectProperty()

    def __init__(self, **kwargs):
        super(KVLangArea, self).__init__(**kwargs)
        self._reload_trigger = Clock.create_trigger(self.func_reload_kv, 1)
        self.bind(text=self._reload_trigger)

    def _get_widget_path(self, widget):
        '''To get path of a widget, path of a widget is a list containing
           the index of it in its parent's children list. For example,
           Widget1:
               Widget2:
               Widget3:
                   Widget4:

           path of Widget4 is [0, 1, 0]
        '''

        path_to_widget = []
        _widget = widget
        while _widget and _widget != self.playground.sandbox.children[0]:
            if not _widget.parent:
                break

            if isinstance(_widget.parent.parent, Carousel):
                parent = _widget.parent
                try:
                    place = parent.parent.slides.index(_widget)

                except ValueError:
                    place = 0

                path_to_widget.append(place)
                _widget = _widget.parent.parent

            elif isinstance(_widget.parent, ScreenManager):
                parent = _widget.parent
                try:
                    place = parent.screens.index(_widget)

                except ValueError:
                    place = 0

                path_to_widget.append(place)
                _widget = _widget.parent

            elif isinstance(_widget.parent, TabbedPanelContent):
                tab_panel = _widget.parent.parent
                path_to_widget.append(0)
                place = len(tab_panel.tab_list) - \
                    tab_panel.tab_list.index(tab_panel.current_tab) - 1

                path_to_widget.append(place)
                _widget = tab_panel

            elif isinstance(_widget, TabbedPanelHeader):
                tab_panel = _widget.parent
                while tab_panel and not isinstance(tab_panel, TabbedPanel):
                    tab_panel = tab_panel.parent

                place = len(tab_panel.tab_list) - \
                    tab_panel.tab_list.index(_widget) - 1

                path_to_widget.append(place)
                _widget = tab_panel

            else:
                place = len(_widget.parent.children) - \
                    _widget.parent.children.index(_widget) - 1

                path_to_widget.append(place)
                _widget = _widget.parent

        return path_to_widget

    def shift_widget(self, widget, from_index):
        '''This function will shift widget's kv str from one position
           to another.
        '''
        self._reload = False

        path = self._get_widget_path(widget)
        path.reverse()
        prev_path = [x for x in path]
        prev_path[-1] = len(widget.parent.children) - from_index - 1
        start_pos, end_pos = self.get_widget_text_pos_from_kv(
            widget, widget.parent, path_to_widget=prev_path)

        widget_text = self.text[start_pos:end_pos]

        if widget.parent.children.index(widget) == 0:
            self.text = self.text[:start_pos] + self.text[end_pos:]
            self.add_widget_to_parent(widget, widget.parent,
                                      kv_str=widget_text)

        else:
            self.text = self.text[:start_pos] + self.text[end_pos:]
            text = re.sub(r'#.+', '', self.text)
            lines = text.splitlines()
            total_lines = len(lines)
            root_lineno = 0
            root_name = self.project_loader.root_rule.name
            for lineno, line in enumerate(lines):
                pos = line.find(root_name)
                if pos != -1 and get_indentation(line) == 0:
                    root_lineno = lineno
                    break

            next_widget_path = path
            lineno = self._find_widget_place(next_widget_path, lines,
                                             total_lines,
                                             root_lineno + 1)

            self.cursor = (0, lineno)
            self.insert_text(widget_text + '\n')

    def add_widget_to_parent(self, widget, target, kv_str=''):
        '''This function is called when widget is added to target.
           It will search for line where parent is defined in text and will add
           widget there.
        '''
        text = re.sub(r'#.+', '', self.text)
        lines = text.splitlines()
        total_lines = len(lines)
        if total_lines == 0:
            return

        self._reload = False

        # If target is not none then widget is not root widget
        if target:
            path_to_widget = self._get_widget_path(target)

            path_to_widget.reverse()

            root_lineno = 0
            root_name = self.project_loader.root_rule.name
            for lineno, line in enumerate(lines):
                pos = line.find(root_name)
                if pos != -1 and get_indentation(line) == 0:
                    root_lineno = lineno
                    break

            parent_lineno = self._find_widget_place(path_to_widget, lines,
                                                    total_lines,
                                                    root_lineno + 1)

            if parent_lineno >= total_lines:
                return

            # Get text of parents line
            parent_line = lines[parent_lineno]
            if not parent_line.strip():
                return

            insert_after_line = -1

            if parent_line.find(':') == -1:
                # If parent_line doesn't contain ':' then insert it
                # Also insert widget's rule after its properties
                insert_after_line = parent_lineno
                _line = 0
                _line_pos = -1
                _line_pos = self.text.find('\n', _line_pos + 1)

                while _line <= insert_after_line:
                    _line_pos = self.text.find('\n', _line_pos + 1)
                    _line += 1

                self.text = self.text[:_line_pos] + ':' + self.text[_line_pos:]
                indent = len(parent_line) - len(parent_line.lstrip())

            else:
                # If ':' in parent_line then,
                # find a place to insert widget's rule
                indent = len(parent_line) - len(parent_line.lstrip())
                lineno = parent_lineno
                _indent = indent + 1
                line = parent_line
                while (line.strip() == '' or _indent > indent):
                    lineno += 1
                    if lineno >= total_lines:
                        break
                    line = lines[lineno]
                    _indent = len(line) - len(line.lstrip())

                insert_after_line = lineno - 1
                line = lines[insert_after_line]
                while line.strip() == '':
                    insert_after_line -= 1
                    line = lines[insert_after_line]

            to_insert = ''
            if kv_str == '':
                to_insert = type(widget).__name__ + ':'
            else:
                to_insert = kv_str.strip()

            if insert_after_line == total_lines - 1:
                # if inserting at the last line
                _line_pos = len(self.text) - 1

                self.text = self.text[:_line_pos + 1] + '\n' + \
                    get_indent_str(indent + 4) + to_insert
            else:
                # inserting somewhere else
                insert_after_line -= 1
                _line = 0
                _line_pos = -1
                _line_pos = self.text.find('\n', _line_pos + 1)
                while _line <= insert_after_line:
                    _line_pos = self.text.find('\n', _line_pos + 1)
                    _line += 1

                self.text = self.text[:_line_pos] + '\n' + \
                    get_indent_str(indent + 4) + to_insert + \
                    self.text[_line_pos:]

        else:
            # widget is a root widget
            parent_lineno = 0
            self.cursor = (0, 0)
            type_name = type(widget).__name__
            is_class = False
            for rule in self.project_loader.class_rules:
                if rule.name == type_name:
                    is_class = True
                    break

            if not is_class:
                self.insert_text(type_name + ':\n')

            self.project_loader.set_root_widget(type_name, widget)

    def get_widget_text_pos_from_kv(self, widget, parent, path_to_widget=[]):
        '''To get start and end pos of widget's rule in kv text
        '''

        if not path_to_widget:
            path_to_widget = self._get_widget_path(widget)
            path_to_widget.reverse()

        # Go to widget's rule's line and determines all its rule's
        # and it's child if any. Then delete them
        text = re.sub(r'#.+', '', self.text)
        lines = text.splitlines()
        total_lines = len(lines)
        root_lineno = 0
        root_name = self.project_loader.root_rule.name
        for lineno, line in enumerate(lines):
            pos = line.find(root_name)
            if pos != -1 and get_indentation(line) == 0:
                root_lineno = lineno
                break

        widget_lineno = self._find_widget_place(path_to_widget, lines,
                                                total_lines, root_lineno + 1)
        widget_line = lines[widget_lineno]
        indent = len(widget_line) - len(widget_line.lstrip())
        lineno = widget_lineno
        _indent = indent + 1
        line = widget_line
        while (line.strip() == '' or _indent > indent):
            lineno += 1
            if lineno >= total_lines:
                break
            line = lines[lineno]
            _indent = len(line) - len(line.lstrip())

        delete_until_line = lineno - 1
        line = lines[delete_until_line]
        while line.strip() == '':
            delete_until_line -= 1
            line = lines[delete_until_line]

        widget_line_pos = get_line_start_pos(self.text, widget_lineno)
        delete_until_line_pos = -1
        if delete_until_line == total_lines - 1:
            delete_until_line_pos = len(self.text)
        else:
            delete_until_line_pos = get_line_end_pos(self.text,
                                                     delete_until_line)

        self._reload = False

        return widget_line_pos, delete_until_line_pos

    def get_widget_text_from_kv(self, widget, parent, path=[]):
        '''This function will get a widget's text from KVLangArea's text given
           its parent.
        '''

        start_pos, end_pos = self.get_widget_text_pos_from_kv(
            widget, parent, path_to_widget=path)
        text = self.text[start_pos:end_pos]

        return text

    def remove_widget_from_parent(self, widget, parent):
        '''This function is called when widget is removed from parent.
           It will delete widget's rule from parent's rule
        '''
        if self.text == '':
            return

        self._reload = False

        delete_from_kv = False
        if type(widget).__name__ == self.project_loader.root_rule.name:
            # If root widget is being deleted then delete its rule only if
            # it is not in class rules.

            if not self.project_loader.is_root_a_class_rule():
                delete_from_kv = True

        else:
            delete_from_kv = True

        if delete_from_kv:
            start_pos, end_pos = self.get_widget_text_pos_from_kv(widget,
                                                                  parent)
            text = self.text[start_pos:end_pos]
            self.text = self.text[:start_pos] + self.text[end_pos:]
            return text

    def _get_widget_from_path(self, path):
        '''This function is used to get widget given its path
        '''

        if not self.playground.root:
            return None

        if len(path) == 0:
            return None

        root = self.playground.root
        path_index = 0
        widget = root
        path_length = len(path)

        while widget.children != [] and path_index < path_length:
            try:
                widget = widget.children[len(widget.children) -
                                         1 - path[path_index]]
            except IndexError:
                widget = widget.children[0]

            path_index += 1

        return widget

    def func_reload_kv(self, *args):
        if not self.reload_kv:
            return

        if self.text == '':
            return

        if not self._reload:
            self._reload = True
            return

        statusbar = self.statusbar

        playground = self.playground
        project_loader = self.project_loader

        try:
            widget = project_loader.reload_from_str(self.text)

            if widget:
                playground.remove_widget_from_parent(playground.root,
                                                     None, from_kv=True)
                playground.add_widget_to_parent(widget, None, from_kv=True)

            statusbar.show_message("")
            self.have_error = False

        except:
            self.have_error = True
            statusbar.show_message("Cannot reload from text")

    def _get_widget_path_at_line(self, lineno, root_lineno=0):
        '''To get widget path of widget at line
        '''

        if self.text == '':
            return []

        text = self.text
        # Remove all comments
        text = re.sub(r'#.+', '', text)

        lines = text.splitlines()
        line = lines[lineno]

        # Search for the line containing widget's name
        _lineno = lineno

        while line.find(':') != -1 and \
                line.strip().find(':') != len(line.strip()) - 1:
            lineno -= 1
            line = lines[lineno]

        path = []
        child_count = 0
        # From current line go above and
        # fill number of children above widget's rule
        while _lineno >= root_lineno and lines[_lineno].strip() != "" and \
                get_indentation(lines[lineno]) != 0:
            _lineno = lineno - 1
            diff_indent = get_indentation(lines[lineno]) - \
                get_indentation(lines[_lineno])

            while _lineno >= root_lineno and (lines[_lineno].strip() == ''
                                              or diff_indent <= 0):
                if lines[_lineno].strip() != '' and diff_indent == 0 and \
                    'canvas' not in lines[_lineno] and \
                        (lines[_lineno].find(':') == -1 or
                         lines[_lineno].find(':') ==
                         len(lines[_lineno].rstrip()) - 1):
                    child_count += 1

                _lineno -= 1
                diff_indent = get_indentation(lines[lineno]) - \
                    get_indentation(lines[_lineno])

            lineno = _lineno

            if _lineno > root_lineno:
                _lineno += 1

            if 'canvas' not in lines[_lineno] and \
                    lines[_lineno].strip().find(':') == \
                    len(lines[_lineno].strip()) - 1:

                path.insert(0, child_count)
                child_count = 0

        return path

    def get_property_value(self, widget, prop):
        self._reload = False
        if prop[:3] != 'on_' and \
                not isinstance(widget.properties()[prop], StringProperty) and\
                value == '':
            return

        path_to_widget = self._get_widget_path(widget)
        path_to_widget.reverse()

        # Go to the line where widget is declared
        lines = re.sub(r'#.+', '', self.text).splitlines()
        total_lines = len(lines)

        root_name = self.project_loader.root_rule.name
        total_lines = len(lines)
        root_lineno = 0
        for lineno, line in enumerate(lines):
            pos = line.find(root_name)
            if pos != -1 and get_indentation(line) == 0:
                root_lineno = lineno
                break

        widget_lineno = self._find_widget_place(path_to_widget, lines,
                                                total_lines, root_lineno + 1)
        widget_line = lines[widget_lineno]
        indent = get_indentation(widget_line)
        prop_found = False

        # Else find if property has already been declared with a value
        lineno = widget_lineno + 1
        # But if widget line is the last line in the text
        if lineno < total_lines:
            line = lines[lineno]
            _indent = get_indentation(line)
            colon_pos = -1
            while lineno < total_lines and (line.strip() == '' or
                                            _indent > indent):
                line = lines[lineno]
                _indent = get_indentation(line)
                if line.strip() != '':
                    colon_pos = line.find(':')
                    if colon_pos == -1:
                        break

                    if colon_pos == len(line.rstrip()) - 1:
                        break

                    if prop == line[:colon_pos].strip():
                        prop_found = True
                        break

                lineno += 1

        if prop_found:
            # if property found then change its value
            _pos_prop_value = get_line_start_pos(self.text, lineno) + \
                colon_pos + 2
            if lineno == total_lines - 1:
                _line_end_pos = len(self.text)
            else:
                _line_end_pos = get_line_end_pos(self.text, lineno)

            return self.text[_pos_prop_value:_line_end_pos]

        return ""

    def set_event_handler(self, widget, prop, value):
        self._reload = False

        path_to_widget = self._get_widget_path(widget)
        path_to_widget.reverse()

        # Go to the line where widget is declared
        lines = re.sub(r'#.+', '', self.text).splitlines()
        total_lines = len(lines)

        root_name = self.project_loader.root_rule.name
        total_lines = len(lines)
        root_lineno = 0
        for lineno, line in enumerate(lines):
            pos = line.find(root_name)
            if pos != -1 and get_indentation(line) == 0:
                root_lineno = lineno
                break

        widget_lineno = self._find_widget_place(path_to_widget, lines,
                                                total_lines, root_lineno + 1)

        widget_line = lines[widget_lineno]
        indent = get_indentation(widget_line)
        prop_found = False

        if not widget_line.strip():
            return

        if ':' not in widget_line:
            # If cannot find ':' then insert it
            self.cursor = (len(lines[widget_lineno]), widget_lineno)
            lines[widget_lineno] += ':'
            self.insert_text(':')

        else:
            # Else find if property has already been declared with a value
            lineno = widget_lineno + 1
            # But if widget line is the last line in the text
            if lineno < total_lines:
                line = lines[lineno]
                _indent = get_indentation(line)
                colon_pos = -1
                while lineno < total_lines and (line.strip() == '' or
                                                _indent > indent):
                    line = lines[lineno]
                    _indent = get_indentation(line)
                    if line.strip() != '':
                        colon_pos = line.find(':')
                        if colon_pos == -1:
                            break

                        if colon_pos == len(line.rstrip()) - 1:
                            break

                        if prop == line[:colon_pos].strip():
                            prop_found = True
                            break

                    lineno += 1

        if prop_found:
            if lineno == total_lines - 1:
                _line_end_pos = len(self.text)
            else:
                _line_end_pos = get_line_end_pos(self.text, lineno)

            if value != '':
                # if property found then change its value
                _pos_prop_value = get_line_start_pos(self.text, lineno) + \
                    colon_pos + 2
                self.text = self.text[:_pos_prop_value] + ' ' + value + \
                    self.text[_line_end_pos:]

                self.cursor = (0, lineno)

            else:
                _line_start_pos = get_line_start_pos(self.text, widget_lineno)
                self.text = \
                    self.text[:get_line_start_pos(self.text, lineno)] + \
                    self.text[_line_end_pos:]

        elif value != '':
            # if not found then add property after the widgets line
            _line_end_pos = get_line_end_pos(self.text, widget_lineno)

            indent_str = '\n'
            for i in range(indent + 4):
                indent_str += ' '

            self.cursor = (len(lines[widget_lineno]), widget_lineno)
            self.insert_text(indent_str + prop + ': ' + str(value))

    def set_property_value(self, widget, prop, value, proptype):
        '''To find and change the value of property of widget rule in text
        '''

        # Do not add property if value is empty and
        # property is not a string property

        self._reload = False
        if not isinstance(widget.properties()[prop], StringProperty) and\
                value == '':
            return

        path_to_widget = self._get_widget_path(widget)
        path_to_widget.reverse()

        # Go to the line where widget is declared
        lines = re.sub(r'#.+', '', self.text.rstrip()).splitlines()
        total_lines = len(lines)

        root_name = self.project_loader.root_rule.name
        total_lines = len(lines)
        root_lineno = 0
        for lineno, line in enumerate(lines):
            pos = line.find(root_name)
            if pos != -1 and get_indentation(line) == 0:
                root_lineno = lineno
                break

        widget_lineno = self._find_widget_place(path_to_widget, lines,
                                                total_lines, root_lineno + 1)
        widget_line = lines[widget_lineno]
        if not widget_line.strip():
            return

        indent = get_indentation(widget_line)
        prop_found = False

        if ':' not in widget_line:
            # If cannot find ':' then insert it
            self.cursor = (len(lines[widget_lineno]), widget_lineno)
            lines[widget_lineno] += ':'
            self.insert_text(':')

        else:
            # Else find if property has already been declared with a value
            lineno = widget_lineno + 1
            # But if widget line is the last line in the text
            if lineno < total_lines:
                line = lines[lineno]
                _indent = get_indentation(line)
                colon_pos = -1
                while lineno < total_lines and (line.strip() == '' or
                                                _indent > indent):
                    line = lines[lineno]
                    _indent = get_indentation(line)
                    if line.strip() != '':
                        colon_pos = line.find(':')
                        if colon_pos == -1:
                            break

                        if colon_pos == len(line.rstrip()) - 1:
                            break

                        if prop == line[:colon_pos].strip():
                            prop_found = True
                            break

                    lineno += 1

        if prop_found:
            # if property found then change its value
            _pos_prop_value = get_line_start_pos(self.text, lineno) + \
                colon_pos + 2
            if lineno == total_lines - 1:
                _line_end_pos = len(self.text)
            else:
                _line_end_pos = get_line_end_pos(self.text, lineno)

            if proptype == 'StringProperty':
                value = "'{}'".format(value.replace("'", "\\'"))

            self.text = self.text[:_pos_prop_value] + ' ' + str(value) + \
                self.text[_line_end_pos:]

            self.cursor = (0, lineno)

        else:
            # if not found then add property after the widgets line
            _line_start_pos = get_line_start_pos(self.text, widget_lineno)
            _line_end_pos = get_line_end_pos(self.text, widget_lineno)
            if proptype == 'StringProperty':
                value = "'{}'".format(value.replace("'", "\\'"))

            indent_str = '\n'
            for i in range(indent + 4):
                indent_str += ' '

            self.cursor = (len(lines[widget_lineno]), widget_lineno)
            self.insert_text(indent_str + prop + ': ' + str(value))

    def _find_widget_place(self, path, lines, total_lines, lineno, indent=4):
        '''To find the line where widget is declared according to path
        '''

        child_count = 0
        path_index = 1
        path_length = len(path)
        # From starting line go down to find the widget's rule according to path
        while lineno < total_lines and path_index < path_length:
            line = lines[lineno]
            _indent = get_indentation(line)
            colon_pos = line.find(':')
            if _indent == indent and line.strip() != '':
                if colon_pos != -1:
                    line = line.rstrip()
                    if colon_pos == len(line) - 1 and 'canvas' not in line:
                        line = line[:colon_pos].lstrip()
                        if child_count == path[path_index]:
                            path_index += 1
                            indent = _indent + 4
                            child_count = 0
                        else:
                            child_count += 1
                else:
                    child_count += 1

            lineno += 1

        return lineno - 1
