__all__ = ('DesignerApp', )

import kivy
import time
import os
import shutil
import traceback

kivy.require('1.4.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.layout import Layout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix import actionbar
from kivy.garden.filebrowser import FileBrowser
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.lang import Builder
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager

from designer.uix.actioncheckbutton import ActionCheckButton
from designer.playground import PlaygroundDragElement
from designer.common import widgets
from designer.uix.editcontview import EditContView
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
from designer.uix.placeholder import Placeholder
from designer.designer_settings import DesignerSettings
from designer.helper_functions import get_kivy_designer_dir
from designer.new_dialog import NewProjectDialog, NEW_PROJECTS
from designer.eventviewer import EventViewer

NEW_PROJECT_DIR_NAME = 'new_proj'
NEW_TEMPLATES_DIR = 'new_templates'

class Designer(FloatLayout):
    '''Designer is the Main Window class of Kivy Designer
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''
    
    designer_console = ObjectProperty(None)
    '''Instance of :class:`designer.designer_console.ConsoleDialog`
    '''

    statusbar = ObjectProperty(None)
    '''Reference to the :class:`~designer.statusbar.StatusBar` instance.
       :data:`statusbar` is a :class:`~kivy.properties.ObjectProperty`
    '''

    editcontview = ObjectProperty(None)
    '''Reference to the :class:`~designer.uix.EditContView` instance.
       :data:`v` is a :class:`~kivy.properties.ObjectProperty`
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
       :data:`_curr_proj_changed` is a :class:`~kivy.properties.BooleanProperty`
    '''

    _proj_modified_outside = BooleanProperty(False)
    '''Specifies whether current project has been changed outside Kivy Designer
       :data:`_proj_modified_outside` is a :class:`~kivy.properties.BooleanProperty`
    '''

    ui_creator = ObjectProperty(None)
    '''Reference to :class:`~designer.ui_creator.UICreator` instance.
       :data:`ui_creator` is a :class:`~kivy.properties.ObjectProperty`
    '''

    designer_content = ObjectProperty(None)
    '''Reference to :class:`~designer.designer_content.DesignerContent` instance.
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

    def __init__(self, **kwargs):
        super(Designer, self).__init__(**kwargs)
        self.project_watcher = ProjectWatcher(self.project_modified)
        self.project_loader = ProjectLoader(self.project_watcher)
        self.recent_manager = RecentManager()
        self.widget_to_paste = None
        self.designer_content = DesignerContent(size_hint=(1, None))

        self.designer_settings = DesignerSettings()
        self.designer_settings.bind(on_config_change=self._config_change)
        self.designer_settings.load_settings()
        self.designer_settings.bind(on_close=self._cancel_popup)

        Clock.schedule_interval(self.project_loader.perform_auto_save,
                                int(self.designer_settings.config_parser.getdefault(
                                    'global', 'auto_save_time', 5))*60)

    def _config_change(self, *args):
        '''Event Handler for 'on_config_change' event of self.designer_settings.
        '''

        Clock.unschedule(self.project_loader.perform_auto_save)
        Clock.schedule_interval(self.project_loader.perform_auto_save,
                                int(self.designer_settings.config_parser.getdefault(
                                    'global', 'auto_save_time', 5))*60)

        self.ui_creator.kv_code_input.reload_kv = \
            bool(self.designer_settings.config_parser.getdefault(
                 'global', 'reload_kv', True))

        self.recent_manager.max_recent_files = \
            int(self.designer_settings.config_parser.getdefault(
                'global', 'num_recent_files', 5))

    def _add_designer_content(self):
        '''Add designer_content to Designer, when a project is loaded
        '''

        for _child in self.children[:]:
            if _child == self.designer_content:
                return
        
        self.add_widget(self.designer_content, 1)
    
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

        #To dispatch modified event only once for all files/folders of proj_dir
        if self._proj_modified_outside:
            return

        self._confirm_dlg = ConfirmationDialog(message="Current Project has "
                                               "been modified\n"
                                               "outside the Kivy Designer.\n"
                                               "Do you want to reload project?")
        self._confirm_dlg.bind(on_ok=self._perform_reload,
                               on_cancel=self._cancel_popup)
        self._popup = Popup(title='Kivy Designer', content=self._confirm_dlg,
                            size_hint=(None, None),size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

        self._proj_modified_outside = True
    
    def _perform_reload(self, *args):
        '''Perform reload of project after it is modified
        ''' 

        #Perform reload of project after it is modified
        self._popup.dismiss()
        self.project_watcher.allow_event_dispatch = False
        self._perform_open(self.project_loader.proj_dir)
        self.project_watcher.allow_event_dispatch = True
        self._proj_modified_outside = False

    def on_show_edit(self, *args):
        '''Event Handler of 'on_show_edit' event. This will show EditContView
           in ActionBar
        '''

        if isinstance(self.actionbar.children[0], EditContView):
            return
        
        if self.editcontview == None:
            self.editcontview = EditContView(
                on_undo=self.action_btn_undo_pressed,
                on_redo=self.action_btn_redo_pressed,
                on_cut=self.action_btn_cut_pressed,
                on_copy=self.action_btn_copy_pressed,
                on_paste=self.action_btn_paste_pressed,
                on_delete=self.action_btn_delete_pressed,
                on_selectall=self.action_btn_select_all_pressed,
                on_next_screen=self._next_screen,
                on_prev_screen=self._prev_screen)

        self.actionbar.add_widget(self.editcontview)

        if isinstance(self.ui_creator.propertyviewer.widget, Carousel) or\
            isinstance(self.ui_creator.propertyviewer.widget, ScreenManager):
            self.editcontview.show_action_btn_screen(True)
        else:
            self.editcontview.show_action_btn_screen(False)

        if self.ui_creator.kv_code_input.clicked:
            self._edit_selected = 'KV'
        elif self.ui_creator.playground.clicked:
            self._edit_selected = 'Play'
        else:
            self._edit_selected = 'Py'

        self.ui_creator.playground.clicked = False
        self.ui_creator.kv_code_input.clicked = False


    def _prev_screen(self, *args):
        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_previous()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.previous()
     
    def _next_screen(self, *args):
        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_next()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.next()

    def on_touch_down(self, touch):
        '''Override of FloatLayout.on_touch_down. Used to determine where
           touch is down and to call self.actionbar.on_previous
        '''

        if not isinstance(self.actionbar.children[0], EditContView) or\
           self.actionbar.collide_point(*touch.pos):
            return super(FloatLayout, self).on_touch_down(touch)

        self.actionbar.on_previous(self)
        
        return super(FloatLayout, self).on_touch_down(touch)  

    def action_btn_new_pressed(self, *args):
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

        self._popup = Popup(title='New', content = self._confirm_dlg, 
                            size_hint=(None,None),size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()
    
    def _show_new_dialog(self, *args):
        if hasattr(self, '_popup'):
            self._popup.dismiss()
        
        self._new_dialog = NewProjectDialog()
        self._new_dialog.bind(on_select=self._perform_new,
                               on_cancel=self._cancel_popup)
        self._popup = Popup(title='New Project', content = self._new_dialog, 
                            size_hint=(None,None),size=('650pt', '450pt'),
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

        templates_dir = os.path.join(os.getcwd(), NEW_TEMPLATES_DIR)
        shutil.copy(os.path.join(templates_dir, py_file),
                    os.path.join(new_proj_dir, "main.py"))

        shutil.copy(os.path.join(templates_dir, kv_file),
                    os.path.join(new_proj_dir, "main.kv"))
        
        self.ui_creator.playground.sandbox.error_active = True
        with self.ui_creator.playground.sandbox:
            self.project_loader.load_new_project(os.path.join(new_proj_dir, 
                                                              "main.kv"))
            root_wigdet = self.project_loader.get_root_widget()
            self.ui_creator.playground.add_widget_to_parent(root_wigdet, None,
                                                            from_undo=True)
            self.ui_creator.kv_code_input.text = self.project_loader.get_full_str()
            self.designer_content.update_tree_view(self.project_loader)
            self._add_designer_content()
        
        self.ui_creator.playground.sandbox.error_active = False

    def cleanup(self):
        '''To cleanup everything loaded by the current project before loading
           another project.
        '''

        self.project_loader.cleanup()
        self.ui_creator.cleanup()
        self.undo_manager.cleanup()
        self.designer_content.toolbox.cleanup()

        for node in self.proj_tree_view.root.nodes[:]:
            self.proj_tree_view.remove_node(node)

        for widget in widgets[:]:
            if widget[1] == 'custom':
                widgets.remove(widget)

        self._curr_proj_changed = False
        self.ui_creator.kv_code_input.text = ""

        self.designer_content.tab_pannel.list_py_code_inputs = []
        for th in self.designer_content.tab_pannel.tab_list[:-1]:
            self.designer_content.tab_pannel.remove_widget(th)

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

        self._popup = Popup(title='Kivy Designer', content = self._confirm_dlg, 
                            size_hint=(None,None),size=('200pt', '150pt'),
                            auto_dismiss=False)
        self._popup.open()

    def _show_open_dialog(self, *args):
        '''To show FileBrowser to "Open" a project
        '''

        if hasattr(self, '_popup'):
            self._popup.dismiss()

        self._fbrowser = FileBrowser(select_string='Open')

        def_path = os.getcwd() 
        if not self.project_loader.new_project and self.project_loader.proj_dir:
            def_path = self.project_loader.proj_dir            
        
        if self._fbrowser.ids.tabbed_browser.current_tab.text == 'List View':
            self._fbrowser.ids.list_view.path = def_path
        else:
            self._fbrowser.ids.icon_view.path = def_path

        self._fbrowser.bind(on_success=self._fbrowser_load,
                            on_canceled=self._cancel_popup)

        self._popup = Popup(title="Open", content = self._fbrowser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)
        self._popup.open()
    
    def _select_class_selected(self, *args):
        '''Event Handler for 'on_select' event of self._select_class
        '''

        selection = self._select_class.listview.adapter.selection[0].text

        with self.ui_creator.playground.sandbox:
            root_widget = self.project_loader.set_root_widget(selection)
            self.ui_creator.playground.add_widget_to_parent(root_widget, None, from_undo=True)
            self.ui_creator.kv_code_input.text = self.project_loader.get_root_str()

        self._select_class_popup.dismiss()
    
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
        self._popup.dismiss()
        self._perform_open(file_path)

    def _perform_open(self, file_path):
        '''To open a project given by file_path
        '''

        for widget in widgets[:]:
            if widget[1] == 'custom':
                widgets.remove(widget)

        self.cleanup()
        
        self.ui_creator.playground.sandbox.error_active = True

        with self.ui_creator.playground.sandbox:
            try:
                self.project_loader.load_project(file_path)

                if self.project_loader.class_rules:
                    for i, _rule in enumerate(self.project_loader.class_rules):
                        widgets.append((_rule.name, 'custom'))
            
                    self.designer_content.toolbox.add_custom()

                #to test listview
                #root_wigdet = None
                root_wigdet = self.project_loader.get_root_widget()            

                if not root_wigdet:
                    #Show list box showing widgets
                    self._select_class = SelectClass(
                        self.project_loader.class_rules)
    
                    self._select_class.bind(on_select=self._select_class_selected,
                                            on_cancel=self._select_class_cancel)
    
                    self._select_class_popup = Popup(title="Select Root Widget",
                                                     content = self._select_class,
                                                     size_hint=(0.5, 0.5),
                                                     auto_dismiss=False)
                    self._select_class_popup.open()

                else:
                    self.ui_creator.playground.add_widget_to_parent(root_wigdet,
                                                                    None,
                                                                    from_undo=True)
                    self.ui_creator.kv_code_input.text = self.project_loader.get_full_str()

                self.recent_manager.add_file(file_path)
                #Record everything for later use
                self.project_loader.record()
                self.designer_content.update_tree_view(self.project_loader)
                self._add_designer_content()

            except Exception as e:
                self.statusbar.show_message('Cannot load Project: %s'%(str(e)))
        
        self.ui_creator.playground.sandbox.error_active = False

    def _cancel_popup(self, *args):
        '''EventHandler for all self._popup when self._popup.content
           emits 'on_cancel' or equivalent.
        '''

        self._proj_modified_outside = False
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
                    self.ui_creator.playground.add_widget_to_parent(root_wigdet,
                                                                    None,
                                                                    from_undo=True)
                    

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
            if not self.project_loader.new_project and self.project_loader.proj_dir:
                def_path = self.project_loader.proj_dir

            if self._save_as_browser.ids.tabbed_browser.current_tab.text == 'List View':
                self._save_as_browser.ids.list_view.path = def_path
            else:
                self._save_as_browser.ids.icon_view.path = def_path

            self._save_as_browser.bind(on_success=self._perform_save_as,
                                       on_canceled=self._cancel_popup)
    
            self._popup = Popup(title="Enter Folder Name",
                                content = self._save_as_browser,
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
        self.designer_settings.parent = None
        self._popup = Popup(title="Kivy Designer Settings",
                            content = self.designer_settings,
                            size_hint=(None, None), 
                            size=(600, 400), auto_dismiss=False)

        self._popup.open()

    def action_btn_recent_files_pressed(self, *args):
        '''Event Handler when ActionButton "Recent Files" is pressed.
        '''

        self._recent_dlg = RecentDialog(self.recent_manager.list_files)
        self._recent_dlg.bind(on_select=self._recent_dlg_selected,
                              on_cancel=self._cancel_popup)
        
        self._popup = Popup(title='Recent Files', content=self._recent_dlg,
                            size_hint=(0.5, 0.5), auto_dismiss=False)
        
        self._popup.open()

    def _recent_dlg_selected(self, *args):
        '''Event Handler for 'on_select' event of self._recent_dlg.
        '''

        self._popup.dismiss()
        selection = ''
        try:
            selection = self._recent_dlg.listview.adapter.selection[0].text
        except:
            pass

        if selection != '':
            self._perform_open(selection)

    def action_btn_quit_pressed(self, *args):
        '''Event Handler when ActionButton "Quit" is pressed.
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
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_undo()

    def action_btn_redo_pressed(self, *args):
        '''Event Handler when ActionButton "Redo" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.undo_manager.do_redo()
        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_redo()
        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_redo()

    def action_btn_cut_pressed(self, *args):
        '''Event Handler when ActionButton "Cut" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_cut()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_cut()

        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_cut()

    def action_btn_copy_pressed(self, *args):
        '''Event Handler when ActionButton "Copy" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_copy()
         
        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_copy()

        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_copy()
        
    def action_btn_paste_pressed(self, *args):
        '''Event Handler when ActionButton "Paste" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_paste()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_paste()

        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_paste()

    def action_btn_delete_pressed(self, *args):
        '''Event Handler when ActionButton "Delete" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_delete()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_delete()

        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_delete()

    def action_btn_select_all_pressed(self, *args):
        '''Event Handler when ActionButton "Select All" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_select_all()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_select_all()

        elif self._edit_selected == 'Py':
            for code_input in self.designer_content.tab_pannel.list_py_code_inputs:
                if code_input.clicked == True:
                    code_input.clicked = False
                    code_input.do_select_all()

    def action_btn_add_custom_widget_press(self, *args):
        '''Event Handler when ActionButton "Add Custom Widget" is pressed.
        '''

        self._custom_browser = FileBrowser(select_string='Add')
        self._custom_browser.bind(on_success=self._custom_browser_load,
                                  on_canceled=self._cancel_popup)

        self._popup = Popup(title="Add Custom Widget",
                            content = self._custom_browser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)
        self._popup.open()

    def _custom_browser_load(self, instance):
        '''Event Handler for 'on_success' event of self._custom_browser
        '''

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
                self.statusbar.show_message('Cannot load widget. %s'%str(e))
        
        self.ui_creator.playground.sandbox.error_active = False

    def action_chk_btn_toolbox_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Toolbox" is activated.
        '''

        if chk_btn.checkbox.active:
            self._toolbox_parent.add_widget(self.designer_content.splitter_tree)
            self.designer_content.splitter_tree.width = self._toolbox_width

        else:
            self._toolbox_parent = self.designer_content.splitter_tree.parent
            self._toolbox_parent.remove_widget(self.designer_content.splitter_tree)
            self._toolbox_width = self.designer_content.splitter_tree.width
            self.designer_content.splitter_tree.width = 0

    def action_chk_btn_property_viewer_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Property Viewer" is activated.
        '''

        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            if self.ui_creator.splitter_widget_tree.parent is None:
                self._splitter_widget_tree_parent.add_widget(self.ui_creator.splitter_widget_tree)
                self.ui_creator.splitter_widget_tree.width = self._splitter_widget_tree_width

            add_tree = False
            if self.ui_creator.grid_widget_tree.parent is not None:
                add_tree = True
                self.ui_creator.splitter_property.size_hint_y = None
                self.ui_creator.splitter_property.height = 300

            self._splitter_property_parent.clear_widgets()
            if add_tree:
                self._splitter_property_parent.add_widget(self.ui_creator.grid_widget_tree)

            self._splitter_property_parent.add_widget(self.ui_creator.splitter_property)
        else:
            self._splitter_property_parent = self.ui_creator.splitter_property.parent
            self._splitter_property_parent.remove_widget(self.ui_creator.splitter_property)
            self._toggle_splitter_widget_tree()

    def action_chk_btn_widget_tree_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Widget Tree" is activated.
        '''

        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            add_prop = False
            if self.ui_creator.splitter_property.parent is not None:
                add_prop = True

            self._grid_widget_tree_parent.clear_widgets()
            self._grid_widget_tree_parent.add_widget(self.ui_creator.grid_widget_tree)
            if add_prop:
                self._grid_widget_tree_parent.add_widget(self.ui_creator.splitter_property)
                self.ui_creator.splitter_property.size_hint_y = None
                self.ui_creator.splitter_property.height = 300
        else:
            self._grid_widget_tree_parent = self.ui_creator.grid_widget_tree.parent
            self._grid_widget_tree_parent.remove_widget(self.ui_creator.grid_widget_tree)
            self.ui_creator.splitter_property.size_hint_y = 1
            self._toggle_splitter_widget_tree()

    def _toggle_splitter_widget_tree(self):
        '''To show/hide splitter_widget_tree
        '''

        if self.ui_creator.splitter_widget_tree.parent is not None and\
            self.ui_creator.splitter_property.parent is None and\
            self.ui_creator.grid_widget_tree.parent is None:

            self._splitter_widget_tree_parent = self.ui_creator.splitter_widget_tree.parent
            self._splitter_widget_tree_parent.remove_widget(self.ui_creator.splitter_widget_tree)
            self._splitter_widget_tree_width = self.ui_creator.splitter_widget_tree.width
            self.ui_creator.splitter_widget_tree.width = 0

        elif self.ui_creator.splitter_widget_tree.parent is None:
            self._splitter_widget_tree_parent.add_widget(self.ui_creator.splitter_widget_tree)
            self.ui_creator.splitter_widget_tree.width = self._splitter_widget_tree_width

    def action_chk_btn_status_bar_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "StatusBar" is activated.
        '''

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

        if chk_btn.checkbox.active:
            self.ui_creator.splitter_kv_code_input.height = self._kv_area_height
            self._kv_area_parent.add_widget(self.ui_creator.splitter_kv_code_input)
        else:
            self._kv_area_parent = self.ui_creator.splitter_kv_code_input.parent
            self._kv_area_height = self.ui_creator.splitter_kv_code_input.height
            self.ui_creator.splitter_kv_code_input.height = 0
            self._kv_area_parent.remove_widget(self.ui_creator.splitter_kv_code_input)

    def _error_adding_file(self, *args):
        '''Event Handler for 'on_error' event of self._add_file_dlg
        '''

        self.statusbar.show_message('Error while adding file to project')
        self._popup.dismiss()
    
    def _added_file(self, *args):
        '''Event Handler for 'on_added' event of self._add_file_dlg
        '''

        self.statusbar.show_message('File successfully added to project')
        self._popup.dismiss()
        if self._add_file_dlg.target_file[3:] == '.py':
            self.designer_content.add_file_to_tree_view(
                self._add_file_dlg.target_file)

    def action_btn_add_file_pressed(self, *args):
        '''Event Handler when ActionButton "Add File" is pressed.
        '''

        self._add_file_dlg = AddFileDialog(self.project_loader)
        self._add_file_dlg.bind(on_added=self._added_file,
                                on_error=self._error_adding_file,
                                on_cancel=self._cancel_popup)

        self._popup = Popup(title="Add File",
                            content = self._add_file_dlg,
                            size_hint=(None, None), 
                            size=(400, 300), auto_dismiss=False)

        self._popup.open()
    
    def action_btn_project_pref_pressed(self, *args):
        '''Event Handler when ActionButton "Project Prefences" is pressed.
        '''
        self.proj_settings = ProjectSettings(proj_loader=self.project_loader)
        self.proj_settings.load_proj_settings()
        self.proj_settings.bind(on_close=self._cancel_popup)
        self._popup = Popup(title="Project Preferences",
                            content = self.proj_settings,
                            size_hint=(None, None), 
                            size=(600, 400), auto_dismiss=False)

        self._popup.open()

    def action_btn_run_project_pressed(self, *args):
        '''Event Handler when ActionButton "Run" is pressed.
        '''
        if self.project_loader.file_list == []:
            return
        args = ''
        envs = ''
        
        python_path = self.designer_settings.config_parser.getdefault(
            'global', 'python_shell_path', '')
        
        if python_path == '':
            self.statusbar.show_message("Python Shell Path not specified,"
                                        " please specify it before running"
                                        " project")
            return

        if self.proj_settings and self.proj_settings.config_parser:
            args = self.proj_settings.config_parser.getdefault('arguments', 'arg', '')
            envs = self.proj_settings.config_parser.getdefault('env variables', 'env', '')
            for env in envs.split(' '):
                self.ui_creator.kivy_console.environment[env[:env.find('=')]] = env[env.find('=')+1:]

        for _file in self.project_loader.file_list:
            if 'main.py' in os.path.basename(_file):
                self.ui_creator.kivy_console.stdin.write('%s %s %s'%
                                                         (python_path,
                                                          _file, args))
                self.ui_creator.tab_pannel.switch_to(
                    self.ui_creator.tab_pannel.tab_list[1])
                return

        self.ui_creator.kivy_console.stdin.write('%s %s %s'%
                                                 (python_path, 
                                                  self.project_loader._app_file,
                                                  args))
        self.ui_creator.tab_pannel.switch_to(
            self.ui_creator.tab_pannel.tab_list[1])

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


class DesignerApp(App):

    widget_focused = ObjectProperty(allownone=True)

    def build(self):
        Factory.register('Playground', module='designer.playground')
        Factory.register('Toolbox', module='designer.toolbox')
        Factory.register('StatusBar', module='designer.statusbar')
        Factory.register('PropertyViewer', module='designer.propertyviewer')
        Factory.register('EventViewer', module='designer.eventviewer')
        Factory.register('WidgetsTree', module='designer.nodetree')
        Factory.register('UICreator', module='designer.ui_creator')
        Factory.register('DesignerContent', module='designer.designer_content')
        Factory.register('KivyConsole', module='designer.uix.kivy_console')
        Factory.register('DesignerContent', module='designer.uix.designer_sandbox')
        Factory.register('Placeholder', module='designer.uix.placeholder')
        Factory.register('EventDropDown', module='designer.eventviewer')
        Factory.register('DesignerActionPrevious', module='designer.uix.designer_action_items')
        Factory.register('DesignerActionGroup', module='designer.uix.designer_action_items')
        Factory.register('DesignerActionButton', module='designer.uix.designer_action_items')

        self._widget_focused = None
        self.root = Designer()
        Clock.schedule_once(self._setup)

    def _setup(self, *args):
        '''To setup the properties of different classes
        '''

        self.root.proj_tree_view = self.root.designer_content.tree_view
        self.root.ui_creator = self.root.designer_content.ui_creator
        self.root.statusbar.playground = self.root.ui_creator.playground
        self.root.project_loader.kv_code_input = self.root.ui_creator.kv_code_input
        self.root.project_loader.tab_pannel = self.root.designer_content.tab_pannel
        self.root.ui_creator.playground.undo_manager = self.root.undo_manager
        self.root.ui_creator.kv_code_input.project_loader = self.root.project_loader
        self.root.ui_creator.kv_code_input.statusbar = self.root.statusbar
        self.root.ui_creator.widgettree.project_loader = self.root.project_loader
        self.root.ui_creator.eventviewer.project_loader = self.root.project_loader
        self.root.ui_creator.eventviewer.designer_tabbed_panel = self.root.designer_content.tab_pannel
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

        self.root.ui_creator.playground.sandbox.bind(on_getting_exception=
            self.root.on_sandbox_getting_exception)

        self.bind(widget_focused=
                  self.root.ui_creator.propertyviewer.setter('widget'))
        self.bind(widget_focused=
                  self.root.ui_creator.eventviewer.setter('widget'))

        self.focus_widget(self.root.ui_creator.playground.root)

        self.create_kivy_designer_dir()

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
            container = PlaygroundDragElement(playground=self.root.ui_creator.playground)
            container.add_widget(widget)
            touch.grab(container)
            touch.grab_current = container
            container.on_touch_move(touch)
            container.center_x = touch.x
            container.y = touch.y + 20

        if container:
            self.root.add_widget(container)
        else:
            self.root.statusbar.show_message("Cannot create %s"%widgetname)

        container.widgettree = self.root.ui_creator.widgettree
        return container

    def focus_widget(self, widget, *largs):
        '''Called when a widget is select in Playground. It will also draw
           lines around focussed widget.
        '''

        if self._widget_focused and (widget is None or self._widget_focused[0] != widget):
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

        self.root.ui_creator.playground.clicked=True
        self.root.on_show_edit()
