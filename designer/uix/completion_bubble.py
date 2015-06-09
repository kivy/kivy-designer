from kivy.adapters.listadapter import ListAdapter
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.bubble import Bubble
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel, ListItemButton

Builder.load_string('''

<CompletionBubble>
    size_hint: None, None
    orientation: 'vertical'
    pos_hint: {'center_x': .5, 'y': .5}
    width: 200
    height: 210
    arrow_pos: 'top_mid'

<SuggestionItem>:
    size_hint: 1, None
    background_normal: ''
    background_down: ''
    height: 35
    selected_color: 0, 0, 0, 0.5
    deselected_color: 0, 0, 0, 0.7
    halign: 'left'
    valign: 'middle'
    text_size: self.width - 20, self.height
    shorten: True
    shorten_from: 'right'
''')


class SuggestionItem(ListItemButton):
    pass


class CompletionBubble(Bubble):

    list_view = ObjectProperty(None)
    '''(internal) Reference a ListView with a list of SuggestionItems
       :data:`list_view` is a :class:`~kivy.properties.ObjectProperty`
    '''

    adapter = ObjectProperty(None)
    '''(internal) Reference a ListView adapter
       :data:`adapter` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(CompletionBubble, self).__init__(**kwargs)


    def _create_list_view(self, data):
        self.adapter = ListAdapter(
            data=data,
            args_converter=self._args_converter,
            cls=SuggestionItem,
            selection_mode='single',
            allow_empty_selection=False
        )
        self.adapter.bind(on_selection_change=self.on_selection_change)
        self.list_view = ListView(adapter=self.adapter)
        self.add_widget(self.list_view)

    def _args_converter(self, index, completion):
        return {'text': completion.name, 'is_selected': False}

    def show_completions(self, completions):
        Window.bind(on_keyboard=self.on_keyboard)
        if not self.list_view:
            self._create_list_view(completions)
        else:
            self.adapter.data = completions
        # self.suggestions.item_strings = completions

    def on_selection_change(self, *args):
        pass

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        selected_index = self.adapter.selection[0].index

        if key == 273:
            # up
            if selected_index > 0:
                new_index = selected_index - 1
                item = self.adapter.get_view(new_index)
                item.trigger_action(0)
                if new_index > 3 and new_index < len(self.adapter.data) - 1:
                    self.list_view.scroll_to(new_index - 3)
        elif key == 274:
            # down
            if selected_index < len(self.adapter.data) - 1:
                new_index = selected_index + 1
                item = self.adapter.get_view(new_index)
                item.trigger_action(0)
                if new_index > 3 and new_index < len(self.adapter.data) - 1:
                    self.list_view.scroll_to(new_index - 3)


if __name__ == '__main__':
    from kivy.app import App
    import jedi


    Builder.load_string('''
<Test>:
    background_normal: ''
    background_color: 1, 0, 1, 1
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.8
        Rectangle:
            pos: self.pos
            size: self.size
    Button:
        text: 'Toggle Completion Menu'
        size_hint: None, None
        width: 250
        height: 50
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        on_press: root.show_bubble()
''')


    class Test(FloatLayout):
        def __init__(self, **kwargs):
            super(Test, self).__init__(**kwargs)
            self.bubble = CompletionBubble()

        def show_bubble(self):
            source = '''
import datetime
datetime.da'''
            script = jedi.Script(source, 3, len('datetime.da'))
            completions = script.completions()
            self.bubble.show_completions(completions*10)
            self.add_widget(self.bubble)


    class MyApp(App):
        def build(self):
            return Test()

    MyApp().run()
