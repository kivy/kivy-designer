import weakref

from designer.uix.contextual import ContextSubMenu
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.actionbar import ActionButton, ActionGroup, ActionItem
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout


class DesignerActionSubMenu(ContextSubMenu, ActionButton):
    pass


class ActionCheckButton(ActionItem, FloatLayout):
    '''ActionCheckButton is a check button displaying text with a checkbox
    '''

    checkbox = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.checkbox.CheckBox`.
       :data:`checkbox` is a :class:`~kivy.properties.ObjectProperty`
    '''

    _label = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.label.Label`.
       :data:`_label` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text = StringProperty('Check Button')
    '''text which is displayed by ActionCheckButton.
       :data:`text` is a :class:`~kivy.properties.StringProperty`
    '''

    desc = StringProperty('')
    '''text which is displayed as description to ActionCheckButton.
       :data:`desc` is a :class:`~kivy.properties.StringProperty` and defaults
       to ''
    '''

    btn_layout = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.boxlayout.BoxLayout`.
       :data:`_label` is a :class:`~kivy.properties.ObjectProperty`
    '''

    checkbox_active = BooleanProperty(True)
    '''boolean indicating the checkbox.active state
        :data:`active` is a :class:`~kivy.properties.BooleanProperty`
    '''

    group = ObjectProperty(None)
    '''Checkbox group
    :data:`group` is a :class:`~kivy.properties.ObjectProperty`
    '''

    allow_no_selection = BooleanProperty(True)
    '''This specifies whether the checkbox in group allows
        everything to be deselected.
    :data:`allow_no_selection` is a :class:`~kivy.properties.BooleanProperty`
    '''

    cont_menu = ObjectProperty(None)

    __events__ = ('on_active',)

    def on_touch_down(self, touch):
        '''Override of its parent's on_touch_down, used to reverse the state
           of CheckBox.
        '''
        if not self.disabled and self.collide_point(*touch.pos):
            self.checkbox._toggle_active()

    def on_active(self, instance, value, *args):
        '''Default handler for 'on_active' event.
        '''
        self.checkbox_active = value


class DesignerActionProfileCheck(ActionCheckButton):
    '''DesignerActionSubMenuCheck a
    :class `~designer.uix.actioncheckbutton.ActionCheckButton`
    It's used to create radio buttons to action menu
    '''

    config_key = StringProperty('')
    '''Dict key to the profile config_parser
       :data:`config_key` is a :class:`~kivy.properties.StringProperty`,
       default to ''.
    '''


class DesignerActionGroup(ActionGroup):

    to_open = BooleanProperty(False)
    '''To keep check of whether to open the dropdown list or not.
    :attr:`to_open` is a :class:`~kivy.properties.BooleanProperty`,
    defaults to False.
    '''
    hovered = BooleanProperty(False)
    '''To keep check of hover over each instance of DesignerActionGroup.
    :attr:`hovered` is a :class:`~kivy.properties.BooleanProperty`,
    defaults to False.
    '''
    instances = []
    '''List to keep the instances of DesignerActionGroup.
    '''

    def __init__(self, **kwargs):
        super(DesignerActionGroup, self).__init__(**kwargs)
        self.__class__.instances.append(weakref.proxy(self))
        self.register_event_type('on_enter')  # Registering the event
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        try:
            pos = args[1]
            inside_actionbutton = self.collide_point(*pos)
            if self.hovered == inside_actionbutton:
                # If mouse is hovering inside the group then return.
                return
            self.hovered = inside_actionbutton
            if inside_actionbutton:
                self.dispatch('on_enter')
        except:
            return

    def on_touch_down(self, touch):
        '''Used to determine where touch is down and to change values
        of to_open.
        '''
        if self.collide_point(touch.x, touch.y):
            DesignerActionGroup.to_open = True
            return super(DesignerActionGroup, self).on_touch_down(touch)

        if not self.is_open:
            DesignerActionGroup.to_open = False

    def on_enter(self):
        '''Event handler for on_enter event
        '''
        if not self.disabled:
            if all(instance.is_open is False for instance in
                    DesignerActionGroup.instances):
                DesignerActionGroup.to_open = False
            for instance in DesignerActionGroup.instances:
                if instance.is_open:
                    instance._dropdown.dismiss()
            if DesignerActionGroup.to_open is True:
                self.is_open = True
                self._toggle_dropdown()


class DesignerSubActionButton(ActionButton):

    def __init__(self, **kwargs):
        super(DesignerSubActionButton, self).__init__(**kwargs)

    def on_press(self):
        if self.cont_menu:
            self.cont_menu.dismiss()


class DesignerActionButton(ActionItem, ButtonBehavior, FloatLayout):
    '''DesignerActionButton is a ActionButton to the ActionBar menu
    '''

    text = StringProperty('Button')
    '''text which is displayed in the DesignerActionButton.
       :data:`text` is a :class:`~kivy.properties.StringProperty` and defaults
       to 'Button'
    '''

    hint = StringProperty('')
    '''text which is displayed as description to DesignerActionButton.
       :data:`hint` is a :class:`~kivy.properties.StringProperty` and defaults
       to ''
    '''
    cont_menu = ObjectProperty(None)

    def on_press(self, *args):
        '''
        Event to hide the ContextualMenu when a ActionButton is pressed
        '''
        self.cont_menu.dismiss()
