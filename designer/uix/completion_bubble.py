from kivy.adapters.listadapter import ListAdapter
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.bubble import Bubble
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListView, ListItemButton

Builder.load_string('''

<CompletionBubble>
    size_hint: None, None
    orientation: 'vertical'
    width: 200
    height: 210
    arrow_pos: 'top_mid'

<SuggestionItem>:
    size_hint: 1, None
    background_normal: ''
    background_down: ''
    height: 35
    selected_color: 1, 1, 1, 0.1
    deselected_color: 0, 0, 0, 0
    halign: 'left'
    valign: 'middle'
    text_size: self.width - 20, self.height
    shorten: True
    shorten_from: 'right'
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.8
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgb: 0.2, 0.2, 0.2
        Rectangle:
            pos: self.pos
            size: self.width, 1
''')


class SuggestionItem(ListItemButton):
    complete = StringProperty('')
    '''Completion text
    '''

    selected_by_touch = ObjectProperty(None)
    '''Callback function to a item selected by touch
    '''
    def on_press(self):
        if self.is_selected:
            self.selected_by_touch(self)


class CompletionListView(ListView):

    scrolled = BooleanProperty(False)
    '''(internal) Identify if the user had scrolled the list with the mouse
    '''

    def _scroll(self, scroll_y):
        self.scrolled = True
        super(CompletionListView, self)._scroll(scroll_y)


class CompletionBubble(Bubble):

    list_view = ObjectProperty(None, allownone=True)
    '''(internal) Reference a ListView with a list of SuggestionItems
       :data:`list_view` is a :class:`~kivy.properties.ObjectProperty`
    '''

    adapter = ObjectProperty(None)
    '''(internal) Reference a ListView adapter
       :data:`adapter` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_complete', 'on_cancel', )

    def __init__(self, **kwargs):
        super(CompletionBubble, self).__init__(**kwargs)
        Window.bind(on_touch_down=self.on_window_touch_down)

    def on_window_touch_down(self, win, touch):
        '''Disable the completion if the user clicks anywhere
        '''
        if not self.collide_point(*touch.pos):
            self.dispatch('on_cancel')

    def _create_list_view(self, data):
        '''Create the ListAdapter
        '''
        self.adapter = ListAdapter(
            data=data,
            args_converter=self._args_converter,
            cls=SuggestionItem,
            selection_mode='single',
            allow_empty_selection=False
        )
        self.adapter.bind(on_selection_change=self.on_selection_change)
        self.list_view = CompletionListView(adapter=self.adapter)
        self.add_widget(self.list_view)

    def _args_converter(self, index, completion):
        return {'text': completion.name,
                'is_selected': False,
                'complete': completion.complete,
                'selected_by_touch': self.selected_by_touch}

    def selected_by_touch(self, item):
        self.dispatch('on_complete', item.complete)

    def show_completions(self, completions, force_scroll=False):
        '''Update the Completion ListView with completions
        '''
        if completions == []:
            fake_completion = type('obj', (object,),
                                   {'name': 'No suggestions', 'complete': ''})
            completions.append(fake_completion)
        Window.bind(on_key_down=self.on_key_down)
        if not self.list_view:
            self._create_list_view(completions)
        else:
            self.adapter.data = completions
        if force_scroll:
            self.list_view.scroll_to(0)

    def on_selection_change(self, *args):
        pass

    def _scroll_item(self, new_index):
        '''Update the scroll view position to display the new_index item
        '''
        item = self.adapter.get_view(new_index)
        if item:
            item.trigger_action(0)
            if new_index > 2 and new_index < len(self.adapter.data) - 1:
                self.list_view.scroll_to(new_index - 3)

    def on_key_down(self, instance, key, *args):
        '''Keyboard listener to grab key codes and interact with the
        Completion box
        '''
        selected_item = self.adapter.selection[0]
        selected_index = selected_item.index
        if self.list_view.scrolled:
            # recreate list view after mouse scroll due to the bug kivy/#3418
            self.remove_widget(self.list_view)
            self.list_view = None
            self.show_completions(self.adapter.data)
            return self.on_key_down(instance, key, args)

        if key == 273:
            # up
            if selected_index > 0:
                self._scroll_item(selected_index - 1)
            return True

        elif key == 274:
            # down
            if selected_index < len(self.adapter.data) - 1:
                self._scroll_item(selected_index + 1)
            return True

        elif key in [9, 13, 32]:
            # tab, enter or space
            self.dispatch('on_complete', selected_item.complete)
            return True

        else:
            # another key cancel the completion
            self.dispatch('on_cancel')
            return False

    def reposition(self, pos, line_height):
        '''Update the Bubble position. Try to display it in the best place of
        the screen
        '''
        win = Window
        self.x = pos[0] - self.width / 2
        self.y = pos[1] - self.height - line_height

        # fit in the screen horizontally
        if self.right > win.width:
            self.x = win.width - self.width
        if self.x < 0:
            self.x = 0

        # fit in the screen vertically
        if self.y < 0:
            diff = abs(self.y)
            # check if we can move it to top
            new_y = pos[1] + line_height
            if new_y + self.height < win.height:  # fit in the screen
                self.y = new_y
            else:  # doesnt fit on top neither on bottom. Check the best place
                new_diff = abs(new_y + self.height - win.height)
                if new_diff < diff:  # if we lose lest moving it to top
                    self.y = new_y

        # compare the desired position with the actual position
        x_relative = self.x - (pos[0] - self.width / 2)

        x_range = self.width / 4  # consider 25% as the range

        def _get_hpos():
            '''Compare the position of the widget with the parent
            to display the arrow in the correct position
            '''
            _pos = 'mid'
            if x_relative == 0:
                _pos = 'mid'
            elif x_relative < -x_range:
                _pos = 'right'
            elif x_relative > x_range:
                _pos = 'left'
            return _pos

        if self.y == pos[1] - self.height - line_height:
            self.arrow_pos = 'top_' + _get_hpos()
        else:
            self.arrow_pos = 'bottom_' + _get_hpos()

    def on_complete(self, *args):
        '''Dispatch a completion selection
        '''
        Window.unbind(on_key_down=self.on_key_down)

    def on_cancel(self, *args):
        '''Disable key listener on cancel
        '''
        Window.unbind(on_key_down=self.on_key_down)

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
            self.bubble.pos_hint = {'center_x': 0.5, 'y': 0}
            self.bubble.bind(on_cancel=self.on_cancel)
            self.bubble.bind(on_complete=self.on_cancel)

        def show_bubble(self):
            source = '''
import datetime
datetime.da'''
            script = jedi.Script(source, 3, len('datetime.da'))
            completions = script.completions()
            self.bubble.show_completions(completions * 10)
            self.add_widget(self.bubble)

        def on_cancel(self, *args):
            if self.bubble.parent is not None:
                self.bubble.show_completions([])
                self.bubble.parent.remove_widget(self.bubble)
                self.is_bubble_visible = False

    class MyApp(App):
        def build(self):
            return Test()

    MyApp().run()
