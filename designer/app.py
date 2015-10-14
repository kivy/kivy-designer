import webbrowser

from designer.designer_tools import DesignerTools
from designer.input_dialog import InputDialog
from designer.profile_settings import ProfileSettings
from designer.profiler import Profiler
from designer.uix.modules_contview import ModulesContView

__all__ = ('DesignerApp', )

import kivy
import time
import os
import shutil
import traceback

kivy.require('1.9.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.layout import Layout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, \
    partial
from kivy.clock import Clock
from kivy.uix import actionbar
from kivy.garden.filebrowser import FileBrowser
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.lang import Builder
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config
from kivy.base import ExceptionHandler, ExceptionManager

import designer
from designer.uix.actioncheckbutton import ActionCheckButton
from designer.playground import PlaygroundDragElement
from designer.common import widgets
from designer.uix.editcontview import EditContView
from designer.uix.modules_contview import ModulesContView
from designer.uix.kv_lang_area import KVLangArea
from designer.undo_manager import WidgetOperation, UndoManager
from designer.project_loader import ProjectLoader, ProjectLoaderException
from designer.select_class import SelectClass
from designer.confirmation_dialog import ConfirmationDialog
from designer.proj_watcher import ProjectWatcher
from designer.recent_manager import RecentManager, RecentDialog
from designer.add_file import AddFileDialog
from designer.ui_creator import UICreator
from designer.designer_content import DesignerContent
from designer.uix.designer_sandbox import DesignerSandbox
from designer.project_settings import ProjectSettings
from designer.designer_settings import DesignerSettings
from designer.helper_functions import get_kivy_designer_dir, show_alert
from designer.new_dialog import NewProjectDialog, NEW_PROJECTS
from designer.eventviewer import EventViewer
from designer.uix.designer_action_items import DesignerActionButton, \
    DesignerActionProfileCheck, DesignerActionSubMenu
from designer.help_dialog import HelpDialog, AboutDialog
from designer.uix.bug_reporter import BugReporterApp
from designer.buildozer_spec_editor import BuildozerSpecEditor
from designer.designer_git import DesignerGit

NEW_PROJECT_DIR_NAME = 'new_proj'
NEW_TEMPLATES_DIR = 'new_templates'


class Designer(FloatLayout):
    '''Designer is the Main Window class of Kivy Designer
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    designer_console = ObjectProperty(None)
    '''Instance of :class:`designer.designer_console.ConsoleDialog`
    '''

    spec_editor = ObjectProperty(None)
    '''Instance of :class:`designer.buildozer_spec_editor.BuildozerSpecEditor`
    '''

    designer_tools = ObjectProperty(None)
    '''Instance of :class:`designer.designer_tools.DesignerTools`
    '''

    designer_git = ObjectProperty(None)
    '''Instance of :class:`designer.designer_git.DesignerGit`
    '''

    statusbar = ObjectProperty(None)
    '''Reference to the :class:`~designer.statusbar.StatusBar` instance.
       :data:`statusbar` is a :class:`~kivy.properties.ObjectProperty`
    '''

    editcontview = ObjectProperty(None)
    '''Reference to the :class:`~designer.uix.EditContView` instance.
       :data:`editcontview` is a :class:`~kivy.properties.ObjectProperty`
    '''

    modulescontview = ObjectProperty(None)
    '''Reference to the :class:`~designer.uix.modules_contview.ModulesContView`.
       :data:`modulescontview` is a :class:`~kivy.properties.ObjectProperty`
    '''

    actionbar = ObjectProperty(None)
    '''Reference to the :class:`~kivy.actionbar.ActionBar` instance.
       ActionBar is used as a MenuBar to display bunch of menu items.
       :data:`actionbar` is a :class:`~kivy.properties.ObjectProperty`
    '''

    undo_manager = ObjectProperty(UndoManager())
    '''Reference to the :class:`~designer.UndoManager` instance.
       :data:`undo_manager` is a :class:`~kivy.properties.ObjectProperty`
    '''

    project_watcher = ObjectProperty(None)
    '''Reference to the :class:`~designer.project_watcher.ProjectWatcher`.
       :data:`project_watcher` is a :class:`~kivy.properties.ObjectProperty`
    '''

    project_loader = ObjectProperty(None)
    '''Reference to the :class:`~designer.project_loader.ProjectLoader`.
       :data:`project_loader` is a :class:`~kivy.properties.ObjectProperty`
    '''

    proj_settings = ObjectProperty(None)
    '''Reference of :class:`~designer.project_settings.ProjectSettings`.
       :data:`proj_settings` is a :class:`~kivy.properties.ObjectProperty`
    '''

    _curr_proj_changed = BooleanProperty(False)
    '''Specifies whether current project has been changed inside Kivy Designer
       :data:`_curr_proj_changed` is
       a :class:`~kivy.properties.BooleanProperty`
    '''

    _proj_modified_outside = BooleanProperty(False)
    '''Specifies whether current project has been changed outside Kivy Designer
       :data:`_proj_modified_outside` is a
       :class:`~kivy.properties.BooleanProperty`
    '''

    ui_creator = ObjectProperty(None)
    '''Reference to :class:`~designer.ui_creator.UICreator` instance.
       :data:`ui_creator` is a :class:`~kivy.properties.ObjectProperty`
    '''

    designer_content = ObjectProperty(None)
    '''Reference to
       :class:`~designer.designer_content.DesignerContent` instance.
       :data:`designer_content` is a :class:`~kivy.properties.ObjectProperty`
    '''

    proj_tree_view = ObjectProperty(None)
    '''Reference to Project Tree instance
       :data:`proj_tree_view` is a :class:`~kivy.properties.ObjectProperty`
    '''

    designer_settings = ObjectProperty(None)
    '''Reference of :class:`~designer.designer_settings.DesignerSettings`.
       :data:`designer_settings` is a :class:`~kivy.properties.ObjectProperty`
    '''

    start_page = ObjectProperty(None)
    '''Reference of :class:`~designer.start_page.DesignerStartPage`.
       :data:`start_page` is a :class:`~kivy.properties.ObjectProperty`
    '''

    select_profile_cont_menu = ObjectProperty(None)
    '''Reference of
        :class:`~designer.uix.designer_action_items.DesignerActionSubMenu`.
       :data:`select_profile_cont_menu` is a
       :class:`~kivy.properties.ObjectProperty`
    '''

    selected_profile = StringProperty('')
    '''Selected profile settings path
    :class:`~kivy.properties.StringProperty` and defaults to ''.
    '''

    @property
    def save_window_size(self):
        '''Save window size on exit.
        '''
        return bool(int(self.designer_settings.config_parser.getdefault(
            'desktop', 'save_window_size', 1
        ))) if Config.getboolean('kivy', 'desktop') else False

    def __init__(self, **kwargs):
        super(Designer, self).__init__(**kwargs)
        self.project_watcher = ProjectWatcher(self.project_modified)
        self.project_loader = ProjectLoader(self.project_watcher)
        self.recent_manager = RecentManager()
        self.spec_editor = BuildozerSpecEditor()
        self.widget_to_paste = None

        self.designer_settings = DesignerSettings()
        self.designer_settings.bind(on_config_change=self._config_change)
        self.designer_settings.load_settings()
        self.designer_settings.bind(on_close=self._cancel_popup)

        self.prof_settings = ProfileSettings()
        self.prof_settings.bind(on_close=self._cancel_popup)
        self.prof_settings.bind(on_changed=self.on_profiles_changed)
        self.prof_settings.bind(
            on_use_this_profile=self._perform_use_this_prof)
        self.prof_settings.load_profiles()

        self.designer_content = DesignerContent(size_hint=(1, None))
        self.designer_content = self.designer_content.__self__

        Clock.schedule_interval(
            self.project_loader.perform_auto_save,
            int(self.designer_settings.config_parser.getdefault(
                'global', 'auto_save_time', 5)) * 60)

        self.profiler = Profiler()
        self.profiler.designer = self
        self.profiler.bind(on_error=self.on_profiler_error)
        self.profiler.bind(on_message=self.on_profiler_message)
        self.profiler.bind(on_run=self.on_profiler_run)
        self.profiler.bind(on_stop=self.on_profiler_stop)

        self.designer_tools = DesignerTools(designer=self)

        Window.bind(on_resize=self._write_window_size)
        Window.bind(on_request_close=self.on_request_close)

    def _write_window_size(self, *_):
        '''Write updated window size to config
        '''
        self.designer_settings.config_parser.set(
            'internal', 'window_width', Window.size[0]
        )
        self.designer_settings.config_parser.set(
            'internal', 'window_height', Window.size[1]
        )
        self.designer_settings.config_parser.write()

    def load_view_settings(self, *args):
        '''Load "View" menu saved settings
        '''
        proj_tree = self.designer_settings.config_parser.getdefault(
            'view', 'actn_chk_proj_tree', True
        )
        if proj_tree == 'False':
            self.ids.actn_chk_proj_tree.checkbox.active = False

        props_events = self.designer_settings.config_parser.getdefault(
            'view', 'actn_chk_prop_event', True
        )
        if props_events == 'False':
            self.ids.actn_chk_prop_event.checkbox.active = False

        wid_tree = self.designer_settings.config_parser.getdefault(
            'view', 'actn_chk_widget_tree', True
        )
        if wid_tree == 'False':
            self.ids.actn_chk_widget_tree.checkbox.active = False

        status_bar = self.designer_settings.config_parser.getdefault(
            'view', 'actn_chk_status_bar', True
        )
        if status_bar == 'False':
            self.ids.actn_chk_status_bar.checkbox.active = False

        kv_lang_area = self.designer_settings.config_parser.getdefault(
            'view', 'actn_chk_kv_lang_area', True
        )
        if kv_lang_area == 'False':
            self.ids.actn_chk_kv_lang_area.checkbox.active = False

    def toggle_fullscreen(self, check, **kwargs):
        '''
        Event Handler when ActionCheckButton "Fullscreen" is changed.
        '''
        if check.checkbox.active is True:
            Window.fullscreen = "auto"
        else:
            Window.fullscreen = False

    def restore_window_size(self, *_):
        '''Restore window size from previous application run
        '''
        width = int(self.designer_settings.config_parser.getdefault(
            'internal', 'window_width', 800
        ))
        height = int(self.designer_settings.config_parser.getdefault(
            'internal', 'window_height', 600
        ))
        Window.size = max(width, 800), max(height, 600)

    def open_repo(self, *args):
        '''
        Open the Kivy Designer repository
        '''
        webbrowser.open("https://github.com/kivy/kivy-designer")

    def open_docs(self, *args):
        '''
        Open the Kivy docs
        '''
        webbrowser.open("http://kivy.org/docs/")

    def show_help(self, *args):
        '''Event handler for 'on_help' event of self.start_page
        '''

        self.help_dlg = HelpDialog()
        self._popup = Popup(title='Kivy Designer Help', content=self.help_dlg,
                            size_hint=(0.95, 0.95),
                            auto_dismiss=False)
        self._popup.open()
        self.help_dlg.bind(on_cancel=self._cancel_popup)

        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]
        self.help_dlg.rst.source = os.path.join(_dir, 'help.rst')

    def set_escape_exit(self):
        Config.set('kivy', 'exit_on_escape',
                   int(self.designer_settings.config_parser.getdefault(
                       'desktop', 'exit_on_escape', 0)))

    def _config_change(self, *args):
        '''Event Handler for 'on_config_change'
           event of self.designer_settings.
        '''

        Clock.unschedule(self.project_loader.perform_auto_save)
        Clock.schedule_interval(
            self.project_loader.perform_auto_save,
            int(self.designer_settings.config_parser.getdefault(
                'global', 'auto_save_time', 5)) * 60)

        self.ui_creator.kv_code_input.reload_kv = \
            bool(self.designer_settings.config_parser.getdefault(
                 'global', 'reload_kv', True))

        self.recent_manager.max_recent_files = \
            int(self.designer_settings.config_parser.getdefault(
                'global', 'num_recent_files', 5))

        if self.save_window_size:
            self._write_window_size()

        self.set_escape_exit()

    def on_profiler_error(self, instance, message):
        '''Display an alert if get an error
        '''
        show_alert('Profile error', message)

    def on_profiler_message(self, instance, message, duration=0):
        '''Display a message in the status bar
        '''
        self.statusbar.show_message(message, duration)

    def on_profiler_run(self, *args):
        '''When a new process starts
        '''
        self.ids.actn_btn_stop_proj.disabled = False

    def on_profiler_stop(self, *args):
        '''When a process is stopped or finished
        '''
        self.ids.actn_btn_stop_proj.disabled = True

    def _add_designer_content(self):
        '''Add designer_content to Designer, when a project is loaded
        '''

        for _child in self.children[:]:
            if _child == self.designer_content:
                return

        self.remove_widget(self.start_page)
        self.start_page.parent = None
        self.add_widget(self.designer_content, 1)

        self.ids['actn_btn_new_file'].disabled = False
        self.ids['actn_btn_save'].disabled = False
        self.ids['actn_btn_save_as'].disabled = False
        self.ids['actn_btn_close_proj'].disabled = False
        self.ids['actn_menu_view'].disabled = False
        self.ids['actn_menu_proj'].disabled = False
        self.ids['actn_menu_run'].disabled = False
        self.ids['actn_menu_tools'].disabled = False

        self.proj_settings = ProjectSettings(proj_loader=self.project_loader)
        self.proj_settings.load_proj_settings()

        Clock.schedule_once(self.load_view_settings, 0)

    def on_statusbar_height(self, *args):
        '''Callback for statusbar.height
        '''

        self.designer_content.y = self.statusbar.height
        self.on_height(*args)

    def on_actionbar_height(self, *args):
        '''Callback for actionbar.height
        '''

        self.on_height(*args)

    def on_height(self, *args):
        '''Callback for self.height
        '''

        if self.actionbar and self.statusbar:
            self.designer_content.height = self.height - \
                self.actionbar.height - self.statusbar.height

            self.designer_content.y = self.statusbar.height

    def project_modified(self, *args):
        '''Event Handler called when Project is modified outside Kivy Designer
        '''

        # To dispatch modified event only once for all files/folders of proj_dir
        if self._proj_modified_outside:
            return

        self._confirm_dlg = ConfirmationDialog(
            message="Current Project has been modified\n"
            "outside the Kivy Designer.\nDo you want to reload project?")
        self._confirm_dlg.bind(on_ok=self._perform_reload,
                               on_cancel=self._cancel_popup)
        self._popup = Popup(title='Kivy Designer', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

        self._proj_modified_outside = True

    def _perform_reload(self, *args):
        '''Perform reload of project after it is modified
        '''

        # Perform reload of project after it is modified
        self._popup.dismiss()
        self.project_watcher.allow_event_dispatch = False
        self._perform_open(self.project_loader.proj_dir)
        self.project_watcher.allow_event_dispatch = True
        self._proj_modified_outside = False
        self.spec_editor.load_settings(self.project_loader.proj_dir)

    def on_show_edit(self, *args):
        '''Event Handler of 'on_show_edit' event. This will show EditContView
           in ActionBar
        '''

        if isinstance(self.actionbar.children[0], EditContView):
            return

        if self.editcontview is None:
            select_all_trigger = Clock.create_trigger(
                self.action_btn_select_all_pressed)
            self.editcontview = EditContView(
                on_undo=self.action_btn_undo_pressed,
                on_redo=self.action_btn_redo_pressed,
                on_cut=self.action_btn_cut_pressed,
                on_copy=self.action_btn_copy_pressed,
                on_paste=self.action_btn_paste_pressed,
                on_delete=self.action_btn_delete_pressed,
                on_selectall=select_all_trigger,
                on_next_screen=self._next_screen,
                on_prev_screen=self._prev_screen,
                on_touch_up=self.on_editcontview_release,
                on_find=partial(self.designer_content.show_findmenu, True))

        self.actionbar.add_widget(self.editcontview)

        widget = self.ui_creator.propertyviewer.widget

        if isinstance(widget, Carousel) or\
                isinstance(widget, ScreenManager) or\
                isinstance(widget, TabbedPanel):
            self.editcontview.show_action_btn_screen(True)
        else:
            self.editcontview.show_action_btn_screen(False)

        if self.ui_creator.kv_code_input.clicked:
            self._edit_selected = 'KV'
        elif self.ui_creator.playground.clicked:
            self._edit_selected = 'Play'
        else:
            self._edit_selected = 'Py'

        if self._edit_selected == 'Py':
            self.editcontview.show_find(True)
        else:
            self.editcontview.show_find(False)

        self.ui_creator.playground.clicked = False
        self.ui_creator.kv_code_input.clicked = False

    def on_editcontview_release(self, instance, touch):
        if self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    Clock.schedule_once(code_input._do_focus)
                    return True
        return self.editcontview.on_touch_up(touch)

    def _prev_screen(self, *args):
        '''Event handler for 'on_prev_screen' for self.editcontview
        '''

        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_previous()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.previous()

        elif isinstance(widget, TabbedPanel):
            index = widget.tab_list.index(widget.current_tab)
            if len(widget.tab_list) <= index + 1:
                return

            widget.switch_to(widget.tab_list[index + 1])

    def _next_screen(self, *args):
        '''Event handler for 'on_next_screen' for self.editcontview
        '''

        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_next()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.next()

        elif isinstance(widget, TabbedPanel):
            index = widget.tab_list.index(widget.current_tab)
            if index == 0:
                return

            widget.switch_to(widget.tab_list[index - 1])

    def on_touch_down(self, touch):
        '''Override of FloatLayout.on_touch_down. Used to determine where
           touch is down and to call self.actionbar.on_previous
        '''

        if not isinstance(self.actionbar.children[0], EditContView) or\
           self.actionbar.collide_point(*touch.pos):
            return super(FloatLayout, self).on_touch_down(touch)

        self.actionbar.on_previous(self)
        self.ui_creator.playground.clicked = False

        return super(FloatLayout, self).on_touch_down(touch)

    def action_btn_new_file_pressed(self, *args):
        '''Event Handler when ActionButton "New Project" is pressed.
        '''
        self._input_dialog = InputDialog("File name:")

        self._input_dialog.bind(on_confirm=self._perform_new_file,
                                on_cancel=self._cancel_popup)
        self._popup = Popup(title="Add new File", content=self._input_dialog,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dimiss=False)
        self._popup.open()

    def _perform_new_file(self, *args):
        '''
        Create a new file in the project folder
        '''
        file_name = self._input_dialog.get_user_input()
        if file_name.find('.') == -1:
            file_name += '.py'
        new_file = os.path.join(self.project_loader.proj_dir, file_name)
        if os.path.exists(new_file):
            self._input_dialog.lbl_error.text = 'File exists'
            return

        self.project_loader.proj_watcher.stop()
        open(new_file, 'a').close()
        self.project_loader.proj_watcher.start_watching(
                self.project_loader.proj_dir)

        self.designer_content.update_tree_view(self.project_loader)

        self._cancel_popup()

    def action_btn_new_project_pressed(self, *args):
        '''Event Handler when ActionButton "New" is pressed.
        '''

        if not self._curr_proj_changed:
            self._show_new_dialog()
            return

        self._confirm_dlg = ConfirmationDialog('All unsaved changes will be'
                                               ' lost.\n'
                                               'Do you want to continue?')
        self._confirm_dlg.bind(on_ok=self._show_new_dialog,
                               on_cancel=self._cancel_popup)

        self._popup = Popup(title='New', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

    def _show_new_dialog(self, *args):
        if hasattr(self, '_popup'):
            self._popup.dismiss()

        self._new_dialog = NewProjectDialog()
        self._new_dialog.bind(on_select=self._perform_new,
                              on_cancel=self._cancel_popup)
        self._popup = Popup(title='New Project', content=self._new_dialog,
                            size_hint=(None, None), size=('650pt', '450pt'),
                            auto_dismiss=False)
        self._popup.open()

    def _perform_new(self, *args):
        '''To load new project
        '''

        if hasattr(self, '_popup'):
            self._popup.dismiss()

        self.cleanup()
        new_proj_dir = os.path.join(get_kivy_designer_dir(),
                                    NEW_PROJECT_DIR_NAME)
        if os.path.exists(new_proj_dir):
            shutil.rmtree(new_proj_dir)

        os.mkdir(new_proj_dir)

        template = self._new_dialog.adapter.selection[0].text
        kv_file = NEW_PROJECTS[template][0]
        py_file = NEW_PROJECTS[template][1]

        _dir = os.path.dirname(designer.__file__)
        _dir = os.path.split(_dir)[0]
        templates_dir = os.path.join(_dir, NEW_TEMPLATES_DIR)
        shutil.copy(os.path.join(templates_dir, py_file),
                    os.path.join(new_proj_dir, "main.py"))

        shutil.copy(os.path.join(templates_dir, kv_file),
                    os.path.join(new_proj_dir, "main.kv"))

        create_buildozer_prj = self.designer_settings.config_parser.getdefault(
                                            'buildozer',
                                            'create_buildozer_prj', False)
        if create_buildozer_prj:
            shutil.copy(os.path.join(templates_dir, 'default.spec'),
                        os.path.join(new_proj_dir, 'buildozer.spec'))

        self.ui_creator.playground.sandbox.error_active = True
        with self.ui_creator.playground.sandbox:
            self.project_loader.load_new_project(os.path.join(new_proj_dir,
                                                              "main.kv"))
            root_wigdet = self.project_loader.get_root_widget()
            self.ui_creator.playground.add_widget_to_parent(root_wigdet, None,
                                                            from_undo=True)
            self.ui_creator.kv_code_input.text = \
                self.project_loader.get_full_str()
            self.designer_content.update_tree_view(self.project_loader)
            self._add_designer_content()
            if self.project_loader.class_rules:
                for i, _rule in enumerate(self.project_loader.class_rules):
                    widgets.append((_rule.name, 'custom'))

                self.designer_content.toolbox.add_custom()

        self.ui_creator.playground.sandbox.error_active = False
        self.statusbar.show_message('Project created successfully', 5)

    def cleanup(self):
        '''To cleanup everything loaded by the current project before loading
           another project.
        '''

        self.project_loader.cleanup()
        self.ui_creator.cleanup()
        self.undo_manager.cleanup()
        self.designer_content.toolbox.cleanup()
        self.designer_content.tab_pannel.cleanup()

        for node in self.proj_tree_view.root.nodes[:]:
            self.proj_tree_view.remove_node(node)

        for widget in widgets[:]:
            if widget[1] == 'custom':
                widgets.remove(widget)

        self._curr_proj_changed = False
        self.ui_creator.kv_code_input.text = ""

    def action_btn_open_pressed(self, *args):
        '''Event Handler when ActionButton "Open" is pressed.
        '''

        if not self._curr_proj_changed:
            self._show_open_dialog()
            return

        self._confirm_dlg = ConfirmationDialog('All unsaved changes will be '
                                               'lost.\n'
                                               'Do you want to continue?')

        self._confirm_dlg.bind(on_ok=self._show_open_dialog,
                               on_cancel=self._cancel_popup)

        self._popup = Popup(title='Kivy Designer', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

    def action_btn_close_proj_pressed(self, *args):
        '''
        Event Handler when ActionButton "Close Project" is pressed.
        '''
        if not self._curr_proj_changed:
            self._perform_close_project()
            return

        self._confirm_dlg = ConfirmationDialog('All unsaved changes will be '
                                               'lost.\n'
                                               'Do you want to continue?')

        self._confirm_dlg.bind(on_ok=self._perform_close_project,
                               on_cancel=self._cancel_popup)

        self._popup = Popup(title='Kivy Designer', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

    def _perform_close_project(self, *args):
        '''
        Close the current project and go to the start page
        '''
        if hasattr(self, '_popup'):
            self._popup.dismiss()

        self.remove_widget(self.designer_content)
        self.designer_content.parent = None
        self.add_widget(self.start_page, 1)

        self.ids['actn_btn_new_file'].disabled = True
        self.ids['actn_btn_save'].disabled = True
        self.ids['actn_btn_save_as'].disabled = True
        self.ids['actn_btn_close_proj'].disabled = True
        self.ids['actn_menu_view'].disabled = True
        self.ids['actn_menu_proj'].disabled = True
        self.ids['actn_menu_run'].disabled = True
        self.ids['actn_menu_tools'].disabled = True

        self.project_watcher.stop()

        self._curr_proj_changed = False

    def _show_open_dialog(self, *args):
        '''To show FileBrowser to "Open" a project
        '''

        if hasattr(self, '_popup'):
            self._popup.dismiss()

        self._fbrowser = FileBrowser(select_string='Open')

        def_path = os.getcwd()
        if not self.project_loader.new_project and \
                self.project_loader.proj_dir:
            def_path = self.project_loader.proj_dir

        if self._fbrowser.ids.tabbed_browser.current_tab.text == 'List View':
            self._fbrowser.ids.list_view.path = def_path
        else:
            self._fbrowser.ids.icon_view.path = def_path

        self._fbrowser.bind(on_success=self._fbrowser_load,
                            on_canceled=self._cancel_popup)

        self._popup = Popup(title="Open", content=self._fbrowser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)
        self._popup.open()

    def _select_class_selected(self, *args):
        '''Event Handler for 'on_select' event of self._select_class
        '''

        try:
            selection = self._select_class.listview.adapter.selection[0].text

            with self.ui_creator.playground.sandbox:
                root_widget = self.project_loader.set_root_widget(selection)
                self.ui_creator.playground.add_widget_to_parent(root_widget,
                                                                None,
                                                                from_undo=True)
                self.ui_creator.kv_code_input.text = \
                    self.project_loader.get_root_str()

                self._select_class_popup.dismiss()

        except:
            self.about_dlg = AboutDialog()
            self._popup = Popup(title='About Kivy Designer',
                                content=self.about_dlg,
                                size_hint=(None, None), size=(600, 400),
                                auto_dismiss=False)
            self._popup.open()
            self.about_dlg.bind(on_cancel=self._cancel_popup)

            invalid_selection = Popup(title='Invalid Selection',
                                      content=Label(text=(
                                          'Please Choose a'
                                          'Valid Root Widget')),
                                      auto_dismiss=True,
                                      size_hint=(.5, .5))
            invalid_selection.open()

    def _select_class_cancel(self, *args):
        '''Event Handler for 'on_cancel' event of self._select_class
        '''

        self._select_class_popup.dismiss()

    def _fbrowser_load(self, instance):
        '''Event Handler for 'on_load' event of self._fbrowser
        '''
        if instance.selection == []:
            return

        file_path = instance.selection[0]
        file_extension = instance.selection[0].split('.')

        self._popup.dismiss()
        error = None
        try:
            if file_extension[1] == 'py':
                self._perform_open(file_path)
            else:
                error = 'Cannot load file type: .%s, Please load a .py file' % \
                    (file_extension[1])
        except:
            error = 'Cannot load empty file type'

        if error:
            self.statusbar.show_message(error)

    def _perform_open(self, file_path):
        '''To open a project given by file_path
        '''

        for widget in widgets[:]:
            if widget[1] == 'custom':
                widgets.remove(widget)

        self.cleanup()

        self.ui_creator.playground.sandbox.error_active = True

        root_widget = None

        with self.ui_creator.playground.sandbox:
            try:
                self.project_loader.load_project(file_path)

                if self.project_loader.class_rules:
                    for i, _rule in enumerate(self.project_loader.class_rules):
                        widgets.append((_rule.name, 'custom'))

                    self.designer_content.toolbox.add_custom()

                # to test listview
                # root_wigdet = None
                root_wigdet = self.project_loader.get_root_widget()

                if not root_wigdet:
                    # Show list box showing widgets
                    self._select_class = SelectClass(
                        self.project_loader.class_rules)

                    self._select_class.bind(
                        on_select=self._select_class_selected,
                        on_cancel=self._select_class_cancel)

                    self._select_class_popup = Popup(
                        title="Select Root Widget",
                        content=self._select_class,
                        size_hint=(0.5, 0.5),
                        auto_dismiss=False)
                    self._select_class_popup.open()

                else:
                    self.ui_creator.playground.add_widget_to_parent(
                        root_wigdet, None, from_undo=True)
                    self.ui_creator.kv_code_input.text = \
                        self.project_loader.get_full_str()

                self.recent_manager.add_file(file_path)
                # Record everything for later use
                self.project_loader.record()
                self.designer_content.update_tree_view(self.project_loader)
                self._add_designer_content()

            except Exception as e:
                self.statusbar.show_message('Cannot load Project: %s' %
                                            (str(e)))

        self.ui_creator.playground.sandbox.error_active = False
        Clock.schedule_once(partial(self.ui_creator.kivy_console.run_command,
            'cd %s' % (self.project_loader.proj_dir)
        ), 1)
        self.designer_git.load_repo(self.project_loader.proj_dir)

    def _cancel_popup(self, *args):
        '''EventHandler for all self._popup when self._popup.content
           emits 'on_cancel' or equivalent.
        '''

        self._popup.dismiss()

    def action_btn_save_pressed(self, *args):
        '''Event Handler when ActionButton "Save" is pressed.
        '''

        if self.project_loader.root_rule:
            try:
                if self.project_loader.new_project:
                    self.action_btn_save_as_pressed()
                    return

                else:
                    self.project_loader.save_project()
                    projdir = self.project_loader.proj_dir
                    self.project_loader.cleanup(stop_watcher=False)
                    self.ui_creator.playground.cleanup()
                    self.project_loader.load_project(projdir)
                    root_wigdet = self.project_loader.get_root_widget()
                    self.ui_creator.playground.add_widget_to_parent(
                        root_wigdet, None, from_undo=True, from_kv=True)
                self._curr_proj_changed = False
                self.statusbar.show_message('Project saved successfully')

            except:
                self.statusbar.show_message('Cannot save project')

    def action_btn_save_as_pressed(self, *args):
        '''Event Handler when ActionButton "Save As" is pressed.
        '''

        if self.project_loader.root_rule:
            self._curr_proj_changed = False

            self._save_as_browser = FileBrowser(select_string='Save')

            def_path = os.getcwd()
            if not self.project_loader.new_project and \
                    self.project_loader.proj_dir:
                def_path = self.project_loader.proj_dir

            if self._save_as_browser.ids.tabbed_browser.current_tab.text == \
                    'List View':
                self._save_as_browser.ids.list_view.path = def_path
            else:
                self._save_as_browser.ids.icon_view.path = def_path

            self._save_as_browser.bind(on_success=self._perform_save_as,
                                       on_canceled=self._cancel_popup)

            self._popup = Popup(title="Enter Folder Name",
                                content=self._save_as_browser,
                                size_hint=(0.9, 0.9), auto_dismiss=False)
            self._popup.open()

    def _perform_save_as(self, instance):
        '''Event handler for 'on_success' event of self._save_as_browser
        '''

        if hasattr(self, '_popup'):
            self._popup.dismiss()

        proj_dir = ''
        if instance.ids.tabbed_browser.current_tab.text == 'List View':
            proj_dir = instance.ids.list_view.path
        else:
            proj_dir = instance.ids.icon_view.path

        proj_dir = os.path.join(proj_dir, instance.filename)
        try:
            self.project_loader.save_project(proj_dir)
            self.recent_manager.add_file(proj_dir)
            projdir = self.project_loader.proj_dir
            self.project_loader.cleanup()
            self.ui_creator.playground.cleanup()
            self.project_loader.load_project(projdir)
            root_wigdet = self.project_loader.get_root_widget()
            self.ui_creator.playground.add_widget_to_parent(root_wigdet,
                                                            None,
                                                            from_undo=True)
            self.statusbar.show_message('Project saved successfully')

        except:
            self.statusbar.show_message('Cannot save project')

    def action_btn_settings_pressed(self, *args):
        '''Event handler for 'on_release' event of
           DesignerActionButton "Settings"
        '''

        self.designer_settings.parent = None
        self._popup = Popup(title="Kivy Designer Settings",
                            content=self.designer_settings,
                            size_hint=(None, None),
                            size=(720, 480), auto_dismiss=False)

        self._popup.open()

    def action_btn_select_prof_project_pressed(self, *args):
        '''Event handler for "Select Profile" menu
        '''
        pass

    def on_profiles_changed(self, *args):
        '''Callback when there is a modification in the profile settings
        '''
        self.prof_settings.load_profiles()
        self.fill_select_profile_menu()

    def _perform_use_this_prof(self, instance, *args):
        '''Callback to "Use this Profile" button
        '''
        _config = instance.selected_config
        _config_path = _config.filename
        self.designer_settings.config_parser.set('internal',
                                                'default_profile',
                                                _config_path)
        self.designer_settings.config_parser.write()

    def fill_select_profile_menu(self, *args):
        '''Fill self.select_profile_cont_menu with available Build Profiles
        '''
        prof_menu = self.select_profile_cont_menu
        prof_menu.remove_children()
        group = 'profile'
        for profile in sorted(self.prof_settings.config_parsers.keys()):
            config = self.prof_settings.config_parsers[profile]
            config_path = config.filename

            prof_name = config.getdefault('profile', 'name', 'PROFILE')
            if not prof_name.strip():
                prof_name = 'PROFILE'

            btn = DesignerActionProfileCheck(group=group,
                                             allow_no_selection=False)
            btn.text = prof_name
            btn.checkbox.active = False

            btn.config_key = profile
            btn.bind(on_active=self._perform_profile_selected)

            if self.designer_settings.config_parser.getdefault('internal',
                                        'default_profile', '') == config_path:
                btn.checkbox.active = True
                self.selected_profile = config_path
                self._perform_profile_selected(btn, btn.checkbox, True)

            prof_menu.add_widget(btn)

        prof_menu._add_widget()

    def _perform_profile_selected(self, instance, checkbox, value, *args):
        '''Event handler to select profile radio button.
        Save the selected config_parser path to the config
        '''
        if value:
            _config = self.prof_settings.config_parsers[instance.config_key]
            _config_path = _config.filename
            self.designer_settings.config_parser.set('internal',
                                                     'default_profile',
                                                     _config_path)
            self.designer_settings.config_parser.write()
            self.selected_profile = _config_path

            target = _config.getdefault('profile', 'target', '')

            if target == 'Desktop':
                self.ids.actn_btn_run_module.disabled = False
            else:
                self.ids.actn_btn_run_module.disabled = True

    def action_btn_recent_files_pressed(self, *args):
        '''Event Handler when ActionButton "Recent Projects" is pressed.
        '''
        self._recent_dlg = RecentDialog(self.recent_manager.list_files)
        self._recent_dlg.bind(on_cancel=self._cancel_popup,
                              on_select=self._recent_file_release)
        self._popup = Popup(title='Recent Projects', content=self._recent_dlg,
                            size_hint=(0.5, 0.5), auto_dismiss=False)
        self._popup.open()

    def _recent_file_release(self, instance, *args):
        '''Event Handler for 'on_select' event of self._recent_dlg.
        '''
        self._perform_open(instance.get_selected_project())
        self._cancel_popup(instance, args)

    def on_request_close(self, *args):
        '''Event Handler for 'on_request_close' event of Window.
           Check if the project was saved before exit
        '''
        if not self._curr_proj_changed:
            self._perform_quit()
            return False
        self._confirm_dlg = ConfirmationDialog('All unsaved changes will be'
                                               ' lost.\n'
                                               'Do you want to quit?')
        self._confirm_dlg.bind(on_ok=self._perform_quit,
                               on_cancel=self._cancel_popup)

        self._popup = Popup(title='Quit', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()
        return True

    def action_btn_quit_pressed(self, *args):
        '''Event Handler when ActionButton "Quit" is pressed.
        '''
        if not self._curr_proj_changed:
            self._perform_quit()
            return
        self._confirm_dlg = ConfirmationDialog('All unsaved changes will be'
                                               ' lost.\n'
                                               'Do you want to quit?')
        self._confirm_dlg.bind(on_ok=self._perform_quit,
                               on_cancel=self._cancel_popup)

        self._popup = Popup(title='Quit', content=self._confirm_dlg,
                            size_hint=(None, None), size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

    def _perform_quit(self, *args):
        '''Perform Application qui.Application
        '''
        App.get_running_app().stop()

    def action_btn_undo_pressed(self, *args):
        '''Event Handler when ActionButton "Undo" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.undo_manager.do_undo()
        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_undo()
        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.do_undo()
                    break

    def action_btn_redo_pressed(self, *args):
        '''Event Handler when ActionButton "Redo" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.undo_manager.do_redo()
        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_redo()
        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.do_redo()
                    break

    def action_btn_cut_pressed(self, *args):
        '''Event Handler when ActionButton "Cut" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_cut()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.cut()

        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.cut()
                    break

    def action_btn_copy_pressed(self, *args):
        '''Event Handler when ActionButton "Copy" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_copy()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.copy()

        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.copy()
                    break

    def action_btn_paste_pressed(self, *args):
        '''Event Handler when ActionButton "Paste" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_paste()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.paste()

        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.paste()
                    break

    def action_btn_delete_pressed(self, *args):
        '''Event Handler when ActionButton "Delete" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_delete()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.delete_selection()

        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    code_input.delete_selection()
                    break

    def action_btn_select_all_pressed(self, *args):
        '''Event Handler when ActionButton "Select All" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_select_all()

        elif self._edit_selected == 'KV':
            Clock.schedule_once(self.ui_creator.kv_code_input.do_select_all)

        elif self._edit_selected == 'Py':
            list_py = self.designer_content.tab_pannel.list_py_code_inputs
            for code_input in list_py:
                if hasattr(code_input, 'clicked') and code_input.clicked:
                    Clock.schedule_once(code_input.do_select_all)
                    break

    def action_btn_add_custom_widget_press(self, *args):
        '''Event Handler when ActionButton "Add Custom Widget" is pressed.
        '''

        self._custom_browser = FileBrowser(select_string='Add')
        self._custom_browser.bind(on_success=self._custom_browser_load,
                                  on_canceled=self._cancel_popup)

        self._popup = Popup(title="Add Custom Widget",
                            content=self._custom_browser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)
        self._popup.open()

    def _custom_browser_load(self, instance):
        '''Event Handler for 'on_success' event of self._custom_browser
        '''
        # if there is no selected file
        if len(instance.selection) < 1:
            return
        file_path = instance.selection[0]
        self._popup.dismiss()

        self.ui_creator.playground.sandbox.error_active = True

        with self.ui_creator.playground.sandbox:
            try:
                self.project_loader.add_custom_widget(file_path)

                self.designer_content.toolbox.cleanup()
                for _rule in (self.project_loader.custom_widgets):
                    widgets.append((_rule.name, 'custom'))

                self.designer_content.toolbox.add_custom()

            except ProjectLoaderException as e:
                self.statusbar.show_message('Cannot load widget. %s' % str(e))

        self.ui_creator.playground.sandbox.error_active = False

    def action_chk_btn_toolbox_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Toolbox" is activated.
        '''
        self.designer_settings.config_parser.set('view',
                                                    'actn_chk_proj_tree',
                                                    chk_btn.checkbox.active)
        self.designer_settings.config_parser.write()

        if chk_btn.checkbox.active:
            self._toolbox_parent.add_widget(
                self.designer_content.splitter_tree)
            self.designer_content.splitter_tree.width = self._toolbox_width

        else:
            self._toolbox_parent = self.designer_content.splitter_tree.parent
            self._toolbox_parent.remove_widget(
                self.designer_content.splitter_tree)
            self._toolbox_width = self.designer_content.splitter_tree.width
            self.designer_content.splitter_tree.width = 0

    def action_chk_btn_property_viewer_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Property Viewer" is activated.
        '''
        self.designer_settings.config_parser.set('view',
                                                    'actn_chk_prop_event',
                                                    chk_btn.checkbox.active)
        self.designer_settings.config_parser.write()

        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            if self.ui_creator.splitter_widget_tree.parent is None:
                self._splitter_widget_tree_parent.add_widget(
                    self.ui_creator.splitter_widget_tree)
                self.ui_creator.splitter_widget_tree.width = \
                    self._splitter_widget_tree_width

            add_tree = False
            if self.ui_creator.grid_widget_tree.parent is not None:
                add_tree = True
                self.ui_creator.splitter_property.size_hint_y = None
                self.ui_creator.splitter_property.height = 300

            self._splitter_property_parent.clear_widgets()
            if add_tree:
                self._splitter_property_parent.add_widget(
                    self.ui_creator.grid_widget_tree)

            self._splitter_property_parent.add_widget(
                self.ui_creator.splitter_property)
        else:
            self._splitter_property_parent = \
                self.ui_creator.splitter_property.parent
            self._splitter_property_parent.remove_widget(
                self.ui_creator.splitter_property)
            self._toggle_splitter_widget_tree()

    def action_chk_btn_widget_tree_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Widget Tree" is activated.
        '''
        self.designer_settings.config_parser.set('view',
                                                 'actn_chk_widget_tree',
                                                 chk_btn.checkbox.active)
        self.designer_settings.config_parser.write()

        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            add_prop = False
            if self.ui_creator.splitter_property.parent is not None:
                add_prop = True

            self._grid_widget_tree_parent.clear_widgets()
            self._grid_widget_tree_parent.add_widget(
                self.ui_creator.grid_widget_tree)
            if add_prop:
                self._grid_widget_tree_parent.add_widget(
                    self.ui_creator.splitter_property)
                self.ui_creator.splitter_property.size_hint_y = None
                self.ui_creator.splitter_property.height = 300
        else:
            self._grid_widget_tree_parent = \
                self.ui_creator.grid_widget_tree.parent
            self._grid_widget_tree_parent.remove_widget(
                self.ui_creator.grid_widget_tree)
            self.ui_creator.splitter_property.size_hint_y = 1
            self._toggle_splitter_widget_tree()

    def _toggle_splitter_widget_tree(self):
        '''To show/hide splitter_widget_tree
        '''

        if self.ui_creator.splitter_widget_tree.parent is not None and\
                self.ui_creator.splitter_property.parent is None and\
                self.ui_creator.grid_widget_tree.parent is None:

            self._splitter_widget_tree_parent = \
                self.ui_creator.splitter_widget_tree.parent
            self._splitter_widget_tree_parent.remove_widget(
                self.ui_creator.splitter_widget_tree)
            self._splitter_widget_tree_width = \
                self.ui_creator.splitter_widget_tree.width
            self.ui_creator.splitter_widget_tree.width = 0

        elif self.ui_creator.splitter_widget_tree.parent is None:
            self._splitter_widget_tree_parent.add_widget(
                self.ui_creator.splitter_widget_tree)
            self.ui_creator.splitter_widget_tree.width = \
                self._splitter_widget_tree_width

    def action_chk_btn_status_bar_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "StatusBar" is activated.
        '''
        self.designer_settings.config_parser.set('view',
                                                 'actn_chk_status_bar',
                                                 chk_btn.checkbox.active)
        self.designer_settings.config_parser.write()

        if chk_btn.checkbox.active:
            self._statusbar_parent.add_widget(self.statusbar)
            self.statusbar.height = self._statusbar_height
        else:
            self._statusbar_parent = self.statusbar.parent
            self._statusbar_height = self.statusbar.height
            self._statusbar_parent.remove_widget(self.statusbar)
            self.statusbar.height = 0

    def action_chk_btn_kv_area_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "KVLangArea" is activated.
        '''
        self.designer_settings.config_parser.set('view',
                                                 'actn_chk_kv_lang_area',
                                                 chk_btn.checkbox.active)
        self.designer_settings.config_parser.write()

        if chk_btn.checkbox.active:
            self.ui_creator.splitter_kv_code_input.height = \
                self._kv_area_height
            self._kv_area_parent.add_widget(
                self.ui_creator.splitter_kv_code_input)
        else:
            self._kv_area_parent = \
                self.ui_creator.splitter_kv_code_input.parent
            self._kv_area_height = \
                self.ui_creator.splitter_kv_code_input.height
            self.ui_creator.splitter_kv_code_input.height = 0
            self._kv_area_parent.remove_widget(
                self.ui_creator.splitter_kv_code_input)

    def _error_adding_file(self, *args):
        '''Event Handler for 'on_error' event of self._add_file_dlg
        '''

        self.statusbar.show_message('Error while adding file to project')
        self._popup.dismiss()

    def _added_file(self, *args):
        '''Event Handler for 'on_added' event of self._add_file_dlg
        '''

        self.statusbar.show_message('File successfully added to project', 5)
        self._popup.dismiss()
        self.designer_content.update_tree_view(self.project_loader)

    def action_btn_add_file_pressed(self, *args):
        '''Event Handler when ActionButton "Add File" is pressed.
        '''

        self._add_file_dlg = AddFileDialog(self.project_loader)
        self._add_file_dlg.bind(on_added=self._added_file,
                                on_error=self._error_adding_file,
                                on_cancel=self._cancel_popup)

        self._popup = Popup(title="Add File",
                            content=self._add_file_dlg,
                            size_hint=(None, None),
                            size=(480, 320), auto_dismiss=False)

        self._popup.open()

    def action_btn_run_module_pressed(self, *args):

        if self.modulescontview is None:
            self.modulescontview = ModulesContView()
            self.modulescontview.bind(
                on_module=self.action_btn_run_project_pressed)

        self.actionbar.add_widget(self.modulescontview)

    def action_btn_project_settings_pressed(self, *args):
        '''Event Handler when ActionButton "Project Settings" is pressed.
        '''
        self.proj_settings = ProjectSettings(proj_loader=self.project_loader)
        self.proj_settings.load_proj_settings()
        self.proj_settings.bind(on_close=self._cancel_popup)
        self._popup = Popup(title="Project Settings",
                            content=self.proj_settings,
                            size_hint=(None, None),
                            size=(720, 480), auto_dismiss=False)

        self._popup.open()

    def action_btn_edit_prof_project_pressed(self, *args):
        '''Event Handler when ActionButton "Edit Profiles" is pressed.
        '''
        self.prof_settings.parent = None
        self.prof_settings.load_profiles()
        self._popup = Popup(title="Build Profiles",
                            content=self.prof_settings,
                            size_hint=(None, None),
                            size=(720, 480),
                            auto_dismiss=False)
        self._popup.open()

    def check_selected_prof(self, *args):
        '''Check if there is a selected build profile.
        :return: True if ok. Show an alert and returns false if not.
        '''
        if self.selected_profile == '' or not \
                        os.path.isfile(self.selected_profile):
            show_alert('Profiler error', 'Please, select a build profile on'
                            '\'Run\' -> \'Select Profile\' menu')
            return False

        self.profiler.load_profile(self.selected_profile,
                                   self.project_loader.proj_dir)
        return True

    def action_btn_stop_project_pressed(self, *args):
        '''Event handler when ActionButton "Stop" is pressed.
        '''
        if not self.check_selected_prof():
            return
        self.profiler.stop()

    def action_btn_clean_project_pressed(self, *args):
        '''Event handler when ActionButton "Clean" is pressed
        '''
        if not self.check_selected_prof():
            return
        self.profiler.clean()

    def action_btn_build_project_pressed(self, *args):
        '''Event handler when ActionButton "Build" is pressed
        '''
        if not self.check_selected_prof():
            return
        self.profiler.build()

    def action_btn_rebuild_project_pressed(self, *args):
        '''Event handler when ActionButton "Build" is pressed
        '''
        if not self.check_selected_prof():
            return
        self.profiler.rebuild()

    def action_btn_run_project_pressed(self, *args, **kwargs):
        '''Event Handler when ActionButton "Run" is pressed.
        '''
        if not self.check_selected_prof():
            return
        if self.project_loader.file_list == []:
            return

        self.profiler.run(*args, **kwargs)

    def on_sandbox_getting_exception(self, *args):
        '''Event Handler for
           :class:`~designer.uix.designer_sandbox.DesignerSandbox`
           on_getting_exception event. This function will add exception
           string in error_console.
        '''

        s = traceback.format_list(traceback.extract_tb(
            self.ui_creator.playground.sandbox.tb))
        s = '\n'.join(s)
        to_insert = "Exception:\n" + s + '\n' + \
            "{!r}".format(self.ui_creator.playground.sandbox.exception)
        text = self.ui_creator.error_console.text + to_insert + '\n\n'
        self.ui_creator.error_console.text = text
        if self.ui_creator.playground.sandbox.error_active:
            self.ui_creator.tab_pannel.switch_to(
                self.ui_creator.tab_pannel.tab_list[0])

        self.ui_creator.playground.sandbox.error_active = False

    def action_btn_about_pressed(self, *args):
        '''Event handler for 'on_release' event of DesignerActionButton
           "About Kivy Designer"
        '''
        self.about_dlg = AboutDialog()
        self._popup = Popup(title='About Kivy Designer',
                            content=self.about_dlg,
                            size_hint=(None, None), size=(600, 400),
                            auto_dismiss=False)
        self._popup.open()
        self.about_dlg.bind(on_cancel=self._cancel_popup)


class DesignerException(ExceptionHandler):

    def handle_exception(self, inst):
        App.get_running_app().stop()
        if isinstance(inst, KeyboardInterrupt):
            return ExceptionManager.PASS
        else:
            for child in Window.children:
                Window.remove_widget(child)
            BugReporterApp(traceback.format_exc()).run()
            return ExceptionManager.PASS


class DesignerApp(App):

    widget_focused = ObjectProperty(allownone=True)
    '''Currently focused widget
    '''

    started = BooleanProperty(False)
    '''Indicates if has finished the build()
    '''

    title = 'Kivy Designer'

    def on_stop(self, *args):
        self.root.ui_creator.py_console.exit()

    def build(self):
        ExceptionManager.add_handler(DesignerException())
        Factory.register('Playground', module='designer.playground')
        Factory.register('Toolbox', module='designer.toolbox')
        Factory.register('StatusBar', module='designer.statusbar')
        Factory.register('PropertyViewer', module='designer.propertyviewer')
        Factory.register('EventViewer', module='designer.eventviewer')
        Factory.register('WidgetsTree', module='designer.nodetree')
        Factory.register('UICreator', module='designer.ui_creator')
        Factory.register('DesignerContent',
                         module='designer.designer_content')
        Factory.register('KivyConsole', module='designer.uix.kivy_console')
        Factory.register('PythonConsole', module='designer.uix.py_console')
        Factory.register('DesignerContent',
                         module='designer.uix.designer_sandbox')
        Factory.register('EventDropDown', module='designer.eventviewer')
        Factory.register('DesignerActionPrevious',
                         module='designer.uix.designer_action_items')
        Factory.register('DesignerActionGroup',
                         module='designer.uix.designer_action_items')
        Factory.register('DesignerActionButton',
                         module='designer.uix.designer_action_items')
        Factory.register('DesignerActionSubMenu',
                         module='designer.uix.designer_action_items')
        Factory.register('DesignerStartPage', module='designer.start_page')
        Factory.register('DesignerLinkLabel', module='designer.start_page')
        Factory.register('RecentFilesBox', module='designer.start_page')
        Factory.register('ContextMenu', module='designer.uix.contextual')
        Factory.register('PlaygroundSizeSelector',
                         module='designer.uix.playground_size_selector')

        self._widget_focused = None
        self.root = Designer()
        Clock.schedule_once(self._setup)

    def _setup(self, *args):
        '''To setup the properties of different classes
        '''

        if self.root.save_window_size:
            Clock.schedule_once(self.root.restore_window_size, 0)
        self.root.set_escape_exit()

        self.root.proj_tree_view = self.root.designer_content.tree_view
        self.root.ui_creator = self.root.designer_content.ui_creator
        self.root.statusbar.playground = self.root.ui_creator.playground
        self.root.project_loader.kv_code_input = \
            self.root.ui_creator.kv_code_input
        self.root.project_loader.tab_pannel = \
            self.root.designer_content.tab_pannel
        self.root.ui_creator.playground.undo_manager = self.root.undo_manager
        self.root.ui_creator.kv_code_input.project_loader = \
            self.root.project_loader
        self.root.ui_creator.kv_code_input.statusbar = self.root.statusbar
        self.root.ui_creator.widgettree.project_loader = \
            self.root.project_loader
        self.root.ui_creator.eventviewer.project_loader = \
            self.root.project_loader
        self.root.ui_creator.eventviewer.designer_tabbed_panel = \
            self.root.designer_content.tab_pannel
        self.root.ui_creator.eventviewer.statusbar = self.root.statusbar
        self.root.statusbar.bind(height=self.root.on_statusbar_height)
        self.root.actionbar.bind(height=self.root.on_actionbar_height)
        self.root.ui_creator.playground.sandbox = DesignerSandbox()
        self.root.ui_creator.playground.add_widget(
            self.root.ui_creator.playground.sandbox)
        self.root.ui_creator.playground.sandbox.pos = \
            self.root.ui_creator.playground.pos
        self.root.ui_creator.playground.sandbox.size = \
            self.root.ui_creator.playground.size
        self.root.start_page.recent_files_box.root = self.root

        self.root.ui_creator.playground.sandbox.bind(
            on_getting_exception=self.root.on_sandbox_getting_exception)

        self.bind(
            widget_focused=self.root.ui_creator.propertyviewer.setter('widget')
        )
        self.bind(
            widget_focused=self.root.ui_creator.eventviewer.setter('widget')
        )

        self.focus_widget(self.root.ui_creator.playground.root)

        self.create_kivy_designer_dir()
        self.root.start_page.recent_files_box.add_recent(
            self.root.recent_manager.list_files)

        self.root.fill_select_profile_menu()
        self.started = True

    def create_kivy_designer_dir(self):
        '''To create the ~/.kivy-designer dir
        '''

        if not os.path.exists(get_kivy_designer_dir()):
            os.mkdir(get_kivy_designer_dir())

    def create_draggable_element(self, widgetname, touch, widget=None):
        '''Create PlagroundDragElement and make it draggable
           until the touch is released also search default args if exist
        '''
        container = None
        if not widget:
            default_args = {}
            for options in widgets:
                if len(options) > 2:
                    default_args = options[2]

            container = self.root.ui_creator.playground.\
                get_playground_drag_element(widgetname, touch, **default_args)

        else:
            container = PlaygroundDragElement(
                playground=self.root.ui_creator.playground, child=widget)
            touch.grab(container)
            touch.grab_current = container
            container.on_touch_move(touch)
            container.center_x = touch.x
            container.y = touch.y + 20

        if container:
            self.root.add_widget(container)
        else:
            self.root.statusbar.show_message("Cannot create %s" % widgetname)

        container.widgettree = self.root.ui_creator.widgettree
        return container

    def focus_widget(self, widget, *largs):
        '''Called when a widget is select in Playground. It will also draw
           lines around focussed widget.
        '''

        if self._widget_focused and (widget is None or
                                     self._widget_focused[0] != widget):
            fwidget = self._widget_focused[0]
            for instr in self._widget_focused[1:]:
                fwidget.canvas.after.remove(instr)
            self._widget_focused = []

        self.widget_focused = widget
        self.root.ui_creator.widgettree.refresh()

        if not widget:
            return

        x, y = widget.pos
        right, top = widget.right, widget.top
        points = [x, y, right, y, right, top, x, top]
        if self._widget_focused:
            line = self._widget_focused[2]
            line.points = points
        else:
            from kivy.graphics import Color, Line
            with widget.canvas.after:
                color = Color(.42, .62, .65)
                line = Line(points=points, close=True, width=2.)
            self._widget_focused = [widget, color, line]

        self.root.ui_creator.playground.clicked = True
        self.root.on_show_edit()
