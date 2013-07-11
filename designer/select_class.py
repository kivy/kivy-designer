from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.properties import ObjectProperty
from kivy.adapters.listadapter import ListAdapter
from functools import partial

class SelectClass(BoxLayout):
    '''SelectClass dialog is shows a list of classes. User would have to 
       select a class from these classes. It will emit 'on_select' when
       select_button is pressed and 'on_cancel' when cancel_button is pressed.
    '''

    listview = ObjectProperty(None)
    '''The ListView used for showing file paths.
    '''

    select_button = ObjectProperty(None)
    '''Button used to select the list item.
    '''

    cancel_button = ObjectProperty(None)
    '''Button to cancel the dialog.
    '''

    adapter = ObjectProperty(None)
    '''ListAdapter used for selecting files.
    '''

    __events__=('on_select', 'on_cancel')

    def __init__(self, class_rule_list, **kwargs):
        super(SelectClass, self).__init__(**kwargs)
        item_strings = [_rule.name for _rule in class_rule_list]
        adapter = ListAdapter(cls=ListItemButton, data=item_strings, selection_mode='single', allow_empty_selection=False)
        self.listview = ListView(adapter=adapter)
        self.add_widget(self.listview, 1)

    def on_select_button(self, *args):
        self.select_button.bind(on_press=partial(self.dispatch, 'on_select'))
    
    def on_cancel_button(self, *args):
        self.cancel_button.bind(on_press=partial(self.dispatch, 'on_cancel'))
        
    def on_select(self, *args):
        pass
    
    def on_cancel(self, *args):
        pass
