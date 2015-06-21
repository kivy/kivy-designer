from kivy.metrics import sp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.actionbar import ActionGroup, ActionPrevious, ActionButton
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
        self.height = sp(48)


class DesignerActionGroup(ActionGroup):
    pass


class DesignerActionButton(ActionButton):
    '''DesignerActionButton is a ActionButton to the ActionBar menu
    '''

    cont_menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DesignerActionButton, self).__init__(**kwargs)
        self.minimum_width = 200
        self.on_press = self.on_btn_press

    def on_btn_press(self, *args):
        '''
        Event to hide the ContextualMenu when a ActionButton is pressed
        '''
        self.cont_menu.dismiss()
