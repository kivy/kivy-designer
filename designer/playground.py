from kivy.uix.scatter import ScatterPlane
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.floatlayout import FloatLayout

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
        self.tree.insert(value, None)
        
    def place_widget(self, widget, x, y):
        x, y = self.to_local(x, y)
        target = self.find_target(x, y, self.root, widget)
        #wx, wy = target.to_widget(x, y)
        #widget.pos = wx, wy
        widget.pos = 0, 0
        self.add_widget_to_parent(widget, target)

    def add_widget_to_parent(self, widget, target, from_undo=False):
        if target is None:
            self.root = widget
            self.add_widget(widget)
            widget.size = self.size
        else:
            target.add_widget(widget)
        
        self.tree.insert(widget, target)
        App.get_running_app().root.widgettree.refresh()

        if not from_undo:
            App.get_running_app().root.undo_manager.push_operation(
                WidgetOperation('add', widget, target, self))

    def remove_widget_from_parent(self, widget, from_undo=False):
        parent = None
        if widget != self.root:
            parent = widget.parent
            parent.remove_widget(widget)
        else:
            self.root.parent.remove_widget(self.root)
            self.root = None

        self.tree.delete(widget)
        App.get_running_app().focus_widget(parent)
        if not from_undo:
            App.get_running_app().root.undo_manager.push_operation(
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
