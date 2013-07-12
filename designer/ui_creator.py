from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.app import App
from kivy.clock import Clock

class UICreator(FloatLayout):
    '''UICreator is the Wigdet responsible for editing/creating UI of project
    '''

    toolbox = ObjectProperty(None)
    '''Reference to the Toolbox instance.
    '''

    propertyviewer = ObjectProperty(None)
    '''Reference to the PropertyViewer instance.
    '''

    playground = ObjectProperty(None)
    '''Reference to the Playground instance.
    '''

    widgettree = ObjectProperty(None)
    '''Reference to the WidgetsTree instance.
    '''
   
    kv_code_input = ObjectProperty(None)
    '''Reference to the KVLangArea instance.
    '''

    splitter_toolbox = ObjectProperty(None)
    '''Reference to the splitter parent of toolbox.
    '''

    splitter_kv_code_input = ObjectProperty(None)
    '''Reference to the splitter parent of kv_code_input.
    '''

    grid_widget_tree = ObjectProperty(None)
    '''Reference to the grid parent of widgettree.
    '''

    splitter_property = ObjectProperty(None)
    '''Reference to the splitter parent of propertyviewer.
    '''

    splitter_widget_tree = ObjectProperty(None)
    '''Reference to the splitter parent of widgettree.
    '''

    def __init__(self, **kwargs):
        super(UICreator, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_everything)
    
    def on_touch_down(self, *args):
        if self.playground and self.playground.keyboard:
            self.playground.keyboard.release()
  
        return super(UICreator, self).on_touch_down(*args)

    def on_show_edit(self, *args):
        App.get_running_app().root.on_show_edit(*args)

    def _setup_everything(self, *args):
        '''To setup all the references in between widget
        '''
        
        self.kv_code_input.playground = self.playground
        self.playground.kv_code_input = self.kv_code_input
        self.playground.widgettree = self.widgettree
        self.propertyviewer.kv_code_input = self.kv_code_input