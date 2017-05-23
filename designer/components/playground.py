import functools
import os
import re
from io import open
from designer.core.undo_manager import WidgetDragOperation, WidgetOperation
from designer.uix.confirmation_dialog import ConfirmationDialogSave
from designer.uix.settings import SettingListContent
from designer.utils.toolbox_widgets import toolbox_widgets as widgets_common
from designer.utils.utils import (
    FakeSettingList,
    get_app_widget,
    get_current_project,
    get_designer,
    ignore_proj_watcher,
    show_message,
)
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Line
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.layout import Layout
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.tabbedpanel import TabbedPanel


class PlaygroundDragElement(BoxLayout):
    '''An instance of this class is the drag element shown when user tries to
       add a widget to :class:`~designer.components.playground.Playground`
       by dragging from :class:`~designer.components.toolbox.Toolbox` to
       :class:`~designer.components.playground.Playground`.
    '''

    playground = ObjectProperty()
    '''Reference to the :class:`~designer.components.playground.Playground`
       :data:`playground` is a :class:`~kivy.properties.ObjectProperty`
    '''

    target = ObjectProperty(allownone=True)
    '''Widget where widget is to be added.
       :data:`target` a :class:`~kivy.properties.ObjectProperty`
    '''

    can_place = BooleanProperty(False)
    '''Whether widget can be added or not.
       :data:`can_place` is a :class:`~kivy.properties.BooleanProperty`
    '''

    drag_type = OptionProperty('new widget', options=('new widget',
                                                      'dragndrop'))
    '''Specifies the type of dragging currently done by PlaygroundDragElement.
       If it is 'new widget', then it means a new widget will be added
       If it is 'dragndrop', then it means already created widget is
       drag-n-drop, from one position to another.
       :data:`drag_type` is a :class:`~kivy.properties.OptionProperty`
    '''

    drag_parent = ObjectProperty(None)
    '''Parent of currently dragged widget.
       Will be none if 'drag_type' is 'new widget'
       :data:`drag_parent` is a :class:`~kivy.properties.ObjectProperty`
    '''

    widgettree = ObjectProperty(None)
    '''Reference to class:`~designer.nodetree.WidgetsTree`,
        the widget_tree of Designer.
       :data:`widgettree` is a :class:`~kivy.properties.ObjectProperty`
    '''

    child = ObjectProperty(None)
    '''The widget which is currently being dragged.
       :data:`child` is a :class:`~kivy.properties.ObjectProperty`
    '''

    widget = ObjectProperty(None)
    '''The widget which is currently being dragged and will be added to the UI.
        This is similar to child, however does not contains custom style used
        to present the dragging widget
       :data:`widget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(PlaygroundDragElement, self).__init__(**kwargs)
        if self.child:
            self.add_widget(self.child)

    def show_lines_on_child(self, *args):
        '''To schedule Clock's callback for _show_lines_on_child.
        '''
        Clock.schedule_once(self._show_lines_on_child)

    def on_widget(self, *args):
        def update_parent(*largs):
            p = self.widget.parent
            if p:
                self.widget.KD__last_parent = p
        self.widget.unbind(parent=update_parent)
        self.widget.bind(parent=update_parent)
        update_parent()

    def _show_lines_on_child(self, *args):
        '''To show boundaries around the child.
        '''
        x, y = self.child.pos
        right, top = self.child.right, self.child.top
        points = [x, y, right, y, right, top, x, top]
        if hasattr(self, '_canvas_instr'):
            points_equal = True
            for i in range(len(points)):
                if points[i] != self._canvas_instr[1].points[i]:
                    points_equal = False
                    break

            if points_equal:
                return

        self.remove_lines_on_child()
        with self.child.canvas.after:
            color = Color(1, 0.5, 0.8)
            line = Line(points=points, close=True, width=2.)

        self._canvas_instr = [color, line]

    def remove_lines_on_child(self, *args):
        '''Remove lines from canvas of child.
        '''
        if hasattr(self, '_canvas_instr') \
                and self._canvas_instr[1].points[0] != -1:
            try:
                self.child.canvas.after.remove(self._canvas_instr[0])
                self.child.canvas.after.remove(self._canvas_instr[1])
            except ValueError:
                pass

            self._canvas_instr[1].points[0] = -1
            Clock.unschedule(self._show_lines_on_child)

    def is_intersecting_playground(self, x, y):
        '''To determine whether x,y is inside playground
        '''
        if not self.playground:
            return False

        if self.playground.x <= x <= self.playground.right \
                and self.playground.y <= y <= self.playground.top:
            return True

        return False

    def is_intersecting_widgettree(self, x, y):
        '''To determine whether x,y is inside playground
        '''
        if not self.widgettree:
            return False

        if self.widgettree.x <= x <= self.widgettree.right \
                and self.widgettree.y <= y <= self.widgettree.top:
            return True

        return False

    def on_touch_move(self, touch):
        '''This is responsible for moving the drag element and showing where
           the widget it contains will be added.
        '''
        # if this widget is not being dragged, exit
        if touch.grab_current is not self:
            return False

        # update dragging position
        self.center_x = touch.x
        self.y = touch.y + 20

        # the widget where it will be added
        target = None

        # now, getting the target widget
        # if is targeting the playground
        if self.is_intersecting_playground(touch.x, touch.y):
            target = self.playground.try_place_widget(
                    self.widget, touch.x, touch.y)

        # if is targeting widget tree
        elif self.is_intersecting_widgettree(touch.x, touch.y):
            pos_in_tree = self.widgettree.tree.to_widget(
                    touch.x, touch.y)
            node = self.widgettree.tree.get_node_at_pos(pos_in_tree)

            if node:
                # if the same widget, skip
                if node.node == self.widget:
                    return True
                else:
                    # otherwise, runs recursively until get a valid target
                    while node and node.node != self.playground.sandbox:
                        widget = node.node
                        if self.playground.allowed_target_for(
                                widget, self.children):
                            # current target is valid
                            target = widget
                            break
                        # runs each parent to find a valid target
                        node = node.parent_node

        self.target = target

        # check if its added somewhere, remove it
        if self.widget.parent:
            if self.target:
                # special cases
                if isinstance(self.target, ScreenManager):
                    if isinstance(self.widget, Screen):
                        self.target.remove_widget(self.widget)
                    self.target.real_remove_widget(self.widget)
                elif not isinstance(self.target, TabbedPanel):
                    self.target.remove_widget(self.widget)
            # inside a usual widget
            if self.widget.parent:
                self.widget.parent.remove_widget(self.widget)

        # check if it can be placed in the target
        # if moving from another place
        if self.drag_type == 'dragndrop':
            self.can_place = target == self.drag_parent
        # if is a new widget
        else:
            self.can_place = target is not None

        # if cannot add it, go away
        if not target or not self.can_place:
            return True

        # try to add the widget

        self.playground.sandbox.error_active = True
        with self.playground.sandbox:
            # adding a new widget
            if isinstance(target, ScreenManager):
                target.real_add_widget(self.widget)
            # usual target
            else:
                target.add_widget(self.widget)
            App.get_running_app().focus_widget(target)

        self.playground.sandbox.error_active = False

        return True

    def on_touch_up(self, touch):
        '''This is responsible for adding the widget to the parent
        '''
        # if this widget is not being dragged, exit
        if touch.grab_current is not self:
            return False

        # aborts the dragging
        touch.ungrab(self)

        widget_from = None
        target = None

        # get info about the dragged widget
        if self.is_intersecting_playground(touch.x, touch.y):
            # if added by playground
            target = self.playground.try_place_widget(
                    self.widget, touch.x, touch.y)
            widget_from = 'playground'
        elif self.is_intersecting_widgettree(touch.x, touch.y):
            # if added by widgettree
            pos_in_tree = self.widgettree.tree.to_widget(
                touch.x, touch.y)
            node = self.widgettree.tree.get_node_at_pos(pos_in_tree)
            if node:
                widget = node.node
                while widget and widget != self.playground.sandbox:
                    if self.playground.allowed_target_for(
                            widget, self.widget):
                        target = widget
                        widget_from = 'treeview'
                        break

                    widget = widget.parent

        # check if has parent
        parent = self.widget.parent

        # check if it's possible to add it in the target
        if self.drag_type == 'dragndrop':
            self.can_place = target == self.drag_parent and \
                                     parent is not None
        else:
            self.can_place = target is not None and parent is not None

        # try to find the widget on parent(from preview) and remove it
        index = -1
        if self.target:
            try:
                index = self.target.children.index(self.widget)
            except ValueError:
                pass

            if isinstance(self.target, ScreenManager):
                self.target.real_remove_widget(self.widget)
            else:
                self.target.remove_widget(self.widget)

        # check if we can add this new widget
        self.playground.sandbox.error_active = True
        with self.playground.sandbox:
            if self.can_place or self.playground.root is None:
                # if widget already exists, just moving it
                if self.drag_type == 'dragndrop':
                    if parent:
                        if widget_from == 'playground':
                            # adding by playground
                            self.playground.place_widget(
                                    self.widget, touch.x, touch.y, index=index)
                        else:
                            # adding by tree
                            self.playground.place_widget(
                                    self.widget, touch.x, touch.y,
                                    index=index, target=target)
                else:
                    # adding by playground
                    if widget_from == 'playground':
                        self.playground.place_widget(
                            self.widget, touch.x, touch.y)
                    # adding by widget tree
                    else:
                        self.playground.add_widget_to_parent(
                                self.widget, target)
            # if could not add it and from playground, undo the modifications
            elif self.drag_type == 'dragndrop':
                # just cant add it, undo the last modifications
                self.playground.undo_dragging()
                # if widget outside of screen is removed
                if target is None:
                    self.playground.remove_widget_from_parent(self.widget)

        self.playground.sandbox.error_active = False

        # remove the dragging widget
        self.target = None
        if self.parent:
            self.parent.remove_widget(self)
        self.playground.drag_operation = []
        self.playground.from_drag = False
        return True

    def fit_child(self, *args):
        '''Updates it's size to display the child correctly
        '''
        if self.child:
            self.size = self.child.size


class Playground(ScatterPlane):
    '''Playground represents the actual area where user will add and delete
       the widgets. It has event on_show_edit, which is emitted whenever
       Playground is clicked.
    '''

    root = ObjectProperty(None, allownone=True)
    '''This property represents the root widget.
       :data:`root` is a :class:`~kivy.properties.ObjectProperty`
    '''

    root_name = StringProperty('')
    '''Specifies the current widget under modification on Playground
       :data:`root_name` is a :class:`~kivy.properties.StringProperty`
    '''

    root_app_widget = ObjectProperty(None, allownone=True)
    '''This property represents the root widget as a ProjectManager.AppWidget
       :data:`root_app_widget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    tree = ObjectProperty()

    clicked = BooleanProperty(False)
    '''This property represents whether
       :class:`~designer.components.playground.Playground`
        has been clicked or not
       :data:`clicked` is a :class:`~kivy.properties.BooleanProperty`
    '''

    sandbox = ObjectProperty(None)
    '''This property represents the sandbox widget which is added to
       :class:`~designer.components.playground.Playground`.
       :data:`sandbox` is a :class:`~kivy.properties.ObjectProperty`
    '''

    kv_code_input = ObjectProperty()
    '''This property refers to the
       :class:`~designer.components.ui_creator.UICreator`'s KVLangArea.
       :data:`kv_code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    widgettree = ObjectProperty()
    '''This property refers to the
       :class:`~designer.components.ui_creator.UICreator`'s WidgetTree.
       :data:`widgettree` is a :class:`~kivy.properties.ObjectProperty`
    '''

    from_drag = BooleanProperty(False)
    '''Specifies whether a widget is dragged or a new widget is added.
       :data:`from_drag` is a :class:`~kivy.properties.BooleanProperty`
    '''

    drag_operation = ListProperty((), allownone=True)
    '''Stores data of drag_operation in form of a tuple.
       drag_operation[0] is the widget which has been dragged.
       drag_operation[1] is the parent of above widget.
       drag_operation[2] is the index of widget in parent's children property.
       :data:`drag_operation` is a :class:`~kivy.properties.ListProperty`
    '''

    _touch_still_down = BooleanProperty(False)
    '''Specifies whether touch is still down or not.
       :data:`_touch_still_down` is a :class:`~kivy.properties.BooleanProperty`
    '''

    dragging = BooleanProperty(False)
    '''Specifies whether currently dragging is performed or not.
       :data:`dragging` is a :class:`~kivy.properties.BooleanProperty`
    '''

    __events__ = ('on_show_edit',)

    def __init__(self, **kwargs):
        super(Playground, self).__init__(**kwargs)
        self.keyboard = None
        self.selected_widget = None
        self.undo_manager = None
        self._widget_x = -1
        self._widget_y = -1
        self.widget_to_paste = None
        self._popup = None
        self._last_root = None

    def on_root(self, *args):
        if self.root:
            self._last_root = self.root

    def on_pos(self, *args):
        '''Default handler for 'on_pos'
        '''
        if self.sandbox:
            self.sandbox.pos = self.pos

    def on_size(self, *args):
        '''Default handler for 'on_size'
        '''
        if self.sandbox:
            self.sandbox.size = self.size

    def on_show_edit(self, *args):
        '''Default handler for 'on_show_edit'
        '''
        pass

    def on_widget_select_pressed(self, *args):
        '''Event handler to playground widget selector press
        '''
        d = get_designer()
        if d.popup:
            return False
        widgets = get_current_project().app_widgets
        app_widgets = []
        for name in widgets.keys():
            widget = widgets[name]
            if widget.is_root:
                name = 'Root - ' + name
            app_widgets.append(name)

        fake_setting = FakeSettingList()
        fake_setting.allow_custom = False
        fake_setting.items = app_widgets
        fake_setting.desc = 'Select the Widget to edit on Playground'
        fake_setting.group = 'playground_widget'

        content = SettingListContent(setting=fake_setting)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        d.popup = Popup(
            content=content,
            title='Playground - Edit Widget',
            size_hint=(None, None),
            size=(popup_width, popup_height),
            auto_dismiss=False
        )

        content.bind(on_apply=self._perform_select_root_widget,
                     on_cancel=d.close_popup)

        content.selected_items = [self.root_name]
        if self.root_app_widget and self.root_app_widget.is_root:
            content.selected_items = ['Root - ' + self.root_name]
        content.show_items()

        d.popup.open()

    def _perform_select_root_widget(self, instance, selected_item, *args):
        '''On Playground edit item selection
        :type selected_item: instance of selected array
        '''
        get_designer().close_popup()
        name = selected_item[0]
        # remove Root label from widget name
        if name.startswith('Root - '):
            name = name.replace('Root - ', '')
        self.load_widget(name)

    def no_widget(self, *args):
        '''Remove any reamining sandbox content and shows an message
        '''
        self.root = None
        show_message('No widget found!', 5, 'error')
        self.sandbox.clear_widgets()

    def load_widget(self, widget_name, update_kv_lang=True):
        '''Load and display and widget given its name.
        If widget is not found, shows information on status bar and clear
        the playground
        :param widget_name name of the widget to display
        :param update_kv_lang if True, reloads the kv file. If False, keep the
            kv lang text
        '''
        d = get_designer()
        if d.popup:
            # if has a popup, it's not using playground
            return False
        widgets = get_current_project().app_widgets
        # if displaying no widget or this widget is not know
        if self.root is None or self.root_app_widget is None or \
                widget_name not in widgets:
            self._perform_load_widget(widget_name, update_kv_lang)
            return
        # if a know widget, continue
        target = widgets[widget_name]

        # check if we are switching kv files
        if target.kv_path != self.root_app_widget.kv_path and \
                not self.kv_code_input.saved:

            file_name = os.path.basename(self.root_app_widget.kv_path)
            _confirm_dlg = ConfirmationDialogSave(
                'The %s was not saved. \n'
                'If you continue, your modifications will be lost.\n'
                'Do you want to save and continue?' % file_name
            )

            @ignore_proj_watcher
            def save_and_load(*args):
                get_current_project().save()
                self._perform_load_widget(widget_name, True)

            def dont_save(*args):
                d.close_popup()
                self._perform_load_widget(widget_name, True)

            _confirm_dlg.bind(
                on_save=save_and_load,
                on_dont_save=dont_save,
                on_cancel=d.close_popup)

            d.popup = Popup(title='Change Widget', content=_confirm_dlg,
                            size_hint=(None, None), size=('400pt', '150pt'),
                            auto_dismiss=False)
            d.popup.open()
            return
        self._perform_load_widget(widget_name, update_kv_lang)

    def _perform_load_widget(self, widget_name, update_kv_lang=True):
        '''Loads the widget if everything is ok
        :param widget_name name of the widget to display
        :param update_kv_lang if True, reloads the kv file. If False, keep the
            kv lang text
        '''
        self.root_name = widget_name
        self.root = None
        self.sandbox.clear_widgets()
        widgets = get_current_project().app_widgets
        try:
            target = widgets[widget_name]
            if update_kv_lang:
                # updates kv lang text with file
                kv_path = target.kv_path
                if kv_path:
                    self.kv_code_input.text = open(kv_path,
                                                   encoding='utf-8').read()
                else:
                    show_message(
                        'Could not found the associated .kv file with %s'
                        ' widget' % widget_name, 5, 'error'
                    )
                    self.kv_code_input.text = ''
            self.root_app_widget = target
            wdg = get_app_widget(target)
            if wdg is None:
                self.kv_code_input.have_error = True
            self.add_widget_to_parent(wdg, None, from_undo=True, from_kv=True)
            self.kv_code_input.path = target.kv_path
        except (KeyError, AttributeError):
            show_message(
                'Failed to load %s widget' % widget_name, 5, 'error')

    def on_reload_kv(self, kv_lang_area, text, force):
        '''Reloads widgets from kv lang input and update the
        visible widget.
        if force is True, all widgets must be reloaded before parsing the new kv
        :param force: if True, will parse the project again
        :param text: kv source
        :param kv_lang_area: instance of kivy lang area
        '''
        proj = get_current_project()
        # copy of initial widgets
        widgets = dict(proj.app_widgets)
        try:
            if force:
                proj.parse()
            if self.root_name:
                kv_path = widgets[self.root_name].kv_path
            else:
                kv_path = self.kv_code_input.path
            proj.parse_kv(text, kv_path)
            # if was displaying one widget, but it was removed
            if self.root_name and self.root_name not in proj.app_widgets:
                    self.load_widget_from_file(self.root_app_widget.kv_path)
                    show_message(
                        'The %s is not available. Displaying another widget'
                        % self.root_name, 5, 'info'
                    )
            elif not self.root_name and not widgets and proj.app_widgets:
                # if was not displaying a widget because there was no widget
                # and now a widget is available
                first_wdg = proj.app_widgets[list(proj.app_widgets.keys())[-1]]
                self.load_widget(first_wdg.name, update_kv_lang=False)
            else:
                # displaying an usual widget
                self.load_widget(self.root_name, update_kv_lang=False)
        except KeyError:
            show_message(
                'Failed to load %s widget' % self.root_name, 5, 'error')

    def load_widget_from_file(self, kv_path):
        '''Loads first widget from a file
        :param kv_path: absolute kv path
        '''
        self.sandbox.clear_widgets()
        proj = get_current_project()
        widgets = proj.app_widgets
        if not os.path.exists(kv_path):
            show_message(kv_path + ' not exists', 5, 'error')
            return
        self.kv_code_input.text = open(kv_path, 'r', encoding='utf-8').read()
        self.kv_code_input.path = kv_path
        for key in widgets:
            wd = widgets[key]
            if wd.kv_path == kv_path:
                self.load_widget(wd.name, update_kv_lang=False)
                return
        # if not found a widget in the path, open the first one
        if len(widgets):
            first_wdg = widgets[list(widgets.keys())[-1]]
            self.load_widget(first_wdg.name, update_kv_lang=False)
            return
        show_message('No widget was found', 5, 'error')

    def try_place_widget(self, widget, x, y):
        '''This function is used to determine where to add the widget
        :param y: new widget position
        :param x: new widget position
        :param widget: widget to be added
        '''

        x, y = self.to_local(x, y)
        return self.find_target(x, y, self.root, widget)

    def place_widget(self, widget, x, y, index=0, target=None):
        '''This function is used to first determine the target where to add
           the widget. Then it add that widget.
           :param target: where this widget should be added.
                        If None, coordinates will be used to locate the target
           :param index: index used in add_widget
           :param x: widget position x
           :param y: widget position y
           :param widget: widget to add
        '''
        local_x, local_y = self.to_local(x, y)
        if not target:
            target = self.find_target(local_x, local_y, self.root, widget)

        if not self.from_drag:
            self.add_widget_to_parent(widget, target)
        else:
            extra_args = {'x': x, 'y': y, 'index': index}
            self.add_widget_to_parent(widget, target, from_kv=True,
                                      from_undo=True, extra_args=extra_args)

    def drag_wigdet(self, widget, target, extra_args, from_undo=False):
        '''This function will drag widget from one place to another inside
           target
        '''
        extra_args['prev_x'], extra_args['prev_y'] = \
            self.to_parent(self._widget_x, self._widget_y)

        if isinstance(target, FloatLayout) or \
                isinstance(target, ScatterLayout) or \
                isinstance(target, RelativeLayout):
            target.add_widget(widget, self.drag_operation[2])
            widget.pos_hint = {}
            widget.x, widget.y = self.to_local(extra_args['x'],
                                               extra_args['y'])
            self.from_drag = False
            added = True
            local_x, local_y = widget.x - target.x, widget.y - target.y
            self.kv_code_input.set_property_value(
                widget, 'pos_hint', "{'x': %f, 'y': %f}" % (
                    local_x / target.width, local_y / target.height),
                'ListPropery')

            if not from_undo:
                self.undo_manager.push_operation(
                    WidgetDragOperation(widget, target,
                                        self.drag_operation[1],
                                        self.drag_operation[2],
                                        self, extra_args=extra_args))

        elif isinstance(target, BoxLayout) or \
                isinstance(target, AnchorLayout) or \
                isinstance(target, GridLayout):
            target.add_widget(widget, extra_args['index'])
            self.from_drag = False
            added = True
            if 'prev_index' in extra_args:
                self.kv_code_input.shift_widget(widget,
                                                extra_args['prev_index'])

            else:
                self.kv_code_input.shift_widget(widget, self.drag_operation[2])

            if not from_undo:
                self.undo_manager.push_operation(
                    WidgetDragOperation(widget, target,
                                        self.drag_operation[1],
                                        self.drag_operation[2],
                                        self, extra_args=extra_args))

    def add_widget_to_parent(self, widget, target, from_undo=False,
                             from_kv=False, kv_str='', extra_args={}):
        '''This function is used to add the widget to the target.
        :param from_undo: this action is comming from undo
        :param target: target will receive the widget
        :param widget: widget to be added
        '''
        added = False
        if widget is None:
            return False

        with self.sandbox:
            if target is None:
                self.root = widget
                self.sandbox.add_widget(widget)
                widget.size = self.sandbox.size
                added = True
            else:
                if extra_args and self.from_drag:
                    self.drag_wigdet(widget, target, extra_args=extra_args)
                else:
                    target.add_widget(widget)
                    added = True
        if not added:
            return False

        self.widgettree.refresh()

        if not from_kv:
            if not kv_str and hasattr(widget, '_KD_KV_STR'):
                kv_str = widget._KD_KV_STR
                del widget._KD_KV_STR
            self.kv_code_input.add_widget_to_parent(widget, target,
                                                    kv_str=kv_str)
        if not from_undo:
            root = App.get_running_app().root
            root.undo_manager.push_operation(WidgetOperation('add',
                                                             widget, target,
                                                             self, ''))

    def get_widget(self, widget_name, **default_args):
        '''This function is used to get the instance of class of name,
           widgetname.
           :param widget_name: name of the widget to be instantiated
        '''
        widget = None
        for _widget in widgets_common:
            if _widget[0] == widget_name and _widget[1] == 'custom':
                app_widgets = get_current_project().app_widgets
                widget = get_app_widget(app_widgets[widget_name])
                break
        if not widget:
            try:
                widget = Factory.get(widget_name)(**default_args)
            except:
                pass
        return widget

    def generate_kv_from_args(self, widget_name, kv_dict, *args):
        '''Converts a dictionary to kv string
        :param widget_name: name of the widget
        :param kv_dict: dict with widget rules
        '''
        kv = widget_name + ':'
        indent = '\n' + ' ' * 4

        try:  # check whether python knows about 'basestring'
            basestring
        except NameError:  # no, it doesn't (it's Python3); use 'str' instead
            basestring = str

        for key in kv_dict.keys():
            value = kv_dict[key]
            if isinstance(value, basestring):
                value = "'" + value + "'"
            kv += indent + key + ': ' + str(value)

        return kv

    def get_playground_drag_element(self, instance, widget_name, touch,
                                    default_args, extra_args, *args):
        '''This function will return the desired playground element
           for widget_name.
           :param extra_args: extra args used to display the dragging widget
           :param default_args: default widget args
           :param touch: instance of the current touch
           :param instance: if from toolbox, ToolboxButton instance.
                    None otherwise
           :param widget_name: name of the widget that will be dragged
        '''

        # create default widget that will be added and the custom to display
        widget = self.get_widget(widget_name, **default_args)
        widget._KD_KV_STR = self.generate_kv_from_args(widget_name,
                                                       default_args)
        values = default_args.copy()
        values.update(extra_args)
        child = self.get_widget(widget_name, **values)
        custom = False
        for op in widgets_common:
            if op[0] == widget_name:
                if op[1] == 'custom':
                    custom = True
                break
        container = PlaygroundDragElement(
                playground=self, child=child, widget=widget)
        if not custom:
            container.fit_child()
        touch.grab(container)
        touch_pos = [touch.x, touch.y]
        if instance:
            touch_pos = instance.to_window(*touch.pos)
        container.center_x = touch_pos[0]
        container.y = touch_pos[1] + 20
        return container

    def cleanup(self):
        '''This function is used to clean the state of Playground, cleaning
           the changes done by currently opened project.
        '''

        # Cleanup is called when project is created or loaded
        # so this operation shouldn't be recorded in Undo
        if self.root:
            self.remove_widget_from_parent(self.root, from_undo=True,
                                           from_kv=True)

        self.selected_widget = None
        self._widget_x = -1
        self._widget_y = -1
        self.widget_to_paste = None

    def remove_widget_from_parent(self, widget, from_undo=False,
                                  from_kv=False):
        '''This function is used to remove widget its parent.
        :param from_undo: is comming from an undo action
        :param widget: widget to be removed
        '''

        parent = None
        d = get_designer()
        if not widget:
            return

        removed_str = ''
        if not from_kv:
            removed_str = self.kv_code_input.remove_widget_from_parent(widget)
        if widget != self.root:
            parent = widget.parent
            if parent is None and hasattr(widget, 'KD__last_parent'):
                parent = widget.KD__last_parent
            if isinstance(parent.parent, Carousel):
                parent.parent.remove_widget(widget)
            elif isinstance(parent, ScreenManager):
                if isinstance(widget, Screen):
                    parent.remove_widget(widget)
                else:
                    parent.real_remove_widget(widget)
            else:
                parent.remove_widget(widget)
        else:
            self.root.parent.remove_widget(self.root)
            self.root = None

        # if is designer
        if hasattr(d, 'ui_creator'):
            d.ui_creator.widgettree.refresh()
        if not from_undo and hasattr(d, 'ui_creator'):
            d.undo_manager.push_operation(
                WidgetOperation('remove', widget, parent, self, removed_str))

    def find_target(self, x, y, target, widget=None):
        '''This widget is used to find the widget which collides with x,y
        :param widget: widget to be added in target
        :param target: widget to search over
        :param x: position to search
        :param y: position to search
        '''
        if target is None or not target.collide_point(x, y):
            return None

        x, y = target.to_local(x, y)
        class_rules = get_current_project().app_widgets

        for child in target.children:
            is_child_custom = False
            if child == widget:
                continue

            for rule_name in class_rules:
                if rule_name == type(child).__name__:
                    is_child_custom = True
                    break

            is_child_complex = False
            for _widget in widgets_common:
                if _widget[0] == type(child).__name__ and \
                                _widget[1] == 'complex':
                    is_child_complex = True
                    break

            # if point lies in custom wigdet's child then return custom widget
            if is_child_custom or is_child_complex:
                if not widget and self._custom_widget_collides(child, x, y):
                    return child

                elif widget:
                    if isinstance(child, TabbedPanel):
                        if child.current_tab:
                            _item = self.find_target(
                                x, y, child.current_tab.content, widget)
                            return _item

                    else:
                        return target

            elif isinstance(child.parent, Carousel):
                t = self.find_target(x, y, child, widget)
                return t

            else:
                if not child.collide_point(x, y):
                    continue

                if not self.allowed_target_for(child, widget) and not \
                        child.children:
                    continue

                return self.find_target(x, y, child, widget)

        return target

    def _custom_widget_collides(self, widget, x, y):
        '''This widget is used to find which custom widget collides with x,y
        '''
        if not widget:
            return False

        if widget.collide_point(x, y):
            return True

        x, y = widget.to_local(x, y)
        for child in widget.children:
            if self._custom_widget_collides(child, x, y):
                return True

        return False

    def allowed_target_for(self, target, widget):
        '''This function is used to determine if widget could be added to
           target.
        '''
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

        if is_target_layout or isinstance(target, Carousel):
            return True

        return False

    def _keyboard_released(self, *args):
        '''Called when self.keyboard is released
        '''
        self.keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''Called when a key on keyboard is pressed
        '''
        if modifiers != [] and modifiers[-1] == 'ctrl':
            if keycode[1] == 'c':
                self.do_copy()

            elif keycode[1] == 'v':
                self.do_paste()

            elif keycode[1] == 'x':
                self.do_cut()

            elif keycode[1] == 'a':
                self.do_select_all()

            elif keycode[1] == 'z':
                self.do_undo()

            elif modifiers[0] == 'shift' and keycode[1] == 'z':
                self.do_redo()

        elif keycode[1] == 'delete':
            self.do_delete()

    def do_undo(self):
        '''Undoes the last operation
        '''
        self.undo_manager.do_undo()

    def do_redo(self):
        '''Undoes the last operation
        '''
        self.undo_manager.do_redo()

    def do_copy(self, for_drag=False):
        '''Copy the selected widget
        '''
        base_widget = self.selected_widget
        if base_widget:
            self.widget_to_paste = self.get_widget(type(base_widget).__name__)
            props = base_widget.properties()
            for prop in props:
                if prop == 'id' or prop == 'children':
                    continue

                setattr(self.widget_to_paste, prop,
                        getattr(base_widget, prop))

            self.widget_to_paste.parent = None
            widget_str = self.kv_code_input. \
                get_widget_text_from_kv(base_widget, None)

            if not for_drag:
                widget_str = re.sub(r'\s+id:\s*[\w\d_]+', '', widget_str)
            self._widget_str_to_paste = widget_str

    def do_paste(self):
        '''Paste the selected widget to the current widget
        '''
        parent = self.selected_widget
        if parent and self.widget_to_paste:
            d = get_current_project()
            class_rules = d.app_widgets
            root_widget = self.root
            is_child_custom = False
            for rule_name in class_rules:
                if rule_name == type(parent).__name__:
                    is_child_custom = True
                    break

            # find appropriate parent to add widget_to_paste
            while parent:
                if isinstance(parent, Layout) and (not is_child_custom
                                                   or root_widget == parent):
                    break

                parent = parent.parent
                is_child_custom = False
                for rule_name in class_rules:
                    if rule_name == type(parent).__name__:
                        is_child_custom = True
                        break

            if parent is not None:
                self.add_widget_to_parent(self.widget_to_paste,
                                          parent,
                                          kv_str=self._widget_str_to_paste)
                self.widget_to_paste = None

    def do_cut(self):
        '''Cuts the selected widget
        '''
        base_widget = self.selected_widget

        if base_widget and base_widget.parent:
            self.widget_to_paste = base_widget
            self._widget_str_to_paste = self.kv_code_input. \
                get_widget_text_from_kv(base_widget, None)

            self.remove_widget_from_parent(base_widget)

    def do_select_all(self):
        '''Select All widgets which basically means selecting root widget
        '''
        self.selected_widget = self.root
        App.get_running_app().focus_widget(self.root)

    def do_delete(self):
        '''Delete the selected widget
        '''
        if self.selected_widget:
            self.remove_widget_from_parent(self.selected_widget)
            self.selected_widget = None

    def on_touch_move(self, touch):
        '''Default handler for 'on_touch_move'
        '''
        if self.widgettree.dragging is True:
            return True

        super(Playground, self).on_touch_move(touch)
        return False

    def on_touch_up(self, touch):
        '''Default handler for 'on_touch_up'
        '''
        if super(ScatterPlane, self).collide_point(*touch.pos):
            self.dragging = False
            Clock.unschedule(self.start_widget_dragging)

        self.dragging = False
        return super(Playground, self).on_touch_up(touch)

    def undo_dragging(self):
        '''To undo the last dragging operation if it has not been completed.
        '''
        if not self.drag_operation:
            return

        if self.drag_operation[0].parent:
            self.drag_operation[0].parent.remove_widget(self.drag_operation[0])

        try:
            self.drag_operation[1].add_widget(self.drag_operation[0],
                                              self.drag_operation[2])
        except TypeError:
            # some widgets not allow index
            self.drag_operation[1].add_widget(self.drag_operation[0])

        Clock.schedule_once(functools.partial(
            App.get_running_app().focus_widget,
            self.drag_operation[0]), 0.01)
        self.drag_operation = []

    def start_widget_dragging(self, *args):
        '''This function will create PlaygroundDragElement
           which will start dragging currently selected widget.
        '''
        if not self.dragging and not self.drag_operation \
                and self.selected_widget and self.selected_widget != self.root:
            # x, y = self.to_local(*touch.pos)
            # target = self.find_target(x, y, self.root)
            drag_widget = self.selected_widget
            self._widget_x, self._widget_y = drag_widget.x, drag_widget.y
            index = self.selected_widget.parent.children.index(drag_widget)
            self.drag_operation = (drag_widget, drag_widget.parent, index)

            self.selected_widget.parent.remove_widget(self.selected_widget)
            drag_elem = App.get_running_app().create_draggable_element(
                None, '', self.touch, self.selected_widget)

            drag_elem.drag_type = 'dragndrop'
            drag_elem.drag_parent = self.drag_operation[1]
            self.dragging = True
            self.from_drag = True
            App.get_running_app().focus_widget(None)

    def on_touch_down(self, touch):
        '''An override of ScatterPlane's on_touch_down.
           Used to determine the current selected widget and also emits,
           on_show_edit event.
        '''

        if super(ScatterPlane, self).collide_point(*touch.pos) and \
                not self.keyboard:
            win = EventLoop.window
            self.keyboard = win.request_keyboard(self._keyboard_released, self)
            self.keyboard.bind(on_key_down=self._on_keyboard_down)

        if super(ScatterPlane, self).collide_point(*touch.pos):
            if not self.dragging:
                self.touch = touch
                Clock.schedule_once(self.start_widget_dragging, 0.5)

            x, y = self.to_local(*touch.pos)
            target = self.find_target(x, y, self.root)
            self.selected_widget = target
            App.get_running_app().focus_widget(target)
            self.clicked = True
            self.dispatch('on_show_edit', Playground)
            return True

        if self.parent.collide_point(*touch.pos):
            super(Playground, self).on_touch_down(touch)

        return False
