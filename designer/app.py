__all__ = ('DesignerApp', )

import kivy
import time

kivy.require('1.4.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.layout import Layout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix import actionbar
from kivy.garden.filebrowser import FileBrowser
from kivy.uix.popup import Popup

from copy import deepcopy, copy

from designer.uix.actioncheckbutton import ActionCheckButton
from designer.playground import PlaygroundDragElement
from designer.common import widgets
from designer.uix.editcontview import EditContView
from designer.uix.kv_lang_area import KVLangArea
from designer.undo_manager import WidgetOperation, UndoManager
from designer.project_loader import ProjectLoader
from designer.select_class import SelectClass

class Designer(FloatLayout):
    toolbox = ObjectProperty(None)
    propertyviewer = ObjectProperty(None)
    playground = ObjectProperty(None)
    widgettree = ObjectProperty(None)
    statusbar = ObjectProperty(None)
    editcontview = ObjectProperty(None)
    kv_code_input = ObjectProperty(None)
    actionbar = ObjectProperty(None)
    undo_manager = ObjectProperty(UndoManager())
    splitter_toolbox = ObjectProperty(None)
    splitter_kv_code_input = ObjectProperty(None)
    grid_widget_tree = ObjectProperty(None)
    splitter_property = ObjectProperty(None)
    splitter_widget_tree = ObjectProperty(None)
    project_loader = ObjectProperty(ProjectLoader())

    def on_show_edit(self, *args):
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
                on_selectall=self.action_btn_select_all_pressed)

        self.actionbar.add_widget(self.editcontview)

        if self.kv_code_input.clicked:
            self._edit_selected = 'KV'
        else:
            self._edit_selected = 'Play'

        self.playground.clicked = False
        self.kv_code_input.clicked = False

    def on_touch_down(self, touch):
        if not isinstance(self.actionbar.children[0], EditContView) or\
           self.actionbar.collide_point(*touch.pos):
            return super(FloatLayout, self).on_touch_down(touch)

        self.actionbar.on_previous(self)
        return super(FloatLayout, self).on_touch_down(touch)  

    def action_btn_new_pressed(self, *args):
        pass

    def action_btn_open_pressed(self, *args):
        self._fbrowser = FileBrowser(select_string='Open')
        self._fbrowser.bind(on_success=self._fbrowser_load,
                            on_canceled=self._fbrowser_canceled)

        self._popup = Popup(title="Open File", content = self._fbrowser,
                            size_hint=(0.9, 0.9), auto_dismiss=False)
        self._popup.open()
    
    def _select_class_selected(self, *args):
        selection = self._select_class.listview.adapter.selection[0].text

        with self.playground.sandbox:
            self.playground.add_widget_to_parent(
                self.project_loader.get_widget_of_class(selection), None)

        self._select_class_popup.dismiss()
    
    def _select_class_cancel(self, *args):
        self._select_class_popup.dismiss()

    def _fbrowser_load(self, instance):
        file_path = instance.selection[0]
        self._popup.dismiss()
        
        for widget in widgets[:]:
            if widget[1] == 'custom':
                widgets.remove(widget)
        
        with self.playground.sandbox:
            if not self.project_loader.load_project(file_path):
                print '''Cannot Load given file, make sure that
                    file is valid, all py files are in the same folder and
                    this folder doesn't contain files related to other projects'''
                return
            
            self.playground.cleanup()
            self.undo_manager.cleanup()
            self.toolbox.cleanup()

            for widget in widgets[:]:
                if widget[1] == 'custom':
                    widgets.remove(widget)
            
            if self.project_loader.class_rules:
                for i, _rule in enumerate(self.project_loader.class_rules):
                    widgets.append((_rule.name, 'custom'))
        
                self.toolbox.add_custom()

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
                self.playground.add_widget_to_parent(root_wigdet, None)
            
            #Record everything for later use
            self.project_loader.record()

    def _fbrowser_canceled(self, instance):
        self._popup.dismiss()

    def action_btn_save_pressed(self, *args):
        pass

    def action_btn_save_as_pressed(self, *args):
        pass

    def action_btn_recent_files_pressed(self, *args):
        pass

    def action_btn_quit_pressed(self, *args):
        pass

    def action_btn_undo_pressed(self, *args):
        if self._edit_selected == 'Play':
            self.undo_manager.do_undo()
        
    def action_btn_redo_pressed(self, *args):
        if self._edit_selected == 'Play':
            self.undo_manager.do_redo()

    def action_btn_cut_pressed(self, *args):
        if self._edit_selected == 'Play':
            base_widget = self.propertyviewer.widget
            if base_widget:
                self.widget_to_paste = base_widget
                self.playground.remove_widget_from_parent(base_widget)

    def action_btn_copy_pressed(self, *args):
        if self._edit_selected == 'Play':
            base_widget = self.propertyviewer.widget
            if base_widget:
                self.widget_to_paste = type(base_widget)()
                props = base_widget.properties()
                for prop in props:
                    setattr(self.widget_to_paste, prop,
                            getattr(base_widget, prop))

                self.widget_to_paste.parent = None

    def action_btn_paste_pressed(self, *args):
        if self._edit_selected == 'Play':
            parent = self.propertyviewer.widget
            if parent and hasattr(self, 'widget_to_paste') and\
               self.widget_to_paste is not None:

                #find appropriate parent to add widget_to_paste
                while not isinstance(parent, Layout):
                    parent = parent.parent

                if parent is not None:
                    self.playground.add_widget_to_parent(self.widget_to_paste,
                                                         parent)
                    self.widget_to_paste = None

    def action_btn_delete_pressed(self, *args):
        if self._edit_selected == 'Play' and self.propertyviewer.widget:
            self.playground.remove_widget_from_parent(
                self.propertyviewer.widget)

    def action_btn_select_all_pressed(self, *args):
        pass

    def action_chk_btn_toolbox_active(self, chk_btn):
        if chk_btn.checkbox.active:
            self._toolbox_parent.add_widget(self.splitter_toolbox)
            self.splitter_toolbox.width = self._toolbox_width
        else:
            self._toolbox_parent = self.splitter_toolbox.parent
            self._toolbox_parent.remove_widget(self.splitter_toolbox)
            self._toolbox_width = self.splitter_toolbox.width
            self.splitter_toolbox.width = 0

    def action_chk_btn_property_viewer_active(self, chk_btn):
        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            if self.splitter_widget_tree.parent is None:
                self._splitter_widget_tree_parent.add_widget(self.splitter_widget_tree)
                self.splitter_widget_tree.width = self._splitter_widget_tree_width

            add_tree = False
            if self.grid_widget_tree.parent is not None:
                add_tree = True
                self.splitter_property.size_hint_y = None
                self.splitter_property.height = 300
            
            self._splitter_property_parent.clear_widgets()
            if add_tree:
                self._splitter_property_parent.add_widget(self.grid_widget_tree)

            self._splitter_property_parent.add_widget(self.splitter_property)
        else:
            self._splitter_property_parent = self.splitter_property.parent
            self._splitter_property_parent.remove_widget(self.splitter_property)
            self._toggle_splitter_widget_tree()

    def action_chk_btn_widget_tree_active(self, chk_btn):
        if chk_btn.checkbox.active:
            self._toggle_splitter_widget_tree()
            add_prop = False
            if self.splitter_property.parent is not None:
                add_prop = True
    
            self._grid_widget_tree_parent.clear_widgets()
            self._grid_widget_tree_parent.add_widget(self.grid_widget_tree)
            if add_prop:
                self._grid_widget_tree_parent.add_widget(self.splitter_property)
                self.splitter_property.size_hint_y = None
                self.splitter_property.height = 300
        else:
            self._grid_widget_tree_parent = self.grid_widget_tree.parent
            self._grid_widget_tree_parent.remove_widget(self.grid_widget_tree)
            self.splitter_property.size_hint_y = 1
            self._toggle_splitter_widget_tree()

    def _toggle_splitter_widget_tree(self):

        if self.splitter_widget_tree.parent is not None and self.splitter_property.parent is None and self.grid_widget_tree.parent is None:
            self._splitter_widget_tree_parent = self.splitter_widget_tree.parent
            self._splitter_widget_tree_parent.remove_widget(self.splitter_widget_tree)
            self._splitter_widget_tree_width = self.splitter_widget_tree.width
            self.splitter_widget_tree.width = 0
    
        elif self.splitter_widget_tree.parent is None:
            self._splitter_widget_tree_parent.add_widget(self.splitter_widget_tree)
            self.splitter_widget_tree.width = self._splitter_widget_tree_width
            
    def action_chk_btn_status_bar_active(self, chk_btn):
        if chk_btn.checkbox.active:
            self._statusbar_parent.add_widget(self.statusbar)
            self.statusbar.height = self._statusbar_height
        else:
            self._statusbar_parent = self.statusbar.parent
            self._statusbar_height = self.statusbar.height
            self._statusbar_parent.remove_widget(self.statusbar)
            self.statusbar.height = 0
    
    def action_chk_btn_kv_area_active(self, chk_btn):
        if chk_btn.checkbox.active:
            self.splitter_kv_code_input.height = self._kv_area_height
            self._kv_area_parent.add_widget(self.splitter_kv_code_input)
        else:
            self._kv_area_parent = self.splitter_kv_code_input.parent
            self._kv_area_height = self.splitter_kv_code_input.height
            self.splitter_kv_code_input.height = 0
            self._kv_area_parent.remove_widget(self.splitter_kv_code_input)

