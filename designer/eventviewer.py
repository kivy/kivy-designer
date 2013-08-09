from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock

from designer.propertyviewer import PropertyViewer,\
    PropertyTextInput, PropertyLabel

import re

class EventHandlerTextInput(TextInput):

    eventwidget = ObjectProperty(None)

    eventname = StringProperty(None)

    kv_code_input = ObjectProperty()

    text_inserted = BooleanProperty(None)

    def on_text(self, instance, value):        
        if not self.kv_code_input:
            return

        self.kv_code_input.set_event_handler(self.eventwidget,
                                             self.eventname, self.text)

class NewEventTextInput(TextInput):
    
    __events__ = ('on_create_event',)
    
    def on_create_event(self, *args):
        pass

    def insert_text(self, substring, from_undo=False):
        if '\n' in substring:
            #Enter pressed create a new event
            substring = substring.replace('\n', '')
            if self.text[:3] == 'on_':
                self.dispatch('on_create_event')

        super(NewEventTextInput, self).insert_text(substring, from_undo)

class EventLabel(PropertyLabel):
    pass

class EventViewer(PropertyViewer):
    
    project_loader = ObjectProperty(None)
    
    designer_tabbed_panel = ObjectProperty(None)
    
    statusbar = ObjectProperty(None)

    def on_widget(self, instance, value):
        self.clear()
        if value is not None:
            self.discover(value)

    def clear(self):
        '''To clear :data:`prop_list`.
        '''
        self.prop_list.clear_widgets()

    def discover(self, value):
        '''To discover all properties and add their
           :class:`~designer.propertyviewer.PropertyLabel` and
           :class:`~designer.propertyviewer.PropertyBoolean`/
           :class:`~designer.propertyviewer.PropertyTextInput`
           to :data:`prop_list`.
        '''

        add = self.prop_list.add_widget
        events = value.events()
        for event in events:
            ip = self.build_for(event)
            if not ip:
                continue
            add(EventLabel(text=event))
            add(ip)
        
        if self.project_loader.is_widget_custom(self.widget):
            #Allow adding a new event only if current widget is a custom rule
            add(EventLabel(text='Type and press enter to \ncreate a new event'))
            txt = NewEventTextInput(multiline=True)
            txt.bind(on_create_event=self.create_event)
            add(txt)
    
    def create_event(self, txt):
        #Find the python file of widget
        py_file = None
        for rule in self.project_loader.class_rules:
            if rule.name == type(self.widget).__name__:
                py_file = rule.file
                break
        
        #Open it in DesignerTabbedPannel
        rel_path = py_file.replace(self.project_loader.proj_dir, '')
        if rel_path[0] == '/' or rel_path[0] == '\\':
            rel_path = rel_path[1:]

        self.designer_tabbed_panel.open_file(py_file, rel_path, switch_to=False)
        self.rel_path = rel_path
        self.txt = txt
        Clock.schedule_once(self._add_event)

    def _add_event(self, *args):
        #Find the class definition
        py_code_input = None
        txt = self.txt
        rel_path = self.rel_path
        for code_input in self.designer_tabbed_panel.list_py_code_inputs:
            if code_input.rel_file_path == rel_path:
                py_code_input = code_input
                break
        
        pos = -1
        for searchiter in re.finditer(r'class\s+%s\(.+\):'%\
                                      type(self.widget).__name__,
                                      py_code_input.text):
            pos = searchiter.end()
        
        if pos != -1:
            col, row = py_code_input.get_cursor_from_index(pos)
            lines = py_code_input.text.splitlines()
            found_events = False
            events_row = row
            for i in range(row, len(lines)):
                if re.match(r'__events__\s*=\s*\(.+\)', lines[i]):
                    found_events = True
                    events_row = i
                    break
                
                elif re.match('class\s+[\w\d\_]+\(.+\):', lines[i]):
                    break
                
                elif re.match('def\s+[\w\d\_]+\(.+\):', lines[i]):
                    break              
            
            if found_events:
                events_col = lines[events_row].rfind(')') - 1
                py_code_input.cursor = events_row, events_col
                py_code_input.insert_text(txt.text)

            else:
                py_code_input.text = py_code_input.text[:pos] + \
                    '\n    __events__=("%s",)\n'\
                    '    def %s(self, *args):\n        pass'%(txt.text, txt.text)+\
                    py_code_input.text[pos:]
            self.statusbar.show_message('New Event Created you must save '
                                        'project for changes to take effect')

    def build_for(self, name):
        '''To create :class:`~designer.propertyviewer.PropertyBoolean`/
           :class:`~designer.propertyviewer.PropertyTextInput`
           for Property 'name'
        '''
        text = self.kv_code_input.get_property_value(self.widget, name)
        return EventHandlerTextInput(kv_code_input=self.kv_code_input,
                                     eventname=name,
                                     eventwidget=self.widget,
                                     multiline=False,
                                     text=text)