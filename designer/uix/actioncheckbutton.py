from kivy.uix.actionbar import ActionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock

from functools import partial


class ActionCheckButton(ActionItem, BoxLayout):
    '''ActionCheckButton is a check button displaying text with a checkbox
    '''

    checkbox = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.checkbox.CheckBox`.
       :data:`checkbox` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text = StringProperty('Check Button')
    '''text which is displayed by ActionCheckButton.
       :data:`text` is a :class:`~kivy.properties.StringProperty`
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
        self._label = Label()
        self.checkbox = CheckBox(active=True,
                                 group=self.group,
                                 allow_no_selection=self.allow_no_selection)
        self.checkbox.size_hint_x = None
        self.checkbox.x = self.x + 2
        self.checkbox.width = '20sp'
        BoxLayout.add_widget(self, self.checkbox)
        BoxLayout.add_widget(self, self._label)
        self._label.valign = 'middle'
        self._label.text = self.text
        self.padding = [10, 0, 0, 0]
        self._label.padding_x = 10
        self.checkbox.bind(active=partial(self.dispatch, 'on_active'))
        Clock.schedule_once(self._label_setup, 0)

    def _label_setup(self, dt):
        '''To setup text_size of _label
        '''
        self._label.text_size = (self.minimum_width - self.checkbox.width - 4,
                                 self._label.size[1])
        self.checkbox.active = self.checkbox_active

    def on_touch_down(self, touch):
        '''Override of its parent's on_touch_down, used to reverse the state
           of CheckBox.
        '''
        if not self.disabled and self.collide_point(*touch.pos):
            self.checkbox._toggle_active()

    def on_active(self, *args):
        '''Default handler for 'on_active' event.
        '''
        self.checkbox_active = args[1]

    def on_text(self, instance, value):
        '''Used to set the text of label
        '''
        self._label.text = value
