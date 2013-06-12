__all__ = ('DesignerApp', )

import kivy
kivy.require('1.4.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.layout import Layout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix import actionbar

from copy import deepcopy, copy

from designer.uix.actioncheckbutton import ActionCheckButton
from designer.playground import PlaygroundDragElement
from designer.common import widgets
from designer.uix.editcontview import EditContView
from designer.uix.kv_lang_area import KVLangArea
from designer.undo_manager import WidgetOperation, UndoManager

class Designer(FloatLayout):
    propertyviewer = ObjectProperty(None)
    playground = ObjectProperty(None)
    widgetstree = ObjectProperty(None)
    statusbar = ObjectProperty(None)
    editcontview = ObjectProperty(None)
    kv_code_input = ObjectProperty(None)
    actionbar = ObjectProperty(None)
    undo_manager = ObjectProperty(UndoManager())

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
        pass

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
                base_widget.parent.remove_widget(base_widget)

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
            parent = None
            if self.propertyviewer.widget != self.playground.root:
                parent = self.propertyviewer.widget.parent
                self.propertyviewer.widget.parent.remove_widget(
                    self.propertyviewer.widget)
            else:
                self.playground.root.parent.remove_widget(self.playground.root)
                self.playground.root = None

            self.playground.tree.delete(self.propertyviewer.widget)
            App.get_running_app().focus_widget(parent)

    def action_btn_select_all_pressed(self, *args):
        pass

    def action_chk_btn_toolbox_active(self, *args):
        pass

    def action_chk_btn_property_viewer_active(self, *args):
        pass

    def action_chk_btn_widget_tree_active(self, *args):
        pass

    def action_chk_btn_status_bar_active(self, *args):
        pass

    def action_chk_btn_kv_area_active(self, *args):
        pass

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
        widget = getattr(Factory, widgetname)(**default_args)
        container = PlaygroundDragElement(playground=self.root.playground)
        container.add_widget(widget)
        touch.grab(container)
        container.center_x = touch.x
        container.y = touch.y + 20

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
        

