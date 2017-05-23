import os
from io import open
from designer.components.buildozer_spec_editor import BuildozerSpecEditor
from designer.uix.confirmation_dialog import ConfirmationDialog
from designer.uix.py_code_input import PyScrollView
from designer.utils.utils import get_designer, show_message
from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    Clock,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    partial,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from kivy.uix.treeview import TreeViewLabel


SUPPORTED_EXT = ('.py', '.py2', '.kv', '.py3', '.txt', '.diff', )


class DesignerContent(FloatLayout):
    '''This class contains the body of the Kivy Designer. It contains,
       Project Tree and TabbedPanel.
    '''

    ui_creator = ObjectProperty(None)
    '''This property refers to the
        :class:`~designer.components.ui_creator.UICreator`
       instance. As there can only be one
       :data:`ui_creator` is a :class:`~kivy.properties.ObjectProperty`
    '''

    tree_toolbox_tab_panel = ObjectProperty(None)
    '''TabbedPanel containing Toolbox and Project Tree. Instance of
       :class:`~designer.components.designer_content.DesignerTabbedPanel`
    '''

    splitter_tree = ObjectProperty(None)
    '''Reference to the splitter parent of tree_toolbox_tab_panel.
       :data:`splitter_toolbox` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    toolbox = ObjectProperty(None)
    '''Reference to the :class:`~designer.components.toolbox.Toolbox` instance.
       :data:`toolbox` is an :class:`~kivy.properties.ObjectProperty`
    '''

    tree_view = ObjectProperty(None)
    '''This property refers to Project Tree. Project Tree displays project's
       py files under its parent directories. Clicking on any of the file will
       open it up for editing.
       :data:`tree_view` is a :class:`~kivy.properties.ObjectProperty`
    '''

    tab_pannel = ObjectProperty(None)
    '''This property refers to the instance of
       :class:`~designer.components.designer_content.DesignerTabbedPanel`.
       :data:`tab_pannel` is a :class:`~kivy.properties.ObjectProperty`
    '''

    in_find = BooleanProperty(False)
    '''This property indicates if the find menu is activated
        :data:`in_find` is a :class:`~kivy.properties.BooleanProperty` and
        defaults to False
    '''

    current_codeinput = ObjectProperty(None, allownone=True)
    '''Instance of the current PythonCodeInput
        :data:`current_codeinput` is a :class:`~kivy.properties.ObjectProperty`
        and defaults to None
    '''

    find_tool = ObjectProperty(None)
    '''Instance of  :class:`~designer.uix.code_find.CodeInputFind`.
        :data:`find_tool` is a :class:`~kivy.properties.ObjectProperty`
        and defaults to None
    '''

    project = ObjectProperty(None)
    '''Instance of
        :class:`~designer.core.project_manager.Project`
        with the current opened project.
        :data:`project` is a :class:`~kivy.properties.ObjectProperty`
        and defaults to None
    '''

    def __init__(self, **kwargs):
        super(DesignerContent, self).__init__(**kwargs)
        self.find_tool.bind(on_close=partial(self.show_findmenu, False))
        self.find_tool.bind(on_next=self.find_tool_next)
        self.find_tool.bind(on_prev=self.find_tool_prev)
        self.focus_code_input = Clock.create_trigger(self._focus_input)

    def update_tree_view(self, project):
        '''This function is used to insert all the py files detected.
           as a node in the Project Tree.
           :param project: instance of the current project
        '''
        self.project = project

        # Fill nodes with file and directories
        self._root_node = self.tree_view.root
        self.clear_tree_view()

        for _file in sorted(project.get_files()):
            self.add_file_to_tree_view(_file)

        self.tree_view.root_options = dict(
            text=os.path.basename(self.project.path))

    def clear_tree_view(self):
        '''
        Clear the TreeView
        '''
        temp = list(self.tree_view.iterate_all_nodes())
        for node in temp:
            self.tree_view.remove_node(node)

    def add_file_to_tree_view(self, _file):
        '''This function is used to insert project files given by it's path
        argument _file. It will also insert any directory node if not present.
        :param _file: path of the file to be inserted
        '''

        self.tree_view.root_options = dict(text='')
        dirname = os.path.dirname(_file)
        dirname = dirname.replace(self.project.path, '')
        # The way os.path.dirname works, there will never be '/' at the end
        # of a directory. So, there will always be '/' at the starting
        # of 'dirname' variable after removing proj_dir

        # This algorithm first breaks path into its components
        # and creates a list of these components.
        _dirname = dirname
        _basename = 'a'
        list_path_components = []
        while _basename != '':
            _split = os.path.split(_dirname)
            _dirname = _split[0]
            _basename = _split[1]
            list_path_components.insert(0, _split[1])

        if list_path_components[0] == '':
            del list_path_components[0]

        # Then it traverses from root_node to its children searching from
        # each component in the path. If it doesn't find any component
        # related with node then it creates it.
        node = self._root_node
        while list_path_components != []:
            found = False
            for _node in node.nodes:
                if _node.text == list_path_components[0]:
                    node = _node
                    found = True
                    break

            if not found:
                for component in list_path_components:
                    _node = TreeViewLabel(text=component)
                    self.tree_view.add_node(_node, node)
                    node = _node
                list_path_components = []
            else:
                del list_path_components[0]

        # Finally add file_node with node as parent.
        file_node = TreeViewLabel(text=os.path.basename(_file))
        file_node.bind(on_touch_down=self._file_node_clicked)
        self.tree_view.add_node(file_node, node)

    def _file_node_clicked(self, instance, touch):
        '''This is emmited whenever any file node of Project Tree is
           clicked. This will open up a tab in DesignerTabbedPanel, for
           editing that py file.
        '''

        # Travel upwards and find the path of instance clicked
        path = instance.text
        parent = instance.parent_node
        while parent != self._root_node:
            _path = parent.text
            path = os.path.join(_path, path)
            parent = parent.parent_node

        full_path = os.path.join(self.project.path, path)
        if os.path.basename(full_path) == 'buildozer.spec':
            self.tab_pannel.show_buildozer_spec_editor(self.project)
        else:
            ext = path[path.rfind('.'):]
            if ext not in SUPPORTED_EXT:
                show_message('This extension is not yet supported', 5, 'error')
                return
            if ext == '.kv':
                self.ui_creator.playground.load_widget_from_file(full_path)
                self.tab_pannel.switch_to(self.tab_pannel.tab_list[-1])
            else:
                self.tab_pannel.open_file(full_path, path)

    def show_findmenu(self, visible, *args):
        '''Makes find menu visible/invisible
        '''
        self.in_find = visible
        if visible:
            Clock.schedule_once(self._focus_find)

    def _focus_find(self, *args):
        '''Focus on the find tool
        '''
        self.find_tool.txt_query.focus = True

    def on_current_tab(self, tabbed_panel, *args):
        '''Event handler to tab selection changes
        '''
        self.show_findmenu(False)
        Clock.schedule_once(partial(self._selected_content, tabbed_panel))

    def _selected_content(self, tabbed_panel, *args):
        '''Called after updating tab content
        '''
        if not tabbed_panel.content.children:
            return
        content = tabbed_panel.content.children[0]

        if isinstance(content, PyScrollView):
            self.current_codeinput = content.code_input
        else:
            self.current_codeinput = None

    def find_tool_prev(self, instance, *args):
        if self.current_codeinput:
            self.current_codeinput.focus = True
            self.current_codeinput.find_prev(instance.query,
                                             instance.use_regex,
                                             instance.case_sensitive)

    def find_tool_next(self, instance, *args):
        if self.current_codeinput:
            self.current_codeinput.focus = True
            self.current_codeinput.find_next(instance.query,
                                             instance.use_regex,
                                             instance.case_sensitive)

    def _focus_input(self, *args):
        self.current_codeinput.focus = True


class DesignerTabbedPanel(TabbedPanel):
    '''DesignerTabbedPanel is used to display files opened up in tabs with
       :class:`~designer.components.ui_creator.UICreator`
       Tab as a special one containing all features to edit the UI.
    '''

    def open_file(self, path, rel_path, switch_to=True):
        '''This will open file for editing in the DesignerTabbedPanel.
        :param switch_to: if should switch to the new tab
        :param rel_path: relative file path
        :param path: absolute file path to open
        '''
        for i, tab_item in enumerate(self.tab_list):
            if hasattr(tab_item, 'rel_path') and tab_item.rel_path == rel_path:
                # self.switch_to(self.tab_list[len(self.tab_list) - i - 2])
                self.switch_to(tab_item)
                return

        panel_item = DesignerCloseableTab(title=os.path.basename(path))
        panel_item.bind(on_close=self.on_close_tab)
        f = open(path, 'r', encoding='utf-8')
        scroll = PyScrollView()
        _py_code_input = scroll.code_input
        _py_code_input.text = f.read()
        _py_code_input.path = path
        _py_code_input.bind(
            on_show_edit=App.get_running_app().root.on_show_edit)
        _py_code_input.bind(saved=panel_item.on_tab_content_saved)
        _py_code_input.bind(error=panel_item.on_tab_content_error)
        f.close()

        d = get_designer()
        if _py_code_input not in d.code_inputs:
            d.code_inputs.append(_py_code_input)

        panel_item.content = scroll
        panel_item.rel_path = rel_path
        self.add_widget(panel_item)
        if switch_to:
            self.switch_to(self.tab_list[0])

    def show_buildozer_spec_editor(self, project):
        '''Loads the buildozer.spec file and adds a new tab with the
        Buildozer Spec Editor
        :param project: instance of the current project
        '''
        for i, child in enumerate(self.tab_list):
            if isinstance(child.content, BuildozerSpecEditor):
                self.switch_to(child)
                return child

        spec_editor = get_designer().spec_editor
        if spec_editor.SPEC_PATH != \
                os.path.join(project.path, 'buildozer.spec'):
            spec_editor.load_settings(project.path)

        panel_spec_item = DesignerCloseableTab(title="Spec Editor")
        panel_spec_item.bind(on_close=self.on_close_tab)
        panel_spec_item.content = spec_editor
        panel_spec_item.rel_path = 'buildozer.spec'
        self.add_widget(panel_spec_item)
        self.switch_to(self.tab_list[0])

    def on_close_tab(self, instance, *args):
        '''Event handler to close icon
        :param instance: tab instance
        '''
        d = get_designer()
        if d.popup:
            return False

        self.switch_to(instance)
        if instance.has_modification:
            # show a dialog to ask if can close
            confirm_dlg = ConfirmationDialog(
                    'All unsaved changes will be lost.\n'
                    'Do you want to continue?')
            popup = Popup(
                    title='New',
                    content=confirm_dlg,
                    size_hint=(None, None),
                    size=('200pt', '150pt'),
                    auto_dismiss=False)

            def close_tab(*args):
                d.close_popup()
                self._perform_close_tab(instance)

            confirm_dlg.bind(
                    on_ok=close_tab,
                    on_cancel=d.close_popup)
            popup.open()
            d.popup = popup
        else:
            Clock.schedule_once(partial(self._perform_close_tab, instance))

    def _perform_close_tab(self, tab, *args):
        # remove code_input from list
        if hasattr(tab.content, 'code_input'):
            code = tab.content.code_input
            d = get_designer()
            if code in d.code_inputs:
                d.code_inputs.remove(code)
        # remove tab
        self.remove_widget(tab)
        if self.tab_list:
            self.switch_to(self.tab_list[0])

    def cleanup(self):
        '''Remove all open tabs
        '''
        for child in self.tab_list[:-1]:
            self.remove_widget(child)
        self.switch_to(self.tab_list[0])


class DesignerTabbedPanelItem(TabbedPanelItem):
    pass


class DesignerCloseableTab(TabbedPanelHeader):
    '''Custom TabbedPanelHeader with close button
    '''

    has_modification = BooleanProperty(False)
    '''Indicates if this tab has unsaved content
        :data:`has_modification` is a :class:`~kivy.properties.BooleanProperty`
    '''

    has_error = BooleanProperty(False)
    '''Indicates if this tab has error
        :data:`has_error` is a :class:`~kivy.properties.BooleanProperty`
    '''

    style = OptionProperty('default',
                           options=['default', 'unsaved', 'error'])
    '''Available tab custom styles
    :data:`style` is a :class:`~kivy.properties.OptionProperty`
    '''

    title = StringProperty('')
    '''Tab header title
    :data:`title` is a :class:`~kivy.properties.StringProperty`
    '''

    rel_path = StringProperty('')
    '''Relative path of file
    :data:`rel_path` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_close', )

    def on_close(self, *args):
        pass

    def on_style(self, instance, style, *args):
        '''Update the tab style
        '''
        if style == 'default':
            self.text = self.title
        elif style == 'unsaved':
            self.text = '[i]%s[i]' % self.title
        elif style == 'error':
            self.text = '[color=#e51919]%s[/color]' % self.title

    def on_tab_content_saved(self, instance, value, *args):
        '''Callback to the tab content saved modifications.
        value is True or False, indicating if status of the file
        '''
        self.has_modification = not value

        # if the file contains an error, keep showing it
        if self.style == 'error':
            return

        self.style = 'default' if value else 'unsaved'

    def on_tab_content_error(self, has_error, *args):
        '''Callback to the tab content error status
        has_error is True or False, indicating the error
        '''

        if has_error:
            self.style = 'error'
        elif self.style == 'error':
            self.style = 'default'

    def on_text(self, *args):
        '''updates the tab width when it has a new title
        '''
        def update_width(*args):
            self.width = min(self.texture_size[0] + 40, 200)
        Clock.schedule_once(update_width)
