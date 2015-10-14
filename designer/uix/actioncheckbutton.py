from kivy.uix.actionbar import ActionItem
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty


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

    def __init__(self, **kwargs):
        super(ActionCheckButton, self).__init__(**kwargs)

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
