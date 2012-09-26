__all__ = ('DesignerApp', )

import kivy
kivy.require('1.4.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from designer.playground import PlaygroundDragElement
from designer.common import widgets


class Designer(FloatLayout):
    propertyviewer = ObjectProperty(None)
    playground = ObjectProperty(None)
    widgetstree = ObjectProperty(None)

class DesignerApp(App):

    widget_focused = ObjectProperty(allownone=True)

    def load_project(self, directory):
        pass

    def save_project(self, directory=None):
        pass

    def clear(self):
        pass

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
        self.root.add_widget(container)

    def focus_widget(self, widget, *largs):
        if self._widget_focused and (widget is None or self._widget_focused[0] != widget):
            fwidget = self._widget_focused[0]
            for instr in self._widget_focused[1:]:
                fwidget.canvas.after.remove(instr)
            self._widget_focused = []
        self.widget_focused = widget
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

        Clock.schedule_once(self.root.widgettree.refresh, 1)
