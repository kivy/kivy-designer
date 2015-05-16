from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix import actionbar


class RootWidget(FloatLayout):
    '''This is the class representing your root widget.
       By default it is inherited from BoxLayout,
       you can use any other layout/widget depending on your usage.
    '''

    cont1 = ObjectProperty(None)
    cont2 = ObjectProperty(None)
    action_bar = ObjectProperty(None)
    carousel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.cont1 = actionbar.ContextualActionView(
            action_previous=actionbar.ActionPrevious(title='Go Back'))
        self.cont2 = actionbar.ContextualActionView(
            action_previous=actionbar.ActionPrevious(title='Go Back'))

        self.action_bar.bind(on_previous=self.on_previous)
        self.prev_index = 0
        self.from_actionbar = False

    def on_index(self, instance, value):
        if value == 2:
            self.action_bar.add_widget(self.cont2)

        elif value == 1:
            if self.prev_index == 0:
                self.action_bar.add_widget(self.cont1)

            elif not self.from_actionbar:
                try:
                    self.action_bar.on_previous()
                except:
                    pass

        elif self.from_actionbar is False:
                try:
                    self.action_bar.on_previous()
                except:
                    pass

        self.prev_index = value
        self.from_actionbar = False

    def on_previous(self, *args):
        self.from_actionbar = True
        self.carousel.load_previous()


class MainApp(App):
    '''This is the main class of your app.
       Define any app wide entities here.
       This class can be accessed anywhere inside the kivy app as,
       in python::

         app = App.get_running_app()
         print (app.title)

       in kv language::

         on_release: print(app.title)
       Name of the .kv file that is auto-loaded is derived from the name
       of this class::

         MainApp = main.kv
         MainClass = mainclass.kv

       The App part is auto removed and the whole name is lowercased.
    '''

    def build(self):
        return RootWidget()

if __name__ == '__main__':
    MainApp().run()

