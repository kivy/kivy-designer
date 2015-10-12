from kivy.metrics import sp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.actionbar import ActionGroup, ActionPrevious, ActionButton, \
    ActionItem
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from designer.uix.actioncheckbutton import ActionCheckButton
from designer.uix.contextual import ContextSubMenu


class DesignerActionPrevious(ActionPrevious):
    pass


class DesignerActionSubMenu(ContextSubMenu, ActionButton):
    pass


class DesignerActionProfileCheck(ActionCheckButton):
    '''DesignerActionSubMenuCheck a
    :class `~designer.uix.actioncheckbutton.ActionCheckButton`
    It's used to create radio buttons to action menu
    '''

    config_key = StringProperty('')
    '''Dict key to the profile config_parser
       :data:`config_key` is a :class:`~kivy.properties.StringProperty`, default
       to ''.
    '''

    def __init__(self, **kwargs):
        super(DesignerActionProfileCheck, self).__init__(**kwargs)
        self.minimum_width = 200
        self.size_hint_y = None
        self.height = sp(49)


class DesignerActionGroup(ActionGroup):
    pass


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

    desc = StringProperty('')
    '''text which is displayed as description to DesignerActionButton.
       :data:`desc` is a :class:`~kivy.properties.StringProperty` and defaults
       to ''
    '''
    cont_menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DesignerActionButton, self).__init__(**kwargs)
        self.minimum_width = 200

    def on_press(self, *args):
        '''
        Event to hide the ContextualMenu when a ActionButton is pressed
        '''
        self.cont_menu.dismiss()
