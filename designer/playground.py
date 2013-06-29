from kivy.uix.scatter import ScatterPlane
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.sandbox import Sandbox
from kivy.factory import Factory

from designer.common import widgets
from designer.tree import Tree
from designer.undo_manager import WidgetOperation

class PlaygroundDragElement(BoxLayout):

    playground = ObjectProperty()
    target = ObjectProperty(allownone=True)
    can_place = BooleanProperty(False)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x = touch.x
            self.y = touch.y + 20
            self.target = self.playground.try_place_widget(
                    self.children[0], self.center_x, self.y - 20)
            self.can_place = self.target is not None
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.target = self.playground.try_place_widget(
                    self.children[0], self.center_x, self.y - 20)
            self.can_place = self.target is not None
            if self.can_place or self.playground.root is None:
                child = self.children[0]
                child.parent.remove_widget(child)
                self.playground.place_widget(
                        child, self.center_x, self.y - 20)
            self.parent.remove_widget(self)
            return True


class Playground(ScatterPlane):

    root = ObjectProperty(allownone=True)
    selection_mode = BooleanProperty(True)
    tree = ObjectProperty()
    clicked = BooleanProperty(False)
    sandbox = ObjectProperty(None)

    __events__ = ('on_show_edit',)

    def __init__(self, **kwargs):
        super(Playground, self).__init__(**kwargs)
        self.tree = Tree()

    def on_show_edit(self, *args):
        pass

    def try_place_widget(self, widget, x, y):
        x, y = self.to_local(x, y)
        return self.find_target(x, y, self.root, widget)

    def on_root(self, instance, value):
        pass #self.tree.insert(value, None)
        
    def place_widget(self, widget, x, y):
        x, y = self.to_local(x, y)
        target = self.find_target(x, y, self.root, widget)
        #wx, wy = target.to_widget(x, y)
        #widget.pos = wx, wy
        widget.pos = 0, 0
        self.add_widget_to_parent(widget, target)

    def add_widget_to_parent(self, widget, target, from_undo=False, from_kv=False):
        added = False
        if target is None:
            with self.sandbox:
                self.root = widget
                self.sandbox.add_widget(widget)
                widget.size = self.sandbox.size
                added = True
        else:
            with self.sandbox:
                target.add_widget(widget)
                added = True
                #Added just for testing, clicking on the 
                #playground will lead an error, but inside sandbox
                #widget.bind(on_touch_down=widget)
        
        #self.tree.insert(widget, target)
        if not added:
            return False

        App.get_running_app().root.widgettree.refresh()
        if not from_kv:
            App.get_running_app().root.kv_code_input.add_widget_to_parent(widget, target)

        if not from_undo:
            App.get_running_app().root.undo_manager.push_operation(
                WidgetOperation('add', widget, target, self))
    
    def get_widget(self, widgetname, **default_args):
        widget = None
        with self.sandbox:
            custom = False
            for _widget in widgets:
                if _widget[0] == widgetname and _widget[1] == 'custom':
                    widget = App.get_running_app().root\
                        .project_loader.get_widget_of_class(widgetname)
                    custom = True
            if not custom:
                try:
                    widget = getattr(Factory, widgetname)(**default_args)
                except:
                    pass
        
        return widget

    def get_playground_drag_element(self, widgetname, touch, **default_args):
        widget = self.get_widget(widgetname, **default_args)
        container = PlaygroundDragElement(playground=self)
        container.add_widget(widget)
        touch.grab(container)
        container.center_x = touch.x
        container.y = touch.y + 20
        return container
    
    def cleanup(self):
        #Cleanup is called when project is created
        #so this operation shouldn't be recorded in Undo
        self.remove_widget_from_parent(self.root, True)
        self.tree = Tree()

    def remove_widget_from_parent(self, widget, from_undo=False, from_kv=False):
        parent = None
        root = App.get_running_app().root
        if not widget:
            return
        
        if not from_kv:
            root.kv_code_input.remove_widget_from_parent(widget, parent)

        if widget != self.root:
            parent = widget.parent
            parent.remove_widget(widget)
        else:
            self.root.parent.remove_widget(self.root)
            self.root = None

        #self.tree.delete(widget)
        root.widgettree.refresh()
        if not from_undo:
            root.undo_manager.push_operation(
                WidgetOperation('remove', widget, parent, self))

    def find_target(self, x, y, target, widget=None):
        if target is None or not target.collide_point(x, y):
            return None
        x, y = target.to_local(x, y)
        for child in target.children:
            if not child.collide_point(x, y):
                continue
            if not self.allowed_target_for(child, widget):
                continue
            return self.find_target(x, y, child, widget)
        return target

    def allowed_target_for(self, target, widget):
        # stop on complex widget
        t = target if widget else target.parent
        if isinstance(t, FileChooserListView):
            return False
        if isinstance(t, FileChooserIconView):
            return False

        # if we don't have widget, always return true
        if widget is None:
            return True

        is_widget_layout = isinstance(widget, Layout)
        is_target_layout = isinstance(target, Layout)
        if is_widget_layout and is_target_layout:
            return True
        if is_target_layout:
            return True
        return False

    def on_touch_down(self, touch):
        if self.selection_mode:
            if super(ScatterPlane, self).collide_point(*touch.pos):
                x, y = self.to_local(*touch.pos)
                target = self.find_target(x, y, self.root)
                App.get_running_app().focus_widget(target)
                self.clicked = True
                self.dispatch('on_show_edit', Playground)
                return True

        if self.parent.collide_point (*touch.pos):
            super(Playground, self).on_touch_down(touch)

        return False
