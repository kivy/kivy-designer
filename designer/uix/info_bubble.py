from kivy.uix.bubble import Bubble
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window


class InfoBubble(Bubble):
    '''Bubble to be used to display short Help Information'''

    message = StringProperty('')
    '''Message to be displayed
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    def show(self, pos, duration, width=None):
        '''Animate the bubble into position'''
        if width:
            self.width = width
        # wait for the bubble to adjust it's size according to text then animate
        Clock.schedule_once(lambda dt: self._show(pos, duration))

    def _show(self, pos, duration):
        '''To show Infobubble at pos with Animation of duration.
        '''
        def on_stop(*l):
            if duration:
                Clock.schedule_once(self.hide, duration + .5)

        self.opacity = 0
        arrow_pos = self.arrow_pos
        if arrow_pos[0] in ('l', 'r'):
            pos = pos[0], pos[1] - (self.height / 2)
        else:
            pos = pos[0] - (self.width / 2), pos[1]

        self.limit_to = Window
        self.pos = pos
        Window.add_widget(self)

        anim = Animation(opacity=1, d=0.75)
        anim.bind(on_complete=on_stop)
        anim.cancel_all(self)
        anim.start(self)

    def hide(self, *dt):
        ''' Auto fade out the Bubble
        '''
        def on_stop(*l):
            Window.remove_widget(self)
        anim = Animation(opacity=0, d=0.75)
        anim.bind(on_complete=on_stop)
        anim.cancel_all(self)
        anim.start(self)
