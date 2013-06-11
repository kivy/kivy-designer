from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty

class KVLangArea(TextInput):
    clicked  = BooleanProperty(False)
    __events__=('on_show_edit',)

    def on_show_edit(self, *args):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clicked = True
            self.dispatch('on_show_edit')

        return super(KVLangArea, self).on_touch_down(touch)
