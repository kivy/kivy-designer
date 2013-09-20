from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.app import App
from kivy.clock import Clock


class UICreator(FloatLayout):
    '''UICreator is the Wigdet responsible for editing/creating UI of project
    '''

    toolbox = ObjectProperty(None)
    '''Reference to the :class:`~designer.toolbox.Toolbox` instance.
       :data:`toolbox` is an :class:`~kivy.properties.ObjectProperty`
    '''

    propertyviewer = ObjectProperty(None)
    '''Reference to the :class:`~designer.propertyviewer.PropertyViewer`
       instance. :data:`propertyviewer` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    playground = ObjectProperty(None)
    '''Reference to the :class:`~designer.playground.Playground` instance.
       :data:`playground` is an :class:`~kivy.properties.ObjectProperty`
    '''

    widgettree = ObjectProperty(None)
    '''Reference to the :class:`~designer.nodetree.WidgetsTree` instance.
       :data:`widgettree` is an :class:`~kivy.properties.ObjectProperty`
    '''

    kv_code_input = ObjectProperty(None)
    '''Reference to the :class:`~designer.uix.KVLangArea` instance.
       :data:`kv_code_input` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_kv_code_input = ObjectProperty(None)
    '''Reference to the splitter parent of kv_code_input.
       :data:`splitter_kv_code_input` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    grid_widget_tree = ObjectProperty(None)
    '''Reference to the grid parent of widgettree.
       :data:`grid_widget_tree` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_property = ObjectProperty(None)
    '''Reference to the splitter parent of propertyviewer.
       :data:`splitter_property` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_widget_tree = ObjectProperty(None)
    '''Reference to the splitter parent of widgettree.
       :data:`splitter_widget_tree` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    error_console = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.codeinput.CodeInput` used for displaying
       exceptions.
    '''

    kivy_console = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.kivy_console.KivyConsole`.
    '''

    python_console = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.py_console.PythonConsole`
    '''

    tab_pannel = ObjectProperty(None)
    '''Instance of :class:`~designer.designer_content.DesignerTabbedPanel`
       containing error_console, kivy_console and kv_lang_area
    '''

    eventviewer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UICreator, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_everything)

    def reload_btn_pressed(self, *args):
        '''Default handler for 'on_release' event of "Reload" button.
        '''
        self.kv_code_input.func_reload_kv()

    def on_touch_down(self, *args):
        '''Default handler for 'on_touch_down' event.
        '''
        if self.playground and self.playground.keyboard:
            self.playground.keyboard.release()

        return super(UICreator, self).on_touch_down(*args)

    def on_show_edit(self, *args):
        '''Event handler for 'on_show_edit' event.
        '''
        App.get_running_app().root.on_show_edit(*args)

    def cleanup(self):
        '''To clean up everything before loading new project.
        '''
        self.playground.cleanup()
        self.kv_code_input.text = ''

    def _setup_everything(self, *args):
        '''To setup all the references in between widget
        '''

        self.kv_code_input.playground = self.playground
        self.playground.kv_code_input = self.kv_code_input
        self.playground.widgettree = self.widgettree
        self.propertyviewer.kv_code_input = self.kv_code_input
        self.eventviewer.kv_code_input = self.kv_code_input
        self.py_console.remove_widget(self.py_console.children[1])