class DesignerApp(App):

    widget_focused = ObjectProperty(allownone=True)

    def build(self):
        Factory.register('Playground', module='designer.playground')
        Factory.register('Toolbox', module='designer.toolbox')
        Factory.register('StatusBar', module='designer.statusbar')
        Factory.register('PropertyViewer', module='designer.propertyviewer')
        Factory.register('WidgetsTree', module='designer.nodetree')
        self._widget_focused = None
        self.root = Designer()
        self.bind(widget_focused=self.root.propertyviewer.setter('widget'))
        self.focus_widget(self.root.playground.root)

    def create_draggable_element(self, widgetname, touch):
        # create the element, and make it draggable until the touch is released
        # search default args if exist
        default_args = {}
        for options in widgets:
            if len(options) > 2:
                default_args = options[2]
        
        container = self.root.playground.get_playground_drag_element(widgetname, touch, **default_args)
        if container:
            self.root.add_widget(container)

    def focus_widget(self, widget, *largs):
        if self._widget_focused and (widget is None or self._widget_focused[0] != widget):
            fwidget = self._widget_focused[0]
            for instr in self._widget_focused[1:]:
                fwidget.canvas.after.remove(instr)
            self._widget_focused = []
        self.widget_focused = widget
        self.root.widgettree.refresh()

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
        

